"""Exercise real generation entrypoints with only ASR and sentence marking stubbed."""
import json
import tempfile
import unittest
import wave
import zipfile
from pathlib import Path
from unittest.mock import patch

from tools.readalong.candidate_safety import plan_audio_blocks


class ChunkPlanTests(unittest.TestCase):
  def test_every_tail_duration_is_accounted_for(self):
    for tail in (0, 1, 9, 10, 29, 30, 31):
      total = 3600 + tail
      blocks = list(plan_audio_blocks(total, 1800))
      self.assertEqual(sum(length for _, length in blocks), total)
      self.assertEqual(blocks[-1][0] + blocks[-1][1], total)
      for (a, b), (c, _) in zip(blocks, blocks[1:]):
        self.assertEqual(a + b, c)

  def test_invalid_sizes_cannot_spin(self):
    for size in (0, -1, float("nan"), float("inf"), 1e-10):
      with self.assertRaises(ValueError):
        list(plan_audio_blocks(100, size))


class GenerationTests(unittest.TestCase):
  def setUp(self):
    try:
      from tools.readalong import universal_aligner, universal_stream_aligner
    except ImportError as exc:
      self.skipTest(f"Run this integration suite with tools/readalong/.venv/bin/python: {exc}")
    self.normal = universal_aligner
    self.stream = universal_stream_aligner
    self.temp = tempfile.TemporaryDirectory(prefix="readalong-generation-")
    self.addCleanup(self.temp.cleanup)
    self.root = Path(self.temp.name)
    cache = patch("tools.readalong.config.resolve_transcripts_cache_dir", return_value=self.root / "cache")
    cache.start()
    self.addCleanup(cache.stop)
    (self.root / "cache").mkdir()
    self.book = self.root / "book"
    self.book.mkdir()
    self.words = [f"word{i}" for i in range(40)]
    self.transcript = [{"word": w, "norm": w, "start": i, "end": i+1}
                       for i, w in enumerate(self.words)]
    html = '<html><head></head><body><p><span id="c0-segment1">' + ' '.join(self.words) + '</span></p></body></html>'
    with zipfile.ZipFile(self.book / "book.epub", "w") as z:
      z.writestr("META-INF/container.xml", '<container><rootfiles><rootfile full-path="content.opf"/></rootfiles></container>')
      z.writestr("content.opf", '<package><manifest><item id="c" href="chapter.xhtml"/></manifest><spine><itemref idref="c"/></spine></package>')
      z.writestr("chapter.xhtml", html)
    with wave.open(str(self.book / "01.mp3"), "wb") as audio:
      audio.setnchannels(1)
      audio.setsampwidth(2)
      audio.setframerate(8000)
      audio.writeframes(b"\0\0" * (40*8000))
    active = self.book / "readalong"
    active.mkdir()
    (active / "sentinel").write_text("unchanged")

  def test_normal_engine_only_generates_unverified_candidate(self):
    output = self.root / "normal"
    with patch.object(self.normal, "transcribe_words", return_value=self.transcript):
      result = self.normal.align_single_book_universal(self.book, output)
    self.assertEqual(result["status"], "NEEDS_REVIEW", result)
    self.assertTrue((output / "timeline.json").is_file())
    self.assertEqual((self.book / "readalong/sentinel").read_text(), "unchanged")
    self.assertFalse((self.book / "readalong/timeline.json").exists())

  def test_stream_engine_only_generates_unverified_candidate(self):
    output = self.root / "stream"
    with patch.object(self.stream, "transcribe_words_cached", return_value=self.transcript), \
         patch.object(self.stream, "extract_audio_chunk"), \
         patch.object(self.stream, "mark_sentences", side_effect=lambda html, **kwargs: html):
      result = self.stream.align_volume_full_stream(self.book, output)
    self.assertEqual(result["status"], "NEEDS_REVIEW", result)
    self.assertEqual((self.book / "readalong/sentinel").read_text(), "unchanged")
    self.assertFalse((self.book / "readalong/timeline.json").exists())

  def test_real_marking_and_two_tracks_split_one_sentence_without_duplicate_ids(self):
    import shutil
    shutil.copyfile(self.book / "01.mp3", self.book / "02.mp3")
    with zipfile.ZipFile(self.book / "book.epub", "w") as z:
      z.writestr("META-INF/container.xml", '<container><rootfiles><rootfile full-path="content.opf"/></rootfiles></container>')
      z.writestr("content.opf", '<package><manifest><item id="c" href="chapter.xhtml"/></manifest><spine><itemref idref="c"/></spine></package>')
      z.writestr("chapter.xhtml", '<html><head></head><body><p>' + ' '.join(self.words) + '.</p></body></html>')
    tracks = [[{"word": w, "start": i*2, "end": i*2+2}
               for i, w in enumerate(self.words[start:start+20])] for start in (0, 20)]
    output = self.root / "two-tracks"
    with patch.object(self.stream, "transcribe_words_cached", side_effect=tracks), \
         patch.object(self.stream, "extract_audio_chunk"):
      result = self.stream.align_volume_full_stream(self.book, output)
    self.assertEqual(result["status"], "NEEDS_REVIEW", result)
    timeline = json.loads((output / "timeline.json").read_text())
    self.assertEqual([s["audioSourceId"] for s in timeline], ["01.mp3", "02.mp3"])
    self.assertNotEqual(timeline[0]["fragment"], timeline[1]["fragment"])
    self.assertEqual(timeline[1]["start"], 0)
    self.assertEqual(timeline[1]["end"], 40)

  def test_both_real_generators_cover_mixed_list_direct_text_and_paragraph(self):
    with zipfile.ZipFile(self.book / "book.epub", "w") as z:
      z.writestr("META-INF/container.xml", '<container><rootfiles><rootfile full-path="content.opf"/></rootfiles></container>')
      z.writestr("content.opf", '<package><manifest><item id="c" href="chapter.xhtml"/></manifest><spine><itemref idref="c"/></spine></package>')
      z.writestr("chapter.xhtml", '<html><body><ol><li value="1">'
                 + ' '.join(self.words[:10]) + ' <p>' + ' '.join(self.words[10:30])
                 + '</p> ' + ' '.join(self.words[30:]) + '</li></ol></body></html>')
    with patch.object(self.normal, "transcribe_words", return_value=self.transcript):
      normal = self.normal.align_single_book_universal(self.book, self.root / "normal-mixed")
    with patch.object(self.stream, "transcribe_words_cached", return_value=self.transcript), \
         patch.object(self.stream, "extract_audio_chunk"):
      stream = self.stream.align_volume_full_stream(self.book, self.root / "stream-mixed")
    for result, path in ((normal, self.root / "normal-mixed"), (stream, self.root / "stream-mixed")):
      self.assertEqual(result["status"], "NEEDS_REVIEW", result)
      rows = json.loads((path / "timeline.json").read_text())
      self.assertGreaterEqual(len(rows), 3)
      self.assertEqual(rows[0]["start"], 0)
      self.assertEqual(rows[-1]["end"], 40)
      self.assertEqual(' '.join(r["text"] for r in rows).split(), self.words)

  def test_generation_engines_default_do_not_confirm_reorders(self):
    """Universal and stream generators must default confirmed_reorders=None and never bypass disambiguation."""
    import inspect
    sig_normal = inspect.signature(self.normal.align_single_book_universal)
    sig_stream = inspect.signature(self.stream.align_volume_full_stream)
    self.assertIn("confirmed_reorders", sig_normal.parameters)
    self.assertIsNone(sig_normal.parameters["confirmed_reorders"].default)
    self.assertIn("confirmed_reorders", sig_stream.parameters)
    self.assertIsNone(sig_stream.parameters["confirmed_reorders"].default)

  def test_both_real_generators_reject_swallowed_segment_instead_of_adding_duration(self):
    rows = [{"audioSourceId": "01.mp3", "document": "text/chapter.xhtml", "fragment": "c0-segment1",
             "text": "word0", "start": a, "end": b} for a, b in ((0, 10), (5, 6))]
    for mode in ("normal", "stream"):
      output = self.root / ("conflict-"+mode)
      with patch("tools.readalong.stream_projection.project_stream", return_value=(rows, {})), \
           patch.object(self.normal, "transcribe_words", return_value=self.transcript), \
           patch.object(self.stream, "transcribe_words_cached", return_value=self.transcript), \
           patch.object(self.stream, "extract_audio_chunk"):
        with self.assertRaisesRegex(ValueError, "Unresolved timing conflict"):
          if mode == "normal":
            self.normal.align_single_book_universal(self.book, output)
          else:
            self.stream.align_volume_full_stream(self.book, output)
      self.assertFalse((output / "timeline.json").exists())

