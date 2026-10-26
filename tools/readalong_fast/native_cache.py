"""Locate source/model-bound native caches independently of display rounding."""
import hashlib
import json
import math
from pathlib import Path


class NativeCacheIndex:
  def __init__(self, roots, model_sha):
    self.roots, self.model_sha = roots, model_sha
    self.entries = None

  def build(self):
    if self.entries is not None:
      return
    self.entries = {}
    for root in self.roots:
      for path in Path(root).glob('*.json'):
        if len(path.stem) != 64:
          continue
        # Read headers only for discovery; fully validate the selected payload.
        with path.open() as stream:
          head = stream.read(4096)
        marker = head.find('"parameters"')
        if marker < 0:
          continue
        try:
          params, _ = json.JSONDecoder().raw_decode(head[head.index('{', marker):])
        except (ValueError, json.JSONDecodeError):
          continue
        if not isinstance(params, dict):
          continue
        if (params.get('modelSha256') != self.model_sha or params.get('engine') != 'mlx-segment-v1'
            or params.get('language') != 'en' or params.get('sampleRate') != 16000
            or params.get('word_timestamps') is not False):
          continue
        if hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest() != path.stem:
          continue
        a, length = params.get('start'), params.get('duration')
        if any(type(v) not in (int, float) or not math.isfinite(v) for v in (a, length)) or a < 0 or length <= 0:
          continue
        self.entries.setdefault(params.get('sourceSha256'), []).append((a, a+length, path, params))

  def covering(self, sha, start, end):
    self.build()
    candidates = [e for e in self.entries.get(sha, []) if e[0] <= start+.001 and e[1] >= end-.001]
    if not candidates:
      return None
    # Smallest containing request minimizes unrelated context, never shifts time.
    return min(candidates, key=lambda e: (e[1]-e[0], str(e[2])))

  def register(self, path, params):
    if self.entries is not None:
      self.entries.setdefault(params['sourceSha256'], []).append((params['start'], params['start']+params['duration'], path, params))
