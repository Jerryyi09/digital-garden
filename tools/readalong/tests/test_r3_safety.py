"""R3 counterexamples and real positive publication paths, using synthetic audio."""
import ast
import hashlib
import json
import os
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from tools.readalong.acoustic_evaluator import evaluate_acoustic_accuracy
from tools.readalong.authoritative_validator import audit_book_authoritative, DOMFragmentExtractor
from tools.readalong.controlled_publisher import (
  BookPublishLock, certify_staging_candidate, publish_staging_to_active,
  rollback_to_previous_active, compute_dir_fingerprint,
)
from tools.readalong.input_inventory import safe_extract_epub
from tools.readalong.tests.build_audit_fixtures import make_clean_book, reference_for


class SafetyTests(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory(prefix="readalong-r3-test-")
    self.root = Path(self.temp.name)
    self.book = make_clean_book(self.root / "book")
    self.assets = self.book / "readalong"
    self.ref = reference_for(self.book)
    self.mf = self.assets / "readalong.manifest.json"

  def tearDown(self):
    self.temp.cleanup()

  def alter_manifest(self, mutate):
    value = json.loads(self.mf.read_text())
    mutate(value)
    self.mf.write_text(json.dumps(value))

  def stage(self):
    path = self.root / "staging"
    shutil.copytree(self.assets, path)
    return path

  def test_self_written_metrics_cannot_be_certified(self):
    self.alter_manifest(lambda m: m.update(timing={"status": "TIMING_VERIFIED", "metrics": {
      "max_error_seconds": 0, "coverage_ratio": 1, "evaluated_segments": 2}}))
    self.assertEqual(audit_book_authoritative(self.book)["status"], "NEEDS_REVIEW")
    stage = self.stage()
    cert = certify_staging_candidate(stage, book_dir=self.book)
    self.assertNotEqual(cert["status"], "PASS")
    self.assertFalse(publish_staging_to_active(self.book, stage, dry_run=True)["success"])

  def test_explicit_complete_reference_is_positive(self):
    self.assertEqual(audit_book_authoritative(self.book, reference_path=self.ref)["status"], "PASS")

  def test_manifest_cannot_auto_select_an_external_reference(self):
    self.alter_manifest(lambda m: m.update(referencePath=str(self.ref),
                                         timing={"reference": str(self.ref), "status": "TIMING_VERIFIED"}))
    self.assertEqual(audit_book_authoritative(self.book)["status"], "NEEDS_REVIEW")

  def test_certification_rejects_active_and_linked_manifests_before_writing(self):
    before = self.mf.read_bytes()
    with self.assertRaises(ValueError):
      certify_staging_candidate(self.assets, book_dir=self.book)
    stage = self.root / "linked"
    stage.mkdir()
    (stage / "readalong.manifest.json").symlink_to(self.mf)
    with self.assertRaises(ValueError):
      certify_staging_candidate(stage, book_dir=self.book)
    self.assertEqual(self.mf.read_bytes(), before)

  def test_nonnumeric_and_overlapping_timeline_never_pass(self):
    timeline = self.assets / "timeline.json"
    original = json.loads(timeline.read_text())
    for value in (float("nan"), float("inf"), True, "2", None):
      rows = json.loads(json.dumps(original))
      rows[0]["start"] = value
      timeline.write_text(json.dumps(rows))
      self.assertEqual(audit_book_authoritative(self.book)["status"], "FAILED")

  def test_generation_output_cannot_be_a_nonempty_candidate_or_revision(self):
    from tools.readalong.candidate_safety import require_candidate_output
    stage = self.stage()
    with self.assertRaises(ValueError):
      require_candidate_output(self.book, stage)
    with self.assertRaises(ValueError):
      require_candidate_output(self.book, self.book / ".readalong_revisions/new")

  def test_changed_timeline_invalidates_reference(self):
    path = self.assets / "timeline.json"
    value = json.loads(path.read_text())
    value[0]["start"] += .01
    path.write_text(json.dumps(value))
    self.assertNotEqual(audit_book_authoritative(self.book, reference_path=self.ref)["status"], "PASS")

  def test_candidate_cannot_choose_reference(self):
    local = self.assets / "reference.json"
    shutil.copyfile(self.ref, local)
    self.assertNotEqual(audit_book_authoritative(self.book, reference_path=local)["status"], "PASS")

  def test_explicit_reference_not_just_approval_strings(self):
    value = json.loads(self.ref.read_text())
    value["audioSha256"] = {"track_01.mp3": "0" * 64}
    self.ref.write_text(json.dumps(value))
    self.assertNotEqual(audit_book_authoritative(self.book, reference_path=self.ref)["status"], "PASS")

  def test_undecodable_audio_even_with_matching_hash_is_rejected(self):
    audio = self.book / "track_01.mp3"
    audio.write_bytes(b"not audio")
    self.alter_manifest(lambda m: m["audioSources"][0].update(sha256=hashlib.sha256(audio.read_bytes()).hexdigest()))
    report = audit_book_authoritative(self.book)
    self.assertEqual(report["status"], "FAILED")
    self.assertTrue(any("probe failed" in e["msg"] for e in report["errors"]))

  def test_missing_placeholder_and_false_hashes_are_not_test_backdoors(self):
    for digest in (None, "placeholder", "", "0" * 64):
      self.alter_manifest(lambda m: m["audioSources"][0].update(sha256=digest))
      self.assertEqual(audit_book_authoritative(self.book)["status"], "FAILED")

  def test_invalid_numeric_schema_returns_report_not_exception(self):
    for duration in (0, -1, float("nan"), float("inf"), True, "16"):
      self.alter_manifest(lambda m: m["audioSources"][0].update(duration=duration))
      self.assertEqual(audit_book_authoritative(self.book)["status"], "FAILED")

  def test_eighty_percent_is_not_complete_scope(self):
    timeline = [{"fragment": f"s{i}", "start": i, "end": i+1} for i in range(100)]
    refs = {f"s{i}": {"start": i, "end": i+1} for i in range(80)}
    self.assertEqual(evaluate_acoustic_accuracy(timeline, refs)["status"], "COVERAGE_INSUFFICIENT")

  def test_nan_reference_is_rejected(self):
    result = evaluate_acoustic_accuracy([{"fragment": "a", "start": 0, "end": 1}],
                                       {"a": {"start": float("nan"), "end": 1}})
    self.assertFalse(result["passed"])

  def test_void_and_nested_elements_preserve_text(self):
    for html, expected in [('<p id="s">Hello<br>world</p>', "Hello world"),
                           ('<p id="s"><span id="drop">H</span>ello <em>world</em>.</p>', "Hello world.")]:
      parser = DOMFragmentExtractor()
      parser.feed(html)
      parser.close()
      self.assertEqual(parser.id_to_text["s"], expected)

  def test_same_words_different_order_is_not_text_equivalence(self):
    html = self.assets / "text/chapter1.html"
    html.write_text(html.read_text().replace("First sentence in text.", "text in sentence First."))
    self.assertEqual(audit_book_authoritative(self.book)["status"], "FAILED")

  def test_zip_sibling_prefix_traversal_is_rejected_before_any_write(self):
    archive = self.root / "bad.epub"
    with zipfile.ZipFile(archive, "w") as z:
      z.writestr("okay.txt", "normal")
      z.writestr("../outside/probe.txt", "escaped")
    with self.assertRaises(ValueError):
      safe_extract_epub(archive, self.root / "out")
    self.assertFalse((self.root / "outside").exists())
    self.assertFalse((self.root / "out/okay.txt").exists())

  def test_zip_compression_budget_and_symlink_rejected(self):
    archive = self.root / "bad.epub"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
      z.writestr("huge", b"0" * (3 * 1024 * 1024))
    with self.assertRaises(ValueError):
      safe_extract_epub(archive, self.root / "out")
    with zipfile.ZipFile(archive, "w") as z:
      info = zipfile.ZipInfo("link")
      info.external_attr = 0o120777 << 16
      z.writestr(info, "../outside")
    with self.assertRaises(ValueError):
      safe_extract_epub(archive, self.root / "out")

  def test_existing_active_directory_never_automatically_migrates(self):
    stage = self.stage()
    certify_staging_candidate(stage, book_dir=self.book, reference_path=self.ref)
    before = compute_dir_fingerprint(self.assets)
    result = publish_staging_to_active(self.book, stage, reference_path=self.ref)
    self.assertEqual(result["code"], "ERR_LEGACY_LAYOUT")
    self.assertEqual(compute_dir_fingerprint(self.assets), before)

  def test_successful_first_publish_and_revision_pointer(self):
    stage = self.stage()
    certify_staging_candidate(stage, book_dir=self.book, reference_path=self.ref)
    # This is test-only removal of generated fixture assets, not migration code.
    shutil.rmtree(self.assets)
    result = publish_staging_to_active(self.book, stage, reference_path=self.ref)
    self.assertTrue(result["success"], result)
    self.assertTrue(self.assets.is_symlink())
    self.assertTrue((self.assets / "timeline.json").is_file())

  def test_copy_failure_never_removes_active(self):
    stage = self.stage()
    certify_staging_candidate(stage, book_dir=self.book, reference_path=self.ref)
    revisions = self.book / ".readalong_revisions"
    revisions.mkdir()
    old = revisions / "old"
    shutil.move(self.assets, old)
    self.assets.symlink_to(old)
    with patch("tools.readalong.controlled_publisher.shutil.copytree", side_effect=OSError("disk full")):
      result = publish_staging_to_active(self.book, stage, reference_path=self.ref)
    self.assertFalse(result["success"])
    self.assertEqual(self.assets.resolve(), old.resolve())
    self.assertTrue((self.assets / "timeline.json").exists())

  def test_lock_is_exclusive_and_stale_filename_does_not_deadlock(self):
    with BookPublishLock(self.book) as first:
      with BookPublishLock(self.book) as second:
        self.assertTrue(first._acquired)
        self.assertFalse(second._acquired)
    with BookPublishLock(self.book) as third:
      self.assertTrue(third._acquired)

  def test_snapshot_tampering_refused(self):
    stage = self.stage()
    certify_staging_candidate(stage, book_dir=self.book, reference_path=self.ref)
    (stage / "text/chapter1.html").write_text("tampered")
    self.assertFalse(publish_staging_to_active(self.book, stage, reference_path=self.ref)["success"])

  def test_generation_and_legacy_install_cannot_write_active(self):
    from tools.readalong.candidate_safety import require_candidate_output
    from tools.readalong.installer import execute_installation
    with self.assertRaises(ValueError):
      require_candidate_output(self.book, self.assets)
    with self.assertRaises(RuntimeError):
      execute_installation({"target_dir": str(self.assets)})
