"""Operational helpers remain read-only and provide deterministic samples."""
import unittest

from tools.readalong.nuc_backup_report import backup_report_command, REMOTE_REPORT
from tools.readalong.playback_samples import playback_samples
from tools.readalong.nuc_target import NUC_SSH


class SyncerOpsTests(unittest.TestCase):
  def test_backup_report_uses_direct_ssh_and_read_only_script(self):
    self.assertEqual(backup_report_command()[:-1], NUC_SSH)
    compile(REMOTE_REPORT, "<remote-report>", "exec")
    for mutation in ("unlink(", "rmdir(", "rmtree(", "write_text(", "mkdir("):
      self.assertNotIn(mutation, REMOTE_REPORT)

  def test_playback_samples_cover_three_points_and_empty_input(self):
    self.assertEqual(playback_samples([]), [])
    samples = playback_samples(list(range(10)))
    self.assertEqual([row["index"] for row in samples], [2, 5, 8])
    self.assertEqual([row["segment"] for row in samples], [2, 5, 8])
