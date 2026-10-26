#!/usr/bin/env python3
"""
Formal Regression Tests for R2 Review Counterexamples.
Covers all isolation edge-cases identified in R2:
- R2-01: Fail-closed on missing acoustic evidence / self-declared bypass
- R2-02: Physical audio duration & SHA-256 mismatch detection
- R2-03: DOM nested tree parsing preservation & duplicate DOM ID detection
- R2-04: Acoustic evaluator 200ms strict contract & coverage completeness
"""

import json
import shutil
import tempfile
import unittest
import wave
from pathlib import Path

from tools.readalong.authoritative_validator import audit_book_authoritative, DOMFragmentExtractor
from tools.readalong.controlled_publisher import certify_staging_candidate, publish_staging_to_active
from tools.readalong.acoustic_evaluator import evaluate_acoustic_accuracy


class TestR2Regressions(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_r2_")
        self.book_dir = Path(self.test_dir) / "book"
        self.ra_dir = self.book_dir / "readalong"
        self.ra_dir.mkdir(parents=True)

        # Generate a real valid 10-second 8kHz mono WAV audio file
        self.audio_path = self.book_dir / "a.wav"
        with wave.open(str(self.audio_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(8000)
            wf.writeframes(b"\0\0" * 80000)

        import hashlib
        self.real_audio_sha256 = hashlib.sha256(self.audio_path.read_bytes()).hexdigest()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _write_book(self, manifest, timeline, html):
        (self.ra_dir / "readalong.manifest.json").write_text(json.dumps(manifest, indent=2))
        (self.ra_dir / "timeline.json").write_text(json.dumps(timeline, indent=2))
        (self.ra_dir / "ch.html").write_text(html, encoding="utf-8")

    def test_r2_nested_dom_ids_preserves_outer_sentence(self):
        """R2-03: Nested DOM IDs (e.g. drop cap) must preserve outer element full text."""
        parser = DOMFragmentExtractor()
        parser.feed('<p><span id="s1"><span id="drop">H</span>ello world.</span></p>')
        self.assertIn("s1", parser.id_to_text, "Outer ID s1 was dropped")
        self.assertEqual(parser.id_to_text["s1"].strip(), "Hello world.")
        self.assertEqual(parser.id_to_text["drop"].strip(), "H")

    def test_r2_duplicate_dom_id_fails(self):
        """R2-03: Multiple elements with the same ID must be rejected as ERR_DUPLICATE_DOM_ID."""
        html = '<p id="s1">First paragraph.</p><p id="s1">Duplicate paragraph.</p>'
        manifest = {
            "schemaVersion": 1,
            "audioSources": [{"id": "a.wav", "duration": 10.0, "sha256": self.real_audio_sha256}],
            "timeline": "timeline.json"
        }
        timeline = [{
            "audioSourceId": "a.wav", "start": 0.0, "end": 10.0,
            "document": "ch.html", "fragment": "s1", "text": "First paragraph."
        }]
        self._write_book(manifest, timeline, html)
        report = audit_book_authoritative(self.book_dir)
        self.assertNotEqual(report["status"], "PASS")
        errors = [e["code"] for e in report["errors"]]
        self.assertIn("ERR_DUPLICATE_DOM_ID", errors)

    def test_r2_real_audio_10s_declared_100s_fails(self):
        """R2-02: Manifest claiming 100s for a 10s audio must be caught by physical probe."""
        html = '<p id="s1">Sentence covering audio.</p>'
        manifest = {
            "schemaVersion": 1,
            "audioSources": [{"id": "a.wav", "duration": 100.0, "sha256": self.real_audio_sha256}],
            "timeline": "timeline.json"
        }
        timeline = [{
            "audioSourceId": "a.wav", "start": 0.0, "end": 100.0,
            "document": "ch.html", "fragment": "s1", "text": "Sentence covering audio."
        }]
        self._write_book(manifest, timeline, html)
        report = audit_book_authoritative(self.book_dir)
        self.assertNotEqual(report["status"], "PASS")
        errors = [e["code"] for e in report["errors"]]
        self.assertTrue(
            "ERR_AUDIO_DURATION_MISMATCH" in errors or "ERR_TIMESTAMP_OUT_OF_BOUNDS" in errors,
            f"Expected duration/bound mismatch error, got: {errors}"
        )

    def test_r2_wrong_audio_sha256_fails(self):
        """R2-02: Audio physical SHA-256 mismatch against manifest must be rejected."""
        html = '<p id="s1">Valid sentence.</p>'
        manifest = {
            "schemaVersion": 1,
            "audioSources": [{"id": "a.wav", "duration": 10.0, "sha256": "wrong_sha256_hex_value"}],
            "timeline": "timeline.json"
        }
        timeline = [{
            "audioSourceId": "a.wav", "start": 0.0, "end": 10.0,
            "document": "ch.html", "fragment": "s1", "text": "Valid sentence."
        }]
        self._write_book(manifest, timeline, html)
        report = audit_book_authoritative(self.book_dir)
        self.assertNotEqual(report["status"], "PASS")
        errors = [e["code"] for e in report["errors"]]
        self.assertIn("ERR_AUDIO_SHA256_MISMATCH", errors)

    def test_r2_no_acoustic_evidence_fails_closed(self):
        """R2-01: Candidate with no acoustic proof cannot achieve PASS or timing_verified=true."""
        html = '<p id="s1">Valid sentence.</p>'
        manifest = {
            "schemaVersion": 1,
            "audioSources": [{"id": "a.wav", "duration": 10.0, "sha256": self.real_audio_sha256}],
            "timeline": "timeline.json"
        }
        timeline = [{
            "audioSourceId": "a.wav", "start": 0.0, "end": 10.0,
            "document": "ch.html", "fragment": "s1", "text": "Valid sentence."
        }]
        self._write_book(manifest, timeline, html)
        report = audit_book_authoritative(self.book_dir)
        self.assertNotEqual(report["status"], "PASS")
        self.assertFalse(report["quality_layers"]["timing_verified"])

    def test_r2_self_declared_status_without_proof_fails(self):
        """R2-01: Pure text declaration of TIMING_VERIFIED without attached proof is rejected."""
        html = '<p id="s1">Valid sentence.</p>'
        manifest = {
            "schemaVersion": 1,
            "audioSources": [{"id": "a.wav", "duration": 10.0, "sha256": self.real_audio_sha256}],
            "timeline": "timeline.json",
            "timing": {"status": "TIMING_VERIFIED"}
        }
        timeline = [{
            "audioSourceId": "a.wav", "start": 0.0, "end": 10.0,
            "document": "ch.html", "fragment": "s1", "text": "Valid sentence."
        }]
        self._write_book(manifest, timeline, html)
        report = audit_book_authoritative(self.book_dir)
        self.assertNotEqual(report["status"], "PASS")
        self.assertFalse(report["quality_layers"]["timing_verified"])

    def test_r2_acoustic_300ms_fails_200ms_contract(self):
        """R2-04: Delta of 300ms exceeds strict 200ms contract and must be rejected."""
        timeline = [{"fragment": "s1", "start": 0.3, "end": 1.3}]
        ref = {"s1": {"start": 0.0, "end": 1.0}}
        res = evaluate_acoustic_accuracy(timeline, reference_data=ref)
        self.assertEqual(res["status"], "ACCURACY_REJECTED")
        self.assertFalse(res["passed"])

    def test_r2_partial_reference_coverage_insufficient(self):
        """R2-04: Evaluating 1 of 100 segments cannot grant whole-book timing verification."""
        timeline = [{"fragment": f"s{i}", "start": float(i), "end": float(i + 1)} for i in range(100)]
        ref = {"s0": {"start": 0.0, "end": 1.0}}
        res = evaluate_acoustic_accuracy(timeline, reference_data=ref)
        self.assertNotEqual(res["status"], "TIMING_VERIFIED")
        self.assertEqual(res.get("coverage_status"), "COVERAGE_INSUFFICIENT")


if __name__ == "__main__":
    unittest.main()
