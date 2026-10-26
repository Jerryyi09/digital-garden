#!/usr/bin/env python3
"""
Regression test suite for audit findings (F01-F13) and positive baseline.
Runs authoritative_validator against the generated isolated fixtures.
"""

import sys
import unittest
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.readalong.authoritative_validator import (
    audit_book_authoritative,
    ERROR_SCHEMA_INVALID,
    ERROR_TRACK_INVENTORY_MISMATCH,
    ERROR_TIMESTAMP_OVERLAP,
    ERROR_TIMESTAMP_INVALID,
    ERROR_DOM_REFERENCE_BROKEN,
    ERROR_UNEXPLAINED_GAP,
    ERROR_SECURITY_VIOLATION
)
from tools.readalong.tests.build_audit_fixtures import build_all_fixtures, FIXTURES_DIR
from tools.readalong.tests.build_audit_fixtures import reference_for


class TestAuditRegressions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        build_all_fixtures()

    def test_positive_baseline_passes(self):
        """Positive clean book must achieve PASS with 0 errors."""
        book = FIXTURES_DIR / "positive_valid_book"
        res = audit_book_authoritative(book, reference_path=reference_for(book))
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(len(res["errors"]), 0)
        self.assertTrue(all(res["quality_layers"].values()))

    def test_f01_missing_track_detected(self):
        """F01: Audio source declared in manifest but has 0 mapped segments."""
        res = audit_book_authoritative(FIXTURES_DIR / "f01_missing_track")
        self.assertEqual(res["status"], "FAILED")
        error_codes = [e["code"] for e in res["errors"]]
        self.assertIn(ERROR_TRACK_INVENTORY_MISMATCH, error_codes)

    def test_f02_timestamp_overlap_detected(self):
        """F02: Start time of segment overlaps previous segment in same track."""
        res = audit_book_authoritative(FIXTURES_DIR / "f02_timestamp_overlap")
        self.assertEqual(res["status"], "FAILED")
        error_codes = [e["code"] for e in res["errors"]]
        self.assertIn(ERROR_TIMESTAMP_OVERLAP, error_codes)

    def test_f02_broken_fragment_detected(self):
        """F02: Fragment ID does not exist in target HTML document."""
        res = audit_book_authoritative(FIXTURES_DIR / "f02_broken_fragment")
        self.assertEqual(res["status"], "FAILED")
        error_codes = [e["code"] for e in res["errors"]]
        self.assertIn(ERROR_DOM_REFERENCE_BROKEN, error_codes)

    def test_f02_missing_html_file_detected(self):
        """F02: Target HTML document file does not exist on disk."""
        res = audit_book_authoritative(FIXTURES_DIR / "f02_missing_html_file")
        self.assertEqual(res["status"], "FAILED")
        error_codes = [e["code"] for e in res["errors"]]
        self.assertIn(ERROR_DOM_REFERENCE_BROKEN, error_codes)

    def test_f02_negative_timestamp_detected(self):
        """F02: Non-numeric, negative, or infinite timestamps."""
        res = audit_book_authoritative(FIXTURES_DIR / "f02_invalid_nan_time")
        self.assertEqual(res["status"], "FAILED")
        error_codes = [e["code"] for e in res["errors"]]
        self.assertIn(ERROR_TIMESTAMP_INVALID, error_codes)

    def test_f03_severe_internal_gap_detected(self):
        """F03: Internal unexplained void gap > 20s must fail gate."""
        res = audit_book_authoritative(FIXTURES_DIR / "f03_severe_internal_gap")
        self.assertEqual(res["status"], "FAILED")
        error_codes = [e["code"] for e in res["errors"]]
        self.assertIn(ERROR_UNEXPLAINED_GAP, error_codes)

    def test_f07_unregistered_physical_audio_detected(self):
        """F07: Physical audio exists on disk but was silently omitted from manifest."""
        res = audit_book_authoritative(FIXTURES_DIR / "f07_unregistered_audio_on_disk")
        self.assertEqual(res["status"], "FAILED")
        error_codes = [e["code"] for e in res["errors"]]
        self.assertIn(ERROR_TRACK_INVENTORY_MISMATCH, error_codes)

    def test_f12_path_traversal_blocked(self):
        """F12: Malicious ../ path traversal in document path must be rejected."""
        res = audit_book_authoritative(FIXTURES_DIR / "f12_path_traversal")
        self.assertEqual(res["status"], "FAILED")
        error_codes = [e["code"] for e in res["errors"]]
        self.assertIn(ERROR_SECURITY_VIOLATION, error_codes)


if __name__ == "__main__":
    unittest.main()
