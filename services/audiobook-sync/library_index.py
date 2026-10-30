"""Metadata-only SQLite index for the audiobook library."""
import json
import os
import sqlite3
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

MEDIA_SUFFIXES = {'.mp3', '.m4a', '.m4b'}
IGNORED_DIRECTORIES = {'readalong', '.readalong', '.readalong_revisions', 'work', 'generated', 'preview', 'runtime-snapshot', '__pycache__'}


def ensure_schema(db):
  db.execute('CREATE TABLE IF NOT EXISTS library_index_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
  db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS library_fts USING fts5(path UNINDEXED, kind UNINDEXED, category, title, author, chapter, summary, tokenize='unicode61 remove_diacritics 2')")


def _summary_map(category_path):
  try:
    data = json.loads((category_path / 'summaries.json').read_text(encoding='utf-8'))
    return data if isinstance(data, dict) else {}
  except (OSError, ValueError):
    return {}


def _epub_authors(book_path):
  for epub in book_path.rglob('*.epub'):
    if any(part in IGNORED_DIRECTORIES for part in epub.relative_to(book_path).parts):
      continue
    try:
      with zipfile.ZipFile(epub) as archive:
        container = ElementTree.fromstring(archive.read('META-INF/container.xml'))
        rootfile = next((node.attrib.get('full-path') for node in container.iter() if node.tag.endswith('rootfile')), None)
        if not rootfile:
          continue
        package = ElementTree.fromstring(archive.read(rootfile))
        creators = [node.text.strip() for node in package.iter() if node.tag.endswith('creator') and node.text and node.text.strip()]
        if creators:
          return ' / '.join(dict.fromkeys(creators))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, ElementTree.ParseError):
      continue
  return ''


def _walk_tracks(book_path):
  for current, dirs, files in os.walk(book_path):
    dirs[:] = [name for name in dirs if name not in IGNORED_DIRECTORIES]
    for name in files:
      path = Path(current) / name
      if path.suffix.lower() in MEDIA_SUFFIXES:
        yield path


def build_index(db_path, library_root, alist_root):
  """Replace the catalog index using only directory names, summaries and EPUB creators."""
  root = Path(library_root)
  if not root.is_dir():
    raise ValueError(f'library root does not exist: {root}')
  with sqlite3.connect(db_path, timeout=30) as db:
    db.execute('PRAGMA busy_timeout=30000')
    ensure_schema(db)
    db.execute('BEGIN IMMEDIATE')
    db.execute('DELETE FROM library_fts')
    books = chapters = 0
    for category_path in sorted((path for path in root.iterdir() if path.is_dir()), key=lambda path: path.name):
      summaries = _summary_map(category_path)
      for book_path in sorted((path for path in category_path.iterdir() if path.is_dir()), key=lambda path: path.name):
        relative = book_path.relative_to(root).as_posix()
        public_book_path = f"{alist_root.rstrip('/')}/{relative}"
        author = _epub_authors(book_path)
        summary = str(summaries.get(book_path.name, ''))
        db.execute('INSERT INTO library_fts VALUES (?, ?, ?, ?, ?, ?, ?)', (public_book_path, 'book', category_path.name, book_path.name, author, '', summary))
        books += 1
        for track_path in _walk_tracks(book_path):
          track_relative = track_path.relative_to(root).as_posix()
          public_track_path = f"{alist_root.rstrip('/')}/{track_relative}"
          db.execute('INSERT INTO library_fts VALUES (?, ?, ?, ?, ?, ?, ?)', (public_track_path, 'chapter', category_path.name, book_path.name, author, track_path.stem, summary))
          chapters += 1
    db.execute("INSERT INTO library_index_meta(key, value) VALUES ('indexed_at', datetime('now')) ON CONFLICT(key) DO UPDATE SET value=excluded.value")
    db.execute("INSERT INTO library_index_meta(key, value) VALUES ('book_count', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (str(books),))
    db.execute("INSERT INTO library_index_meta(key, value) VALUES ('chapter_count', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (str(chapters),))
  return {'books': books, 'chapters': chapters}


def match_expression(query):
  terms = [term.replace('"', '') for term in query.split() if term]
  if not terms:
    return ''
  return ' AND '.join(f'"{term}"*' for term in terms)


def one_edit_or_less(left, right):
  if left == right:
    return True
  if abs(len(left) - len(right)) > 1:
    return False
  if len(left) == len(right):
    return sum(a != b for a, b in zip(left, right)) <= 1
  if len(left) > len(right):
    left, right = right, left
  index_left = index_right = edits = 0
  while index_left < len(left) and index_right < len(right):
    if left[index_left] == right[index_right]:
      index_left += 1
      index_right += 1
    elif edits:
      return False
    else:
      edits += 1
      index_right += 1
  return True


def search(db, query, limit=40):
  expression = match_expression(query)
  if not expression:
    return []
  rows = db.execute(
    'SELECT path, kind, category, title, author, chapter, summary FROM library_fts WHERE library_fts MATCH ? ORDER BY bm25(library_fts), kind = \'book\' DESC LIMIT ?',
    (expression, limit),
  ).fetchall()
  if not rows and query.isascii() and query.replace(' ', '').isalpha():
    requested = [term.casefold() for term in query.split()]
    authors = db.execute("SELECT DISTINCT author FROM library_fts WHERE kind='book' AND author <> ''").fetchall()
    close_authors = [
      author for (author,) in authors
      if any(one_edit_or_less(term, candidate.casefold()) for term in requested for candidate in author.split())
    ]
    if close_authors:
      placeholders = ','.join('?' for _ in close_authors)
      rows = db.execute(
        f"SELECT path, kind, category, title, author, chapter, summary FROM library_fts WHERE kind='book' AND author IN ({placeholders}) LIMIT ?",
        (*close_authors, limit),
      ).fetchall()
  return [dict(zip(('path', 'kind', 'category', 'title', 'author', 'chapter', 'summary'), row)) for row in rows]


if __name__ == '__main__':
  if len(sys.argv) != 4:
    raise SystemExit('usage: library_index.py DATABASE LIBRARY_ROOT ALIST_ROOT')
  print(json.dumps(build_index(*sys.argv[1:]), ensure_ascii=False))
