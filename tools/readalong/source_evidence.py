"""Bounded source verification; persistent reuse is explicitly opt-in."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
from threading import Lock

from tools.readalong.atomic_io import atomic_json


def identity(path):
  st = Path(path).stat()
  return [st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns]


class SourceEvidence:
  def __init__(self, hash_reader, duration_reader, workers=4, cache_path=None):
    if workers not in (1, 2, 3, 4):
      raise ValueError('workers must be between 1 and 4')
    self.hash_reader, self.duration_reader = hash_reader, duration_reader
    self.workers = workers
    self.path = Path(cache_path) if cache_path else None
    self.rows, self.reused, self.used, self.lock = {}, set(), set(), Lock()
    if self.path and self.path.exists():
      payload = json.loads(self.path.read_text())
      if payload.get('version') != 1 or not isinstance(payload.get('rows'), dict):
        raise ValueError('Invalid source evidence cache')
      self.rows = payload['rows']
    self.loaded = set(self.rows)

  def read(self, path, kind):
    path = Path(path).resolve(strict=True)
    key = str(path)+'|'+kind
    before = identity(path)
    with self.lock:
      self.used.add(key)
    entry = self.rows.get(key)
    if entry and entry.get('stat') == before:
      with self.lock:
        if key in self.loaded:
          self.reused.add(key)
      return entry['value']
    value = (self.hash_reader if kind == 'sha256' else self.duration_reader)(path)
    if identity(path) != before:
      raise ValueError('Source changed while verifying: '+str(path))
    with self.lock:
      self.loaded.discard(key)
      self.rows[key] = {'stat': before, 'value': value,
        'verifiedAt': datetime.now(timezone.utc).isoformat()}
    return value

  def sha256(self, path):
    return self.read(path, 'sha256')

  def duration(self, path):
    return self.read(path, 'duration')

  def prefetch(self, paths):
    def collect(path):
      try:
        self.sha256(path)
        self.duration(path)
      except OSError:
        # Missing files remain ordered diagnostics in the original validator.
        pass
    if len(paths) > 1 and self.workers > 1:
      with ThreadPoolExecutor(max_workers=self.workers) as pool:
        list(pool.map(collect, paths))
    else:
      for path in paths:
        collect(path)

  def finish(self):
    if self.path:
      atomic_json(self.path, {'version': 1, 'rows': self.rows})

  def ensure_stable(self):
    for key in self.used:
      if key in self.rows and identity(key.rsplit('|', 1)[0]) != self.rows[key]['stat']:
        raise ValueError('Source changed during audit: '+key)

  def disclosure(self):
    return {'mode': 'incremental-stat-bound', 'cachePath': str(self.path),
      'reusedEvidenceCount': len(self.reused),
      'evidenceVerifiedAt': {key: self.rows[key]['verifiedAt'] for key in self.used if key in self.rows},
      'independentFullRead': False}
