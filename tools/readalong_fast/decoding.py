"""Decode bounded PCM without treating book-local faults as system failures."""
import errno
import hashlib
import math
from pathlib import Path
import re
import subprocess

from tools.readalong.batch_candidate_remapper import atomic_json


class AudioDecodeIssue(RuntimeError):
  """A suspect book interval must not reach ASR or a publishable timeline."""
  def __init__(self, evidence_path, report):
    self.evidence_path = str(evidence_path)
    self.report = report
    super().__init__(f"AUDIO_DECODE_ISSUE: {report['reason']}; requested={report['requestedSeconds']} "
      f"decoded={report['decodedSeconds']}; evidence={evidence_path}")


class DecodeEnvironmentError(RuntimeError):
  """Missing decoder/filter or an invalid command is a batch-wide problem."""


def pcm_timeline(pcm, stderr, start, duration):
  """Bind compact PCM to observed frame PTS; never infer holes from total length."""
  frames, suspect, used, pending_error = [], [], 0, False
  count = len(pcm)//4
  ordinal = 0
  filter_instance = None
  for line in stderr.splitlines():
    if not re.search(r'\[Parsed_ashowinfo_\d+ @ ', line) or not re.search(r'\bn:\d+', line):
      if re.search(r'error|invalid|header missing|corrupt|conceal|failed', line, re.I) and (' @ ' in line or line.startswith('Error')):
        pending_error = True
      continue
    match = re.search(r'n:(\d+)\s+pts:(-?\d+)\s+pts_time:\S+.*?channels:(\d+).*?rate:(\d+)\s+nb_samples:(\d+)', line)
    if not match:
      raise ValueError('Unparseable audio-frame timing: '+line[:220])
    n, pts, channels, rate, samples = map(int, match.groups())
    instance = re.search(r'\[Parsed_ashowinfo_\d+ @ ([^\]]+)\]', line).group(1)
    if filter_instance is not None and instance != filter_instance and n == 0:
      # Some MP3s change stream parameters mid-file. FFmpeg rebuilds filters;
      # a new counter is legitimate only if PTS still preserves physical time.
      ordinal = 0
    filter_instance = instance
    if n != ordinal or channels != 1 or rate != 16000 or samples <= 0 or 'fmt:flt ' not in line:
      raise ValueError('Unexpected frame sequence or PCM geometry')
    ordinal += 1
    take = min(samples, count-used)
    if take <= 0:
      continue
    a, b = pts/16000, (pts+take)/16000
    if a < -.0001 or b > duration+.1:
      raise ValueError('Audio frame PTS is outside the requested window')
    if frames:
      prior = frames[-1]
      if a < prior['audioStart']-.0001:
        raise ValueError('Audio frame PTS moves backward')
      overlap = prior['audioEnd']-a
      if overlap > .25:
        raise ValueError('Audio frame PTS overlap exceeds the bounded repair window')
      if overlap > .005:
        # Preserve the real frame PTS and PCM ordering, but quarantine speech
        # near this small timestamp collision. Merging never fabricates time.
        suspect.append({'start': start+max(0.0, min(prior['audioStart'], a)-.05),
          'end': start+min(duration, max(prior['audioEnd'], b)+.05)})
    if pending_error:
      suspect.append({'start': start+(frames[-1]['audioStart'] if frames else 0), 'end': start+b})
      pending_error = False
    frames.append({'pcmStart': used/16000, 'pcmEnd': (used+take)/16000,
      'audioStart': a, 'audioEnd': b})
    used += take
  if not frames or used != count:
    raise ValueError('Frame timing does not account for every decoded PCM sample')
  if pending_error:
    suspect.append({'start': start+frames[-1]['audioStart'], 'end': start+duration})
  windows, gaps, edge = [], [], 0.0
  for frame in frames:
    if frame['audioStart'] > edge+.0001:
      gaps.append({'start': start+edge, 'end': start+frame['audioStart']})
    if (windows and abs(windows[-1]['pcmEnd']-frame['pcmStart']) <= 1/16000
        and abs((windows[-1]['audioStart']-windows[-1]['pcmStart'])-
                (frame['audioStart']-frame['pcmStart'])) <= .005):
      windows[-1].update(pcmEnd=frame['pcmEnd'], audioEnd=frame['audioEnd'])
    else:
      windows.append(dict(frame))
    edge = max(edge, frame['audioEnd'])
  if edge < duration-.0001:
    gaps.append({'start': start+edge, 'end': start+duration})
  return {'method': 'observed-frame-pts-v1', 'chunkStart': start, 'frameCount': len(frames),
    'windows': windows, 'missingIntervals': gaps, 'suspectIntervals': suspect,
    'timelineEnd': min(start+duration, start+edge)}


def remap_segments(rows, timing):
  """Map real ASR segment boundaries; reject segments spanning loss/concealment."""
  result = []
  for row in rows:
    a, b = row.get('start'), row.get('end')
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in (a, b)) or b <= a:
      result.append(dict(row))
      continue
    left, right = a-timing['chunkStart'], b-timing['chunkStart']
    containing = [w for w in timing['windows'] if w['pcmStart']-.0001 <= left and right <= w['pcmEnd']+.0001]
    if len(containing) == 1:
      w = containing[0]
      mapped = {**row, 'start': timing['chunkStart']+w['audioStart']+left-w['pcmStart'],
        'end': timing['chunkStart']+w['audioStart']+right-w['pcmStart']}
      if any(mapped['start'] < gap['end'] and mapped['end'] > gap['start'] for gap in timing['suspectIntervals']):
        mapped.update(decodeTimingRejected=True)
    else:
      # No invented word split across a packet-loss boundary. Keep the actual
      # model interval as diagnostic only, never as trusted playback timing.
      mapped = {**row, 'decodeTimingRejected': True}
    mapped['pcmObservedInterval'] = {'start': a, 'end': b}
    result.append(mapped)
  return result


def decode_pcm(audio, start, duration, evidence_path, parameters, tolerant=False):
  """Preserve decoder diagnostics; never compact corrupt frames into ASR time."""
  proc = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", str(audio),
    "-t", str(duration), "-map", "0:a:0", "-vn", "-ac", "1", "-ar", "16000",
    "-f", "f32le", "pipe:1"], check=False, capture_output=True)
  stderr = getattr(proc, "stderr", b"").decode(errors="replace")
  code = getattr(proc, "returncode", 0)
  text = stderr.lower()
  for marker, number in (("no space left on device", errno.ENOSPC), ("permission denied", errno.EACCES),
      ("input/output error", errno.EIO), ("read-only file system", errno.EROFS),
      ("cannot allocate memory", errno.ENOMEM), ("out of memory", errno.ENOMEM)):
    if marker in text:
      raise OSError(number, stderr)
  if code < 0 or any(s in text for s in ("unknown decoder", "decoder not found", "no such filter",
      "unrecognized option", "unknown encoder", "error splitting the argument list")):
    raise DecodeEnvironmentError(f"FFMPEG_ENVIRONMENT: returncode={code}; {stderr}")
  if len(proc.stdout) % 4:
    raise DecodeEnvironmentError("FFMPEG_ENVIRONMENT: invalid float32 PCM byte count")
  pcm = proc.stdout[:round(duration*16000)*4]
  decoded = len(pcm)/4/16000
  reason = ("DECODER_REPORTED_ERRORS" if code or stderr.strip() else
    "EMPTY_OUTPUT" if not pcm else "PCM_SHORTFALL" if duration-decoded > .25 else None)
  report = {"schemaVersion": 1, "parameters": parameters, "sourcePath": str(Path(audio).resolve()),
    "requestedStart": start, "requestedEnd": start+duration, "requestedSeconds": duration,
    "decodedSeconds": decoded, "returnedPcmSeconds": len(proc.stdout)/4/16000,
    "shortfallSeconds": max(0, duration-decoded), "ffmpegReturnCode": code, "stderr": stderr,
    "pcmSha256": hashlib.sha256(pcm).hexdigest(), "status": "QUARANTINE" if reason else "DECODED",
    "reason": reason, "missingIntervalLocationKnown": False,
    "note": "A shortfall does not prove a missing tail; no silence insertion or timestamp repair was performed"}
  atomic_json(evidence_path, report)
  if reason:
    if tolerant and pcm:
      # Retry decoding once with measured frame PTS, never with guessed silence
      # insertion, timestamp stretching, or a change to the user's source file.
      probe = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-v', 'info', '-filter_threads', '1', '-threads', '1', '-ss', str(start),
        '-i', str(audio), '-t', str(duration), '-map', '0:a:0', '-vn', '-ac', '1', '-ar', '16000',
        '-af', 'aresample=16000,aformat=sample_fmts=flt:channel_layouts=mono,asettb=1/16000,ashowinfo', '-f', 'f32le', 'pipe:1'],
        check=False, capture_output=True)
      probe_text = getattr(probe, 'stderr', b'').decode(errors='replace')
      # Preserve system faults even if they happen only on the diagnostic pass.
      for marker, number in (('no space left on device', errno.ENOSPC), ('permission denied', errno.EACCES),
          ('input/output error', errno.EIO), ('out of memory', errno.ENOMEM), ('cannot allocate memory', errno.ENOMEM)):
        if marker in probe_text.lower():
          raise OSError(number, probe_text)
      if getattr(probe, 'returncode', 0) < 0 or any(s in probe_text.lower() for s in ('no such filter', 'unrecognized option', 'unknown decoder')):
        raise DecodeEnvironmentError('Timestamp probe is unavailable or terminated')
      try:
        if len(probe.stdout) % 4:
          raise ValueError('Incomplete float32 sample in timestamp probe')
        timing = pcm_timeline(probe.stdout, probe_text, start, duration)
      except ValueError as exc:
        report['recoveryRejected'] = str(exc)
        atomic_json(evidence_path, report)
      else:
        report.update(status='RECOVERED_WITH_TIMELINE_MAP', timingMap=timing,
          timelineEnd=timing['timelineEnd'], missingIntervalLocationKnown=True,
          decodedSeconds=len(probe.stdout)/4/16000, pcmSha256=hashlib.sha256(probe.stdout).hexdigest(),
          timestampProbeLogSha256=hashlib.sha256(probe_text.encode()).hexdigest(),
          note='Frame PTS preserves original time; suspect/loss-crossing ASR segments remain untrusted; no source repair performed')
        atomic_json(evidence_path, report)
        return probe.stdout, report
    raise AudioDecodeIssue(evidence_path, report)
  return pcm, report
