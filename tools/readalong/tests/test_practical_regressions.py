"""Counterexamples for practical usability and evidence-preserving timing."""
import unittest
from tools.readalong.usability_evaluator import evaluate_readalong_usability


def report(gaps=None):
  return {
    "status": "NEEDS_REVIEW", "errors": [],
    "asrTokenEvidence": {"audioTokens": 1000, "matchedTokens": 1000},
    "quality_layers": {k: True for k in ("schema", "inventory", "monotonicity", "dom_integrity")},
    "track_stats": {"a": {"duration": 1000.0, "segment_count": 10}},
    "uncovered_intervals": gaps or [],
  }


def gap(start, end, kind="TAIL_GAP"):
  return {"track": "a", "start": start, "end": end, "gap": end-start, "type": kind}


class PracticalRegressions(unittest.TestCase):
  def test_empty_report_cannot_pass(self):
    self.assertEqual(evaluate_readalong_usability({})["readalongUsability"], "SCRIPT_ERROR")

  def test_truncated_tail_is_not_material(self):
    value = evaluate_readalong_usability(report([gap(3, 1000)]))
    self.assertEqual(value["readalongUsability"], "REVIEW_MAPPING")
    self.assertEqual(value["metrics"]["scope_gap_ratio"], 0)

  def test_small_global_ratio_cannot_hide_long_local_void(self):
    value = evaluate_readalong_usability(report([gap(100, 140, "INTERNAL_VOID")]))
    self.assertEqual(value["readalongUsability"], "REVIEW_MAPPING")

  def test_distributed_small_gaps_within_five_percent_are_usable(self):
    gaps = [gap(i*100, i*100+4, "INTERNAL_VOID") for i in range(10)]
    value = evaluate_readalong_usability(report(gaps))
    self.assertEqual(value["readalongUsability"], "USABLE_WITH_GAPS")
    self.assertAlmostEqual(value["metrics"]["narration_gap_ratio"], .04)

  def test_invalid_metrics_cannot_pass(self):
    for duration in (0, -1, float("nan"), float("inf"), True):
      data = report()
      data["track_stats"]["a"]["duration"] = duration
      self.assertEqual(evaluate_readalong_usability(data)["readalongUsability"], "SCRIPT_ERROR")

  def test_duplicate_gap_accounting_rejected(self):
    self.assertEqual(evaluate_readalong_usability(report([gap(900, 1000)]*2))["readalongUsability"], "SCRIPT_ERROR")

  def test_unknown_error_cannot_pass(self):
    data = report()
    data["errors"] = [{"code": "ERR_NEW_UNKNOWN_FAILURE"}]
    self.assertEqual(evaluate_readalong_usability(data)["readalongUsability"], "SCRIPT_ERROR")

  def test_lexical_failure_alone_is_not_material_proof(self):
    value = evaluate_readalong_usability(report([gap(100, 300, "INTERNAL_VOID")]),
      unmapped_diagnostics=[{"reason": "NO_LEXICAL_CORRESPONDENCE"}]*10)
    self.assertEqual(value["readalongUsability"], "REVIEW_MAPPING")

  def test_material_policy_needs_source_binding(self):
    policy = {"sourceFingerprint": "a"*64, "materialInterval": {
      "audioSourceId": "a", "start": 900, "end": 1000, "evidence": "credits"}}
    data = report([gap(900, 1000)])
    self.assertEqual(evaluate_readalong_usability(data, policy)["readalongUsability"], "SCRIPT_ERROR")
    data["sourceFingerprint"] = "a"*64
    value = evaluate_readalong_usability(data, policy)
    self.assertEqual(value["readalongUsability"], "USABLE_WITH_GAPS")
    self.assertAlmostEqual(value["metrics"]["scope_gap_ratio"], .1)

  def test_many_short_holes_cannot_hide_unmatched_speech(self):
    data = report([gap(i*5, i*5+1, "INTERNAL_VOID") for i in range(100)])
    data["asrTokenEvidence"]["matchedTokens"] = 100
    self.assertEqual(evaluate_readalong_usability(data)["readalongUsability"], "REVIEW_MAPPING")

  def test_missing_lexical_evidence_is_not_proof_of_following(self):
    data = report()
    del data["asrTokenEvidence"]
    self.assertEqual(evaluate_readalong_usability(data)["readalongUsability"], "REVIEW_MAPPING")

  def test_credit_words_excluded_only_by_physical_interval(self):
    data = report([gap(900, 1000)])
    data["sourceFingerprint"] = "b"*64
    data["asrTokenEvidence"] = {"audioTokens": 10, "matchedTokens": 9,
      "tokenIntervals": [["a", i*100, i*100+1, int(i < 9)] for i in range(10)]}
    policy = {"sourceFingerprint": "b"*64, "materialInterval": {
      "audioSourceId": "a", "start": 900, "end": 1000, "evidence": "credits"}}
    value = evaluate_readalong_usability(data, policy)
    self.assertEqual(value["readalongUsability"], "USABLE_WITH_GAPS")
    self.assertEqual(value["metrics"]["material_scope_asr_tokens"], 1)
    self.assertEqual(value["metrics"]["unmatched_asr_token_ratio"], 0)
    self.assertAlmostEqual(value["metrics"]["whole_audio_unmatched_asr_token_ratio"], .1)

  def test_forged_token_totals_cannot_pass(self):
    data = report()
    data["asrTokenEvidence"] = {"audioTokens": 1, "matchedTokens": 1,
                               "tokenIntervals": [["a", 0, 1, 0]]}
    self.assertEqual(evaluate_readalong_usability(data)["readalongUsability"], "SCRIPT_ERROR")


if __name__ == "__main__":
  unittest.main()
