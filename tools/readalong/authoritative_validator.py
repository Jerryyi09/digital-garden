"""Read-only fail-closed validation of a specific input and candidate revision."""
import json
import math
import re
import subprocess
import unicodedata
import wave
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

from tools.readalong.acoustic_evaluator import (
  POLICY_VERSION, occurrence_key, sha256, valid_interval, verify_reference,
)

ERROR_SCHEMA_INVALID = "ERR_SCHEMA_INVALID"
ERROR_TRACK_INVENTORY_MISMATCH = "ERR_TRACK_INVENTORY_MISMATCH"
ERROR_TIMESTAMP_OVERLAP = "ERR_TIMESTAMP_OVERLAP"
ERROR_TIMESTAMP_INVALID = "ERR_TIMESTAMP_INVALID"
ERROR_DOM_REFERENCE_BROKEN = "ERR_DOM_REFERENCE_BROKEN"
ERROR_UNEXPLAINED_GAP = "ERR_UNEXPLAINED_GAP"
ERROR_DENSITY_ABNORMAL = "ERR_DENSITY_ABNORMAL"
ERROR_SECURITY_VIOLATION = "ERR_SECURITY_VIOLATION"
ERROR_TIMING_UNVERIFIED = "ERR_TIMING_UNVERIFIED"
ERROR_DUPLICATE_DOM_ID = "ERR_DUPLICATE_DOM_ID"
ERROR_AUDIO_DURATION_MISMATCH = "ERR_AUDIO_DURATION_MISMATCH"
ERROR_AUDIO_SHA256_MISMATCH = "ERR_AUDIO_SHA256_MISMATCH"
AUDIO_SUFFIXES = {".mp3", ".m4a", ".m4b", ".wav"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}


class DOMFragmentExtractor(HTMLParser):
  """Collect complete subtrees, including void elements, without indexing comments."""
  def __init__(self):
    super().__init__(convert_charrefs=True)
    self.id_to_text, self.seen_ids, self.duplicate_ids = {}, set(), []
    self._stack = []

  def handle_starttag(self, tag, attrs):
    attrs = dict(attrs)
    fid = attrs.get("id")
    if fid is not None:
      if fid in self.seen_ids:
        self.duplicate_ids.append(fid)
      self.seen_ids.add(fid)
    if tag == "br":
      self.handle_data(" ")
    hidden = (tag in {"script", "style", "head"} or "hidden" in attrs
              or bool(re.search(r"display\s*:\s*none|visibility\s*:\s*hidden",
                                attrs.get("style", ""), re.I))
              or bool(self._stack and self._stack[-1]["hidden"]))
    entry = {"tag": tag, "id": fid, "chunks": [], "hidden": hidden}
    if tag in VOID:
      if fid is not None:
        self.id_to_text.setdefault(fid, "")
    else:
      self._stack.append(entry)

  def handle_startendtag(self, tag, attrs):
    self.handle_starttag(tag, attrs)
    if tag not in VOID:
      self.handle_endtag(tag)

  def handle_data(self, data):
    # Append in source order to every visible ancestor; never re-propagate on close.
    if self._stack and not self._stack[-1]["hidden"]:
      for entry in self._stack:
        if entry["id"] is not None and not entry["hidden"]:
          entry["chunks"].append(data)

  def handle_endtag(self, tag):
    for index in range(len(self._stack)-1, -1, -1):
      if self._stack[index]["tag"] == tag:
        for entry in self._stack[index:]:
          if entry["id"] is not None:
            self.id_to_text.setdefault(entry["id"], " ".join("".join(entry["chunks"]).split()))
        del self._stack[index:]
        break

  def close(self):
    super().close()
    # Optional HTML closing tags have the same accumulated subtree text.
    for entry in self._stack:
      if entry["id"] is not None:
        self.id_to_text.setdefault(entry["id"], " ".join("".join(entry["chunks"]).split()))
    self._stack.clear()


def compute_file_sha256(path):
  return sha256(path)


def probe_audio_duration(path):
  try:
    if Path(path).suffix.lower() == ".wav":
      with wave.open(str(path), "rb") as audio:
        frames = audio.getnframes()
        rate = audio.getframerate()
        # Reject truncated PCM fixtures, not just superficially valid headers.
        expected = frames * audio.getnchannels() * audio.getsampwidth()
        if len(audio.readframes(frames)) != expected:
          return 0.0
        return frames / rate if rate > 0 else 0.0
    raw = subprocess.check_output([
      "ffprobe", "-v", "error", "-show_entries", "format=duration",
      "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], stderr=subprocess.DEVNULL, timeout=30)
    duration = float(raw)
    return duration if math.isfinite(duration) and duration > 0 else 0.0
  except (OSError, ValueError, wave.Error, subprocess.SubprocessError):
    return 0.0


def canonical_text(text):
  return " ".join(unicodedata.normalize("NFKC", text).split())


def compute_token_overlap_ratio(a, b):
  # Legacy diagnostics only. Acceptance uses ordered complete text instead.
  x, y = set(re.findall(r"\w+", a.lower())), set(re.findall(r"\w+", b.lower()))
  return len(x & y) / len(x | y) if x and y else 0.0


def safe_path(root, name):
  if not isinstance(name, str) or not name or "\\" in name:
    raise ValueError("Missing or unsafe relative path")
  decoded = unquote(name)
  part = Path(decoded)
  if part.is_absolute() or ".." in part.parts:
    raise ValueError("Path traversal")
  path = (root / part).resolve()
  if not path.is_relative_to(root.resolve()) or path == root.resolve():
    raise ValueError("Path escapes root")
  return path


def _report(target):
  return {"book_id": Path(target).name, "path": str(target), "status": "FAILED",
          "policyVersion": POLICY_VERSION,
          "quality_layers": {k: False for k in
            ("schema", "inventory", "monotonicity", "dom_integrity",
             "coverage_and_gaps", "density", "timing_verified")},
          "errors": [], "warnings": [], "uncovered_intervals": [],
          "track_stats": {}, "summary": {}}


def audit_book_authoritative(target_dir, book_dir=None, exemptions=None, reference_path=None, *, source_evidence=None):
  report = _report(target_dir)
  try:
    return _audit(Path(target_dir), book_dir, exemptions, reference_path, report, source_evidence)
  except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
    report["errors"].append({"code": ERROR_SCHEMA_INVALID, "msg": str(exc)})
    report["status"] = "FAILED"
    report["certificationStatus"] = "FAILED"
    report["readalongUsability"] = "SCRIPT_ERROR"
    return report


def _audit(target, book_dir, exemptions, reference_path, report, source_evidence=None):
  target = target.resolve(strict=True)
  assets = target / "readalong" if (target / "readalong/readalong.manifest.json").is_file() else target
  # Never guess a sibling book. Staging away from the book requires explicit input.
  book = Path(book_dir).resolve(strict=True) if book_dir else (
    target if assets != target else target.parent)
  report["book_id"] = book.name
  manifest = json.loads((assets / "readalong.manifest.json").read_text())
  if not isinstance(manifest, dict) or type(manifest.get("schemaVersion")) is not int or manifest["schemaVersion"] != 1:
    raise ValueError("Invalid manifest schemaVersion")
  if "assetRevision" in manifest and (
      not isinstance(manifest["assetRevision"], str)
      or not re.fullmatch("[0-9a-f]{32}", manifest["assetRevision"])):
    raise ValueError("Invalid asset revision identity")
  from tools.readalong.timeline_shards import load_timeline_payload
  timeline_path = safe_path(assets, manifest.get("timeline", "timeline.json"))
  timeline = load_timeline_payload(assets, manifest)
  sources = manifest.get("audioSources")
  if not isinstance(timeline, list) or not timeline or not all(isinstance(s, dict) for s in timeline):
    raise ValueError("Timeline must be a non-empty list of segment objects")
  if not isinstance(sources, list) or not sources or not all(isinstance(s, dict) for s in sources):
    raise ValueError("audioSources must be a non-empty object list")
  report["quality_layers"]["schema"] = True

  def error(code, message):
    report["errors"].append({"code": code, "msg": message})

  if exemptions:
    error(ERROR_UNEXPLAINED_GAP, "Unbound exemptions are not approved evidence")
  hashes, durations, declared = {}, {}, set()
  from tools.readalong.source_evidence import SourceEvidence
  evidence = source_evidence or SourceEvidence(sha256, probe_audio_duration)
  paths = []
  for source in sources:
    try:
      paths.append(safe_path(book, source.get('id')))
    except ValueError:
      pass
  evidence.prefetch(list(dict.fromkeys(paths)))
  for source in sources:
    sid = source.get("id")
    if not isinstance(sid, str) or not sid or sid in declared:
      raise ValueError("Audio source IDs must be unique non-empty relative paths")
    declared.add(sid)
    audio = safe_path(book, sid)
    if not audio.is_file():
      error(ERROR_TRACK_INVENTORY_MISMATCH, f"Missing physical audio: {sid}")
      durations[sid] = 0
      continue
    declared_hash = source.get("sha256")
    actual_hash = evidence.sha256(audio)
    hashes[sid] = actual_hash
    if not isinstance(declared_hash, str) or not re.fullmatch("[0-9a-f]{64}", declared_hash) or declared_hash != actual_hash:
      error(ERROR_AUDIO_SHA256_MISMATCH, f"Missing/invalid/mismatched audio hash: {sid}")
    physical = evidence.duration(audio)
    durations[sid] = physical
    if not math.isfinite(physical) or physical <= 0:
      error(ERROR_TRACK_INVENTORY_MISMATCH, f"Audio duration probe failed: {sid}")
    duration = source.get("duration")
    if duration is None and physical > 0:
      # Legacy manifest without explicit duration field, default to verified physical probe
      duration = physical
    if (not isinstance(duration, (int, float)) or isinstance(duration, bool)
        or not math.isfinite(duration) or duration <= 0):
      error(ERROR_AUDIO_DURATION_MISMATCH, f"Invalid declared duration: {sid}")
    elif physical > 0 and abs(duration - physical) > .1:
      error(ERROR_AUDIO_DURATION_MISMATCH, f"Duration differs from physical audio: {sid}")
  disk = {p.relative_to(book).as_posix() for p in book.rglob("*")
          if p.is_file() and p.suffix.lower() in AUDIO_SUFFIXES
          and not any(part.startswith(".") or part in {"readalong", "work", "text"}
                      for part in p.relative_to(book).parts)}
  if disk != declared:
    error(ERROR_TRACK_INVENTORY_MISMATCH, f"Physical inventory mismatch: {sorted(disk ^ declared)}")
  report["quality_layers"]["inventory"] = not report["errors"]
  docs, groups, identities = {}, {sid: [] for sid in declared}, set()
  document_paths = {}
  for i, segment in enumerate(timeline):
    sid = segment.get("audioSourceId")
    if sid not in groups:
      error(ERROR_TRACK_INVENTORY_MISMATCH, f"Segment {i}: unknown audio source")
      continue
    if not valid_interval(segment):
      error(ERROR_TIMESTAMP_INVALID, f"Segment {i}: invalid finite interval")
      continue
    start, end = segment["start"], segment["end"]
    if durations[sid] <= 0 or end > durations[sid] + .001:
      error(ERROR_TIMESTAMP_INVALID, f"Segment {i}: exceeds physical audio duration")
    if groups[sid] and start < groups[sid][-1]["end"]:
      error(ERROR_TIMESTAMP_OVERLAP, f"Segment {i}: overlap or time reversal")
    groups[sid].append(segment)
    key = occurrence_key(segment)
    if key in identities:
      error(ERROR_SCHEMA_INVALID, f"Segment {i}: duplicate occurrence identity")
    identities.add(key)
    name, frag = segment.get("document"), segment.get("fragment")
    if not isinstance(frag, str) or not frag.strip():
      error(ERROR_DOM_REFERENCE_BROKEN, f"Segment {i}: missing fragment")
      continue
    try:
      # Resolve each valid document once per audit; still check its existence
      # for every segment. Practical audits bind the complete candidate hash.
      if isinstance(name, str) and name in document_paths:
        document = document_paths[name]
      else:
        document = safe_path(assets, name)
        document_paths[name] = document
    except ValueError:
      error(ERROR_SECURITY_VIOLATION, f"Segment {i}: unsafe document path")
      continue
    if not document.is_file():
      error(ERROR_DOM_REFERENCE_BROKEN, f"Segment {i}: document missing")
      continue
    if name not in docs:
      parser = DOMFragmentExtractor()
      parser.feed(document.read_text(encoding="utf-8", errors="strict"))
      parser.close()
      docs[name] = parser
      if parser.duplicate_ids:
        error(ERROR_DUPLICATE_DOM_ID, f"Duplicate DOM IDs: {name}: {parser.duplicate_ids}")
    text = docs[name].id_to_text.get(frag)
    if text is None or not text or not isinstance(segment.get("text"), str) or canonical_text(segment["text"]) != canonical_text(text):
      error(ERROR_DOM_REFERENCE_BROKEN, f"Segment {i}: missing/empty/mismatched DOM text")
  report["quality_layers"]["monotonicity"] = not any(e["code"] in
    {ERROR_TIMESTAMP_INVALID, ERROR_TIMESTAMP_OVERLAP, ERROR_SCHEMA_INVALID, ERROR_TRACK_INVENTORY_MISMATCH}
    for e in report["errors"])
  report["quality_layers"]["dom_integrity"] = not any(e["code"] in
    {ERROR_DOM_REFERENCE_BROKEN, ERROR_DUPLICATE_DOM_ID, ERROR_SECURITY_VIOLATION}
    for e in report["errors"])

  for sid, segments in groups.items():
    dur = durations[sid]
    report["track_stats"][sid] = {"duration": dur, "segment_count": len(segments)}
    if not segments:
      error(ERROR_TRACK_INVENTORY_MISMATCH, f"No mapped narration or approved scope for {sid}")
      continue
    ordered = sorted(segments, key=lambda s: s["start"])
    gaps = [(0, ordered[0]["start"], "HEAD_DELAY")]
    covered_end = ordered[0]["end"]
    for seg in ordered[1:]:
      gaps.append((covered_end, seg["start"], "INTERNAL_VOID"))
      covered_end = max(covered_end, seg["end"])
    gaps.append((covered_end, dur, "TAIL_GAP"))
    stats = report["track_stats"][sid]
    stats.update(head_delay=ordered[0]["start"], tail_gap=max(0, dur-covered_end), internal_gaps=[])
    for a, b, kind in gaps:
      if b > a:
        gap = {"track": sid, "start": a, "end": b, "gap": b-a, "type": kind}
        report["uncovered_intervals"].append(gap)
        if kind == "INTERNAL_VOID":
          stats["internal_gaps"].append(gap)
        if b-a > (25 if kind == "HEAD_DELAY" else 20):
          error(ERROR_UNEXPLAINED_GAP, f"Unexplained {kind} in {sid}: {a:.3f}..{b:.3f}")
  report["quality_layers"]["coverage_and_gaps"] = not any(
    e["code"] in {ERROR_UNEXPLAINED_GAP, ERROR_TRACK_INVENTORY_MISMATCH} for e in report["errors"])
  # Density is diagnostic only: adding segments must never create proof.
  report["quality_layers"]["density"] = True
  report["summary"] = {"total_segments": len(timeline), "total_audio_mins": sum(durations.values())/60}

  try:
    acoustic = verify_reference(reference_path, assets, book, timeline_path, timeline, hashes)
  except (OSError, ValueError, TypeError, KeyError) as exc:
    acoustic = {"status": "TIMING_UNVERIFIED", "passed": False, "reason": str(exc)}
  report["acoustic"] = acoustic
  report["scope"] = "complete-timeline"
  report["quality_layers"]["timing_verified"] = acoustic.get("passed") is True
  if not acoustic.get("passed"):
    error(ERROR_TIMING_UNVERIFIED, acoustic.get("reason", acoustic["status"]))
  other_errors = [e for e in report["errors"] if e["code"] != ERROR_TIMING_UNVERIFIED]
  report["status"] = "FAILED" if other_errors else ("PASS" if acoustic.get("passed") else "NEEDS_REVIEW")
  report["certificationStatus"] = report["status"]
  projection_file = assets / "projection.json"
  if projection_file.is_file():
    try:
      projection = json.loads(projection_file.read_text())
      report["asrTokenEvidence"] = {k: projection[k] for k in ("audioTokens", "matchedTokens")}
      report["asrTokenEvidence"]["scope"] = "generator-lexical-estimate-not-independent-reference"
      if "tokenIntervals" in projection:
        report["asrTokenEvidence"]["tokenIntervals"] = projection["tokenIntervals"]
    except (ValueError, KeyError, TypeError):
      report["asrTokenEvidence"] = {"invalid": True}
  try:
    from tools.readalong.usability_evaluator import evaluate_readalong_usability
    usability_res = evaluate_readalong_usability(report)
    report["readalongUsability"] = usability_res["readalongUsability"]
    report["usabilityEvaluation"] = usability_res
  except Exception as exc:
    report["readalongUsability"] = "SCRIPT_ERROR"
    report["usabilityEvaluation"] = {"error": str(exc)}
  return report


def main():
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("book")
  parser.add_argument("--reference", help="Operator-approved external reference JSON")
  parser.add_argument("--json", action="store_true")
  args = parser.parse_args()
  report = audit_book_authoritative(Path(args.book), reference_path=args.reference)
  print(json.dumps(report, ensure_ascii=False, indent=2))
  raise SystemExit(0 if report["status"] == "PASS" else 2)


if __name__ == "__main__":
  main()
