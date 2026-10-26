"""Unit tests for nuc_syncer safety rules and manifest resource assembly."""
import os
import subprocess
from unittest.mock import patch
import json
from pathlib import Path
import tempfile
import unicodedata
import unittest

from tools.readalong.nuc_syncer import (assert_safe_sync_args, build_book_rsync_command,
  build_book_sync_manifest, choose_remote_name, resolve_remote_book, sync_book_to_nuc)
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
    self.assertIn("Track 01 - Intro.mp3", info["sources"])
    self.assertIn("Track 02 - Main.m4b", info["sources"])
    self.assertIn("cover.jpg", info["files"])
    self.assertIn("summary.txt", info["files"])
    self.assertIn("book.epub", info["sources"])
    self.assertNotIn("Unlisted.mp3", info["sources"])

  def test_directory_matching_preserves_existing_names(self):
    for local, existing, expected in [
      (" Siddhartha ", ["Siddhartha"], "Siddhartha"),
      ('Book "$`quote`', ['Book "$`quote`'], 'Book "$`quote`'),
      ("Siddhartha ", ["Siddhartha\uf028"], "Siddhartha\uf028"),
      ("Siddhartha ", ["Siddhartha", "Siddhartha "], "Siddhartha"),
      (" New Book ", [], "New Book"),
      (unicodedata.normalize("NFD", "Café"), ["Café"], "Café"),
    ]:
      with self.subTest(local=local, existing=existing):
        self.assertEqual(choose_remote_name(local, existing), expected)

  def test_ambiguous_and_unsafe_names_fail_closed(self):
    with self.assertRaises(ValueError):
      choose_remote_name("Book", ["Book ", " Book"])
    for name in ("..", "../Book", " "):
      with self.assertRaises(ValueError):
        choose_remote_name(name, [])

  def test_remote_listing_passes_paths_as_stdin_not_shell(self):
    name = 'Book "$`touch nope`'
    with patch("tools.readalong.nuc_syncer.subprocess.run") as run:
      run.return_value.stdout = json.dumps({"categories": ["Cat"], "books": {"Cat": [name]}})
      self.assertEqual(resolve_remote_book("Cat", name), ("Cat", name))
      self.assertEqual(run.call_count, 1)
      args, kwargs = run.call_args
      self.assertNotIn(name, args[0][-1])
      self.assertNotIn("mkdir", args[0][-1])
      self.assertEqual(json.loads(kwargs["input"])[1], "Cat")

  def test_source_group_never_backs_up_or_overwrites(self):
    info = {"sources": ["a.mp3", "b.epub"], "files": ["cover.jpg"], "dirs": ["readalong"]}
    cmd = build_book_rsync_command(self.root, "dest", "backup", info, source_group=True)
    self.assertIn("--ignore-existing", cmd)
    self.assertNotIn("--backup", cmd)
    self.assertFalse(any(x.startswith("--backup-dir") for x in cmd))
    self.assertFalse(any(x.endswith("/cover.jpg") or x.endswith("/readalong") for x in cmd))
    managed = build_book_rsync_command(self.root, "dest", "backup", info)
    self.assertIn("--backup", managed)
    self.assertFalse(any(x.endswith(".mp3") or x.endswith(".epub") for x in managed))

  def test_sync_uses_resolved_path_for_both_groups_and_dry_run(self):
    source = self.root / "Book "
    (source / "readalong").mkdir(parents=True)
    (source / "readalong/readalong.manifest.json").write_text(json.dumps({"audioSources": [{"id": "a.mp3"}]}))
    (source / "a.mp3").write_bytes(b"audio")
    for remote_name in ("Book", "Book\uf028", 'Book "$`quote`'):
      with self.subTest(remote_name=remote_name), patch(
          "tools.readalong.nuc_syncer.resolve_remote_book", return_value=("Cat", remote_name)), patch(
          "tools.readalong.nuc_syncer.subprocess.run") as run:
        sync_book_to_nuc(source, "Cat", source.name, dry_run=True)
        self.assertEqual(run.call_count, 2)
        for call in run.call_args_list:
          command = call.args[0]
          self.assertIn("--dry-run", command)
          self.assertIn("-R", command)
          self.assertTrue(any(f"/./Cat/{remote_name}/" in arg for arg in command))
          self.assertEqual(command[-1], f"{NUC_TARGET}:/mnt/750/Music/有声书/")
          self.assertNotIn("mkdir", " ".join(command))

  def test_real_rsync_alias_and_existing_audio_mtime(self):
    # Exercise the real rsync receiver locally, including implied symlink directories.
    source = self.root / 'Book "$`quote` '
    (source / "readalong").mkdir(parents=True)
    (source / "readalong/readalong.manifest.json").write_text(json.dumps({"audioSources": [{"id": "a.mp3"}]}))
    (source / "a.mp3").write_bytes(b"new audio")
    (source / "book.epub").write_bytes(b"new epub")
    (source / "unlisted.mp3").write_bytes(b"unlisted")
    remote = self.root / "remote"
    name = 'Book "$`quote`'
    target = remote / "Cat" / name
    target.mkdir(parents=True)
    (target / "a.mp3").write_bytes(b"old audio preserved")
    os.utime(target / "a.mp3", (1, 1))
    real_run = subprocess.run
    calls = []
    def local_run(command, **kwargs):
      calls.append(command)
      command = list(command)
      idx = command.index("-e")
      del command[idx:idx + 2]
      command = [c for c in command if not c.startswith("--iconv=")]
      command[-1] = str(remote) + "/"
      return real_run(command, capture_output=True, text=True, **kwargs)
    with patch("tools.readalong.nuc_syncer.resolve_remote_book", return_value=("Cat", name)), patch(
        "tools.readalong.nuc_syncer.subprocess.run", side_effect=local_run):
      result = sync_book_to_nuc(source, "Cat", source.name)
    self.assertEqual(result["book_name"], name)
    self.assertEqual(len(calls), 2)
    self.assertEqual((target / "a.mp3").read_bytes(), b"old audio preserved")
    self.assertEqual((target / "a.mp3").stat().st_mtime, 1)
    self.assertEqual((target / "book.epub").read_bytes(), b"new epub")
    self.assertTrue((target / "readalong/readalong.manifest.json").is_file())
    self.assertFalse((target / "unlisted.mp3").exists())
    self.assertEqual([p.name for p in (remote / "Cat").iterdir()], [name])


if __name__ == "__main__":
  unittest.main()
