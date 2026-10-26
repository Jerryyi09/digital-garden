"""Read-only EPUB marking preflight. No ASR, publication or quality certification."""
import argparse
import hashlib
import json
import os
from pathlib import Path

from bs4 import BeautifulSoup
from tools.readalong.batch_candidate_remapper import atomic_json, code_identity, snapshot
from tools.readalong.candidate_safety import require_candidate_output, source_files
from tools.readalong.config import resolve_nltk_data_path
from tools.readalong.engine.mark_sentence import mark_sentences
from tools.readalong.stream_projection import prepare_documents, uncovered_text_nodes
from tools.readalong.universal_aligner import safe_unzip
from tools.readalong.universal_stream_aligner import get_spine_htmls
from tools.readalong.authoritative_validator import DOMFragmentExtractor, safe_path, canonical_text


def visible_text(raw):
  soup = BeautifulSoup(raw, "lxml")
  root_id = "readalong-verification-root"
  while soup.find(id=root_id):
    root_id += "x"
  parser = DOMFragmentExtractor()
  parser.feed(f'<div id="{root_id}">' + str(soup.body or soup) + '</div>')
  parser.close()
  return canonical_text(parser.id_to_text[root_id])


def verify_book_marking(book, output):
  book, output = Path(book).resolve(strict=True), Path(output).resolve()
  require_candidate_output(book, output)
  if output.is_relative_to(book):
    raise ValueError("Preflight output must be outside the physical book")
  epubs = source_files(book, {".epub"})
  if len(epubs) != 1:
    raise ValueError("Preflight requires an explicit, unambiguous EPUB")
  before = snapshot(book)
  identity = code_identity()
  os.environ["NLTK_DATA"] = str(resolve_nltk_data_path())
  text_root = output / "text"
  safe_unzip(epubs[0], text_root)
  spine = get_spine_htmls(epubs[0])
  if not spine:
    raise ValueError("Empty EPUB reading order")
  originals = {name: safe_path(text_root, name).read_text(encoding="utf-8") for name in spine}
  documents, fragments, tokens = prepare_documents(text_root, spine, mark_sentences)
  rows = []
  for name, doc in documents.items():
    marked = str(doc)
    original_text, marked_text = visible_text(originals[name]), visible_text(marked)
    if original_text != marked_text:
      raise ValueError(f"Visible text changed: {name}")
    parser = DOMFragmentExtractor()
    parser.feed(marked)
    parser.close()
    if parser.duplicate_ids or uncovered_text_nodes(doc):
      raise ValueError(f"Duplicate IDs or uncovered visible text: {name}")
    original_soup = BeautifulSoup(originals[name], "lxml")
    # Every original reference target must remain unique and addressable.
    original_ids = [node["id"] for node in original_soup.find_all(id=True)]
    if len(original_ids) != len(set(original_ids)):
      raise ValueError(f"Duplicate original IDs: {name}")
    missing = set(original_ids) - set(parser.id_to_text)
    if missing:
      raise ValueError(f"Original reference target removed: {name}")
    safe_path(text_root, name).write_text(marked, encoding="utf-8")
    rows.append({"document": name, "uncoveredVisibleTextNodes": 0, "duplicateIds": 0,
                 "originalIdsPreserved": len(original_ids),
                 "visibleTextSha256": hashlib.sha256(marked_text.encode()).hexdigest()})
  after = snapshot(book)
  if before != after or identity != code_identity():
    raise RuntimeError("Source assets or code changed during marking preflight")
  report = {"status": "DOM_PREFLIGHT_PASS", "scope": "epub-spine-marking-only",
            "sourceUnchanged": True, "codeSha256": identity, "sourceSnapshot": before,
            "documents": rows, "documentCount": len(rows), "fragmentCount": len(fragments),
            "tokenCount": len(tokens), "acousticVerified": False,
            "audioAlignmentPerformed": False, "published": False}
  atomic_json(output / "dom-preflight.json", report)
  return report


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("book", type=Path)
  parser.add_argument("output", type=Path, help="New empty private directory outside book")
  args = parser.parse_args()
  report = verify_book_marking(args.book, args.output)
  print(json.dumps({k: report[k] for k in ("status", "documentCount", "fragmentCount", "tokenCount")}))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
