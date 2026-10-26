"""Configuration and path management for the readalong alignment toolkit."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_DIR = PROJECT_ROOT / "private" / "audiobook-validation" / "power-of-habit" / "runtime-snapshot"

DEFAULT_MODEL_PATH = SNAPSHOT_DIR / "models" / "tiny.en"
DEFAULT_NLTK_DATA = SNAPSHOT_DIR / "nltk_data"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "private" / "readalong-output"

DEFAULT_ALIST_ROOT = "/750HD/有声书"
# Processing source is the local SSD library. /Volumes/750 is only the NUC deploy target, never a scan/map/verify source.
DEFAULT_LOCAL_ROOT = "/Users/jerryyi/Desktop/寒假/未命名文件夹"

# Pinned model checksums
EXPECTED_MODEL_CHECKSUMS = {
    "config.json": "452e616242261333a661bc86db762b3720d6cc7e2eccd3d8e19a631871c26dd9",
    "weights.npz": "4627203f0807d6496dda0d200e893b04ff24c98e73aa51c485c06203a0330b17",
}


def resolve_model_path(model_arg: str | None = None) -> Path:
    """Resolve ASR model path prioritizing local snapshot, env vars, or user cache."""
    if model_arg:
        arg_path = Path(model_arg)
        if arg_path.exists():
            return arg_path

    env_path = os.environ.get("READALONG_MODEL_PATH")
    if env_path and Path(env_path).exists():
        return Path(env_path)

    if DEFAULT_MODEL_PATH.exists():
        return DEFAULT_MODEL_PATH

    cache_model = Path.home() / ".cache" / "digital-garden" / "models" / "tiny.en"
    if cache_model.exists():
        return cache_model

    return DEFAULT_MODEL_PATH


def resolve_nltk_data_path(nltk_arg: str | None = None) -> Path:
    """Resolve NLTK punkt_tab tokenizer data directory."""
    if nltk_arg:
        arg_path = Path(nltk_arg)
        if arg_path.exists():
            return arg_path

    env_path = os.environ.get("NLTK_DATA") or os.environ.get("READALONG_NLTK_DATA")
    if env_path and Path(env_path).exists():
        return Path(env_path)

    if DEFAULT_NLTK_DATA.exists():
        return DEFAULT_NLTK_DATA

    cache_nltk = Path.home() / ".cache" / "digital-garden" / "nltk_data"
    return cache_nltk


DEFAULT_CACHE_ROOT = PROJECT_ROOT / "private" / "readalong-cache"

def resolve_transcripts_cache_dir() -> Path:
    """Resolve ASR transcripts persistent cache directory."""
    env_path = os.environ.get("READALONG_CACHE_ROOT")
    if env_path:
        p = Path(env_path)
        p.mkdir(parents=True, exist_ok=True)
        return p
    if DEFAULT_CACHE_ROOT.exists():
        return DEFAULT_CACHE_ROOT
    p = Path.home() / ".cache" / "digital-garden" / "transcripts"
    p.mkdir(parents=True, exist_ok=True)
    return p


def transcript_cache_candidates(name: str) -> list[Path]:
    """Look up exact content/parameter keys in additional read-only caches."""
    roots = [resolve_transcripts_cache_dir()]
    roots.extend(Path(p) for p in os.environ.get("READALONG_CACHE_READ_ROOTS", "").split(os.pathsep) if p)
    return [root / name for root in roots]
