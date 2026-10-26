#!/usr/bin/env python3
"""
Unified Readalong CLI (RA-11 Core)

Single controlled CLI for audio-text synchronization:
  - inspect: Read-only inventory of book tracks and EPUB.
  - audit: Comprehensive read-only authoritative validation with typed JSON report.
  - align: Aligns candidate into isolated staging revision without touching active.
  - publish: Atomically promotes a certified staging revision to active readalong/.
  - rollback: Restores previous active backup.
"""

import sys
import json
import argparse
from pathlib import Path

from tools.readalong.input_inventory import build_book_inventory
from tools.readalong.authoritative_validator import audit_book_authoritative
from tools.readalong.controlled_publisher import (
    create_staging_revision,
    certify_staging_candidate,
    publish_staging_to_active,
    rollback_to_previous_active
)


def cmd_inspect(args):
    book_dir = Path(args.book).resolve()
    inv = build_book_inventory(book_dir)
    print(json.dumps(inv, indent=2, ensure_ascii=False))
    sys.exit(0 if inv.get("status") == "VALID" else 2)


def cmd_audit(args):
    book_dir = Path(args.book).resolve()
    report = audit_book_authoritative(book_dir, reference_path=args.reference)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        sym = "✅ PASS" if report["status"] == "PASS" else "❌ FAILED"
        print(f"\nAudit Report: {sym} for {report['book_id']}")
        print(f"  Layers: {report['quality_layers']}")
        print(f"  Errors: {len(report['errors'])}, Warnings: {len(report['warnings'])}")
        for err in report["errors"][:5]:
            print(f"    - [{err['code']}] {err['msg']}")
        if len(report["errors"]) > 5:
            print(f"    ... and {len(report['errors']) - 5} more")
    sys.exit(0 if report["status"] == "PASS" else 2)


def cmd_align(args):
    book_dir = Path(args.book).resolve()
    staging_dir = create_staging_revision(book_dir)
    print(f"[*] Created staging revision at: {staging_dir}")
    print("[*] Running universal alignment engine...")
    try:
        from tools.readalong.universal_aligner import align_single_book_universal
    except ImportError as e:
        print(f"[!] Alignment engine dependencies not met in this environment: {e}")
        sys.exit(1)
    res = align_single_book_universal(book_dir, staging_dir, max_sample_seconds=args.max_sample)
    status = res.get("status")
    print(f"[*] Alignment finished with status: {status}")
    print(f"[*] Candidate preserved in staging: {staging_dir}. Alignment never publishes.")
    sys.exit(0 if status == "PASS" else 2)


def cmd_publish(args):
    book_dir = Path(args.book).resolve()
    staging_dir = Path(args.staging).resolve()
    if args.standard == 'strict' or args.reference:
        if not args.reference:
            raise ValueError('Strict certification publication requires --reference')
        res = publish_staging_to_active(book_dir, staging_dir, dry_run=args.dry_run, reference_path=args.reference)
    else:
        from tools.readalong.practical_publisher import publish_practical
        material = json.loads(Path(args.material_policy).read_text()) if args.material_policy else None
        res = publish_practical(book_dir, staging_dir, dry_run=args.dry_run, material=material)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    sys.exit(0 if res.get("success") else 1)


def cmd_certify(args):
    report = certify_staging_candidate(Path(args.staging), book_dir=Path(args.book),
                                      reference_path=args.reference)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if report["status"] == "PASS" else 2)


def cmd_rollback(args):
    book_dir = Path(args.book).resolve()
    backup_dir = Path(args.backup).resolve()
    res = rollback_to_previous_active(book_dir, backup_dir, reference_path=args.reference)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    sys.exit(0 if res.get("success") else 1)


def cmd_practical(args):
  from tools.readalong.practical_publisher import audit_practical, publish_practical, rollback_practical, exclude_readalong
  material = None
  if getattr(args, 'material_policy', None):
    material = json.loads(Path(args.material_policy).read_text())
  if args.command == 'audit-practical':
    result = audit_practical(args.book, args.staging, material,
      workers=args.workers, incremental_cache=args.incremental_cache)
    ok = result['publishAllowed']
  elif args.command == 'publish-practical':
    result = publish_practical(args.book, args.staging, dry_run=args.dry_run, material=material)
    ok = result['success']
  elif args.command == 'exclude-practical':
    result = exclude_readalong(args.book, args.reason)
    ok = result['success']
  else:
    result = rollback_practical(args.book, args.revision)
    ok = result['success']
  print(json.dumps(result, indent=2, ensure_ascii=False))
  sys.exit(0 if ok else 2)


def main():
    parser = argparse.ArgumentParser(description="Unified Controlled Readalong CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # inspect
    p_insp = subparsers.add_parser("inspect", help="Inspect book inventory")
    p_insp.add_argument("book", help="Path to book directory")
    p_insp.set_defaults(func=cmd_inspect)

    # audit
    p_aud = subparsers.add_parser("audit", help="Run authoritative read-only audit")
    p_aud.add_argument("book", help="Path to book directory")
    p_aud.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_aud.add_argument("--reference", help="Explicit operator-approved external reference JSON")
    p_aud.set_defaults(func=cmd_audit)

    # align
    p_align = subparsers.add_parser("align", help="Align candidate into staging revision")
    p_align.add_argument("book", help="Path to book directory")
    p_align.add_argument("--max-sample", type=float, default=1800.0)
    p_align.set_defaults(func=cmd_align)

    # publish
    p_cert = subparsers.add_parser("certify", help="Recompute approved reference evidence for a candidate")
    p_cert.add_argument("book")
    p_cert.add_argument("staging")
    p_cert.add_argument("--reference", required=True)
    p_cert.set_defaults(func=cmd_certify)

    p_pub = subparsers.add_parser("publish", help="Publish using personal practical policy by default; strict is explicit")
    p_pub.add_argument("book", help="Path to book directory")
    p_pub.add_argument("staging", help="Path to staging revision directory")
    p_pub.add_argument("--dry-run", action="store_true")
    p_pub.add_argument("--standard", choices=['practical', 'strict'], default='practical')
    p_pub.add_argument("--reference", help="Approved external reference JSON; explicitly selects strict certification")
    p_pub.add_argument("--material-policy", help="One source-bound approved policy entry JSON")
    p_pub.set_defaults(func=cmd_publish)

    # rollback
    p_rb = subparsers.add_parser("rollback", help="Rollback active to backup revision")
    p_rb.add_argument("book", help="Path to book directory")
    p_rb.add_argument("backup", help="Path to backup directory")
    p_rb.add_argument("--reference", required=True, help="Approved external reference JSON")
    p_rb.set_defaults(func=cmd_rollback)

    for command in ('audit-practical', 'publish-practical'):
        p = subparsers.add_parser(command, help='Personal-use 5%% policy; no external acoustic reference required')
        p.add_argument('book')
        p.add_argument('staging')
        if command == 'audit-practical':
            p.add_argument('--workers', type=int, choices=range(1, 5), default=4)
            p.add_argument('--incremental-cache', help='Opt-in trusted local stat-bound evidence JSON; not full revalidation')
        p.add_argument('--material-policy', help='One explicit source-bound approved policy entry JSON, not an entries wrapper')
        if command == 'publish-practical':
            p.add_argument('--dry-run', action='store_true')
        p.set_defaults(func=cmd_practical)
    p = subparsers.add_parser('rollback-practical', help='Restore the saved entry manifest without deleting assets')
    p.add_argument('book')
    p.add_argument('revision')
    p.set_defaults(func=cmd_practical)

    p = subparsers.add_parser('exclude-practical', help='Disable follow-along, retain source audio and save previous entry')
    p.add_argument('book')
    p.add_argument('--reason', required=True)
    p.set_defaults(func=cmd_practical)

    args = parser.parse_args()
    try:
        args.func(args)
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"status": "FAILED", "error": str(exc)}, ensure_ascii=False))
        sys.exit(2)


if __name__ == "__main__":
    main()
