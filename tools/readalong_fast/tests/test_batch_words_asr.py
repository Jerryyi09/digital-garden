"""Unit and deterministic verification tests for mlx-batch-silence-words-v1."""
import hashlib
import json
import unittest
import numpy as np

from tools.readalong_fast.batch_asr import silence_cuts, window_bounds
from tools.readalong_fast.batch_words_asr import (
  WORDS_ENGINE, batch_words_params, rebuild_global_words_and_segments
)


class BatchWordsAsrTests(unittest.TestCase):
  def test_engine_identity(self):
    params = batch_words_params("testsha", "modelsha", 0.0, 1800.0)
    self.assertEqual(params["engine"], WORDS_ENGINE)
    self.assertTrue(params["word_timestamps"])
    self.assertEqual(params["batchSize"], 16)

  def test_rebuild_words_strictly_monotone_and_clamped(self):
    bounds = [(0, 16000 * 10), (16000 * 10, 16000 * 20)]
    # window 1: words from 1.0s to 9.5s, with an overflow word to 10.5s
    # window 2: words from 0.5s to 8.0s
    outputs = [
      {
        "words": [
          {"word": "Hello", "start": 1.0, "end": 2.0, "probability": 0.99},
          {"word": "world", "start": 2.1, "end": 3.0, "probability": 0.98},
          {"word": "overflow", "start": 9.0, "end": 10.5, "probability": 0.95},
        ],
        "tokens": []
      },
      {
        "words": [
          {"word": "Next", "start": 0.5, "end": 1.5, "probability": 0.99},
          {"word": "window", "start": 1.6, "end": 2.5, "probability": 0.98},
        ],
        "tokens": []
      }
    ]

    segs, words, past_end = rebuild_global_words_and_segments(
      outputs, bounds, start=100.0, block_end=120.0,
      timestamp_begin=50364, eot=50257, decode=lambda x: ""
    )

    self.assertEqual(len(words), 5)
    self.assertEqual(past_end, 1) # overflow word clamped

    # check monotonicity
    for i in range(len(words) - 1):
      w1, w2 = words[i], words[i+1]
      self.assertLessEqual(w1["start"], w1["end"])
      self.assertLessEqual(w1["end"], w2["start"])

    # first word in window 1: global start 100.0 + 1.0 = 101.0
    self.assertEqual(words[0]["word"], "Hello")
    self.assertEqual(words[0]["start"], 101.0)
    self.assertEqual(words[0]["end"], 102.0)

    # overflow word: window 1 ends at 100 + 10 = 110.0, so end clamped to 110.0
    self.assertEqual(words[2]["word"], "overflow")
    self.assertEqual(words[2]["end"], 110.0)

    # first word in window 2: window 2 starts at 110.0, offset 0.5 -> global 110.5
    self.assertEqual(words[3]["word"], "Next")
    self.assertEqual(words[3]["start"], 110.5)
    self.assertEqual(words[3]["end"], 111.5)


if __name__ == "__main__":
  unittest.main()
