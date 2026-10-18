"""Unified CLI entry point for the readalong alignment toolkit."""

import argparse
import json
from pathlib import Path
import sys

from tools.readalong.aligner import align_book
from tools.readalong.config import (
    DEFAULT_LOCAL_ROOT,
    DEFAULT_OUTPUT_DIR,
)
from tools.readalong.installer import execute_installation, plan_installation
from tools.readalong.scanner import inspect_book_dir, scan_library
from tools.readalong.validator import validate_overlay_epub


def cmd_scan(args: argparse.Namespace) -> int:
    """Scan library root or inspect a single book."""
    root_path = Path(args.root or DEFAULT_LOCAL_ROOT)
    if not root_path.exists():
        print(f"Error: Path does not exist: {root_path}", file=sys.stderr)
        return 1

    if any((root_path / f).suffix.lower() == ".epub" for f in root_path.iterdir() if f.is_file()):
        results = [inspect_book_dir(root_path)]
    else:
        results = scan_library(root_path, language=args.language)

    if args.dry_run or args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"Scanned {len(results)} books in {root_path}:")
        for b in results:
            print(f"  [{b['pairing_status']}] {b['book_id']} ({b['total_audio_duration']:.1f}s audio)")
            if b.get("epub_info") and b["epub_info"].get("metadata"):
                title = b["epub_info"]["metadata"].get("title", "Unknown")
                author = b["epub_info"]["metadata"].get("creator", "Unknown")
                print(f"    Title: {title} by {author}")
    return 0


def cmd_align(args: argparse.Namespace) -> int:
    """Align a single book."""
    book_dir = Path(args.book_dir)
    if not book_dir.exists():
        print(f"Error: Book directory does not exist: {book_dir}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir) if args.output_dir else None
    model_path = Path(args.model) if args.model else None

    print(f"Starting alignment for: {book_dir.name}")
    try:
        res = align_book(
            book_dir=book_dir,
            language=args.language,
            timing=args.timing,
            resume=args.resume,
            sample=args.sample,
            output_dir=output_dir,
            model_path=model_path,
            chunk_seconds=args.chunk_seconds,
        )
        print("\nAlignment finished successfully!")
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if res["structural_pass"] else 2
    except Exception as e:
        print(f"Alignment error: {e}", file=sys.stderr)
        return 1


def cmd_batch(args: argparse.Namespace) -> int:
    """Batch align all paired books under a library root."""
    root_path = Path(args.root or DEFAULT_LOCAL_ROOT)
    if not root_path.exists():
        print(f"Error: Root path does not exist: {root_path}", file=sys.stderr)
        return 1

    books = scan_library(root_path, language=args.language)
    paired_books = [b for b in books if b["pairing_status"] == "paired"]

    print(f"Found {len(paired_books)} paired books out of {len(books)} scanned in {root_path}.")
    stats = {"succeeded": 0, "failed": 0, "skipped": 0}

    for b in paired_books:
        b_dir = Path(b["directory"])
        b_id = b["book_id"]
        out_target = (Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR) / b_id
        if args.resume and (out_target / "readalong.manifest.json").exists():
            print(f"Skipping already aligned book: {b_id}")
            stats["skipped"] += 1
            continue

        print(f"\nProcessing [{b_id}]...")
        try:
            res = align_book(
                book_dir=b_dir,
                language=args.language,
                resume=args.resume,
                output_dir=out_target,
            )
            if res.get("structural_pass"):
                stats["succeeded"] += 1
            else:
                stats["failed"] += 1
        except Exception as e:
            print(f"Failed to align {b_id}: {e}", file=sys.stderr)
            stats["failed"] += 1

    print("\nBatch alignment summary:")
    print(json.dumps(stats, indent=2))
    return 0 if stats["failed"] == 0 else 1


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate existing readalong output."""
    output_base = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    target_dir = output_base / args.book_id if args.book_id else Path(args.output_dir or ".")
    generated_epub = next(target_dir.glob("*.readalong.epub"), None) or next(
        (target_dir / "generated").glob("*.media-overlay.epub"), None
    )

    if not generated_epub or not generated_epub.exists():
        print(f"Error: No media-overlay EPUB found in {target_dir}", file=sys.stderr)
        return 1

    report = validate_overlay_epub(generated_epub)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["structural_pass"] else 1


def cmd_install(args: argparse.Namespace) -> int:
    """Install or preview deployment of generated readalong assets."""
    target_dir = Path(args.target_dir) if args.target_dir else None
    if not target_dir:
        # Default local target alongside the book if local
        target_dir = Path(DEFAULT_LOCAL_ROOT) / args.book_id / ".readalong"

    plan = plan_installation(
        book_id=args.book_id,
        target_dir=target_dir,
        output_base=Path(args.output_dir) if args.output_dir else None,
    )
    result = execute_installation(plan, dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""
    parser = argparse.ArgumentParser(
        prog="readalong",
        description="Audiobook readalong alignment and EPUB media overlay CLI toolkit.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # scan
    p_scan = subparsers.add_parser("scan", help="Scan book library and check pairings.")
    p_scan.add_argument("--root", default=DEFAULT_LOCAL_ROOT, help="Library root directory.")
    p_scan.add_argument("--language", default="en", help="Language filter.")
    p_scan.add_argument("--dry-run", action="store_true", help="Print json report without side effects.")
    p_scan.add_argument("--json", action="store_true", help="Output full JSON.")
    p_scan.set_defaults(func=cmd_scan)

    # align
    p_align = subparsers.add_parser("align", help="Align a single audiobook.")
    p_align.add_argument("--book-dir", required=True, help="Directory containing book audio and EPUB.")
    p_align.add_argument("--language", default="en", help="Language of book.")
    p_align.add_argument("--timing", default="whisper-word", choices=["whisper-word", "ctc"], help="Timing method.")
    p_align.add_argument("--resume", action="store_true", default=True, help="Reuse previous transcription/chunks.")
    p_align.add_argument("--no-resume", dest="resume", action="store_false")
    p_align.add_argument("--sample", default=None, help="Sample slice name (e.g. 'prologue').")
    p_align.add_argument("--output-dir", default=None, help="Custom output directory.")
    p_align.add_argument("--model", default=None, help="Custom model path.")
    p_align.add_argument("--chunk-seconds", type=int, default=600, help="Chunk duration in seconds.")
    p_align.set_defaults(func=cmd_align)

    # batch
    p_batch = subparsers.add_parser("batch", help="Batch align library books.")
    p_batch.add_argument("--root", default=DEFAULT_LOCAL_ROOT, help="Library root directory.")
    p_batch.add_argument("--language", default="en", help="Language filter.")
    p_batch.add_argument("--resume", action="store_true", default=True, help="Skip already aligned books.")
    p_batch.add_argument("--output-dir", default=None, help="Base output directory.")
    p_batch.set_defaults(func=cmd_batch)

    # validate
    p_val = subparsers.add_parser("validate", help="Validate generated readalong output.")
    p_val.add_argument("--book-id", default=None, help="Book ID to validate.")
    p_val.add_argument("--output-dir", default=None, help="Output directory to validate.")
    p_val.set_defaults(func=cmd_validate)

    # install
    p_inst = subparsers.add_parser("install", help="Deploy readalong assets.")
    p_inst.add_argument("--book-id", required=True, help="Book ID.")
    p_inst.add_argument("--target", default="local", choices=["local", "nuc"], help="Target platform.")
    p_inst.add_argument("--target-dir", default=None, help="Target directory.")
    p_inst.add_argument("--output-dir", default=None, help="Base output directory.")
    p_inst.add_argument("--dry-run", action="store_true", help="Preview installation.")
    p_inst.set_defaults(func=cmd_install)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    code = args.func(args)
    sys.exit(code)


if __name__ == "__main__":
    main()
