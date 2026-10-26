"""Unit tests for multi-volume book verification matching app.js line 1157-1170."""
import unittest
from unittest.mock import MagicMock

from tools.readalong.nuc_verifier import AlistClient, verify_book_on_alist


class VolumeVerificationTests(unittest.TestCase):
  def setUp(self):
    self.client = MagicMock(spec=AlistClient)

  def test_volume_fallback_finds_parent_cover_and_summary(self):
    manifest = {
      "schemaVersion": 1,
      "bookId": "Volume 1",
      "readalongEnabled": True,
      "assetRevision": None,
      "timeline": "timeline.json",
      "textRoot": "text/",
      "audioSources": [{"id": "vol1.m4b", "name": "vol1.m4b", "alistPath": "/750HD/有声书/心智成长/Series/Volume 1/vol1.m4b"}]
    }
    timeline = [{"start": 0, "end": 10, "audioSourceId": "vol1.m4b"}]

    def fake_list_dir(path, refresh=True):
      if path.endswith("Series/Volume 1"):
        # Subdirectory has audio, textRoot, but NO cover.jpg and NO summary.txt
        return {"code": 200, "data": {"content": [{"name": "vol1.m4b", "is_dir": False}, {"name": "readalong", "is_dir": True}]}}
      if path.endswith("Series"):
        # Parent directory has cover.jpg and summary.txt
        return {"code": 200, "data": {"content": [{"name": "cover.jpg", "is_dir": False}, {"name": "summary.txt", "is_dir": False}]}}
      if path.endswith("readalong/text"):
        return {"code": 200, "data": {"content": [{"name": "content.opf", "is_dir": False}]}}
      return {"code": 200, "data": {"content": []}}

    def fake_fetch_json(path):
      if "readalong.manifest.json" in path: return manifest, None
      if "timeline.json" in path: return timeline, None
      return None, "not found"

    def fake_fetch_raw(path):
      if "content.opf" in path: return b"<package></package>", None
      return None, "not found"

    def fake_get_file_info(path):
      return {"code": 200, "message": "success"}

    self.client.list_dir.side_effect = fake_list_dir
    self.client.fetch_json.side_effect = fake_fetch_json
    self.client.fetch_raw.side_effect = fake_fetch_raw
    self.client.get_file_info.side_effect = fake_get_file_info

    ok, msg, details = verify_book_on_alist(self.client, "心智成长", "Series/Volume 1")
    self.assertTrue(ok, msg)
    self.assertEqual(msg, "OK")


if __name__ == "__main__":
  unittest.main()
