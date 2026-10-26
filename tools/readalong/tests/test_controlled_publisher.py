#!/usr/bin/env python3
"""
Test suite for RA-03: Controlled Staging, Certification & Anti-Tamper Publisher
"""

import json
import shutil
import unittest
from pathlib import Path

from tools.readalong.controlled_publisher import (
    certify_staging_candidate,
    publish_staging_to_active,
    rollback_to_previous_active,
    QUALITY_CERT_FILENAME
)
from tools.readalong.tests.build_audit_fixtures import make_clean_book, FIXTURES_DIR
from tools.readalong.tests.build_audit_fixtures import reference_for


class TestControlledPublisher(unittest.TestCase):

    def setUp(self):
        self.test_root = FIXTURES_DIR / "publisher_test_env"
        if self.test_root.exists():
            shutil.rmtree(self.test_root)
        self.test_root.mkdir(parents=True, exist_ok=True)
        self.book_dir = make_clean_book(self.test_root / "test_book")
        self.reference = reference_for(self.book_dir)

    def test_refuse_publish_without_certificate(self):
        """Must reject publishing if staging lacks quality.json."""
        staging_dir = self.test_root / "staging_no_cert"
        shutil.copytree(self.book_dir / "readalong", staging_dir)
        res = publish_staging_to_active(self.book_dir, staging_dir)
        self.assertFalse(res["success"])
        self.assertEqual(res["code"], "ERR_NO_QUALITY_CERT")

    def test_refuse_publish_if_status_not_pass(self):
        """Must reject publishing if status is FAILED or PARTIAL."""
        staging_dir = self.test_root / "staging_failed_cert"
        shutil.copytree(self.book_dir / "readalong", staging_dir)
        (staging_dir / QUALITY_CERT_FILENAME).write_text(json.dumps({
            "status": "FAILED",
            "errors": [{"code": "ERR_TEST", "msg": "Fail"}]
        }))
        res = publish_staging_to_active(self.book_dir, staging_dir)
        self.assertFalse(res["success"])
        self.assertEqual(res["code"], "ERR_CERT_NOT_PASSED")

    def test_refuse_publish_if_tampered(self):
        """Must reject publishing if files were modified after certification."""
        staging_dir = self.test_root / "staging_tampered"
        shutil.copytree(self.book_dir / "readalong", staging_dir)
        (staging_dir / QUALITY_CERT_FILENAME).write_text(json.dumps({
            "status": "PASS",
            "staging_fingerprint": "fake_fingerprint_hash_12345"
        }))
        res = publish_staging_to_active(self.book_dir, staging_dir)
        self.assertFalse(res["success"])
        self.assertEqual(res["code"], "ERR_TAMPER_DETECTED")

    def test_successful_publish_and_explicit_rollback(self):
        """Valid passing candidate is promoted and previous active is backed up."""
        staging_dir = self.test_root / "staging_valid"
        shutil.copytree(self.book_dir / "readalong", staging_dir)

        # Use legitimate certification pipeline
        cert = certify_staging_candidate(staging_dir, book_dir=self.book_dir, reference_path=self.reference)
        self.assertEqual(cert["status"], "PASS")

        # Explicit fixture-only layout migration; production refuses this automatically.
        revisions = self.book_dir / ".readalong_revisions"
        revisions.mkdir()
        previous = revisions / "initial"
        shutil.move(self.book_dir / "readalong", previous)
        shutil.copyfile(staging_dir / "quality.json", previous / "quality.json")
        shutil.copyfile(staging_dir / "readalong.manifest.json", previous / "readalong.manifest.json")
        (self.book_dir / "readalong").symlink_to(previous, target_is_directory=True)
        res = publish_staging_to_active(self.book_dir, staging_dir, reference_path=self.reference)
        self.assertTrue(res["success"], f"Publish failed: {res.get('msg')}")
        self.assertTrue((self.book_dir / "readalong").exists())
        self.assertIsNotNone(res["backup_dir"])
        self.assertTrue(Path(res["backup_dir"]).exists())

        # Test rollback
        rb_res = rollback_to_previous_active(self.book_dir, Path(res["backup_dir"]), reference_path=self.reference)
        self.assertTrue(rb_res["success"])


if __name__ == "__main__":
    unittest.main()
