"""Compatibility entrypoint for read-only authoritative audits (no report writes)."""
import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(PROJECT_ROOT))
from tools.readalong.authoritative_validator import audit_book_authoritative, AUDIO_SUFFIXES


def validate_book_readalong(book_dir, verbose=False):
  report = audit_book_authoritative(book_dir)
  errors = [f"[{e['code']}] {e['msg']}" for e in report["errors"]]
  if report["status"] != "PASS" and not errors:
    errors.append(f"[{report['status']}] No complete acceptance evidence")
  return errors


def main():
  parser = argparse.ArgumentParser(description="Read-only library audit")
  parser.add_argument("--root", required=True)
  parser.add_argument("--verbose", action="store_true")
  parser.add_argument("--no-report", action="store_true", help="Compatibility flag; audit never writes reports")
  args = parser.parse_args()
  root = Path(args.root)
  if not root.is_dir():
    print(json.dumps({"status": "FAILED", "reason": "root_not_found"}))
    return 2
  books = {p.parent.parent for p in root.rglob("readalong.manifest.json")
           if p.parent.name == "readalong" and not any(x.startswith(".") for x in p.relative_to(root).parts)}
  for audio in root.rglob("*"):
    if (audio.is_file() and audio.suffix.lower() in AUDIO_SUFFIXES
        and not any(x.startswith(".") or x in {"readalong", "work", "text"} for x in audio.relative_to(root).parts)):
      if not any(audio.is_relative_to(book) for book in books):
        books.add(audio.parent)
  reports = [audit_book_authoritative(book) for book in sorted(books)]
  passed = bool(reports) and all(r["status"] == "PASS" for r in reports)
  print(json.dumps({"status": "PASS" if passed else "FAILED", "books": reports,
                    "reason": None if reports else "no_inputs"}, ensure_ascii=False, indent=2))
  return 0 if passed else 2


if __name__ == "__main__":
  raise SystemExit(main())
