"""V5 Batch Pipeline Runner: Runs sentence mapping, publish_practical, and Tier 1-3 verification for an entire category."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
  sys.path.insert(0, str(repo_root))

from tools.readalong.practical_publisher import publish_practical
from tools.readalong.nuc_syncer import sync_book_to_nuc
from tools.readalong.tier_verifier import tier1_local_static_check, tier2_remote_batch_check, tier3_alist_sample_check
from tools.readalong.batch_candidate_remapper import sanitize_slug

LOCAL_ROOT = Path("/Users/jerryyi/Desktop/寒假/未命名文件夹")
CACHE_ROOT = repo_root / "private/readalong-cache"
RUNS_BASE = repo_root / "private/readalong-sentence-level-20261026/v5_runs"
RUNS_BASE.mkdir(parents=True, exist_ok=True)
py = str(repo_root / "tools/readalong/.venv/bin/python")


def dir_tree_hash(dir_path: Path):
  h = hashlib.sha256()
  for p in sorted(dir_path.rglob("*")):
    if p.is_file() and not p.name.startswith("._") and p.name != ".DS_Store":
      rel = p.relative_to(dir_path).as_posix()
      h.update(rel.encode("utf-8"))
      h.update(p.read_bytes())
  return h.hexdigest()


def published_text_root(book_dir: Path):
  manifest = json.loads((book_dir / "readalong" / "readalong.manifest.json").read_text(encoding="utf-8"))
  revision = manifest.get("assetRevision")
  source_base = book_dir / ".readalong_revisions" / revision if revision else book_dir / "readalong"
  return source_base / (manifest.get("textRoot") or "text/")


def published_tier2_hashes(book_dir: Path):
  manifest_path = book_dir / "readalong" / "readalong.manifest.json"
  manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
  revision = manifest.get("assetRevision")
  source_base = book_dir / ".readalong_revisions" / revision if revision else book_dir / "readalong"
  timeline_path = source_base / (manifest.get("timeline") or "timeline.json")
  return (
    dir_tree_hash(published_text_root(book_dir)),
    hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
    hashlib.sha256(timeline_path.read_bytes()).hexdigest(),
  )


def run_category_v5(category: str, max_books: int = None, existing_run_dir: Path = None):
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
      continue

    audit_res = json.loads(audit_path.read_text())
    decision = audit_res.get("decision", audit_res.get("readalongUsability"))
    publish_allowed = audit_res.get("publishAllowed") is True or decision in ("USABLE", "USABLE_WITH_GAPS")
    if not publish_allowed:
      print(f"  [EXCLUDE] {uid}: decision={decision}")
      batch_summary.append({"book": uid, "status": "EXCLUDED", "decision": decision})
      continue

    # 本地发布
    pub_res = publish_practical(bdir, cand_dir)
    assert pub_res.get("success"), f"Publish failed for {uid}: {pub_res}"

    # Tier 1 本地静态检验
    t1_ok, t1_issues, t1_metrics = tier1_local_static_check(bdir)
    if not t1_ok:
      print(f"  [TIER 1 FAILED] {uid}: {t1_issues}")
      batch_summary.append({"book": uid, "status": "TIER1_FAILED", "issues": t1_issues})
      continue

    # 4. SSH 安全同步至 NUC
    sync_book_to_nuc(bdir, category, book_name, remote_host="hp", remote_base="/mnt/750/Music/有声书")
    active_manifest = json.loads((bdir / "readalong" / "readalong.manifest.json").read_text(encoding="utf-8"))
    synced_for_tier2.append((category, book_name, *published_tier2_hashes(bdir)))
    batch_summary.append({
      "book": uid, "status": "SYNCED", "metrics": t1_metrics,
      "decision": decision, "revision": active_manifest.get("assetRevision")
    })
    print(f"  [TIER 1 OK] {uid} (median={t1_metrics['median_duration']}s, p95={t1_metrics['p95_duration']}s, synced)")

  # 4. Tier 2 服务器单进程文件级核验
  print(f"\n[4/5] Executing Tier 2 single-call server filesystem audit ({len(synced_for_tier2)} books)...")
  t0_t2 = time.perf_counter()
  t2_ok, t2_errs = tier2_remote_batch_check("hp", synced_for_tier2)
  t2_time = time.perf_counter() - t0_t2
  if not t2_ok:
    print(f"  [TIER 2 FAILED] Server audit failed: {t2_errs}")
    raise RuntimeError("Tier 2 verification failed")
  print(f"  [TIER 2 PASSED] in {t2_time:.2f}s! All {len(synced_for_tier2)} books verified on server filesystem.")

  # 5. Tier 3 Alist 网关抽样（整批抽 1 本）
  sample_cat, sample_book, _ = synced_for_tier2[0]
  print(f"\n[5/5] Executing Tier 3 Alist gateway sample check on {sample_cat}/{sample_book}...")
  t0_t3 = time.perf_counter()
  t3_ok, t3_msg = tier3_alist_sample_check(sample_cat, sample_book, remote_host="hp")
  t3_time = time.perf_counter() - t0_t3
  if not t3_ok:
    print(f"  [TIER 3 FAILED] Alist check failed: {t3_msg}")
    raise RuntimeError("Tier 3 verification failed")
  print(f"  [TIER 3 PASSED] in {t3_time:.2f}s! Alist gateway verified functional.")

  total_time = time.perf_counter() - t_batch_start

  # 输出批次摘要 Markdown
  report_file = repo_root / f"private/readalong-sentence-level-20261026/V5_BATCH_{category}.md"
  md = f"# V5 分批滚动重跑报告：【{category}】分类\n\n"
  md += f"- **完成时间**：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
  md += f"- **总耗时**：{total_time:.1f}s（ASR映射：{asr_time:.1f}s，Tier 2：{t2_time:.2f}s，Tier 3：{t3_time:.2f}s）\n"
  md += f"- **同步并核验通过图书**：**{len(synced_for_tier2)}** 本\n\n"
  md += "| 书名 | 状态 | 句级段数 | 时长中位数 (≤4s) | 时长 95 分位 (≤10s) | 兜底占比 (≤10%) | 版本号 |\n"
  md += "|---|:---:|:---:|:---:|:---:|:---:|:---:|\n"
  for item in batch_summary:
    if item["status"] == "SYNCED":
      m = item["metrics"]
      md += f"| ✅ **{item['book']}** | `OK` | {m['segments_count']} | **{m['median_duration']}s** | {m['p95_duration']}s | {m['fallback_ratio']:.1%} | `{item['revision'][:8]}` |\n"
    else:
      md += f"| ⚠️ **{item['book']}** | `{item['status']}` | - | - | - | - | - |\n"

  report_file.write_text(md, encoding="utf-8")
  print(f"\nBatch summary saved to: {report_file}")
  return batch_summary


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("category", help="Category name, e.g. 心智成长")
  parser.add_argument("--max-books", type=int, default=None)
  parser.add_argument("--existing-run-dir", type=Path, default=None)
  args = parser.parse_args()
  run_category_v5(args.category, max_books=args.max_books, existing_run_dir=args.existing_run_dir)
