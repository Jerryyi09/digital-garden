import subprocess
import unittest
from unittest import mock

from tools.readalong import nuc_target


class NucRetryTests(unittest.TestCase):
  def _results(self, *codes, err="ssh: connect to host 10.0.0.85 port 2222: No route to host"):
    return [subprocess.CompletedProcess(["ssh"], c, stdout="", stderr=f"err{c} {err}") for c in codes]

  def test_transport_failure_is_retried_then_succeeds(self):
    with mock.patch.object(nuc_target.subprocess, "run", side_effect=self._results(255, 255, 0)) as run:
      result = nuc_target.run_nuc(["ssh"], sleep=lambda s: None, capture_output=True, text=True)
    self.assertEqual(result.returncode, 0)
    self.assertEqual(run.call_count, 3)

  def test_remote_command_failure_is_not_retried(self):
    with mock.patch.object(nuc_target.subprocess, "run", side_effect=self._results(1)) as run:
      with self.assertRaises(nuc_target.NucCommandError):
        nuc_target.run_nuc(["ssh"], sleep=lambda s: None, capture_output=True, text=True)
    self.assertEqual(run.call_count, 1)

  def test_persistent_failure_raises_with_stderr(self):
    with mock.patch.object(nuc_target.subprocess, "run", side_effect=self._results(255, 255, 255)):
      with self.assertRaises(nuc_target.NucCommandError) as ctx:
        nuc_target.run_nuc(["ssh"], sleep=lambda s: None, capture_output=True, text=True)
    self.assertIn("err255", str(ctx.exception))


  def test_mid_session_drop_is_never_retried(self):
    results = self._results(255, 0, err="client_loop: send disconnect: Broken pipe")
    with mock.patch.object(nuc_target.subprocess, "run", side_effect=results) as run:
      with self.assertRaises(nuc_target.NucCommandError):
        nuc_target.run_nuc(["ssh"], sleep=lambda s: None, capture_output=True, text=True)
    self.assertEqual(run.call_count, 1)

  def test_banner_timeout_on_overloaded_host_is_not_retried(self):
    results = self._results(255, 0, err="Connection timed out during banner exchange")
    with mock.patch.object(nuc_target.subprocess, "run", side_effect=results) as run:
      with self.assertRaises(nuc_target.NucCommandError):
        nuc_target.run_nuc(["ssh"], sleep=lambda s: None, capture_output=True, text=True)
    self.assertEqual(run.call_count, 1)

  def test_bounded_remote_adds_timeout_priority_and_lock(self):
    cmd = nuc_target.bounded_remote("python3 -c 'x'", seconds=600, lock="tier2")
    self.assertTrue(cmd.startswith("timeout -k 10 600 nice -n 19 ionice -c3 flock -n /tmp/readalong-tier2.lock "))

  def test_ssh_has_connect_timeout_and_keepalive(self):
    joined = " ".join(nuc_target.NUC_SSH)
    for opt in ("ConnectTimeout=10", "ServerAliveInterval=15", "ServerAliveCountMax=3"):
      self.assertIn(opt, joined)
      self.assertIn(opt, nuc_target.NUC_RSYNC_E)


if __name__ == "__main__":
  unittest.main()
