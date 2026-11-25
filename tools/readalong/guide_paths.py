"""Local-only output paths shared by standalone guide generators."""
import os
from pathlib import Path


def guide_category_path(category):
  root = Path(os.environ.get("READALONG_LIBRARY_ROOT", "/Users/jerryyi/Desktop/寒假/未命名文件夹")).expanduser().resolve()
  if root == Path("/Volumes") or Path("/Volumes") in root.parents:
    raise ValueError("Guide generation requires a local SSD path, not /Volumes")
  return str(root / category)
