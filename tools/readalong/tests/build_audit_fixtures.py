#!/usr/bin/env python3
"""
Build isolated test fixtures for the 13 audit findings (F01-F13) and positive baselines.
Used by RA-01 regression test suite.
"""

import json
from pathlib import Path
import tempfile
import wave
from tools.readalong.acoustic_evaluator import POLICY_VERSION, sha256

FIXTURES_DIR = Path(tempfile.mkdtemp(prefix="readalong-fixtures-"))


def reference_for(book):
    return book.parent / (book.name + "-reference.json")


def write_reference(book):
    """Simulate an operator-approved reference for synthetic tests only."""
    assets = book / "readalong"
    timeline_file = assets / "timeline.json"
    timeline = json.loads(timeline_file.read_text())
    manifest = json.loads((assets / "readalong.manifest.json").read_text())
    reference = {
        "schemaVersion": 1, "policyVersion": POLICY_VERSION,
        "scope": "complete-timeline", "approvedBy": "SYNTHETIC-TEST-ONLY",
        "approvedAt": "2026-10-23", "timelineSha256": sha256(timeline_file),
        "audioSha256": {s["id"]: sha256(book / s["id"]) for s in manifest["audioSources"]},
        "documentsSha256": {s["document"]: sha256(assets / s["document"]) for s in timeline},
        "segments": timeline,
    }
    reference_for(book).write_text(json.dumps(reference))
    return reference_for(book)

def make_clean_book(base_path: Path):
    """Creates a well-formed minimal book structure with 1 audio and 1 HTML doc."""
    base_path.mkdir(parents=True, exist_ok=True)
    readalong = base_path / "readalong"
    readalong.mkdir(parents=True, exist_ok=True)
    text_dir = readalong / "text"
    text_dir.mkdir(parents=True, exist_ok=True)

    # 1. Physical audio dummy
    audio_path = base_path / "track_01.mp3"
    # Valid PCM with a legacy .mp3 filename; ffprobe detects the actual container.
    with wave.open(str(audio_path), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(8000)
        stream.writeframes(b"\0\0" * 128000)
    audio_bytes = audio_path.read_bytes()
    import hashlib
    actual_sha = hashlib.sha256(audio_bytes).hexdigest()

    # 2. HTML doc
    html_file = text_dir / "chapter1.html"
    html_file.write_text(
        '<!DOCTYPE html><html><head><title>Ch1</title></head><body>'
        '<p><span id="c01-segment01">First sentence in text.</span> '
        '<span id="c01-segment02">Second sentence in text.</span></p>'
        '</body></html>',
        encoding="utf-8"
    )

    # 3. Manifest
    # Speech runs from 2.0 to 15.0. Duration is 16.0s (head delay 2.0s <= 25s, tail gap 1.0s <= 20s).
    manifest = {
        "schemaVersion": 1,
        "bookId": base_path.name,
        "language": "en",
        "audioSources": [
            {
                "id": "track_01.mp3",
                "name": "track_01.mp3",
                "duration": 16.0,
                "sha256": actual_sha
            }
        ],
        "timeline": "timeline.json",
        "textRoot": "text/",
        "segmentCount": 2,
        "timing": {
            "status": "TIMING_VERIFIED",
            "evaluator": "acoustic_evaluator_v1",
            "metrics": {
                "evaluated_segments": 2,
                "total_segments": 2,
                "coverage_ratio": 1.0,
                "mae_seconds": 0.03,
                "p50_seconds": 0.02,
                "p95_seconds": 0.05,
                "max_error_seconds": 0.06
            }
        }
    }
    (readalong / "readalong.manifest.json").write_text(json.dumps(manifest, indent=2))

    # 4. Timeline
    timeline = [
        {
            "audioSourceId": "track_01.mp3",
            "start": 2.0,
            "end": 8.0,
            "document": "text/chapter1.html",
            "fragment": "c01-segment01",
            "text": "First sentence in text.",
            "timingStatus": "VERIFIED"
        },
        {
            "audioSourceId": "track_01.mp3",
            "start": 8.5,
            "end": 15.0,
            "document": "text/chapter1.html",
            "fragment": "c01-segment02",
            "text": "Second sentence in text.",
            "timingStatus": "VERIFIED"
        }
    ]
    (readalong / "timeline.json").write_text(json.dumps(timeline, indent=2))
    write_reference(base_path)
    return base_path

def build_all_fixtures():
    if FIXTURES_DIR.exists():
        import shutil
        shutil.rmtree(FIXTURES_DIR)
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    # Positive baseline: PASS
    p_clean = make_clean_book(FIXTURES_DIR / "positive_valid_book")

    # F01: Missing entire track without exemption (manifest has 2 audio sources, timeline only covers 1)
    f01 = make_clean_book(FIXTURES_DIR / "f01_missing_track")
    f01_mf = json.loads((f01 / "readalong" / "readalong.manifest.json").read_text())
    f01_mf["audioSources"].append({
        "id": "track_02_main.mp3",
        "name": "track_02_main.mp3",
        "duration": 180.0,
        "sha256": "dummy_sha2"
    })
    (f01 / "track_02_main.mp3").write_bytes(b"TRACK_02_AUDIO")
    (f01 / "readalong" / "readalong.manifest.json").write_text(json.dumps(f01_mf, indent=2))

    # F02: Timestamp overlap within same track (start[1] < end[0])
    f02_overlap = make_clean_book(FIXTURES_DIR / "f02_timestamp_overlap")
    tl = json.loads((f02_overlap / "readalong" / "timeline.json").read_text())
    tl[1]["start"] = 6.0  # Overlaps with 2.0 - 8.0!
    (f02_overlap / "readalong" / "timeline.json").write_text(json.dumps(tl, indent=2))

    # F02_b: Broken fragment reference (fragment ID does not exist in target HTML)
    f02_broken = make_clean_book(FIXTURES_DIR / "f02_broken_fragment")
    tl_b = json.loads((f02_broken / "readalong" / "timeline.json").read_text())
    tl_b[0]["fragment"] = "non_existent_fragment_id_999"
    (f02_broken / "readalong" / "timeline.json").write_text(json.dumps(tl_b, indent=2))

    # F02_c: Missing referenced HTML file
    f02_nodoc = make_clean_book(FIXTURES_DIR / "f02_missing_html_file")
    tl_c = json.loads((f02_nodoc / "readalong" / "timeline.json").read_text())
    tl_c[0]["document"] = "text/deleted_file.html"
    (f02_nodoc / "readalong" / "timeline.json").write_text(json.dumps(tl_c, indent=2))

    # F02_d: Nan/Infinite or negative timestamp
    f02_nan = make_clean_book(FIXTURES_DIR / "f02_invalid_nan_time")
    tl_d = json.loads((f02_nan / "readalong" / "timeline.json").read_text())
    tl_d[0]["start"] = -5.0
    (f02_nan / "readalong" / "timeline.json").write_text(json.dumps(tl_d, indent=2))

    # F03: Unexplained severe gap > 20s (e.g. 50s gap in middle of speech)
    f03_gap = make_clean_book(FIXTURES_DIR / "f03_severe_internal_gap")
    tl_gap = json.loads((f03_gap / "readalong" / "timeline.json").read_text())
    tl_gap[1]["start"] = 45.0  # Gap = 45.0 - 8.0 = 37.0s!
    tl_gap[1]["end"] = 52.0
    (f03_gap / "readalong" / "timeline.json").write_text(json.dumps(tl_gap, indent=2))

    # F07: Unregistered physical audio exists on disk but not declared in manifest
    f07_unreg = make_clean_book(FIXTURES_DIR / "f07_unregistered_audio_on_disk")
    (f07_unreg / "track_forgotten_02.mp3").write_bytes(b"FORGOTTEN_AUDIO")

    # F08: Density below threshold (< 3.0 segs/min across long audio)
    f08_density = make_clean_book(FIXTURES_DIR / "f08_fake_low_density")
    f08_mf = json.loads((f08_density / "readalong" / "readalong.manifest.json").read_text())
    f08_mf["audioSources"][0]["duration"] = 1200.0  # 20 minutes with only 2 segments = 0.1 segs/min!
    (f08_density / "readalong" / "readalong.manifest.json").write_text(json.dumps(f08_mf, indent=2))

    # F12: Path traversal in document reference
    f12_traversal = make_clean_book(FIXTURES_DIR / "f12_path_traversal")
    tl_t = json.loads((f12_traversal / "readalong" / "timeline.json").read_text())
    tl_t[0]["document"] = "../../etc/passwd"
    (f12_traversal / "readalong" / "timeline.json").write_text(json.dumps(tl_t, indent=2))

    print(f"Generated {len(list(FIXTURES_DIR.iterdir()))} test fixtures under {FIXTURES_DIR}")

if __name__ == "__main__":
    build_all_fixtures()
