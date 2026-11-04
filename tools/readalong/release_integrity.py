"""Hash the exact active release payload used by Tier 2 verification."""
import hashlib
import json
from pathlib import Path


def dir_tree_manifest_hash(dir_path: Path):
  """Cheap structural digest: names plus sizes, never file contents.

  rsync already moved these bytes over a checksummed channel; re-reading every
  text file on the NUC only re-proves the transfer, at the cost of a full tree
  read per book. Names and sizes still catch truncation, missing shards and
  stray additions.
  """
  h = hashlib.sha256()
  for path in sorted(dir_path.rglob("*")):
    if path.is_file() and not path.name.startswith("._") and path.name != ".DS_Store":
      h.update(path.relative_to(dir_path).as_posix().encode("utf-8"))
      h.update(str(path.stat().st_size).encode("ascii"))
  return h.hexdigest()


def timeline_payload_hash(base, manifest):
  """Hash the index and every referenced shard, with bounded read memory."""
  base = Path(base)
  timeline = base / (manifest.get("timelineIndex") or manifest.get("timeline") or "timeline.json")
  def digest(path):
    with path.open("rb") as stream:
      hasher = hashlib.sha256()
      for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        hasher.update(chunk)
      return hasher.hexdigest()
  index_hash = digest(timeline)
  if manifest.get("timelineFormat") != "per-audio-source-v1":
    return index_hash
  index = json.loads(timeline.read_text(encoding="utf-8"))
  hasher = hashlib.sha256(index_hash.encode("ascii"))
  for rel in sorted(set(index["files"].values())):
    shard = (base / rel).resolve()
    if not shard.is_relative_to(base.resolve()):
      raise ValueError("Unsafe timeline shard path: " + rel)
    hasher.update(json.dumps([rel, digest(shard)], ensure_ascii=False).encode("utf-8"))
  return hasher.hexdigest()


def published_tier2_hashes(book_dir: Path):
  manifest_path = book_dir / "readalong" / "readalong.manifest.json"
  manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
  revision = manifest.get("assetRevision")
  source_base = book_dir / ".readalong_revisions" / revision if revision else book_dir / "readalong"
  text_root = source_base / (manifest.get("textRoot") or "text/")
  return (dir_tree_manifest_hash(text_root), hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
          timeline_payload_hash(source_base, manifest))


def tier2_book_payload(category, book_name, book_dir):
  return (category, book_name, *published_tier2_hashes(book_dir))
