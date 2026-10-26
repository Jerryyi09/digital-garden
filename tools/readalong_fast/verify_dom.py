"""Recheck every recorded duplicate-ID/spine failure without running ASR."""
import argparse
from collections import Counter
import json
from pathlib import Path

from bs4 import BeautifulSoup
from tools.readalong.authoritative_validator import DOMFragmentExtractor
from tools.readalong.batch_candidate_remapper import atomic_json
from tools.readalong.universal_stream_aligner import get_spine_htmls
from tools.readalong_fast.matcher import prepare_paragraphs
from tools.readalong_fast.pipeline import file_hash, safe_path, stat_key
from tools.readalong_fast.resume import fast_identity


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--first-run", type=Path, required=True)
  parser.add_argument("--output", type=Path, required=True)
  args = parser.parse_args()
  if args.output.exists():
    raise ValueError("Use a new evidence directory")
  inv = json.loads((args.first_run/"inventory.json").read_text())
  ledger = json.loads((args.first_run/"results.json").read_text())
  if args.output.resolve().is_relative_to(args.first_run.resolve()) or any(
      args.output.resolve().is_relative_to(Path(u["book_dir"]).resolve()) for u in inv["units"]):
    raise ValueError("Evidence must stay outside prior runs and books")
  summary = {"codeSha256": fast_identity(), "published": False, "newAsrPerformed": False, "records": []}
  for unit in inv["units"]:
    row = ledger["records"][unit["unit_id"]]
    if not any(e in row.get("error", "") for e in ("Duplicate original DOM IDs:", "Duplicate spine document")):
      continue
    book = Path(unit["book_dir"]).resolve(strict=True)
    epub = safe_path(book, unit["epubs"][0]["rel_to_book"])
    before = stat_key(epub)
    if file_hash(epub) != unit["epubs"][0]["sha256"]:
      raise RuntimeError("SOURCE_CHANGED")
    text_root = Path(row["candidatePath"])/"text"
    spine = get_spine_htmls(epub)
    snapshots = {name: stat_key(safe_path(text_root, name)) for name in set(spine)}
    original_text = {name: BeautifulSoup(safe_path(text_root, name).read_text(encoding="utf-8"), "html.parser") for name in set(spine)}
    diagnostics = []
    docs, paras, words = prepare_paragraphs(text_root, spine, diagnostics)
    for name, soup in docs.items():
      source = original_text[name]
      if (source.body or source).get_text() != (soup.body or soup).get_text():
        raise ValueError(f"Visible text changed: {unit['unit_id']} {name}")
      ids = [n["id"] for n in soup.find_all(id=True)]
      if len(ids) != len(set(ids)):
        raise ValueError("Candidate still has duplicate IDs")
    parsed = {}
    for name, soup in docs.items():
      parser = DOMFragmentExtractor()
      parser.feed(str(soup))
      parser.close()
      parsed["text/"+name] = parser.id_to_text
    if any(parsed[p["document"]].get(p["fragment"]) != p["text"] for p in paras):
      raise ValueError("Physical paragraph target/text mismatch")
    if stat_key(epub) != before or any(stat_key(safe_path(text_root, n)) != state for n, state in snapshots.items()):
      raise RuntimeError("SOURCE_CHANGED: verification input changed")
    summary["records"].append({"unitId": unit["unit_id"], "physicalDocuments": len(docs),
      "spineOccurrences": len(spine), "paragraphOccurrences": len(paras), "tokens": len(words),
      "textPreserved": True, "uniqueIds": True, "referencesValid": True,
      "sourceUnchanged": True, "diagnosticCounts": dict(Counter(d["reason"] for d in diagnostics)),
      "diagnostics": diagnostics})
  atomic_json(args.output/"dom-verification.json", summary)
  print(json.dumps([{k: v for k, v in r.items() if k != "diagnostics"} for r in summary["records"]], ensure_ascii=False, indent=2))


if __name__ == "__main__":
  main()
