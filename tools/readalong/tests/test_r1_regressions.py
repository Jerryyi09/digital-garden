#!/usr/bin/env python3
"""
Regression test suite for Review R1 findings.
Formalizes all 10 adversarial failure cases and mutations identified in R1.
These tests MUST fail until the underlying validation and publishing mechanisms are fixed.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path

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
from tools.readalong.controlled_publisher import (
    certify_staging_candidate,
    publish_staging_to_active
)
from tools.readalong.tests.build_audit_fixtures import make_clean_book


class TestR1Regressions(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="r1_reg_"))

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _setup_book(self):
        book_dir = self.tmp_dir / "book"
        return make_clean_book(book_dir)

    def test_r1_unverified_timing_cannot_pass(self):
        """R1-01: Explicit or unverified acoustic timing (TIMING_UNVERIFIED) must NOT PASS."""
        book = self._setup_book()
        mf_path = book / "readalong/readalong.manifest.json"
        tl_path = book / "readalong/timeline.json"
        mf = json.loads(mf_path.read_text())
        tl = json.loads(tl_path.read_text())

        mf["timing"] = {"status": "TIMING_UNVERIFIED"}
        for s in tl:
            s["timingStatus"] = "TIMING_UNVERIFIED"

        mf_path.write_text(json.dumps(mf))
        tl_path.write_text(json.dumps(tl))

        res = audit_book_authoritative(book)
        self.assertNotEqual(res["status"], "PASS", "Book with TIMING_UNVERIFIED must not achieve PASS")
        self.assertIn("NEEDS_REVIEW", (res["status"], res.get("review_status", "")))

    def test_r1_missing_physical_audio_fails(self):
        """R1-02: Manifest declares audio, but physical file on disk is deleted."""
        book = self._setup_book()
        (book / "track_01.mp3").unlink()

        res = audit_book_authoritative(book)
        self.assertEqual(res["status"], "FAILED")
        error_codes = [e["code"] for e in res["errors"]]
        self.assertIn(ERROR_TRACK_INVENTORY_MISMATCH, error_codes)

    def test_r1_out_of_bounds_timestamp_fails(self):
        """R1-02: Segment end timestamp exceeds declared/measured physical audio duration."""
        book = self._setup_book()
        tl_path = book / "readalong/timeline.json"
        tl = json.loads(tl_path.read_text())
        # track_01.mp3 duration is 60.0s in manifest, set end to 90.0s
        tl[-1]["end"] = 90.0
        tl_path.write_text(json.dumps(tl))

        res = audit_book_authoritative(book)
        self.assertEqual(res["status"], "FAILED")
        error_codes = [e["code"] for e in res["errors"]]
        self.assertIn(ERROR_TIMESTAMP_INVALID, error_codes)

    def test_r1_empty_fragment_fails(self):
        """R1-02: Timeline segment has empty or missing fragment identifier."""
        book = self._setup_book()
        tl_path = book / "readalong/timeline.json"
        tl = json.loads(tl_path.read_text())
        for s in tl:
            s["fragment"] = ""
        tl_path.write_text(json.dumps(tl))

        res = audit_book_authoritative(book)
        self.assertEqual(res["status"], "FAILED")
        error_codes = [e["code"] for e in res["errors"]]
        self.assertIn(ERROR_DOM_REFERENCE_BROKEN, error_codes)

    def test_r1_fragment_only_in_comment_fails(self):
        """R1-02: Fragment ID exists inside HTML comment but not on an actual DOM element."""
        book = self._setup_book()
        html_path = book / "readalong/text/chapter1.html"
        html_path.write_text("<!-- id=\"c01-segment01\" id=\"c01-segment02\" --><p>No such elements.</p>", encoding="utf-8")

        res = audit_book_authoritative(book)
        self.assertEqual(res["status"], "FAILED")
        error_codes = [e["code"] for e in res["errors"]]
        self.assertIn(ERROR_DOM_REFERENCE_BROKEN, error_codes)

    def test_r1_text_mismatch_fails(self):
        """R1-02: Segment text is completely different from the DOM element text."""
        book = self._setup_book()
        tl_path = book / "readalong/timeline.json"
        tl = json.loads(tl_path.read_text())
        for s in tl:
            s["text"] = "Completely different text that does not appear in DOM at all."
        tl_path.write_text(json.dumps(tl))

        res = audit_book_authoritative(book)
        self.assertEqual(res["status"], "FAILED")
        error_codes = [e["code"] for e in res["errors"]]
        self.assertTrue(any("TEXT" in e["code"] or "DOM" in e["code"] for e in res["errors"]))

    def test_r1_large_head_delay_fails(self):
        """R1-02: First segment starts after 100 seconds unexplained gap."""
        book = self._setup_book()
        mf_path = book / "readalong/readalong.manifest.json"
        tl_path = book / "readalong/timeline.json"
        mf = json.loads(mf_path.read_text())
        tl = json.loads(tl_path.read_text())

        mf["audioSources"][0]["duration"] = 200.0
        for s in tl:
            s["start"] += 100.0
            s["end"] += 100.0
        mf_path.write_text(json.dumps(mf))
        tl_path.write_text(json.dumps(tl))

        res = audit_book_authoritative(book)
        self.assertEqual(res["status"], "FAILED")
        error_codes = [e["code"] for e in res["errors"]]
        self.assertIn(ERROR_UNEXPLAINED_GAP, error_codes)

    def test_r1_large_tail_gap_fails(self):
        """R1-02: 60s track only mapped to 15s, leaving 45s tail gap without explanation."""
        book = self._setup_book()
        import wave, hashlib
        audio = book / "track_01.mp3"
        with wave.open(str(audio), "wb") as stream:
            stream.setnchannels(1)
            stream.setsampwidth(2)
            stream.setframerate(8000)
            stream.writeframes(b"\0\0" * 480000)
        mf_path = book / "readalong/readalong.manifest.json"
        mf = json.loads(mf_path.read_text())
        mf["audioSources"][0]["duration"] = 60.0  # Real 45s tail gap, not fabricated metadata.
        mf["audioSources"][0]["sha256"] = hashlib.sha256(audio.read_bytes()).hexdigest()
        mf_path.write_text(json.dumps(mf))
        res = audit_book_authoritative(book)
        self.assertEqual(res["status"], "FAILED")
        error_codes = [e["code"] for e in res["errors"]]
        self.assertIn(ERROR_UNEXPLAINED_GAP, error_codes)

    def test_r1_publisher_rejects_empty_fingerprint(self):
        """R1-03: Publisher must refuse staging if quality.json lacks valid recorded fingerprint."""
        book = self._setup_book()
        stage = self.tmp_dir / "flat_staging"
        shutil.copytree(book / "readalong", stage)
        (stage / "quality.json").write_text(json.dumps({"status": "PASS"}))

        res = publish_staging_to_active(book, stage, dry_run=True)
        self.assertFalse(res.get("success"), "Must reject publish when fingerprint is missing or empty")

    def test_r1_normal_aligner_staging_output_certification(self):
        """R1-04: Normal aligner output directory contract must be certifiable by publisher."""
        book = self._setup_book()
        stage = self.tmp_dir / "staging_contract"
        shutil.copytree(book / "readalong", stage)

        # When stage contains readalong assets directly, certification must recognize either
        # direct stage directory or stage/readalong/ without crashing on schema.
        cert = certify_staging_candidate(stage, book_dir=book)
        # Should not fail on ERR_SCHEMA_INVALID missing readalong folder
        schema_errors = [e for e in cert.get("errors", []) if e.get("code") == ERROR_SCHEMA_INVALID and "readalong/ folder" in e.get("msg", "")]
        self.assertEqual(len(schema_errors), 0, "Certification must handle staging contract properly")


if __name__ == "__main__":
    unittest.main()
