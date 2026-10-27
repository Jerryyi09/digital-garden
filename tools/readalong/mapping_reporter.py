"""Readalong mapping quality auditor and actionable edition advisor.

Analyzes the benchmark execution results (benchmark.json, practical-audit.json,
timeline shards) for a batch run or single-book run. Produces a structured
summary report and actionable edition/EPUB replacement suggestions for books
that exhibit mismatches, chunking, or drifting, extracting edition clues (publisher,
translator, narrator, publication year, version) directly from audio metadata and
opening spoken credits.
"""
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import statistics
import subprocess
import sys


def extract_audio_edition_clues(book_dir: Path, asr_cache_root: Path = None) -> dict:
  """Extract edition clues (publisher, translator, narrator, year, version) from audio tags and opening ASR."""
  if not book_dir or not book_dir.is_dir():
    return {}

  audio_files = sorted(p for p in book_dir.iterdir()
                       if p.is_file() and p.suffix.lower() in (".mp3", ".m4b", ".m4a"))
  if not audio_files:
    return {}

  first_track = audio_files[0]
  clues = {}

  # 1. ffprobe format tags
  try:
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(first_track)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    if r.returncode == 0:
      tags = json.loads(r.stdout).get("format", {}).get("tags", {})
      clues["author"] = tags.get("artist") or tags.get("album_artist")
      clues["album"] = tags.get("album")
      clues["year"] = tags.get("date") or tags.get("year")
      clues["publisher"] = tags.get("publisher") or tags.get("organization") or tags.get("label")
      clues["comment"] = tags.get("comment")
      if not clues.get("year") and tags.get("creation_time"):
        clues["year"] = tags["creation_time"][:4]
  except Exception:
    pass

  # 2. Opening ASR spoken credits from cache
  opening_asr = ""
  if asr_cache_root and asr_cache_root.is_dir():
    try:
      from tools.readalong_fast.pipeline import SpeechCache
      from tools.readalong.input_inventory import model_fingerprint
      from tools.readalong.config import resolve_model_path
      sha = hashlib.sha256(first_track.read_bytes()).hexdigest()
      cache = SpeechCache(asr_cache_root, [asr_cache_root], model_fingerprint(resolve_model_path()), False, asr_engine="words")
      words = cache.chunk_words(first_track, sha, 0, 1800)
      if words:
        opening_asr = " ".join(w.get("word", "") for w in words[:120])
    except Exception:
      pass

  # If opening_asr is available, extract regex clues
  if opening_asr:
    clues["openingQuote"] = opening_asr[:140] + ("..." if len(opening_asr) > 140 else "")
    if not clues.get("publisher"):
      m_pub = re.search(r"(?:([A-Za-z0-9\s&]+?)\s+(?:audio\s+presents|presents|audiobooks?|media|publishing))", opening_asr, re.I)
      if m_pub:
        clues["publisher"] = m_pub.group(1).strip() + " Audio"
    if not clues.get("author"):
      m_written = re.search(r"(?:written by|by)\s+([A-Za-z\s]+?)(?:,\s*read by|\.\s*read by|read by|\band\b|\bwith\b|\bincludes\b|\bfor\b)", opening_asr, re.I)
      if m_written:
        clues["author"] = m_written.group(1).strip()
    if not clues.get("narrator"):
      m_narrator = re.search(r"(?:read by|narrated by|performed by)\s+([A-Za-z\s]+?)(?:,\s*|\.\s*|\bincludes\b|\bfor\b|\bwith\b|\bcopyright\b)", opening_asr, re.I)
      if m_narrator:
        clues["narrator"] = m_narrator.group(1).strip()
    if not clues.get("translator"):
      m_trans = re.search(r"(?:translated by|translation by)\s+([A-Za-z\s]+?)(?:,\s*|\.\s*|\bread by\b|\bfor\b)", opening_asr, re.I)
      if m_trans:
        clues["translator"] = m_trans.group(1).strip()
    if not clues.get("year"):
      m_year = re.search(r"(?:copyright|published in|recorded in|\(c\)|©)\s*(?:[a-zA-Z\s]+)?(19\d{2}|20\d{2})", opening_asr, re.I)
      if m_year:
        clues["year"] = m_year.group(1).strip()

  return {k: v for k, v in clues.items() if v}


def analyze_unit_quality(run_dir: Path, record: dict, asr_cache_root: Path = None, library_root: Path = None) -> dict:
  """Analyze a single book's timeline, audit metrics and edition clues."""
  uid = record.get("unit_id", "")
  usability = record.get("readalongUsability", "UNKNOWN")
  screen_decision = record.get("screenDecision")
  screen_detail = record.get("screenDetail") or {}
  metrics = record.get("metrics") or {}
  timings = record.get("timings") or {}
  total_seconds = timings.get("totalSeconds", 0.0)
  unmapped_ratio = metrics.get("unmappedSpeechUnitRatio")

  # Find the book's output folder in the run directory
  candidates = []
  run_root = run_dir / "run" if (run_dir / "run").is_dir() else run_dir
  for p in run_root.iterdir():
    if not p.is_dir():
      continue
    mf = p / "readalong.manifest.json"
    if mf.is_file():
      try:
        m = json.loads(mf.read_text(encoding="utf-8"))
        if m.get("bookId") == uid or m.get("bookId") == uid.split("/")[-1]:
          candidates.append((p, m))
      except Exception:
        pass

  timeline = []
  audit_data = {}
  cand_dir = None
  if candidates:
    cand_dir, manifest = candidates[0]
    audit_file = cand_dir / "practical-audit.json"
    if audit_file.is_file():
      try:
        audit_data = json.loads(audit_file.read_text(encoding="utf-8"))
      except Exception:
        pass
    from tools.readalong.timeline_shards import load_timeline_payload
    try:
      timeline = load_timeline_payload(cand_dir, manifest)
    except Exception:
      timeline = []

  counts = Counter(s.get("timingStatus") for s in timeline)
  exact_count = counts.get("SENTENCE_EXACT", 0)
  partial_count = counts.get("SENTENCE_PARTIAL", 0)
  fallback_count = counts.get("SENTENCE_FROM_PARAGRAPH", 0)
  unverified_count = counts.get("TIMING_UNVERIFIED", 0)
  durations = [s["end"] - s["start"] for s in timeline if s.get("end", 0) > s.get("start", 0)]
  median_duration = statistics.median(durations) if durations else 0.0
  total_segments = len(timeline) or metrics.get("timelineSegments", 0)

  # Problem categorization
  is_mismatch = (screen_decision == "SAMPLE_MISMATCH"
                 or record.get("materialMismatchConfirmed") is True
                 or usability in ("REVIEW_MAPPING", "EXCLUDE_PRACTICAL_CANDIDATE")
                 or (unmapped_ratio is not None and unmapped_ratio > 0.15))

  is_paragraph_chunked = (not is_mismatch and (
    median_duration > 3.8
    or (total_segments > 0 and (fallback_count / (total_segments - unverified_count + 1e-9)) > 0.50
        and median_duration > 2.8)
  ))

  is_drift_or_gapped = (not is_mismatch and not is_paragraph_chunked and (
    (unmapped_ratio is not None and unmapped_ratio > 0.03)
    or (metrics.get("unalignedTrackCount", 0) > 0)
    or (len(audit_data.get("longUnexplainedIntervals", [])) > 2)
  ))

  # Locate physical book dir on local SSD to extract edition clues
  book_name = uid.split("/")[-1]
  book_dir = None
  if library_root and library_root.is_dir():
    for cat_dir in library_root.iterdir():
      if not cat_dir.is_dir():
        continue
      cand_bdir = cat_dir / book_name
      if cand_bdir.is_dir():
        book_dir = cand_bdir
        break

  clues = extract_audio_edition_clues(book_dir, asr_cache_root) if book_dir else {}

  # Format search keywords suggestion
  search_terms = [f'"{book_name}"']
  if clues.get("author"):
    search_terms.append(f'"{clues["author"]}"')
  if clues.get("publisher"):
    search_terms.append(f'"{clues["publisher"]}"')
  if clues.get("translator"):
    search_terms.append(f'"{clues["translator"]}"')
  if clues.get("year"):
    search_terms.append(f'"{clues["year"]}"')
  search_cmd = " ".join(search_terms) + " (格式优先: EPUB / 无删节版)"

  clues_summary = []
  if clues.get("publisher"):
    clues_summary.append(f"• 出版/制作机构: {clues['publisher']}")
  if clues.get("author"):
    clues_summary.append(f"• 原作者: {clues['author']}")
  if clues.get("narrator"):
    clues_summary.append(f"• 演播者: {clues['narrator']}")
  if clues.get("translator"):
    clues_summary.append(f"• 译者: {clues['translator']}")
  if clues.get("year"):
    clues_summary.append(f"• 出版/录制年份: {clues['year']}")
  if clues.get("album"):
    clues_summary.append(f"• 专辑/版本标注: {clues['album']}")
  if clues.get("comment"):
    clues_summary.append(f"• 来源/备注: {clues['comment']}")
  if clues.get("openingQuote"):
    clues_summary.append(f"• 开篇语音播报片段: \"{clues['openingQuote']}\"")

  clues_block = "\n".join(f"     {line}" for line in clues_summary) if clues_summary else "     (未提取到明显的音频元数据标签)"

  if is_mismatch:
    level = "MISMATCH"
    tag = "[严重错配 需换底本]"
    reason = "音频朗读文本与电子书底本不属于同一出版版本（译本差异、古典改写本或有声书为删节版本）。"
    advisory = (
      f"1. 【音频提取的录音底本线索】:\n{clues_block}\n"
      f"2. 【EPUB 换版精准搜索指令】:\n"
      f"     👉 请在 z-library 搜索: {search_cmd}\n"
      f"3. 【音频核对】: 检查当前音频是否为 Unabridged (完整无删节版)；若音频为 Abridged 删节版，建议重新下载完整全本音频。"
    )
  elif is_paragraph_chunked:
    level = "CHUNKED"
    tag = "[高亮整段 建议换版]"
    reason = f"高亮中位数达 {median_duration:.2f}s (偏粗)。EPUB 内部缺少标准 <p> 段落划分 (整章放在单一容器)，分句受限降级为整段高亮。"
    advisory = (
      f"1. 【音频提取的录音底本线索】:\n{clues_block}\n"
      f"2. 【EPUB 换版建议】: 当前 EPUB 可能由非标准工具或 PDF 转换导出。建议在 z-library 搜索更换排版规范（带标准 <p> 标签分段）的标准出版社版本:\n"
      f"     👉 请在 z-library 搜索: {search_cmd}\n"
      f"3. 播放体验: 若不换版仍可跟读，但视口高亮将以整大段为单位滚动，缺乏逐句跟随精度。"
    )
  elif is_drift_or_gapped:
    level = "DRIFT"
    tag = "[局部漂移 建议核对]"
    reason = f"未定位率达 {unmapped_ratio*100:.2f}% 或存在部分未对齐音轨，演播者可能跳读了前言、附录、小标题或存在局部插图说明空洞。"
    advisory = (
      f"1. 【音频提取的录音底本线索】:\n{clues_block}\n"
      f"2. 【物料核查建议】: 检查是否有音频包含多余的导读/访谈/片头宣告未在正文中体现。\n"
      f"3. 【例外声明】: 若属已知演播差异，可在 material-exceptions.json 中添加该书的免责区间，无需换书即可发布。"
    )
  else:
    level = "PASS"
    tag = "[质量优质 可发布]"
    reason = f"句级高亮中位数 {median_duration:.2f}s，未定位率仅 {unmapped_ratio*100:.2f}%，精排句级覆盖良好。"
    advisory = "符合 personal-readalong-5pct-v1 实用发布标准，可直接进行本地发布与直连同步。"

  return {
    "unit_id": uid,
    "usability": usability,
    "screen_decision": screen_decision,
    "unmapped_ratio": unmapped_ratio,
    "total_segments": total_segments,
    "exact_count": exact_count,
    "partial_count": partial_count,
    "fallback_count": fallback_count,
    "unverified_count": unverified_count,
    "median_duration": median_duration,
    "total_seconds": total_seconds,
    "aligned_tracks": metrics.get("alignedTrackCount", 0),
    "unaligned_tracks": metrics.get("unalignedTrackCount", 0),
    "level": level,
    "tag": tag,
    "reason": reason,
    "advisory": advisory,
    "cand_dir": cand_dir,
    "clues": clues,
  }


def generate_mapping_report(run_dir_path: str, target_path: str) -> str:
  """Analyze run directory and print formatted report and advisories."""
  run_dir = Path(run_dir_path).resolve()
  target = Path(target_path).resolve()
  bench_path = run_dir / "run" / "benchmark.json"
  if not bench_path.is_file():
    bench_path = run_dir / "benchmark.json"
  if not bench_path.is_file():
    print(f"ERROR: No benchmark.json found in {run_dir}")
    return ""

  benchmark_data = json.loads(bench_path.read_text(encoding="utf-8"))
  records = benchmark_data.get("records", [])

  # Resolve cache root and library root
  repo_root = Path(__file__).resolve().parent.parent.parent
  cache_root = repo_root / "private/readalong-cache"
  library_root = Path("/Users/jerryyi/Desktop/寒假/未命名文件夹")

  analyzed = [analyze_unit_quality(run_dir, r, cache_root, library_root) for r in records]

  # Count statistics
  total_books = len(analyzed)
  pass_count = sum(1 for a in analyzed if a["level"] == "PASS")
  chunked_count = sum(1 for a in analyzed if a["level"] == "CHUNKED")
  drift_count = sum(1 for a in analyzed if a["level"] == "DRIFT")
  mismatch_count = sum(1 for a in analyzed if a["level"] == "MISMATCH")
  total_time = sum(a["total_seconds"] for a in analyzed)

  lines = []
  lines.append("=" * 102)
  lines.append(f"                 有声书映射质量评估与换版本建议报告 (Readalong Mapping Report)")
  lines.append(f"  目标路径: {target}")
  lines.append(f"  批次目录: {run_dir}")
  lines.append(f"  处理图书: 共 {total_books} 本 | 优质通过: {pass_count} 本 | 粒度偏粗: {chunked_count} 本 | 局部漂移: {drift_count} 本 | 严重错配: {mismatch_count} 本")
  lines.append(f"  总耗时:   {total_time:.1f} 秒")
  lines.append("=" * 102)
  lines.append("")

  # Table header
  header = f"{'图书名称 (Unit ID)':<38} {'综合判定':<16} {'句级段数':<10} {'高亮中位':<10} {'未定位率':<10} {'耗时'}"
  lines.append(header)
  lines.append("-" * 102)

  for a in analyzed:
    uid = a["unit_id"]
    if len(uid) > 36:
      uid = uid[:33] + "..."
    tag = a["tag"]
    segs = f"{a['exact_count'] + a['partial_count']}/{a['total_segments']}"
    med = f"{a['median_duration']:.2f}s" if a['median_duration'] > 0 else "N/A"
    unm = f"{a['unmapped_ratio']*100:.2f}%" if a['unmapped_ratio'] is not None else "N/A"
    sec = f"{a['total_seconds']:.1f}s"
    lines.append(f"{uid:<38} {tag:<16} {segs:<10} {med:<10} {unm:<10} {sec}")

  lines.append("=" * 102)
  lines.append("")

  # Section: Detailed Advisories for Problem Books
  problem_books = [a for a in analyzed if a["level"] != "PASS"]
  if problem_books:
    lines.append("【问题图书诊断与换版本建议清单 (Actionable Edition Advisories)】")
    lines.append("=" * 102)
    for idx, a in enumerate(problem_books, 1):
      lines.append(f"\n{idx}. 图书: 《{a['unit_id']}》 ---> {a['tag']}")
      lines.append(f"   [物理现象] 总段数: {a['total_segments']}, 句级精排: {a['exact_count']}, 中位数: {a['median_duration']:.2f}s, 未定位率: {a['unmapped_ratio']*100 if a['unmapped_ratio'] is not None else 0:.2f}%")
      lines.append(f"   [根本原因] {a['reason']}")
      lines.append(f"   [换版本具体指引]")
      for adv_line in a['advisory'].split("\n"):
        lines.append(f"  {adv_line}")
    lines.append("\n" + "=" * 102)
  else:
    lines.append("🎉 全部图书均达到高质量句级同步标准，无需更换版本！")
    lines.append("=" * 102)

  # Actionable next steps
  lines.append("\n【后续操作指引】")
  if pass_count > 0:
    lines.append(f"  ✅ 达到发布标准的图书 ({pass_count} 本)，可使用以下命令执行本地发布、同步 NUC 与三层核验：")
    lines.append(f"     scripts/readalong-publish-nuc \"{run_dir}\"")
  if problem_books:
    lines.append(f"  ⚠️  建议更换版本的图书 ({len(problem_books)} 本)：参考上述从音频提取的出版社、译者、年份线索更换 EPUB/音频后，重新运行 mapping 即可。")
  lines.append("=" * 102)

  report_text = "\n".join(lines)
  # Write markdown copy to run_dir
  report_file = run_dir / "MAPPING_REPORT.md"
  try:
    report_file.write_text(report_text, encoding="utf-8")
  except Exception:
    pass

  return report_text


def main():
  if len(sys.argv) < 3:
    print("Usage: python -m tools.readalong.mapping_reporter <run_dir> <target>")
    sys.exit(1)
  report = generate_mapping_report(sys.argv[1], sys.argv[2])
  if report:
    print(report)


if __name__ == "__main__":
  main()
