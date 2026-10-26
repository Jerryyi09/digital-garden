"""Unit tests for Tier 1 local static audit and natural sorting."""
import json
from pathlib import Path
import tempfile
import unittest

from tools.readalong.full_inventory_scanner import natural_sort_key
from tools.readalong.tier_verifier import tier1_local_static_check


class TierVerifierTests(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.root = Path(self.temp.name)

  def test_natural_sort_ordering(self):
    tracks = ["10.mp3", "1.mp3", "2.mp3", "20.mp3", "11.mp3", "9.mp3"]
    sorted_tracks = sorted(tracks, key=natural_sort_key)
    self.assertEqual(sorted_tracks, ["1.mp3", "2.mp3", "9.mp3", "10.mp3", "11.mp3", "20.mp3"])

  def test_tier1_catches_missing_highlight_css(self):
    book_dir = self.root / "TestBook"
    ra = book_dir / "readalong"
    ra.mkdir(parents=True)
    text_dir = ra / "text"
    text_dir.mkdir()
    # HTML without .readalong-active
    (text_dir / "c1.html").write_text("<html><head></head><body><span id='s1'>Hello</span></body></html>")
    (book_dir / "t1.mp3").write_bytes(b"audio")

    manifest = {
      "schemaVersion": 1,
      "bookId": "TestBook",
      "timeline": "timeline.json",
      "textRoot": "text/",
      "audioSources": [{"id": "t1.mp3", "alistPath": f"/750HD/有声书/Category/TestBook/t1.mp3"}]
    }
    timeline = [{"audioSourceId": "t1.mp3", "start": 0.0, "end": 2.0, "document": "text/c1.html", "fragment": "s1", "text": "Hello"}]
    (ra / "readalong.manifest.json").write_text(json.dumps(manifest))
    (ra / "timeline.json").write_text(json.dumps(timeline))

    ok, issues, metrics = tier1_local_static_check(book_dir)
    self.assertFalse(ok)
    self.assertTrue(any("HIGHLIGHT_CSS_MISSING" in i for i in issues))

  def test_tier1_catches_url_encoded_documents(self):
    book_dir = self.root / "TestBookEncoded"
    ra = book_dir / "readalong"
    ra.mkdir(parents=True)
    text_dir = ra / "text"
    text_dir.mkdir()
    (text_dir / "c1.html").write_text("<html><head><style>.readalong-active{}</style></head><body><span id='s1'>Hello</span></body></html>")
    (book_dir / "t1.mp3").write_bytes(b"audio")

    manifest = {
      "schemaVersion": 1,
      "bookId": "TestBook",
      "timeline": "timeline.json",
      "textRoot": "text/",
      "audioSources": [{"id": "t1.mp3", "alistPath": f"/750HD/有声书/Category/TestBookEncoded/t1.mp3"}]
    }
    # Encoded path: text/c%201.html
    timeline = [{"audioSourceId": "t1.mp3", "start": 0.0, "end": 2.0, "document": "text/c%201.html", "fragment": "s1", "text": "Hello"}]
    (ra / "readalong.manifest.json").write_text(json.dumps(manifest))
    (ra / "timeline.json").write_text(json.dumps(timeline))

    ok, issues, metrics = tier1_local_static_check(book_dir)
    self.assertFalse(ok)
    self.assertTrue(any("DOCUMENT_PATH_URL_ENCODED" in i for i in issues))


if __name__ == "__main__":
  unittest.main()
