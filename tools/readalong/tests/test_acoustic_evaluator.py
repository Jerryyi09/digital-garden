#!/usr/bin/env python3
"""
Unit tests for RA-08: Acoustic Evaluator & Golden Standard Metrics
"""

import unittest
from tools.readalong.acoustic_evaluator import evaluate_acoustic_accuracy


class TestAcousticEvaluator(unittest.TestCase):

    def test_unverified_when_reference_missing(self):
        timeline = [{"fragment": "p1", "start": 1.0, "end": 4.0}]
        res = evaluate_acoustic_accuracy(timeline, reference_data=None)
        self.assertEqual(res["status"], "TIMING_UNVERIFIED")
        self.assertIsNone(res["metrics"])

    def test_verified_when_within_tolerances(self):
        timeline = [
            {"fragment": "p1", "start": 1.05, "end": 4.10},
            {"fragment": "p2", "start": 4.25, "end": 8.02}
        ]
        ref = {
            "p1": {"start": 1.00, "end": 4.00},
            "p2": {"start": 4.20, "end": 8.00}
        }
        res = evaluate_acoustic_accuracy(timeline, reference_data=ref)
        self.assertEqual(res["status"], "TIMING_VERIFIED")
        self.assertTrue(res["passed"])
        self.assertLess(res["metrics"]["mae_seconds"], 0.1)

    def test_accuracy_rejected_when_error_exceeds_threshold(self):
        timeline = [
            {"fragment": "p1", "start": 1.0, "end": 7.0}  # 3 seconds off
        ]
        ref = {
            "p1": {"start": 1.0, "end": 4.0}
        }
        res = evaluate_acoustic_accuracy(timeline, reference_data=ref)
        self.assertEqual(res["status"], "ACCURACY_REJECTED")
        self.assertFalse(res["passed"])
        self.assertGreater(res["metrics"]["max_error_seconds"], 2.0)


if __name__ == "__main__":
    unittest.main()
