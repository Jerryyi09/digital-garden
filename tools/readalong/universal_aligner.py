"""Universal, divergence-tolerant readalong aligner for library collections."""

from difflib import SequenceMatcher
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Any
import xml.etree.ElementTree as ET
import zipfile
import warnings
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

from tools.readalong.config import (
    DEFAULT_ALIST_ROOT,
    DEFAULT_OUTPUT_DIR,
    resolve_model_path,
    resolve_nltk_data_path,
)
from tools.readalong.engine.mark_sentence import mark_sentences
from tools.readalong.exporter import READALONG_CSS_INJECTION
from tools.readalong.validator import compute_sha256, validate_overlay_epub
from tools.readalong.input_inventory import natural_sort_key, compute_strong_cache_key, safe_extract_epub, model_fingerprint


def safe_unzip(zip_path: Path, target_dir: Path, css_injection=None) -> list[str]:
    """Use the shared bounded extractor; stylesheet changes affect candidates only."""
    extracted = safe_extract_epub(zip_path, target_dir)
    for name in extracted:
        path = target_dir / name
        if path.suffix.lower() in (".htm", ".html", ".xhtml"):
            html = path.read_text(encoding="utf-8", errors="strict")
            if css_injection and "</head>" in html and ".readalong-active" not in html:
                html = html.replace("</head>", f"<style>{css_injection}</style></head>", 1)
                path.write_text(html, encoding="utf-8")
    return extracted


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
    """Extract first N seconds of audio safely without video streams, using atomic write."""
    dur = get_audio_duration(input_audio)
    # If audio is already shorter than duration_seconds, direct use is safe
    if 0.0 < dur <= duration_seconds:
        return dur

    output_audio.parent.mkdir(parents=True, exist_ok=True)
    if output_audio.exists() and output_audio.stat().st_size > 0:
        sample_dur = get_audio_duration(output_audio)
        if sample_dur > 0:
            return sample_dur
        # Corrupted sample, remove and re-extract
        output_audio.unlink(missing_ok=True)

    tmp_out = output_audio.with_suffix(f".tmp_{os.getpid()}_{output_audio.suffix}")
    try:
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(input_audio), "-t", str(duration_seconds),
            "-map", "0:a:0", "-vn", "-sn", "-dn",
            "-c:a", "aac", "-b:a", "64k", "-ac", "1", "-ar", "24000",
            str(tmp_out),
        ], check=True)
        tmp_out.replace(output_audio)
    finally:
        tmp_out.unlink(missing_ok=True)

    return get_audio_duration(output_audio)


def transcribe_words(audio_path: Path, model_path: Path) -> list[dict]:
    """Transcribe audio with word-level timestamps."""
    from tools.readalong.asr_runtime import transcription_backend
    mlx_transcribe = transcription_backend()
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
    max_sample_seconds: float = 1800.0,
    max_tracks: int | None = None,
    confirmed_reorders: Any = None,
) -> dict:
    """Universal alignment for an audiobook across all chapters/tracks."""
    from tools.readalong.candidate_safety import require_candidate_output
    require_candidate_output(book_dir, output_dir)
    if not math.isfinite(max_sample_seconds) or max_sample_seconds <= 0:
        raise ValueError("Sample duration must be finite and positive")
    from tools.readalong.candidate_safety import source_files, alist_audio_path
    epubs = source_files(book_dir, {".epub"})
    if not epubs:
        return {"status": "skipped", "reason": "no_epub"}

    primary_epub = epubs[0]
    if len(epubs) != 1:
        return {"status": "NEEDS_REVIEW", "reason": "ambiguous_epub_pairing"}
    audios = source_files(book_dir, {".mp3", ".m4a", ".m4b"})
    if not audios:
        return {"status": "skipped", "reason": "no_audio"}

    # Sort audios naturally by name using natural numeric sorting
    audios.sort(key=lambda p: natural_sort_key(p.relative_to(book_dir).as_posix()))
    if max_tracks:
        audios = audios[:max_tracks]

    work_dir = output_dir / "work"
    text_dir = output_dir / "text"
    work_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)

    model_path = resolve_model_path()
    model_sha = model_fingerprint(model_path)
    os.environ["NLTK_DATA"] = str(resolve_nltk_data_path())

    # 1. Safely extract all original EPUB assets into text/ preventing Zip Slip
    safe_unzip(primary_epub, text_dir, css_injection=READALONG_CSS_INJECTION)

    all_segments = []
    audio_sources = []
    category = book_dir.parent.name
    if category in ("未命名文件夹", "寒假"):
        category = "文学作品"

    from tools.readalong.stream_projection import prepare_documents, project_stream
    from tools.readalong.universal_stream_aligner import get_spine_htmls
    from tools.readalong.authoritative_validator import safe_path
    from tools.readalong.config import resolve_transcripts_cache_dir

    spine_htmls = get_spine_htmls(primary_epub)
    documents, fragments, book_tokens = prepare_documents(text_dir, spine_htmls, mark_sentences)
    ordered_audio_words = []

    # Track-by-track alignment across all audio files in the book
    for track_idx, audio_file in enumerate(audios):
        track_claimed_frags = set()
        print(f"  --> Aligning track [{track_idx + 1}/{len(audios)}]: {audio_file.name}")
        dur = get_audio_duration(audio_file)
        if not math.isfinite(dur) or dur <= 0:
            return {"status": "FAILED", "reason": "audio_probe_failed"}
        audio_sha = compute_sha256(audio_file)
        cache_key = compute_strong_cache_key(audio_sha, {"modelSha256": model_sha,
            "language": "en", "word_timestamps": True, "max_sample": max_sample_seconds})
        if 0 < dur <= max_sample_seconds:
            transcribe_target = audio_file
        else:
            sample_m4a = work_dir / f"sample_{cache_key}.m4a"
            extract_audio_sample(audio_file, sample_m4a, duration_seconds=max_sample_seconds)
            transcribe_target = sample_m4a

        # Strong cache key incorporating file content hash and alignment parameters
        transcript_cache = work_dir / f"transcript_{audio_file.stem}_{cache_key[:12]}.json"
        audio_words = None
        if transcript_cache.exists():
            try:
                audio_words = json.loads(transcript_cache.read_text(encoding="utf-8"))
            except Exception:
                audio_words = None

        if audio_words is None:
            from tools.readalong.config import transcript_cache_candidates
            for shared_cache in transcript_cache_candidates(transcript_cache.name):
              if shared_cache.exists() and shared_cache.stat().st_size > 50:
                try:
                    audio_words = json.loads(shared_cache.read_text(encoding="utf-8"))
                    transcript_cache.write_text(json.dumps(audio_words, ensure_ascii=False, indent=2))
                    break
                except Exception:
                    audio_words = None

        if audio_words is None:
            if os.environ.get("READALONG_CACHE_ONLY") == "1":
                raise RuntimeError(f"CACHE_MISS: {transcript_cache.name}")
            try:
                audio_words = transcribe_words(transcribe_target, model_path)
                content = json.dumps(audio_words, ensure_ascii=False, indent=2)
                transcript_cache.write_text(content)
                try:
                    (resolve_transcripts_cache_dir() / transcript_cache.name).write_text(content)
                except Exception:
                    pass
            except Exception as e:
                raise RuntimeError(f"ASR_TRANSCRIPTION_FAILED: {audio_file.name}: {e}") from e

        audio_sources.append({
            "id": audio_file.relative_to(book_dir).as_posix(),
            "name": audio_file.name,
            "alistPath": alist_audio_path(book_dir, audio_file, DEFAULT_ALIST_ROOT),
            "sha256": compute_sha256(audio_file),
            "duration": get_audio_duration(audio_file),
        })

        if not audio_words:
            print(f"      (No transcription words for {audio_file.name}, skipping segments)")
            continue

        track_id = audio_file.relative_to(book_dir).as_posix()
        for w in audio_words:
            if normalize_token(w.get("word", "")):
                ordered_audio_words.append({**w, "audioSourceId": track_id})

    final_segments, projection_stats = project_stream(
        book_tokens, fragments, ordered_audio_words, confirmed_reorders=confirmed_reorders
    )

    for name, soup in documents.items():
        safe_path(text_dir, name).write_text(str(soup), encoding="utf-8")
    (output_dir / "projection.json").write_text(
        json.dumps(projection_stats, ensure_ascii=False, indent=2) + "\n"
    )

    all_segments = final_segments

    # Sort all segments
    all_segments.sort(key=lambda s: (s["audioSourceId"], s["start"], s["end"]))

    from tools.readalong.timeline_boundaries import resolve_boundaries
    all_segments, boundary_repairs = resolve_boundaries(all_segments)
    projection_stats["boundaryRepairs"] = boundary_repairs
    (output_dir / "projection.json").write_text(
        json.dumps(projection_stats, ensure_ascii=False, indent=2) + "\n")

    # Save timeline.json
    timeline_path = output_dir / "timeline.json"
    timeline_path.write_text(json.dumps(all_segments, ensure_ascii=False, indent=2) + "\n")

    # Build manifest
    book_id = re.sub(r"[^\w\s-]", "", book_dir.name.lower()).replace(" ", "-")
    first_doc = all_segments[0]["document"] if all_segments else ""

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
        "segmentCount": len(all_segments),
        "sampleAligned": any(s["duration"] > max_sample_seconds for s in audio_sources),
        "alignedDocument": first_doc,
    }

    from tools.readalong.controlled_publisher import certify_staging_candidate

    manifest_path = output_dir / "readalong.manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    # Authoritative certification of staging candidate
    cert = certify_staging_candidate(output_dir, book_dir=book_dir)
    print(f"      Candidate certification verdict: {cert.get('status')}")

    return {
        "status": cert["status"],
        "book_id": book_id,
        "tracks_processed": len(audios),
        "segment_count": len(all_segments),
        "staging_dir": str(output_dir),
        "certification": cert,
    }
