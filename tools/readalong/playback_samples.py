"""Generate reproducible timeline inspection points; this is not a listening test."""
import argparse
import json
from pathlib import Path


def playback_samples(timeline):
  if not timeline:
    return []
  return [{"progress": fraction, "index": int(len(timeline) * fraction),
           "segment": timeline[int(len(timeline) * fraction)]} for fraction in (0.2, 0.5, 0.8)]


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("timeline", type=Path)
  args = parser.parse_args()
  print(json.dumps(playback_samples(json.loads(args.timeline.read_text(encoding="utf-8"))),
                   ensure_ascii=False, indent=2))


if __name__ == "__main__":
  main()
