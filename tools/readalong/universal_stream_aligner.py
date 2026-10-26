"""Multi-Window Continuous Alignment Engine for Multi-Hour Single-Track Audiobooks.

Streams through long audio files (e.g. 10+ hour M4B/MP3s) in consecutive
30-minute blocks, aligns each block across all candidate EPUB HTML chapters,
and stitches the final timeline seamlessly.
"""

from collections import defaultdict
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
from bs4 import BeautifulSoup
import warnings

# Suppress XML/HTML BS4 warnings
warnings.filterwarnings("ignore")

from tools.readalong.config import (
    DEFAULT_ALIST_ROOT,
    DEFAULT_OUTPUT_DIR,
    resolve_model_path,
    resolve_nltk_data_path,
)
from tools.readalong.engine.mark_sentence import mark_sentences
from tools.readalong.exporter import READALONG_CSS_INJECTION
from tools.readalong.validator import compute_sha256
from tools.readalong.universal_aligner import safe_unzip
from tools.readalong.input_inventory import natural_sort_key, compute_strong_cache_key, model_fingerprint


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


def extract_audio_chunk(input_audio: Path, output_audio: Path, start_s: float, duration_s: float) -> float:
    """Extract a slice [start_s, start_s + duration_s] without video/data streams."""
    output_audio.parent.mkdir(parents=True, exist_ok=True)
    if output_audio.exists() and output_audio.stat().st_size > 1000:
        return get_audio_duration(output_audio)

    # Fast path: stream copy when input and output containers match
    if input_audio.suffix.lower() == output_audio.suffix.lower():
        proc = subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", str(start_s),
            "-i", str(input_audio),
            "-t", str(duration_s),
            "-map", "0:a:0",
            "-c", "copy",
            str(output_audio),
        ])
        if proc.returncode == 0 and output_audio.exists() and output_audio.stat().st_size > 1000:
            return get_audio_duration(output_audio)

    # Fallback: re-encode to mono AAC
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", str(start_s),
        "-t", str(duration_s),
        "-i", str(input_audio),
        "-map", "0:a:0", "-vn", "-sn", "-dn",
        "-c:a", "aac", "-b:a", "64k", "-ac", "1", "-ar", "24000",
        str(output_audio),
    ], check=True)
    return get_audio_duration(output_audio)


def transcribe_words_cached(chunk_audio: Path, model_path: Path, cache_json: Path, base_time_s: float) -> list[dict]:
    """Transcribe a chunk and add base_time_s offset so timestamps are global."""
    if cache_json.exists() and cache_json.stat().st_size > 50:
        try:
            return json.loads(cache_json.read_text(encoding="utf-8"))
        except Exception:
            pass

    from tools.readalong.config import resolve_transcripts_cache_dir, transcript_cache_candidates
    shared_cache = resolve_transcripts_cache_dir() / cache_json.name
    for candidate_cache in transcript_cache_candidates(cache_json.name):
      if candidate_cache.exists() and candidate_cache.stat().st_size > 50:
        try:
            words = json.loads(candidate_cache.read_text(encoding="utf-8"))
            cache_json.write_text(json.dumps(words, ensure_ascii=False, indent=2))
            return words
        except Exception:
            pass

    if os.environ.get("READALONG_CACHE_ONLY") == "1":
        raise RuntimeError(f"CACHE_MISS: {cache_json.name}")

    from tools.readalong.asr_runtime import transcription_backend
    mlx_transcribe = transcription_backend()
    res = mlx_transcribe(
        str(chunk_audio),
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
                    "start": round(base_time_s + float(w.get("start", 0.0)), 3),
                    "end": round(base_time_s + float(w.get("end", 0.0)), 3),
                })

    content = json.dumps(words, ensure_ascii=False, indent=2)
    cache_json.write_text(content)
    try:
        shared_cache.write_text(content)
    except Exception:
        pass
    return words


def get_spine_htmls(epub_path: Path) -> list[str]:
    """Get content documents in proper reading order from OPF spine."""
    with zipfile.ZipFile(epub_path) as z:
        c_xml = z.read("META-INF/container.xml")
        root = ET.fromstring(c_xml)
        opf_path = root.find(".//{*}rootfile").attrib["full-path"]
        opf_dir = str(Path(opf_path).parent)
        opf = ET.fromstring(z.read(opf_path))
        manifest = {item.attrib["id"]: item.attrib["href"] for item in opf.findall(".//{*}manifest/{*}item")}
        spine = [item.attrib["idref"] for item in opf.findall(".//{*}spine/{*}itemref")]

        spine_htmls = []
        for idref in spine:
            if idref in manifest:
                href = manifest[idref]
                full_href = f"{opf_dir}/{href}".lstrip("/") if opf_dir and opf_dir != "." else href
                if full_href.lower().endswith((".htm", ".html", ".xhtml", ".xml")):
                    spine_htmls.append(full_href)
        return spine_htmls


def align_volume_full_stream(
    book_dir: Path,
    output_dir: Path,
    block_duration_s: float = 1800.0,
    confirmed_reorders: Any = None,
) -> dict:
    """Full-length continuous stream alignment for multi-hour audiobooks."""
    from tools.readalong.candidate_safety import require_candidate_output
    require_candidate_output(book_dir, output_dir)
    if not math.isfinite(block_duration_s) or block_duration_s <= 0:
        raise ValueError("Block duration must be positive and finite")
    t_start = time.time()
    from tools.readalong.candidate_safety import source_files, alist_audio_path
    epubs = source_files(book_dir, {".epub"})
    if not epubs:
        return {"status": "skipped", "reason": "no_epub"}
    primary_epub = epubs[0]
    if len(epubs) != 1:
        return {"status": "NEEDS_REVIEW", "reason": "ambiguous_epub_pairing"}
    epub_sha = compute_sha256(primary_epub)

    audios = source_files(book_dir, {".mp3", ".m4a", ".m4b"})
    if not audios:
        return {"status": "skipped", "reason": "no_audio"}
    audios.sort(key=lambda p: natural_sort_key(p.relative_to(book_dir).as_posix()))

    work_dir = output_dir / "work"
    text_dir = output_dir / "text"
    work_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)

    model_path = resolve_model_path()
    model_sha = model_fingerprint(model_path)
    os.environ["NLTK_DATA"] = str(resolve_nltk_data_path())

    # 1. Safely extract EPUB assets into text/ preventing Zip Slip
    safe_unzip(primary_epub, text_dir, css_injection=READALONG_CSS_INJECTION)

    spine_htmls = get_spine_htmls(primary_epub)

    all_segments = []
    audio_sources = []
    category = book_dir.parent.parent.name if book_dir.parent.name.startswith("Volume") else book_dir.parent.name
    if category in ("未命名文件夹", "寒假"):
        category = "文学作品"

    # Segment original documents once, independent of track boundaries.
    from tools.readalong.stream_projection import prepare_documents, project_stream
    documents, fragments, book_tokens = prepare_documents(text_dir, spine_htmls, mark_sentences)
    ordered_audio_words = []

    for track_idx, audio_file in enumerate(audios):
        total_dur = get_audio_duration(audio_file)
        if not math.isfinite(total_dur) or total_dur <= 0:
            return {"status": "FAILED", "reason": "audio_probe_failed"}
        audio_sha = compute_sha256(audio_file)
        audio_sources.append({
            "id": audio_file.relative_to(book_dir).as_posix(),
            "name": audio_file.name,
            "alistPath": alist_audio_path(book_dir, audio_file, DEFAULT_ALIST_ROOT),
            "sha256": compute_sha256(audio_file),
            "duration": total_dur,
        })

        # Ensure 100% full temporal coverage without remainder truncation
        from tools.readalong.candidate_safety import plan_audio_blocks
        blocks = list(plan_audio_blocks(total_dur, block_duration_s))

        num_blocks = len(blocks)
        print(f"\nTrack [{track_idx + 1}/{len(audios)}]: {audio_file.name}")
        print(f"Duration: {total_dur:.1f}s ({total_dur / 3600:.2f}h) -> {num_blocks} blocks covering 0.0s to {total_dur:.1f}s")

        # Step 1: Transcribe and stitch into continuous global word stream
        global_words = []
        for b_idx, (start_s, dur_s) in enumerate(blocks):
            chunk_stem = compute_strong_cache_key(audio_sha, {
                "modelSha256": model_sha, "start": start_s, "duration": dur_s,
                "language": "en", "word_timestamps": True, "sampleRate": 24000})
            chunk_ext = audio_file.suffix.lower() if audio_file.suffix.lower() in ('.mp3', '.m4a', '.m4b', '.aac') else '.m4a'
            chunk_audio_file = work_dir / f"{chunk_stem}{chunk_ext}"
            cache_json = work_dir / f"{chunk_stem}.json"

            t_blk = time.time()
            from tools.readalong.config import transcript_cache_candidates
            cached = cache_json.is_file() or any(p.is_file() for p in transcript_cache_candidates(cache_json.name))
            if not cached and os.environ.get("READALONG_CACHE_ONLY") != "1":
                extract_audio_chunk(audio_file, chunk_audio_file, start_s, dur_s)
            chunk_words = transcribe_words_cached(chunk_audio_file, model_path, cache_json, base_time_s=start_s)
            global_words.extend(chunk_words)

        # Preserve natural track order; timestamps remain local to their source.
        global_words.sort(key=lambda word: word["start"])
        for word in global_words:
            if normalize_token(word.get("word", "")):
                ordered_audio_words.append({
                    **word, "audioSourceId": audio_file.relative_to(book_dir).as_posix(),
                })

    # One monotone book/audio correspondence, supporting unambiguous re-read occurrences.
    final_segments, projection_stats = project_stream(
        book_tokens, fragments, ordered_audio_words, confirmed_reorders=confirmed_reorders
    )
    from tools.readalong.authoritative_validator import safe_path
    for name, soup in documents.items():
        safe_path(text_dir, name).write_text(str(soup), encoding="utf-8")
    (output_dir / "projection.json").write_text(
        json.dumps(projection_stats, ensure_ascii=False, indent=2) + "\n")

    from tools.readalong.timeline_boundaries import resolve_boundaries
    final_segments, boundary_repairs = resolve_boundaries(final_segments)
    projection_stats["boundaryRepairs"] = boundary_repairs
    (output_dir / "projection.json").write_text(
        json.dumps(projection_stats, ensure_ascii=False, indent=2) + "\n")

    # Save timeline.json
    if compute_sha256(primary_epub) != epub_sha or model_fingerprint(model_path) != model_sha:
        raise RuntimeError("EPUB or model changed during generation")
    timeline_path = output_dir / "timeline.json"
    timeline_path.write_text(json.dumps(final_segments, ensure_ascii=False, indent=2) + "\n")

    # Build manifest
    book_id = re.sub(r"[^\w\s-]", "", book_dir.name.lower()).replace(" ", "-")
    first_doc = final_segments[0]["document"] if final_segments else ""

    manifest = {
        "schemaVersion": 1,
        "bookId": book_id,
        "language": "en",
        "sourceEpubSha256": epub_sha,
        "timing": {
            "engine": "whisper-word-global-monotone-exact-v1",
            "model": model_path.name,
            "modelSha256": model_sha,
        },
        "audioSources": audio_sources,
        "timeline": "timeline.json",
        "textRoot": "text/",
        "segmentCount": len(final_segments),
        "sampleAligned": False,
        "alignedDocument": first_doc,
    }

    manifest_path = output_dir / "readalong.manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    # Authoritative certification of staging candidate (never overwrite active directly)
    from tools.readalong.controlled_publisher import certify_staging_candidate
    cert = certify_staging_candidate(output_dir, book_dir=book_dir)
    print(f"\nCandidate certification verdict: {cert.get('status')}")
    print(f"[Controlled Staging] Output preserved in isolated staging: {output_dir}")

    elapsed_total = time.time() - t_start
    total_hours = sum(source["duration"] for source in audio_sources) / 3600
    print(f"\nCandidate generated: {book_dir.name}: {len(final_segments)} segments across {total_hours:.1f}h; verdict={cert['status']}; elapsed={elapsed_total:.1f}s\n")

    return {
        "status": cert["status"],
        "book_id": book_id,
        "segment_count": len(final_segments),
        "elapsed_seconds": round(elapsed_total, 2),
        "staging_dir": str(output_dir),
        "certification": cert,
    }
