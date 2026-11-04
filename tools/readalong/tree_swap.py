"""Recoverable directory swaps; callers must hold the book publication lock."""
import json
import os
from pathlib import Path
import shutil

from tools.readalong.atomic_io import atomic_json


def recover_tree_swap(book):
  book = Path(book).resolve()
  journal = book / '.readalong-swap.json'
  if not journal.exists():
    return
  record = json.loads(journal.read_text())
  staged = book / record['staged']
  backup = book / record['backup']
  if (staged.parent != book or not staged.name.startswith(('.readalong_stage_', '.readalong_restore_'))
      or not backup.resolve().is_relative_to((book / '.readalong_rollback').resolve())):
    raise ValueError('Unsafe directory swap recovery record')
  active = book / 'readalong'
  if not os.path.lexists(active):
    if not os.path.lexists(backup):
      raise ValueError('Interrupted publication has no previous tree to restore')
    os.replace(backup, active)
  # A present entry means either the old tree survived or the new tree committed.
  if staged.exists():
    shutil.rmtree(staged)
  journal.unlink()


def replace_active_tree(book, staged, backup):
  book = Path(book).resolve()
  active = book / 'readalong'
  journal = book / '.readalong-swap.json'
  if os.path.lexists(backup):
    raise ValueError('Previous tree backup already exists; refusing to overwrite it')
  backup.parent.mkdir(parents=True, exist_ok=True)
  if not os.path.lexists(active):
    os.replace(staged, active)
    return
  atomic_json(journal, {'staged': staged.relative_to(book).as_posix(),
    'backup': backup.relative_to(book).as_posix()})
  try:
    os.replace(active, backup)
    os.replace(staged, active)
  except BaseException:
    # Retain the journal and staged files if recovery itself fails.
    recover_tree_swap(book)
    raise
  journal.unlink()
