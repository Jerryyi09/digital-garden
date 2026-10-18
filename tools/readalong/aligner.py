"""Single book alignment orchestrator."""

import json
import os
from pathlib import Path
import subprocess
import sys
import time

from tools.readalong.config import (
    DEFAULT_ALIST_ROOT,
    DEFAULT_OUTPUT_DIR,
    resolve_model_path,
    resolve_nltk_data_path,
)
from tools.readalong.exporter import export_readalong_bundle
from tools.readalong.scanner import inspect_book_dir
from tools.readalong.validator import compute_sha256, validate_overlay_epub


def extract_sample_audio(
    source_audio: Path,
    output_audio: Path,
    start_time: float,
    end_time: float,
) -> None:
    """Extract a slice of audio for bounded sample validation."""
    output_audio.parent.mkdir(parents=True, exist_ok=True)
    if output_audio.exists() and output_audio.stat().st_size > 0:
        return

    duration = end_time - start_time
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
        "-ss", str(start_time), "-i", str(source_audio),
        "-t", str(duration), "-map", "0:a:0", "-vn",
        "-map_metadata", "-1", "-map_chapters", "-1",
        "-c:a", "aac", "-b:a", "64k", "-ac", "1", "-ar", "24000",
        str(output_audio),
    ], check=True)


def combine_audio_files(audio_files: list[Path], output_audio: Path) -> list[dict]:
    """Concatenate multiple audio files into a single pipeline audio and return source offsets."""
    output_audio.parent.mkdir(parents=True, exist_ok=True)
    offsets = []
    current_time = 0.0

    for f in audio_files:
        raw = subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=nw=1:nk=1", str(f)
        ])
        dur = float(raw.strip())
        offsets.append({
            "id": f.name,
            "path": str(f),
            "duration": dur,
            "start_offset": current_time,
            "end_offset": current_time + dur,
        })
        current_time += dur

    if not output_audio.exists() or output_audio.stat().st_size == 0:
        concat_list = output_audio.with_suffix(".txt")
        with concat_list.open("w", encoding="utf-8") as handle:
            for f in audio_files:
                handle.write(f"file '{f.resolve()}'\n")

        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-vn", "-c:a", "aac", "-b:a", "64k", "-ac", "1", "-ar", "24000",
            str(output_audio),
        ], check=True)
        if concat_list.exists():
            concat_list.unlink()

    return offsets


def align_book(
    book_dir: Path,
    language: str = "en",
    timing: str = "whisper-word",
    resume: bool = True,
    sample: str | None = None,
    output_dir: Path | None = None,
    model_path: Path | None = None,
    chunk_seconds: int = 600,
) -> dict:
    """Run full readalong alignment for a single book."""
    started_time = time.time()
    info = inspect_book_dir(book_dir)
    if info["pairing_status"] != "paired":
        raise ValueError(
            f"Cannot align book in {book_dir}: pairing status is {info['pairing_status']}"
        )

    primary_epub = Path(info["primary_epub"])
    primary_audio = Path(info["primary_audio"])
    audios = [Path(p) for p in info["audios"]]
    book_id = info["book_id"]

    out_base = output_dir or (DEFAULT_OUTPUT_DIR / book_id)
    work_dir = out_base / "work"
    generated_dir = out_base / "generated"
    work_dir.mkdir(parents=True, exist_ok=True)
    generated_dir.mkdir(parents=True, exist_ok=True)

    resolved_model = resolve_model_path(str(model_path) if model_path else None)
    resolved_nltk = resolve_nltk_data_path()

    os.environ["NLTK_DATA"] = str(resolved_nltk)
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["OMP_NUM_THREADS"] = "4"

    source_offset = 0.0
    audio_for_pipeline = primary_audio
    chapters_meta = []
    audio_sources_meta = None

    if len(audios) > 1 and not sample:
        # Multi-audiobook: concatenate seamlessly for alignment pipeline
        combined_audio = work_dir / "combined_audio.m4a"
        audio_offsets = combine_audio_files(audios, combined_audio)
        audio_for_pipeline = combined_audio
        audio_sources_meta = []

        for item in audio_offsets:
            p = Path(item["path"])
            try:
                parts = p.parts
                if "有声书" in parts:
                    idx = parts.index("有声书")
                    rel_from_root = "/".join(parts[idx + 1:])
                    src_alist_path = f"{DEFAULT_ALIST_ROOT}/{rel_from_root}"
                else:
                    src_alist_path = f"{DEFAULT_ALIST_ROOT}/{book_dir.name}/{p.name}"
            except Exception:
                src_alist_path = f"{DEFAULT_ALIST_ROOT}/{p.name}"

            audio_sources_meta.append({
                "id": p.name,
                "path": str(p),
                "alistPath": src_alist_path,
                "duration": item["duration"],
                "start_offset": item["start_offset"],
                "end_offset": item["end_offset"],
                "sha256": compute_sha256(p),
            })
            chapters_meta.append({
                "title": p.stem,
                "start": item["start_offset"],
                "end": item["end_offset"],
            })
    else:
        # Single audio (or sample mode)
        audio_probe = info["audio_info"][0]["probe"]
        all_chapters = audio_probe.get("chapters", [])

        if sample:
            sample_title = sample.lower()
            matched_chap = next(
                (c for c in all_chapters if sample_title in c.get("title", "").lower()),
                None
            )
            if not matched_chap and all_chapters:
                matched_chap = all_chapters[0]

            if matched_chap:
                sample_m4a = work_dir / f"sample_{sample_title}.m4a"
                extract_sample_audio(
                    primary_audio, sample_m4a,
                    matched_chap["start"], matched_chap["end"]
                )
                audio_for_pipeline = sample_m4a
                source_offset = matched_chap["start"]
                chapters_meta.append({
                    "title": matched_chap["title"],
                    "start": matched_chap["start"],
                    "end": matched_chap["end"],
                })
        else:
            chapters_meta = all_chapters

    # Compute AList path for primary audio
    try:
        parts = book_dir.parts
        if "有声书" in parts:
            idx = parts.index("有声书")
            rel_from_root = "/".join(parts[idx + 1:])
            alist_audio_path = f"{DEFAULT_ALIST_ROOT}/{rel_from_root}/{primary_audio.name}"
        else:
            alist_audio_path = f"{DEFAULT_ALIST_ROOT}/{book_dir.name}/{primary_audio.name}"
    except Exception:
        alist_audio_path = f"{DEFAULT_ALIST_ROOT}/{primary_audio.name}"

    # Prepare argv for generate_epub_overlay
    engine_dir = Path(__file__).parent / "engine"
    sys.path.insert(0, str(engine_dir.resolve()))
    import generate_epub_overlay

    old_argv = sys.argv
    sys.argv = [
        "generate_epub_overlay.py",
        "--audio", str(audio_for_pipeline),
        "--epub", str(primary_epub),
        "--output-dir", str(generated_dir),
        "--work-dir", str(work_dir),
        "--backend", "mlx",
        "--model", str(resolved_model),
        "--language", language,
        "--chunk-seconds", str(chunk_seconds),
        "--batch-size", "1",
        "--mlx-cache-gb", "2",
    ]

    try:
        exit_code = generate_epub_overlay.main()
        if exit_code != 0:
            raise RuntimeError(f"generate_epub_overlay failed with exit code {exit_code}")
    finally:
        sys.argv = old_argv

    # Locate generated EPUB
    generated_epubs = list(generated_dir.glob("*.media-overlay.epub"))
    if not generated_epubs:
        raise RuntimeError("No media-overlay EPUB was produced in generated directory")
    overlay_epub = generated_epubs[0]

    # Probe actual chunk durations from work/run/0*.m4a
    run_dir = work_dir / "run"
    chunk_durations = {}
    chunk_files = sorted(run_dir.glob("0*.m4a"))
    for cf in chunk_files:
        try:
            raw = subprocess.check_output([
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=nw=1:nk=1", str(cf)
            ])
            # Key can match audio/000.m4a or ../audio/000.m4a
            chunk_dur = float(raw.strip())
            chunk_durations[f"audio/{cf.name}"] = chunk_dur
            chunk_durations[f"../audio/{cf.name}"] = chunk_dur
            chunk_durations[cf.name] = chunk_dur
        except Exception:
            chunk_durations[f"audio/{cf.name}"] = float(chunk_seconds)

    # Export PWA bundle
    export_res = export_readalong_bundle(
        generated_epub=overlay_epub,
        output_dir=out_base,
        book_id=book_id,
        source_epub=primary_epub,
        primary_audio=primary_audio,
        alist_audio_path=alist_audio_path,
        chunk_durations=chunk_durations,
        source_offset=source_offset,
        chapters_meta=chapters_meta,
        model_name=resolved_model.name,
        audio_sources_meta=audio_sources_meta,
    )

    # Validate output EPUB
    val_hashes = {str(primary_epub): compute_sha256(primary_epub)}
    if audio_sources_meta:
        for s in audio_sources_meta:
            val_hashes[s["path"]] = s["sha256"]
    else:
        val_hashes[str(primary_audio)] = compute_sha256(primary_audio)

    val_report = validate_overlay_epub(
        overlay_epub,
        expected_source_hashes=val_hashes,
        allow_missing_audio_files=True,
    )

    validation_path = out_base / "validation.json"
    validation_path.write_text(json.dumps(val_report, ensure_ascii=False, indent=2) + "\n")

    # Write source manifest
    source_manifest = {
        "bookId": book_id,
        "sourceAudio": str(primary_audio),
        "sourceAudioSha256": compute_sha256(primary_audio),
        "sourceAudioDuration": sum(s.get("duration", 0.0) for s in audio_sources_meta) if audio_sources_meta else info["audio_info"][0]["probe"].get("duration", 0.0),
        "audioSourcesCount": len(audio_sources_meta) if audio_sources_meta else 1,
        "sourceEpub": str(primary_epub),
        "sourceEpubSha256": compute_sha256(primary_epub),
        "sample": sample,
        "sourceOffset": source_offset,
        "timingEngine": timing,
        "modelPath": str(resolved_model),
        "elapsedSeconds": round(time.time() - started_time, 2),
    }
    (out_base / "source-manifest.json").write_text(
        json.dumps(source_manifest, ensure_ascii=False, indent=2) + "\n"
    )

    return {
        "book_id": book_id,
        "output_dir": str(out_base),
        "structural_pass": val_report["structural_pass"],
        "segment_count": export_res["segment_count"],
        "elapsed_seconds": source_manifest["elapsedSeconds"],
        "manifest_path": export_res["manifest_path"],
        "timeline_path": export_res["timeline_path"],
    }
