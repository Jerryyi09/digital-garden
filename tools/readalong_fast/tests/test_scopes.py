"""Approved range unions must not hide unknown audio or break empty-track rules."""
import unittest
from pathlib import Path
import tempfile
from bs4 import BeautifulSoup

from tools.readalong_fast.pipeline import audit_candidate, verify_track_inventory
from tools.readalong_fast.scopes import material_ranges, subtract_ranges


class ScopeTests(unittest.TestCase):
  def policy(self, ranges):
    return {"approved": True, "sourceFingerprint": "a"*64,
      "materialIntervals": [{"audioSourceId": sid, "start": a, "end": b, "evidence": "Synthetic approved credits"}
                            for sid, a, b in ranges]}

  def audit(self, ranges, extra=None):
    speech = [{"id": "body", "audioSourceId": "body", "start": 0, "end": 100},
              {"id": "credits", "audioSourceId": "credits", "start": 0, "end": 100}]
    sources = {"body": {"duration": 100}, "credits": {"duration": 100}}
    timeline = [{"audioSourceId": "body", "start": 0, "end": 100, "speechUnitId": "body",
      "document": "text/a.html", "fragment": "p", "text": "Hello world", "occurrenceId": "0"}]
    policy = self.policy(ranges)
    if extra:
      policy.update(extra)
    return audit_candidate(timeline, speech, sources, {"a.html": BeautifulSoup('<p id="p">Hello world</p>', 'html.parser')}, [], policy, "a"*64)

  def test_fully_excluded_credit_track_is_not_an_unknown_empty_track(self):
    report = self.audit([("credits", 0, 100)])
    self.assertEqual(report["readalongUsability"], "USABLE_WITH_GAPS")
    self.assertEqual(report["metrics"]["emptyTracks"], [])
    self.assertEqual(report["metrics"]["fullyExcludedTracks"], ["credits"])
    self.assertEqual(report["metrics"]["unmappedSpeechUnitRatio"], 0)

  def test_partially_excluded_empty_track_stays_blocked(self):
    report = self.audit([("credits", 0, 99)])
    self.assertEqual(report["readalongUsability"], "REVIEW_MAPPING")
    self.assertEqual(report["metrics"]["emptyTracks"], ["credits"])

  def test_union_merges_adjacent_duplicate_and_overlapping_ranges(self):
    report = self.audit([("credits", 0, 60), ("credits", 40, 100), ("credits", 0, 60)])
    self.assertEqual(report["metrics"]["materialSpeechSeconds"], 100)
    self.assertEqual(len(report["materialIntervalsApplied"]), 1)
    self.assertEqual(report["metrics"]["observedSpeechUnitSeconds"], 100)

  def test_disconnected_ranges_preserve_internal_unknown_range(self):
    self.assertEqual(subtract_ranges(0, 100, [(0, 10), (90, 100)]), [(10, 90)])
    report = self.audit([("credits", 0, 10), ("credits", 90, 100)])
    self.assertEqual(report["longUnexplainedIntervals"], [{"audioSourceId": "credits", "start": 10, "end": 90, "unexplainedSeconds": 80}])

  def test_out_of_bounds_unknown_track_nan_and_proposals_do_not_exempt(self):
    for ranges, extra in [([("credits", 0, 101)], {}), ([("unknown", 0, 1)], {}),
        ([("credits", 0, float('nan'))], {}), ([("credits", 0, 100)], {"approved": False}),
        ([("credits", 0, 100)], {"sourceFingerprint": "b"*64})]:
      with self.subTest(ranges=ranges, extra=extra):
        report = self.audit(ranges, extra)
        self.assertEqual(report["readalongUsability"], "SCRIPT_ERROR")
        self.assertIn("MATERIAL_POLICY_INVALID", report["errors"])
        self.assertFalse(report["materialIntervalsApplied"])

  def test_legacy_single_authorized_range_remains_supported(self):
    sources = {"a": {"duration": 100}}
    policy = {"sourceFingerprint": "a"*64, "authorization": "User scope decision",
      "materialInterval": {"audioSourceId": "a", "start": 90, "end": 100, "evidence": "Credits"}}
    self.assertEqual(material_ranges(policy, sources, "a"*64), {"a": [(90, 100)]})

  def test_no_source_binding_cannot_be_a_quality_exemption(self):
    with self.assertRaises(ValueError):
      material_ranges(self.policy([("a", 0, 100)]), {"a": {"duration": 100}})

  def test_short_title_tracks_are_inventory_not_unregistered_noise(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      for name in ('body.mp3', 'title.mp3', '._body.mp3'):
        (root/name).write_bytes(b'fixture')
      (root/'readalong').mkdir()
      (root/'readalong/copy.mp3').write_bytes(b'generated asset')
      with self.assertRaisesRegex(ValueError, 'ERR_TRACK_INVENTORY_MISMATCH'):
        verify_track_inventory(root, [{'rel_to_book': 'body.mp3'}])
      verify_track_inventory(root, [{'rel_to_book': 'body.mp3'}, {'rel_to_book': 'title.mp3'}])
      with self.assertRaisesRegex(ValueError, 'ERR_TRACK_INVENTORY_MISMATCH'):
        verify_track_inventory(root, [{'rel_to_book': 'body.mp3'}, {'rel_to_book': 'title.mp3'}, {'rel_to_book': 'title.mp3'}])
