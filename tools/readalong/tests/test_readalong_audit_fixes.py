"""Exercise publication failure boundaries without touching a real book or NUC."""
import contextlib
import io
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
from unittest.mock import patch

import pytest

from tools.readalong.atomic_io import atomic_json
from tools.readalong.release_integrity import tier2_book_payload
from tools.readalong.tier_verifier import tier2_remote_batch_check
from tools.readalong.tree_swap import recover_tree_swap, replace_active_tree


def swap_fixture(tmp_path):
  active = tmp_path / 'readalong'
  active.mkdir()
  (active / 'old.txt').write_text('old')
  staged = tmp_path / '.readalong_stage_test'
  staged.mkdir()
  (staged / 'new.txt').write_text('new')
  backup = tmp_path / '.readalong_rollback/test/replaced-active'
  return active, staged, backup


def test_failed_install_restores_previous_tree(tmp_path):
  active, staged, backup = swap_fixture(tmp_path)
  replace = os.replace
  def fail(source, dest):
    if Path(source) == staged:
      raise OSError('injected install failure')
    return replace(source, dest)
  with patch('tools.readalong.tree_swap.os.replace', side_effect=fail):
    with pytest.raises(OSError, match='install failure'):
      replace_active_tree(tmp_path, staged, backup)
  assert (active / 'old.txt').read_text() == 'old'
  assert not (tmp_path / '.readalong-swap.json').exists()


@pytest.mark.parametrize('phase', ['before_move', 'between_moves', 'after_install'])
def test_restart_recovers_interrupted_directory_swap(tmp_path, phase):
  active, staged, backup = swap_fixture(tmp_path)
  backup.parent.mkdir(parents=True)
  atomic_json(tmp_path / '.readalong-swap.json', {'staged': staged.name,
    'backup': backup.relative_to(tmp_path).as_posix()})
  if phase != 'before_move':
    os.replace(active, backup)
  if phase == 'after_install':
    os.replace(staged, active)
  recover_tree_swap(tmp_path)
  assert (active / ('new.txt' if phase == 'after_install' else 'old.txt')).is_file()
  assert not staged.exists()
  assert not (tmp_path / '.readalong-swap.json').exists()


def test_failed_recovery_retains_journal_for_retry(tmp_path):
  active, staged, backup = swap_fixture(tmp_path)
  replace = os.replace
  def fail(source, dest):
    if Path(source) in (staged, backup):
      raise OSError('injected failure')
    return replace(source, dest)
  with patch('tools.readalong.tree_swap.os.replace', side_effect=fail):
    with pytest.raises(OSError):
      replace_active_tree(tmp_path, staged, backup)
  assert (tmp_path / '.readalong-swap.json').exists()
  assert backup.is_dir() and staged.is_dir()
  recover_tree_swap(tmp_path)
  assert (active / 'old.txt').is_file()


def shard_fixture(tmp_path):
  book = tmp_path / 'Category' / 'Book'
  active = book / 'readalong'
  active.mkdir(parents=True)
  (book / 'one.mp3').write_bytes(b'audio')
  manifest = {'timelineFormat': 'per-audio-source-v1', 'timeline': 'index.json',
    'audioSources': [{'id': 'one.mp3'}]}
  (active / 'readalong.manifest.json').write_text(json.dumps(manifest))
  (active / 'index.json').write_text(json.dumps({'files': {'one': 'one.json', 'two': 'two.json'}}))
  for name in ('one', 'two'):
    (active / f'{name}.json').write_text(json.dumps([{'audioSourceId': 'one.mp3', 'start': 0}] * 50))
  return book, active


def local_remote_check(root, payload):
  # Execute the exact generated remote Python locally; never launch SSH.
  def run_locally(command, **kwargs):
    args = shlex.split(command[-1])
    script = args[args.index('-c') + 1]
    return subprocess.run([sys.executable, '-c', script], capture_output=True, text=True)
  with patch('tools.readalong.tier_verifier.run_nuc', side_effect=run_locally):
    return tier2_remote_batch_check(book_tuples=[payload], remote_root=str(root))


def test_all_shards_are_hashed_and_missing_later_shard_fails(tmp_path):
  book, active = shard_fixture(tmp_path)
  payload = tier2_book_payload('Category', 'Book', book)
  assert local_remote_check(tmp_path, payload) == (True, [])
  (active / 'two.json').unlink()
  ok, errors = local_remote_check(tmp_path, payload)
  assert not ok and any('two.json' in error for error in errors)
  # Even legacy callers without hashes must check every shard's existence.
  ok, errors = local_remote_check(tmp_path, payload[:3])
  assert not ok and any('TIMELINE_SHARD_MISSING' in error for error in errors)


def test_same_size_later_shard_corruption_fails_hash(tmp_path):
  book, active = shard_fixture(tmp_path)
  payload = tier2_book_payload('Category', 'Book', book)
  target = active / 'two.json'
  target.write_text(target.read_text().replace('"start": 0', '"start": 1'))
  ok, errors = local_remote_check(tmp_path, payload)
  assert not ok and any('TIMELINE_HASH_MISMATCH' in error for error in errors)


@pytest.mark.parametrize(('successes', 'failures', 'expected'), [(1, 0, 0), (1, 1, 1), (0, 1, 1), (0, 0, 2)])
def test_batch_exit_status_reports_partial_and_empty_results(successes, failures, expected):
  script = Path('scripts/readalong-publish-nuc').read_text()
  tail = script[script.index("print('\\n==================================================')", script.index('# Tier 3:')):script.rindex('\nEOF')]
  scope = {'sys': sys, 'synced_books_for_tier2': [None] * successes,
    'failed_books': [('book', 'SYNC_FAILED', [])] * failures}
  code = 0
  with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    try:
      exec(tail, scope)
    except SystemExit as exc:
      code = exc.code
  assert code == expected
