"""High-precision per-track alignment for audiobooks with multiple audio files or version divergence."""

from difflib import SequenceMatcher
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import quote
import xml.etree.ElementTree as ET
import zipfile
from bs4 import BeautifulSoup

from tools.readalong.config import (
    DEFAULT_ALIST_ROOT,
    DEFAULT_OUTPUT_DIR,
    resolve_nltk_data_path,
)
from tools.readalong.engine.mark_sentence import mark_sentences
from tools.readalong.exporter import READALONG_CSS_INJECTION
from tools.readalong.validator import compute_sha256, validate_overlay_epub


def normalize_token(w: str) -> str:
    return re.sub(r"[^a-z0-9]", "", w.lower())


def get_mp3_durations(mp3_files: list[Path]) -> list[float]:
    durations = []
    for f in mp3_files:
        raw = subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=nw=1:nk=1", str(f)
        ]).decode().strip()
        durations.append(float(raw))
    return durations


def extract_track_words(run_dir: Path, mp3_durations: list[float]) -> list[list[dict]]:
    """Extract words partitioned per original audio track with relative timestamps."""
    all_words = []
    for jf in sorted(run_dir.glob("0*.json")):
        idx = int(jf.stem)
        base_time = idx * 600.0
        data = json.load(jf.open(encoding="utf-8"))
        for seg in data.get("segments", []):
            for w in seg.get("words", []):
                start = base_time + w.get("start", 0.0)
                end = base_time + w.get("end", 0.0)
                norm = normalize_token(w.get("word", ""))
                if norm:
                    all_words.append({
                        "word": w.get("word", "").strip(),
                        "norm": norm,
                        "start": round(start, 3),
                        "end": round(end, 3),
                    })

    tracks_words = []
    current_offset = 0.0
    for dur in mp3_durations:
        track_end = current_offset + dur
        track_w = []
        for w in all_words:
            if current_offset <= w["start"] < track_end:
                track_w.append({
                    "word": w["word"],
                    "norm": w["norm"],
                    "start": round(w["start"] - current_offset, 3),
                    "end": round(min(dur, w["end"] - current_offset), 3),
                })
        tracks_words.append(track_w)
        current_offset += dur

    return tracks_words


def align_chapter_html(
    html_content: str,
    chapter_id: str,
    track_words: list[dict],
    doc_rel_path: str,
    audio_source_id: str,
    start_audio_ptr: int = 0,
) -> tuple[str, list[dict], int]:
    """Segment HTML, align to track words monotonically, and return (marked_html, segments, end_ptr)."""
    marked_html = mark_sentences(html_content, chapter_id=chapter_id)
    soup = BeautifulSoup(marked_html, "lxml")

    # Inject readalong CSS if not present
    if "</head>" in marked_html and ".readalong-active" not in marked_html:
        marked_html = marked_html.replace("</head>", f"<style>{READALONG_CSS_INJECTION}</style></head>", 1)

    spans = [
        s for s in soup.find_all("span")
        if s.get("id", "").startswith(f"c{chapter_id}-segment") or s.get("id", "").startswith(f"{chapter_id}-segment")
    ]

    audio_norms = [w["norm"] for w in track_words]
    audio_ptr = start_audio_ptr
    segments = []

    for span in spans:
        text = span.get_text().strip()
        tokens = [normalize_token(w) for w in text.split()]
        tokens = [t for t in tokens if t]
        if not tokens:
            continue

        # Skip isolated Roman numerals or numbers (e.g. "1.", "I.")
        if len(tokens) < 2 and tokens[0] in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "i", "ii", "iii", "a", "b", "c"):
            continue

        # Lookahead search in sliding window
        window_end = min(len(audio_norms), audio_ptr + 350)
        sub_audio = audio_norms[audio_ptr:window_end]

        matcher = SequenceMatcher(None, tokens, sub_audio)
        match = matcher.find_longest_match(0, len(tokens), 0, len(sub_audio))

        # Precision match rule preventing false jumps
        is_valid_match = False
        if len(tokens) <= 3:
            if match.size == len(tokens) and match.b < 40:
                is_valid_match = True
        else:
            if match.b > 50:
                is_valid_match = (match.size >= 4)
            else:
                is_valid_match = (match.size >= 3) or (match.size >= len(tokens) * 0.5)

        if is_valid_match:
            abs_match_start = audio_ptr + match.b
            abs_match_end = audio_ptr + match.b + match.size - 1
            seg_start = track_words[abs_match_start]["start"]
            seg_end = track_words[abs_match_end]["end"]
            if seg_end <= seg_start:
                seg_end = round(seg_start + 0.1, 3)

            segments.append({
                "audioSourceId": audio_source_id,
                "start": seg_start,
                "end": seg_end,
                "document": f"text/{doc_rel_path}",
                "fragment": span["id"],
                "text": text,
                "reviewStatus": "unreviewed",
            })
            audio_ptr = abs_match_end + 1

    return marked_html, segments, audio_ptr


def align_talking_to_strangers(
    book_dir: Path,
    output_dir: Path | None = None,
) -> dict:
    from tools.readalong.candidate_safety import retired_write_entrypoint
    retired_write_entrypoint()
    """End-to-end alignment specifically for Talking to Strangers with 13 audio tracks."""
    os.environ["NLTK_DATA"] = str(resolve_nltk_data_path())
    out_base = output_dir or (DEFAULT_OUTPUT_DIR / "talking-to-strangers-what-we-should-know-about-the-people-we-dont-know-malcom-gladwell")
    work_dir = out_base / "work"
    run_dir = work_dir / "run"
    text_dir = out_base / "text"
    text_dir.mkdir(parents=True, exist_ok=True)

    mp3_files = sorted([f for f in book_dir.glob("*.mp3") if not f.name.startswith("._")])
    if len(mp3_files) != 13:
        raise ValueError(f"Expected 13 MP3 tracks, found {len(mp3_files)}")

    epub_files = list(book_dir.glob("*.epub"))
    if not epub_files:
        raise ValueError("No EPUB found in book directory")
    source_epub = epub_files[0]

    mp3_durations = get_mp3_durations(mp3_files)
    track_words_list = extract_track_words(run_dir, mp3_durations)

    # Spine mapping for Talking to Strangers
    spine_mapping = [
        [("s007-Chapter-001.xhtml", "c001")],
        [("s008-Part-001.xhtml", "c001p"), ("s009-Chapter-002.xhtml", "c002")],
        [("s010-Chapter-003.xhtml", "c003")],
        [("s011-Part-002.xhtml", "c002p"), ("s012-Chapter-004.xhtml", "c004")],
        [("s013-Chapter-005.xhtml", "c005")],
        [("s014-Chapter-006.xhtml", "c006")],
        [("s015-Part-003.xhtml", "c003p"), ("s016-Chapter-007.xhtml", "c007")],
        [("s017-Chapter7-hbg-001.xhtml", "c008")],
        [("s018-Chapter-008.xhtml", "c009")],
        [("s019-Part-004.xhtml", "c004p"), ("s020-Chapter-009.xhtml", "c010")],
        [("s021-Part-005.xhtml", "c005p"), ("s022-Chapter-010.xhtml", "c011")],
        [("s023-Chapter-011.xhtml", "c012")],
        [("s024-Chapter-012.xhtml", "c013")],
    ]

    # 1. Extract all original EPUB assets into text_dir
    with zipfile.ZipFile(source_epub) as z:
        for name in z.namelist():
            if name.endswith("/"):
                continue
            dest = text_dir / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(z.read(name))

    # 2. Process each track and its corresponding HTML chapters directly from source EPUB
    all_segments = []
    aligned_html_map = {}

    with zipfile.ZipFile(source_epub) as z:
        for track_idx, (mp3_file, html_targets) in enumerate(zip(mp3_files, spine_mapping)):
            track_words = track_words_list[track_idx]
            audio_source_id = mp3_file.name
            audio_ptr = 0

            for html_rel_name, chapter_id in html_targets:
                full_html_path = f"OEBPS/Text/{html_rel_name}"
                raw_html = z.read(full_html_path).decode("utf-8")

                marked_html, segs, audio_ptr = align_chapter_html(
                    html_content=raw_html,
                    chapter_id=chapter_id,
                    track_words=track_words,
                    doc_rel_path=full_html_path,
                    audio_source_id=audio_source_id,
                    start_audio_ptr=audio_ptr,
                )

                # Overwrite text file with freshly marked HTML
                (text_dir / full_html_path).write_text(marked_html, encoding="utf-8")
                all_segments.extend(segs)
                aligned_html_map[full_html_path] = segs
                print(f"Track {track_idx + 1} ({mp3_file.name[:12]}...): aligned {len(segs)} segments in {html_rel_name}")

    # Sort segments strictly by (audioSourceId, start, end)
    all_segments.sort(key=lambda s: (s["audioSourceId"], s["start"], s["end"]))

    # 3. Write timeline.json
    timeline_path = out_base / "timeline.json"
    timeline_path.write_text(json.dumps(all_segments, ensure_ascii=False, indent=2) + "\n")

    # 4. Write readalong.manifest.json
    audio_sources_meta = []
    parts = book_dir.parts
    idx = parts.index("有声书") if "有声书" in parts else -1
    rel_book_dir = "/".join(parts[idx + 1:]) if idx >= 0 else book_dir.name

    for i, mp3 in enumerate(mp3_files):
        audio_sources_meta.append({
            "id": mp3.name,
            "name": mp3.name,
            "alistPath": f"{DEFAULT_ALIST_ROOT}/{rel_book_dir}/{mp3.name}",
            "sha256": compute_sha256(mp3),
            "duration": mp3_durations[i],
        })

    chapters_meta = [
        {"title": "Introduction", "track": mp3_files[0].name},
        {"title": "Chapter 1: Fidel Castro's Revenge", "track": mp3_files[1].name},
        {"title": "Chapter 2: Getting to Know der Führer", "track": mp3_files[2].name},
        {"title": "Chapter 3: The Queen of Cuba", "track": mp3_files[3].name},
        {"title": "Chapter 4: The Holy Fool", "track": mp3_files[4].name},
        {"title": "Chapter 5: Case Study: The Boy in the Shower", "track": mp3_files[5].name},
        {"title": "Chapter 6: The Friends Fallacy", "track": mp3_files[6].name},
        {"title": "Chapter 7: The Amanda Knox Case", "track": mp3_files[7].name},
        {"title": "Chapter 8: Case Study: The Fraternity Party", "track": mp3_files[8].name},
        {"title": "Chapter 9: KSM: What Happens When the Stranger Is a Terrorist?", "track": mp3_files[9].name},
        {"title": "Chapter 10: Sylvia Plath", "track": mp3_files[10].name},
        {"title": "Chapter 11: Case Study: The Kansas City Experiments", "track": mp3_files[11].name},
        {"title": "Chapter 12: Sandra Bland", "track": mp3_files[12].name},
    ]

    manifest = {
        "schemaVersion": 1,
        "bookId": "talking-to-strangers-what-we-should-know-about-the-people-we-dont-know-malcom-gladwell",
        "language": "en",
        "sourceEpubSha256": compute_sha256(source_epub),
        "timing": {
            "engine": "whisper-word",
            "model": "tiny.en",
        },
        "audioSources": audio_sources_meta,
        "timeline": "timeline.json",
        "textRoot": "text/",
        "segmentCount": len(all_segments),
        "chapters": chapters_meta,
    }

    manifest_path = out_base / "readalong.manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    return {
        "book_id": manifest["bookId"],
        "segment_count": len(all_segments),
        "timeline_path": str(timeline_path),
        "manifest_path": str(manifest_path),
        "output_dir": str(out_base),
    }
