"""Batch runner for desktop 心智成长 audiobook library alignment."""

import json
import os
from pathlib import Path
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from tools.readalong.universal_aligner import align_single_book_universal

DESKTOP_ROOT = Path("/Users/jerryyi/Desktop/寒假/心智成长")
OUTPUT_BASE = PROJECT_ROOT / "private" / "readalong-output"


def main():
    dirs = sorted([d for d in DESKTOP_ROOT.iterdir() if d.is_dir() and not d.name.startswith(".")])
    books_with_epub = []

    for d in dirs:
        epubs = [e for e in d.rglob("*.epub") if not e.name.startswith("._")]
        if epubs:
            books_with_epub.append(d)

    print(f"Total directories: {len(dirs)}")
    print(f"Directories with EPUB to align: {len(books_with_epub)}\n")

    results = []
    total_start = time.time()

    for idx, b_dir in enumerate(books_with_epub, start=1):
        book_slug = b_dir.name
        book_out = OUTPUT_BASE / book_slug
        print(f"[{idx}/{len(books_with_epub)}] Processing: {b_dir.name}...")
        start_t = time.time()

        try:
            # Check if already aligned with non-empty timeline
            existing_timeline = b_dir / "readalong" / "timeline.json"
            if existing_timeline.exists() and existing_timeline.stat().st_size > 100:
                print(f"    Already aligned, reading existing metadata...")
                manifest_data = json.load((b_dir / "readalong" / "readalong.manifest.json").open())
                timeline_data = json.load(existing_timeline.open())
                res = {
                    "status": "success",
                    "book_id": manifest_data.get("bookId"),
                    "matched_html": manifest_data.get("alignedDocument", "existing"),
                    "segment_count": len(timeline_data),
                    "cached": True,
                }
            else:
                res = align_single_book_universal(
                    book_dir=b_dir,
                    output_dir=book_out,
                    max_sample_seconds=900.0,
                )
            elapsed = time.time() - start_t
            res["book_name"] = b_dir.name
            res["elapsed_seconds"] = round(elapsed, 2)
            results.append(res)
            print(f"    Result: {res['status']} ({res.get('segment_count', 0)} segments in {elapsed:.1f}s)")
        except Exception as e:
            elapsed = time.time() - start_t
            err_res = {
                "status": "error",
                "book_name": b_dir.name,
                "error": str(e),
                "elapsed_seconds": round(elapsed, 2),
            }
            results.append(err_res)
            print(f"    Error (skipped): {e}")

    summary_file = OUTPUT_BASE / "batch_alignment_summary.json"
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    summary_file.write_text(json.dumps(results, ensure_ascii=False, indent=2))

    successes = sum(1 for r in results if r["status"] == "success")
    errors = sum(1 for r in results if r["status"] == "error")
    skipped = sum(1 for r in results if r["status"] == "skipped")

    print("\n" + "=" * 60)
    print(f"Batch Alignment Completed in {time.time() - total_start:.1f}s")
    print(f"Success: {successes} | Error: {errors} | Skipped: {skipped}")
    print(f"Summary saved to: {summary_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
