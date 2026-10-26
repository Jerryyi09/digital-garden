"""Explicit publication of immutable assets; no candidate can attest its own timing."""
import contextlib
import fcntl
import hashlib
import json
import os
import shutil
import uuid
from pathlib import Path

from tools.readalong.acoustic_evaluator import POLICY_VERSION
from tools.readalong.authoritative_validator import audit_book_authoritative

QUALITY_CERT_FILENAME = "quality.json"


class BookPublishLock:
  """Kernel lock survives a lock-file name and is released even after process death."""
  def __init__(self, book_dir):
    self.path = Path(book_dir) / ".readalong_publish.lock"
    self._acquired = False
    self.stream = None

  def __enter__(self):
    self.stream = self.path.open("a+b")
    try:
      fcntl.flock(self.stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
      self._acquired = True
    except BlockingIOError:
      self.stream.close()
    return self

  def __exit__(self, *args):
    if self._acquired:
      fcntl.flock(self.stream, fcntl.LOCK_UN)
      self.stream.close()


def _assets(path):
  path = Path(path)
  return path / "readalong" if (path / "readalong/readalong.manifest.json").is_file() else path


def compute_dir_fingerprint(directory, exclude_names=None):
  """Hash framed paths and contents; symlinks and private ASR work are not assets."""
  directory = Path(directory)
  excluded = exclude_names or {QUALITY_CERT_FILENAME}
  digest = hashlib.sha256()
  if not directory.is_dir():
    raise ValueError("Asset directory missing")
  for path in sorted(directory.rglob("*")):
    relative = path.relative_to(directory)
    if relative.parts[0] == "work":
      continue
    if path.is_symlink():
      raise ValueError("Symlinks are not permitted within candidate assets")
    if path.is_file() and relative.as_posix() not in excluded:
      name = relative.as_posix().encode()
      digest.update(len(name).to_bytes(8, "big"))
      digest.update(name)
      digest.update(path.stat().st_size.to_bytes(8, "big"))
      with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
          digest.update(chunk)
  return digest.hexdigest()


def create_staging_revision(book_dir):
  directory = Path(book_dir) / (".readalong_staging_" + uuid.uuid4().hex)
  directory.mkdir(parents=True, exist_ok=False)
  return directory


def certify_staging_candidate(staging_dir, book_dir=None, exemptions=None, reference_path=None):
  assets = _assets(staging_dir)
  if book_dir is None:
    raise ValueError("Certification requires an explicit physical input book")
  # Reject linked files before even assigning candidate metadata.
  compute_dir_fingerprint(assets)
  if book_dir:
    book = Path(book_dir).resolve()
    resolved = assets.resolve()
    if (resolved.is_relative_to((book / "readalong").resolve())
        or resolved.is_relative_to((book / ".readalong_revisions").resolve())):
      raise ValueError("Certification cannot mutate active or published revisions")
  manifest_file = assets / "readalong.manifest.json"
  manifest = json.loads(manifest_file.read_text())
  if not manifest.get("assetRevision"):
    manifest["assetRevision"] = uuid.uuid4().hex
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
  before = compute_dir_fingerprint(assets)
  report = audit_book_authoritative(assets, book_dir=book_dir, exemptions=exemptions,
                                   reference_path=reference_path)
  after = compute_dir_fingerprint(assets)
  status = report["status"] if before == after else "FAILED"
  cert = {
    "schemaVersion": 2, "policyVersion": POLICY_VERSION,
    "bookId": report["book_id"], "status": status,
    "staging_fingerprint": after,
    "referenceSha256": report.get("acoustic", {}).get("referenceSha256"),
    "errors": report["errors"], "quality_layers": report["quality_layers"],
    "uncovered_intervals": report["uncovered_intervals"],
  }
  # This is a receipt, not an authenticity signature. Publish always recomputes.
  temp = assets / (".quality-" + uuid.uuid4().hex)
  temp.write_text(json.dumps(cert, indent=2, ensure_ascii=False) + "\n")
  os.replace(temp, assets / QUALITY_CERT_FILENAME)
  return cert


def _check(book, assets, reference_path):
  cert_file = assets / QUALITY_CERT_FILENAME
  if not cert_file.is_file():
    return {"success": False, "code": "ERR_NO_QUALITY_CERT"}
  try:
    cert = json.loads(cert_file.read_text())
    if cert.get("status") != "PASS":
      return {"success": False, "code": "ERR_CERT_NOT_PASSED"}
    fp = compute_dir_fingerprint(assets)
    if (cert.get("schemaVersion") != 2 or cert.get("policyVersion") != POLICY_VERSION
        or cert.get("bookId") != book.name or cert.get("staging_fingerprint") != fp):
      return {"success": False, "code": "ERR_TAMPER_DETECTED"}
    report = audit_book_authoritative(assets, book_dir=book, reference_path=reference_path)
    if (report["status"] != "PASS" or not reference_path
        or cert.get("referenceSha256") != report.get("acoustic", {}).get("referenceSha256")):
      return {"success": False, "code": "ERR_REAUDIT_FAILED", "report": report}
    return {"success": True, "fingerprint": fp}
  except (OSError, ValueError, TypeError, AttributeError) as exc:
    return {"success": False, "code": "ERR_CERT_MALFORMED", "msg": str(exc)}


def _switch(book, revision):
  """One same-filesystem rename replaces a symlink; never move active out first."""
  active = book / "readalong"
  if active.exists() and not active.is_symlink():
    raise ValueError("Legacy active directory requires explicit offline migration")
  pointer = book / (".readalong_pointer_" + uuid.uuid4().hex)
  try:
    pointer.symlink_to(os.path.relpath(revision, book), target_is_directory=True)
    os.replace(pointer, active)
  finally:
    if pointer.is_symlink():
      pointer.unlink()


def publish_staging_to_active(book_dir, staging_dir, dry_run=False, reference_path=None):
  book = Path(book_dir).resolve(strict=True)
  assets = _assets(staging_dir).resolve(strict=True)
  revisions = book / ".readalong_revisions"
  with BookPublishLock(book) as lock:
    if not lock._acquired:
      return {"success": False, "code": "ERR_PUBLISH_LOCKED"}
    checked = _check(book, assets, reference_path)
    if not checked["success"]:
      return checked
    active = book / "readalong"
    if active.exists() and not active.is_symlink():
      return {"success": False, "code": "ERR_LEGACY_LAYOUT",
              "msg": "Refusing automatic migration of an existing active directory"}
    if active.is_symlink() and not active.resolve().is_relative_to(revisions.resolve()):
      return {"success": False, "code": "ERR_UNMANAGED_ACTIVE"}
    if dry_run:
      return {"success": True, "dry_run": True}
    previous = str(active.resolve()) if active.is_symlink() else None
    revisions.mkdir(exist_ok=True)
    manifest = json.loads((assets / "readalong.manifest.json").read_text())
    revision_id = manifest.get("assetRevision", "")
    if len(revision_id) != 32 or any(c not in "0123456789abcdef" for c in revision_id):
      return {"success": False, "code": "ERR_REVISION_ID"}
    revision = revisions / revision_id
    if revision.exists():
      return {"success": False, "code": "ERR_REVISION_EXISTS"}
    try:
      shutil.copytree(assets, revision, symlinks=True,
                      ignore=lambda path, names: ["work"] if Path(path) == assets and "work" in names else [])
      if compute_dir_fingerprint(revision) != checked["fingerprint"]:
        raise ValueError("Snapshot fingerprint differs from certified candidate")
      # Audit the copied snapshot under the same lock, not the mutable staging.
      copied = _check(book, revision, reference_path)
      if not copied["success"]:
        return copied
      _switch(book, revision)
      return {"success": True, "active_dir": str(active), "revision_dir": str(revision),
              "backup_dir": previous}
    except (OSError, ValueError) as exc:
      # Leave a failed immutable candidate for inspection; never delete old active.
      return {"success": False, "code": "ERR_SNAPSHOT_CORRUPTED", "msg": str(exc)}


def rollback_to_previous_active(book_dir, backup_dir, reference_path=None):
  book = Path(book_dir).resolve(strict=True)
  revision = Path(backup_dir).resolve(strict=True)
  if not revision.is_relative_to((book / ".readalong_revisions").resolve()):
    return {"success": False, "code": "ERR_UNMANAGED_REVISION"}
  with BookPublishLock(book) as lock:
    if not lock._acquired:
      return {"success": False, "code": "ERR_PUBLISH_LOCKED"}
    result = _check(book, revision, reference_path)
    if not result["success"]:
      return result
    try:
      _switch(book, revision)
      return {"success": True, "active_dir": str(book / "readalong")}
    except (OSError, ValueError) as exc:
      return {"success": False, "code": "ERR_IO_FAILURE", "msg": str(exc)}
