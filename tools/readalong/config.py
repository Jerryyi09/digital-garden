"""Configuration and path management for the readalong alignment toolkit."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_DIR = PROJECT_ROOT / "private" / "audiobook-validation" / "power-of-habit" / "runtime-snapshot"

DEFAULT_MODEL_PATH = SNAPSHOT_DIR / "models" / "tiny.en"
DEFAULT_NLTK_DATA = SNAPSHOT_DIR / "nltk_data"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "private" / "readalong-output"

DEFAULT_ALIST_ROOT = "/750HD/有声书"
DEFAULT_LOCAL_ROOT = "/Volumes/750/Music/有声书"

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
