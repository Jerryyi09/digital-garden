"""Bounded native-ASR diagnostic; preserve raw output before validating it."""
import argparse
import json
from pathlib import Path
import subprocess
import time

from tools.readalong.asr_runtime import transcription_backend
from tools.readalong.batch_candidate_remapper import atomic_json
from tools.readalong.config import resolve_model_path
from tools.readalong.authoritative_validator import safe_path
from tools.readalong_fast.pipeline import InputCache, checked_units, stat_key


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--inventory", type=Path, required=True)
  parser.add_argument("--unit", required=True)
  parser.add_argument("--output", type=Path, required=True)
  parser.add_argument("--track", type=int, default=0)
  parser.add_argument("--start", type=float, default=0)
  parser.add_argument("--duration", type=float, default=15)
  args = parser.parse_args()
  import math
  if not all(math.isfinite(v) for v in (args.start, args.duration)) or args.start < 0 or not 0 < args.duration <= 1800:
    raise ValueError("Probe must be finite and bounded to at most 1800 seconds")
  units = json.loads(args.inventory.read_text())["units"]
  unit = next(u for u in units if u["unit_id"] == args.unit)
  book = Path(unit["book_dir"]).resolve(strict=True)
  output = args.output.resolve()
  if output.exists() or any(output.is_relative_to(Path(u["book_dir"]).resolve()) for u in units):
    raise ValueError("Probe output must be a new directory outside all source books")
  row = unit["audio_tracks"][args.track]
  audio = safe_path(book, row["rel_to_book"])
  if args.start+args.duration > row["measured_duration"]+.001:
    raise ValueError("Probe exceeds inventory audio duration")
  output.mkdir(parents=True)
  state = InputCache(output/"inputs.json").verify(audio, row["sha256"])
  import numpy as np
  begin = time.perf_counter()
  proc = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(args.start), "-i", str(audio),
    "-t", str(args.duration), "-map", "0:a:0", "-vn", "-ac", "1", "-ar", "16000",
    "-f", "f32le", "pipe:1"], check=True, capture_output=True)
  pcm = np.frombuffer(proc.stdout, dtype="<f4").copy()
  decoded = time.perf_counter()
  result = transcription_backend()(pcm, path_or_hf_repo=str(resolve_model_path()),
    language="en", word_timestamps=False, condition_on_previous_text=False, verbose=False, fp16=True)
  rows = [{"start": args.start+s["start"], "end": args.start+s["end"], "text": s["text"]}
    for s in result.get("segments", [])]
  report = {"unitId": args.unit, "audioSourceId": row["rel_to_book"], "sourceSha256": row["sha256"],
    "start": args.start, "duration": args.duration, "decodedSeconds": len(pcm)/16000,
    "decodeSeconds": decoded-begin, "asrSeconds": time.perf_counter()-decoded,
    "wordTimestamps": False, "rawSegments": rows, "sourceUnchanged": stat_key(audio) == state}
  atomic_json(output/"raw.json", report)
  try:
    checked_units(rows, args.start, args.start+args.duration)
    report["legacyCheck"] = "ACCEPTED"
  except ValueError as exc:
    report["legacyCheck"] = str(exc)
  atomic_json(output/"raw.json", report)
  print(json.dumps({k: v for k, v in report.items() if k != "rawSegments"}, ensure_ascii=False))


if __name__ == "__main__":
  main()
