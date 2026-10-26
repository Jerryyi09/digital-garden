"""Runner and evaluator for V2 benchmark: Comparing new sentence-level pipeline against the 4 recognized books."""
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path
from difflib import SequenceMatcher
import numpy as np

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
  sys.path.insert(0, str(repo_root))

BOOKS = [
  "101 Essays That Will Change The Way You Think",
  "Clear Thinking",
  "Make Your Bed",
  "Think Like a Psychologist"
]

LOCAL_CATEGORY = Path("/Users/jerryyi/Desktop/寒假/未命名文件夹/心智成长")
OUTPUT_BASE = Path("/Users/jerryyi/digital-garden/private/readalong-sentence-level-20261026/runs")
OUTPUT_BASE.mkdir(parents=True, exist_ok=True)


def evaluate_timelines(old_tl: list, new_tl: list):
  # 1. 每次高亮时长分布
  new_durations = [s["end"] - s["start"] for s in new_tl if s.get("end", 0) > s.get("start", 0)]
  new_median_dur = float(np.median(new_durations)) if new_durations else 0.0
  new_p90_dur = float(np.percentile(new_durations, 90)) if new_durations else 0.0

  # 2. 兜底句子比例
  fallback_count = sum(1 for s in new_tl if s.get("timingStatus") == "SENTENCE_FROM_PARAGRAPH")
  fallback_ratio = fallback_count / max(1, len(new_tl))

  # 3. 逐句对应偏差比对（按文本规范化后做 SequenceMatcher）
  from tools.readalong_fast.sentence_aligner import normalize_token
  old_texts = [" ".join(normalize_token(w) for w in s.get("text", "").split() if normalize_token(w)) for s in old_tl]
  new_texts = [" ".join(normalize_token(w) for w in s.get("text", "").split() if normalize_token(w)) for s in new_tl]

  matcher = SequenceMatcher(None, old_texts, new_texts, autojunk=False)
  diffs = []
  for a_idx, b_idx, size in matcher.get_matching_blocks():
    if size <= 0:
      continue
    for step in range(size):
      old_s = old_tl[a_idx + step].get("start", 0.0)
      new_s = new_tl[b_idx + step].get("start", 0.0)
      diffs.append(abs(new_s - old_s))

  median_diff = float(np.median(diffs)) if diffs else 999.0
  p90_diff = float(np.percentile(diffs, 90)) if diffs else 999.0

  return {
    "old_count": len(old_tl),
    "new_count": len(new_tl),
    "matched_eval_sentences": len(diffs),
    "median_start_diff": median_diff,
    "p90_start_diff": p90_diff,
    "new_median_duration": new_median_dur,
    "new_p90_duration": new_p90_dur,
    "fallback_ratio": fallback_ratio
  }


def main():
  results = {}
  repo_root = Path(__file__).resolve().parents[2]
  py = str(repo_root / "tools/readalong/.venv/bin/python")

  for book in BOOKS:
    book_dir = LOCAL_CATEGORY / book
    old_tl_path = book_dir / "readalong/timeline.json"
    if not old_tl_path.exists():
      print(f"Skipping {book}: no old timeline")
      continue

    old_tl = json.loads(old_tl_path.read_text())
    out_dir = OUTPUT_BASE / book.replace(" ", "_")

    print(f"\n==========================================")
    print(f"Running sentence mapping for: {book}")
    print(f"==========================================")
    t0 = time.perf_counter()

    # 1. 扫描库存 (root 传分类目录)
    inv_dir = out_dir / "inv"
    inv_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([py, "-m", "tools.readalong.full_inventory_scanner", str(inv_dir), "--root", str(LOCAL_CATEGORY)],
                   check=True, stdout=subprocess.DEVNULL)
    inv_path = inv_dir / "inventory.json"

    # 2. 运行 benchmark (asr_engine=words)
    run_dir = out_dir / "run"
    if run_dir.exists():
      import shutil
      shutil.rmtree(run_dir)

    subprocess.run([
      py, "-m", "tools.readalong_fast.benchmark",
      "--inventory", str(inv_path),
      "--output", str(run_dir),
      "--cache-read-root", str(repo_root / "private/readalong-cache"),
      "--allow-new-asr",
      "--asr-engine", "words",
      "--unit", f"心智成长/{book}"
    ], check=True)

    elapsed = time.perf_counter() - t0
    new_tl_path = run_dir / "timeline.json"
    if not new_tl_path.exists():
      # check slug
      from tools.readalong.batch_candidate_remapper import sanitize_slug
      slug = sanitize_slug(f"心智成长/{book}")
      new_tl_path = run_dir / slug / "timeline.json"

    new_tl = json.loads(new_tl_path.read_text())
    eval_res = evaluate_timelines(old_tl, new_tl)
    eval_res["elapsed_seconds"] = round(elapsed, 1)
    results[book] = eval_res
    print(f"Completed {book}: {eval_res}")

  # 写入 Markdown 汇总报告
  report_md = "# V2 对照实验汇总报告（4本旧流程逐句跟读标杆）\n\n"
  report_md += "| 书名 | 旧版句数 | 新版句数 | 匹配对比句数 | 句首偏差中位数 (≤0.3s) | 句首偏差 90 分位 (≤1.0s) | 高亮时长中位数 (≤4s) | 兜底占比 (≤10%) | 耗时 |\n"
  report_md += "|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n"

  all_passed = True
  for b, r in results.items():
    p1 = r["median_start_diff"] <= 0.3
    p2 = r["p90_start_diff"] <= 1.0
    p3 = r["new_median_duration"] <= 4.0
    p4 = r["fallback_ratio"] <= 0.10
    passed = p1 and p2 and p3 and p4
    all_passed = all_passed and passed
    pass_mark = "✅" if passed else "❌"
    report_md += f"| {pass_mark} **{b}** | {r['old_count']} | {r['new_count']} | {r['matched_eval_sentences']} | **{r['median_start_diff']:.2f}s** | {r['p90_start_diff']:.2f}s | **{r['new_median_duration']:.2f}s** | {r['fallback_ratio']:.1%} | {r['elapsed_seconds']}s |\n"

  summary_path = repo_root / "private/readalong-sentence-level-20261026/V2_BENCHMARK.md"
  summary_path.write_text(report_md, encoding="utf-8")
  print(f"\nV2 Summary saved to {summary_path}")
  print(f"All V2 thresholds passed: {all_passed}")


if __name__ == "__main__":
  main()
