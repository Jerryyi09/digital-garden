"""One-pass practical candidate generation with reusable segment/word ASR caches."""
from collections import Counter, defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
import re
import time
from pathlib import Path
import subprocess

from tools.readalong.asr_runtime import transcription_backend
from tools.readalong.authoritative_validator import DOMFragmentExtractor, canonical_text, safe_path, probe_audio_duration
from tools.readalong.batch_candidate_remapper import atomic_json
from tools.readalong.candidate_safety import alist_audio_path, plan_audio_blocks, require_candidate_output
from tools.readalong.config import resolve_model_path
from tools.readalong.input_inventory import compute_strong_cache_key, safe_extract_epub
from tools.readalong.universal_stream_aligner import get_spine_htmls
from tools.readalong_fast.matcher import ParagraphIndex, prepare_paragraphs, tokens
from tools.readalong_fast.decoding import AudioDecodeIssue, decode_pcm, remap_segments
from tools.readalong_fast.scopes import material_ranges, subtract_ranges
from tools.readalong.full_inventory_scanner import scan_root_raw
from tools.readalong_fast.native_cache import NativeCacheIndex
from tools.readalong_fast.sampling import verdict_runs_full_book

CONTEXT_SECONDS = 20


def verify_track_inventory(book, tracks):
  """Inventory every physical source, including title/credit tracks, exactly once."""
  declared = [row['rel_to_book'] for row in tracks]
  physical = {p.relative_to(book).as_posix() for p in scan_root_raw(book)[0]}
  if len(declared) != len(set(declared)) or set(declared) != physical:
    raise ValueError('ERR_TRACK_INVENTORY_MISMATCH: '+json.dumps({
      'undeclared': sorted(physical-set(declared)), 'missing': sorted(set(declared)-physical),
      'duplicateDeclarations': len(declared)-len(set(declared))}))


def context_units(rows):
  """Join adjacent observed ASR segments; never split by invented timestamps."""
  result = []
  for row in rows:
    if (result and not row.get("timingRejected") and not result[-1].get("timingRejected")
        and row["start"] >= result[-1]["end"] and row["start"]-result[-1]["end"] <= 1.5
        and row["end"]-result[-1]["start"] <= CONTEXT_SECONDS):
      if "parts" not in result[-1]:
        result[-1]["parts"] = [dict(result[-1])]
      result[-1]["parts"].extend(row.get("parts", [dict(row)]))
      result[-1]["end"] = row["end"]
      result[-1]["text"] += " "+row["text"]
    else:
      result.append(dict(row))
  return result


def stat_key(path):
  path = Path(path)
  if path.is_symlink():
    raise ValueError(f"Linked input is not permitted: {path}")
  st = path.stat()
  return [st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns]


def file_hash(path):
  digest = hashlib.sha256()
  with Path(path).open("rb") as stream:
    for chunk in iter(lambda: stream.read(1024*1024), b""):
      digest.update(chunk)
  return digest.hexdigest()


class InputCache:
  """Hash each unchanged input once; reuse measured duration bound to that hash."""
  def __init__(self, path):
    self.path = Path(path)
    self.rows = json.loads(self.path.read_text()) if self.path.exists() else {}

  def verify(self, path, expected_hash):
    if Path(path).is_symlink():
      raise ValueError("Linked input is not permitted")
    path = Path(path).resolve(strict=True)
    key = stat_key(path)
    entry = self.rows.get(str(path), {})
    digest = entry.get("sha256") if entry.get("stat") == key else file_hash(path)
    if digest != expected_hash or stat_key(path) != key:
      raise RuntimeError(f"SOURCE_CHANGED: {path}")
    self.rows[str(path)] = {**(entry if entry.get("stat") == key else {}), "stat": key, "sha256": digest}
    atomic_json(self.path, self.rows)
    return key

  def duration(self, path, measured):
    # Preserve exact legacy chunk-cache geometry. Inventory display durations
    # were rounded to four decimals, which can invalidate the final chunk key.
    path = Path(path).resolve(strict=True)
    entry = self.rows[str(path)]
    if "duration" not in entry:
      duration = probe_audio_duration(path)
      if not math.isfinite(duration) or duration <= 0 or abs(duration-measured) > .1:
        raise RuntimeError("SOURCE_CHANGED: duration no longer agrees with inventory")
      entry["duration"] = duration
      atomic_json(self.path, self.rows)
    return entry["duration"]


def checked_units(rows, start, end):
  result = []
  prior = start
  for row in rows:
    a, b = row.get("start"), row.get("end")
    if (type(a) not in (int, float) or type(b) not in (int, float)
        or not math.isfinite(a) or not math.isfinite(b)
        or a < start-.001 or b > end+.05 or a < prior-.05 or a >= b or a >= end):
      raise ValueError(f"INVALID_ASR_INTERVAL: index={len(result)} start={a!r} end={b!r} priorEnd={prior!r} requested={start}..{end}")
    if not isinstance(row.get("text"), str) or not row["text"].strip():
      continue
    result.append({"start": a, "end": min(b, end), "text": row["text"]})
    prior = b
  return result


def normalize_native(rows, start, end):
  """Intersect native observations with real PCM; abstain on timing conflicts."""
  clean, diagnostics = [], []
  prior = start
  for i, row in enumerate(rows):
    a, b, text = row.get("start"), row.get("end"), row.get("text")
    reason = None
    if (not isinstance(text, str) or not text.strip()) and not row.get("decodeUnavailable"):
      reason = "EMPTY_TEXT"
    elif (type(a) not in (int, float) or type(b) not in (int, float)
          or not math.isfinite(a) or not math.isfinite(b)):
      reason = "NONFINITE_OR_MISSING_TIME"
    elif a == b:
      reason = "ZERO_DURATION"
    elif a > b:
      reason = "REVERSED_INTERVAL"
    elif a >= end or b <= start:
      reason = "OUTSIDE_DECODED_AUDIO"
    if reason:
      diagnostics.append({"index": i, "reason": reason, "raw": json_safe(row)})
      continue
    left, right = max(start, a), min(end, b)
    if left != a or right != b:
      diagnostics.append({"index": i, "reason": "INTERSECTED_WITH_DECODED_AUDIO", "raw": row,
                          "retainedStart": left, "retainedEnd": right})
    rejected = (row.get("timingRejected") or row.get("decodeTimingRejected") or row.get("decodeUnavailable")
      or max(start-a, b-end) > .5 or left < prior-.05 or right <= prior)
    if rejected:
      clean.append({**row, "start": left, "end": right, "text": text, "timingRejected": True})
      diagnostics.append({"index": i, "reason": "DECODE_UNAVAILABLE" if row.get("decodeUnavailable") else
        "DECODE_TIMELINE_UNTRUSTED" if row.get("decodeTimingRejected") else "UNTRUSTED_BOUNDARY_OR_OVERLAP", "raw": row})
      continue
    left = max(left, prior)
    kept = {"start": left, "end": right, "text": text}
    if left != a or right != b:
      kept["observedInterval"] = {"start": a, "end": b}
    clean.append(kept)
    prior = right
  return clean, diagnostics


def json_safe(value):
  """Keep malformed diagnostic values without emitting nonstandard JSON NaN."""
  if isinstance(value, float) and not math.isfinite(value):
    return repr(value)
  if isinstance(value, dict):
    return {k: json_safe(v) for k, v in value.items()}
  if isinstance(value, list):
    return [json_safe(v) for v in value]
  return value


def words_to_units(words, start, end):
  """Reuse observed word times; grouping never interpolates timestamps."""
  rows, groups, group = [], [], []
  for word in words:
    if word.get("start") == word.get("end"):
      continue
    if not isinstance(word.get("word"), str):
      raise ValueError("Invalid legacy word cache")
    if group and (word["start"]-group[-1]["end"] > 1.5 or word["end"]-group[0]["start"] > CONTEXT_SECONDS):
      rows.append({"start": group[0]["start"], "end": group[-1]["end"], "text": " ".join(w["word"] for w in group)})
      groups.append(group)
      group = []
    group.append(word)
  if group:
    rows.append({"start": group[0]["start"], "end": group[-1]["end"], "text": " ".join(w["word"] for w in group)})
    groups.append(group)
  clean = checked_units(rows, start, end)
  for row, group in zip(clean, groups):
    parts, part = [], []
    for word in group:
      if part and word["end"]-part[0]["start"] > 5:
        parts.append({"start": part[0]["start"], "end": part[-1]["end"], "text": " ".join(w["word"] for w in part)})
        part = []
      part.append(word)
    if part:
      parts.append({"start": part[0]["start"], "end": part[-1]["end"], "text": " ".join(w["word"] for w in part)})
    if len(parts) > 1:
      try:
        row["parts"] = checked_units(parts, row["start"], row["end"])
      except ValueError:
        # A valid coarse observation is not evidence for invalid finer times.
        pass
  return clean


class SpeechCache:
  def __init__(self, root, read_roots, model_sha, cache_only=False, tolerant_decode=True,
               asr_engine="batch"):
    self.root = Path(root)
    self.root.mkdir(parents=True, exist_ok=True)
    self.read_roots = list(dict.fromkeys([self.root]+[Path(p) for p in read_roots]))
    self.model_sha = model_sha
    self.cache_only = cache_only
    self.tolerant_decode = tolerant_decode
    if asr_engine not in ("serial", "batch", "words"):
      raise ValueError("asr_engine must be 'serial', 'batch', or 'words'")
    self.asr_engine = asr_engine
    self.stats = Counter()
    self.diagnostics = []
    self.native_index = NativeCacheIndex(self.read_roots, model_sha)
    # Decoding only. ffmpeg runs as a subprocess and releases the GIL, so one
    # prefetch thread overlaps the next block's decode with this block's GPU
    # inference. Transcription never leaves the main thread: MLX/Metal under
    # concurrency changes numerical results, which would pollute published
    # timelines.
    self._prefetch_pool = None
    self._prefetch = {}

  def start_prefetch(self, jobs):
    """Warm PCM for the given (audio, start, duration, key, params) jobs.

    Only decode results are shared; evidence files are still written by
    decode_pcm itself, so on-disk ordering and content are unchanged."""
    self.stop_prefetch()
    if not jobs:
      return
    self._prefetch_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="pcm-prefetch")

    def decode(job):
      audio, start, duration, key, params = job
      try:
        return decode_pcm(audio, start, duration, self.root/(key+".decode.json"), params,
                          tolerant=self.tolerant_decode)
      except AudioDecodeIssue as exc:
        # The consuming chunk() call re-raises with identical semantics.
        return exc

    for job in jobs:
      audio, start, duration, key, params = job
      self._prefetch[(str(audio), start, duration, key)] = self._prefetch_pool.submit(decode, job)

  def take_prefetched(self, audio, start, duration, key):
    future = self._prefetch.pop((str(audio), start, duration, key), None)
    return None if future is None else future.result()

  def stop_prefetch(self):
    if self._prefetch_pool is not None:
      self._prefetch_pool.shutdown(wait=True)
      self._prefetch_pool = None
    self._prefetch.clear()

  def covering_native(self, sha, start, duration):
    entry = self.native_index.covering(sha, start, start+duration)
    if entry is None:
      return None
    a, b, path, params = entry
    data = json.loads(path.read_text())
    if data.get('parameters') != params:
      raise ValueError('Native cache changed after discovery')
    decoded_end = data.get('decodedEnd', b)
    if type(decoded_end) not in (int, float) or not math.isfinite(decoded_end) or not a < decoded_end <= b+.001:
      raise ValueError('Invalid containing-cache decoded boundary')
    rows, diagnostics = normalize_native(data.get('rawSegments', data['segments']), a, decoded_end)
    self.diagnostics.extend({**d, 'cachePath': str(path), 'sourceSha256': sha} for d in diagnostics)
    audit = data.get('decodeAudit', {})
    if audit.get('status') == 'RECOVERED_WITH_TIMELINE_MAP':
      timing = audit.get('timingMap')
      if (not isinstance(timing, dict) or timing.get('chunkStart') != a
          or timing.get('method') != 'observed-frame-pts-v1'):
        raise ValueError('Containing cache lacks frame-time evidence')
      self.diagnostics.append({'reason': 'DECODE_RECOVERED_WITH_FRAME_PTS', 'sourceSha256': sha, 'timingMap': timing})
    self.stats['nativeContainingCacheHits'] += 1
    return [r for r in rows if r['end'] > start and r['start'] < start+duration]

  def lookup_words(self, names, start, end, account=True):
    for root in self.read_roots:
      for name in names:
        path = root/name
        if path.is_file():
          try:
            words = json.loads(path.read_text())
            if not isinstance(words, list) or not words:
              continue
            rows = words_to_units(words, start, end)
            if rows:
              if account:
                self.stats["legacyCachedAudioSeconds"] += end-start
              return rows
          except (ValueError, KeyError, TypeError) as exc:
            self.stats["invalidLegacyCaches"] += 1
            self.diagnostics.append({"reason": "INVALID_LEGACY_CACHE", "path": str(path), "error": str(exc)})
    return None

  def whole_legacy_track(self, audio, sha, duration, cap, account=True):
    # A cap at/above duration did not change the original full-track ASR input.
    caps = list(dict.fromkeys([cap, duration+1, 900, 900.0, 1800, 1800.0]))
    names = []
    for limit in caps:
      if limit >= duration:
        key = compute_strong_cache_key(sha, {"modelSha256": self.model_sha,
          "language": "en", "word_timestamps": True, "max_sample": limit})
        names.append(f"transcript_{audio.stem}_{key[:12]}.json")
    return self.lookup_words(names, 0, duration, account)

  def screen_clip(self, audio, sha, track_duration, cap, start, duration=15):
    rows = self.whole_legacy_track(audio, sha, track_duration, cap, account=False)
    if rows is None:
      block_start = int(start//1800)*1800.0
      length = min(1800.0, track_duration-block_start)
      key = compute_strong_cache_key(sha, {"modelSha256": self.model_sha,
        "start": block_start, "duration": length, "language": "en",
        "word_timestamps": True, "sampleRate": 24000})
      rows = self.lookup_words([key+".json"], block_start, block_start+length, account=False)
    if rows is not None:
      self.stats["screenCachedProbes"] += 1
      return [r for r in rows if r["end"] > start and r["start"] < start+duration]
    rows = self.covering_native(sha, start, min(duration, track_duration-start))
    if rows is not None:
      self.stats['screenCachedProbes'] += 1
      return rows
    before = self.stats["newAsrAudioSeconds"]
    rows = self.chunk(audio, sha, start, min(duration, track_duration-start))
    self.stats["screenNewAsrProbes" if self.stats["newAsrAudioSeconds"] > before else "screenCachedProbes"] += 1
    return rows

  def chunk_params(self, sha, start, duration):
    """Pure identity computation, so a caller can schedule a prefetch without
    touching caches or emitting diagnostics."""
    if self.asr_engine == "words":
      from tools.readalong_fast.batch_words_asr import batch_words_params
      return batch_words_params(sha, self.model_sha, start, duration)
    return {"sourceSha256": sha, "modelSha256": self.model_sha, "start": start,
      "duration": duration, "language": "en", "word_timestamps": False,
      "sampleRate": 16000, "engine": "mlx-segment-v1"}

  def needs_decode(self, audio, sha, start, duration):
    """True only when this block will actually run ffmpeg: no word, segment, or
    containing cache can serve it."""
    legacy = compute_strong_cache_key(sha, {"modelSha256": self.model_sha,
      "start": start, "duration": duration, "language": "en",
      "word_timestamps": True, "sampleRate": 24000})
    for root in self.read_roots:
      if (root/(legacy+".json")).is_file():
        return False
    key = hashlib.sha256(json.dumps(self.chunk_params(sha, start, duration), sort_keys=True).encode()).hexdigest()
    for root in self.read_roots:
      if (root/(key+".json")).is_file():
        return False
    if self.asr_engine == "words":
      return True
    return self.native_index.covering(sha, start, start+duration) is None

  def chunk_words(self, audio, sha, start, duration):
    """Retrieve word timestamps for the chunk. Checks legacy and new batch-words cache."""
    legacy = compute_strong_cache_key(sha, {"modelSha256": self.model_sha,
      "start": start, "duration": duration, "language": "en",
      "word_timestamps": True, "sampleRate": 24000})
    for root in self.read_roots:
      path = root/(legacy+".json")
      if path.is_file():
        try:
          data = json.loads(path.read_text())
          if isinstance(data, list):
            if data or self.cache_only:
              return data
          if isinstance(data, dict) and "words" in data:
            words = data["words"]
            if data.get("decodeUnavailable") or any(
                row.get("decodeUnavailable") for row in data.get("segments", [])
                if isinstance(row, dict)):
              if self.cache_only:
                return words
              self.diagnostics.append({"reason": "RETRY_PREVIOUSLY_UNAVAILABLE_WORD_CACHE",
                "start": start, "end": start+duration, "sourceSha256": sha, "cachePath": str(path)})
            elif words or self.cache_only:
              return words
        except Exception:
          pass
    params = self.chunk_params(sha, start, duration)
    key = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
    for root in self.read_roots:
      path = root/(key+".json")
      if path.is_file():
        try:
          data = json.loads(path.read_text())
          if isinstance(data, dict) and "words" in data:
            words = data["words"]
            unavailable = data.get("decodeUnavailable") or any(
              row.get("decodeUnavailable") for row in data.get("segments", [])
              if isinstance(row, dict))
            if unavailable:
              if self.cache_only:
                return words
              self.diagnostics.append({"reason": "RETRY_PREVIOUSLY_UNAVAILABLE_WORD_CACHE",
                "start": start, "end": start+duration, "sourceSha256": sha, "cachePath": str(path)})
            elif words or self.cache_only:
              return words
        except Exception:
          pass
    # If not yet decoded/transcribed, trigger chunk() first
    self.chunk(audio, sha, start, duration)
    for root in self.read_roots + [self.root]:
      path = root/(key+".json")
      if path.is_file():
        try:
          data = json.loads(path.read_text())
          if isinstance(data, dict) and "words" in data:
            return data["words"]
        except Exception:
          pass
    return []

  def chunk(self, audio, sha, start, duration):
    legacy = compute_strong_cache_key(sha, {"modelSha256": self.model_sha,
      "start": start, "duration": duration, "language": "en",
      "word_timestamps": True, "sampleRate": 24000})
    rows = self.lookup_words([legacy+".json"], start, start+duration)
    if rows is not None:
      return rows
    params = self.chunk_params(sha, start, duration)
    key = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
    for root in self.read_roots:
      path = root/(key+".json")
      if path.is_file():
        data = json.loads(path.read_text())
        if data.get("parameters") != params:
          raise ValueError("Segment cache identity mismatch")
        decode_audit = data.get("decodeAudit", {})
        if decode_audit.get("status") == "RECOVERED_WITH_TIMELINE_MAP":
          timing = decode_audit.get("timingMap")
          if not isinstance(timing, dict) or timing.get("method") != "observed-frame-pts-v1" or timing.get("chunkStart") != start:
            raise ValueError("Recovered cache lacks bound frame-timing evidence")
          self.diagnostics.append({"reason": "DECODE_RECOVERED_WITH_FRAME_PTS", "start": start,
            "end": start+duration, "sourceSha256": sha, "timingMap": timing, "cachePath": str(path)})
        decoded_end = data.get("decodedEnd", start+duration)
        if (type(decoded_end) not in (int, float) or not math.isfinite(decoded_end)
            or not start < decoded_end <= start+duration+.001):
          raise ValueError("Segment cache decoded boundary is invalid")
        rows, diagnostics = normalize_native(data.get("rawSegments", data["segments"]), start, decoded_end)
        self.diagnostics.extend({**d, "cachePath": str(path), "sourceSha256": sha,
          "requestedStart": start, "requestedEnd": start+duration} for d in diagnostics)
        if any(row.get("decodeUnavailable") for row in rows) and not self.cache_only:
          # A quarantined decode is not a successful cache hit. Retry it when
          # decoding is enabled so a transient/repairable source failure can heal.
          self.diagnostics.append({"reason": "RETRY_PREVIOUSLY_UNAVAILABLE_DECODE", "start": start,
            "end": start+duration, "sourceSha256": sha, "cachePath": str(path)})
          continue
        self.stats["unavailableDecodeAudioSeconds" if any(r.get("decodeUnavailable") for r in rows)
                   else "segmentCachedAudioSeconds"] += duration
        return context_units(rows)
    if self.asr_engine != "words":
      rows = self.covering_native(sha, start, duration)
      if rows is not None:
        rows, diagnostics = normalize_native(rows, start, start+duration)
        self.diagnostics.extend(diagnostics)
        if any(row.get("decodeUnavailable") for row in rows) and not self.cache_only:
          # Native coverage can point at the same quarantined cache entry that
          # the exact-key lookup just rejected. Do not let it short-circuit a
          # requested retry.
          rows = None
      if rows is not None:
        self.stats['unavailableDecodeAudioSeconds' if any(r.get('decodeUnavailable') for r in rows)
                   else 'segmentCachedAudioSeconds'] += duration
        return context_units(rows)
    if self.cache_only:
      raise RuntimeError(f"CACHE_MISS: {audio.name} {start}..{start+duration}")
    # Decode directly to bounded PCM; no intermediate lossy M4A re-encoding.
    import numpy as np
    t0 = time.perf_counter()
    prefetched = self.take_prefetched(audio, start, duration, key)
    try:
      if isinstance(prefetched, AudioDecodeIssue):
        raise prefetched
      pcm_bytes, decode_report = prefetched or decode_pcm(
        audio, start, duration, self.root/(key+".decode.json"), params, tolerant=self.tolerant_decode)
    except AudioDecodeIssue as exc:
      if not self.tolerant_decode:
        raise
      # Preserve the rest of the book. This row is unobserved audio, not a
      # fabricated transcript and never eligible for highlighting or coverage.
      raw = [{"start": start, "end": start+duration, "text": "",
        "decodeUnavailable": True, "timingRejected": True}]
      self.diagnostics.append({"reason": "DECODE_UNAVAILABLE", "start": start, "end": start+duration,
        "sourceSha256": sha, "evidencePath": exc.evidence_path})
      atomic_json(self.root/(key+".json"), {"parameters": params, "segments": raw,
        "rawSegments": raw, "decodedEnd": start+duration,
        "decodeAudit": {"status": "QUARANTINE", "evidencePath": exc.evidence_path}})
      self.stats["unavailableDecodeAudioSeconds"] += duration
      self.native_index.register(self.root/(key+'.json'), params)
      return raw
    pcm = np.frombuffer(pcm_bytes, dtype="<f4").copy()
    decoded_end = decode_report.get("timelineEnd", min(start+duration, start+len(pcm)/16000))
    if decode_report["status"] == "RECOVERED_WITH_TIMELINE_MAP":
      self.diagnostics.append({"reason": "DECODE_RECOVERED_WITH_FRAME_PTS", "start": start,
        "end": start+duration, "sourceSha256": sha, "timingMap": decode_report["timingMap"]})
    self.stats["decodeSeconds"] += time.perf_counter()-t0
    t0 = time.perf_counter()
    if self.asr_engine in ("words", "batch") and decode_report["status"] != "RECOVERED_WITH_TIMELINE_MAP":
      if self.asr_engine == "words":
        raw_rows, words = self.transcribe_words_batched(pcm, sha, start, duration)
        if raw_rows is not None:
          self.stats["batchAsrAudioSeconds"] += duration
          self.stats["asrSeconds"] += time.perf_counter()-t0
          return self.persist_rows(raw_rows, params, key, start, duration, decoded_end, decode_report, sha, words=words)
      else:
        raw_rows = self.transcribe_batched(pcm, sha, start, duration)
        if raw_rows is not None:
          self.stats["batchAsrAudioSeconds"] += duration
          self.stats["asrSeconds"] += time.perf_counter()-t0
          return self.persist_rows(raw_rows, params, key, start, duration, decoded_end, decode_report, sha)
    result = transcription_backend()(pcm, path_or_hf_repo=str(resolve_model_path()),
      language="en", word_timestamps=False, condition_on_previous_text=False, verbose=False, fp16=True)
    self.stats["asrSeconds"] += time.perf_counter()-t0
    raw_rows = [{"start": start+s["start"] if type(s.get("start")) in (int, float) else None,
      "end": start+s["end"] if type(s.get("end")) in (int, float) else None, "text": s.get("text")}
      for s in result.get("segments", [])]
    if "timingMap" in decode_report:
      raw_rows = remap_segments(raw_rows, decode_report["timingMap"])
    return self.persist_rows(raw_rows, params, key, start, duration, decoded_end, decode_report, sha)

  def transcribe_words_batched(self, pcm, sha, start, duration):
    """Batched decoding producing both segment rows and word-level timestamps."""
    from tools.readalong_fast.batch_asr import BATCH_SIZE, cuts_sha, silence_cuts, window_bounds
    from tools.readalong_fast.batch_words_asr import batch_words_params, rebuild_global_words_and_segments
    from mlx_whisperx.backend.mlx_whisper.transcribe import transcribe_chunks_batched
    from mlx_whisperx.backend.mlx_whisper.tokenizer import get_tokenizer
    cuts = silence_cuts(pcm)
    if len(cuts) < 2:
      return None, None
    bounds = window_bounds(cuts, len(pcm))
    tokenizer = get_tokenizer(False, language="en")
    outputs = transcribe_chunks_batched([pcm[a:b] for a, b in bounds], batch_size=BATCH_SIZE,
      path_or_hf_repo=str(resolve_model_path()), language="en",
      word_timestamps=True, fp16=True)
    rows, words, past_end = rebuild_global_words_and_segments(
      outputs, bounds, start, start+len(pcm)/16000,
      tokenizer.timestamp_begin, tokenizer.eot, tokenizer.decode)
    self.diagnostics.append({"reason": "BATCH_WINDOW_GEOMETRY", "start": start, "end": start+duration,
      "sourceSha256": sha, "engine": batch_words_params(sha, self.model_sha, start, duration)["engine"],
      "windowCount": len(bounds), "cutsSha256": cuts_sha(cuts),
      "timestampPastWindowEndCount": past_end, "wordsCount": len(words)})
    return rows, words

  def transcribe_batched(self, pcm, sha, start, duration):
    """Segment rows from batched decoding, or None when the block is too short.

    Batched timestamps are window-relative, so windows must not overlap: that is
    what made the earlier attempt produce impossible global times."""
    from tools.readalong_fast.batch_asr import (BATCH_SIZE, batch_params, cuts_sha,
      rebuild_global_rows, silence_cuts, window_bounds)
    from mlx_whisperx.backend.mlx_whisper.transcribe import transcribe_chunks_batched
    from mlx_whisperx.backend.mlx_whisper.tokenizer import get_tokenizer
    cuts = silence_cuts(pcm)
    if len(cuts) < 2:
      return None
    bounds = window_bounds(cuts, len(pcm))
    tokenizer = get_tokenizer(False, language="en")
    outputs = transcribe_chunks_batched([pcm[a:b] for a, b in bounds], batch_size=BATCH_SIZE,
      path_or_hf_repo=str(resolve_model_path()), language="en",
      word_timestamps=False, fp16=True)
    rows, past_end = rebuild_global_rows(outputs, bounds, start, start+len(pcm)/16000,
      tokenizer.timestamp_begin, tokenizer.eot, tokenizer.decode)
    self.diagnostics.append({"reason": "BATCH_WINDOW_GEOMETRY", "start": start, "end": start+duration,
      "sourceSha256": sha, "engine": batch_params(sha, self.model_sha, start, duration)["engine"],
      "windowCount": len(bounds), "cutsSha256": cuts_sha(cuts),
      "timestampPastWindowEndCount": past_end})
    return rows

  def persist_rows(self, raw_rows, params, key, start, duration, decoded_end, decode_report, sha, words=None):
    """Shared evidence and normalization tail for every ASR engine."""
    # Preserve evidence before normalization, including rejected/padded output.
    raw_payload = {"parameters": params, "decodedEnd": decoded_end, "segments": json_safe(raw_rows)}
    if words is not None:
      raw_payload["words"] = json_safe(words)
    atomic_json(self.root/(key+".raw.json"), raw_payload)
    rows, diagnostics = normalize_native(raw_rows, start, decoded_end)
    self.diagnostics.extend({**d, "cachePath": str(self.root/(key+".raw.json")), "sourceSha256": sha,
      "requestedStart": start, "requestedEnd": start+duration} for d in diagnostics)
    payload = {"parameters": params, "segments": rows,
      "rawSegments": json_safe(raw_rows), "decodedEnd": decoded_end, "diagnostics": diagnostics,
      "decodeAudit": {"status": decode_report["status"], "timingMap": decode_report.get("timingMap"),
        "evidencePath": str(self.root/(key+".decode.json"))}}
    if words is not None:
      payload["words"] = json_safe(words)
    atomic_json(self.root/(key+".json"), payload)
    self.stats["newAsrAudioSeconds"] += duration
    self.native_index.register(self.root/(key+'.json'), params)
    return context_units(rows)


def is_spoken_apparatus(text, start_sec=None):
  """Classify non-body spoken announcements (LibriVox credits, stage directions, track headings)."""
  if not isinstance(text, str):
    return True
  t = text.lower().strip()
  if re.search(r"(.)\1{8,}", t) or "hahahaha" in t:
    return True
  if any(p in t for p in (
      "librivox", "libra box", "librabox", "libra vach", "libby vox", "liberal fox", "leap of ox",
      "public domain", "volunteer", "read by", "red by", "bread by", "reads by", "end of act",
      "persons represented", "recorded for this play", "sound-y-faire",
      "room in a cottage", "room in the palace", "apartment in the", "street before", "olivia's house",
      "this is audible", "brought to you by penguin",
  )):
    return True
  toks = tokens(text)
  if not toks:
    return True
  if len(toks) <= 16 and any(w in toks for w in (
      "act", "scene", "seen", "enter", "exit", "exeunt", "exhale", "excient", "flourish",
      "alarum", "sennet", "retire", "sonnet", "sonet", "sonnets", "music", "prologue", "epilogue", "chapter",
  )):
    return True
  if start_sec is not None and start_sec < 60.0:
    if any(w in toks for w in (
        "act", "scene", "seen", "sonnet", "sonet", "chapter", "palace", "athens",
        "illyria", "venice", "verona", "elsinore", "macbeth", "tempest", "twelfth", "midsummer", "summonite",
    )):
      return True
  return False


def detect_edition_front_back_ranges(units, mapped_ids, sources):
  """Identify >=180s audio-only edition preambles/forewords/afterwords in front 16% / back 12% of books >=1h."""
  total_phys = sum(s["duration"] for s in sources.values())
  if total_phys < 3600:
    return {}
  by_sid = defaultdict(list)
  for u in units:
    if not u.get("decodeUnavailable"):
      by_sid[u["audioSourceId"]].append(u)
  ranges = defaultdict(list)
  for sid, source in sources.items():
    dur = source["duration"]
    u_list = sorted(by_sid.get(sid, []), key=lambda x: x["start"])
    if not u_list:
      continue
    front_limit = max(600.0, dur * 0.16)
    back_limit = min(max(0.0, dur - 600.0), dur * 0.88)
    for zone_units in (
      [u for u in u_list if u["end"] <= front_limit],
      [u for u in u_list if u["start"] >= back_limit],
    ):
      if not zone_units:
        continue
      # Split zone_units whenever there is a sustained mapped run (>= 90s with >= 70% mapped)
      n = len(zone_units)
      in_sustained_mapped = [False] * n
      i = 0
      while i < n:
        j = i
        sp_sum = map_sum = 0.0
        while j < n:
          d = max(0.0, zone_units[j]["end"] - zone_units[j]["start"])
          if zone_units[j]["id"] in mapped_ids:
            sp_sum += d
            map_sum += d
            j += 1
          elif d <= 15.0 and j + 1 < n and zone_units[j + 1]["id"] in mapped_ids:
            sp_sum += d
            j += 1
          else:
            break
        if map_sum >= 90.0 and sp_sum > 0 and map_sum / sp_sum >= 0.70:
          for k in range(i, j):
            in_sustained_mapped[k] = True
          i = j
        else:
          i += 1
      b_start = None
      b_end = None
      b_sp = b_map = 0.0
      for idx_u, u in enumerate(zone_units):
        if not in_sustained_mapped[idx_u]:
          if b_start is None:
            b_start = u["start"]
          b_end = u["end"]
          d = max(0.0, u["end"] - u["start"])
          b_sp += d
          if u["id"] in mapped_ids:
            b_map += d
        else:
          if b_start is not None and b_end - b_start >= 180.0 and (b_sp == 0 or b_map / b_sp < 0.25):
            ranges[sid].append((0.0 if b_start < 30.0 else b_start, b_end))
          b_start = b_end = None
          b_sp = b_map = 0.0
      if b_start is not None and b_end - b_start >= 180.0 and (b_sp == 0 or b_map / b_sp < 0.25):
        ranges[sid].append((0.0 if b_start < 30.0 else b_start, dur if dur - b_end < 30.0 else b_end))
  return dict(ranges)


def audit_candidate(timeline, units, sources, docs, paragraphs, material=None, source_fingerprint=None):
  """One practical audit, no signatures or strict acoustic certification."""
  errors, previous, seen = [], {}, set()
  policy_errors = []
  try:
    scopes = material_ranges(material, sources, source_fingerprint)
  except ValueError as exc:
    scopes = {}
    errors.append("MATERIAL_POLICY_INVALID")
    policy_errors.append(str(exc))
  parsed = {}
  for name, soup in docs.items():
    parser = DOMFragmentExtractor()
    parser.feed(str(soup))
    parser.close()
    parsed["text/"+name] = parser
    if parser.duplicate_ids:
      errors.append("DUPLICATE_DOM_ID")
  for seg in timeline:
    sid = seg["audioSourceId"]
    if sid not in sources or not 0 <= seg["start"] < seg["end"] <= sources[sid]["duration"]+.001:
      errors.append("INVALID_INTERVAL")
      continue
    if seg["start"] < previous.get(sid, 0):
      errors.append("TIMESTAMP_OVERLAP")
    previous[sid] = seg["end"]
    parser = parsed.get(seg["document"])
    if not parser or canonical_text(parser.id_to_text.get(seg["fragment"], "")) != canonical_text(seg["text"]):
      errors.append("DOM_REFERENCE_BROKEN")
    identity = (sid, seg["document"], seg["fragment"], seg["occurrenceId"])
    if identity in seen:
      errors.append("DUPLICATE_OCCURRENCE")
    seen.add(identity)
  mapped_ids = {s["speechUnitId"] for s in timeline if "speechUnitId" in s}
  # Sentence-level coverage: also consider speech units intersected by aligned segments
  for seg in timeline:
    sid = seg["audioSourceId"]
    s_a, s_b = seg["start"], seg["end"]
    for unit in units:
      if unit["audioSourceId"] == sid and not (unit["end"] <= s_a or unit["start"] >= s_b):
        mapped_ids.add(unit["id"])
  spoken = missing = material_seconds = unavailable = 0.0
  max_missing = 0.0
  tr_spoken = defaultdict(float)
  tr_missing = defaultdict(float)
  for unit in units:
    a, b = unit["start"], unit["end"]
    sid = unit["audioSourceId"]
    if unit.get("decodeUnavailable"):
      unavailable += b-a
      continue
    remaining = subtract_ranges(a, b, scopes.get(sid, []))
    duration = sum(end-start for start, end in remaining)
    excluded = b-a-duration
    if unit["id"] not in mapped_ids and unit.get("nonBodyApparatus"):
      material_seconds += b-a
      continue
    spoken += duration
    material_seconds += excluded
    tr_spoken[sid] += duration
    if unit["id"] not in mapped_ids:
      missing += duration
      tr_missing[sid] += duration
      max_missing = max([max_missing]+[end-start for start, end in remaining])
  # Compute per-track alignment breakdown (supporting anthologies with partial/out-of-order stories)
  aligned_tracks, unaligned_tracks = [], []
  for sid, source in sources.items():
    sp = tr_spoken[sid]
    unm = tr_missing[sid]
    mp = max(0.0, sp-unm)
    ur = unm/sp if sp > 0 else 1.0
    row_info = {"audioSourceId": sid, "duration": source["duration"],
                "mappedSpeechSeconds": mp, "unmappedSpeechSeconds": unm, "unmappedSpeechRatio": ur}
    if sp > 0 and ur <= 0.10:
      aligned_tracks.append({**row_info, "status": "ALIGNED"})
    else:
      unaligned_tracks.append({**row_info, "status": "UNALIGNED"})
  aligned_sp = sum(t["mappedSpeechSeconds"]+t["unmappedSpeechSeconds"] for t in aligned_tracks)
  aligned_unm = sum(t["unmappedSpeechSeconds"] for t in aligned_tracks)
  aligned_tracks_ratio = aligned_unm/aligned_sp if aligned_sp > 0 else None
  # Also compute main-body unmapped ratio excluding unmapped front/back edition bonus intervals (>=180s at track start/end)
  body_spoken, body_missing = spoken, missing
  total_phys = sum(s["duration"] for s in sources.values())
  if total_phys >= 3600:
    front_back_ranges = defaultdict(list, detect_edition_front_back_ranges(units, mapped_ids, sources))
    by_sid_segs = defaultdict(list)
    for seg in timeline:
      by_sid_segs[seg["audioSourceId"]].append(seg)
    for sid, source in sources.items():
      srows = sorted(by_sid_segs.get(sid, []), key=lambda s: s["start"])
      if srows:
        if srows[0]["start"] >= 180:
          front_back_ranges[sid].append((0.0, srows[0]["start"]))
        if source["duration"]-srows[-1]["end"] >= 180:
          front_back_ranges[sid].append((srows[-1]["end"], source["duration"]))
    if front_back_ranges:
      b_sp = b_unm = 0.0
      for unit in units:
        if unit.get("decodeUnavailable") or (unit["id"] not in mapped_ids and unit.get("nonBodyApparatus")):
          continue
        sid = unit["audioSourceId"]
        comb_scopes = list(scopes.get(sid, []))+front_back_ranges.get(sid, [])
        rem = subtract_ranges(unit["start"], unit["end"], comb_scopes)
        d = sum(e-s for s, e in rem)
        b_sp += d
        if unit["id"] not in mapped_ids:
          b_unm += d
      if b_sp >= spoken*0.70 and b_sp > 0:
        body_spoken, body_missing = b_sp, b_unm
  body_ratio = body_missing/body_spoken if body_spoken > 0 else None
  # Unobserved long regions are not automatically assumed to be silence/credits.
  raw_gaps, empty_tracks, excluded_tracks = [], [], []
  for sid, source in sources.items():
    rows = sorted((s for s in timeline if s["audioSourceId"] == sid), key=lambda s: s["start"])
    if not rows:
      if subtract_ranges(0, source["duration"], scopes.get(sid, [])):
        empty_tracks.append(sid)
      else:
        excluded_tracks.append(sid)
    edge = 0.0
    for row in rows+[{"start": source["duration"], "end": source["duration"]}]:
      if row["start"] > edge:
        raw_gaps.append({"audioSourceId": sid, "start": edge, "end": row["start"]})
      edge = max(edge, row["end"])
  serious_gaps = []
  for gap in raw_gaps:
    remaining = subtract_ranges(gap["start"], gap["end"], scopes.get(gap["audioSourceId"], []))
    for a, b in remaining:
      if b-a > 60:
        serious_gaps.append({"audioSourceId": gap["audioSourceId"], "start": a, "end": b,
          "unexplainedSeconds": b-a})
  ratio = missing/spoken if spoken > 0 else None
  anthology_partial_ok = (len(sources) >= 5 and len(aligned_tracks) >= 5
                          and aligned_tracks_ratio is not None and aligned_tracks_ratio <= .05)
  body_edition_ok = (total_phys >= 3600 and (
      (body_ratio is not None and body_ratio <= .06) or (ratio is not None and ratio <= .06)))
  minor_decode_ok = (unavailable > 0 and total_phys >= 3600 and unavailable/max(1.0, total_phys) <= .20
                     and ratio is not None and ratio <= .05)
  if errors:
    status = "SCRIPT_ERROR"
  elif ratio is None:
    status = "REVIEW_MAPPING"
  elif (unavailable and not minor_decode_ok) or (
      ratio > .05 and not anthology_partial_ok and not body_edition_ok
  ) or (empty_tracks and not anthology_partial_ok):
    status = "REVIEW_MAPPING"
  elif not anthology_partial_ok and not body_edition_ok and not minor_decode_ok and (max_missing > 45 or serious_gaps) and ratio > .05:
    status = "REVIEW_MAPPING"
  else:
    status = "USABLE_WITH_GAPS" if (missing or raw_gaps or material or unavailable or unaligned_tracks) else "USABLE"
  return {"readalongUsability": status, "certificationStatus": "NOT_REQUESTED",
    "granularity": "paragraph-context", "acousticAccuracyVerified": False,
    "metrics": {"observedSpeechUnitSeconds": spoken, "unmappedSpeechUnitSeconds": missing,
      "unmappedSpeechUnitRatio": ratio, "bodyUnmappedSpeechUnitRatio": body_ratio,
      "alignedTracksUnmappedRatio": aligned_tracks_ratio,
      "alignedTrackCount": len(aligned_tracks), "unalignedTrackCount": len(unaligned_tracks),
      "materialSpeechSeconds": material_seconds,
      "maxUnmappedSpeechUnitSeconds": max_missing, "emptyTracks": empty_tracks,
      "fullyExcludedTracks": excluded_tracks,
      "unobservedDecodeSeconds": unavailable,
      "timelineSegments": len(timeline), "paragraphs": len(paragraphs)},
    "trackAlignmentSummary": {
      "totalTracks": len(sources),
      "alignedTrackCount": len(aligned_tracks),
      "unalignedTrackCount": len(unaligned_tracks),
      "alignedTracks": aligned_tracks,
      "unalignedTracks": unaligned_tracks,
    },
    "errors": errors, "policyErrors": policy_errors,
    "materialIntervalsApplied": [{"audioSourceId": sid, "start": a, "end": b} for sid, ranges in scopes.items() for a, b in ranges],
    "rawUnmappedIntervals": raw_gaps, "longUnexplainedIntervals": serious_gaps,
    "note": "ASR speech-unit coverage estimate, not measured word accuracy; paragraph highlighting is approximate"}


def sample_screen(cache, index, specs, cap, timings):
  """Estimate the unmapped ratio from real cache blocks before a full run.

  Samples are the same blocks a full run would use, so they are cache hits
  later rather than throwaway probes. A decisive verdict needs every sampled
  block to agree, because a wrong SAMPLE_MISMATCH silently drops a usable book.
  Returns (verdict, detail, evidence rows); the caller decides what to do.

  Sampling is not overhead on a book that goes on to run: the blocks it reads are
  the full run's own blocks, so the run does that much less ASR. The only true
  overhead is the uncursored matching and bootstrap below, reported separately as
  `screenOverheadSeconds`; `screenSeconds` is wall clock and is not comparable."""
  from tools.readalong_fast.sampling import (classify, extend_strata, stratified_blocks,
    MIN_BLOCK_TOKENS, MIN_SAMPLE_TOKENS, MAX_SAMPLE_BLOCKS, verdict_runs_full_book)
  tracks = [{"audioSourceId": sid, "duration": duration} for _, sid, _, duration in specs]
  by_id = {sid: (audio, sha) for audio, sid, sha, _ in specs}
  plan = stratified_blocks(tracks)
  rows_out, samples = [], []
  asr_before = cache.stats["asrSeconds"]
  decode_before = cache.stats["decodeSeconds"]
  match_seconds = 0.0

  def measure(spec):
    """One stratum's located/missing seconds, matched uncursored inside the window."""
    audio, sha = by_id[spec["audioSourceId"]]
    block = cache.chunk(audio, sha, spec["start"], spec["duration"])
    window = [r for r in block if r["end"] > spec["measureStart"]
              and r["start"] < spec["measureStart"]+spec["measureDuration"]]
    observed = missing = 0.0
    t0 = time.perf_counter()
    for row in window:
      if row.get("timingRejected"):
        continue
      span = row["end"]-row["start"]
      if span <= 0:
        continue
      observed += span
      if index.locate_detailed(row["text"], None)["match"] is None:
        missing += span
    elapsed = time.perf_counter()-t0
    token_count = sum(len(tokens(r["text"])) for r in window)
    sample = {"observedSeconds": observed, "missingSeconds": missing, "tokens": token_count}
    row = {"audioSourceId": spec["audioSourceId"], "start": spec["start"],
      "duration": spec["duration"], "measureStart": spec["measureStart"],
      "measureDuration": spec["measureDuration"], "observedSeconds": observed,
      "missingSeconds": missing, "tokenCount": token_count,
      "locatedRatio": (1-missing/observed) if observed > 0 else None,
      "textSample": " ".join(r["text"] for r in window if not r.get("timingRejected"))[:600]}
    return sample, row, elapsed

  for spec in plan:
    sample, row, elapsed = measure(spec)
    # Silence and music carry no evidence, so they neither add tokens nor count
    # toward the block count a decisive verdict needs.
    if sample["tokens"] < MIN_BLOCK_TOKENS:
      continue
    samples.append(sample)
    rows_out.append(row)
    match_seconds += elapsed
  # A book of many short tracks can be decisive yet thin: 179 whole tracks of
  # 28-120s each total ~860 tokens, below the floor. Append neighbouring strata
  # until the total is met; the extra tracks are short, so the cost is small.
  if sum(s["tokens"] for s in samples) < MIN_SAMPLE_TOKENS:
    for spec in extend_strata(tracks, plan, MAX_SAMPLE_BLOCKS):
      sample, row, elapsed = measure(spec)
      if sample["tokens"] < MIN_BLOCK_TOKENS:
        continue
      samples.append(sample)
      rows_out.append(row)
      match_seconds += elapsed
      if sum(s["tokens"] for s in samples) >= MIN_SAMPLE_TOKENS:
        break
  t0 = time.perf_counter()
  verdict, detail = classify(samples)
  match_seconds += time.perf_counter()-t0
  timings["screenAsrSeconds"] = cache.stats["asrSeconds"]-asr_before
  timings["screenDecodeSeconds"] = cache.stats["decodeSeconds"]-decode_before
  timings["screenMatchSeconds"] = match_seconds
  return verdict, detail, rows_out


def _published_readalong(book):
  """True when the book already carries a follow-along entry that a run published.

  A bare `readalongEnabled: true` is not enough to call a book live: the entry a
  real publication writes also carries `practicalRelease`, so that is what marks
  a book as retractable-or-not."""
  entry = Path(book)/"readalong/readalong.manifest.json"
  if not entry.is_file():
    return False
  try:
    manifest = json.loads(entry.read_text())
  except (OSError, ValueError):
    return True
  return manifest.get("readalongEnabled") is not False and "practicalRelease" in manifest


def auto_exclude_mismatch(book, detail, verdict):
  """Switch follow-along off for a book whose audio and text editions do not match.

  Guardrail: a book already published with follow-along on is reported, never
  switched off, because a screening run must not retract a live book. The receipt
  is the one the `exclude-practical` command writes, so both paths agree."""
  if _published_readalong(book):
    return {"registered": False, "reason": "PUBLISHED_BOOK_NOT_AUTO_EXCLUDED"}
  reason = (f"SCREEN_{verdict}: sampled located ratio {detail.get('locatedRatio')!r}, "
            f"bootstrap located upper bound {detail.get('locatedUpper')!r}, "
            f"highest block {detail.get('maxBlockLocatedRatio')!r} over "
            f"{detail.get('blocks')} blocks")
  from tools.readalong.practical_publisher import exclude_readalong
  result = exclude_readalong(book, reason)
  return {"registered": bool(result.get("success")), "action": result.get("action"),
          "reason": reason, "result": result}


def generate(unit, output, cache, inputs, material=None, screen=True):
  start = time.perf_counter()
  if not unit.get("epubs") or not unit.get("audio_tracks"):
    raise ValueError("An EPUB and nonempty audio inventory are required")
  book, output = Path(unit["book_dir"]).resolve(strict=True), Path(output).resolve()
  verify_track_inventory(book, unit['audio_tracks'])
  require_candidate_output(book, output)
  if output.is_relative_to(book):
    raise ValueError("Candidate must remain outside the source book")
  old_cache_stats = cache.stats.copy()
  diagnostic_start = len(cache.diagnostics)
  if len(unit['epubs']) > 1:
    from tools.readalong_fast.pairing import pair_epubs
    unit = pair_epubs(unit, output, cache, inputs)
  records = unit["audio_tracks"]+unit["epubs"]
  t0 = time.perf_counter()
  before = {}
  for row in records:
    if (book/row["rel_to_book"]).is_symlink():
      raise ValueError("Linked input is not permitted")
    path = safe_path(book, row["rel_to_book"])
    before[path] = inputs.verify(path, row["sha256"])
  source_hash = hashlib.sha256(json.dumps({r["rel_to_book"]: r["sha256"] for r in records}, sort_keys=True).encode()).hexdigest()
  if material and material["sourceFingerprint"] != source_hash:
    raise RuntimeError("SOURCE_CHANGED: material policy binding mismatch")
  timings = {"inputVerificationSeconds": time.perf_counter()-t0}
  active = book/"readalong"
  active_stat = {str(p): stat_key(p) for p in active.rglob("*") if p.is_file()} if active.exists() else {}
  registered_exclusion = False
  output.mkdir(parents=True, exist_ok=True)
  try:
    t0 = time.perf_counter()
    epub = safe_path(book, unit["epubs"][0]["rel_to_book"])
    text_root = output/"text"
    safe_extract_epub(epub, text_root)
    spine = get_spine_htmls(epub)
    document_diagnostics = []
    docs, paragraphs, book_tokens = prepare_paragraphs(text_root, spine, document_diagnostics)
    index = ParagraphIndex(book_tokens, paragraphs)
    timings["epubAndIndexSeconds"] = time.perf_counter()-t0
    sources, speech = {}, []
    cap = max(t["measured_duration"] for t in unit["audio_tracks"])+1
    specs = []
    for row in unit["audio_tracks"]:
      sid, duration = row["rel_to_book"], row["measured_duration"]
      if type(duration) not in (int, float) or not math.isfinite(duration) or duration <= 0:
        raise ValueError("Invalid inventory duration")
      audio = safe_path(book, sid)
      if duration > 1800:
        duration = inputs.duration(audio, duration)
      sources[sid] = {"id": sid, "name": audio.name, "duration": duration, "sha256": row["sha256"],
                      "alistPath": alist_audio_path(book, audio, "/750HD/有声书")}
      specs.append((audio, sid, row["sha256"], duration))
    material_ranges(material, sources, source_hash)
    screen_rows = []
    screen_verdict = None
    screen_detail = None
    if screen:
      t0 = time.perf_counter()
      screen_verdict, screen_detail, screen_rows = sample_screen(cache, index, specs, cap, timings)
      timings["screenSeconds"] = time.perf_counter()-t0
      # Screening's non-ASR cost: the part a full run would not have paid anyway.
      timings["screenOverheadSeconds"] = timings.get("screenMatchSeconds", 0.0)
      if not verdict_runs_full_book(screen_verdict):
        # A confirmed mismatch means the sampled blocks carried no located speech.
        # Register it now, unless the book is already published: a screening run
        # must never retract a live book, so that case is reported instead.
        registration = auto_exclude_mismatch(book, screen_detail, screen_verdict)
        registered_exclusion = bool(registration.get("registered"))
        report = {"readalongUsability": "REVIEW_MAPPING", "certificationStatus": "NOT_REQUESTED",
          "stage": "SCREEN_REVIEW", "fullAudioProcessed": False, "published": False,
          "materialMismatchConfirmed": True, "metrics": {"distributedSamples": len(screen_rows),
          "locatedSamples": sum(1 for r in screen_rows if (r["locatedRatio"] or 0) > 0)},
          "screenDecision": screen_verdict, "screenDetail": screen_detail,
          "materialAssessment": "MISMATCH_CONFIRMED",
          "autoRegistration": registration,
          "recommendedAction": "EXCLUDE_PRACTICAL_CANDIDATE",
          "screenEvidence": screen_rows, "sourceFingerprint": source_hash, "listeningVerified": False,
          "note": "Every sampled block carried no located speech; the audio and text editions appear incompatible",
          "timings": {**timings, "totalSeconds": time.perf_counter()-start},
          "speechCacheStats": dict(cache.stats-old_cache_stats), "matchingStats": dict(index.metrics),
          "asrDiagnostics": cache.diagnostics[diagnostic_start:], "documentDiagnostics": document_diagnostics}
        atomic_json(output/"practical-audit.json", report)
        return report
    for audio, sid, sha, duration in specs:
      t0 = time.perf_counter()
      rows = cache.whole_legacy_track(audio, sha, duration, cap)
      if rows is None:
        rows = []
        blocks = list(plan_audio_blocks(duration, 1800))
        # Decode block n+1 while block n occupies the GPU. Blocks already
        # served by any cache are skipped so no wasted ffmpeg runs.
        pending = [(audio, a, length, sha) for a, length in blocks
                   if cache.needs_decode(audio, sha, a, length)]
        cache.start_prefetch([
          (audio, a, length,
           hashlib.sha256(json.dumps(cache.chunk_params(sha, a, length), sort_keys=True).encode()).hexdigest(),
           cache.chunk_params(sha, a, length))
          for _, a, length, _ in pending])
        try:
          for a, length in blocks:
            rows.extend(cache.chunk(audio, sha, a, length))
        finally:
          cache.stop_prefetch()
      timings["speechAndCacheSeconds"] = timings.get("speechAndCacheSeconds", 0)+time.perf_counter()-t0
      for r in rows:
        speech.append({**r, "audioSourceId": sid, "id": str(len(speech))})
    t0 = time.perf_counter()
    cursor, timeline, occurrences, unit_diagnostics = None, [], Counter(), []
    context_sid, last_match_document = None, None
    order_events = []
    last_physical_match, context_end = None, None
    queue, effective_speech = deque(speech), []
    while queue:
      heard = queue.popleft()
      if heard["audioSourceId"] != context_sid:
        # Playback order is authoritative. A new track is not evidence that
        # the next story follows the preceding EPUB chapter or repeated phrase.
        cursor, last_match_document, context_end = None, None, None
        context_sid = heard["audioSourceId"]
      elif context_end is not None and heard["start"]-context_end > 60:
        # An old chapter is not safe disambiguation evidence after a long gap.
        cursor, last_match_document, context_end = None, None, None
      if heard.get("timingRejected"):
        effective_speech.append(heard)
        unit_diagnostics.append({"speechUnitId": heard["id"], "reason": "ASR_TIMING_REJECTED"})
        continue
      outcome = index.locate_detailed(heard["text"], cursor)
      match = outcome["match"]
      if not match and cursor is None and last_physical_match is not None and outcome["diagnostic"].get("reason") != "AMBIGUOUS_MATCH":
        fallback_outcome = index.locate_detailed(heard["text"], last_physical_match["tokenEnd"])
        if fallback_outcome["match"] is not None:
          outcome = fallback_outcome
          match = outcome["match"]
      if not match and len(heard.get("parts", [])) > 1:
        # Retry only original observed boundaries; never interpolate word times.
        parts = checked_units(heard["parts"], heard["start"], heard["end"])
        queue.extendleft(reversed([{**p, "audioSourceId": heard["audioSourceId"],
          "id": heard["id"]+"/"+str(i)} for i, p in enumerate(parts)]))
        index.metrics["observedBoundaryFallbacks"] += 1
        unit_diagnostics.append({"speechUnitId": heard["id"], "audioSourceId": heard["audioSourceId"],
          "start": heard["start"], "end": heard["end"], "reason": "OBSERVED_BOUNDARY_FALLBACK",
          "matchDiagnostic": outcome["diagnostic"]})
        continue
      if not match and is_spoken_apparatus(heard["text"], heard["start"]):
        heard = {**heard, "nonBodyApparatus": True}
      effective_speech.append(heard)
      if not match:
        unit_diagnostics.append({"speechUnitId": heard["id"], "audioSourceId": heard["audioSourceId"],
          "start": heard["start"], "end": heard["end"], "reason": outcome["diagnostic"]["reason"],
          "matchDiagnostic": outcome["diagnostic"]})
        continue
      para = match["paragraph"]
      if (last_physical_match is not None and last_physical_match["audioSourceId"] != heard["audioSourceId"]
          and match["start"] < last_physical_match["tokenEnd"]-24):
        order_events.append({"audioSourceId": heard["audioSourceId"], "start": heard["start"],
          "end": heard["end"], "speechUnitId": heard["id"],
          "previousAudioSourceId": last_physical_match["audioSourceId"],
          "previousTokenEnd": last_physical_match["tokenEnd"], "matchedTokenStart": match["start"],
          "fromDocument": last_physical_match["document"], "toDocument": para["document"],
          "reason": "TRACK_ORDER_DIFFERS_FROM_TEXT",
          "note": "Confident text locations move backward across tracks; preserve audio playback order"})
      if cursor is not None and (match["start"] < cursor-24 or match["start"] > cursor+2000):
        order_events.append({"audioSourceId": heard["audioSourceId"], "start": heard["start"],
          "end": heard["end"], "speechUnitId": heard["id"], "previousTokenEnd": cursor,
          "matchedTokenStart": match["start"], "fromDocument": last_match_document,
          "toDocument": para["document"], "reason": "NONLINEAR_TEXT_RELOCATION",
          "note": "Observed text relocation; not proof of incompatible material or confirmed anthology order"})
      key = (heard["audioSourceId"], para["document"], para["fragment"])
      # Native ASR units may touch, but must never manufacture positive time.
      previous = timeline[-1] if timeline and timeline[-1]["audioSourceId"] == heard["audioSourceId"] else None
      a = heard["start"]
      if previous and a < previous["end"]:
        if previous["end"]-a > .05 or heard["end"] <= previous["end"]:
          unit_diagnostics.append({"speechUnitId": heard["id"], "reason": "OBSERVED_TIMING_CONFLICT"})
          continue
        a = previous["end"]
      seg = {"audioSourceId": heard["audioSourceId"], "start": a, "end": heard["end"],
        "document": para["document"], "fragment": para["fragment"], "text": para["text"],
        "occurrenceId": str(occurrences[key]), "speechUnitId": heard["id"],
        "timingStatus": "SEGMENT_TIMING_UNVERIFIED", "contextOnly": True,
        "localizationMethod": outcome["diagnostic"]["locationMode"],
        "lexicalMatchRatio": match["score"]}
      if a != heard["start"]:
        seg["observedInterval"] = {"start": heard["start"], "end": heard["end"]}
        seg["boundaryMethod"] = "bounded-start-trim-unverified"
      occurrences[key] += 1
      timeline.append(seg)
      cursor = match["end"]
      last_match_document = para["document"]
      context_end = heard["end"]
      last_physical_match = {"audioSourceId": heard["audioSourceId"], "document": para["document"],
                             "tokenEnd": match["end"]}
    timings["matchingSeconds"] = time.perf_counter()-t0
    if len(sources) >= 5:
      mapped_ids_pre = {s["speechUnitId"] for s in timeline}
      tr_sp_pre, tr_unm_pre = defaultdict(float), defaultdict(float)
      for u_row in effective_speech:
        if u_row.get("decodeUnavailable") or (u_row["id"] not in mapped_ids_pre and u_row.get("nonBodyApparatus")):
          continue
        d_pre = max(0.0, u_row["end"]-u_row["start"])
        tr_sp_pre[u_row["audioSourceId"]] += d_pre
        if u_row["id"] not in mapped_ids_pre:
          tr_unm_pre[u_row["audioSourceId"]] += d_pre
      good_sids = {sid for sid, sp in tr_sp_pre.items() if sp > 0 and tr_unm_pre[sid]/sp <= 0.10}
      bad_sids = {sid for sid, sp in tr_sp_pre.items() if sp > 0 and tr_unm_pre[sid]/sp > 0.30}
      if len(good_sids) >= 5 and bad_sids:
        timeline = [s for s in timeline if s["audioSourceId"] not in bad_sids]
    fb_ranges = detect_edition_front_back_ranges(effective_speech, {s["speechUnitId"] for s in timeline}, sources)
    if fb_ranges:
      timeline = [
        s for s in timeline
        if not any(a <= s["start"] and s["end"] <= b for a, b in fb_ranges.get(s["audioSourceId"], []))
      ]
    if cache.asr_engine == "words":
      from tools.readalong.stream_projection import prepare_documents, project_stream
      from tools.readalong_fast.sentence_aligner import refine_timeline_by_dom, merge_stream_projection_with_paragraph_fallback
      from tools.readalong.engine.mark_sentence import mark_sentences
      from tools.readalong.timeline_boundaries import resolve_boundaries
      # Collect all recognized words across tracks
      all_audio_words = []
      for audio, sid, sha, duration in specs:
        blocks = list(plan_audio_blocks(duration, 1800))
        for a, length in blocks:
          chunk_end = a + length
          for w in cache.chunk_words(audio, sha, a, length):
            w_copy = dict(w)
            w_copy["end"] = min(w_copy["end"], chunk_end)
            w_copy["start"] = min(w_copy["start"], w_copy["end"])
            all_audio_words.append({**w_copy, "audioSourceId": sid})
      track_order = {sid: idx for idx, (_, sid, _, _) in enumerate(specs)}
      all_audio_words.sort(key=lambda w: (track_order.get(w.get("audioSourceId", ""), 999), w.get("start", 0.0)))

      sent_docs, sent_fragments, sent_tokens = prepare_documents(text_root, spine, mark_sentences)
      # Refine only within a coarse paragraph match; preserve that anchor when
      # sentence-level word refinement has no reliable match.
      paragraph_refinement = refine_timeline_by_dom(timeline, sent_docs, all_audio_words,
        {sid: duration for _, sid, _, duration in specs})
      raw_segments, projection_stats = project_stream(sent_tokens, sent_fragments, all_audio_words)
      projected_timeline, repairs = resolve_boundaries(raw_segments)
      sentence_timeline = merge_stream_projection_with_paragraph_fallback(projected_timeline, paragraph_refinement)
      sentence_timeline, repairs = resolve_boundaries(sentence_timeline)

      # A paragraph fallback can retain the coarse ``fast-*`` anchor after
      # sentence marking replaced that wrapper with sentence spans. Rebind only
      # when the serialized DOM contains exactly one fragment with the same
      # canonical text; ambiguous text remains a fallback and is audited.
      dom_fragment_cache = {}
      track_durations = {sid: duration for _, sid, _, duration in specs}
      repaired_sentence_timeline = []
      for seg in sentence_timeline:
        sid = seg.get("audioSourceId")
        if sid in track_durations:
          seg["start"] = max(0.0, min(float(seg["start"]), track_durations[sid]))
          seg["end"] = max(0.0, min(float(seg["end"]), track_durations[sid]))
        doc_key = seg.get("document", "")
        doc_name = doc_key.removeprefix("text/")
        soup = sent_docs.get(doc_name) or sent_docs.get(doc_key)
        if soup is not None:
          cache_key = id(soup)
          if cache_key not in dom_fragment_cache:
            parser = DOMFragmentExtractor()
            parser.feed(str(soup))
            parser.close()
            by_text = defaultdict(list)
            for fragment, text in parser.id_to_text.items():
              by_text[canonical_text(text)].append(fragment)
            dom_fragment_cache[cache_key] = (parser, by_text)
          parser, by_text = dom_fragment_cache[cache_key]
          current = canonical_text(parser.id_to_text.get(seg.get("fragment", ""), ""))
          wanted = canonical_text(seg.get("text", ""))
          if current != wanted and wanted and len(by_text.get(wanted, [])) == 1:
            seg["fragment"] = by_text[wanted][0]
            seg["text"] = parser.id_to_text[seg["fragment"]]
        if seg.get("end", 0) > seg.get("start", 0):
          repaired_sentence_timeline.append(seg)
      sentence_timeline = repaired_sentence_timeline

      for s in sentence_timeline:
        s.setdefault("occurrenceId", "0")
        s.setdefault("speechUnitId", f"{s['audioSourceId']}:{s['start']}")

      from tools.readalong.exporter import READALONG_CSS_INJECTION
      for name, soup in sent_docs.items():
        if not soup.head:
          head = soup.new_tag("head")
          (soup.html or soup).insert(0, head)
        if not soup.head.find("style", attrs={"data-readalong": "active"}):
          style = soup.new_tag("style")
          style["data-readalong"] = "active"
          style.string = READALONG_CSS_INJECTION
          soup.head.append(style)
        safe_path(text_root, name).write_text(str(soup), encoding="utf-8")
      # Use the exact serialized DOM text for paragraph-wide fallback anchors;
      # this keeps the exported timeline and DOM audit on the same text source.
      fallback_text_cache = {}
      for seg in sentence_timeline:
        if seg.get("timingStatus") != "SENTENCE_FROM_PARAGRAPH":
          continue
        doc_key = seg.get("document", "")
        doc_name = doc_key.removeprefix("text/")
        soup = sent_docs.get(doc_name) or sent_docs.get(doc_key)
        if not soup:
          continue
        cache_key = id(soup)
        if cache_key not in fallback_text_cache:
          parser = DOMFragmentExtractor()
          parser.feed(str(soup))
          parser.close()
          fallback_text_cache[cache_key] = parser.id_to_text
        exact_text = fallback_text_cache[cache_key].get(seg.get("fragment"), "")
        if exact_text:
          seg["text"] = exact_text
      from tools.readalong.timeline_shards import write_timeline_payload
      timeline_fields = write_timeline_payload(output, sentence_timeline)
      atomic_json(output/"readalong.manifest.json", {"schemaVersion": 1,
        "bookId": book.name, "language": "en", "audioSources": list(sources.values()),
        **timeline_fields, "textRoot": "text/", "sampleAligned": False,
        "sourceEpubSha256": unit["epubs"][0]["sha256"], "segmentCount": len(sentence_timeline),
        "timing": {"engine": "mlx-batch-silence-words-v1", "granularity": "sentence"}})
      final_timeline = sentence_timeline
      final_docs = sent_docs
    else:
      for name, soup in docs.items():
        safe_path(text_root, name).write_text(str(soup), encoding="utf-8")
      from tools.readalong.timeline_shards import write_timeline_payload
      timeline_fields = write_timeline_payload(output, timeline)
      atomic_json(output/"readalong.manifest.json", {"schemaVersion": 1,
        "bookId": book.name, "language": "en", "audioSources": list(sources.values()),
        **timeline_fields, "textRoot": "text/", "sampleAligned": False,
        "sourceEpubSha256": unit["epubs"][0]["sha256"], "segmentCount": len(timeline),
        "timing": {"engine": "fast-paragraph-v1", "granularity": "paragraph-context"}})
      final_timeline = timeline
      final_docs = docs
    t0 = time.perf_counter()
    report = audit_candidate(final_timeline, effective_speech, sources, final_docs, paragraphs, material, source_hash)
    asr_diagnostics = cache.diagnostics[diagnostic_start:]
    decode_impacts = []
    for sid, source in sources.items():
      gaps = sorted((g['start'], g['end']) for d in asr_diagnostics
        if d['reason'] == 'DECODE_RECOVERED_WITH_FRAME_PTS' and d.get('sourceSha256') == source['sha256']
        for g in d['timingMap']['missingIntervals'])
      union = []
      for a, b in gaps:
        if union and a <= union[-1][1]:
          union[-1] = (union[-1][0], max(union[-1][1], b))
        else:
          union.append((a, b))
      decode_impacts.extend({'audioSourceId': sid, 'start': a, 'end': b, 'type': 'OBSERVED_FRAME_PTS_GAP'} for a, b in union)
    report['metrics']['observedDecodeLossSeconds'] = sum(g['end']-g['start'] for g in decode_impacts)
    report['decodeImpactIntervals'] = decode_impacts
    uncertain = [d for d in asr_diagnostics if d["reason"] in {"NONFINITE_OR_MISSING_TIME", "REVERSED_INTERVAL"}]
    if uncertain and report["readalongUsability"] in {"USABLE", "USABLE_WITH_GAPS"}:
      report["readalongUsability"] = "REVIEW_MAPPING"
    if asr_diagnostics and report["readalongUsability"] == "USABLE":
      report["readalongUsability"] = "USABLE_WITH_GAPS"
    timings["practicalAuditSeconds"] = time.perf_counter()-t0
    report.update(sourceFingerprint=source_hash, published=False, listeningVerified=False,
      fullAudioProcessed=not any(u.get("decodeUnavailable") for u in effective_speech), allTracksVisited=True,
      incompleteDecodeIntervals=[{"audioSourceId": u["audioSourceId"], "start": u["start"], "end": u["end"]}
        for u in effective_speech if u.get("decodeUnavailable")], screenEvidence=screen_rows,
      screenDecision=screen_verdict, screenDetail=screen_detail,
      textOrderEvents=order_events,
      localizationReasonCounts=dict(Counter(d["reason"] for d in unit_diagnostics)),
      timings=timings, matchingStats=dict(index.metrics), speechCacheStats=dict(cache.stats-old_cache_stats),
      unitDiagnostics=unit_diagnostics, asrDiagnostics=asr_diagnostics, documentDiagnostics=document_diagnostics)
    report["timings"]["totalSeconds"] = time.perf_counter()-start
    atomic_json(output/"practical-audit.json", report)
    return report
  finally:
    verify_track_inventory(book, unit['audio_tracks'])
    if any(stat_key(p) != state for p, state in before.items()):
      raise RuntimeError("SOURCE_CHANGED: original input stat changed during generation")
    after = {str(p): stat_key(p) for p in active.rglob("*") if p.is_file()} if active.exists() else {}
    changed_active = sorted(path for path in set(active_stat) | set(after)
      if active_stat.get(path) != after.get(path))
    if changed_active and not registered_exclusion:
      raise RuntimeError("SOURCE_CHANGED: active assets changed during generation: " + ", ".join(changed_active[:8]))
