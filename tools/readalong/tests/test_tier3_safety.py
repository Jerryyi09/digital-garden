import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.readalong import nuc_verifier


class AlistCredentialTests(unittest.TestCase):
  def test_missing_credentials_fail_loudly_without_fallback(self):
    with tempfile.TemporaryDirectory() as home, mock.patch.dict(os.environ, {}, clear=True), \
         mock.patch.object(nuc_verifier.Path, "home", return_value=Path(home)):
      with self.assertRaises(RuntimeError):
        nuc_verifier.load_alist_credentials()

  def test_env_credentials_are_used(self):
    with mock.patch.dict(os.environ, {"READALONG_ALIST_USER": "u", "READALONG_ALIST_PASSWORD": "p"}, clear=True):
      self.assertEqual(nuc_verifier.load_alist_credentials(), ("u", "p"))

  def test_no_password_literal_in_client_source(self):
    src = Path(nuc_verifier.__file__).read_text(encoding="utf-8")
    self.assertNotIn('password="hp"', src)


class Tier3RemoteCommandTests(unittest.TestCase):
  def test_remote_checker_runs_bounded_locked_and_quoted(self):
    calls = []

    def fake_run_nuc(cmd, **kwargs):
      calls.append(cmd)
      return subprocess.CompletedProcess(cmd, 0, stdout="VERIFY:True:OK", stderr="")

    with mock.patch("tools.readalong.nuc_target.run_nuc", side_effect=fake_run_nuc):
      ok, _ = nuc_verifier.verify_book_via_ssh("hp@10.0.0.85", "文学理论", 'Bad $name "x"')
    self.assertTrue(ok)
    remote = calls[-1][-1]
    self.assertTrue(remote.startswith("timeout -k 10 180 nice -n 19 ionice -c3 flock -n /tmp/readalong-tier3.lock "))
    self.assertIn("/home/hp/.readalong-tools/remote_checker.py", remote)
    self.assertNotIn("/tmp/remote_checker.py", remote)
    self.assertIn("'Bad $name \"x\"'", remote)


if __name__ == "__main__":
  unittest.main()
