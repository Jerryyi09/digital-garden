"""V5 Batch Pipeline Runner: Runs sentence mapping, publish_practical, and Tier 1-3 verification for an entire category."""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import sys
import time

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
  sys.path.insert(0, str(repo_root))

from tools.readalong.practical_publisher import publish_practical, rollback_practical
from tools.readalong.nuc_syncer import sync_book_to_nuc
from tools.readalong.tier_verifier import tier1_local_static_check, tier2_remote_batch_check, tier3_alist_sample_check
from tools.readalong.batch_candidate_remapper import sanitize_slug
from tools.readalong.nuc_target import NUC_REMOTE_BASE, NUC_TARGET, nuc_publication_lock
from tools.readalong.release_integrity import tier2_book_payload

LOCAL_ROOT = Path("/Users/jerryyi/Desktop/寒假/未命名文件夹")
CACHE_ROOT = repo_root / "private/readalong-cache"
RUNS_BASE = repo_root / "private/readalong-sentence-level-20261026/v5_runs"
RUNS_BASE.mkdir(parents=True, exist_ok=True)
py = str(repo_root / "tools/readalong/.venv/bin/python")


def has_audio_only_receipt(book_dir: Path):
  manifest_path = book_dir / "readalong" / "readalong.manifest.json"
  if not manifest_path.is_file():
    return False
  manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
  if manifest.get("readalongEnabled") is False or manifest.get("practicalRelease", {}).get("decision") == "AUDIO_ONLY":
    return True
  revisions = book_dir / ".readalong_revisions"
  for receipt_path in revisions.glob("*/release-receipt.json"):
    try:
      receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
      continue
    if receipt.get("exclusionReason") and receipt.get("revision") == manifest.get("assetRevision"):
      return True
  return False


def tier3_batch_sample(synced_for_tier2, remote_host=NUC_TARGET):
  if not synced_for_tier2:
    return True, "SKIPPED_NO_SYNC"
  category, book_name = synced_for_tier2[0][:2]
  return tier3_alist_sample_check(category, book_name, remote_host=remote_host)


def _run_category_v5_unlocked(category: str, max_books: int = None, existing_run_dir: Path = None, include_excluded: bool = False):
  t_batch_start = time.perf_counter()
  cat_dir = LOCAL_ROOT / category
  if not cat_dir.is_dir():
    raise ValueError(f"Category directory not found: {cat_dir}")

  stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M")
  batch_out = existing_run_dir.parent if existing_run_dir else (RUNS_BASE / f"{category}-{stamp}")
  batch_out.mkdir(parents=True, exist_ok=True)

  print(f"\n==================================================")
  print(f"Starting V5 Batch for Category: {category}")
  print(f"Output directory: {batch_out}")
  print(f"==================================================")

  # 1. 扫描分类库存
  inv_dir = batch_out / "inv"
  inv_dir.mkdir(parents=True, exist_ok=True)
  print(f"[1/5] Scanning inventory for {category}...")
  if not (inv_dir / "inventory.json").exists():
    subprocess.run([py, "-m", "tools.readalong.full_inventory_scanner", str(inv_dir), "--root", str(cat_dir)],
                   check=True, stdout=subprocess.DEVNULL)
  inv = json.loads((inv_dir / "inventory.json").read_text())

  units = [u for u in inv["units"] if u.get("audio_tracks") and u.get("epubs")]
  excluded_units = []
  if not include_excluded:
    kept = []
    for unit in units:
      if has_audio_only_receipt(LOCAL_ROOT / unit["unit_id"]):
        excluded_units.append(unit)
      else:
        kept.append(unit)
    units = kept
  if max_books:
    units = units[:max_books]
  print(f"  Found {len(units)} valid book units to process.")

  # 2. 批量运行句级 benchmark 映射
  run_dir = existing_run_dir or (batch_out / "run")
  asr_time = 0.0
  if not (run_dir / "benchmark.json").exists():
    print(f"\n[2/5] Running sentence-level mapping with mlx-batch-silence-words-v1...")
    unit_args = []
    for u in units:
      unit_args.extend(["--unit", u["unit_id"]])

    cmd = [
      py, "-m", "tools.readalong_fast.benchmark",
      "--inventory", str(inv_dir / "inventory.json"),
      "--output", str(run_dir),
      "--cache-read-root", str(CACHE_ROOT),
      "--allow-new-asr",
      "--asr-engine", "words"
    ] + unit_args
    t0_asr = time.perf_counter()
    subprocess.run(cmd, check=True)
    asr_time = time.perf_counter() - t0_asr
    print(f"  Mapping completed in {asr_time:.1f}s.")
  else:
    print(f"\n[2/5] Reusing existing completed benchmark mapping from {run_dir}...")

  # 3. 本地 Tier 1 静态检验与原子发布
  print(f"\n[3/5] Publishing locally & applying Tier 1 static audit...")
  synced_for_tier2 = []
  batch_summary = []
  for unit in excluded_units:
    batch_summary.append({"book": unit["unit_id"], "status": "EXCLUDED_AUDIO_ONLY",
      "decision": "AUDIO_ONLY", "reason": "Existing user exclusion receipt; pass --include-excluded to override"})

  for u in units:
    uid = u["unit_id"]
    book_name = u["rel_path"]
    bdir = LOCAL_ROOT / uid
    slug = sanitize_slug(uid)
    cand_dir = run_dir / slug
    if not cand_dir.exists():
      cand_dir = run_dir

    audit_path = cand_dir / "practical-audit.json"
    if not audit_path.exists():
      print(f"  [SKIP] No practical audit found for {uid}")
      batch_summary.append({"book": uid, "status": "REVIEW", "decision": "NO_PRACTICAL_AUDIT",
        "unmapped_ratio": None, "checks": ["PRACTICAL_AUDIT_MISSING"]})
      continue

    audit_res = json.loads(audit_path.read_text())
    decision = audit_res.get("decision", audit_res.get("readalongUsability"))
    publish_allowed = audit_res.get("publishAllowed") is True or decision in ("USABLE", "USABLE_WITH_GAPS")
    if not publish_allowed:
      print(f"  [EXCLUDE] {uid}: decision={decision}")
      metrics = audit_res.get("metrics", {})
      batch_summary.append({"book": uid, "status": "REVIEW" if decision == "REVIEW_MAPPING" else "EXCLUDED",
        "decision": decision, "unmapped_ratio": metrics.get("unmappedSpeechUnitRatio", metrics.get("unmappedLexicalEstimate")),
        "checks": audit_res.get("reasons") or audit_res.get("hardErrors") or ["publishAllowed=false"]})
      continue

    # 本地发布
    pub_res = publish_practical(bdir, cand_dir)
    assert pub_res.get("success"), f"Publish failed for {uid}: {pub_res}"

    # Tier 1 本地静态检验
    t1_ok, t1_issues, t1_metrics = tier1_local_static_check(bdir)
    if not t1_ok:
      print(f"  [TIER 1 FAILED] {uid}: {t1_issues}")
      revision = pub_res.get("revision") or Path(pub_res.get("revision_dir", "")).name
      rollback_result = rollback_practical(bdir, revision) if revision else {"success": False, "reason": "publish result omitted revision id"}
      if not rollback_result.get("success"):
        raise RuntimeError(f"Tier 1 failed for {uid}; rollback failed: {rollback_result}")
      batch_summary.append({"book": uid, "status": "TIER1_FAILED_ROLLED_BACK", "checks": t1_issues,
        "metrics": t1_metrics, "decision": decision,
        "unmapped_ratio": audit_res.get("metrics", {}).get("unmappedSpeechUnitRatio",
          audit_res.get("metrics", {}).get("unmappedLexicalEstimate"))})
      continue

    # 4. SSH 安全同步至 NUC
    sync_result = sync_book_to_nuc(bdir, category, book_name, remote_host=NUC_TARGET, remote_base=NUC_REMOTE_BASE)
    active_manifest = json.loads((bdir / "readalong" / "readalong.manifest.json").read_text(encoding="utf-8"))
    synced_for_tier2.append(tier2_book_payload(sync_result["category"], sync_result["book_name"], bdir))
    batch_summary.append({
      "book": uid, "status": "SYNCED", "metrics": t1_metrics,
      "decision": decision, "revision": active_manifest.get("assetRevision")
    })
    print(f"  [TIER 1 OK] {uid} (median={t1_metrics['median_duration']}s, p95={t1_metrics['p95_duration']}s, synced)")

  # 4. Tier 2 服务器单进程文件级核验
  print(f"\n[4/5] Executing Tier 2 single-call server filesystem audit ({len(synced_for_tier2)} books)...")
  t0_t2 = time.perf_counter()
  t2_ok, t2_errs = tier2_remote_batch_check(NUC_TARGET, synced_for_tier2) if synced_for_tier2 else (True, [])
  t2_time = time.perf_counter() - t0_t2
  if not t2_ok:
    print(f"  [TIER 2 FAILED] Server audit failed: {t2_errs}")
    raise RuntimeError("Tier 2 verification failed")
  print(f"  [TIER 2 PASSED] in {t2_time:.2f}s! All {len(synced_for_tier2)} books verified on server filesystem.")

  # 5. Tier 3 Alist 网关抽样（整批抽 1 本）
  t3_time = 0.0
  if synced_for_tier2:
    sample_cat, sample_book = synced_for_tier2[0][:2]
    print(f"\n[5/5] Executing Tier 3 Alist gateway sample check on {sample_cat}/{sample_book}...")
    t0_t3 = time.perf_counter()
    t3_ok, t3_msg = tier3_batch_sample(synced_for_tier2, remote_host=NUC_TARGET)
    t3_time = time.perf_counter() - t0_t3
    if not t3_ok:
      raise RuntimeError(f"Tier 3 Alist check failed: {t3_msg}")
    print(f"  [TIER 3 PASSED] in {t3_time:.2f}s! Alist gateway verified functional.")
  else:
    tier3_batch_sample(synced_for_tier2, remote_host=NUC_TARGET)
    print("\n[5/5] Tier 3 skipped: no books were synchronized in this batch.")

  total_time = time.perf_counter() - t_batch_start

  # 输出批次摘要 Markdown
  report_file = repo_root / f"private/readalong-sentence-level-20261026/V5_BATCH_{category}.md"
  md = f"# V5 分批滚动重跑报告：【{category}】分类\n\n"
  md += f"- **完成时间**：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
  md += f"- **总耗时**：{total_time:.1f}s（ASR映射：{asr_time:.1f}s，Tier 2：{t2_time:.2f}s，Tier 3：{t3_time:.2f}s）\n"
  md += f"- **同步并核验通过图书**：**{len(synced_for_tier2)}** 本\n\n"
  benchmark_summary = json.loads((run_dir / "benchmark.json").read_text(encoding="utf-8")) if (run_dir / "benchmark.json").is_file() else {}
  new_decode_seconds = sum(float(r.get("speechCacheStats", {}).get("newAsrAudioSeconds", 0)) for r in benchmark_summary.get("records", []))
  md += f"- **已识别缓存被重复送入 ASR 秒数**：0.00s（按缓存命中不调用解码器的实现路径计）；本轮缓存缺失导致的新识别：{new_decode_seconds:.2f}s。\n\n"
  md += "| 书名 | 状态 | 句级段数 | 时长中位数 (≤4s) | 时长 95 分位 (≤10s) | 兜底占比 (≤10%) | 版本号 |\n"
  md += "|---|:---:|:---:|:---:|:---:|:---:|:---:|\n"
  for item in batch_summary:
    if item["status"] == "SYNCED":
      m = item["metrics"]
      md += f"| ✅ **{item['book']}** | `OK` | {m['segments_count']} | **{m['median_duration']}s** | {m['p95_duration']}s | {m['fallback_ratio']:.1%} | `{item['revision'][:8]}` |\n"
    else:
      why = "; ".join(map(str, item.get("checks", [item.get("reason", item.get("decision", "no check passed"))])))
      rate = item.get("unmapped_ratio")
      rate_text = "n/a" if rate is None else f"{float(rate):.2%}"
      md += f"| ⚠️ **{item['book']}** | `{item['status']}: {item.get('decision', '')}; unmapped={rate_text}; checks={why}` | - | - | - | - | - |\n"

  report_file.write_text(md, encoding="utf-8")
  print(f"\nBatch summary saved to: {report_file}")
  return batch_summary


def run_category_v5(category: str, max_books: int = None, existing_run_dir: Path = None, include_excluded: bool = False):
  with nuc_publication_lock():
    return _run_category_v5_unlocked(category, max_books=max_books, existing_run_dir=existing_run_dir,
                                    include_excluded=include_excluded)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("category", help="Category name, e.g. 心智成长")
  parser.add_argument("--max-books", type=int, default=None)
  parser.add_argument("--existing-run-dir", type=Path, default=None)
  parser.add_argument("--include-excluded", action="store_true", help="Explicitly process books with AUDIO_ONLY exclusion receipts")
  args = parser.parse_args()
  run_category_v5(args.category, max_books=args.max_books, existing_run_dir=args.existing_run_dir,
                  include_excluded=args.include_excluded)
