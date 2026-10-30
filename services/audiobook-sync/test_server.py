import importlib.util
import io
import json
from concurrent.futures import ThreadPoolExecutor
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('garden_sync', Path(__file__).with_name('server.py'))
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)
backup_spec = importlib.util.spec_from_file_location('garden_backup', Path(__file__).with_name('backup.py'))
backup_module = importlib.util.module_from_spec(backup_spec)
backup_spec.loader.exec_module(backup_module)


class SyncTests(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    server.DB_PATH = str(Path(self.temp.name) / 'sync.db')
    server.initialize_database()
    self.auth = patch.object(server, 'authenticate', side_effect=lambda token, client, device: {'one': 1, 'two': 2}.get(token))
    self.auth.start()
    self.http = server.ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
    self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
    self.thread.start()
    self.base = f'http://127.0.0.1:{self.http.server_port}/sync/v1/items'

  def tearDown(self):
    self.http.shutdown()
    self.http.server_close()
    self.thread.join()
    self.auth.stop()
    self.temp.cleanup()

  def request(self, token, body=None):
    req = urllib.request.Request(self.base, data=json.dumps(body).encode() if body is not None else None, headers={'Authorization': token, 'Content-Type': 'application/json'})
    try:
      with urllib.request.urlopen(req) as response:
        return response.status, json.load(response)
    except urllib.error.HTTPError as exc:
      with exc:
        return exc.code, json.load(exc)

  def test_user_isolation_and_conflict(self):
    item = {'kind': 'progress', 'id': '/book/track', 'revision': 0, 'value': {'position': 30}}
    self.assertEqual(self.request('one', item)[0], 200)
    self.assertEqual(self.request('one', item)[0], 409)
    self.assertEqual(self.request('two')[1]['items'], [])
    self.assertEqual(self.request('one')[1]['items'][0]['value']['position'], 30)
    item.update(revision=1, value={'position': 5})
    self.assertEqual(self.request('one', item)[0], 200)
    self.assertEqual(self.request('one')[1]['items'][0]['value']['position'], 5)

  def test_auth_and_invalid_input(self):
    self.assertEqual(self.request('invalid')[0], 401)
    self.assertEqual(self.request('one', {'kind': 'other', 'id': 'x', 'revision': 0, 'value': {}})[0], 400)

  def test_bookmarks_are_account_scoped_and_can_be_tombstoned(self):
    item = {'kind': 'bookmark', 'id': 'b1', 'revision': 0, 'value': {'position': 42, 'deleted': False}}
    self.assertEqual(self.request('one', item)[0], 200)
    self.assertEqual(self.request('two')[1]['items'], [])
    item.update(revision=1, value={'position': 42, 'deleted': True})
    self.assertEqual(self.request('one', item)[0], 200)
    self.assertTrue(self.request('one')[1]['items'][0]['value']['deleted'])

  def test_preflight_only_allows_configured_origins(self):
    for origin, allowed in [('https://notes.melyi.uk', True), ('https://other.example', False)]:
      req = urllib.request.Request(self.base, method='OPTIONS', headers={'Origin': origin})
      with urllib.request.urlopen(req) as response:
        self.assertEqual(response.status, 204)
        self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), origin if allowed else None)

  def test_concurrent_edits_only_one_wins(self):
    def write(position):
      return self.request('one', {'kind': 'progress', 'id': 'race', 'revision': 0, 'value': {'position': position}})[0]
    with ThreadPoolExecutor(max_workers=2) as pool:
      statuses = list(pool.map(write, [10, 20]))
    self.assertEqual(sorted(statuses), [200, 409])
    self.assertIn(self.request('one')[1]['items'][0]['value']['position'], [10, 20])

  def test_consistent_backup_never_overwrites(self):
    item = {'kind': 'progress', 'id': 'track', 'revision': 0, 'value': {'position': 31}}
    self.assertEqual(self.request('one', item)[0], 200)
    path = Path(self.temp.name) / 'backup.sqlite3'
    backup_module.backup(server.DB_PATH, path)
    with server.sqlite3.connect(path) as db:
      self.assertEqual(db.execute('SELECT count(*) FROM items').fetchone()[0], 1)
    with self.assertRaises(FileExistsError):
      backup_module.backup(server.DB_PATH, path)


class AuthenticationTests(unittest.TestCase):
  def test_alist_account_roles_and_disabled_users(self):
    for role, disabled, expected in [(0, False, 7), (2, False, 7), (1, False, None), (0, True, None), ([3], False, 7), ([2], False, 7), ([1], False, None), ([1, 3], False, None), ([], False, None)]:
      data = json.dumps({'code': 200, 'data': {'id': 7, 'role': role, 'disabled': disabled}}).encode()
      with patch.object(server.urllib.request, 'urlopen', return_value=io.BytesIO(data)):
        self.assertEqual(server.authenticate('token'), expected)
    self.assertIsNone(server.authenticate(''))

  def test_alist_receives_device_credentials(self):
    data = json.dumps({'code': 200, 'data': {'id': 7, 'role': [3], 'disabled': False}}).encode()
    with patch.object(server.urllib.request, 'urlopen', return_value=io.BytesIO(data)) as call:
      self.assertEqual(server.authenticate('token', 'device-id', 'device-secret'), 7)
      headers = dict(call.call_args.args[0].header_items())
      self.assertEqual(headers['Client-id'], 'device-id')
      self.assertEqual(headers['Device-key'], 'device-secret')


if __name__ == '__main__':
  unittest.main()
