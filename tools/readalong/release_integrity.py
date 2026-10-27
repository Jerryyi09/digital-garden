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


def published_tier2_hashes(book_dir: Path):
  manifest_path = book_dir / "readalong" / "readalong.manifest.json"
  manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
  revision = manifest.get("assetRevision")
  source_base = book_dir / ".readalong_revisions" / revision if revision else book_dir / "readalong"
  text_root = source_base / (manifest.get("textRoot") or "text/")
  timeline_path = source_base / (manifest.get("timeline") or "timeline.json")
  return (dir_tree_manifest_hash(text_root), hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
          hashlib.sha256(timeline_path.read_bytes()).hexdigest())


def tier2_book_payload(category, book_name, book_dir):
  return (category, book_name, *published_tier2_hashes(book_dir))
