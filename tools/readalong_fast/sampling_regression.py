"""Fixed screening regression library: the verdicts a threshold edit must not break.

Every case is scored from already-recorded block evidence, so this command costs
no ASR and no full-book mapping. The expectations come from two places:

  * the 2026-10-24 V3 calibration over 28 cached books, whose verdicts the new
    criteria must reproduce exactly;
  * the 2026-10-25 re-screening of four real same-book-different-edition
    mismatches (Peter Pan, Tess, The Scarlet Letter, Great Expectations), which
    the old "every block <= 2% located" rule missed.

The four real mismatches matter most: they are the everyday case, where the audio
is an English original and the EPUB is a different edition of the same book, so a
few stray fragments always match. Constructed cross-book pairs score exactly 0
and cannot calibrate that boundary.

Run it before any change to `sampling.py` ships:

  python -m tools.readalong_fast.sampling_regression
"""
import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.readalong_fast.sampling import (MIN_SAMPLE_TOKENS, VERDICT_BORDERLINE,
  VERDICT_MISMATCH, VERDICT_MODERATE, VERDICT_PASS, classify)

REGRESSION_DIR = Path(__file__).resolve().parent/"regression_data"

# (source file, unit_id, expected verdict). The regression records are replayed because
# their caches are not all in the repo, but their per-block evidence is recorded.
CASES = [
  (REGRESSION_DIR/"calibration-main.json", "文学作品/安娜卡列妮娜", VERDICT_PASS),
  (REGRESSION_DIR/"calibration-main.json", "文学作品/傲慢与偏见", VERDICT_PASS),
  (REGRESSION_DIR/"calibration-main.json", "文学作品/莎士比亚故事集", VERDICT_PASS),
  (REGRESSION_DIR/"calibration-main.json", "文学作品/复活", VERDICT_BORDERLINE),
  (REGRESSION_DIR/"calibration-main.json", "文学作品/飘", VERDICT_BORDERLINE),
  (REGRESSION_DIR/"calibration-main.json", "文学作品/欧亨利短篇小说", VERDICT_MODERATE),
  (REGRESSION_DIR/"calibration-main.json", "文学作品/杀死一只知更鸟", VERDICT_MISMATCH),
  (REGRESSION_DIR/"calibration-main.json", "心智成长/心流", VERDICT_MISMATCH),
  (REGRESSION_DIR/"calibration-constructed-mismatch.json", "文学作品/安娜卡列妮娜", VERDICT_MISMATCH),
  (REGRESSION_DIR/"calibration-constructed-mismatch.json", "文学作品/傲慢与偏见", VERDICT_MISMATCH),
  # Real edition mismatches, re-screened 2026-10-25 from the V4 run caches.
  # Great Expectations is the short-track case: 179 tracks of 28-120s, so its
  # strata are extended until the aggregate token floor is met.
  (REGRESSION_DIR/"calibration-calib4.json", "文学作品/彼得潘 Peter Pan", VERDICT_MISMATCH),
  (REGRESSION_DIR/"calibration-calib4.json", "文学作品/德伯家的苔丝", VERDICT_MISMATCH),
  (REGRESSION_DIR/"calibration-calib4.json", "文学作品/红字", VERDICT_MISMATCH),
  (REGRESSION_DIR/"calibration-calib4.json", "文学作品/远大前程", VERDICT_MISMATCH),
]

# Books the order names that the recorded evidence cannot judge, with the reason.
# They are listed so a reader can see they were not silently dropped.
UNAVAILABLE = {
  "文学作品/安娜卡列妮娜 + Garnett": "the Garnett-edition EPUB is archived off the working disk",
  "心智成长/The Power of Positive Thinking": "no V3 record; its cache is not in the repo",
  "文学作品/弗兰肯斯坦": "no V3 record; its 18000s block was never decoded (AUDIO_DECODE_INCOMPLETE)",
  "心智成长/七个高效习惯": "no V3 record; its cache is not in the repo",
  "文学作品/麦田里的守望者": "no V3 constructed-mismatch record; only 安娜 and 傲慢与偏见 were built",
}


def score(record):
  blocks = record.get("perBlock") or []
  samples = [{"observedSeconds": b["observedSeconds"], "missingSeconds": b["missingSeconds"],
              "tokens": b["tokens"]} for b in blocks]
  return classify(samples)


def load(path):
  if not path.is_file():
    return None
  return {r["unit_id"]: r for r in json.loads(path.read_text())["records"]}


def main(argv=None):
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--json", type=Path, help="also write the full report here")
  args = parser.parse_args(argv)
  start = time.perf_counter()
  cache, failures, rows = {}, [], []
  for path, unit_id, expected in CASES:
    if path not in cache:
      cache[path] = load(path)
    record = (cache[path] or {}).get(unit_id)
    if record is None:
      failures.append(f"{unit_id}: no recorded evidence in {path.name}")
      continue
    verdict, detail = score(record)
    ok = verdict == expected
    if not ok:
      failures.append(f"{unit_id}: expected {expected}, got {verdict} ({detail.get('reason', '')})")
    rows.append({"unitId": unit_id, "expected": expected, "actual": verdict, "ok": ok,
      "locatedRatio": detail.get("locatedRatio"), "locatedUpper": detail.get("locatedUpper"),
      "maxBlockLocatedRatio": detail.get("maxBlockLocatedRatio"),
      "blocks": detail.get("blocks"), "reason": detail.get("reason"), "source": path.name})
  # Every V3 record, not just the named cases: a threshold edit that changes any
  # previously-calibrated verdict is a regression even if it misses the spot checks.
  sweep, swept = [], 0
  for path in (REGRESSION_DIR/"calibration-main.json", REGRESSION_DIR/"calibration-constructed-mismatch.json"):
    for unit_id, record in (load(path) or {}).items():
      if not record.get("perBlock"):
        continue
      swept += 1
      verdict, detail = score(record)
      if verdict != record["verdict"]:
        failures.append(f"SWEEP {unit_id}: V3 recorded {record['verdict']}, now {verdict}")
        sweep.append({"unitId": unit_id, "recorded": record["verdict"], "now": verdict})
  elapsed = time.perf_counter()-start
  for row in rows:
    g = lambda k: "n/a" if row[k] is None else f"{row[k]:.4f}"
    print(f"{'ok ' if row['ok'] else 'FAIL'} {row['unitId']:34s} {row['actual']:18s} "
          f"located={g('locatedRatio')} upper={g('locatedUpper')} maxblk={g('maxBlockLocatedRatio')} "
          f"{row['reason'] or ''}")
  # The closest good book must show both veto reasons, so a threshold drift that
  # quietly starts excluding it is visible here rather than in production.
  for row in rows:
    if row["unitId"] == "文学作品/复活":
      print(f"\n复活 veto detail: locatedUpper={row['locatedUpper']:.4f} "
            f"(threshold <0.20), maxBlock={row['maxBlockLocatedRatio']:.4f} (veto >=0.50)")
  print(f"\nV3 sweep: {swept} recorded verdicts re-scored, {len(sweep)} changed")
  for unit_id, why in UNAVAILABLE.items():
    print(f"n/a  {unit_id:34s} {why}")
  print(f"\n{len(rows)-len([r for r in rows if not r['ok']])}/{len(rows)} named cases matched "
        f"in {elapsed:.2f}s")
  if failures:
    print("\nFAILURES:")
    for line in failures:
      print("  "+line)
  if args.json:
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps({"elapsedSeconds": elapsed, "rows": rows,
      "sweptRecords": swept, "sweepChanges": sweep,
      "unavailable": UNAVAILABLE, "failures": failures}, ensure_ascii=False, indent=2))
  return 1 if failures else 0


if __name__ == "__main__":
  sys.exit(main())
