"""Unit tests for nuc_syncer safety rules and manifest resource assembly."""
import json
from pathlib import Path
import tempfile
import unicodedata
import unittest

from tools.readalong.nuc_syncer import assert_safe_sync_args, build_book_rsync_command, build_book_sync_manifest
from tools.readalong.nuc_target import NUC_TARGET, NUC_SSH, direct_ssh_command


class NucSyncerSafetyTests(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.root = Path(self.temp.name)

  def test_rejects_delete_arguments(self):
    dangerous = ["--delete", "--delete-after", "--delete-during", "--delete-excluded", "--remove-source-files", "-d"]
    for arg in dangerous:
      with self.subTest(arg=arg):
        with self.assertRaises(ValueError) as ctx:
          assert_safe_sync_args([arg])
        self.assertIn("Dangerous argument rejected", str(ctx.exception))

  def test_direct_nuc_rsync_command_is_unicode_safe_and_never_deletes(self):
    cmd = build_book_rsync_command(Path("/tmp/book"), f"{NUC_TARGET}:/mnt/library/Cat/Book/",
      "/tmp/backup", {"dirs": ["readalong"], "files": ["audio.mp3"]})
    self.assertIn("-s", cmd)
    self.assertIn("--iconv=UTF-8-MAC,UTF-8", cmd)
    self.assertIn("-F /dev/null", cmd[cmd.index("-e") + 1])
    self.assertIn(f"{NUC_TARGET}:/mnt/library/Cat/Book/", cmd)
    self.assertFalse(any(arg.startswith("--delete") or arg == "-d" for arg in cmd))

  def test_shared_connection_never_uses_alias_proxy_or_router(self):
    cmd = direct_ssh_command("hp", "true")
    self.assertEqual(cmd[cmd.index("-p") + 1], "2222")
    self.assertEqual(cmd[-2], NUC_TARGET)
    joined = " ".join(cmd + NUC_SSH)
    for forbidden in ("ProxyJump", "ProxyCommand", "10.0.0.1", "hp:"):
      self.assertNotIn(forbidden, joined)

  def test_shared_connection_rejects_non_nuc_hosts(self):
    with self.assertRaises(ValueError):
      direct_ssh_command("user@router.example", "true")

  def test_rejects_sync_when_asset_revision_specified_but_dir_missing(self):
    book_dir = self.root / "BookWithMissingRev"
    book_dir.mkdir()
    ra_dir = book_dir / "readalong"
    ra_dir.mkdir()
    rev_id = "f" * 32
    manifest = {
      "schemaVersion": 1,
      "bookId": "BookWithMissingRev",
      "assetRevision": rev_id,
      "audioSources": []
    }
    (ra_dir / "readalong.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    # Do NOT create .readalong_revisions/ffff... directory
    with self.assertRaises(ValueError) as ctx:
      build_book_sync_manifest(book_dir)
    self.assertIn("version directory is missing on local disk", str(ctx.exception))

  def test_builds_sync_manifest_with_spaces_and_nfd(self):
    # Book with spaces in name and NFD in category
    cat_nfd = unicodedata.normalize("NFD", "文学作品")
    book_dir = self.root / cat_nfd / "A Book With Spaces"
    book_dir.mkdir(parents=True)

    # Manifest specifying audio
    ra_dir = book_dir / "readalong"
    ra_dir.mkdir()
    rev_id = "1" * 32
    manifest = {
      "schemaVersion": 1,
      "bookId": "A Book With Spaces",
      "assetRevision": rev_id,
      "audioSources": [
        {"id": "Track 01 - Intro.mp3", "name": "Track 01 - Intro.mp3"},
        {"id": "Track 02 - Main.m4b", "name": "Track 02 - Main.m4b"}
      ]
    }
    (ra_dir / "readalong.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    # Revision directory
    rev_dir = book_dir / ".readalong_revisions" / rev_id
    rev_dir.mkdir(parents=True)
    (rev_dir / "timeline.json").write_text("[]")

    # Historical revision directory that should NOT be synced
    old_rev_dir = book_dir / ".readalong_revisions" / ("0" * 32)
    old_rev_dir.mkdir(parents=True)

    # Physical files
    (book_dir / "Track 01 - Intro.mp3").write_bytes(b"audio1")
    (book_dir / "Track 02 - Main.m4b").write_bytes(b"audio2")
    # Unlisted extra audio that must NOT be synced
    (book_dir / "Unlisted.mp3").write_bytes(b"unlisted")
    (book_dir / "cover.jpg").write_bytes(b"cover")
    (book_dir / "summary.txt").write_text("summary", encoding="utf-8")
    (book_dir / "book.epub").write_bytes(b"epub")

    info = build_book_sync_manifest(book_dir)
    # Check that dirs only include current revision
    self.assertIn("readalong", info["dirs"])
    self.assertIn(f".readalong_revisions/{rev_id}", info["dirs"])
    self.assertNotIn(f".readalong_revisions/{'0'*32}", info["dirs"])

    # Check that files include audited audio, cover, summary, epub
    self.assertIn("Track 01 - Intro.mp3", info["files"])
    self.assertIn("Track 02 - Main.m4b", info["files"])
    self.assertIn("cover.jpg", info["files"])
    self.assertIn("summary.txt", info["files"])
    self.assertIn("book.epub", info["files"])
    self.assertNotIn("Unlisted.mp3", info["files"])


if __name__ == "__main__":
  unittest.main()
