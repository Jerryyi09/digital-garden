"""Tiered verification system replacing slow full-library Alist scans (WO-RL-SENTENCE-20261026 Section 11:05).

Tier 1: Local static audit (sub-second, zero network, runs before/after publish_practical).
Tier 2: Single-batch remote SSH filesystem audit (sub-second, single SSH call, single process).
Tier 3: Single-book Alist API sample check (verifies Alist gateway layer for the batch).
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unicodedata
from bs4 import BeautifulSoup

from tools.readalong.full_inventory_scanner import natural_sort_key
from tools.readalong.nuc_target import NUC_SSH, NUC_TARGET, canonical_nuc_target, direct_ssh_command


def tier1_local_static_check(book_dir: Path) -> tuple[bool, list[str], dict]:
  """Tier 1: Thorough local static validation of a book before syncing. Zero network."""
  issues = []
  metrics = {}
  ra_dir = book_dir / "readalong"
  mf_path = ra_dir / "readalong.manifest.json"
  if not mf_path.is_file():
    return False, ["MANIFEST_MISSING"], {}

  try:
    manifest = json.loads(mf_path.read_text(encoding="utf-8"))
  except Exception as e:
    return False, [f"MANIFEST_JSON_INVALID: {e}"], {}

  # 1. 结构与版本目录
  if manifest.get("schemaVersion") != 1:
    issues.append("SCHEMA_VERSION_INVALID")

  asset_rev = manifest.get("assetRevision")
  if asset_rev and re.fullmatch(r"[a-f0-9]{32}", asset_rev):
    rev_dir = book_dir / ".readalong_revisions" / asset_rev
    if not rev_dir.is_dir():
      issues.append(f"REVISION_DIR_MISSING: {rev_dir}")
    source_base = rev_dir
  else:
    source_base = ra_dir

  tl_path = source_base / (manifest.get("timeline") or "timeline.json")
  if not tl_path.is_file():
    return False, [f"TIMELINE_FILE_MISSING: {tl_path}"], {}

  try:
    timeline = json.loads(tl_path.read_text(encoding="utf-8"))
  except Exception as e:
    return False, [f"TIMELINE_JSON_INVALID: {e}"], {}

  if not isinstance(timeline, list) or len(timeline) == 0:
    issues.append("TIMELINE_EMPTY")

  # 2. 正文文件与 fragment 锚点存在性、%xx URL 编码检测
  text_root = source_base / (manifest.get("textRoot") or "text/")
  checked_docs = {}
  parsed_spans = {}
  for seg in timeline:
    doc_rel = seg.get("document", "")
    if "%" in doc_rel:
      issues.append(f"DOCUMENT_PATH_URL_ENCODED: {doc_rel}")
      break

    if doc_rel not in checked_docs:
      doc_p = source_base / doc_rel
      if not doc_p.is_file():
        issues.append(f"DOCUMENT_FILE_MISSING: {doc_rel}")
        checked_docs[doc_rel] = False
      else:
        checked_docs[doc_rel] = True
        raw_html = doc_p.read_text(encoding="utf-8", errors="ignore")
        if ".readalong-active" not in raw_html:
          issues.append(f"HIGHLIGHT_CSS_MISSING_IN_DOC: {doc_rel}")
        soup = BeautifulSoup(raw_html, "html.parser")
        parsed_spans[doc_rel] = set(node["id"] for node in soup.find_all(id=True))

    frag = seg.get("fragment")
    if checked_docs.get(doc_rel) and frag not in parsed_spans.get(doc_rel, set()):
      issues.append(f"FRAGMENT_ANCHOR_MISSING: {doc_rel}#{frag}")
      if len(issues) > 10:
        break

  # 3. 音频源存在性、alistPath 一致性、自然排序检测
  audio_sources = manifest.get("audioSources", [])
  if not audio_sources:
    issues.append("AUDIO_SOURCES_EMPTY")

  source_names = [s.get("id") or s.get("name") for s in audio_sources]
  sorted_natural = sorted(source_names, key=natural_sort_key)
  if source_names != sorted_natural:
    issues.append(f"AUDIO_TRACKS_NOT_NATURALLY_SORTED: {source_names[:5]} vs {sorted_natural[:5]}")

  # 获取分类名与相对路径
  parts = book_dir.parts
  if "有声书" in parts:
    rel_book = Path(*parts[parts.index("有声书") + 1:]).as_posix()
  elif "未命名文件夹" in parts:
    rel_book = Path(*parts[parts.index("未命名文件夹") + 1:]).as_posix()
  else:
    rel_book = f"{book_dir.parent.name}/{book_dir.name}"

  for s in audio_sources:
    sid = s.get("id") or s.get("name")
    if not (book_dir / sid).is_file():
      issues.append(f"AUDIO_PHYSICAL_FILE_MISSING: {sid}")
    expected_alist = f"/750HD/有声书/{rel_book}/{sid}"
    if s.get("alistPath") != expected_alist:
      issues.append(f"ALIST_PATH_MISMATCH: got {s.get('alistPath')} expected {expected_alist}")

  # 4. 粒度指标计算
  durations = [s["end"] - s["start"] for s in timeline if s.get("end", 0) > s.get("start", 0)]
  import numpy as np
  med_dur = float(np.median(durations)) if durations else 0.0
  p95_dur = float(np.percentile(durations, 95)) if durations else 0.0
  fallback_count = sum(1 for s in timeline if s.get("timingStatus") == "SENTENCE_FROM_PARAGRAPH")
  fb_ratio = fallback_count / max(1, len(timeline))

  metrics["median_duration"] = round(med_dur, 2)
  metrics["p95_duration"] = round(p95_dur, 2)
  metrics["fallback_ratio"] = round(fb_ratio, 4)
  metrics["segments_count"] = len(timeline)

  if med_dur > 4.0:
    issues.append(f"MEDIAN_DURATION_TOO_HIGH: {med_dur:.2f}s > 4.0s")
  if p95_dur > 10.0:
    issues.append(f"P95_DURATION_TOO_HIGH: {p95_dur:.2f}s > 10.0s")
  metrics["fallback_segments_count"] = fallback_count
  metrics["fallback_granularity_note"] = "Fallback sentences highlight their containing paragraph and are reported separately from book-level pass/fail."

  return len(issues) == 0, issues, metrics


SSH_DIRECT_CMD = NUC_SSH[:-1]
DEFAULT_REMOTE_TARGET = NUC_TARGET


def tier2_remote_batch_check(remote_host: str = DEFAULT_REMOTE_TARGET, book_tuples: list[tuple] = None, remote_root: str = "/mnt/750/Music/有声书") -> tuple[bool, list[str]]:
  """Tier 2: Single SSH call batch filesystem audit of all modified books on NUC."""
  import base64
  payload_b64 = base64.b64encode(json.dumps(book_tuples).encode("utf-8")).decode("ascii")
  script = f"""python3 -c '
import json, sys, hashlib, re, base64
from pathlib import Path

root = Path("{remote_root}")
targets = json.loads(base64.b64decode("{payload_b64}").decode("utf-8"))
errors = []

for target in targets:
    cat, name, local_hash = target[:3]
    local_manifest_hash = target[3] if len(target) > 3 else None
    local_timeline_hash = target[4] if len(target) > 4 else None
    bdir = root / cat / name
    if not bdir.is_dir():
        errors.append(f"REMOTE_DIR_MISSING: {{cat}}/{{name}}")
        continue
    mf_path = bdir / "readalong/readalong.manifest.json"
    if not mf_path.is_file():
        errors.append(f"MANIFEST_MISSING: {{cat}}/{{name}}")
        continue
    m = json.loads(mf_path.read_text(encoding="utf-8"))
    if local_manifest_hash:
        remote_manifest_hash = hashlib.sha256(mf_path.read_bytes()).hexdigest()
        if remote_manifest_hash != local_manifest_hash:
            errors.append(f"MANIFEST_HASH_MISMATCH: {{cat}}/{{name}} local={{local_manifest_hash[:8]}} rem={{remote_manifest_hash[:8]}}")
    asset_rev = m.get("assetRevision")
    if asset_rev and re.fullmatch(r"[a-f0-9]{{32}}", asset_rev):
        s_base = bdir / ".readalong_revisions" / asset_rev
        if not s_base.is_dir():
            errors.append(f"REVISION_DIR_MISSING: {{cat}}/{{name}}/.readalong_revisions/{{asset_rev}}")
            continue
    else:
        s_base = bdir / "readalong"

    tl_path = s_base / (m.get("timeline") or "timeline.json")
    if not tl_path.is_file():
        errors.append(f"TIMELINE_MISSING: {{cat}}/{{name}}")
        continue
    if local_timeline_hash:
        remote_timeline_hash = hashlib.sha256(tl_path.read_bytes()).hexdigest()
        if remote_timeline_hash != local_timeline_hash:
            errors.append(f"TIMELINE_HASH_MISMATCH: {{cat}}/{{name}} local={{local_timeline_hash[:8]}} rem={{remote_timeline_hash[:8]}}")
    tl = json.loads(tl_path.read_text(encoding="utf-8"))

    # 音源文件与音轨 ID 校验
    sources = m.get("audioSources", [])
    known_ids = set(s.get("id") or s.get("name") for s in sources)
    for s in sources:
        sid = s.get("id") or s.get("name")
        if not (bdir / sid).is_file():
            errors.append(f"AUDIO_FILE_MISSING: {{cat}}/{{name}}/{{sid}}")
    for seg in tl[:50]: # quick sample
        aid = seg.get("audioSourceId")
        if aid and aid not in known_ids:
            errors.append(f"AUDIO_ID_UNMATCHED: {{cat}}/{{name}}/{{aid}}")
            break

    # 树哈希校验
    hasher = hashlib.sha256()
    text_root = s_base / (m.get("textRoot") or "text/")
    for p in sorted(text_root.rglob("*")):
        if p.is_file() and not p.name.startswith("._") and p.name != ".DS_Store":
            rel = p.relative_to(text_root).as_posix()
            hasher.update(rel.encode("utf-8"))
            hasher.update(p.read_bytes())
    rem_tree = hasher.hexdigest()
    if local_hash and rem_tree != local_hash:
        errors.append(f"TEXT_TREE_HASH_MISMATCH: {{cat}}/{{name}} local={{local_hash[:8]}} rem={{rem_tree[:8]}}")

if errors:
    print("FAILED:" + ";".join(errors))
    sys.exit(1)
print("TIER2_OK")
' """
  host = canonical_nuc_target(remote_host)
  res = subprocess.run(direct_ssh_command(host, script), capture_output=True, text=True)
  out = res.stdout.strip()
  if res.returncode == 0 and "TIER2_OK" in out:
    return True, []
  errs = out.replace("FAILED:", "").split(";") if "FAILED:" in out else [res.stderr.strip() or out]
  return False, errs


def tier3_alist_sample_check(category: str, book_name: str, remote_host: str = DEFAULT_REMOTE_TARGET) -> tuple[bool, str]:
  """Tier 3: Check 1 sample book via Alist API to prove gateway health."""
  from tools.readalong.nuc_verifier import verify_book_via_ssh
  host = canonical_nuc_target(remote_host)
  return verify_book_via_ssh(host, category, book_name)
