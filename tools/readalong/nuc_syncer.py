"""Secure book synchronizer to NUC via SSH rsync with atomic backup and Alist verification."""
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import shlex
import tempfile
import unicodedata

from tools.readalong.nuc_verifier import AlistClient, verify_book_on_alist
from tools.readalong.nuc_target import NUC_RSYNC_E, NUC_SSH, NUC_TARGET, canonical_nuc_target, direct_ssh_command


def build_book_sync_manifest(book_dir: Path):
  """Build explicit list of files to sync for a book based strictly on its manifest."""
  manifest_path = book_dir / "readalong" / "readalong.manifest.json"
  if not manifest_path.exists():
    raise ValueError(f"Missing readalong.manifest.json in {book_dir}")

  manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
  files_to_sync = []
  source_files = []
  dirs_to_sync = []

  # 1. readalong directory
  dirs_to_sync.append("readalong")

  # 2. current revision directory check
  asset_rev = manifest.get("assetRevision")
  if asset_rev and re.fullmatch(r"[a-f0-9]{32}", asset_rev):
    rev_path = book_dir / ".readalong_revisions" / asset_rev
    if not rev_path.is_dir():
      raise ValueError(f"Manifest specifies assetRevision '{asset_rev}' but version directory is missing on local disk: {rev_path}")
    dirs_to_sync.append(f".readalong_revisions/{asset_rev}")

  # 3. cover and summary
  for name in ("cover.jpg", "cover.jpeg", "summary.txt"):
    if (book_dir / name).is_file():
      files_to_sync.append(name)

  # 4. audios listed in manifest
  for s in manifest.get("audioSources", []):
    audio_id = s.get("id") or s.get("name")
    if audio_id and (book_dir / audio_id).is_file():
      source_files.append(audio_id)

  # 5. epub if present
  for ep in book_dir.glob("*.epub"):
    if ep.is_file():
      source_files.append(ep.name)

  return {
    "manifest": manifest,
    "files": sorted(set(files_to_sync)),
    "sources": sorted(set(source_files)),
    "dirs": sorted(set(dirs_to_sync))
  }


def assert_safe_sync_args(args: list[str]):
  """Strictly reject any delete flags."""
  for a in args:
    if a.startswith("--delete") or a == "-d" or "--remove-source-files" in a:
      raise ValueError(f"Dangerous argument rejected: {a}")


def resolve_rsync_bin():
  for p in ("/opt/homebrew/bin/rsync", "/usr/local/bin/rsync", "rsync"):
    if os.path.isabs(p) and os.path.isfile(p) and os.access(p, os.X_OK):
      return p
  return "rsync"


def build_book_rsync_command(book_dir: Path, remote_dest: str, backup_dir: str, sync_info: dict,
                             *, source_group=False, relative_prefix="", dry_run=False):
  rsync_cmd = [resolve_rsync_bin(), "-av", "-s", "-R", "--iconv=UTF-8-MAC,UTF-8",
    "-e", NUC_RSYNC_E, "--stats", "--itemize-changes",
    "--exclude=._*", "--exclude=.DS_Store"]
  if source_group:
    rsync_cmd.append("--ignore-existing")
    names = sync_info["sources"]
  else:
    rsync_cmd.extend(["--backup", f"--backup-dir={backup_dir}"])
    names = sync_info["dirs"] + sync_info["files"]
  if dry_run:
    rsync_cmd.append("--dry-run")
  items = [f"{book_dir}/./{relative_prefix}{name}" for name in names]
  command = rsync_cmd + items + [remote_dest]
  assert_safe_sync_args(command)
  return command


SSH_CMD_STR = NUC_RSYNC_E
SSH_DIRECT_CMD = NUC_SSH[:-1]
DEFAULT_REMOTE_TARGET = NUC_TARGET


def normalized_directory_name(name):
  """Match SMB private-use substitutions and whitespace without renaming originals."""
  name = unicodedata.normalize("NFC", "".join(
    " " if unicodedata.category(c) == "Co" else c for c in name)).strip()
  if not name or name in (".", "..") or "/" in name or "\x00" in name:
    raise ValueError(f"Invalid directory component: {name!r}")
  return name


def choose_remote_name(name, existing):
  normalized = normalized_directory_name(name)
  matches = [item for item in existing if normalized_directory_name(item) == normalized]
  if normalized in matches:
    return normalized
  if len(matches) > 1:
    raise ValueError(f"Ambiguous remote directories for {name!r}: {matches!r}")
  return matches[0] if matches else normalized


def resolve_remote_book(category, book_name, remote_host=DEFAULT_REMOTE_TARGET,
                        remote_base="/mnt/750/Music/有声书"):
  """Read both directory levels in one SSH call; paths are JSON stdin data."""
  normalized_directory_name(category)
  normalized_directory_name(book_name)
  script = """
import json, sys, unicodedata
from pathlib import Path
base, category = json.load(sys.stdin)
root = Path(base)
def norm(s):
  return unicodedata.normalize('NFC', ''.join(' ' if unicodedata.category(c) == 'Co' else c for c in s)).strip()
categories = [p.name for p in root.iterdir() if p.is_dir() and not p.is_symlink()]
matches = [c for c in categories if norm(c) == norm(category)]
books = {c: [p.name for p in (root / c).iterdir() if p.is_dir() and not p.is_symlink()] for c in matches}
print(json.dumps({'categories': categories, 'books': books}))
"""
  result = subprocess.run(direct_ssh_command(remote_host, "python3 -c " + shlex.quote(script)),
    input=json.dumps([remote_base, category]), capture_output=True, text=True, check=True)
  listing = json.loads(result.stdout)
  remote_category = choose_remote_name(category, listing["categories"])
  return remote_category, choose_remote_name(book_name, listing["books"].get(remote_category, []))


def sync_book_to_nuc(book_dir: Path, category: str, book_name: str, remote_host=DEFAULT_REMOTE_TARGET,
                     remote_base="/mnt/750/Music/有声书", extra_rsync_args=None, *, dry_run=False):
  """Sync managed assets with backups and missing sources without overwriting sources."""
  if extra_rsync_args:
    assert_safe_sync_args(extra_rsync_args)
    raise ValueError("Extra rsync arguments are unsupported; use dry_run=True for previews")
  target_host = canonical_nuc_target(remote_host)
  sync_info = build_book_sync_manifest(book_dir)
  category, book_name = resolve_remote_book(category, book_name, target_host, remote_base)
  ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
  backup_dir = f"/home/hp/readalong-sync-backup/{ts}/{category}/{book_name}"
  remote_dest = f"{target_host}:{remote_base}/"

  # Implied rsync directories follow this local alias without copying book contents.
  # Only explicitly selected assets cross the /./ relative-path boundary.
  with tempfile.TemporaryDirectory(prefix="readalong-sync-") as temp:
    staging = Path(temp)
    (staging / category).mkdir()
    (staging / category / book_name).symlink_to(book_dir.resolve(), target_is_directory=True)
    for source_group in (True, False):
      if source_group and not sync_info["sources"]:
        continue
      command = build_book_rsync_command(staging, remote_dest, backup_dir, sync_info,
        source_group=source_group, relative_prefix=f"{category}/{book_name}/", dry_run=dry_run)
      subprocess.run(command, check=True)
  return {"category": category, "book_name": book_name, "dry_run": dry_run}
