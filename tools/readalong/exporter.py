"""Export and package readalong assets for PWA consumption and standalone reading."""

import hashlib
import json
from pathlib import Path
import posixpath
import shutil
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile

from tools.readalong.validator import compute_sha256, parse_clock, resolve_reference


READALONG_CSS_INJECTION = """
/* Readalong highlight and typography styling */
.readalong-active {
  background-color: #dce7ae !important;
  color: #163c23 !important;
  border-radius: 3px;
  box-shadow: 0 0 0 2px #aec47d;
  transition: background-color 0.15s ease;
}
body {
  max-width: 820px;
  margin: 0 auto !important;
  padding: 24px 20px 80px 20px !important;
  line-height: 1.85 !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Georgia, serif !important;
  color: #263d34 !important;
  background-color: #fbf9f4 !important;
  -webkit-text-size-adjust: 100%;
}
p {
  margin: 1.2em 0 !important;
}
"""


def export_readalong_bundle(
    generated_epub: Path,
    output_dir: Path,
    book_id: str,
    source_epub: Path,
    primary_audio: Path,
    alist_audio_path: str,
    chunk_durations: dict[str, float] | list[float] | None = None,
    source_offset: float = 0.0,
    chapters_meta: list[dict] | None = None,
    model_name: str = "tiny.en",
    audio_sources_meta: list[dict] | None = None,
) -> dict:
    """Extract and build PWA-ready readalong bundle from the generated overlay EPUB."""
    output_dir.mkdir(parents=True, exist_ok=True)
    text_dir = output_dir / "text"
    text_dir.mkdir(parents=True, exist_ok=True)

    segments = []
    documents = {}

    with zipfile.ZipFile(generated_epub) as archive:
        names = set(archive.namelist())

        # Extract all non-audio files (HTML, CSS, images, etc.) into text_dir
        for name in names:
            if name.endswith("/") or name.lower().endswith((".m4a", ".mp3", ".m4b", ".wav")):
                continue
            dest = text_dir / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            content = archive.read(name)

            # If HTML/XHTML, inject readalong styling into <head>
            if name.lower().endswith((".htm", ".html", ".xhtml")):
                html_str = content.decode("utf-8", errors="replace")
                if "</head>" in html_str:
                    injected_style = f"<style>{READALONG_CSS_INJECTION}</style></head>"
                    html_str = html_str.replace("</head>", injected_style, 1)
                dest.write_text(html_str, encoding="utf-8")
            else:
                dest.write_bytes(content)

        # Parse SMIL media overlay files
        smils = sorted(name for name in names if name.lower().endswith(".smil"))
        for smil in smils:
            root = ET.fromstring(archive.read(smil))
            for par in root.iter():
                if par.tag.split("}")[-1] != "par":
                    continue
                text_elem = next((x for x in par if x.tag.split("}")[-1] == "text"), None)
                audio_elem = next((x for x in par if x.tag.split("}")[-1] == "audio"), None)
                if text_elem is None or audio_elem is None:
                    continue

                doc_path, fragment = resolve_reference(smil, text_elem.attrib["src"])
                audio_path, _ = resolve_reference(smil, audio_elem.attrib["src"])

                clip_begin = parse_clock(audio_elem.attrib["clipBegin"])
                clip_end = parse_clock(audio_elem.attrib["clipEnd"])

                if doc_path not in documents:
                    try:
                        dom = ET.fromstring(archive.read(doc_path))
                        documents[doc_path] = {
                            node.attrib["id"]: " ".join(" ".join(node.itertext()).split())
                            for node in dom.iter()
                            if "id" in node.attrib
                        }
                    except Exception:
                        documents[doc_path] = {}

                text_content = documents[doc_path].get(fragment, "")

                segments.append({
                    "chunk_audio": audio_path,
                    "chunk_start": clip_begin,
                    "chunk_end": clip_end,
                    "document": f"text/{doc_path}",
                    "fragment": fragment,
                    "text": text_content,
                })

    # Sort chunks naturally to establish offset mapping
    distinct_chunks = sorted({s["chunk_audio"] for s in segments})
    chunk_offsets = {}
    current_offset = source_offset

    # Map chunk file basenames to duration
    chunk_dur_map = {}
    if isinstance(chunk_durations, dict):
        chunk_dur_map = chunk_durations
    elif isinstance(chunk_durations, list):
        for i, chunk_name in enumerate(distinct_chunks):
            if i < len(chunk_durations):
                chunk_dur_map[chunk_name] = chunk_durations[i]

    for chunk_name in distinct_chunks:
        chunk_offsets[chunk_name] = current_offset
        chunk_dur = chunk_dur_map.get(chunk_name, 600.0)
        current_offset += chunk_dur

    # Build timeline segments mapped to concrete audio files
    timeline_segments = []
    has_multiple_sources = bool(audio_sources_meta and len(audio_sources_meta) > 1)

    for s in segments:
        base_offset = chunk_offsets.get(s["chunk_audio"], source_offset)
        abs_start = round(base_offset + s["chunk_start"], 3)
        abs_end = round(base_offset + s["chunk_end"], 3)

        if has_multiple_sources:
            # Locate which source file this segment falls into
            matched_src = next(
                (src for src in audio_sources_meta if src["start_offset"] <= abs_start < src["end_offset"]),
                None,
            )
            if not matched_src:
                matched_src = audio_sources_meta[-1] if abs_start >= audio_sources_meta[-1]["end_offset"] else audio_sources_meta[0]

            rel_start = round(max(0.0, abs_start - matched_src["start_offset"]), 3)
            rel_end = round(min(matched_src["duration"], abs_end - matched_src["start_offset"]), 3)
            if rel_end <= rel_start:
                rel_end = round(rel_start + 0.1, 3)

            timeline_segments.append({
                "audioSourceId": matched_src["id"],
                "start": rel_start,
                "end": rel_end,
                "document": s["document"],
                "fragment": s["fragment"],
                "text": s["text"],
                "reviewStatus": "unreviewed",
            })
        else:
            audio_source_id = primary_audio.name
            timeline_segments.append({
                "audioSourceId": audio_source_id,
                "start": abs_start,
                "end": abs_end,
                "document": s["document"],
                "fragment": s["fragment"],
                "text": s["text"],
                "reviewStatus": "unreviewed",
            })

    # Timeline MUST be strictly sorted by (audioSourceId, start, end)
    timeline_segments.sort(key=lambda seg: (seg["audioSourceId"], seg["start"], seg["end"]))

    # Save timeline.json
    timeline_path = output_dir / "timeline.json"
    timeline_path.write_text(json.dumps(timeline_segments, ensure_ascii=False, indent=2) + "\n")

    # Read EPUB title & metadata
    epub_sha256 = compute_sha256(source_epub)

    audio_sources_list = []
    if audio_sources_meta:
        for src in audio_sources_meta:
            audio_sources_list.append({
                "id": src["id"],
                "name": src["id"],
                "alistPath": src["alistPath"],
                "sha256": src.get("sha256", ""),
                "duration": src.get("duration", 0.0),
            })
    else:
        audio_sha256 = compute_sha256(primary_audio)
        audio_sources_list.append({
            "id": primary_audio.name,
            "name": primary_audio.name,
            "alistPath": alist_audio_path,
            "sha256": audio_sha256,
        })

    # Build readalong.manifest.json
    manifest = {
        "schemaVersion": 1,
        "bookId": book_id,
        "language": "en",
        "sourceEpubSha256": epub_sha256,
        "timing": {
            "engine": "whisper-word",
            "model": model_name,
        },
        "audioSources": audio_sources_list,
        "timeline": "timeline.json",
        "textRoot": "text/",
        "segmentCount": len(timeline_segments),
        "chapters": chapters_meta or [],
    }

    manifest_path = output_dir / "readalong.manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    # Copy generated EPUB as standalone standard export
    export_epub = output_dir / "book.readalong.epub"
    if not export_epub.exists() or export_epub.stat().st_size != generated_epub.stat().st_size:
        shutil.copyfile(generated_epub, export_epub)

    return {
        "output_dir": str(output_dir),
        "manifest_path": str(manifest_path),
        "timeline_path": str(timeline_path),
        "segment_count": len(timeline_segments),
    }
    timeline_path = output_dir / "timeline.json"
    timeline_path.write_text(json.dumps(timeline_segments, ensure_ascii=False, indent=2) + "\n")

    # Read EPUB title & metadata
    epub_sha256 = compute_sha256(source_epub)
    audio_sha256 = compute_sha256(primary_audio)

    # Build readalong.manifest.json
    manifest = {
        "schemaVersion": 1,
        "bookId": book_id,
        "language": "en",
        "sourceEpubSha256": epub_sha256,
        "timing": {
            "engine": "whisper-word",
            "model": model_name,
        },
        "audioSources": [
            {
                "id": audio_source_id,
                "name": primary_audio.name,
                "alistPath": alist_audio_path,
                "sha256": audio_sha256,
            }
        ],
        "timeline": "timeline.json",
        "textRoot": "text/",
        "segmentCount": len(timeline_segments),
        "chapters": chapters_meta or [],
    }

    manifest_path = output_dir / "readalong.manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    # Copy generated EPUB as standalone standard export
    export_epub = output_dir / "book.readalong.epub"
    if not export_epub.exists() or export_epub.stat().st_size != generated_epub.stat().st_size:
        shutil.copyfile(generated_epub, export_epub)

    return {
        "output_dir": str(output_dir),
        "manifest_path": str(manifest_path),
        "timeline_path": str(timeline_path),
        "segment_count": len(timeline_segments),
    }
