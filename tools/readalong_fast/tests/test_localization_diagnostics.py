"""Production-path anthology ordering and honest localization diagnostics."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from tools.readalong_fast.matcher import ParagraphIndex, tokens
from tools.readalong_fast.pipeline import InputCache, SpeechCache, file_hash, generate


A = "a copper bird carries a golden message across the quiet valley before sunrise"
B = "the wooden boat sails past a distant island under the bright stars of winter"
REPEAT = "this repeated introduction describes the author and offers a welcome to every reader"


class LocalizationDiagnosticTests(unittest.TestCase):
  def index(self, text):
    book = tokens(text)
    return ParagraphIndex(book, [{"offset": 0, "length": len(book), "document": "a", "fragment": "p"}])

  def test_no_anchor_does_not_claim_material_mismatch(self):
    result = self.index(A).locate_detailed(B)
    self.assertIsNone(result["match"])
    self.assertEqual(result["diagnostic"]["reason"], "NO_RELIABLE_ANCHOR")
    self.assertNotIn("materialMismatchConfirmed", result["diagnostic"])

  def test_short_initial_phrase_cannot_use_implicit_start_of_book_context(self):
    index = self.index("welcome to the book and its many chapters")
    self.assertEqual(index.locate_detailed("welcome to the")["diagnostic"]["reason"], "SHORT_QUERY_WITHOUT_CONTEXT")
    self.assertIsNotNone(index.locate_detailed("welcome to the", 0)["match"])

  def test_short_phrase_cannot_jump_into_an_unrelated_story(self):
    text = A+" "+" ".join(f"padding{i}" for i in range(300))+" I would like to see you again today"
    index = self.index(text)
    result = index.locate_detailed("I would like to see you", len(tokens(A)))
    self.assertIsNone(result["match"])
    self.assertIn("SHORT_GLOBAL_RELOCATION_UNSAFE", result["diagnostic"]["rejections"])

  def test_candidate_rejection_is_not_conflated_with_no_anchor(self):
    result = self.index(A).locate_detailed("a copper bird carries a unrelated token nonsense "*2)
    self.assertIsNone(result["match"])
    self.assertEqual(result["diagnostic"]["reason"], "CANDIDATE_REJECTED")
    self.assertIn("LOW_LEXICAL_MATCH", result["diagnostic"]["rejections"])

  def generate(self, chapters, tracks, screen=False, duration=None):
    temp = tempfile.TemporaryDirectory()
    self.addCleanup(temp.cleanup)
    root = Path(temp.name)
    book = root/"book"
    book.mkdir()
    with zipfile.ZipFile(book/"book.epub", "w") as archive:
      archive.writestr("META-INF/container.xml", '<container><rootfiles><rootfile full-path="content.opf"/></rootfiles></container>')
      manifest = ''.join(f'<item id="c{i}" href="c{i}.html"/>' for i in range(len(chapters)))
      spine = ''.join(f'<itemref idref="c{i}"/>' for i in range(len(chapters)))
      archive.writestr("content.opf", f'<package><manifest>{manifest}</manifest><spine>{spine}</spine></package>')
      for i, paragraphs in enumerate(chapters):
        archive.writestr(f"c{i}.html", '<html><body>'+''.join(f'<p>{p}</p>' for p in paragraphs)+'</body></html>')
    audio = []
    by_name = {}
    for i, rows in enumerate(tracks):
      name = f"{i}.mp3"
      (book/name).write_bytes(f"synthetic-{i}".encode())
      by_name[name] = rows
      audio.append({"rel_to_book": name, "sha256": file_hash(book/name), "measured_duration": duration or rows[-1]["end"]})
    unit = {"book_dir": str(book), "audio_tracks": audio,
      "epubs": [{"rel_to_book": "book.epub", "sha256": file_hash(book/"book.epub")}]}
    cache = SpeechCache(root/"cache", [], "a"*64, True)
    # A screen sample is a full grid block of real speech, not a 15s probe: the
    # estimator needs a few hundred tokens before it will commit to a verdict.
    # Rows are placed relative to the requested block, as a real chunk() would.
    def block_rows(path, sha, start, duration, *rest):
      return [{"start": start+i*15.0, "end": start+i*15.0+15, "text": B}
              for i in range(int(duration//15))]
    with patch.object(cache, "whole_legacy_track", side_effect=lambda path, *args: by_name[path.name]), \
         patch.object(cache, "chunk", side_effect=block_rows), \
         patch.object(InputCache, "duration", side_effect=lambda path, measured: measured):
      report = generate(unit, root/"candidate", cache, InputCache(root/"inputs.json"), screen=screen)
    timeline_path = root/"candidate/timeline.json"
    return report, json.loads(timeline_path.read_text()) if timeline_path.exists() else []

  def test_production_screen_reports_mismatch_without_certifying_the_book(self):
    report, timeline = self.generate([[A]], [[{"start": 0, "end": 10, "text": A}]], screen=True, duration=14400)
    self.assertEqual(report["stage"], "SCREEN_REVIEW")
    self.assertEqual(report["readalongUsability"], "REVIEW_MAPPING")
    # The sampled audio carries plenty of speech, none of it in this EPUB: the
    # editions really are incompatible, and the report says so without pretending
    # to have certified the full book.
    self.assertTrue(report["materialMismatchConfirmed"])
    self.assertEqual(report["materialAssessment"], "MISMATCH_CONFIRMED")
    self.assertEqual(report["recommendedAction"], "EXCLUDE_PRACTICAL_CANDIDATE")
    # One stratum per 1800s block on a 14400s track, each a full grid block.
    self.assertEqual(len(report["screenEvidence"]), 6)
    self.assertTrue(all(s["tokenCount"] >= 200 for s in report["screenEvidence"]))
    self.assertTrue(all(s["locatedRatio"] == 0 for s in report["screenEvidence"]))
    self.assertFalse(report["fullAudioProcessed"])
    self.assertFalse(timeline)

  def test_reversed_anthology_tracks_map_to_correct_documents_without_time_reordering(self):
    filler = " ".join(f"filler{i}" for i in range(90))
    report, timeline = self.generate([[A, filler], [B]], [
      [{"start": 0, "end": 10, "text": B}], [{"start": 0, "end": 10, "text": A}]])
    self.assertEqual([s["document"] for s in timeline], ["text/c1.html", "text/c0.html"])
    self.assertEqual([s["audioSourceId"] for s in timeline], ["0.mp3", "1.mp3"])
    self.assertEqual([(s["start"], s["end"]) for s in timeline], [(0, 10), (0, 10)])
    self.assertEqual(report["readalongUsability"], "USABLE")
    self.assertEqual(report["textOrderEvents"][0]["reason"], "TRACK_ORDER_DIFFERS_FROM_TEXT")

  def test_unavailable_chunk_keeps_other_audio_without_claiming_full_processing(self):
    report, timeline = self.generate([[A]], [
      [{"start": 0, "end": 10, "text": "", "decodeUnavailable": True, "timingRejected": True}],
      [{"start": 0, "end": 10, "text": A}]])
    self.assertEqual(len(timeline), 1)
    self.assertEqual(timeline[0]["audioSourceId"], "1.mp3")
    self.assertFalse(report["fullAudioProcessed"])
    self.assertTrue(report["allTracksVisited"])
    self.assertEqual(report["metrics"]["unobservedDecodeSeconds"], 10)
    self.assertEqual(report["readalongUsability"], "REVIEW_MAPPING")

  def test_previous_track_does_not_resolve_ambiguous_new_track_prefix(self):
    filler = " ".join(f"filler{i}" for i in range(150))
    report, timeline = self.generate([[A, REPEAT, filler], [REPEAT, B]], [
      [{"start": 0, "end": 5, "text": A}, {"start": 5, "end": 10, "text": REPEAT}],
      [{"start": 0, "end": 5, "text": REPEAT}, {"start": 5, "end": 10, "text": B}]])
    self.assertFalse(any(s["audioSourceId"] == "1.mp3" and s["start"] == 0 for s in timeline))
    self.assertTrue(any(s["audioSourceId"] == "1.mp3" and s["start"] == 5 for s in timeline))
    self.assertEqual(report["localizationReasonCounts"]["AMBIGUOUS_MATCH"], 1)

  def test_gap_does_not_keep_stale_context_for_repeated_text(self):
    filler = " ".join(f"filler{i}" for i in range(150))
    report, timeline = self.generate([[A, REPEAT, filler], [REPEAT, B]], [[
      {"start": 0, "end": 5, "text": A}, {"start": 90, "end": 95, "text": REPEAT}]])
    self.assertEqual(len(timeline), 1)
    self.assertEqual(report["localizationReasonCounts"]["AMBIGUOUS_MATCH"], 1)


if __name__ == "__main__":
  unittest.main()
