"""Report logger for readalong alignment and validation events.

Appends timestamped execution logs and validation audit tables to
the Obsidian deliverable documentation:
'22 有声书音文同步映射检验记录.md'
"""

import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DOC_PATH = Path(
  "/Users/jerryyi/Library/Mobile Documents/iCloud~md~obsidian/Documents/学习笔记/03 Archives/Rosemary Garden/交付版本 01 文档/22 有声书音文同步映射检验记录.md"
)

HEADER_TEMPLATE = """# 22 有声书音文同步映射检验记录

> **文档定位**：本文是 Rosemary Garden 花园听书（Rosemary Listen）音文同步映射与合规检验的自动化执行日志与审计报告文档，记录每次批量或单书映射对齐、时间轴单调性检验、片段覆盖度与外置盘部署交付的历史明细与状态追踪。
> **归档位置**：`学习笔记/03 Archives/Rosemary Garden/交付版本 01 文档/`
> **更新机制**：自动化映射与检验工具链执行完毕后自动以时间戳条目追加写入。

---
"""


def ensure_doc_header() -> None:
  """Ensure the deliverable document exists with the initial standard header."""
  DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
  if not DOC_PATH.exists() or DOC_PATH.stat().st_size == 0:
    DOC_PATH.write_text(HEADER_TEMPLATE, encoding="utf-8")


def append_markdown_block(block: str) -> None:
  """Safely append a markdown block to the deliverable document."""
  ensure_doc_header()
  current_text = DOC_PATH.read_text(encoding="utf-8")
  if not current_text.endswith("\n"):
    current_text += "\n"
  new_text = current_text + "\n" + block.strip() + "\n"
  DOC_PATH.write_text(new_text, encoding="utf-8")


def log_alignment_report(
  batch_name: str,
  results: List[Dict[str, Any]],
  duration_s: float,
  notes: Optional[str] = None
) -> None:
  """Record an alignment execution batch to the document."""
  now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  lines = [
    f"## [{now_str}] 音文同步映射对齐执行记录 - {batch_name}",
    "",
    f"- **执行耗时**：{duration_s:.1f} 秒 ({duration_s / 60:.2f} 分钟)",
    f"- **处理书籍数**：{len(results)} 本",
  ]
  if notes:
    lines.append(f"- **备注说明**：{notes}")

  lines.extend([
    "",
    "| 书籍名称 | 状态 | 音轨数 | 句段总数 (segmentCount) | 覆盖范围 / 详情 |",
    "| :--- | :---: | :---: | :---: | :--- |"
  ])

  for r in results:
    name = r.get("book_name", "未知")
    status = r.get("status", "未知")
    status_badge = "✅ 成功" if status == "success" else f"❌ {status}"
    tracks = r.get("tracks_count", 0)
    segs = r.get("segment_count", 0)
    details = r.get("details", "-")
    lines.append(f"| **{name}** | {status_badge} | {tracks} | {segs} | {details} |")

  lines.append("")
  append_markdown_block("\n".join(lines))


def log_validation_report(
  target_root: str,
  passed_books: List[Dict[str, Any]],
  failed_books: List[Dict[str, Any]],
  notes: Optional[str] = None
) -> None:
  """Record a manifest & timeline validation audit to the document."""
  now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  total = len(passed_books) + len(failed_books)
  pass_rate = (len(passed_books) / total * 100.0) if total > 0 else 0.0

  lines = [
    f"## [{now_str}] 音文同步资产完整性检验报告",
    "",
    f"- **审计目录**：`{target_root}`",
    f"- **合规汇总**：共审计 **{total}** 本书籍，**{len(passed_books)}** 本通过，**{len(failed_books)}** 本异常（合规率: **{pass_rate:.1f}%**）",
  ]
  if notes:
    lines.append(f"- **核验要点**：{notes}")

  lines.extend([
    "",
    "| 书籍名称 | 检验结论 | 映射片段数 | 音轨数 | 详情 / 异常说明 |",
    "| :--- | :---: | :---: | :---: | :--- |"
  ])

  for b in passed_books:
    name = b.get("name", "未知")
    segs = b.get("segment_count", "-")
    tracks = b.get("track_count", "-")
    lines.append(f"| **{name}** | ✅ 100% 合规 | {segs} | {tracks} | 时间戳单调递增，HTML 与 fragment 校验无误 |")

  for b in failed_books:
    name = b.get("name", "未知")
    errs = "; ".join(b.get("errors", [])[:3])
    if len(b.get("errors", [])) > 3:
      errs += f" (共 {len(b.get('errors'))} 项问题)"
    lines.append(f"| **{name}** | ❌ 校验未通过 | - | - | {errs} |")

  lines.append("")
  append_markdown_block("\n".join(lines))


def log_deployment_report(
  dest_volume: str,
  synced_books: List[Dict[str, Any]],
  notes: Optional[str] = None
) -> None:
  """Record deployment and synchronization to external volume."""
  now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  lines = [
    f"## [{now_str}] 外置存储盘部署与同步交付记录",
    "",
    f"- **目标盘符/挂载点**：`{dest_volume}`",
    f"- **同步书籍数**：{len(synced_books)} 本",
  ]
  if notes:
    lines.append(f"- **部署说明**：{notes}")

  lines.extend([
    "",
    "| 书籍名称 | 目标相对路径 | 资产状态 | 校验状态 |",
    "| :--- | :--- | :---: | :---: |"
  ])

  for s in synced_books:
    name = s.get("name", "未知")
    path = s.get("path", "-")
    status = s.get("status", "已同步")
    val_status = s.get("validation", "已校验")
    lines.append(f"| **{name}** | `{path}` | {status} | {val_status} |")

  lines.append("")
  append_markdown_block("\n".join(lines))
