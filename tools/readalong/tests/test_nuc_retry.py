import subprocess
import unittest
from unittest import mock

from tools.readalong import nuc_target


class NucRetryTests(unittest.TestCase):
  def _results(self, *codes):
    return [subprocess.CompletedProcess(["ssh"], c, stdout="", stderr=f"err{c}") for c in codes]

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


if __name__ == "__main__":
  unittest.main()
