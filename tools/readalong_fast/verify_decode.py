"""Read-only physical reproduction of one stopped book's decode interval."""
import argparse
import json
from pathlib import Path

from tools.readalong.batch_candidate_remapper import atomic_json
from tools.readalong.authoritative_validator import safe_path
from tools.readalong_fast.decoding import AudioDecodeIssue, decode_pcm
from tools.readalong_fast.pipeline import InputCache, file_hash, stat_key
from tools.readalong_fast.resume import fast_identity


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--stopped-run", type=Path, required=True)
  parser.add_argument("--output", type=Path, required=True)
  parser.add_argument("--start", type=float, required=True)
  parser.add_argument("--duration", type=float, default=1800)
  parser.add_argument("--track", type=int, default=0)
  args = parser.parse_args()
  import math
  if not all(math.isfinite(v) for v in (args.start, args.duration)) or args.start < 0 or not 0 < args.duration <= 1800:
    raise ValueError("Verification must be bounded to at most 1800 seconds")
  run = args.stopped_run.resolve(strict=True)
  stop = json.loads((run/"STOP.json").read_text())
  inv = json.loads((run/"inventory.json").read_text())
  unit = next(u for u in inv["units"] if u["unit_id"] == stop["unit_id"])
  book = Path(unit["book_dir"]).resolve(strict=True)
  out = args.output.resolve()
  if out.exists() or out.is_relative_to(run) or any(out.is_relative_to(Path(u["book_dir"]).resolve()) for u in inv["units"]):
    raise ValueError("Use new isolated verification output")
  track = unit["audio_tracks"][args.track]
  if args.start+args.duration > track["measured_duration"]+.001:
    raise ValueError("Verification interval exceeds physical inventory")
  out.mkdir(parents=True)
  inputs = InputCache(out/"inputs.json")
  before = {safe_path(book, r["rel_to_book"]): inputs.verify(safe_path(book, r["rel_to_book"]), r["sha256"])
    for r in unit["audio_tracks"]+unit["epubs"]}
  active = book/"readalong"
  active_before = {str(p): stat_key(p) for p in active.rglob("*") if p.is_file()}
  snapshots = {name: file_hash(run/name) for name in ("plan.json", "results.json", "inventory.json", "STOP.json")}
  try:
    decode_pcm(safe_path(book, track["rel_to_book"]), args.start, args.duration, out/"decode.json",
      {"sourceSha256": track["sha256"], "start": args.start, "duration": args.duration, "sampleRate": 16000})
    raise ValueError("Decode issue did not reproduce; do not issue quarantine recovery approval")
  except AudioDecodeIssue as exc:
    issue = exc.report
  if (any(stat_key(p) != s for p, s in before.items()) or active_before != {str(p): stat_key(p) for p in active.rglob("*") if p.is_file()}
      or any(file_hash(run/name) != s for name, s in snapshots.items())):
    raise RuntimeError("SOURCE_CHANGED: verification snapshot changed")
  report = {"unitId": unit["unit_id"], "codeSha256": fast_identity(), "sourceHashVerified": True,
    "sourceSha256": track["sha256"], "sourceUnchanged": True, "activeUnchanged": True,
    "previousRunUnchanged": True, "asrInvoked": False, "outcome": "QUARANTINED_AUDIO",
    "decodeEvidencePath": str(out/"decode.json"), "decodeEvidenceSha256": file_hash(out/"decode.json"),
    "requestedStart": args.start, "requestedEnd": args.start+args.duration,
    "decodedSeconds": issue["decodedSeconds"], "reason": issue["reason"],
    "missingIntervalLocationKnown": False, "fullAudioProcessed": False, "published": False}
  atomic_json(out/"verification.json", report)
  print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
  main()
