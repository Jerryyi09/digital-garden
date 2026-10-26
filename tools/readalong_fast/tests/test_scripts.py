"""Unit tests for operator and execution CLI scripts: readalong-map and readalong-publish-nuc."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[3]


class ScriptIntegrationTests(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.root = Path(self.temp.name)

  def test_publish_script_shell_syntax(self):
    subprocess.run(["bash", "-n", str(REPO_ROOT / "scripts/readalong-publish-nuc")], check=True)

  def test_map_script_rejects_volumes_mount_path(self):
    script = REPO_ROOT/"scripts/readalong-map"
    res = subprocess.run([str(script), "/Volumes/750/Music/有声书"], capture_output=True, text=True)
    self.assertNotEqual(res.returncode, 0)
    self.assertIn("Strictly forbidden", res.stderr + res.stdout)

  def test_map_script_requires_target_argument(self):
    script = REPO_ROOT/"scripts/readalong-map"
    res = subprocess.run([str(script)], capture_output=True, text=True)
    self.assertNotEqual(res.returncode, 0)
    self.assertIn("Usage:", res.stderr + res.stdout)

  def test_map_script_requires_existing_directory(self):
    script = REPO_ROOT/"scripts/readalong-map"
    res = subprocess.run([str(script), "/tmp/non_existent_dir_12345"], capture_output=True, text=True)
    self.assertNotEqual(res.returncode, 0)
    self.assertIn("Directory not found", res.stderr + res.stdout)

  def test_publish_script_requires_batch_dir(self):
    script = REPO_ROOT/"scripts/readalong-publish-nuc"
    res = subprocess.run([str(script)], capture_output=True, text=True)
    self.assertNotEqual(res.returncode, 0)
    self.assertIn("Usage:", res.stderr + res.stdout)

  def test_publish_script_rejects_missing_inventory(self):
    script = REPO_ROOT/"scripts/readalong-publish-nuc"
    empty = self.root/"empty-batch"
    empty.mkdir()
    res = subprocess.run([str(script), str(empty)], capture_output=True, text=True)
    self.assertNotEqual(res.returncode, 0)
    self.assertIn("Missing inventory.json", res.stderr + res.stdout)

  def test_publish_script_rejects_dangerous_delete_arguments(self):
    script = REPO_ROOT/"scripts/readalong-publish-nuc"
    empty = self.root/"empty-batch"
    empty.mkdir()
    res = subprocess.run([str(script), str(empty), "--delete"], capture_output=True, text=True)
    self.assertNotEqual(res.returncode, 0)
    self.assertIn("Dangerous argument rejected", res.stderr + res.stdout)

  def test_publish_script_rejects_non_ssh_target_base(self):
    script = REPO_ROOT/"scripts/readalong-publish-nuc"
    empty = self.root/"empty-batch"
    empty.mkdir()
    (empty / "inventory.json").write_text("{}", encoding="utf-8")
    res = subprocess.run([str(script), str(empty), "--target-base", "/Volumes/750/Music/有声书"], capture_output=True, text=True)
    self.assertNotEqual(res.returncode, 0)
    self.assertIn("Target base must be an SSH remote path", res.stderr + res.stdout)

  def test_publish_script_locks_against_concurrent_runs(self):
    import fcntl
    script = REPO_ROOT/"scripts/readalong-publish-nuc"
    empty = self.root/"empty-batch"
    empty.mkdir()
    (empty / "inventory.json").write_text('{"units": []}', encoding="utf-8")

    # Simulate an active process holding the flock
    with open("/tmp/readalong-publish-nuc.lock", "a+") as f:
      try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
      except BlockingIOError:
        # An actual publisher already supplies the competing lock holder.
        pass
      res = subprocess.run([str(script), str(empty)], capture_output=True, text=True)
      self.assertNotEqual(res.returncode, 0)
      self.assertIn("Another NUC publication process is currently running", res.stderr + res.stdout)


if __name__ == "__main__":
  unittest.main()
