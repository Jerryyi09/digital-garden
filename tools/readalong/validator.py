"""Independent structural and alignment validation for generated readalong assets."""

from collections import Counter
import hashlib
import json
from pathlib import Path
import posixpath
import subprocess
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile


def parse_clock(value: str) -> float:
    """Parse SMIL clock value (e.g. npt=12.34s, 120ms, or 01:23:45.67)."""
    val = value.removeprefix("npt=").strip()
    if val.endswith("ms"):
        return float(val[:-2]) / 1000.0
    val = val.removesuffix("s")
    parts = val.split(":")
    seconds = 0.0
    for part in parts:
        seconds = seconds * 60.0 + float(part)
    return seconds


def resolve_reference(base_file: str, href: str) -> tuple[str, str]:
    """Resolve a relative href against a base path and return (document_path, fragment_id)."""
    parsed = urlsplit(href)
    base_dir = posixpath.dirname(base_file)
    doc_path = posixpath.normpath(posixpath.join(base_dir, unquote(parsed.path)))
    fragment = unquote(parsed.fragment)
    return doc_path, fragment


def compute_sha256(file_path: Path) -> str:
    """Compute sha256 checksum of a file."""
    digest = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_overlay_epub(
    epub_path: Path,
    expected_source_hashes: dict[str, str] | None = None,
    allow_missing_audio_files: bool = False,
) -> dict:
    """Validate a generated media-overlay EPUB for structural correctness."""
    if not epub_path.exists():
        return {
            "structural_pass": False,
            "error": f"File not found: {epub_path}",
            "issues": [{"issue": "file_not_found", "file": str(epub_path)}],
        }

    issues = []
    segments = []
    documents = {}
    smils = []

    with zipfile.ZipFile(epub_path) as archive:
        names = set(archive.namelist())
        smils = sorted(name for name in names if name.lower().endswith(".smil"))
        if not smils:
            issues.append({"issue": "no_smil_overlays_found"})

        for smil in smils:
            try:
                root = ET.fromstring(archive.read(smil))
            except Exception as e:
                issues.append({"smil": smil, "issue": "malformed_smil_xml", "error": str(e)})
                continue

            for par in root.iter():
                if par.tag.split("}")[-1] != "par":
                    continue
                text_elem = next((x for x in par if x.tag.split("}")[-1] == "text"), None)
                audio_elem = next((x for x in par if x.tag.split("}")[-1] == "audio"), None)

                if text_elem is None or audio_elem is None:
                    issues.append({"smil": smil, "issue": "missing_text_or_audio_in_par"})
                    continue

                text_src = text_elem.attrib.get("src", "")
                audio_src = audio_elem.attrib.get("src", "")

                doc_path, fragment = resolve_reference(smil, text_src)
                media_path, _ = resolve_reference(smil, audio_src)

                clip_begin = parse_clock(audio_elem.attrib.get("clipBegin", "0s"))
                clip_end = parse_clock(audio_elem.attrib.get("clipEnd", "0s"))

                if doc_path not in names:
                    issues.append({"smil": smil, "issue": "text_document_not_in_epub", "document": doc_path})
                    continue
                if media_path not in names and not allow_missing_audio_files:
                    issues.append({"smil": smil, "issue": "audio_not_in_epub", "audio": media_path})
                    continue
                if not fragment:
                    issues.append({"smil": smil, "issue": "missing_text_fragment_id", "src": text_src})
                    continue
                if clip_end <= clip_begin or clip_begin < 0:
                    issues.append({
                        "smil": smil,
                        "issue": "invalid_clip_interval",
                        "clipBegin": clip_begin,
                        "clipEnd": clip_end,
                    })
                    continue

                if doc_path not in documents:
                    try:
                        dom = ET.fromstring(archive.read(doc_path))
                        documents[doc_path] = {
                            node.attrib["id"]: " ".join(" ".join(node.itertext()).split())
                            for node in dom.iter()
                            if "id" in node.attrib
                        }
                    except Exception as e:
                        issues.append({"smil": smil, "document": doc_path, "issue": "document_parse_error", "error": str(e)})
                        documents[doc_path] = {}

                if fragment not in documents[doc_path]:
                    issues.append({"smil": smil, "issue": "missing_fragment_in_document", "fragment": fragment, "document": doc_path})
                    continue

                segments.append({
                    "audio": media_path,
                    "start": clip_begin,
                    "end": clip_end,
                    "document": doc_path,
                    "fragment": fragment,
                    "text": documents[doc_path][fragment],
                })

    # Check temporal ordering
    audio_order = {media: index for index, media in enumerate(sorted({s["audio"] for s in segments}))}
    previous = None
    for segment in segments:
        if previous and segment["document"] == previous["document"]:
            if audio_order.get(segment["audio"], 0) < audio_order.get(previous["audio"], 0):
                issues.append({"issue": "audio_order_reversal", "fragment": segment["fragment"]})
            elif segment["audio"] == previous["audio"] and segment["start"] < previous["start"]:
                issues.append({"issue": "time_order_reversal", "fragment": segment["fragment"]})
        previous = segment

    # Check gaps and overlaps per audio file
    for media in sorted({segment["audio"] for segment in segments}):
        group = sorted((s for s in segments if s["audio"] == media), key=lambda s: s["start"])
        for index, segment in enumerate(group):
            if index > 0:
                prev_end = group[index - 1]["end"]
                if segment["start"] < prev_end - 0.05:
                    issues.append({
                        "audio": media,
                        "issue": "overlapping_clips",
                        "fragment": segment["fragment"],
                        "overlap_seconds": prev_end - segment["start"],
                    })
                elif segment["start"] - prev_end > 1.0:
                    issues.append({
                        "audio": media,
                        "issue": "interior_coverage_gap",
                        "fragment": segment["fragment"],
                        "gap_seconds": segment["start"] - prev_end,
                    })

    source_hashes_match = True
    if expected_source_hashes:
        for path_str, expected_hash in expected_source_hashes.items():
            p = Path(path_str)
            if p.exists():
                actual_hash = compute_sha256(p)
                if actual_hash != expected_hash:
                    source_hashes_match = False
                    issues.append({"issue": "source_file_hash_mismatch", "file": path_str})

    structural_pass = bool(segments) and not any(
        i["issue"] in (
            "file_not_found", "no_smil_overlays_found", "malformed_smil_xml",
            "missing_text_or_audio_in_par", "text_document_not_in_epub",
            "missing_fragment_in_document", "invalid_clip_interval",
            "audio_order_reversal", "time_order_reversal", "overlapping_clips"
        )
        for i in issues
    ) and source_hashes_match

    return {
        "epub": str(epub_path),
        "smil_count": len(smils),
        "segment_count": len(segments),
        "matched_documents": dict(Counter(s["document"] for s in segments)),
        "issues": issues,
        "structural_pass": structural_pass,
        "segments": segments,
    }
