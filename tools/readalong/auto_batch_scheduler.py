"""Autonomous batch scheduler for readalong library mapping, audit, and publication.

Iterates over categories sequentially (never concurrently to honor MLX/ASR single-threaded safety).
For each category:
  1. Ensures metadata (cover.jpg and summary.txt) are present.
  2. Runs scripts/readalong-map.
  3. If publishable candidates exist, runs scripts/readalong-publish-nuc.
  4. Records metrics, passes, and actionable edition advisories.
  5. Continues to the next category without stopping on individual book failures.
"""
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LOCAL_BASE = Path("/Users/jerryyi/Desktop/寒假/未命名文件夹")
CACHE_ROOT = REPO_ROOT / "private/readalong-cache"
RUNS_BASE = REPO_ROOT / "private/readalong-library-runs"
PYTHON = REPO_ROOT / "tools/readalong/.venv/bin/python"


def prepare_category_metadata(cat_dir: Path):
  """Ensure cover.jpg and summary.txt exist before mapping to guarantee Tier 3 Alist pass."""
  for bdir in cat_dir.iterdir():
    if not bdir.is_dir() or bdir.name.startswith("."):
      continue
    epubs = list(bdir.glob("*.epub"))
    audios = list(bdir.glob("*.mp3")) + list(bdir.glob("*.m4b")) + list(bdir.glob("*.m4a"))
    if not epubs or not audios:
      continue

    # Cover
    cover_p = bdir / "cover.jpg"
    if not cover_p.is_file():
      jpgs = [p for p in bdir.iterdir() if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg") and not p.name.startswith(".")]
      if jpgs:
        shutil.copy2(jpgs[0], cover_p)
      else:
        try:
          with zipfile.ZipFile(epubs[0]) as z:
            for n in z.namelist():
              if any(ext in n.lower() for ext in (".jpg", ".jpeg", ".png")):
                cover_p.write_bytes(z.read(n))
                break
        except Exception:
          pass

    # Summary
    sum_p = bdir / "summary.txt"
    if not sum_p.is_file():
      desc_text = ""
      try:
        with zipfile.ZipFile(epubs[0]) as z:
          c_xml = z.read("META-INF/container.xml")
          root = ET.fromstring(c_xml)
          opf_path = root.find(".//{*}rootfile").attrib["full-path"]
          opf = ET.fromstring(z.read(opf_path))
          desc = opf.find(".//{*}metadata/{*}description")
          if desc is not None and desc.text:
            desc_text = BeautifulSoup(desc.text, "html.parser").get_text("\n", strip=True)
      except Exception:
        pass
      if not desc_text:
        desc_text = f"《{bdir.name}》有声书与精排电子书阅读。"
      sum_p.write_text(desc_text, encoding="utf-8")


def process_category(cat_name: str) -> dict:
  """Run full map -> verify -> publish pipeline for one category."""
  t0 = time.perf_counter()
  cat_dir = LOCAL_BASE / cat_name
  print(f"\n{'='*80}")
  print(f"  [START CATEGORY] {cat_name} ({cat_dir})")
  print(f"{'='*80}")

  # 1. Prepare metadata
  print(f"[*] Preparing metadata (covers & summaries) for {cat_name}...")
  prepare_category_metadata(cat_dir)

  # 2. Run readalong-map
  print(f"[*] Executing scripts/readalong-map for {cat_name}...")
  map_cmd = [str(REPO_ROOT / "scripts/readalong-map"), str(cat_dir)]
  map_res = subprocess.run(map_cmd, capture_output=True, text=True)
  print(map_res.stdout[-2500:] if len(map_res.stdout) > 2500 else map_res.stdout)
  if map_res.returncode != 0:
    print(f"  [ERROR] mapping script failed with exit code {map_res.returncode}: {map_res.stderr[-500:]}")
    return {"category": cat_name, "status": "MAP_FAILED", "error": map_res.stderr[-500:]}

  # Find the latest run folder for this category
  runs = sorted(RUNS_BASE.glob(f"{cat_name}-*"), key=lambda p: p.stat().st_mtime)
  if not runs:
    print(f"  [ERROR] No run directory found for {cat_name}")
    return {"category": cat_name, "status": "NO_RUN_DIR"}
  latest_run = runs[-1]

  # 3. Check benchmark results and run publication if publishable candidates exist
  bench_path = latest_run / "run" / "benchmark.json"
  if not bench_path.is_file():
    bench_path = latest_run / "benchmark.json"

  publishable_count = 0
  if bench_path.is_file():
    bdata = json.loads(bench_path.read_text(encoding="utf-8"))
    for r in bdata.get("records", []):
      if r.get("readalongUsability") in ("USABLE_WITH_GAPS", "SAMPLE_PASS") and not r.get("materialMismatchConfirmed"):
        publishable_count += 1

  pub_ok = False
  pub_msg = ""
  if publishable_count > 0:
    print(f"\n[*] Found {publishable_count} publishable book(s). Executing scripts/readalong-publish-nuc...")
    pub_cmd = [str(REPO_ROOT / "scripts/readalong-publish-nuc"), str(latest_run)]
    pub_res = subprocess.run(pub_cmd, capture_output=True, text=True)
    print(pub_res.stdout[-2000:] if len(pub_res.stdout) > 2000 else pub_res.stdout)
    if pub_res.returncode == 0:
      pub_ok = True
      print(f"  [SUCCESS] Tier 1/2/3 verification and NUC sync PASSED for {cat_name}!")
    else:
      pub_msg = pub_res.stderr[-500:]
      print(f"  [WARNING] Publication failed for {cat_name}: {pub_msg}")
  else:
    print(f"  [NOTICE] No publishable books in {cat_name} (all skipped or mismatched).")

  elapsed = time.perf_counter() - t0
  return {
    "category": cat_name,
    "status": "COMPLETED",
    "elapsed_seconds": elapsed,
    "run_dir": str(latest_run),
    "publishable_count": publishable_count,
    "published": pub_ok,
    "pub_error": pub_msg,
  }


def main():
  categories_to_run = sys.argv[1:] if len(sys.argv) > 1 else [
    "英文读写",
    "传记",
    "政治",
    "自然博物",
    "历史",
    "数理化",
    "哲学",
    "社会文化",
    "科学技术",
    "商业经济"
  ]

  print(f"Starting autonomous pipeline over {len(categories_to_run)} categories:")
  for idx, cat in enumerate(categories_to_run, 1):
    print(f"  {idx:02d}. {cat}")

  results = []
  t_total = time.perf_counter()
  for idx, cat in enumerate(categories_to_run, 1):
    print(f"\n>>> [{idx}/{len(categories_to_run)}] PROCESSING: {cat} <<<")
    res = process_category(cat)
    results.append(res)
    print(f">>> FINISHED: {cat} in {res.get('elapsed_seconds', 0):.1f}s <<<\n")

  total_time = time.perf_counter() - t_total
  print("\n" + "="*80)
  print(f"ALL CATEGORIES FINISHED in {total_time/60:.1f} minutes!")
  print("="*80)
  for r in results:
    print(f"  {r['category']:<20} | Status: {r['status']:<10} | Publishable: {r.get('publishable_count', 0)} | Published: {r.get('published')} | Elapsed: {r.get('elapsed_seconds', 0):.1f}s")


if __name__ == "__main__":
  main()
