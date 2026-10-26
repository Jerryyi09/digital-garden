"""Read-only real-book experiments; no production audit defaults are changed."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
from statistics import median
import subprocess
import sys
import tempfile
from time import perf_counter
from unittest.mock import patch

from tools.readalong import authoritative_validator as validator
from tools.readalong import practical_publisher as publisher
from tools.readalong.atomic_io import atomic_json
from tools.readalong.candidate_safety import source_files
from tools.readalong_fast.pipeline import stat_key

HASH = validator.sha256
PROBE = validator.probe_audio_duration


class Evidence:
  """Experimental stat-bound cache, scoped to one benchmark process."""
  def __init__(self):
    self.rows = {}

  def get(self, path, kind):
    path = Path(path).resolve(strict=True)
    key = (str(path), kind)
    before = stat_key(path)
    entry = self.rows.get(key)
    if entry and entry[0] == before:
      return entry[1]
    value = (HASH if kind == 'hash' else PROBE)(path)
    if stat_key(path) != before:
      raise RuntimeError('Source changed while reading')
    self.rows[key] = (before, value)
    return value

  def sha(self, path):
    return self.get(path, 'hash')

  def duration(self, path):
    return self.get(path, 'duration')


def audit(book, candidate, evidence=None, parallel=False):
  if evidence is None:
    return publisher.audit_practical(book, candidate)
  manifest = json.loads((candidate/'readalong.manifest.json').read_text())
  paths = [validator.safe_path(book, row['id']) for row in manifest['audioSources']]
  def collect(path):
    try:
      evidence.sha(path)
      evidence.duration(path)
    except OSError:
      # Let the original audit produce its ordered missing-file diagnostics.
      return
  if parallel:
    with ThreadPoolExecutor(max_workers=4) as pool:
      list(pool.map(collect, paths))
  with ExitStack() as stack:
    stack.enter_context(patch.object(validator, 'sha256', evidence.sha))
    stack.enter_context(patch.object(validator, 'probe_audio_duration', evidence.duration))
    stack.enter_context(patch.object(publisher, 'sha256', evidence.sha))
    return publisher.audit_practical(book, candidate)


def mutation_checks():
  checks = {}
  with tempfile.TemporaryDirectory() as directory:
    path = Path(directory)/'source.bin'
    path.write_bytes(b'original')
    cache = Evidence()
    before = cache.sha(path)
    saved = path.stat()
    path.write_bytes(b'modified')
    os.utime(path, ns=(saved.st_atime_ns, saved.st_mtime_ns))
    checks['same_size_restored_mtime_detected'] = cache.sha(path) != before
    replacement = Path(directory)/'replacement.bin'
    replacement.write_bytes(b'replaced')
    replacement.replace(path)
    checks['replacement_detected'] = cache.sha(path) == HASH(path)
    path.unlink()
    try:
      cache.sha(path)
    except FileNotFoundError:
      checks['deletion_detected'] = True
  assert all(checks.values()) and len(checks) == 3
  return checks


def startup_worker(roots, count, reuse):
  from tools.readalong.config import resolve_model_path
  from tools.readalong.input_inventory import model_fingerprint
  from tools.readalong_fast.native_cache import NativeCacheIndex
  signatures = []
  for i in range(count):
    if not reuse or i == 0:
      model = model_fingerprint(resolve_model_path())
      index = NativeCacheIndex(roots, model)
      index.build()
    entries = [(sha, a, b, str(path), params)
               for sha, values in sorted(index.entries.items())
               for a, b, path, params in sorted(values, key=lambda item: str(item[2]))]
    digest = hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()
    signatures.append([model, len(index.entries), sum(map(len, index.entries.values())), digest])
  return signatures


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--output', type=Path)
  parser.add_argument('--worker', type=int)
  parser.add_argument('--startup-only', action='store_true')
  parser.add_argument('--cache-root', action='append', required=True)
  args = parser.parse_args()
  if args.worker:
    print(json.dumps(startup_worker(args.cache_root, args.worker, True)))
    return
  if not args.output or args.output.exists():
    raise ValueError('Provide a new result path')
  ledger = json.loads(Path('private/readalong-release-bundles/personal-20261024/decisions.json').read_text())['records']
  report = {'scope': 'read-only experimental practical audits; no ASR or publication',
            'books': [], 'mutationChecks': mutation_checks()}
  units = ['心智成长/101 Essays That Will Change The Way You Think',
           '心智成长/A Little History of Psychology', '文学作品/麦田里的守望者']
  for uid in ([] if args.startup_only else units):
    row = ledger[uid]
    book, candidate = Path(row['bookDir']), Path(row['candidatePath'])
    baseline = audit(book, candidate)
    warm = Evidence()
    start = perf_counter()
    assert audit(book, candidate, warm) == baseline
    population = perf_counter()-start
    samples = {mode: [] for mode in ['full', 'parallel4', 'incrementalWarm']}
    for trial in range(3):
      modes = list(samples)
      if trial % 2:
        modes.reverse()
      for mode in modes:
        start = perf_counter()
        result = audit(book, candidate, None if mode == 'full' else (warm if mode == 'incrementalWarm' else Evidence()), mode == 'parallel4')
        samples[mode].append(perf_counter()-start)
        assert result == baseline, (uid, mode, 'audit differs')
    medians = {mode: median(values) for mode, values in samples.items()}
    manifest = json.loads((candidate/'readalong.manifest.json').read_text())
    result = {'unit': uid, 'tracks': len(manifest['audioSources']), 'decision': baseline['decision'],
              'samplesSeconds': samples, 'medianSeconds': medians, 'populationSeconds': population,
              'speedups': {mode: medians['full']/value for mode, value in medians.items()}, 'reportsEqual': True}
    report['books'].append(result)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    atomic_json(args.output, report)
  cmd = [sys.executable, '-B', '-m', 'tools.readalong_fast.benchmark_audit_options']
  for root in args.cache_root:
    cmd += ['--cache-root', root]
  samples = {'separateProcesses': [], 'sharedProcess': []}
  for trial in range(3):
    for mode in (list(samples) if trial % 2 == 0 else list(reversed(samples))):
      start = perf_counter()
      if mode == 'separateProcesses':
        signatures = [json.loads(subprocess.check_output(cmd+['--worker', '1']))[0] for _ in units]
      else:
        signatures = json.loads(subprocess.check_output(cmd+['--worker', str(len(units))]))
      samples[mode].append(perf_counter()-start)
      assert all(item == signatures[0] for item in signatures)
      if 'expected' not in locals():
        expected = signatures
      assert signatures == expected
  report['startup'] = {'samplesSeconds': samples, 'signatures': expected,
    'speedup': median(samples['separateProcesses'])/median(samples['sharedProcess']),
    'scope': '3 model fingerprints and cache-index startups versus one reused startup, includes imports; not full generation'}
  report['scriptSha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
  atomic_json(args.output, report)
  print(json.dumps(report['startup'], ensure_ascii=False), flush=True)


if __name__ == '__main__':
  main()
