"""V1 mechanism tests for the batched engine, its cache identity, and prefetch."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.readalong_fast.batch_asr import (BATCH_SIZE, ENGINE, batch_params, cuts_sha,
  rebuild_global_rows, silence_cuts, window_bounds)
from tools.readalong_fast.pipeline import SpeechCache


class Tokenizer:
  """Minimal stand-in for the Whisper tokenizer used by rebuild_global_rows."""
  timestamp_begin = 50364
  eot = 50257

  def __init__(self, vocab):
    self.vocab = vocab

  def decode(self, tokens):
    return "".join(self.vocab[t] for t in tokens)


class TimeReconstructionTests(unittest.TestCase):
  def test_window_relative_timestamps_become_block_global(self):
    # Two 10s windows; a segment spanning window-local 1.0..3.0 in each.
    bounds = [(0, 160000), (160000, 320000)]
    tok = Tokenizer({1: "hello ", 2: "world"})
    outputs = [{"tokens": [1, 2, Tokenizer.timestamp_begin+50, 1, Tokenizer.timestamp_begin+150]},
               {"tokens": [1, 2, Tokenizer.timestamp_begin+50, 1, Tokenizer.timestamp_begin+150]}]
    rows, past = rebuild_global_rows(outputs, bounds, 0.0, 20.0,
      tok.timestamp_begin, tok.eot, tok.decode)
    self.assertEqual(past, 0)
    self.assertAlmostEqual(rows[0]["start"], 1.0)
    self.assertAlmostEqual(rows[0]["end"], 3.0)
    # Second window starts at 10s, so its rows must be offset by 10s.
    self.assertAlmostEqual(rows[1]["start"], 11.0)
    self.assertAlmostEqual(rows[1]["end"], 13.0)

  def test_timestamp_past_window_end_is_clamped_and_flagged(self):
    bounds = [(0, 160000)]  # 10s window
    tok = Tokenizer({1: "tail"})
    # Closing timestamp at 20s sits inside model padding, not observed audio.
    outputs = [{"tokens": [1, Tokenizer.timestamp_begin+0, Tokenizer.timestamp_begin+1000]}]
    rows, past = rebuild_global_rows(outputs, bounds, 0.0, 10.0,
      tok.timestamp_begin, tok.eot, tok.decode)
    self.assertEqual(past, 1)
    self.assertTrue(rows[0]["timestampPastWindowEnd"])
    self.assertAlmostEqual(rows[0]["end"], 10.0)

  def test_text_without_closing_timestamp_is_untrusted(self):
    bounds = [(0, 160000)]
    tok = Tokenizer({1: "open"})
    outputs = [{"tokens": [1, Tokenizer.timestamp_begin+0, 1]}]
    rows, _ = rebuild_global_rows(outputs, bounds, 0.0, 10.0,
      tok.timestamp_begin, tok.eot, tok.decode)
    self.assertTrue(rows[0]["timingRejected"])

  def test_prediction_entirely_past_window_never_reverses(self):
    # A real book produced "Can I?" / "Okay." whose start and end both sat past
    # the window end; clamping only the end left start > end and broke the
    # per-track ordering guarantee.
    bounds = [(0, 160000)]  # 10s window
    tok = Tokenizer({1: "late"})
    outputs = [{"tokens": [1, Tokenizer.timestamp_begin+600, Tokenizer.timestamp_begin+700]}]
    rows, _ = rebuild_global_rows(outputs, bounds, 0.0, 10.0,
      tok.timestamp_begin, tok.eot, tok.decode)
    self.assertLessEqual(rows[0]["start"], rows[0]["end"])
    self.assertEqual(rows[0]["end"], 10.0)
    self.assertTrue(rows[0]["timingRejected"])

  def test_rows_never_reverse_within_a_block(self):
    pcm = np.random.RandomState(11).randn(16000*120).astype("<f4")
    cuts = silence_cuts(pcm)
    bounds = window_bounds(cuts, len(pcm))
    tok = Tokenizer({1: "w"})
    outputs = [{"tokens": [1, Tokenizer.timestamp_begin+40, Tokenizer.timestamp_begin+90,
                           1, Tokenizer.timestamp_begin+900, 1]}
               for _ in bounds]
    rows, _ = rebuild_global_rows(outputs, bounds, 0.0, 120.0,
      tok.timestamp_begin, tok.eot, tok.decode)
    for previous, current in zip(rows, rows[1:]):
      self.assertLessEqual(previous["end"], current["start"]+1e-6,
        f"{previous} overlaps or reverses {current}")

  def test_reconstructed_rows_never_overlap_and_stay_inside_block(self):
    pcm = np.random.RandomState(7).randn(16000*90).astype("<f4")
    cuts = silence_cuts(pcm)
    bounds = window_bounds(cuts, len(pcm))
    self.assertGreater(len(bounds), 2)
    self.assertTrue(all(b <= c for (_, b), (c, _) in zip(bounds, bounds[1:])),
                    "windows must not overlap")
    self.assertEqual(bounds[0][0], 0)
    self.assertEqual(bounds[-1][1], len(pcm))


class CutGeometryTests(unittest.TestCase):
  def test_cuts_are_deterministic_and_fall_in_silence(self):
    pcm = np.ones(16000*90, dtype="<f4")*0.5
    # Carve an unmistakable silence well inside the first search span.
    pcm[16000*25:16000*26] = 0.0
    cuts = silence_cuts(pcm)
    self.assertEqual(cuts, silence_cuts(pcm))
    self.assertLessEqual(abs(cuts[1]-16000*25), 16000)

  def test_cuts_sha_changes_with_geometry(self):
    self.assertNotEqual(cuts_sha([0, 100]), cuts_sha([0, 101]))
    self.assertEqual(cuts_sha([0, 100]), cuts_sha([0, 100]))

  def test_short_block_yields_single_window(self):
    self.assertEqual(silence_cuts(np.zeros(16000*10, dtype="<f4")), [0])


class CacheIdentityTests(unittest.TestCase):
  def test_engine_batch_size_and_cuts_are_in_identity(self):
    params = batch_params("a"*64, "b"*64, 0.0, 1800.0)
    self.assertEqual(params["engine"], ENGINE)
    self.assertEqual(params["batchSize"], BATCH_SIZE)
    for field in ("targetSeconds", "searchSeconds", "hopSeconds", "sampleRate"):
      self.assertIn(field, params)

  def test_serial_and_batch_identities_differ(self):
    with tempfile.TemporaryDirectory() as tmp:
      cache = SpeechCache(Path(tmp)/"cache", [], "b"*64, asr_engine="batch")
      serial = cache.chunk_params("a"*64, 0.0, 1800.0)
      batched = batch_params("a"*64, "b"*64, 0.0, 1800.0)
      self.assertNotEqual(serial["engine"], batched["engine"])
      key = hashlib.sha256(json.dumps(batched, sort_keys=True).encode()).hexdigest()
      other = dict(batched, batchSize=8)
      self.assertNotEqual(key, hashlib.sha256(json.dumps(other, sort_keys=True).encode()).hexdigest())

  def test_invalid_engine_is_rejected(self):
    with tempfile.TemporaryDirectory() as tmp:
      with self.assertRaises(ValueError):
        SpeechCache(Path(tmp)/"cache", [], "b"*64, asr_engine="parallel")

  def test_batch_is_the_default_engine(self):
    """The 2.57x speedup only reaches production if the default is batch.

    `benchmark.py` was the only caller passing the flag, so every production
    entry point silently kept running the serial engine."""
    with tempfile.TemporaryDirectory() as tmp:
      self.assertEqual(SpeechCache(Path(tmp)/"cache", [], "b"*64).asr_engine, "batch")

  def test_serial_remains_selectable(self):
    with tempfile.TemporaryDirectory() as tmp:
      cache = SpeechCache(Path(tmp)/"cache", [], "b"*64, asr_engine="serial")
      self.assertEqual(cache.asr_engine, "serial")
      self.assertEqual(cache.chunk_params("a"*64, 0.0, 1800.0)["engine"], "mlx-segment-v1")


class EntryPointEngineTests(unittest.TestCase):
  """Every production entry point must be able to select the engine.

  A default that no caller can override is not a default, it is a hardcode, and
  an entry point that forgets to pass the flag silently pins the serial engine."""
  def help_text(self, module, argv):
    import contextlib, io
    from unittest.mock import patch
    with contextlib.redirect_stdout(io.StringIO()) as out, \
         contextlib.redirect_stderr(io.StringIO()), patch.object(sys, "argv", argv):
      with self.assertRaises(SystemExit):
        module.main()
    return out.getvalue()

  def test_benchmark_offers_the_engine_flag_with_batch_default(self):
    from tools.readalong_fast import benchmark
    text = self.help_text(benchmark, ["benchmark", "--help"])
    self.assertIn("--asr-engine", text)
    self.assertIn("--asr-engine {serial,batch,words}", text)

  def test_resume_offers_the_engine_flag_with_batch_default(self):
    from tools.readalong_fast import resume
    text = self.help_text(resume, ["resume", "--help"])
    self.assertIn("--asr-engine {serial,batch,words}", text)

  def test_resume_forwards_the_engine_to_the_cache(self):
    """A flag that is parsed but never forwarded leaves the serial engine live."""
    import inspect
    from tools.readalong_fast import resume
    self.assertIn("asr_engine=asr_engine", inspect.getsource(resume.run))
    self.assertEqual(inspect.signature(resume.run).parameters["asr_engine"].default, "batch")

  def test_every_entry_point_defaults_the_flag_to_batch(self):
    """The parser default is the thing that decides which engine production runs."""
    import argparse
    from unittest.mock import patch
    from tools.readalong_fast import benchmark, resume
    for module in (benchmark, resume):
      captured = {}
      original = argparse.ArgumentParser.parse_args
      def grab(self, *a, **k):
        captured["parser"] = self
        raise SystemExit(0)
      with patch.object(argparse.ArgumentParser, "parse_args", grab):
        with self.assertRaises(SystemExit):
          module.main()
      action = next(a for a in captured["parser"]._actions if a.dest == "asr_engine")
      self.assertEqual(action.default, "batch", module.__name__)
      self.assertEqual(set(action.choices), {"serial", "batch", "words"}, module.__name__)


class EngineSelectionTests(unittest.TestCase):
  def test_existing_serial_cache_is_reused_without_new_asr(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      model = "c"*64
      params = {"sourceSha256": "a"*64, "modelSha256": model, "start": 0.0, "duration": 1800.0,
        "language": "en", "word_timestamps": False, "sampleRate": 16000, "engine": "mlx-segment-v1"}
      key = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
      (root/"cached").mkdir(parents=True)
      (root/"cached"/(key+".json")).write_text(json.dumps({"parameters": params,
        "segments": [{"start": 0.0, "end": 1.0, "text": "cached"}],
        "rawSegments": [{"start": 0.0, "end": 1.0, "text": "cached"}], "decodedEnd": 1800.0}))
      cache = SpeechCache(root/"new", [root/"cached"], model, asr_engine="batch")
      rows = cache.chunk(root/"missing.mp3", "a"*64, 0.0, 1800.0)
      self.assertEqual([r["text"] for r in rows], ["cached"])
      self.assertEqual(cache.stats["newAsrAudioSeconds"], 0)

  def test_needs_decode_is_false_for_cached_block(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      model = "c"*64
      params = {"sourceSha256": "a"*64, "modelSha256": model, "start": 0.0, "duration": 1800.0,
        "language": "en", "word_timestamps": False, "sampleRate": 16000, "engine": "mlx-segment-v1"}
      key = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
      (root/"cached").mkdir(parents=True)
      (root/"cached"/(key+".json")).write_text(json.dumps({"parameters": params, "segments": []}))
      cache = SpeechCache(root/"new", [root/"cached"], model, asr_engine="batch")
      self.assertFalse(cache.needs_decode(root/"x.mp3", "a"*64, 0.0, 1800.0))
      self.assertTrue(cache.needs_decode(root/"x.mp3", "d"*64, 0.0, 1800.0))


class PrefetchTests(unittest.TestCase):
  def test_prefetch_slot_is_consumed_once(self):
    with tempfile.TemporaryDirectory() as tmp:
      cache = SpeechCache(Path(tmp)/"cache", [], "e"*64)
      self.assertIsNone(cache.take_prefetched(Path("x.mp3"), 0.0, 1800.0, "k"))
      cache.start_prefetch([])
      cache.stop_prefetch()
      self.assertIsNone(cache.take_prefetched(Path("x.mp3"), 0.0, 1800.0, "k"))


if __name__ == "__main__":
  unittest.main()
