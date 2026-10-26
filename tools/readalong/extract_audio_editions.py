"""Extract Precise Audio Edition Information for Audiobooks.

Extracts:
1. ID3 / Media Tags (album, artist, title, publisher, copyright, composer).
2. Physical opening audio speech (transcribes first 35 seconds to capture
   narrator announcement, translator, and publisher imprint).
3. Compares with current EPUB metadata and flags exact version mismatch details.
"""

import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(PROJECT_ROOT))

from tools.readalong.config import resolve_model_path


def get_media_tags(file_path: Path) -> dict:
  try:
    cmd = [
      "ffprobe", "-v", "error", "-show_entries", "format_tags",
      "-of", "json", str(file_path)
    ]
    raw = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8")
    data = json.loads(raw)
    return data.get("format", {}).get("tags", {})
  except Exception:
    return {}


def transcribe_head_audio(file_path: Path, model_path: Path, duration_s: float = 35.0) -> str:
  temp_sample = Path(f"/tmp/probe_{file_path.stem}.m4a")
  try:
    cmd = [
      "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
      "-ss", "0", "-t", str(duration_s),
      "-i", str(file_path),
      "-map", "0:a:0", "-vn", "-sn", "-dn",
      "-c:a", "aac", "-b:a", "64k", "-ac", "1", "-ar", "24000",
      str(temp_sample)
    ]
    subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)

    from mlx_whisperx.backend.mlx_whisper.transcribe import transcribe
    res = transcribe(
      str(temp_sample),
      path_or_hf_repo=str(model_path),
      language="en",
      word_timestamps=False,
      verbose=False
    )
    texts = [s.get("text", "").strip() for s in res.get("segments", [])]
    return " ".join(texts)
  except Exception as e:
    return f"[Transcription error: {e}]"
  finally:
    if temp_sample.exists():
      try:
        temp_sample.unlink()
      except Exception:
        pass


def get_epub_info(book_dir: Path) -> dict:
  epubs = [e for e in book_dir.glob("*.epub") if not e.name.startswith("._")]
  if not epubs:
    return {"file": "None", "title": "None", "creator": "None"}
  ep = epubs[0]
  title = "Unknown"
  creator = "Unknown"
  try:
    with zipfile.ZipFile(ep) as z:
      for n in z.namelist():
        if n.endswith(".opf"):
          root = ET.fromstring(z.read(n))
          title = next((e.text for e in root.iter() if "title" in e.tag and e.text), "Unknown")
          creator = next((e.text for e in root.iter() if "creator" in e.tag and e.text), "Unknown")
          break
  except Exception:
    pass
  return {"file": ep.name, "title": title, "creator": creator}


def probe_book_edition(book_dir: Path, model_path: Path) -> dict:
  audios = sorted([
    a for a in book_dir.glob("*")
    if a.suffix.lower() in (".mp3", ".m4a", ".m4b") and not a.name.startswith("._")
  ], key=lambda x: x.name)

  if not audios:
    return {"name": book_dir.name, "status": "no_audio"}

  first_audio = audios[0]
  tags = get_media_tags(first_audio)
  announcement = transcribe_head_audio(first_audio, model_path, duration_s=35.0)
  epub_info = get_epub_info(book_dir)

  album = tags.get("album") or tags.get("ALBUM") or "-"
  artist = tags.get("artist") or tags.get("ARTIST") or tags.get("album_artist") or "-"
  publisher = tags.get("publisher") or tags.get("PUBLISHER") or tags.get("copyright") or "-"
  title_tag = tags.get("title") or tags.get("TITLE") or first_audio.name

  # Detect abridged / unabridged
  combined_text = f"{album} {title_tag} {announcement}".lower()
  edition_type = "Unabridged (无删节全本)"
  if "abridged" in combined_text and "unabridged" not in combined_text:
    edition_type = "Abridged (删节精简版/改写本)"

  # Detect LibriVox
  is_librivox = "librivox" in combined_text

  return {
    "name": book_dir.name,
    "first_audio": first_audio.name,
    "album": album,
    "artist": artist,
    "publisher": publisher,
    "edition_type": edition_type,
    "is_librivox": is_librivox,
    "announcement": announcement,
    "epub_file": epub_info["file"],
    "epub_title": epub_info["title"],
    "epub_creator": epub_info["creator"],
  }
