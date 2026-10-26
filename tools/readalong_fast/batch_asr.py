"""Batched segment ASR over deterministic non-overlapping silence windows.

Timestamps returned by transcribe_chunks_batched are window-relative. Overlapping
windows produced impossible global times (coverage 1946s on an 1800s block, 72
segments rejected by normalize_native). Non-overlapping windows whose cuts sit at
local RMS minima fix that: coverage stays inside the block and rejected segments
drop to a couple of seconds.

Batch composition changes the numerical result, so batch size and the window cut
list are part of the cache identity. Windows never overlap, and a window's end is
clamped to the real decoded PCM length rather than to a padded model interval.
"""
import hashlib

import numpy as np

ENGINE = "mlx-batch-silence-v1"
WINDOW_TARGET_SECONDS = 28.0
WINDOW_SEARCH_SECONDS = 6.0
CUT_HOP_SECONDS = 0.05
MIN_TRAILING_SECONDS = 30.0
BATCH_SIZE = 16
SAMPLE_RATE = 16000

CUT_PARAMS = {"engine": ENGINE, "targetSeconds": WINDOW_TARGET_SECONDS,
  "searchSeconds": WINDOW_SEARCH_SECONDS, "hopSeconds": CUT_HOP_SECONDS,
  "minTrailingSeconds": MIN_TRAILING_SECONDS, "sampleRate": SAMPLE_RATE}


def silence_cuts(pcm, target=WINDOW_TARGET_SECONDS, search=WINDOW_SEARCH_SECONDS,
                 hop=CUT_HOP_SECONDS, min_trailing=MIN_TRAILING_SECONDS):
  """Deterministic window boundaries covering the whole block.

  Each cut lands on the 50ms frame of lowest RMS within the search span, so it
  falls in silence rather than mid-word. Returns absolute sample offsets."""
  width = int(hop*SAMPLE_RATE)
  cuts, pos = [0], 0
  while len(pcm)-pos > min_trailing*SAMPLE_RATE:
    lo = pos+int((target-search)*SAMPLE_RATE)
    hi = pos+int(target*SAMPLE_RATE)
    if hi > len(pcm):
      break
    span = pcm[lo:hi][:(hi-lo)//width*width]
    if not len(span):
      break
    frames = span.reshape(-1, width)
    pos = lo+int(np.argmin((frames**2).mean(1)))*width+width//2
    cuts.append(pos)
  return cuts


def window_bounds(cuts, total_samples):
  return list(zip(cuts, cuts[1:]+[total_samples]))


def cuts_sha(cuts):
  return hashlib.sha256(",".join(str(c) for c in cuts).encode()).hexdigest()


def batch_params(sha, model_sha, start, duration):
  """Cache identity. Window geometry is bound through the cut list digest so a
  change in cut placement or batch size can never reuse another path's rows."""
  return {"sourceSha256": sha, "modelSha256": model_sha, "start": start,
    "duration": duration, "language": "en", "word_timestamps": False,
    "sampleRate": SAMPLE_RATE, "engine": ENGINE, "batchSize": BATCH_SIZE,
    **CUT_PARAMS}


def rebuild_global_rows(outputs, bounds, start, block_end, timestamp_begin, eot, decode):
  """Window-relative timestamp tokens to block-global segment rows.

  A closing timestamp past the window's real PCM length is a prediction into the
  model's padding, not observed audio: the end is clamped to the window end and
  the row is flagged. Text without a closing timestamp is kept as untrusted and
  excluded from highlighting. Both are intersections with observed audio, never
  interpolation."""
  rows, past_end = [], 0
  for out, (a, b) in zip(outputs, bounds):
    offset, window_len = a/SAMPLE_RATE, (b-a)/SAMPLE_RATE
    window_end = start+offset+window_len
    text, seg_start = [], None
    for token in out.get("tokens", []):
      if token >= timestamp_begin:
        ts = offset+(token-timestamp_begin)*0.02
        if seg_start is None or not text:
          seg_start = ts
        else:
          rows.append({"start": start+seg_start, "end": start+ts, "text": decode(text),
            "_windowEnd": window_end})
          text, seg_start = [], ts
      elif token < eot:
        text.append(token)
    if text:
      rows.append({"start": start+(seg_start or 0), "end": window_end, "text": decode(text),
        "_windowEnd": window_end, "timingRejected": True})
  rebuilt = []
  for row in rows:
    window_end = row.pop("_windowEnd")
    if row["end"] > window_end+1e-6:
      past_end += 1
      row["timestampPastWindowEnd"] = True
      row["end"] = window_end
    # A prediction that starts past the window's real audio has no observed
    # speech behind it at all: clamping only the end would leave start > end and
    # break the per-track ordering guarantee.
    if row["start"] >= window_end-1e-6:
      row["start"] = window_end
      row["timingRejected"] = True
    rebuilt.append(row)
  return rebuilt, past_end
