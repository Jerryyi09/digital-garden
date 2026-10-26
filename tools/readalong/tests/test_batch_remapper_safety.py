"""Durable checkpoint and fail-closed orchestration regressions."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

try:
  from tools.readalong.batch_candidate_remapper import BatchRemapper, atomic_json, input_blocker
except ImportError:
  BatchRemapper = None


@unittest.skipIf(BatchRemapper is None, "Use readalong .venv")
class BatchSafetyTests(unittest.TestCase):
  def setUp(self):
    temp = tempfile.TemporaryDirectory()
    self.addCleanup(temp.cleanup)
    self.root = Path(temp.name)
    self.unit = {"unit_id": "root/book", "book_dir": str(self.root / "book"),
                 "audio_tracks": [{"rel_to_book": "01.mp3", "sha256": "x", "measured_duration": 10}],
                 "epubs": [{"rel_to_book": "b.epub", "sha256": "y", "valid_zip": True}],
                 "detected_languages": ["en"], "active_readalong_fingerprint": None}
    atomic_json(self.root / "inventory.json", {"units": [self.unit]})

  def test_corrupt_ledger_never_resets_attempts(self):
    (self.root / "results.json").write_text('{bad')
    with self.assertRaises(ValueError):
      BatchRemapper(self.root)

  def test_nonobject_ledger_is_rejected(self):
    atomic_json(self.root / "results.json", [])
    with self.assertRaises(ValueError):
      BatchRemapper(self.root)

  def test_legacy_ledger_requires_reviewed_recovery(self):
    atomic_json(self.root / "results.json", {"schema_version": 2, "records": {}})
    with self.assertRaises(ValueError):
      BatchRemapper(self.root)

  def test_stop_marker_blocks_resume(self):
    (self.root / "STOP.md").write_text("stopped")
    with self.assertRaises(RuntimeError):
      BatchRemapper(self.root)

  def test_orphan_candidates_do_not_reset_budget(self):
    (self.root / "candidates/old").mkdir(parents=True)
    with self.assertRaises(RuntimeError):
      BatchRemapper(self.root)

  def test_missing_language_metadata_is_not_evidence_of_non_english_content(self):
    self.unit.pop("detected_languages")
    self.assertIsNone(input_blocker(self.unit))
    self.assertNotIn("detected_languages", self.unit)
    self.unit["detected_languages"] = ["zh"]
    self.assertEqual(input_blocker(self.unit), "LANGUAGE_REQUIRES_REVIEW")

  def test_blockers_derive_from_inventory_not_book_title(self):
    self.unit["epubs"] *= 2
    self.assertEqual(input_blocker(self.unit), "MULTI_EPUB")

  def test_modified_inventory_cannot_reuse_completed_checkpoint(self):
    runner = BatchRemapper(self.root)
    runner._save_ledger()
    self.unit["unit_id"] = "root/changed"
    atomic_json(self.root / "inventory.json", {"units": [self.unit]})
    with self.assertRaises(ValueError):
      BatchRemapper(self.root)

  def test_failed_candidate_stops_before_retry_and_persists_budget(self):
    from tools.readalong import batch_candidate_remapper as module
    runner = BatchRemapper(self.root)
    snap = {"sources": {"01.mp3": "x", "b.epub": "y"}, "active": None}
    def generate(book, candidate, **kwargs):
      state = json.loads((self.root / "results.json").read_text())
      self.assertEqual(state["records"][self.unit["unit_id"]]["attempts"], 1)
      atomic_json(candidate / "readalong.manifest.json", {"sampleAligned": False})
    with patch.object(module, "snapshot", return_value=snap), \
         patch.object(runner, "_assert_gate"), \
         patch.object(module, "align_single_book_universal", side_effect=generate) as align, \
         patch.object(module, "audit_book_authoritative", return_value={
           "status": "FAILED", "errors": [{"code": "ERR_DUPLICATE_DOM_ID"}]}):
      with self.assertRaises(RuntimeError):
        runner.run_unit(self.unit)
      self.assertEqual(align.call_count, 1)
    self.assertTrue((self.root / "STOP.md").is_file())
    self.assertEqual(json.loads((self.root / "results.json").read_text())
                     ["records"][self.unit["unit_id"]]["candidateStatusAfter"], "FAILED")

  def test_direct_python_run_cannot_bypass_missing_gate(self):
    from tools.readalong import batch_candidate_remapper as module
    runner = BatchRemapper(self.root)
    with patch.object(module, "align_single_book_universal") as generate:
      with self.assertRaises(RuntimeError):
        runner.run_unit(self.unit)
      generate.assert_not_called()

  def test_inherited_exhausted_budget_blocks_generation(self):
    from tools.readalong import batch_candidate_remapper as module
    runner = BatchRemapper(self.root)
    uid = self.unit["unit_id"]
    runner.ledger["records"][uid] = {"attempts": 2, "inheritedOnly": True}
    snap = {"sources": {"01.mp3": "x", "b.epub": "y"}, "active": None}
    with patch.object(module, "snapshot", return_value=snap), \
         patch.object(module, "align_single_book_universal") as generate:
      with self.assertRaisesRegex(RuntimeError, "budget exhausted"):
        runner._run_unit_locked(self.unit)
      generate.assert_not_called()

  def test_material_quarantine_preserves_failed_status_and_budget_without_asr(self):
    from tools.readalong import batch_candidate_remapper as module
    runner = BatchRemapper(self.root)
    uid = self.unit["unit_id"]
    runner.ledger["records"][uid] = {"attempts": 2, "inheritedOnly": True}
    runner._gate_decision = {"sampleEvaluations": {uid: {
      "batchExcluded": True, "audit": {"status": "FAILED"},
      "materialIssue": {"classification": "MATERIAL_MISMATCH"},
      "candidatePath": "/synthetic/candidate", "candidateFingerprint": "a" * 64,
    }}}
    snap = {"sources": {"01.mp3": "x", "b.epub": "y"}, "active": None}
    with patch.object(module, "snapshot", return_value=snap), \
         patch.object(module, "align_single_book_universal") as generate:
      record = runner._run_unit_locked(self.unit)
      generate.assert_not_called()
    self.assertEqual(record["attempts"], 2)
    self.assertEqual(record["candidateStatusAfter"], "FAILED")
    self.assertEqual(record["workflowStatus"], "QUARANTINED_MATERIAL")

  def test_unproven_inherited_completion_is_not_reused(self):
    from tools.readalong import batch_candidate_remapper as module
    runner = BatchRemapper(self.root)
    uid = self.unit["unit_id"]
    runner.ledger["records"][uid] = {"attempts": 1, "inheritedOnly": True,
                                      "workflow_completed": False}
    snap = {"sources": {"01.mp3": "x", "b.epub": "y"}, "active": None}
    def generate(book, candidate, **kwargs):
      self.assertEqual(candidate.name, "attempt-02")
      self.assertEqual(runner.ledger["records"][uid]["attempts"], 2)
      atomic_json(candidate / "readalong.manifest.json", {"sampleAligned": False})
    with patch.object(module, "snapshot", return_value=snap), \
         patch.object(module, "audit_book_authoritative", side_effect=[
           {"status": "FAILED"}, {"status": "NEEDS_REVIEW", "errors": [{"code": "ERR_TIMING_UNVERIFIED"}]}]), \
         patch.object(module, "align_single_book_universal", side_effect=generate) as align:
      record = runner._run_unit_locked(self.unit)
      self.assertEqual(align.call_count, 1)
      self.assertEqual(record["attempts"], 2)
      self.assertEqual(record["candidateStatusAfter"], "NEEDS_REVIEW")
