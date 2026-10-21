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
    import argparse
    parser = argparse.ArgumentParser(description="Batch audiobook aligner for desktop collections")
    parser.add_argument("--root", default=str(DESKTOP_ROOT), help="Root directory containing book subdirectories")
    args = parser.parse_args()

    root_dir = Path(args.root)
    dirs = sorted([d for d in root_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])
    books_with_epub = []

    for d in dirs:
        epubs = [e for e in d.rglob("*.epub") if not e.name.startswith("._")]
        if epubs:
            books_with_epub.append(d)

    print(f"Target collection root: {root_dir}")
    print(f"Total subdirectories: {len(dirs)}")
    print(f"Directories with EPUB: {len(books_with_epub)}\n")

    results = []
    total_start = time.time()

    for idx, b_dir in enumerate(books_with_epub, start=1):
        book_slug = b_dir.name
        book_out = OUTPUT_BASE / book_slug
        print(f"[{idx}/{len(books_with_epub)}] Processing: {b_dir.name}...")
        start_t = time.time()

        try:
            audios = [
                a for a in b_dir.rglob("*")
                if a.suffix.lower() in (".mp3", ".m4a", ".m4b") and not a.name.startswith("._")
            ]

            # Check if all audio tracks are already aligned in timeline
            existing_timeline = b_dir / "readalong" / "timeline.json"
            is_fully_aligned = False
            if existing_timeline.exists() and existing_timeline.stat().st_size > 100:
                try:
                    timeline_data = json.load(existing_timeline.open(encoding="utf-8"))
                    tl_tracks = set(s.get("audioSourceId") for s in timeline_data if s.get("audioSourceId"))
                    if len(audios) > 1:
                        # For multi-track books, require coverage across all tracks
                        if len(tl_tracks) >= len(audios):
                            is_fully_aligned = True
                    else:
                        if len(timeline_data) > 0:
                            is_fully_aligned = True
                except Exception:
                    is_fully_aligned = False

            if is_fully_aligned:
                print(f"    Already fully aligned across all tracks ({len(tl_tracks)}/{len(audios)}), skipping.")
                manifest_data = json.load((b_dir / "readalong" / "readalong.manifest.json").open())
                res = {
                    "status": "success",
                    "book_id": manifest_data.get("bookId"),
                    "matched_html": manifest_data.get("alignedDocument", "existing"),
                    "segment_count": len(timeline_data),
                    "cached": True,
                }
            else:
                print(f"    Incomplete alignment detected (only partial tracks). Starting full multi-track alignment...")
                res = align_single_book_universal(
                    book_dir=b_dir,
                    output_dir=book_out,
                    max_sample_seconds=1800.0,
                )
            elapsed = time.time() - start_t
            res["book_name"] = b_dir.name
            res["elapsed_seconds"] = round(elapsed, 2)
            results.append(res)
            print(f"    Result: {res['status']} ({res.get('segment_count', 0)} segments in {elapsed:.1f}s)\n")
        except Exception as e:
            elapsed = time.time() - start_t
            err_res = {
                "status": "error",
                "book_name": b_dir.name,
                "error": str(e),
                "elapsed_seconds": round(elapsed, 2),
            }
            results.append(err_res)
            print(f"    Error: {e}\n")

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
