"""Preview or publish only guide assets, without requiring a readalong manifest."""
import argparse
import json
from pathlib import Path

from .nuc_syncer import sync_book_to_nuc
from .nuc_target import nuc_publication_lock


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("book", type=Path, help="Local book directory under category")
  parser.add_argument("--apply", action="store_true", help="Publish after reviewing and approving the overwrite list")
  args = parser.parse_args()
  book = args.book.expanduser().resolve()
  if Path("/Volumes") in book.parents:
    parser.error("Use the local SSD library, not /Volumes")
  with nuc_publication_lock():
    result = sync_book_to_nuc(book, book.parent.name, book.name,
      dry_run=not args.apply, guides_only=True)
  print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
  main()
