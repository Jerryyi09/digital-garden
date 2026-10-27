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

  def test_encoded_document_does_not_mask_later_findings(self):
    # A single encoded path used to break the scan, so every problem behind it
    # went unreported and one fix produced a fresh failure on the next run.
    book_dir = self.root / "TestBookEncodedThenBroken"
    ra = book_dir / "readalong"
    ra.mkdir(parents=True)
    text_dir = ra / "text"
    text_dir.mkdir()
    (text_dir / "c1.html").write_text("<html><head><style>.readalong-active{}</style></head><body><span id='s1'>Hello</span></body></html>")
    (book_dir / "t1.mp3").write_bytes(b"audio")

    manifest = {
      "schemaVersion": 1,
      "bookId": "TestBookEncodedThenBroken",
      "timeline": "timeline.json",
      "textRoot": "text/",
      "audioSources": [{"id": "t1.mp3", "alistPath": "/750HD/有声书/Category/TestBookEncodedThenBroken/t1.mp3"}]
    }
    timeline = [
      {"audioSourceId": "t1.mp3", "start": 0.0, "end": 2.0, "document": "text/c%201.html", "fragment": "s1", "text": "Hello"},
      {"audioSourceId": "t1.mp3", "start": 2.0, "end": 4.0, "document": "text/c1.html", "fragment": "absent", "text": "Hello"},
    ]
    (ra / "readalong.manifest.json").write_text(json.dumps(manifest))
    (ra / "timeline.json").write_text(json.dumps(timeline))

    ok, issues, metrics = tier1_local_static_check(book_dir)
    self.assertFalse(ok)
    self.assertTrue(any("DOCUMENT_PATH_URL_ENCODED" in i for i in issues))
    self.assertTrue(any("FRAGMENT_ANCHOR_MISSING" in i for i in issues),
      f"the encoded path masked a later finding: {issues}")

  def test_unsafe_document_path_is_reported_not_read(self):
    book_dir = self.root / "TestBookTraversal"
    ra = book_dir / "readalong"
    ra.mkdir(parents=True)
    (ra / "text").mkdir()
    (book_dir / "t1.mp3").write_bytes(b"audio")
    (book_dir / "outside.html").write_text("<html><body><span id='s1'>Hello</span></body></html>")

    manifest = {
      "schemaVersion": 1,
      "bookId": "TestBookTraversal",
      "timeline": "timeline.json",
      "textRoot": "text/",
      "audioSources": [{"id": "t1.mp3", "alistPath": "/750HD/有声书/Category/TestBookTraversal/t1.mp3"}]
    }
    timeline = [{"audioSourceId": "t1.mp3", "start": 0.0, "end": 2.0,
                 "document": "text/../outside.html", "fragment": "s1", "text": "Hello"}]
    (ra / "readalong.manifest.json").write_text(json.dumps(manifest))
    (ra / "timeline.json").write_text(json.dumps(timeline))

    ok, issues, metrics = tier1_local_static_check(book_dir)
    self.assertFalse(ok)
    self.assertTrue(any("DOCUMENT_PATH_UNSAFE" in i for i in issues), issues)


class SpineHrefDecodingTests(unittest.TestCase):
  """An OPF href may percent-encode characters the archive stores literally."""

  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.root = Path(self.temp.name)

  def build_epub(self, hrefs, entry_names):
    import zipfile
    path = self.root / "mixed.epub"
    items = "".join(f'<item id="i{index}" href="{href}" media-type="application/xhtml+xml"/>'
                    for index, href in enumerate(hrefs))
    refs = "".join(f'<itemref idref="i{index}"/>' for index in range(len(hrefs)))
    with zipfile.ZipFile(path, "w") as z:
      z.writestr("mimetype", "application/epub+zip")
      z.writestr("META-INF/container.xml",
        '<?xml version="1.0"?><container version="1.0" '
        'xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles>'
        '<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
        '</rootfiles></container>')
      z.writestr("OEBPS/content.opf",
        '<?xml version="1.0"?><package xmlns="http://www.idpf.org/2007/opf" version="2.0" '
        'unique-identifier="id"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        '<dc:title>T</dc:title><dc:identifier id="id">x</dc:identifier></metadata>'
        f'<manifest>{items}</manifest><spine>{refs}</spine></package>')
      for name in entry_names:
        z.writestr(name, "<html><body><p>Body text for the encoding probe.</p></body></html>")
    return path

  def test_encoded_and_literal_hrefs_resolve_to_the_same_real_names(self):
    from tools.readalong.universal_stream_aligner import get_spine_htmls
    epub = self.build_epub(
      ["Orwell - 1984 - part one.html", "Orwell%20-%201984%20-%20part%20two.html"],
      ["OEBPS/Orwell - 1984 - part one.html", "OEBPS/Orwell - 1984 - part two.html"])
    spine = get_spine_htmls(epub)
    self.assertEqual(spine, ["OEBPS/Orwell - 1984 - part one.html",
                             "OEBPS/Orwell - 1984 - part two.html"])
    self.assertFalse(any("%" in name for name in spine))

  def test_every_returned_name_is_an_archive_entry(self):
    import zipfile
    from tools.readalong.universal_stream_aligner import get_spine_htmls
    epub = self.build_epub(
      ["a%20b.html", "plain.html"],
      ["OEBPS/a b.html", "OEBPS/plain.html"])
    with zipfile.ZipFile(epub) as z:
      stored = set(z.namelist())
    for name in get_spine_htmls(epub):
      self.assertIn(name, stored, f"{name} is not a real archive entry")

  def test_a_literal_percent_in_an_entry_name_is_preserved(self):
    # An archive may legitimately store a literal '%'.  Decoding must not
    # invent a different name for it.
    from tools.readalong.universal_stream_aligner import get_spine_htmls
    epub = self.build_epub(["100%25.html"], ["OEBPS/100%.html"])
    self.assertEqual(get_spine_htmls(epub), ["OEBPS/100%.html"])


if __name__ == "__main__":
  unittest.main()
