#!/usr/bin/env python3
"""
Full Library Discovery & Conservation Inventory Scanner (Work Order LIB-VERIFY-01)

Recursively scans both audiobook roots, verifies strict conservation of all
physical source audio and EPUB files, computes authoritative fingerprints and
durations, and writes an immutable inventory ledger.
"""

import sys
import os
import json
import time
import hashlib
import subprocess
import datetime
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple

from tools.readalong.input_inventory import natural_sort_key, compute_file_sha256
from tools.readalong.authoritative_validator import probe_audio_duration
from tools.readalong.controlled_publisher import compute_dir_fingerprint

AUDIO_EXTS = {".mp3", ".m4a", ".m4b"}
EBOOK_EXTS = {".epub", ".pdf", ".mobi", ".azw", ".azw3", ".djvu"}


def get_epub_metadata(epub_path: Path) -> Dict[str, Any]:
    """Inspects EPUB container and OPF metadata safely."""
    res = {"language": "unknown", "valid_zip": False, "error": None}
    try:
        with zipfile.ZipFile(epub_path, "r") as z:
            res["valid_zip"] = True
            container_bytes = z.read("META-INF/container.xml")
            root = ET.fromstring(container_bytes)
            opf_path = None
            for elem in root.iter():
                if elem.tag.endswith("rootfile"):
                    opf_path = elem.attrib.get("full-path")
                    break
            if opf_path and opf_path in z.namelist():
                opf_bytes = z.read(opf_path)
                opf_root = ET.fromstring(opf_bytes)
                for elem in opf_root.iter():
                    if elem.tag.endswith("language"):
                        res["language"] = elem.text.strip() if elem.text else "unknown"
                        break
    except Exception as exc:
        res["error"] = str(exc)
    return res


def scan_root_raw(root_dir: Path) -> Tuple[List[Path], List[Path], List[Path]]:
    """Discovers all physical source audio, epubs, and other ebooks, strictly ignoring generated assets."""
    audios = []
    epubs = []
    other_ebooks = []

    for p in root_dir.rglob("*"):
        if p.name.startswith("._") or p.name.startswith(".DS_Store"):
            continue
        rel_parts = p.relative_to(root_dir).parts
        # Skip readalong active/staging/revisions/work
        if any(part in ("readalong", ".readalong_revisions", "work") or part.startswith(".readalong_staging") for part in rel_parts):
            continue
        if p.is_file():
            ext = p.suffix.lower()
            if ext in AUDIO_EXTS:
                audios.append(p)
            elif ext == ".epub":
                epubs.append(p)
            elif ext in EBOOK_EXTS:
                other_ebooks.append(p)

    return (
        sorted(audios, key=lambda x: natural_sort_key(str(x))),
        sorted(epubs, key=lambda x: natural_sort_key(str(x))),
        sorted(other_ebooks, key=lambda x: natural_sort_key(str(x)))
    )


def build_full_inventory(roots: List[Path], run_dir: Path) -> Dict[str, Any]:
    events_log = run_dir / "events.jsonl"
    start_ts = time.time()

    def log_event(event_type: str, payload: dict):
        entry = {
            "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "event": event_type,
            **payload
        }
        with events_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    log_event("INVENTORY_SCAN_STARTED", {"roots": [str(r) for r in roots]})

    inventory = {
        "schema_version": 2,
        "scan_time_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "roots": [],
        "summary": {
            "total_roots": len(roots),
            "total_units": 0,
            "total_physical_audios": 0,
            "total_physical_epubs": 0,
            "total_other_ebooks": 0,
            "conservation_verified": False,
        },
        "units": []
    }

    all_discovered_audios: Set[Path] = set()
    all_assigned_audios: Set[Path] = set()

    for root in roots:
        root = root.resolve()
        raw_audios, raw_epubs, raw_others = scan_root_raw(root)
        all_discovered_audios.update(raw_audios)

        root_meta = {
            "root_path": str(root),
            "root_name": root.name,
            "discovered_audios": len(raw_audios),
            "discovered_epubs": len(raw_epubs),
            "discovered_others": len(raw_others),
            "units_count": 0
        }

        # Resolve validation units
        units_in_root: List[Dict[str, Any]] = []

        direct_dirs = sorted([d for d in root.iterdir() if d.is_dir() and not d.name.startswith(".")],
                             key=lambda x: natural_sort_key(x.name))

        for d in direct_dirs:
            # Special case: Great Mental Models has 4 explicit volume subdirectories
            if root.name == "心智成长" and d.name == "Great Mental Models":
                sub_vols = sorted([sub for sub in d.iterdir() if sub.is_dir() and not sub.name.startswith(".") and sub.name not in ("readalong", ".readalong_revisions", "work")],
                                  key=lambda x: natural_sort_key(x.name))
                for vol in sub_vols:
                    unit_audios = [a for a in raw_audios if a.is_relative_to(vol)]
                    unit_epubs = [e for e in raw_epubs if e.is_relative_to(vol)]
                    unit_others = [o for o in raw_others if o.is_relative_to(vol)]
                    units_in_root.append({
                        "book_dir": vol,
                        "rel_path": vol.relative_to(root).as_posix(),
                        "parent_work": d.name,
                        "is_subvolume": True,
                        "audios": unit_audios,
                        "epubs": unit_epubs,
                        "others": unit_others,
                    })
            else:
                # All audio/epubs under d belongs to d (including nested Discs like in '心流')
                unit_audios = [a for a in raw_audios if a.is_relative_to(d)]
                unit_epubs = [e for e in raw_epubs if e.is_relative_to(d)]
                unit_others = [o for o in raw_others if o.is_relative_to(d)]
                units_in_root.append({
                    "book_dir": d,
                    "rel_path": d.relative_to(root).as_posix(),
                    "parent_work": d.name,
                    "is_subvolume": False,
                    "audios": unit_audios,
                    "epubs": unit_epubs,
                    "others": unit_others,
                })

        root_meta["units_count"] = len(units_in_root)
        inventory["roots"].append(root_meta)

        # Process each unit
        for u in units_in_root:
            b_dir = u["book_dir"]
            rel_path = u["rel_path"]
            unit_id = f"{root.name}/{rel_path}"

            unit_audios = sorted(u["audios"], key=lambda x: natural_sort_key(x.name))
            unit_epubs = sorted(u["epubs"], key=lambda x: natural_sort_key(x.name))
            unit_others = sorted(u["others"], key=lambda x: natural_sort_key(x.name))

            for a in unit_audios:
                if a in all_assigned_audios:
                    raise RuntimeError(f"FATAL: Audio track assigned twice across units: {a}")
                all_assigned_audios.add(a)

            # Check existing active readalong
            active_manifest_path = b_dir / "readalong" / "readalong.manifest.json"
            has_active = active_manifest_path.is_file()
            active_fp = None
            if has_active:
                try:
                    active_fp = compute_dir_fingerprint(b_dir / "readalong")
                except Exception as exc:
                    active_fp = f"ERROR: {exc}"

            # Inventory status
            status = "VALID"
            discovery_notes = []

            if not unit_audios:
                status = "MISSING_AUDIO"
                discovery_notes.append("No physical source audio found in unit")
            if not unit_epubs:
                if unit_others:
                    status = "UNSUPPORTED_FORMAT"
                    discovery_notes.append(f"Only non-EPUB ebooks found ({[o.suffix for o in unit_others]})")
                else:
                    status = "MISSING_EPUB"
                    discovery_notes.append("No EPUB or ebook files found in unit")
            elif len(unit_epubs) > 1:
                status = "MULTI_EPUB"
                discovery_notes.append(f"Multiple EPUBs ({len(unit_epubs)}) require explicit edition pairing")

            # Audio track metadata
            audio_records = []
            total_duration = 0.0
            for idx, a_path in enumerate(unit_audios):
                a_size = a_path.stat().st_size
                a_sha256 = compute_file_sha256(a_path)
                try:
                    a_dur = probe_audio_duration(a_path)
                except Exception as exc:
                    a_dur = -1.0
                    discovery_notes.append(f"Audio probe error on {a_path.name}: {exc}")
                total_duration += max(0.0, a_dur)
                audio_records.append({
                    "order": idx + 1,
                    "filename": a_path.name,
                    "rel_to_book": a_path.relative_to(b_dir).as_posix(),
                    "size_bytes": a_size,
                    "sha256": a_sha256,
                    "measured_duration": round(a_dur, 4)
                })

            # EPUB metadata
            epub_records = []
            detected_languages = set()
            for e_path in unit_epubs:
                e_size = e_path.stat().st_size
                e_sha256 = compute_file_sha256(e_path)
                meta = get_epub_metadata(e_path)
                detected_languages.add(meta["language"])
                epub_records.append({
                    "filename": e_path.name,
                    "rel_to_book": e_path.relative_to(b_dir).as_posix(),
                    "size_bytes": e_size,
                    "sha256": e_sha256,
                    "language": meta["language"],
                    "valid_zip": meta["valid_zip"],
                    "error": meta["error"]
                })

            other_records = []
            for o_path in unit_others:
                other_records.append({
                    "filename": o_path.name,
                    "rel_to_book": o_path.relative_to(b_dir).as_posix(),
                    "size_bytes": o_path.stat().st_size,
                    "format": o_path.suffix.lower()
                })

            unit_record = {
                "unit_id": unit_id,
                "root_name": root.name,
                "rel_path": rel_path,
                "book_dir": str(b_dir),
                "is_subvolume": u["is_subvolume"],
                "parent_work": u["parent_work"],
                "status": status,
                "discovery_notes": discovery_notes,
                "audio_count": len(unit_audios),
                "total_measured_duration": round(total_duration, 4),
                "epub_count": len(unit_epubs),
                "other_count": len(unit_others),
                "detected_languages": sorted(list(detected_languages)),
                "has_active_readalong": has_active,
                "active_manifest_exists": has_active,
                "active_readalong_fingerprint": active_fp,
                "audio_tracks": audio_records,
                "epubs": epub_records,
                "other_ebooks": other_records
            }
            inventory["units"].append(unit_record)

    # Conservation Verification
    unassigned = all_discovered_audios - all_assigned_audios
    if unassigned:
        raise RuntimeError(f"FATAL: Unassigned audio tracks remain: {[str(p) for p in unassigned]}")
    if len(all_discovered_audios) != len(all_assigned_audios):
        raise RuntimeError(f"FATAL: Discovered audio count ({len(all_discovered_audios)}) != Assigned ({len(all_assigned_audios)})")

    inventory["summary"]["total_units"] = len(inventory["units"])
    inventory["summary"]["total_physical_audios"] = len(all_discovered_audios)
    inventory["summary"]["total_physical_epubs"] = sum(u["epub_count"] for u in inventory["units"])
    inventory["summary"]["total_other_ebooks"] = sum(u["other_count"] for u in inventory["units"])
    inventory["summary"]["conservation_verified"] = True
    inventory["summary"]["elapsed_seconds"] = round(time.time() - start_ts, 2)

    log_event("INVENTORY_SCAN_COMPLETED", inventory["summary"])
    return inventory


def default_roots() -> List[Path]:
    """Every category directory of the local SSD library (config.DEFAULT_LOCAL_ROOT).
    /Volumes/750 is only the NUC deploy target and is never scanned."""
    from tools.readalong.config import DEFAULT_LOCAL_ROOT
    base = Path(DEFAULT_LOCAL_ROOT)
    return sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith("."))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build a full inventory for one or more library roots.")
    parser.add_argument("run_dir", nargs="?", default="private/readalong-library-runs/20261023T004348Z")
    parser.add_argument("--root", action="append", type=Path, default=[],
                        help="Category root containing book subdirectories; repeatable. Defaults to every category of the local SSD library.")
    args = parser.parse_args()
    roots = args.root or default_roots()
    missing = [r for r in roots if not r.is_dir()]
    if missing:
        parser.error(f"root not found: {', '.join(map(str, missing))}")
    run_dir = Path(args.run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Starting full library scan across {len(roots)} roots...")
    inventory = build_full_inventory(roots, run_dir)

    out_file = run_dir / "inventory.json"
    out_file.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n")
    print(f"[+] Inventory written to: {out_file}")
    print(f"    Total units: {inventory['summary']['total_units']}")
    print(f"    Total physical audios: {inventory['summary']['total_physical_audios']}")
    print(f"    Total physical epubs: {inventory['summary']['total_physical_epubs']}")
    print(f"    Total other ebooks: {inventory['summary']['total_other_ebooks']}")
    print(f"    Conservation verified: {inventory['summary']['conservation_verified']}")
    print(f"    Scan elapsed: {inventory['summary']['elapsed_seconds']}s")


if __name__ == "__main__":
    main()
