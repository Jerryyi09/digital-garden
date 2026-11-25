"""Verify guide output remains local and configurable without generating assets."""
import os
from unittest.mock import patch
import unittest

from tools.readalong.guide_paths import guide_category_path


class GuidePathTests(unittest.TestCase):
  def test_local_root_override(self):
    with patch.dict(os.environ, {"READALONG_LIBRARY_ROOT": "/tmp/guide-fixture"}):
      self.assertEqual(guide_category_path("科幻"), "/private/tmp/guide-fixture/科幻")

  def test_mounted_root_is_rejected(self):
    with patch.dict(os.environ, {"READALONG_LIBRARY_ROOT": "/Volumes/750/Music/有声书"}):
      with self.assertRaises(ValueError):
        guide_category_path("科幻")
