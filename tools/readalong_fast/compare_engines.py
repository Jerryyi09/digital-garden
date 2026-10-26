"""V2 A/B comparison: does the batched engine lose text the serial one kept?

The unmapped ratio alone cannot answer this, because the ratio's numerator and
denominator shrink together. These metrics count what a reader actually sees:
recognized words, distinct highlighted fragments, and long gaps in the timeline.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.readalong_fast.matcher import tokens


def load_timeline(root):
  matches = list(Path(root).rglob("timeline.json"))
  if len(matches) != 1:
    raise ValueError(f"Expected one timeline.json under {root}, found {len(matches)}")
  return json.loads(matches[0].read_text())


def timeline_rows(timeline):
  if isinstance(timeline, dict):
    for key in ("segments", "timeline", "rows"):
      if isinstance(timeline.get(key), list):
        return timeline[key]
  if isinstance(timeline, list):
    return timeline
  raise ValueError("Unrecognized timeline shape")


def fragments(timeline):
  """Distinct highlighted (document, fragment) pairs the reader can land on."""
  seen = set()
  for row in timeline_rows(timeline):
    if row.get("timingRejected"):
      continue
    document = row.get("document") or row.get("documentId") or row.get("href")
    fragment = row.get("fragment") or row.get("fragmentId") or row.get("id")
    if document is not None and fragment is not None:
      seen.add((str(document), str(fragment)))
  return seen


def speech_words(timeline):
  counter = Counter()
  for row in timeline_rows(timeline):
    if row.get("timingRejected"):
      continue
    counter.update(tokens(row.get("text", "")))
  return counter


def long_gaps(timeline, threshold=60.0):
  """Per-track gaps over the threshold, the reader-visible holes."""
  by_track = {}
  for row in timeline_rows(timeline):
    if row.get("timingRejected"):
      continue
    track = row.get("audioSourceId") or row.get("track")
    start, end = row.get("start"), row.get("end")
    if track is None or start is None or end is None or end <= start:
      continue
    by_track.setdefault(track, []).append((start, end))
  gaps = []
  for track, spans in by_track.items():
    spans.sort()
    for (_, previous_end), (start, _) in zip(spans, spans[1:]):
      if start-previous_end > threshold:
        gaps.append({"audioSourceId": track, "start": previous_end, "end": start,
          "seconds": start-previous_end})
  return gaps


def summarize(timeline):
  words = speech_words(timeline)
  return {"rows": len(timeline_rows(timeline)), "words": sum(words.values()),
    "distinctWords": len(words), "fragments": len(fragments(timeline)),
    "longGaps": len(long_gaps(timeline)),
    "longGapSeconds": sum(g["seconds"] for g in long_gaps(timeline))}


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--serial", type=Path, required=True)
  parser.add_argument("--batch", type=Path, required=True)
  parser.add_argument("--label", default="book")
  args = parser.parse_args()
  serial, batch = summarize(load_timeline(args.serial)), summarize(load_timeline(args.batch))
  comparison = {"label": args.label, "serial": serial, "batch": batch, "checks": {}}
  checks = comparison["checks"]
  checks["wordRetention"] = batch["words"]/serial["words"] if serial["words"] else None
  checks["distinctWordRetention"] = (batch["distinctWords"]/serial["distinctWords"]
    if serial["distinctWords"] else None)
  checks["fragmentRetention"] = (batch["fragments"]/serial["fragments"]
    if serial["fragments"] else None)
  checks["longGapsNotIncreased"] = batch["longGaps"] <= serial["longGaps"]
  # Pass conditions from the work order: 97% of words, 98% of distinct highlights.
  checks["passWordRetention"] = checks["wordRetention"] is not None and checks["wordRetention"] >= 0.97
  checks["passFragmentRetention"] = (checks["fragmentRetention"] is not None
    and checks["fragmentRetention"] >= 0.98)
  checks["pass"] = bool(checks["passWordRetention"] and checks["passFragmentRetention"]
    and checks["longGapsNotIncreased"])
  print(json.dumps(comparison, ensure_ascii=False, indent=1))


if __name__ == "__main__":
  main()
