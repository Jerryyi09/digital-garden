"""Live gate regressions using decodable physical audio, not fake PASS reports."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.readalong.recovery_gate import (
  bind_sample, build_gate_evidence, evaluate_sample_candidate, evaluate_recovery_gate,
  assert_recovery_gate_passed, RecoveryGateRejection, REQUIRED_UNITS,
  REQUIRED_STRUCTURAL_LAYERS,
)
from tools.readalong.tests.build_audit_fixtures import make_clean_book


class TestRecoveryGate(unittest.TestCase):
  def setUp(self):
    self.tmp = tempfile.TemporaryDirectory()
    self.addCleanup(self.tmp.cleanup)
    self.root = Path(self.tmp.name)
    self.books = [make_clean_book(self.root / name) for name in ("one", "two")]
    self.samples = [bind_sample(uid, book, book / "readalong")
                    for uid, book in zip(REQUIRED_UNITS, self.books)]
    self.mapping = dict(zip(REQUIRED_UNITS, self.books))

  def write_gate(self, evidence):
    path = self.root / "gate.json"
    path.write_text(json.dumps(evidence))
    return path

  def break_timeline(self, index=0):
    path = self.books[index] / "readalong/timeline.json"
    rows = json.loads(path.read_text())
    rows[1]["start"] = 7
    path.write_text(json.dumps(rows))
    self.samples[index] = bind_sample(REQUIRED_UNITS[index], self.books[index],
                                     self.books[index] / "readalong")

  def test_gate_rejects_when_any_sample_has_failed_status(self):
    self.break_timeline()
    decision = evaluate_recovery_gate(self.samples)
    self.assertFalse(decision["gatePassed"])
    self.assertIn(REQUIRED_UNITS[0], decision["failedUnits"])

  def test_cannot_substitute_failed_sample_with_another_passed_sample(self):
    decision = evaluate_recovery_gate(self.samples[1:])
    self.assertFalse(decision["gatePassed"])
    self.assertIn(REQUIRED_UNITS[0], decision["missingRequiredUnits"])

  def test_gate_allows_structural_pass_when_only_acoustic_reference_missing(self):
    evidence = build_gate_evidence(self.samples)
    self.assertTrue(evidence["gatePassed"])
    sample = evidence["sampleEvaluations"][REQUIRED_UNITS[0]]
    self.assertEqual(sample["audit"]["status"], "NEEDS_REVIEW")
    self.assertEqual([e["code"] for e in sample["audit"]["errors"]], ["ERR_TIMING_UNVERIFIED"])
    self.assertEqual(sample["status"], "STRUCTURAL_PASS")
    self.assertFalse(sample["acousticVerified"])
    decision = assert_recovery_gate_passed(self.write_gate(evidence), self.mapping)
    self.assertTrue(decision["gatePassed"])

  def test_assert_recovery_gate_passed_intercepts_invalid_or_missing_evidence(self):
    for value in ({"gatePassed": True, "decision": "APPROVED_FOR_BATCH"},
                  {"gatePassed": False, "decision": "REJECTED"}, [], None):
      with self.assertRaises(RecoveryGateRejection):
        assert_recovery_gate_passed(self.write_gate(value))
    with self.assertRaises(RecoveryGateRejection):
      assert_recovery_gate_passed(self.root / "nonexistent")

  def test_empty_candidate_and_forged_report_cannot_pass(self):
    candidate = self.root / "empty"
    candidate.mkdir()
    sample = bind_sample(REQUIRED_UNITS[0], self.books[0], candidate)
    report = self.root / "fake-report.json"
    report.write_text(json.dumps({"status": "PASS", "errors": [], "quality_layers": {
      key: True for key in ("schema", "inventory", "monotonicity", "dom_integrity",
                           "coverage_and_gaps", "density", "timing_verified")}}))
    sample["reportPath"] = str(report)
    self.assertFalse(evaluate_sample_candidate(sample)["passed"])

  def test_empty_reduced_and_duplicate_required_sets_are_rejected(self):
    for required in ([], [REQUIRED_UNITS[0]], list(REQUIRED_UNITS) + [REQUIRED_UNITS[0]]):
      with self.assertRaises(RecoveryGateRejection):
        evaluate_recovery_gate(self.samples, required)

  def test_duplicate_sample_cannot_overwrite_failed_decision(self):
    with self.assertRaises(RecoveryGateRejection):
      evaluate_recovery_gate(self.samples + [self.samples[0]])

  def test_fingerprint_is_mandatory_not_an_optional_hint(self):
    for key in ("expectedFingerprint", "sourceFingerprint"):
      for value in ("", None, "0" * 64):
        sample = {**self.samples[0], key: value}
        self.assertFalse(evaluate_sample_candidate(sample)["passed"])

  def test_live_audit_rejects_forged_approval_even_with_matching_fingerprints(self):
    self.break_timeline()
    evidence = build_gate_evidence(self.samples)
    evidence.update(gatePassed=True, decision="APPROVED_FOR_BATCH")
    with self.assertRaises(RecoveryGateRejection):
      assert_recovery_gate_passed(self.write_gate(evidence), self.mapping)

  def test_candidate_changed_after_approval_is_rejected(self):
    evidence = build_gate_evidence(self.samples)
    self.break_timeline()
    with self.assertRaises(RecoveryGateRejection):
      assert_recovery_gate_passed(self.write_gate(evidence), self.mapping)

  def test_source_changed_after_approval_is_rejected(self):
    evidence = build_gate_evidence(self.samples)
    (self.books[0] / "added.mp3").write_bytes(b"new input")
    with self.assertRaises(RecoveryGateRejection):
      assert_recovery_gate_passed(self.write_gate(evidence), self.mapping)

  def test_swapped_physical_book_is_rejected(self):
    evidence = build_gate_evidence(self.samples)
    swapped = dict(zip(REQUIRED_UNITS, reversed(self.books)))
    with self.assertRaises(RecoveryGateRejection):
      assert_recovery_gate_passed(self.write_gate(evidence), swapped)

  def test_stale_code_model_and_policy_are_rejected(self):
    evidence = build_gate_evidence(self.samples)
    for key in ("codeSha256", "modelSha256", "policyVersion", "materialPolicySha256"):
      wrong = {**evidence, "identity": {**evidence["identity"], key: "stale"}}
      with self.assertRaises(RecoveryGateRejection):
        assert_recovery_gate_passed(self.write_gate(wrong), self.mapping)

  def test_files_changed_during_audit_are_rejected(self):
    from tools.readalong import recovery_gate as module
    original = module.audit_book_authoritative
    def mutate(*args, **kwargs):
      report = original(*args, **kwargs)
      (self.books[0] / "readalong/changed.txt").write_text("changed")
      return report
    with patch.object(module, "audit_book_authoritative", side_effect=mutate):
      self.assertFalse(evaluate_sample_candidate(self.samples[0])["passed"])

  def test_explicit_material_quarantine_does_not_promote_failed_quality(self):
    import wave
    from tools.readalong import material_policy
    from tools.readalong.batch_candidate_remapper import compute_sha256
    book = self.books[0]
    audio = book / "track_01.mp3"
    with wave.open(str(audio), "wb") as stream:
      stream.setnchannels(1)
      stream.setsampwidth(2)
      stream.setframerate(8000)
      stream.writeframes(b"\0\0" * (61 * 8000))
    manifest = book / "readalong/readalong.manifest.json"
    value = json.loads(manifest.read_text())
    value["audioSources"][0].update(duration=61, sha256=compute_sha256(audio))
    manifest.write_text(json.dumps(value))
    self.samples[0] = bind_sample(REQUIRED_UNITS[0], book, book / "readalong")
    entry = {"unitId": REQUIRED_UNITS[0], "sourceFingerprint": self.samples[0]["sourceFingerprint"],
             "disposition": "QUARANTINE_BOOK", "qualityStatusUnchanged": True, "publishAllowed": False,
             "materialInterval": {"audioSourceId": "track_01.mp3", "end": 61},
             "mappingIntervalStillUnresolved": {"start": 15},
             "allowedAuditCodes": ["ERR_UNEXPLAINED_GAP", "ERR_TIMING_UNVERIFIED"]}
    policy = self.root / "material-policy.json"
    policy.write_text(json.dumps({"schemaVersion": 1, "entries": [entry]}))
    with patch.object(material_policy, "POLICY_PATH", policy):
      evidence = build_gate_evidence(self.samples)
      self.assertEqual(evidence["decision"], "APPROVED_FOR_BATCH_WITH_QUARANTINE")
      result = evidence["sampleEvaluations"][REQUIRED_UNITS[0]]
      self.assertFalse(result["passed"])
      self.assertTrue(result["batchExcluded"])
      self.assertEqual(result["audit"]["status"], "FAILED")
      self.assertTrue(assert_recovery_gate_passed(self.write_gate(evidence), self.mapping)["gatePassed"])
      # The same material policy must not hide new DOM/script failures.
      html = book / "readalong/text/chapter1.html"
      html.write_text(html.read_text().replace('id="c01-segment02"', 'id="c01-segment01"'))
      self.samples[0] = bind_sample(REQUIRED_UNITS[0], book, book / "readalong")
      self.assertFalse(build_gate_evidence(self.samples)["gatePassed"])

  def test_material_policy_cannot_cover_a_new_gap_outside_declared_range(self):
    from tools.readalong.material_policy import classify_quarantine
    report = {"status": "FAILED", "quality_layers": {k: True for k in REQUIRED_STRUCTURAL_LAYERS},
              "errors": [{"code": "ERR_UNEXPLAINED_GAP"}],
              "uncovered_intervals": [{"track": "Make Your Bed-Part02.mp3", "start": 1,
                                       "end": 100, "gap": 99, "type": "INTERNAL_VOID"}]}
    sample = {"unitId": REQUIRED_UNITS[0],
              "sourceFingerprint": "33005cd00d0d97d3c2bb081ab79bcda1e5d2e908996444894d1343c1b64341d2"}
    self.assertIsNone(classify_quarantine(sample, report))


if __name__ == "__main__":
  unittest.main()
