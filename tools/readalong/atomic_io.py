"""Small dependency-free durable JSON writes for audit and publication."""
import json
import os
from pathlib import Path
import tempfile


def atomic_json(path, data):
  path = Path(path)
  path.parent.mkdir(parents=True, exist_ok=True)
  fd, temporary = tempfile.mkstemp(prefix='.checkpoint-', dir=path.parent)
  try:
    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
      json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
      stream.write('\n')
      stream.flush()
      os.fsync(stream.fileno())
    os.replace(temporary, path)
  finally:
    if os.path.exists(temporary):
      os.unlink(temporary)
