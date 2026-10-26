"""Unit tests for LIB-VERIFY-06 usability decoupling and 5% tolerance contract."""
import unittest
from tools.readalong.usability_evaluator import (
  evaluate_readalong_usability,
  USABILITY_USABLE,
  USABILITY_USABLE_WITH_GAPS,
  USABILITY_REVIEW_MAPPING,
  USABILITY_REVIEW_MATERIAL,
  USABILITY_SCRIPT_ERROR,
)


class Lib06ContractTests(unittest.TestCase):
  def evaluate(self, report, **kwargs):
    report["asrTokenEvidence"] = {"audioTokens": 1000, "matchedTokens": 1000}
    report.setdefault("quality_layers", {})
    report["quality_layers"].update({k: True for k in ("schema", "inventory", "monotonicity", "dom_integrity")})
    return evaluate_readalong_usability(report, **kwargs)

  def test_hard_error_yields_script_error(self):
    report = {
      "errors": [{"code": "ERR_DOM_REFERENCE_BROKEN", "msg": "corrupt span"}],
      "status": "FAILED",
      "track_stats": {"t1": {"duration": 100.0, "segment_count": 5}},
      "uncovered_intervals": [],
    }
    res = self.evaluate(report)
    self.assertEqual(res["readalongUsability"], USABILITY_SCRIPT_ERROR)
    self.assertEqual(res["certificationStatus"], "FAILED")
    self.assertIn("ERR_DOM_REFERENCE_BROKEN", res["hardErrors"])

  def test_unverified_outro_is_not_a_scope_exemption(self):
    # A 30s tail requires evidence even if the global ratio is below 5%.
    report = {
      "errors": [{"code": "ERR_UNEXPLAINED_GAP", "msg": "outro gap"}],
      "status": "FAILED",
      "track_stats": {"t1": {"duration": 1000.0, "segment_count": 100}},
      "uncovered_intervals": [
        {"track": "t1", "start": 970.0, "end": 1000.0, "gap": 30.0, "type": "TAIL_GAP"}
      ],
    }
    res = self.evaluate(report)
    self.assertEqual(res["readalongUsability"], USABILITY_REVIEW_MAPPING)
    self.assertEqual(res["certificationStatus"], "FAILED")
    self.assertAlmostEqual(res["metrics"]["scope_gap_ratio"], 0)
    self.assertEqual(res["actionRecommended"], "REVIEW_LOCAL_MAPPING")

  def test_strictly_aligned_yields_usable(self):
    # Total duration 1000s, 2s head delay (0.2%), 1s internal gap (0.1%) -> USABLE
    report = {
      "errors": [],
      "status": "NEEDS_REVIEW",
      "quality_layers": {"timing_verified": False},
      "track_stats": {"t1": {"duration": 1000.0, "segment_count": 100}},
      "uncovered_intervals": [
        {"track": "t1", "start": 0.0, "end": 2.0, "gap": 2.0, "type": "HEAD_DELAY"},
        {"track": "t1", "start": 100.0, "end": 101.0, "gap": 1.0, "type": "INTERNAL_VOID"}
      ],
    }
    res = self.evaluate(report)
    self.assertEqual(res["readalongUsability"], USABILITY_USABLE)
    self.assertEqual(res["certificationStatus"], "NEEDS_REVIEW")
    self.assertEqual(res["actionRecommended"], "ACCEPT")

  def test_gap_between_5_and_10_percent_yields_review_mapping(self):
    # Total duration 1000s, 70s internal gaps (7%) -> REVIEW_MAPPING
    report = {
      "errors": [{"code": "ERR_UNEXPLAINED_GAP", "msg": "gap"}],
      "status": "FAILED",
      "track_stats": {"t1": {"duration": 1000.0, "segment_count": 100}},
      "uncovered_intervals": [
        {"track": "t1", "start": 100.0, "end": 170.0, "gap": 70.0, "type": "INTERNAL_VOID"}
      ],
    }
    res = self.evaluate(report)
    self.assertEqual(res["readalongUsability"], USABILITY_REVIEW_MAPPING)
    self.assertEqual(res["certificationStatus"], "FAILED")
    self.assertEqual(res["actionRecommended"], "REVIEW_LOCAL_MAPPING")

  def test_lexical_divergence_does_not_prove_material_incompatibility(self):
    # ASR or algorithm errors can also cause zero lexical correspondence.
    report = {
      "errors": [{"code": "ERR_UNEXPLAINED_GAP", "msg": "large gap"}],
      "status": "FAILED",
      "track_stats": {"t1": {"duration": 1000.0, "segment_count": 50}},
      "uncovered_intervals": [
        {"track": "t1", "start": 100.0, "end": 250.0, "gap": 150.0, "type": "INTERNAL_VOID"}
      ],
    }
    unmapped_diags = [{"reason": "NO_LEXICAL_CORRESPONDENCE"} for _ in range(10)]
    res = self.evaluate(report, unmapped_diagnostics=unmapped_diags)
    self.assertEqual(res["readalongUsability"], USABILITY_REVIEW_MAPPING)
    self.assertEqual(res["actionRecommended"], "REVIEW_LOCAL_MAPPING")

  def test_material_policy_for_make_your_bed(self):
    # Simulated Make Your Bed with 91.55s outro
    policy_entry = {
      "unitId": "心智成长/Make Your Bed",
      "sourceFingerprint": "a"*64,
      "materialInterval": {
        "audioSourceId": "Make Your Bed-Part02.mp3",
        "start": 3041.04,
        "end": 3132.59,
        "type": "AUDIO_ONLY_PRODUCTION_CREDITS",
        "evidence": "Synthetic test credits reference"
      }
    }
    report = {
      "sourceFingerprint": "a"*64,
      "errors": [{"code": "ERR_UNEXPLAINED_GAP", "msg": "outro"}],
      "status": "FAILED",
      "track_stats": {
        "Make Your Bed-Part01.mp3": {"duration": 2900.0, "segment_count": 300},
        "Make Your Bed-Part02.mp3": {"duration": 3132.59, "segment_count": 300}
      },
      "uncovered_intervals": [
        {"track": "Make Your Bed-Part02.mp3", "start": 3041.04, "end": 3132.59, "gap": 91.55, "type": "TAIL_GAP"}
      ]
    }
    res = self.evaluate(report, material_policy_entry=policy_entry)
    self.assertEqual(res["readalongUsability"], USABILITY_USABLE_WITH_GAPS)
    self.assertEqual(res["certificationStatus"], "FAILED")
    self.assertTrue(res["materialPolicyApplied"])


if __name__ == "__main__":
  unittest.main()
