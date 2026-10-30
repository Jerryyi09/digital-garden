"""Authenticated per-user sync API; SQLite is only accessed on the server host."""
import json
import contextlib
import os
import sqlite3
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DB_PATH = os.environ.get('GARDEN_SYNC_DB', 'garden-sync.sqlite3')
ALIST_ME = os.environ.get('GARDEN_ALIST_ME', 'http://127.0.0.1:5244/alist/api/me')
ALLOWED_ORIGINS = {'https://notes.melyi.uk', 'https://melyi.uk:8089'}
MAX_BODY = 131072


@contextlib.contextmanager
def connect():
  db = sqlite3.connect(DB_PATH, timeout=10)
  try:
    db.execute('PRAGMA busy_timeout=10000')
    with db:
      yield db
  finally:
    db.close()


def initialize_database():
  Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
  with connect() as db:
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('CREATE TABLE IF NOT EXISTS items (user_id INTEGER NOT NULL, kind TEXT NOT NULL, item_id TEXT NOT NULL, revision INTEGER NOT NULL, payload TEXT NOT NULL, updated_at INTEGER NOT NULL, PRIMARY KEY(user_id, kind, item_id))')


def authenticate(token, client_id='', device_key=''):
  if not token or len(token) > 8192:
    return None
  if len(client_id) > 512 or len(device_key) > 8192:
    return None
  headers = {'Authorization': token}
  if client_id:
    headers['Client-Id'] = client_id
  if device_key:
    headers['Device-Key'] = device_key
  request = urllib.request.Request(ALIST_ME, headers=headers)
  try:
    with urllib.request.urlopen(request, timeout=5) as response:
      result = json.load(response)
    user = result.get('data') or {}
    role = user.get('role')
    if isinstance(role, list):
      allowed_role = bool(role) and all(type(value) is int and value > 0 and value != 1 for value in role)
    else:
      allowed_role = type(role) is int and role in (0, 2)
    if result.get('code') != 200 or user.get('disabled') is not False or not allowed_role:
      return None
    user_id = user.get('id')
    return user_id if isinstance(user_id, int) and not isinstance(user_id, bool) and user_id > 0 else None
  except (OSError, ValueError, urllib.error.URLError):
    return None


class Handler(BaseHTTPRequestHandler):
  def log_message(self, format, *args):
    pass

  def send_json(self, status, value):
    body = b'' if status == 204 else json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()
    self.send_response(status)
    origin = self.headers.get('Origin')
    if origin in ALLOWED_ORIGINS:
      self.send_header('Access-Control-Allow-Origin', origin)
      self.send_header('Vary', 'Origin')
      self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
      self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type, Client-Id, Device-Key')
    self.send_header('Cache-Control', 'no-store')
    self.send_header('Content-Type', 'application/json; charset=utf-8')
    self.send_header('Content-Length', str(len(body)))
    self.end_headers()
    self.wfile.write(body)

  def do_OPTIONS(self):
    self.send_json(204, {})

  def user(self):
    user_id = authenticate(self.headers.get('Authorization', ''), self.headers.get('Client-Id', ''), self.headers.get('Device-Key', ''))
    if user_id is None:
      self.send_json(401, {'error': 'authentication_failed'})
    return user_id

  def do_GET(self):
    if self.path != '/sync/v1/items':
      return self.send_json(404, {'error': 'not_found'})
    user_id = self.user()
    if user_id is None:
      return
    with connect() as db:
      rows = db.execute('SELECT kind, item_id, revision, payload, updated_at FROM items WHERE user_id=?', (user_id,)).fetchall()
    self.send_json(200, {'items': [{'kind': k, 'id': i, 'revision': r, 'value': json.loads(p), 'updatedAt': t} for k, i, r, p, t in rows]})

  def do_POST(self):
    if self.path != '/sync/v1/items':
      return self.send_json(404, {'error': 'not_found'})
    user_id = self.user()
    if user_id is None:
      return
    try:
      length = int(self.headers.get('Content-Length', '0'))
      if not 0 < length <= MAX_BODY:
        raise ValueError()
      data = json.loads(self.rfile.read(length))
      kind, item_id, revision, value = data['kind'], data['id'], data['revision'], data['value']
      if kind not in ('progress', 'bookmark') or not isinstance(item_id, str) or not 0 < len(item_id) <= 4096 or type(revision) is not int or revision < 0 or not isinstance(value, dict):
        raise ValueError()
      payload = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':'))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
      return self.send_json(400, {'error': 'invalid_request'})
    now = time.time_ns() // 1_000_000
    with connect() as db:
      db.execute('BEGIN IMMEDIATE')
      row = db.execute('SELECT revision, payload, updated_at FROM items WHERE user_id=? AND kind=? AND item_id=?', (user_id, kind, item_id)).fetchone()
      current_revision = row[0] if row else 0
      if current_revision != revision:
        return self.send_json(409, {'error': 'conflict', 'current': {'revision': row[0], 'value': json.loads(row[1]), 'updatedAt': row[2]} if row else None})
      next_revision = current_revision + 1
      db.execute('INSERT INTO items VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(user_id,kind,item_id) DO UPDATE SET revision=excluded.revision,payload=excluded.payload,updated_at=excluded.updated_at', (user_id, kind, item_id, next_revision, payload, now))
    self.send_json(200, {'revision': next_revision, 'updatedAt': now})


if __name__ == '__main__':
  initialize_database()
  host = os.environ.get('GARDEN_SYNC_HOST', '127.0.0.1')
  ThreadingHTTPServer((host, int(os.environ.get('GARDEN_SYNC_PORT', '8791'))), Handler).serve_forever()
