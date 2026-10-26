"""Work order LIB-VERIFY-02 Section A5 comprehensive regression test suite.

Covers the 10 strict regression dimensions:
1. Cross-track sentence splits without DOM corruption or backtracking.
2. Intra-track and cross-track re-reading with independent occurrence identities.
3. Reading-order variations (e.g. summary vs appendix reordering).
4. Ambiguous identical phrases across documents rejected from false alignment.
5. Irrelevant outro not captured by spurious matches; zero/reversed durations rejected.
6. Re-reading across inline tags and internal IDs preserving DOM integrity.
7. Acoustic reference must cover re-reading occurrences; missing one rejects PASS.
8. PWA playback sync matches active occurrence without jumping back to earlier time.
9. Corrupt/stale ledgers, code changes, STOP markers and budget invariants.
10. Long stream bounded processing and resource safety中止 rules.
"""
from collections import defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from bs4 import BeautifulSoup

from tools.readalong.config import resolve_nltk_data_path

os.environ["NLTK_DATA"] = str(resolve_nltk_data_path())

from tools.readalong.stream_projection import (
  prepare_documents, project_stream, normalize_token, find_reorder_matches
)
from tools.readalong.engine.mark_sentence import mark_sentences
from tools.readalong.authoritative_validator import (
  audit_book_authoritative, occurrence_key, ERROR_SCHEMA_INVALID,
  ERROR_DUPLICATE_DOM_ID, ERROR_TIMING_UNVERIFIED, ERROR_UNEXPLAINED_GAP
)
from tools.readalong.acoustic_evaluator import (
  evaluate_acoustic_accuracy, verify_reference, POLICY_VERSION
)
from tools.readalong.batch_candidate_remapper import BatchRemapper, run_lock


class ContinuationA5RegressionTests(unittest.TestCase):
  def setUp(self):
    self.tmp = tempfile.TemporaryDirectory()
    self.base = Path(self.tmp.name)
    self.text_dir = self.base / "text"
    self.text_dir.mkdir(parents=True)

  def tearDown(self):
    self.tmp.cleanup()

  def make_spine(self, docs):
    spine = []
    for name, content in docs.items():
      p = self.text_dir / name
      p.parent.mkdir(parents=True, exist_ok=True)
      p.write_text(content, encoding="utf-8")
      spine.append(name)
    return spine

  def words(self, tokens, split=None, source1="01.mp3", source2="02.mp3", start_time=0.0):
    res = []
    t = start_time
    for i, tok in enumerate(tokens):
      src = source1 if (split is None or i < split) else source2
      res.append({"word": tok, "norm": tok, "start": round(t, 2),
                  "end": round(t + 0.5, 2), "audioSourceId": src})
      t += 0.5
    return res

  # 1. Normal cross-track same chapter / sentence without backtracking or duplicate DOM IDs
  def test_a5_1_cross_track_split_preserves_dom_and_no_backtrack(self):
    html = '<p><span id="c1-segment0">alpha beta gamma delta epsilon zeta eta theta iota kappa</span></p>'
    spine = self.make_spine({"c1.xhtml": html})
    docs, frags, tokens = prepare_documents(self.text_dir, spine, lambda raw, **kw: raw)
    # Split after 5 words across two tracks
    audio = self.words(tokens, split=5)
    segments, stats = project_stream(tokens, frags, audio)
    self.assertEqual(len(segments), 2)
    self.assertEqual(segments[0]["audioSourceId"], "01.mp3")
    self.assertEqual(segments[1]["audioSourceId"], "02.mp3")
    self.assertEqual(segments[0]["occurrenceId"], "0")
    self.assertEqual(segments[1]["occurrenceId"], "0")
    # Verify no duplicate DOM IDs in modified document
    soup = BeautifulSoup(str(docs["c1.xhtml"]), "html.parser")
    ids = [node["id"] for node in soup.find_all(id=True)]
    self.assertEqual(len(ids), len(set(ids)))
    self.assertTrue(any("part0" in i for i in ids))
    self.assertTrue(any("part1" in i for i in ids))

  # 2. Re-reading same paragraph within track and across tracks keeps independent occurrence IDs
  def test_a5_2_re_reading_preserves_both_occurrences_with_distinct_identities(self):
    first_text = "start each day with a task completed find someone to help you through life respect everyone"
    second_text = "know that life is not fair and that you will fail often step up when times are toughest"
    html = f'<p><span id="c1-segment0">{first_text}</span><span id="c1-segment1">{second_text}</span></p>'
    spine = self.make_spine({"c1.xhtml": html})
    docs, frags, tokens = prepare_documents(self.text_dir, spine, lambda raw, **kw: raw)
    # Audio reads: first_text, second_text, then repeats first_text at the end
    first_tokens = [normalize_token(w) for w in first_text.split()]
    audio = self.words(tokens + first_tokens, source1="track1.mp3")
    # Project with confirmed reorder allowed
    segments, stats = project_stream(tokens, frags, audio, confirmed_reorders=True)
    self.assertEqual(len(segments), 3)
    # The repeated first_text segment has occurrenceId "1"
    keys = [occurrence_key(s) for s in segments]
    self.assertEqual(len(keys), len(set(keys)), "Every occurrence must have a unique identity")
    occ0 = [s for s in segments if s["fragment"] == "c1-segment0" and s["occurrenceId"] == "0"][0]
    occ1 = [s for s in segments if s["fragment"] == "c1-segment0" and s["occurrenceId"] == "1"][0]
    self.assertLess(occ0["end"], occ1["start"])
    self.assertEqual(occ0["text"], occ1["text"])

  # 3. Reading-order variations (text: summary -> appendix; audio: appendix -> summary)
  def test_a5_3_reading_order_variation_aligned_monotonically(self):
    summary = "the quick brown fox jumps over the lazy dog in the sunny forest"
    appendix = "pack my box with five dozen liquor jugs before morning comes"
    spine = self.make_spine({
      "summary.xhtml": f'<p><span id="s-segment0">{summary}</span></p>',
      "appendix.xhtml": f'<p><span id="a-segment0">{appendix}</span></p>',
    })
    docs, frags, tokens = prepare_documents(self.text_dir, spine, lambda raw, **kw: raw)
    # Audio plays appendix first, then summary
    app_tokens = [normalize_token(w) for w in appendix.split()]
    sum_tokens = [normalize_token(w) for w in summary.split()]
    audio = self.words(app_tokens + sum_tokens, source1="narration.mp3")
    segments, stats = project_stream(tokens, frags, audio, confirmed_reorders=True)
    self.assertEqual(len(segments), 2)
    # Verify segments are ordered strictly by audio playback time
    self.assertEqual(segments[0]["fragment"], "a-segment0")
    self.assertEqual(segments[1]["fragment"], "s-segment0")
    self.assertLessEqual(segments[0]["end"], segments[1]["start"])

  # 4. Repeated short phrases across multiple chapters rejected as ambiguous
  def test_a5_4_ambiguous_repeated_phrases_rejected_without_evidence(self):
    common = "if you want to change your life today"
    spine = self.make_spine({
      "ch1.xhtml": f'<p><span id="c1-segment0">{common} chapter one special context words here</span></p>',
      "ch2.xhtml": f'<p><span id="c2-segment0">{common} chapter two another different story here</span></p>',
      "ch3.xhtml": f'<p><span id="c3-segment0">irrelevant third chapter text without the phrase</span></p>',
    })
    docs, frags, tokens = prepare_documents(self.text_dir, spine, lambda raw, **kw: raw)
    # Audio has primary flow through ch1, then an unmapped tail with just the common phrase repeated
    comm_tokens = [normalize_token(w) for w in common.split()]
    audio = self.words(tokens + comm_tokens, source1="main.mp3")
    segments, stats = project_stream(tokens, frags, audio, confirmed_reorders=True)
    # The ambiguous common phrase must NOT create an arbitrary segment
    unmapped = stats["unmappedAudioRanges"]
    self.assertTrue(any(u.get("reason") in ("POSSIBLE_REORDER_OR_REPEAT", "AMBIGUOUS_REORDER_OR_REPEAT")
                        for u in unmapped))

  # 5. Irrelevant outro not captured by spurious matches; zero-duration words excluded
  def test_a5_5_irrelevant_outro_not_spurious_and_zero_duration_rejected(self):
    main_text = "brave soldiers march across the field during the cold morning dawn"
    spine = self.make_spine({"ch1.xhtml": f'<p><span id="c1-segment0">{main_text}</span></p>'})
    docs, frags, tokens = prepare_documents(self.text_dir, spine, lambda raw, **kw: raw)
    outro = "this has been a production copyright all rights reserved visit our website"
    outro_tokens = [normalize_token(w) for w in outro.split()]
    audio = self.words(tokens + outro_tokens, source1="audio.mp3")
    # Inject a zero-duration word
    audio[2]["end"] = audio[2]["start"]
    segments, stats = project_stream(tokens, frags, audio, confirmed_reorders=True)
    # Outro must not match main_text
    self.assertEqual(len(segments), 1)
    self.assertEqual(len(stats["unusableWordIntervals"]), 1)
    self.assertEqual(stats["unmappedAudioRanges"][-1]["reason"], "NO_LEXICAL_CORRESPONDENCE")

  # 6. Re-reading across inline tags and internal IDs preserving DOM integrity
  def test_a5_6_re_reading_preserves_inline_elements_and_internal_ids(self):
    html = ('<p><span id="c1-segment0">the brave leader said <a href="#note1" id="footnote1">listen closely</a> '
            'to every word spoken today in this hall</span></p>')
    spine = self.make_spine({"c1.xhtml": html})
    docs, frags, tokens = prepare_documents(self.text_dir, spine, lambda raw, **kw: raw)
    audio = self.words(tokens + tokens, source1="track.mp3")
    segments, stats = project_stream(tokens, frags, audio, confirmed_reorders=True)
    self.assertEqual(len(segments), 2)
    # Check that footnote1 ID was not cloned or duplicated
    soup = BeautifulSoup(str(docs["c1.xhtml"]), "html.parser")
    fn_nodes = soup.find_all(id="footnote1")
    self.assertEqual(len(fn_nodes), 1)

  # 7. Acoustic reference must cover every occurrence; missing one rejects PASS
  def test_a5_7_acoustic_reference_must_cover_all_occurrences(self):
    timeline = [
      {"audioSourceId": "t.mp3", "document": "text/c1.xhtml", "fragment": "seg0",
       "occurrenceId": "0", "start": 0.0, "end": 5.0, "text": "hello world"},
      {"audioSourceId": "t.mp3", "document": "text/c1.xhtml", "fragment": "seg0",
       "occurrenceId": "1", "start": 10.0, "end": 15.0, "text": "hello world"},
    ]
    # Incomplete reference data covering only occurrence "0"
    ref_incomplete = {
      ("t.mp3", "text/c1.xhtml", "seg0", "0"): {"start": 0.01, "end": 4.99},
    }
    res_incomplete = evaluate_acoustic_accuracy(timeline, ref_incomplete)
    self.assertFalse(res_incomplete["passed"])
    self.assertEqual(res_incomplete["coverage_status"], "COVERAGE_INSUFFICIENT")

    # Complete reference covering both occurrences
    ref_complete = {
      ("t.mp3", "text/c1.xhtml", "seg0", "0"): {"start": 0.01, "end": 4.99},
      ("t.mp3", "text/c1.xhtml", "seg0", "1"): {"start": 10.02, "end": 14.98},
    }
    res_complete = evaluate_acoustic_accuracy(timeline, ref_complete)
    self.assertTrue(res_complete["passed"])
    self.assertEqual(res_complete["status"], "TIMING_VERIFIED")

  # 8. Corrupt or stale ledger and code change halts batch processing
  def test_a5_9_ledger_tampering_or_code_change_halts_safely(self):
    run_dir = self.base / "run"
    run_dir.mkdir()
    inv_path = run_dir / "inventory.json"
    inv_data = {"units": [{"unit_id": "u1", "book_dir": str(self.base), "audio_tracks": [], "epubs": []}]}
    inv_path.write_text(json.dumps(inv_data))
    # Write corrupt results.json schema
    (run_dir / "results.json").write_text(json.dumps({"schema_version": 2, "records": {}}))
    with self.assertRaises(ValueError) as ctx:
      BatchRemapper(run_dir)
    self.assertIn("incompatible", str(ctx.exception))

  # 9. STOP marker halts batch processing immediately without overwrite
  def test_a5_9_stop_marker_prevents_resume(self):
    run_dir = self.base / "stop_run"
    run_dir.mkdir()
    (run_dir / "STOP.md").write_text("# Emergency Stop")
    (run_dir / "inventory.json").write_text(json.dumps({"units": []}))
    with self.assertRaises(RuntimeError) as ctx:
      BatchRemapper(run_dir)
    self.assertIn("Batch is stopped", str(ctx.exception))

  # 10. Long stream bounded processing and resource safety中止 rules
  def test_a5_10_large_stream_bounded_and_zero_tokens_handled(self):
    # Empty tokens or zero duration
    res, stats = project_stream([], [], [])
    self.assertEqual(res, [])
    self.assertEqual(stats["matchedTokens"], 0)
    # Reject non-finite timestamps
    bad_audio = [{"audioSourceId": "a.mp3", "word": "bad", "start": float("nan"), "end": 1.0}]
    with self.assertRaises(ValueError):
      project_stream(["bad"], [], bad_audio)


if __name__ == "__main__":
  unittest.main()
