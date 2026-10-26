"""Per-audio-source timeline shards for large readalong releases."""
import hashlib
import json
import re
from pathlib import Path


TIMELINE_SHARD_THRESHOLD_BYTES = 300 * 1024 * 1024


def _file_name(source_id: str) -> str:
  stem = re.sub(r"[^A-Za-z0-9._-]+", "_", source_id).strip("._") or "track"
  digest = hashlib.sha1(source_id.encode("utf-8")).hexdigest()[:10]
  return f"{stem}.{digest}.json"


def write_timeline_payload(output_dir: Path, timeline: list[dict], *, threshold_bytes: int = TIMELINE_SHARD_THRESHOLD_BYTES):
  """Write a legacy timeline or per-source shards and return manifest fields."""
  serialized = json.dumps(timeline, ensure_ascii=False, indent=2) + "\n"
  if len(serialized.encode("utf-8")) < threshold_bytes:
    (output_dir / "timeline.json").write_text(serialized, encoding="utf-8")
    return {"timeline": "timeline.json", "segmentCount": len(timeline)}

  grouped = {}
  for segment in timeline:
    grouped.setdefault(segment["audioSourceId"], []).append(segment)
  shard_dir = output_dir / "timeline-shards"
  shard_dir.mkdir(parents=True, exist_ok=True)
  files = {}
  for source_id, segments in grouped.items():
    name = _file_name(source_id)
    (shard_dir / name).write_text(
      json.dumps(segments, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    files[source_id] = f"timeline-shards/{name}"
  index = {"format": "per-audio-source-v1", "files": files, "segmentCount": len(timeline)}
  (output_dir / "timeline-index.json").write_text(
    json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
  )
  return {
    "timeline": "timeline-index.json",
    "timelineFormat": "per-audio-source-v1",
    "timelineIndex": "timeline-index.json",
    "segmentCount": len(timeline),
  }


def load_timeline_payload(base_dir: Path, manifest: dict) -> list[dict]:
  """Load either a legacy timeline or the new sharded representation."""
  if manifest.get("timelineFormat") != "per-audio-source-v1":
    return json.loads((base_dir / (manifest.get("timeline") or "timeline.json")).read_text(encoding="utf-8"))
  index = json.loads((base_dir / (manifest.get("timelineIndex") or manifest.get("timeline") or "timeline-index.json")).read_text(encoding="utf-8"))
  result = []
  for rel in index.get("files", {}).values():
    result.extend(json.loads((base_dir / rel).read_text(encoding="utf-8")))
  return result
