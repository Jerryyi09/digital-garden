"""Runner and evaluator for V3 benchmark: 3 representative books (Nexus, AI Explained, 麦田里的守望者)."""
import json
import math
import subprocess
import sys
import time
from pathlib import Path
import numpy as np

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
  sys.path.insert(0, str(repo_root))

BOOKS = [
  ("计算机与AI", "Nexus"),
  ("计算机与AI", "AI Explained"),
  ("文学作品", "麦田里的守望者")
]

LOCAL_ROOT = Path("/Users/jerryyi/Desktop/寒假/未命名文件夹")
OUTPUT_BASE = repo_root / "private/readalong-sentence-level-20261026/v3_runs"
OUTPUT_BASE.mkdir(parents=True, exist_ok=True)


def main():
  results = {}
  py = str(repo_root / "tools/readalong/.venv/bin/python")

  for cat, book in BOOKS:
    book_dir = LOCAL_ROOT / cat / book
    out_dir = OUTPUT_BASE / f"{cat}_{book}".replace(" ", "_")

    print(f"\n==========================================")
    print(f"Running V3 sentence mapping for: {cat}/{book}")
    print(f"==========================================")
    t0 = time.perf_counter()

    # 1. 扫描库存
    inv_dir = out_dir / "inv"
    inv_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([py, "-m", "tools.readalong.full_inventory_scanner", str(inv_dir), "--root", str(LOCAL_ROOT / cat)],
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
      "--unit", f"{cat}/{book}"
    ], check=True)

    elapsed = time.perf_counter() - t0

    # 3. 提取结果指标
    from tools.readalong.batch_candidate_remapper import sanitize_slug
    slug = sanitize_slug(f"{cat}/{book}")
    cand_dir = run_dir / slug
    if not cand_dir.exists():
      cand_dir = run_dir

    new_tl = json.loads((cand_dir / "timeline.json").read_text())
    audit_rep = json.loads((cand_dir / "practical-audit.json").read_text())

    durations = [s["end"] - s["start"] for s in new_tl if s.get("end", 0) > s.get("start", 0)]
    median_dur = float(np.median(durations)) if durations else 0.0
    p95_dur = float(np.percentile(durations, 95)) if durations else 0.0

    fallback_count = sum(1 for s in new_tl if s.get("timingStatus") == "SENTENCE_FROM_PARAGRAPH")
    fallback_ratio = fallback_count / max(1, len(new_tl))

    metrics = audit_rep.get("metrics") or {}
    unmapped_ratio = metrics.get("unmappedSpeechUnitRatio") or 0.0

    results[f"{cat}/{book}"] = {
      "segments": len(new_tl),
      "median_duration": median_dur,
      "p95_duration": p95_dur,
      "fallback_ratio": fallback_ratio,
      "unmapped_ratio": unmapped_ratio,
      "decision": audit_rep.get("decision", audit_rep.get("readalongUsability")),
      "elapsed_seconds": round(elapsed, 1)
    }
    print(f"Completed {cat}/{book}: {results[f'{cat}/{book}']}")

  # 写入 Markdown 汇总报告
  report_md = "# V3 代表书验证汇总报告（Nexus, AI Explained, 麦田里的守望者）\n\n"
  report_md += "| 书名 | 句级段数 | 时长中位数 (≤4s) | 时长 95 分位 (≤10s) | 兜底占比 (≤10%) | 未定位语音占比 | 审核判定 | 耗时 |\n"
  report_md += "|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n"

  all_passed = True
  for name, r in results.items():
    p1 = r["median_duration"] <= 4.0
    p2 = r["p95_duration"] <= 10.0
    p3 = r["fallback_ratio"] <= 0.10
    passed = p1 and p2 and p3
    all_passed = all_passed and passed
    pass_mark = "✅" if passed else "❌"
    report_md += f"| {pass_mark} **{name}** | {r['segments']} | **{r['median_duration']:.2f}s** | {r['p95_duration']:.2f}s | **{r['fallback_ratio']:.1%}** | {r['unmapped_ratio']:.2%} | {r['decision']} | {r['elapsed_seconds']}s |\n"

  summary_path = repo_root / "private/readalong-sentence-level-20261026/V3_REPRESENTATIVE.md"
  summary_path.write_text(report_md, encoding="utf-8")
  print(f"\nV3 Summary saved to {summary_path}")
  print(f"All V3 thresholds passed: {all_passed}")


if __name__ == "__main__":
  main()
