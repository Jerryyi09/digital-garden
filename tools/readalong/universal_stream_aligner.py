"""Multi-Window Continuous Alignment Engine for Multi-Hour Single-Track Audiobooks.

Streams through long audio files (e.g. 10+ hour M4B/MP3s) in consecutive
30-minute blocks, aligns each block across all candidate EPUB HTML chapters,
and stitches the final timeline seamlessly.
"""

from collections import defaultdict
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

    from mlx_whisperx.backend.mlx_whisper.transcribe import transcribe as mlx_transcribe
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

    cache_json.write_text(json.dumps(words, ensure_ascii=False, indent=2))
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
) -> dict:
    """Full-length continuous stream alignment for multi-hour audiobooks."""
    t_start = time.time()
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
    audios.sort(key=lambda p: p.name)

    work_dir = output_dir / "work"
    text_dir = output_dir / "text"
    work_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)

    model_path = resolve_model_path()
    os.environ["NLTK_DATA"] = str(resolve_nltk_data_path())

    # 1. Unzip EPUB assets into text/
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

    spine_htmls = get_spine_htmls(primary_epub)

    all_segments = []
    audio_sources = []
    category = book_dir.parent.parent.name if book_dir.parent.name.startswith("Volume") else book_dir.parent.name
    if category in ("未命名文件夹", "寒假"):
        category = "文学作品"

    # Pre-index tokens for all candidate spine HTMLs
    html_token_cache = {}
    with zipfile.ZipFile(primary_epub) as z:
        for h in spine_htmls:
            try:
                raw_html = z.read(h).decode("utf-8", errors="replace")
                soup = BeautifulSoup(raw_html, "html.parser")
                text = " ".join(soup.get_text().split())
                tokens = [normalize_token(w) for w in text.split()]
                tokens = [t for t in tokens if t]
                if len(tokens) >= 10:
                    html_token_cache[h] = tokens
            except Exception:
                pass

    print(f"\n=======================================================")
    print(f"Aligning Full Stream: {book_dir.name}")
    print(f"Total audio tracks: {len(audios)} | Total EPUB spine HTMLs: {len(html_token_cache)}")
    print(f"=======================================================")

    for track_idx, audio_file in enumerate(audios):
        total_dur = get_audio_duration(audio_file)
        audio_sources.append({
            "id": audio_file.name,
            "name": audio_file.name,
            "alistPath": f"{DEFAULT_ALIST_ROOT}/{category}/{book_dir.parent.name}/{book_dir.name}/{audio_file.name}" if book_dir.parent.name.startswith("Great Mental") else f"{DEFAULT_ALIST_ROOT}/{category}/{book_dir.name}/{audio_file.name}",
            "sha256": compute_sha256(audio_file),
            "duration": total_dur,
        })

        num_blocks = max(1, int(total_dur // block_duration_s) + (1 if total_dur % block_duration_s > 30 else 0))
        print(f"\nTrack [{track_idx + 1}/{len(audios)}]: {audio_file.name}")
        print(f"Duration: {total_dur:.1f}s ({total_dur / 3600:.2f}h) -> {num_blocks} blocks of {block_duration_s/60:.0f} mins")

        for b_idx in range(num_blocks):
            start_s = b_idx * block_duration_s
            dur_s = min(block_duration_s, total_dur - start_s)
            if dur_s < 10.0:
                continue

            chunk_stem = f"{audio_file.stem}_blk{b_idx:03d}_{int(start_s)}"
            chunk_m4a = work_dir / f"{chunk_stem}.m4a"
            cache_json = work_dir / f"{chunk_stem}.json"

            t_blk_start = time.time()
            extract_audio_chunk(audio_file, chunk_m4a, start_s, dur_s)
            chunk_words = transcribe_words_cached(chunk_m4a, model_path, cache_json, base_time_s=start_s)
            t_trans = time.time() - t_blk_start

            if not chunk_words:
                continue

            chunk_norms = [w["norm"] for w in chunk_words]

            # 1. Identify ALL matching HTML chapters inside this audio block
            matched_html_candidates = []
            for h_file, h_tokens in html_token_cache.items():
                m = SequenceMatcher(None, h_tokens, chunk_norms).find_longest_match(0, len(h_tokens), 0, len(chunk_norms))
                if m.size >= 12:
                    matched_html_candidates.append((h_file, m.size, m.b))

            if not matched_html_candidates:
                print(f"  Block #{b_idx+1}/{num_blocks} [{start_s/60:.0f}~{(start_s+dur_s)/60:.0f}m]: Transcribed {len(chunk_words)}w ({t_trans:.1f}s) | No chapter matches found.")
                continue

            # Sort matched chapters by their appearance in the audio stream (m.b)
            matched_html_candidates.sort(key=lambda x: x[2])
            block_aligned_count = 0

            # 2. Align each matched chapter HTML within this block
            for h_file, match_size, approx_b in matched_html_candidates:
                target_dest = text_dir / h_file
                raw_content = target_dest.read_text(encoding="utf-8")
                doc_id = re.sub(r"[^a-zA-Z0-9]", "", f"{Path(h_file).stem}")[:8] or "doc"

                if "segment" not in raw_content:
                    marked_html = mark_sentences(raw_content, chapter_id=doc_id)
                    target_dest.write_text(marked_html, encoding="utf-8")
                else:
                    marked_html = raw_content

                soup = BeautifulSoup(marked_html, "html.parser")
                spans = [s for s in soup.find_all("span") if s.get("id") and "segment" in s["id"]]

                audio_ptr = max(0, approx_b - 20)
                # Refine anchor search around approx_b
                for span in spans[:15]:
                    t_toks = [normalize_token(w) for w in span.get_text().split() if normalize_token(w)]
                    if len(t_toks) >= 3:
                        init_m = SequenceMatcher(None, t_toks, chunk_norms).find_longest_match(0, len(t_toks), audio_ptr, min(len(chunk_norms), audio_ptr + 400))
                        if init_m.size >= min(4, len(t_toks)):
                            audio_ptr = max(0, init_m.b - 5)
                            break

                chapter_segs = []
                for span in spans:
                    text = span.get_text().strip()
                    tokens = [normalize_token(w) for w in text.split() if normalize_token(w)]
                    if len(tokens) < 2:
                        continue

                    window_end = min(len(chunk_norms), audio_ptr + 1500)
                    sub_audio = chunk_norms[audio_ptr:window_end]

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
                        abs_start = chunk_words[audio_ptr + match.b]["start"]
                        abs_end = chunk_words[audio_ptr + match.b + match.size - 1]["end"]
                        if abs_end <= abs_start:
                            abs_end = round(abs_start + 0.1, 3)

                        chapter_segs.append({
                            "audioSourceId": audio_file.name,
                            "start": abs_start,
                            "end": abs_end,
                            "document": f"text/{h_file}",
                            "fragment": span["id"],
                            "text": text,
                            "reviewStatus": "unreviewed",
                        })
                        audio_ptr = audio_ptr + match.b + match.size

                if chapter_segs:
                    all_segments.extend(chapter_segs)
                    block_aligned_count += len(chapter_segs)

            print(f"  Block #{b_idx+1}/{num_blocks} [{start_s/60:.0f}~{(start_s+dur_s)/60:.0f}m]: Transcribed {len(chunk_words)}w ({t_trans:.1f}s) | Aligned {block_aligned_count} segs across {len(matched_html_candidates)} chapters!")

    # De-duplicate any segments by fragment and sort monotonically
    dedup_map = {}
    for s in all_segments:
        key = (s["audioSourceId"], s["fragment"])
        if key not in dedup_map or s["start"] < dedup_map[key]["start"]:
            dedup_map[key] = s

    final_segments = sorted(dedup_map.values(), key=lambda s: (s["audioSourceId"], s["start"], s["end"]))

    # Save timeline.json
    timeline_path = output_dir / "timeline.json"
    timeline_path.write_text(json.dumps(final_segments, ensure_ascii=False, indent=2) + "\n")

    # Build manifest
    book_id = re.sub(r"[^\w\s-]", "", book_dir.name.lower()).replace(" ", "-")
    first_doc = final_segments[0]["document"] if final_segments else ""

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
        "segmentCount": len(final_segments),
        "sampleAligned": False,
        "alignedDocument": first_doc,
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

    elapsed_total = time.time() - t_start
    print(f"\n✓ Completed {book_dir.name}: {len(final_segments)} segments across {total_dur/3600:.1f}h in {elapsed_total:.1f}s ({elapsed_total/60:.1f} mins)!\n")

    return {
        "status": "success",
        "book_id": book_id,
        "segment_count": len(final_segments),
        "elapsed_seconds": round(elapsed_total, 2),
        "install_dir": str(install_target),
    }
