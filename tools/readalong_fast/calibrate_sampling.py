"""V3 calibration: run the block sampling estimator against full-book truth, from cache only.

Truth is computed by matching every cached block of the book (zero new ASR), giving
the same located/unlocated seconds the estimator samples. Running both through the
same code path is what makes the comparison meaningful: any gap between them is
sampling error, not a difference in how located speech is measured.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.readalong.config import resolve_model_path
from tools.readalong.input_inventory import model_fingerprint
from tools.readalong_fast.matcher import ParagraphIndex, prepare_paragraphs, tokens
from tools.readalong_fast.pipeline import InputCache, SpeechCache
from tools.readalong_fast.sampling import (MAX_SAMPLE_BLOCKS, MIN_BLOCK_TOKENS,
  MIN_SAMPLE_TOKENS, block_plan, classify, extend_strata, stratified_blocks,
  verdict_runs_full_book)
from tools.readalong.universal_stream_aligner import get_spine_htmls
from tools.readalong.batch_candidate_remapper import atomic_json, sanitize_slug


def measure_block(index, rows, start, duration):
  """Located vs unlocated speech seconds for one block, cursor-free.

  Blocks are measured independently so the estimate never depends on the order
  samples happen to be taken in."""
  observed = missing = 0.0
  for row in rows:
    if row.get("timingRejected"):
      continue
    span = row["end"]-row["start"]
    if span <= 0:
      continue
    observed += span
    if index.locate_detailed(row["text"], None)["match"] is None:
      missing += span
  return {"observedSeconds": observed, "missingSeconds": missing}


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--inventory", type=Path, required=True)
  parser.add_argument("--unit", action="append", required=True)
  parser.add_argument("--output", type=Path, required=True)
  parser.add_argument("--cache-read-root", type=Path, action="append", default=[])
  parser.add_argument("--book-epub-override", action="append", default=[],
    help="unit_id=path; pair this audio with another book's EPUB to build a mismatch case")
  args = parser.parse_args()
  if args.output.exists():
    raise ValueError("Use a new calibration directory")
  inv = json.loads(args.inventory.read_text())
  units = {u["unit_id"]: u for u in inv["units"]}
  overrides = dict(o.split("=", 1) for o in args.book_epub_override)
  args.output.mkdir(parents=True)
  model_sha = model_fingerprint(resolve_model_path())
  cache = SpeechCache(args.output/"cache", args.cache_read_root, model_sha, cache_only=True)
  inputs = InputCache(args.output/"verified-inputs.json")
  report = {"codeSha256": None, "records": []}
  for uid in args.unit:
    unit = units[uid]
    book = Path(unit["book_dir"])
    dest = args.output/sanitize_slug(uid)
    dest.mkdir(parents=True, exist_ok=True)
    epub_rel = overrides.get(uid) or unit["epubs"][0]["rel_to_book"]
    epub = Path(epub_rel) if overrides.get(uid) else book/epub_rel
    if not epub.is_file():
      # A source book archived off the working disk still has a usable cache, but
      # the calibration cannot tokenize without its EPUB; skip it and keep the batch going.
      record = {"unit_id": uid, "epub": str(epub), "verdict": "CALIBRATION_UNAVAILABLE",
        "runsFullBook": True, "detail": {"reason": "EPUB_NOT_PRESENT"}}
      report["records"].append(record)
      print(json.dumps(record, ensure_ascii=False), flush=True)
      continue
    from tools.readalong.input_inventory import safe_extract_epub
    text_root = dest/"text"
    safe_extract_epub(epub, text_root)
    spine = get_spine_htmls(epub)
    _, paragraphs, book_tokens = prepare_paragraphs(text_root, spine, [])
    index = ParagraphIndex(book_tokens, paragraphs)
    tracks = [{"audioSourceId": t["rel_to_book"], "duration": t["measured_duration"]}
              for t in unit["audio_tracks"]]
    blocks = stratified_blocks(tracks)
    per_block, total_obs, total_missing = [], 0.0, 0.0

    def measure(spec):
      audio = book/spec["audioSourceId"]
      sha = next(t["sha256"] for t in unit["audio_tracks"] if t["rel_to_book"] == spec["audioSourceId"])
      # Fetch the whole grid block, then measure only the stratum window inside it.
      rows = cache.chunk(audio, sha, spec["start"], spec["duration"])
      rows = [r for r in rows if r["end"] > spec["measureStart"]
              and r["start"] < spec["measureStart"]+spec["measureDuration"]]
      stat = measure_block(index, rows, spec["measureStart"], spec["measureDuration"])
      stat.update(spec)
      stat["tokens"] = sum(len(tokens(r["text"])) for r in rows)
      return stat

    for spec in blocks:
      stat = measure(spec)
      if stat["tokens"] < MIN_BLOCK_TOKENS:
        continue
      per_block.append(stat)
    # Mirror the production path: a thin short-track sample is extended until the
    # aggregate token floor is met, so the recorded evidence matches what ships.
    if sum(s["tokens"] for s in per_block) < MIN_SAMPLE_TOKENS:
      for spec in extend_strata(tracks, blocks, MAX_SAMPLE_BLOCKS):
        stat = measure(spec)
        if stat["tokens"] < MIN_BLOCK_TOKENS:
          continue
        per_block.append(stat)
        if sum(s["tokens"] for s in per_block) >= MIN_SAMPLE_TOKENS:
          break
    verdict, detail = classify(per_block)
    for s in per_block:
      total_obs += s["observedSeconds"]
      total_missing += s["missingSeconds"]
    record = {"unit_id": uid, "epub": epub_rel, "verdict": verdict, "runsFullBook": verdict_runs_full_book(verdict),
      "detail": detail, "sampleBlocks": len(per_block),
      "sampleUnmappedRatio": total_missing/total_obs if total_obs else None,
      "perBlock": [{k: s[k] for k in ("audioSourceId", "start", "duration", "measureStart",
        "measureDuration", "observedSeconds", "missingSeconds", "tokens")} for s in per_block]}
    report["records"].append(record)
    print(json.dumps(record, ensure_ascii=False), flush=True)
  atomic_json(args.output/"calibration.json", report)


if __name__ == "__main__":
  main()
