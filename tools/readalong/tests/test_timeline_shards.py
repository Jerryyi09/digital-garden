import json
from pathlib import Path

from tools.readalong.timeline_shards import load_timeline_payload, write_timeline_payload


def test_small_timeline_keeps_legacy_shape(tmp_path: Path):
  timeline = [{"audioSourceId": "a.mp3", "start": 0, "end": 1}]
  fields = write_timeline_payload(tmp_path, timeline, threshold_bytes=10_000)
  assert fields["timeline"] == "timeline.json"
  assert not (tmp_path / "timeline-index.json").exists()
  assert load_timeline_payload(tmp_path, fields) == timeline


def test_large_timeline_shards_by_audio_source(tmp_path: Path):
  timeline = [
    {"audioSourceId": "01.mp3", "start": i, "end": i + 1, "text": "x" * 40}
    for i in range(4)
  ] + [
    {"audioSourceId": "02.mp3", "start": i, "end": i + 1, "text": "y" * 40}
    for i in range(3)
  ]
  fields = write_timeline_payload(tmp_path, timeline, threshold_bytes=10)
  assert fields["timelineFormat"] == "per-audio-source-v1"
  index = json.loads((tmp_path / "timeline-index.json").read_text())
  assert set(index["files"]) == {"01.mp3", "02.mp3"}
  assert load_timeline_payload(tmp_path, fields) == timeline
