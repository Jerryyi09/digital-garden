"""Book directory scanning, pairing precheck, and metadata extraction."""

import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile

AUDIO_EXTENSIONS = {".m4b", ".mp3", ".m4a"}
IGNORE_DIRS = {".git", ".venv", "work", "generated", "preview", "runtime-snapshot", "__pycache__"}


def is_ignored(path: Path) -> bool:
    """Check if the path or any parent should be ignored."""
    name = path.name
    if name.startswith("._") or name == ".DS_Store":
        return True
    return any(part in IGNORE_DIRS for part in path.parts)


def probe_audio(file_path: Path) -> dict:
    """Probe audio duration and chapters via ffprobe."""
    try:
        raw = subprocess.check_output([
            "ffprobe", "-v", "error", "-show_format", "-show_chapters", "-of", "json",
            str(file_path)
        ], stderr=subprocess.DEVNULL)
        info = json.loads(raw)
        duration = float(info.get("format", {}).get("duration", 0.0))
        chapters = info.get("chapters", [])
        return {
            "duration": duration,
            "chapter_count": len(chapters),
            "chapters": [
                {
                    "title": c.get("tags", {}).get("title", f"Chapter {i+1}"),
                    "start": float(c.get("start_time", 0.0)),
                    "end": float(c.get("end_time", 0.0)),
                }
                for i, c in enumerate(chapters)
            ]
        }
    except Exception as e:
        return {"duration": 0.0, "chapter_count": 0, "chapters": [], "error": str(e)}


def probe_epub(file_path: Path) -> dict:
    """Probe EPUB metadata and spine documents without extracting."""
    try:
        with zipfile.ZipFile(file_path) as archive:
            root_xml = ET.fromstring(archive.read("META-INF/container.xml"))
            opf_path = next(
                n.attrib["full-path"]
                for n in root_xml.iter()
                if n.tag.endswith("rootfile") and "full-path" in n.attrib
            )
            opf_dir = Path(opf_path).parent.as_posix()
            package = ET.fromstring(archive.read(opf_path))

            metadata = {}
            manifest = {}
            for elem in package.iter():
                tag = elem.tag.split("}")[-1]
                if tag in ("title", "creator", "language", "identifier"):
                    metadata[tag] = (elem.text or "").strip()
                elif tag == "item" and "id" in elem.attrib and "href" in elem.attrib:
                    manifest[elem.attrib["id"]] = elem.attrib

            spine_items = []
            for itemref in package.iter():
                if itemref.tag.split("}")[-1] == "itemref":
                    idref = itemref.attrib.get("idref")
                    if idref and idref in manifest:
                        href = manifest[idref]["href"]
                        full_href = f"{opf_dir}/{href}".lstrip("/") if opf_dir and opf_dir != "." else href
                        spine_items.append({
                            "id": idref,
                            "href": full_href,
                            "media_type": manifest[idref].get("media-type", ""),
                        })

            return {
                "metadata": metadata,
                "spine_count": len(spine_items),
                "spine": spine_items,
            }
    except Exception as e:
        return {"metadata": {}, "spine_count": 0, "spine": [], "error": str(e)}


def slugify(text: str) -> str:
    """Generate a clean slug for book IDs."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


def inspect_book_dir(book_dir: Path) -> dict:
    """Inspect a single book directory for audio and EPUB pairings."""
    epubs = [e for e in book_dir.rglob("*.epub") if not is_ignored(e) and not e.name.startswith("._")]
    audios = [a for a in book_dir.rglob("*") if a.suffix.lower() in AUDIO_EXTENSIONS and not is_ignored(a) and not a.name.startswith("._")]

    # Sort files naturally
    epubs.sort(key=lambda p: p.name)
    audios.sort(key=lambda p: p.name)

    book_id = slugify(book_dir.name)
    pairing_status = "unpaired"
    if len(epubs) >= 1 and len(audios) >= 1:
        pairing_status = "paired"
    elif not epubs and audios:
        pairing_status = "missing_epub"
    elif epubs and not audios:
        pairing_status = "missing_audio"

    epub_info = probe_epub(epubs[0]) if epubs else None
    audio_info = [
        {"path": str(a), "name": a.name, "probe": probe_audio(a)}
        for a in audios
    ]

    total_audio_duration = sum(a["probe"].get("duration", 0.0) for a in audio_info)

    return {
        "book_id": book_id,
        "directory": str(book_dir),
        "pairing_status": pairing_status,
        "epubs": [str(e) for e in epubs],
        "audios": [str(a) for a in audios],
        "primary_epub": str(epubs[0]) if epubs else None,
        "primary_audio": str(audios[0]) if audios else None,
        "is_single_m4b": len(audios) == 1 and audios[0].suffix.lower() == ".m4b",
        "total_audio_duration": total_audio_duration,
        "epub_info": epub_info,
        "audio_info": audio_info,
    }


def scan_library(root_dir: Path, language: str = "en") -> list[dict]:
    """Scan a library root for audiobooks."""
    books = []
    # If root_dir itself contains media directly
    has_direct_media = any(
        f.suffix.lower() in AUDIO_EXTENSIONS or f.suffix.lower() == ".epub"
        for f in root_dir.iterdir() if f.is_file() and not is_ignored(f)
    )
    if has_direct_media:
        return [inspect_book_dir(root_dir)]

    for item in sorted(root_dir.iterdir()):
        if item.is_dir() and not is_ignored(item):
            has_media = any(
                f.suffix.lower() in AUDIO_EXTENSIONS or f.suffix.lower() == ".epub"
                for f in item.rglob("*") if f.is_file() and not is_ignored(f)
            )
            if has_media:
                info = inspect_book_dir(item)
                epub_lang = (info.get("epub_info") or {}).get("metadata", {}).get("language", "")
                if not language or not epub_lang or epub_lang.lower().startswith(language.lower()) or epub_lang.lower() == "und":
                    books.append(info)
    return books
