"""Batched word-timestamp and segment ASR over deterministic non-overlapping silence windows.

Engine: mlx-batch-silence-words-v1.
Combines batch-16 silence-windowed decoding with word_timestamps=True.
Guarantees strictly monotone global timestamps clamped to observed audio frames.
"""
import hashlib
from typing import List, Tuple, Dict, Any
import numpy as np

from tools.readalong_fast.batch_asr import (
  WINDOW_TARGET_SECONDS, WINDOW_SEARCH_SECONDS, CUT_HOP_SECONDS,
  MIN_TRAILING_SECONDS, BATCH_SIZE, SAMPLE_RATE, CUT_PARAMS,
  silence_cuts, window_bounds, cuts_sha
)

WORDS_ENGINE = "mlx-batch-silence-words-v1"

WORDS_CUT_PARAMS = {
  **CUT_PARAMS,
  "engine": WORDS_ENGINE,
  "word_timestamps": True,
}


def batch_words_params(sha: str, model_sha: str, start: float, duration: float) -> Dict[str, Any]:
  """Cache identity for word-timestamp batched ASR."""
  return {
    "sourceSha256": sha,
    "modelSha256": model_sha,
    "start": start,
    "duration": duration,
    "language": "en",
    "word_timestamps": True,
    "sampleRate": SAMPLE_RATE,
    "engine": WORDS_ENGINE,
    "batchSize": BATCH_SIZE,
    **WORDS_CUT_PARAMS
  }


def rebuild_global_words_and_segments(
    outputs: List[Dict[str, Any]],
    bounds: List[Tuple[int, int]],
    start: float,
    block_end: float,
    timestamp_begin: int,
    eot: int,
    decode
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], int]:
  """Convert window-relative segments and words to global strictly-monotone timelines.

  Returns:
    (rebuilt_segments, rebuilt_words, past_end_count)
  """
  raw_segments = []
  raw_words = []
  past_end = 0

  for out, (a, b) in zip(outputs, bounds):
    offset = a / SAMPLE_RATE
    window_len = (b - a) / SAMPLE_RATE
    window_start = start + offset
    window_end = window_start + window_len

    # 1. 提取逐词时间戳
    win_words = out.get("words") or []
    for w in win_words:
      w_text = w.get("word") or ""
      if not w_text:
        continue
      w_s = float(w.get("start", 0.0))
      w_e = float(w.get("end", 0.0))

      # 转换到全局时间
      g_s = window_start + w_s
      g_e = window_start + w_e

      # 边界约束到实测音频长度
      if g_e > window_end + 1e-4:
        past_end += 1
        g_e = window_end
      if g_s >= window_end - 1e-4:
        g_s = window_end
      if g_e < g_s:
        g_e = g_s

      raw_words.append({
        "word": w_text,
        "start": round(g_s, 3),
        "end": round(g_e, 3),
        "probability": float(w.get("probability", 1.0))
      })

    # 2. 提取分段时间戳 (tokens 回退/重构)
    text, seg_start = [], None
    for token in out.get("tokens", []):
      if token >= timestamp_begin:
        ts = offset + (token - timestamp_begin) * 0.02
        if seg_start is None or not text:
          seg_start = ts
        else:
          raw_segments.append({
            "start": start + seg_start,
            "end": start + ts,
            "text": decode(text),
            "_windowEnd": window_end
          })
          text, seg_start = [], ts
      elif token < eot:
        text.append(token)
    if text:
      raw_segments.append({
        "start": start + (seg_start or 0),
        "end": window_end,
        "text": decode(text),
        "_windowEnd": window_end,
        "timingRejected": True
      })

  # 规范化分段
  rebuilt_segments = []
  for row in raw_segments:
    w_end = row.pop("_windowEnd")
    if row["end"] > w_end + 1e-6:
      row["timestampPastWindowEnd"] = True
      row["end"] = w_end
    if row["start"] >= w_end - 1e-6:
      row["start"] = w_end
      row["timingRejected"] = True
    row["start"] = round(row["start"], 3)
    row["end"] = round(row["end"], 3)
    rebuilt_segments.append(row)

  # 规范化逐词时间戳（严格全局单调递增，平滑重叠）
  rebuilt_words = []
  last_end = start
  for w in raw_words:
    cur_s = max(w["start"], last_end)
    cur_e = max(w["end"], cur_s)
    w["start"] = round(cur_s, 3)
    w["end"] = round(cur_e, 3)
    last_end = w["end"]
    rebuilt_words.append(w)

  return rebuilt_segments, rebuilt_words, past_end
