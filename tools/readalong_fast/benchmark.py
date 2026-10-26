"""Read-only-cache real-book verification and bounded-vs-global matcher timing."""
import argparse
from collections import Counter
from difflib import SequenceMatcher
import json
from pathlib import Path
import time

from tools.readalong.batch_candidate_remapper import atomic_json, sanitize_slug
from tools.readalong.input_inventory import model_fingerprint
from tools.readalong.config import DEFAULT_CACHE_ROOT, resolve_model_path
from tools.readalong_fast.matcher import prepare_paragraphs, tokens
from tools.readalong_fast.pipeline import InputCache, SpeechCache, generate
from tools.readalong.universal_stream_aligner import get_spine_htmls
from tools.readalong_fast.resume import fast_identity


def resolve_cache_roots(write_root=None, read_roots=()):
  """New ASR is written to the authoritative cache root unless a write root is given explicitly.

  Writing to the run's own output directory (the previous behaviour) stranded every new
  transcription in that run, so the next batch re-transcribed the same audio.
  """
  write = Path(write_root) if write_root else DEFAULT_CACHE_ROOT
  reads = list(dict.fromkeys([write, *[Path(r) for r in read_roots], DEFAULT_CACHE_ROOT]))
  return write, reads


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--inventory", type=Path, required=True)
  parser.add_argument("--output", type=Path, required=True)
  parser.add_argument("--unit", action="append", required=True)
  parser.add_argument("--cache-read-root", type=Path, action="append", default=[],
    help="Additional cache roots to read; defaults to [DEFAULT_CACHE_ROOT] if omitted")
  parser.add_argument("--cache-write-root", type=Path, default=None,
    help="Where new ASR results are written; defaults to the authoritative DEFAULT_CACHE_ROOT so every run "
         "reuses every earlier run's work. Pass a run-local path only for isolated experiments.")
  parser.add_argument("--compare-global", action="store_true")
  parser.add_argument("--allow-new-asr", action="store_true", help="Explicit bounded representative-book verification, not a library batch")
  parser.add_argument("--material-policy", type=Path, help="Explicit source-bound authorized scope file; never a proposal file")
  parser.add_argument("--asr-engine", choices=("serial", "batch", "words"), default="batch",
    help="New-ASR engine for cache misses; batch is mlx-batch-silence-v1 and is the default")
  args = parser.parse_args()
  if args.output.exists():
    raise ValueError("Use a new benchmark directory")
  inv = json.loads(args.inventory.read_text())
  units = {u["unit_id"]: u for u in inv["units"]}
  if any(uid not in units for uid in args.unit):
    raise ValueError("Unknown physical unit")
  if any(args.output.resolve().is_relative_to(Path(u["book_dir"]).resolve()) for u in units.values()):
    raise ValueError("Benchmark output must be outside source books")
  args.output.mkdir(parents=True)
  model_sha = model_fingerprint(resolve_model_path())
  policy_path = args.material_policy or Path(__file__).parent.parent/"readalong/material-exceptions.json"
  entries = json.loads(policy_path.read_text())["entries"]
  policy = {e["unitId"]: e for e in entries}
  if len(policy) != len(entries):
    raise ValueError("Duplicate unit policies are not permitted")
  write_root, cache_roots = resolve_cache_roots(args.cache_write_root, args.cache_read_root)
  cache = SpeechCache(write_root, cache_roots, model_sha, not args.allow_new_asr,
    asr_engine=args.asr_engine)
  inputs = InputCache(args.output/"verified-inputs.json")
  summary = {"codeSha256": fast_identity(), "newAsrAllowed": args.allow_new_asr,
    "newAsrPerformed": False, "published": False, "asrEngine": args.asr_engine, "records": []}
  for uid in args.unit:
    unit = units[uid]
    dest = args.output/sanitize_slug(uid)
    report = generate(unit, dest, cache, inputs, policy.get(uid))
    if args.compare_global:
      spine = get_spine_htmls(Path(unit["book_dir"])/unit["epubs"][0]["rel_to_book"])
      _, _, book_tokens = prepare_paragraphs(dest/"text", spine)
      words = []
      cap = max(t["measured_duration"] for t in unit["audio_tracks"])+1
      for t in unit["audio_tracks"]:
        audio = Path(unit["book_dir"])/t["rel_to_book"]
        duration = inputs.duration(audio, t["measured_duration"]) if t["measured_duration"] > 1800 else t["measured_duration"]
        rows = cache.whole_legacy_track(audio, t["sha256"], duration, cap)
        if rows is None:
          from tools.readalong.candidate_safety import plan_audio_blocks
          rows = [r for a, length in plan_audio_blocks(duration, 1800) for r in cache.chunk(audio, t["sha256"], a, length)]
        words.extend(w for r in rows for w in tokens(r["text"]))
      start, cpu = time.perf_counter(), time.process_time()
      blocks = SequenceMatcher(None, book_tokens, words, autojunk=False).get_matching_blocks()
      report["globalMatcherComparison"] = {"wallSeconds": time.perf_counter()-start,
        "cpuSeconds": time.process_time()-cpu, "bookTokens": len(book_tokens), "audioTokens": len(words),
        "matchedTokens": sum(b.size for b in blocks),
        "note": "Global matching core only; paragraph and word modes have different granularity, not an accuracy equivalence test"}
    summary["records"].append({"unit_id": uid, "readalongUsability": report["readalongUsability"],
      "screenDecision": report.get("screenDecision"), "screenDetail": report.get("screenDetail"),
      "metrics": report["metrics"], "timings": report["timings"], "matchingStats": report["matchingStats"],
      "speechCacheStats": report["speechCacheStats"], "globalMatcherComparison": report.get("globalMatcherComparison")})
    summary["records"][-1].update(fullAudioProcessed=report["fullAudioProcessed"],
      asrDiagnosticCounts=dict(Counter(d["reason"] for d in report.get("asrDiagnostics", []))),
      documentDiagnosticCounts=dict(Counter(d["reason"] for d in report.get("documentDiagnostics", []))))
    summary["newAsrPerformed"] = summary["newAsrPerformed"] or report["speechCacheStats"].get("newAsrAudioSeconds", 0) > 0
    if summary["codeSha256"] != fast_identity():
      raise RuntimeError("Benchmark source code changed")
    atomic_json(args.output/"benchmark.json", summary)
    print(json.dumps(summary["records"][-1], ensure_ascii=False), flush=True)


if __name__ == "__main__":
  main()
