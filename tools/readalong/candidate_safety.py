"""Keep generation away from existing assets, revisions and book roots."""
from pathlib import Path
import math


def require_candidate_output(book_dir, output_dir):
  book = Path(book_dir).resolve(strict=True)
  output = Path(output_dir).resolve()
  if output == book or output.is_relative_to((book / "readalong").resolve()):
    raise ValueError("Generation cannot write active assets or the input root")
  if output.is_relative_to((book / ".readalong_revisions").resolve()):
    raise ValueError("Published revisions cannot be regenerated")
  if output.exists() and any(output.iterdir()):
    raise ValueError("Use a new empty candidate directory; old assets must not be overwritten")


def retired_write_entrypoint(*args, **kwargs):
  raise RuntimeError("Legacy entrypoint retired; use readalong_cli align/audit/publish explicitly")


def source_files(book_dir, suffixes):
  book = Path(book_dir)
  return [p for p in book.rglob("*") if p.is_file() and p.suffix.lower() in suffixes
          and not any(part.startswith(".") or part in {"readalong", "work", "text"}
                      for part in p.relative_to(book).parts)]


def alist_audio_path(book_dir, audio_file, alist_root):
  book = Path(book_dir).resolve()
  audio = Path(audio_file).resolve()
  parts = book.parts
  if "有声书" in parts:
    relative_book = Path(*parts[parts.index("有声书") + 1:])
  elif "未命名文件夹" in parts:
    relative_book = Path(*parts[parts.index("未命名文件夹") + 1:])
  else:
    # 兼容分卷多级目录：向上查找直到分类目录或取相对层级
    relative_book = Path(book.parent.name) / book.name
  return alist_root.rstrip("/") + "/" + (relative_book / audio.relative_to(book)).as_posix()


def plan_audio_blocks(duration, block_seconds):
  if not all(math.isfinite(v) and v > 0 for v in (duration, block_seconds)) or block_seconds < 1:
    raise ValueError("Finite positive duration and block size >= 1s required")
  start = 0.0
  while start < duration:
    end = min(duration, start + block_seconds)
    yield start, end - start
    start = end
