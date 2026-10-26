"""Unit tests for NUC Alist verification rules matching client app.js."""
import unittest
from unittest.mock import MagicMock

from tools.readalong.nuc_verifier import AlistClient, verify_book_on_alist


class NucVerifierTests(unittest.TestCase):
  def setUp(self):
    self.client = MagicMock(spec=AlistClient)
    self.client.list_dir.return_value = {"code": 200, "message": "success"}

  def test_passes_when_all_conditions_met(self):
    manifest = {
      "schemaVersion": 1,
      "bookId": "TestBook",
      "readalongEnabled": True,
      "assetRevision": "a" * 32,
      "timeline": "timeline.json",
      "textRoot": "text/",
      "audioSources": [{"id": "t1.mp3", "name": "t1.mp3", "alistPath": "/750HD/有声书/文学作品/TestBook/t1.mp3"}]
    }
    timeline = [{"start": 0, "end": 10, "audioSourceId": "t1.mp3"}]

    self.client.list_dir.return_value = {
      "code": 200,
      "data": {
        "content": [
          {"name": "t1.mp3", "is_dir": False},
          {"name": "cover.jpg", "is_dir": False},
          {"name": "summary.txt", "is_dir": False},
          {"name": "content.opf", "is_dir": False}
        ]
      }
    }

    def fake_fetch_json(path):
      if "readalong.manifest.json" in path:
        return manifest, None
      if "timeline.json" in path:
        return timeline, None
      return None, "not found"

    def fake_fetch_raw(path):
      if "content.opf" in path:
        return b"<package></package>", None
      return None, "not found"

    def fake_get_file_info(path):
      return {"code": 200, "message": "success"}

    self.client.fetch_json.side_effect = fake_fetch_json
    self.client.fetch_raw.side_effect = fake_fetch_raw
    self.client.get_file_info.side_effect = fake_get_file_info

    ok, msg, details = verify_book_on_alist(self.client, "文学作品", "TestBook")
    self.assertTrue(ok, msg)
    self.assertEqual(msg, "OK")

  def test_fails_when_revision_directory_or_timeline_missing(self):
    manifest = {
      "schemaVersion": 1,
      "bookId": "TestBook",
      "readalongEnabled": True,
      "assetRevision": "b" * 32,
      "timeline": "timeline.json",
      "textRoot": "text/",
      "audioSources": [{"id": "t1.mp3", "alistPath": "/path/t1.mp3"}]
    }
    def fake_fetch_json(path):
      if "readalong.manifest.json" in path:
        return manifest, None
      if "timeline.json" in path:
        return None, "404 not found"
      return None, "not found"

    self.client.fetch_json.side_effect = fake_fetch_json
    ok, msg, details = verify_book_on_alist(self.client, "文学作品", "TestBook")
    self.assertFalse(ok)
    self.assertIn("TIMELINE_UNREADABLE", msg)

  def test_fails_when_audio_source_missing(self):
    manifest = {
      "schemaVersion": 1,
      "bookId": "TestBook",
      "readalongEnabled": True,
      "assetRevision": None,
      "timeline": "timeline.json",
      "textRoot": "text/",
      "audioSources": [{"id": "missing.mp3", "alistPath": "/750HD/有声书/文学作品/TestBook/missing.mp3"}]
    }
    timeline = [{"start": 0, "end": 5, "audioSourceId": "missing.mp3"}]
    def fake_fetch_json(path):
      if "readalong.manifest.json" in path:
        return manifest, None
      if "timeline.json" in path:
        return timeline, None
      return None, "not found"

    def fake_get_file_info(path):
      if "missing.mp3" in path:
        return {"code": 404, "message": "object not found"}
      return {"code": 200, "message": "success"}

    self.client.fetch_json.side_effect = fake_fetch_json
    self.client.get_file_info.side_effect = fake_get_file_info

    ok, msg, details = verify_book_on_alist(self.client, "文学作品", "TestBook")
    self.assertFalse(ok)
    self.assertIn("AUDIO_SOURCE_ALIST_PATH_NOT_FOUND", msg)

  def test_fails_when_audio_source_id_unmatched(self):
    manifest = {
      "schemaVersion": 1,
      "bookId": "TestBook",
      "readalongEnabled": True,
      "assetRevision": None,
      "timeline": "timeline.json",
      "textRoot": "text/",
      "audioSources": [{"id": "correct.mp3", "name": "correct.mp3", "alistPath": "/path/correct.mp3"}]
    }
    timeline = [{"start": 0, "end": 5, "audioSourceId": "wrong_audio_id.mp3"}]
    def fake_fetch_json(path):
      if "readalong.manifest.json" in path:
        return manifest, None
      if "timeline.json" in path:
        return timeline, None
      return None, "not found"

    def fake_get_file_info(path):
      return {"code": 200, "message": "success"}

    self.client.fetch_json.side_effect = fake_fetch_json
    self.client.get_file_info.side_effect = fake_get_file_info

    ok, msg, details = verify_book_on_alist(self.client, "文学作品", "TestBook")
    self.assertFalse(ok)
    self.assertIn("TIMELINE_SEGMENT_AUDIO_UNREGISTERED", msg)


if __name__ == "__main__":
  unittest.main()
