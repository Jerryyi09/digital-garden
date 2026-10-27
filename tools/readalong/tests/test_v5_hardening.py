import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.readalong.nuc_target import NUC_TARGET, direct_ssh_command
from tools.readalong.release_integrity import published_tier2_hashes, tier2_book_payload
from tools.readalong.tier_verifier import tier2_remote_batch_check
from tools.readalong_fast.v5_batch_runner import has_audio_only_receipt, tier3_batch_sample


class V5HardeningTests(unittest.TestCase):
  def test_audio_only_receipt_is_respected(self):
    with tempfile.TemporaryDirectory() as tmp:
      book = Path(tmp)
      active = book / "readalong"
      active.mkdir()
      (active / "readalong.manifest.json").write_text(json.dumps({
        "assetRevision": "a" * 32, "readalongEnabled": False,
        "practicalRelease": {"decision": "AUDIO_ONLY"}
      }), encoding="utf-8")
      self.assertTrue(has_audio_only_receipt(book))

  def test_tier2_hashes_follow_published_revision(self):
    with tempfile.TemporaryDirectory() as tmp:
      book = Path(tmp)
      (book / "readalong/text").mkdir(parents=True)
      (book / "readalong/text/chapter.html").write_text("stale", encoding="utf-8")
      revision = "b" * 32
      rev = book / ".readalong_revisions" / revision
      (rev / "text").mkdir(parents=True)
      (rev / "text/chapter.html").write_text("published", encoding="utf-8")
      (rev / "timeline.json").write_text("[]", encoding="utf-8")
      manifest_path = book / "readalong/readalong.manifest.json"
      manifest_path.write_text(json.dumps({"assetRevision": revision, "timeline": "timeline.json",
        "textRoot": "text/"}), encoding="utf-8")
      hashes = published_tier2_hashes(book)
      self.assertEqual(hashes, tier2_book_payload("Cat", "Book", book)[2:])
      self.assertNotEqual(hashes[0], "")

  def test_tier2_uses_canonical_direct_target_and_five_field_payload(self):
    completed = type("Completed", (), {"returncode": 0, "stdout": "TIER2_OK", "stderr": ""})()
    with patch("tools.readalong.tier_verifier.subprocess.run", return_value=completed) as run:
      ok, errors = tier2_remote_batch_check("hp", [("Cat", "Book", "x" * 64, "y" * 64, "z" * 64)])
    self.assertTrue(ok, errors)
    cmd = run.call_args.args[0]
    self.assertEqual(cmd[cmd.index("-p") + 1], "2222")
    self.assertIn(NUC_TARGET, cmd)
    joined = " ".join(cmd)
    for forbidden in ("ProxyJump", "ProxyCommand", "10.0.0.1", "hp:"):
      self.assertNotIn(forbidden, joined)

  def test_tier2_text_digest_tracks_names_and_sizes(self):
    # The digest is deliberately structural: rsync already moved the bytes, so
    # re-reading every text file on the NUC only re-proves the transfer.
    from tools.readalong.release_integrity import dir_tree_manifest_hash
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      (root / "a.html").write_text("12345", encoding="utf-8")
      (root / "sub").mkdir()
      (root / "sub/b.html").write_text("abc", encoding="utf-8")
      baseline = dir_tree_manifest_hash(root)

      (root / "sub/c.html").write_text("x", encoding="utf-8")
      self.assertNotEqual(dir_tree_manifest_hash(root), baseline, "an added file must change the digest")
      (root / "sub/c.html").unlink()

      (root / "a.html").write_text("123456", encoding="utf-8")
      self.assertNotEqual(dir_tree_manifest_hash(root), baseline, "a resized file must change the digest")
      (root / "a.html").write_text("12345", encoding="utf-8")
      self.assertEqual(dir_tree_manifest_hash(root), baseline, "restoring content and size must restore the digest")

  def test_tier2_remote_digest_matches_the_local_algorithm(self):
    # A drift between these two implementations would fail every book, so pin
    # the exact byte sequence the remote script is expected to produce.
    import hashlib
    from tools.readalong.release_integrity import dir_tree_manifest_hash
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      (root / "sub").mkdir()
      (root / "sub/ch.html").write_text("hello", encoding="utf-8")
      (root / "top.html").write_text("hi", encoding="utf-8")
      expected = hashlib.sha256()
      for rel, size in (("sub/ch.html", 5), ("top.html", 2)):
        expected.update(rel.encode("utf-8"))
        expected.update(str(size).encode("ascii"))
      self.assertEqual(dir_tree_manifest_hash(root), expected.hexdigest())

  def test_tier3_empty_batch_is_a_successful_skip(self):
    with patch("tools.readalong_fast.v5_batch_runner.tier3_alist_sample_check") as sample:
      self.assertEqual(tier3_batch_sample([]), (True, "SKIPPED_NO_SYNC"))
      sample.assert_not_called()

  def test_every_ssh_call_uses_shared_builder(self):
    cmd = direct_ssh_command("hp", "true")
    self.assertEqual(cmd[cmd.index("-F") + 1], "/dev/null")
    self.assertEqual(cmd[cmd.index("-p") + 1], "2222")
    self.assertEqual(cmd[-2], NUC_TARGET)


if __name__ == "__main__":
  unittest.main()
