"""Create a consistent SQLite backup without overwriting an existing file."""
import argparse
from contextlib import closing
import os
import sqlite3
from pathlib import Path


def backup(source, destination):
  source = Path(source).resolve(strict=True)
  destination = Path(destination)
  destination.parent.mkdir(parents=True, exist_ok=True)
  fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
  os.close(fd)
  with closing(sqlite3.connect(f'{source.as_uri()}?mode=ro', uri=True)) as src:
    with closing(sqlite3.connect(destination)) as dst:
      src.backup(dst)
      if dst.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
        raise RuntimeError('Backup integrity check failed; file retained for inspection')


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('source')
  parser.add_argument('destination')
  args = parser.parse_args()
  backup(args.source, args.destination)
