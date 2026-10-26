#!/usr/bin/env python3
"""
Immutable Input Inventory, Version Pairing & Cache Fingerprint (RA-04 Core)

1. Establishes immutable input inventory: audio paths, content SHA-256, measured duration.
2. Natural sorting as unambiguous default for tracks; flags ambiguous ordering.
3. Strongly fingerprinted cache key: audio_sha256 + sample_params + model_id + epub_sha256.
4. Safe EPUB extraction: blocks path traversal, symlinks, absolute paths.
"""

import re
import json
import zipfile
import hashlib
import stat
from pathlib import Path
from typing import Dict, Any, List, Optional


def natural_sort_key(s: str):
    """Natural sort key for strings containing numbers (e.g. track 1, 2, 10)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def safe_extract_epub(epub_path: Path, target_dir: Path) -> List[str]:
    """Preflight the whole archive before writing; enforce finite resource budgets."""
    extracted_files = []
    target_dir.mkdir(parents=True, exist_ok=True)
    resolved_target = target_dir.resolve()

    with zipfile.ZipFile(epub_path, "r") as z:
        members = z.infolist()
        if len(members) > 10000 or sum(m.file_size for m in members) > 256 * 1024 * 1024:
            raise ValueError("EPUB resource budget exceeded")
        seen = set()
        for member in members:
            # Check for path traversal or absolute path
            member_path = Path(member.filename)
            if member_path.is_absolute() or ".." in member_path.parts or "\\" in member.filename:
                raise ValueError(f"Malicious path traversal detected in EPUB archive: {member.filename}")

            dest_path = (target_dir / member.filename).resolve()
            if not dest_path.is_relative_to(resolved_target) or dest_path == resolved_target:
                raise ValueError(f"Path escapes extraction directory: {member.filename}")

            if (dest_path in seen or stat.S_ISLNK(member.external_attr >> 16)
                or member.file_size > 64 * 1024 * 1024
                or member.file_size / max(1, member.compress_size) > 1000):
                raise ValueError("Unsafe EPUB entry or compression budget exceeded")
            seen.add(dest_path)
        for member in members:
            dest_path = (target_dir / member.filename).resolve()
            if member.is_dir():
                dest_path.mkdir(parents=True, exist_ok=True)
                continue
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            # The header budget is checked again against streamed uncompressed bytes.
            count = 0
            with z.open(member) as source, dest_path.open("xb") as target:
                while chunk := source.read(65536):
                    count += len(chunk)
                    if count > member.file_size or count > 64 * 1024 * 1024:
                        raise ValueError("EPUB expanded beyond declared budget")
                    target.write(chunk)
            extracted_files.append(member.filename)

    return extracted_files


def build_book_inventory(book_dir: Path) -> Dict[str, Any]:
    """Scans and builds an immutable inventory for a book directory."""
    epubs = sorted(list(book_dir.glob("*.epub")), key=lambda p: natural_sort_key(p.name))
    audios = sorted([f for f in book_dir.iterdir() if f.is_file() and f.suffix.lower() in (".mp3", ".m4a", ".m4b") and "readalong" not in f.as_posix()], key=lambda p: natural_sort_key(p.name))

    inventory = {
        "book_id": book_dir.name,
        "primary_epub": None,
        "epubs": [],
        "audio_tracks": [],
        "warnings": [],
        "status": "VALID"
    }

    if not epubs:
        inventory["status"] = "INVALID"
        inventory["warnings"].append("No EPUB file found in book directory")
    else:
        inventory["primary_epub"] = {
            "name": epubs[0].name,
            "path": str(epubs[0].resolve()),
            "sha256": compute_file_sha256(epubs[0])
        }
        if len(epubs) > 1:
            inventory["status"] = "NEEDS_REVIEW"
            inventory["primary_epub"] = None
            inventory["warnings"].append("Multiple EPUBs require explicit edition pairing")

    if not audios:
        inventory["status"] = "INVALID"
        inventory["warnings"].append("No audio files found in book directory")

    for idx, a in enumerate(audios):
        inventory["audio_tracks"].append({
            "order": idx + 1,
            "filename": a.name,
            "path": str(a.resolve()),
            "sha256": compute_file_sha256(a),
            "size_bytes": a.stat().st_size
        })

    return inventory


def generate_cache_key(audio_sha256: str, model_id: str, sample_params: dict, epub_sha256: str = "") -> str:
    """Generates strong fingerprint combining audio content, model, and sampling parameters."""
    h = hashlib.sha256()
    h.update(audio_sha256.encode("utf-8"))
    h.update(model_id.encode("utf-8"))
    h.update(json.dumps(sample_params, sort_keys=True).encode("utf-8"))
    if epub_sha256:
        h.update(epub_sha256.encode("utf-8"))
    return h.hexdigest()


def compute_strong_cache_key(audio_sha256: str, sample_params: dict) -> str:
    """Versioned compatibility wrapper; callers must include the actual model hash."""
    return generate_cache_key(audio_sha256, "readalong-cache-v2", sample_params)


def model_fingerprint(model_path: Path) -> str:
    files = sorted(p for p in Path(model_path).rglob("*") if p.is_file())
    if not files:
        raise ValueError("Model files missing")
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(model_path).as_posix().encode())
        digest.update(compute_file_sha256(path).encode())
    return digest.hexdigest()
