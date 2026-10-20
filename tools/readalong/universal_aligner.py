"""Universal, divergence-tolerant readalong aligner for library collections."""

from difflib import SequenceMatcher
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET
import zipfile
from bs4 import BeautifulSoup

from tools.readalong.config import (
    DEFAULT_ALIST_ROOT,
    DEFAULT_OUTPUT_DIR,
    resolve_model_path,
    resolve_nltk_data_path,
)
from tools.readalong.engine.mark_sentence import mark_sentences
from tools.readalong.exporter import READALONG_CSS_INJECTION
from tools.readalong.validator import compute_sha256, validate_overlay_epub


def normalize_token(w: str) -> str:
    return re.sub(r"[^a-z0-9]", "", w.lower())


def get_audio_duration(file_path: Path) -> float:
    try:
        raw = subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=nw=1:nk=1", str(file_path)
        ], stderr=subprocess.DEVNULL).decode().strip()
        return float(raw)
    except Exception:
        return 0.0


def extract_audio_sample(input_audio: Path, output_audio: Path, duration_seconds: float = 900.0) -> float:
    """Extract first N seconds of audio safely without video streams."""
    output_audio.parent.mkdir(parents=True, exist_ok=True)
    if output_audio.exists() and output_audio.stat().st_size > 0:
        return get_audio_duration(output_audio)

    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(input_audio), "-t", str(duration_seconds),
        "-map", "0:a:0", "-vn", "-sn", "-dn",
        "-c:a", "aac", "-b:a", "64k", "-ac", "1", "-ar", "24000",
        str(output_audio),
    ], check=True)
    return get_audio_duration(output_audio)


def transcribe_words(audio_path: Path, model_path: Path) -> list[dict]:
    """Transcribe audio with word-level timestamps."""
    from mlx_whisperx.backend.mlx_whisper.transcribe import transcribe as mlx_transcribe
    res = mlx_transcribe(
        str(audio_path),
        path_or_hf_repo=str(model_path),
        language="en",
        word_timestamps=True,
        condition_on_previous_text=False,
        verbose=False,
        fp16=True,
    )
    words = []
    for seg in res.get("segments", []):
        for w in seg.get("words", []):
            norm = normalize_token(w.get("word", ""))
            if norm:
                words.append({
                    "word": w.get("word", "").strip(),
                    "norm": norm,
                    "start": round(float(w.get("start", 0.0)), 3),
                    "end": round(float(w.get("end", 0.0)), 3),
                })
    return words


def find_best_matching_html(epub_path: Path, audio_words: list[dict]) -> tuple[str | None, list[str]]:
    """Scan all HTML files in EPUB and find the best matching candidate."""
    if not audio_words:
        return None, []

    audio_norms = [w["norm"] for w in audio_words if w["norm"]]
    best_html = None
    best_score = 0
    spine_htmls = []

    with zipfile.ZipFile(epub_path) as z:
        # Determine spine order from OPF
        root_xml = ET.fromstring(z.read("META-INF/container.xml"))
        opf_path = next(n.attrib["full-path"] for n in root_xml.iter() if n.tag.endswith("rootfile"))
        opf_dir = Path(opf_path).parent.as_posix()
        pkg = ET.fromstring(z.read(opf_path))

        manifest = {}
        for elem in pkg.iter():
            if elem.tag.endswith("item") and "id" in elem.attrib and "href" in elem.attrib:
                manifest[elem.attrib["id"]] = elem.attrib["href"]

        for itemref in pkg.iter():
            if itemref.tag.endswith("itemref"):
                idref = itemref.attrib.get("idref")
                if idref and idref in manifest:
                    href = manifest[idref]
                    full_href = f"{opf_dir}/{href}".lstrip("/") if opf_dir and opf_dir != "." else href
                    if full_href.lower().endswith((".htm", ".html", ".xhtml", ".xml")):
                        spine_htmls.append(full_href)

        # Score candidates, ignoring pure frontmatter / navigation documents
        def is_frontmatter_file(f_name: str) -> bool:
            base = os.path.basename(f_name).lower()
            stem = os.path.splitext(base)[0]
            if stem in ("cover", "titlepage", "title_page", "title", "toc", "nav", "copyright", "adcard", "ad-card"):
                return True
            if base.startswith(("cover.", "toc.", "nav.", "titlepage.", "copyright.")):
                return True
            return False

        for html_file in spine_htmls:
            if is_frontmatter_file(html_file):
                continue
            try:
                raw_html = z.read(html_file).decode("utf-8", errors="replace")
                soup = BeautifulSoup(raw_html, "lxml")
                text = " ".join(soup.get_text().split())
                tokens = [normalize_token(w) for w in text.split()]
                tokens = [t for t in tokens if t]
                if len(tokens) < 30:
                    continue

                m = SequenceMatcher(None, tokens, audio_norms).find_longest_match(0, len(tokens), 0, len(audio_norms))
                score = m.size
                if score > best_score:
                    best_score = score
                    best_html = html_file
            except Exception:
                continue

    return best_html, spine_htmls


def align_single_book_universal(
    book_dir: Path,
    output_dir: Path,
    max_sample_seconds: float = 1200.0,
) -> dict:
    """Universal alignment for a book, tolerant to version discrepancies."""
    epubs = [e for e in book_dir.rglob("*.epub") if not e.name.startswith("._")]
    if not epubs:
        return {"status": "skipped", "reason": "no_epub"}

    primary_epub = epubs[0]
    audios = [
        a for a in book_dir.rglob("*")
        if a.suffix.lower() in (".mp3", ".m4a", ".m4b") and not a.name.startswith("._")
    ]
    if not audios:
        return {"status": "skipped", "reason": "no_audio"}

    # Sort audios naturally
    audios.sort(key=lambda p: p.name)
    primary_audio = audios[0]

    # If first track is a very short credit or opening audio (< 60s), pick the first substantial chapter track
    if len(audios) > 1 and (get_audio_duration(primary_audio) < 60.0 or any(k in primary_audio.name.lower() for k in ("opening credit", "credits", "opening_credit"))):
        for a in audios[1:]:
            if get_audio_duration(a) >= 60.0:
                primary_audio = a
                break

    work_dir = output_dir / "work"
    text_dir = output_dir / "text"
    work_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)

    model_path = resolve_model_path()
    os.environ["NLTK_DATA"] = str(resolve_nltk_data_path())

    # 1. Prepare sample audio for alignment
    sample_m4a = work_dir / f"sample_{primary_audio.stem}.m4a"
    sample_duration = extract_audio_sample(primary_audio, sample_m4a, duration_seconds=max_sample_seconds)

    # 2. Transcribe words
    transcript_cache = work_dir / f"transcript_{primary_audio.stem}.json"
    if transcript_cache.exists():
        audio_words = json.load(transcript_cache.open(encoding="utf-8"))
    else:
        audio_words = transcribe_words(sample_m4a, model_path)
        transcript_cache.write_text(json.dumps(audio_words, ensure_ascii=False, indent=2))

    if not audio_words:
        return {"status": "skipped", "reason": "transcription_empty"}

    # 3. Find matching HTML in EPUB
    matched_html, spine_htmls = find_best_matching_html(primary_epub, audio_words)
    if not matched_html:
        # Fall back to first non-empty content page
        matched_html = next(
            (h for h in spine_htmls if not any(x in h.lower() for x in ("title", "cover", "toc", "nav"))),
            spine_htmls[0] if spine_htmls else None
        )

    if not matched_html:
        return {"status": "failed", "reason": "no_html_found"}

    # 4. Extract all EPUB assets into text/
    with zipfile.ZipFile(primary_epub) as z:
        for name in z.namelist():
            if name.endswith("/"):
                continue
            dest = text_dir / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            content = z.read(name)
            if name.lower().endswith((".htm", ".html", ".xhtml", ".xml")):
                html_str = content.decode("utf-8", errors="replace")
                if "</head>" in html_str and ".readalong-active" not in html_str:
                    html_str = html_str.replace("</head>", f"<style>{READALONG_CSS_INJECTION}</style></head>", 1)
                dest.write_text(html_str, encoding="utf-8")
            else:
                dest.write_bytes(content)

    # 5. Segment and align the target HTML
    target_dest = text_dir / matched_html
    raw_content = target_dest.read_text(encoding="utf-8")
    chapter_id = re.sub(r"[^a-zA-Z0-9]", "", Path(matched_html).stem)[:8] or "ch1"

    marked_html = mark_sentences(raw_content, chapter_id=chapter_id)
    soup = BeautifulSoup(marked_html, "lxml")
    spans = [
        s for s in soup.find_all("span")
        if s.get("id", "").startswith(f"c{chapter_id}-segment") or s.get("id", "").startswith(f"{chapter_id}-segment")
    ]

    audio_norms = [w["norm"] for w in audio_words]
    segments = []

    # First anchor: locate where the chapter starts in the audio stream
    audio_ptr = 0
    for span in spans[:10]:
        t_tokens = [normalize_token(w) for w in span.get_text().split()]
        t_tokens = [t for t in t_tokens if t]
        if len(t_tokens) >= 3:
            init_m = SequenceMatcher(None, t_tokens, audio_norms).find_longest_match(0, len(t_tokens), 0, len(audio_norms))
            if init_m.size >= min(4, len(t_tokens)):
                audio_ptr = max(0, init_m.b - 5)
                break

    for span in spans:
        text = span.get_text().strip()
        tokens = [normalize_token(w) for w in text.split()]
        tokens = [t for t in tokens if t]
        if not tokens:
            continue

        if len(tokens) < 2 and tokens[0] in ("1", "2", "3", "4", "5", "i", "ii", "a", "b", "c"):
            continue

        # Lookahead search in flexible sliding window (up to 1200 words)
        window_end = min(len(audio_norms), audio_ptr + 1200)
        sub_audio = audio_norms[audio_ptr:window_end]

        matcher = SequenceMatcher(None, tokens, sub_audio)
        match = matcher.find_longest_match(0, len(tokens), 0, len(sub_audio))

        is_valid = False
        if len(tokens) <= 3:
            if match.size == len(tokens) and match.b < 80:
                is_valid = True
        else:
            if match.b > 80:
                is_valid = (match.size >= 4)
            else:
                is_valid = (match.size >= 3) or (match.size >= len(tokens) * 0.5)

        if is_valid:
            abs_start = audio_words[audio_ptr + match.b]["start"]
            abs_end = audio_words[audio_ptr + match.b + match.size - 1]["end"]
            if abs_end <= abs_start:
                abs_end = round(abs_start + 0.1, 3)

            segments.append({
                "audioSourceId": primary_audio.name,
                "start": abs_start,
                "end": abs_end,
                "document": f"text/{matched_html}",
                "fragment": span["id"],
                "text": text,
                "reviewStatus": "unreviewed",
            })
            audio_ptr = audio_ptr + match.b + match.size

    # Overwrite target html with spans
    target_dest.write_text(marked_html, encoding="utf-8")

    # Sort segments
    segments.sort(key=lambda s: (s["start"], s["end"]))

    # Save timeline.json
    timeline_path = output_dir / "timeline.json"
    timeline_path.write_text(json.dumps(segments, ensure_ascii=False, indent=2) + "\n")

    # Build manifest
    book_id = re.sub(r"[^\w\s-]", "", book_dir.name.lower()).replace(" ", "-")
    category = book_dir.parent.name
    if category in ("未命名文件夹", "寒假"):
        category = "文学作品"

    audio_sources = [
        {
            "id": primary_audio.name,
            "name": primary_audio.name,
            "alistPath": f"{DEFAULT_ALIST_ROOT}/{category}/{book_dir.name}/{primary_audio.name}",
            "sha256": compute_sha256(primary_audio),
            "duration": get_audio_duration(primary_audio),
        }
    ]

    manifest = {
        "schemaVersion": 1,
        "bookId": book_id,
        "language": "en",
        "sourceEpubSha256": compute_sha256(primary_epub),
        "timing": {
            "engine": "whisper-word",
            "model": "tiny.en",
        },
        "audioSources": audio_sources,
        "timeline": "timeline.json",
        "textRoot": "text/",
        "segmentCount": len(segments),
        "sampleAligned": True,
        "alignedDocument": f"text/{matched_html}",
    }

    manifest_path = output_dir / "readalong.manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    # Install directly into book directory's readalong/ folder
    install_target = book_dir / "readalong"
    install_target.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(manifest_path, install_target / "readalong.manifest.json")
    shutil.copyfile(timeline_path, install_target / "timeline.json")
    if (install_target / "text").exists():
        shutil.rmtree(install_target / "text")
    shutil.copytree(text_dir, install_target / "text")

    return {
        "status": "success",
        "book_id": book_id,
        "matched_html": matched_html,
        "segment_count": len(segments),
        "sample_duration": sample_duration,
        "install_dir": str(install_target),
    }
