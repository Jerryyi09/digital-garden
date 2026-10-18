"""Installer for deploying generated readalong assets to local library or NUC."""

import json
from pathlib import Path
import shutil

from tools.readalong.config import DEFAULT_OUTPUT_DIR


def plan_installation(
    book_id: str,
    target_dir: Path,
    output_base: Path | None = None,
) -> dict:
    """Plan the exact files and directories to install."""
    source_dir = (output_base or DEFAULT_OUTPUT_DIR) / book_id
    if not source_dir.exists():
        raise FileNotFoundError(f"Generated output directory not found: {source_dir}")

    manifest_path = source_dir / "readalong.manifest.json"
    timeline_path = source_dir / "timeline.json"
    text_dir = source_dir / "text"

    if not manifest_path.exists() or not timeline_path.exists() or not text_dir.exists():
        raise FileNotFoundError(
            f"Missing required readalong files in {source_dir}. Run align first."
        )

    files_to_copy = []
    # 1. Manifest
    files_to_copy.append({
        "src": str(manifest_path),
        "dest": str(target_dir / "readalong.manifest.json"),
        "rel": "readalong.manifest.json",
    })
    # 2. Timeline
    files_to_copy.append({
        "src": str(timeline_path),
        "dest": str(target_dir / "timeline.json"),
        "rel": "timeline.json",
    })
    # 3. Text files
    for item in text_dir.rglob("*"):
        if item.is_file():
            rel = item.relative_to(source_dir).as_posix()
            files_to_copy.append({
                "src": str(item),
                "dest": str(target_dir / rel),
                "rel": rel,
            })

    return {
        "book_id": book_id,
        "source_dir": str(source_dir),
        "target_dir": str(target_dir),
        "file_count": len(files_to_copy),
        "files": files_to_copy,
    }


def execute_installation(
    plan: dict,
    dry_run: bool = False,
) -> dict:
    """Execute the installation plan."""
    target_dir = Path(plan["target_dir"])
    if dry_run:
        return {
            "status": "dry_run",
            "file_count": plan["file_count"],
            "target_dir": str(target_dir),
            "files": [f["rel"] for f in plan["files"]],
        }

    target_dir.mkdir(parents=True, exist_ok=True)
    for entry in plan["files"]:
        src = Path(entry["src"])
        dest = Path(entry["dest"])
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)

    return {
        "status": "installed",
        "file_count": plan["file_count"],
        "target_dir": str(target_dir),
    }
