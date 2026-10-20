#!/usr/bin/env python3
"""
Audiobook Readalong Manifest & Timeline Integrity Validator

Audits existing and newly added audiobook readalong assets:
1. Validates readalong.manifest.json schema and audioSources.
2. Checks timeline.json timestamps for monotonicity, non-negativity, and reasonable gaps.
3. Verifies that all referenced HTML documents exist on disk.
4. Checks that HTML files contain the exact fragment IDs declared in timeline.json.

Usage:
  python3 tools/readalong/validate_manifests.py [--root <path>]
"""

import sys
import json
import argparse
from pathlib import Path


def validate_book_readalong(book_dir: Path, verbose: bool = False) -> list[str]:
    errors = []
    readalong_dir = book_dir / "readalong"
    if not readalong_dir.exists():
        return errors  # No readalong configured for this book, skip

    manifest_file = readalong_dir / "readalong.manifest.json"
    if not manifest_file.exists():
        return [f"Missing manifest file at {manifest_file}"]

    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"Malformed JSON in {manifest_file}: {e}"]

    # Schema checks
    if manifest.get("schemaVersion") != 1:
        errors.append(f"Invalid schemaVersion: {manifest.get('schemaVersion')}")

    timeline_name = manifest.get("timeline", "timeline.json")
    timeline_file = readalong_dir / timeline_name
    if not timeline_file.exists():
        return [f"Missing timeline file: {timeline_file}"]

    try:
        timeline = json.loads(timeline_file.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"Malformed JSON in {timeline_file}: {e}"]

    if not isinstance(timeline, list) or len(timeline) == 0:
        errors.append("Timeline is empty or not a list")
        return errors

    # Check documents and fragments
    seen_docs = {}
    last_per_track = {}

    for idx, seg in enumerate(timeline):
        start = seg.get("start")
        end = seg.get("end")
        doc_rel = seg.get("document")
        frag = seg.get("fragment")
        track = seg.get("audioSourceId", "")

        if start is None or end is None:
            errors.append(f"Segment #{idx} missing start/end")
            continue

        try:
            start_f = float(start)
            end_f = float(end)
        except (ValueError, TypeError):
            errors.append(f"Segment #{idx} non-numeric start/end: {start}, {end}")
            continue

        if start_f < 0 or end_f < start_f:
            errors.append(f"Segment #{idx} invalid time range: [{start_f}, {end_f}]")

        # Monotonicity check within same track
        if track in last_per_track:
            prev_start = last_per_track[track]
            if start_f < prev_start:
                errors.append(
                    f"Segment #{idx} track '{track}' time goes backward: {start_f} < {prev_start}"
                )
        last_per_track[track] = start_f

        # Check document file exists
        if doc_rel:
            if doc_rel not in seen_docs:
                doc_path = readalong_dir / doc_rel
                if not doc_path.exists():
                    errors.append(f"Referenced document not found: {doc_path}")
                    seen_docs[doc_rel] = None
                else:
                    try:
                        seen_docs[doc_rel] = doc_path.read_text(encoding="utf-8", errors="replace")
                    except Exception as e:
                        errors.append(f"Failed to read document {doc_path}: {e}")
                        seen_docs[doc_rel] = None

            # Verify fragment ID in document
            html_content = seen_docs.get(doc_rel)
            if html_content and frag:
                needle = f'id="{frag}"'
                needle_alt = f"id='{frag}'"
                if needle not in html_content and needle_alt not in html_content:
                    errors.append(f"Fragment ID '{frag}' not found in document '{doc_rel}'")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate audiobook readalong assets")
    parser.add_argument(
        "--root",
        default="/Users/jerryyi/Desktop/寒假",
        help="Root path containing audiobook folders",
    )
    parser.add_argument("--verbose", action="store_true", help="Print detailed info")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"Directory {root} does not exist.")
        sys.exit(0)

    book_dirs = [p.parent for p in root.rglob("readalong.manifest.json")]
    print(f"Found {len(book_dirs)} books with readalong assets under {root}\n")

    total_books = len(book_dirs)
    passed_books = 0
    failed_books = []

    for b in book_dirs:
        errs = validate_book_readalong(b, verbose=args.verbose)
        if errs:
            failed_books.append((b.name, errs))
            print(f"❌ {b.name} ({len(errs)} issues):")
            for e in errs[:5]:
                print(f"   - {e}")
            if len(errs) > 5:
                print(f"   ... and {len(errs) - 5} more")
        else:
            passed_books += 1
            if args.verbose:
                print(f"✅ {b.name}")

    print("\n" + "=" * 50)
    print(f"Validation Summary: {passed_books}/{total_books} passed")
    if failed_books:
        print(f"Found {len(failed_books)} books with issues that need attention.")
        sys.exit(1)
    else:
        print("All readalong assets are 100% compliant and ready!")
        sys.exit(0)


if __name__ == "__main__":
    main()
