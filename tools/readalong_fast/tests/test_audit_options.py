"""Experimental acceleration must preserve rejection of changed inputs."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tools.readalong.tests.build_audit_fixtures import make_clean_book
from tools.readalong_fast.benchmark_audit_options import Evidence, audit, mutation_checks


class AuditOptionTests(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    root = Path(self.temp.name)
    self.book = make_clean_book(root/'book')
    (self.book/'original.epub').write_bytes(b'synthetic-epub')
    self.candidate = root/'candidate'
    shutil.copytree(self.book/'readalong', self.candidate)
    path = self.candidate/'readalong.manifest.json'
    manifest = json.loads(path.read_text())
    manifest.update(sampleAligned=False, sourceEpubSha256=hashlib.sha256(b'synthetic-epub').hexdigest())
    path.write_text(json.dumps(manifest))
    (self.candidate/'projection.json').write_text(json.dumps({'audioTokens': 100, 'matchedTokens': 98}))
    self.warm = Evidence()
    self.assertTrue(audit(self.book, self.candidate, self.warm)['publishAllowed'])

  def assert_rejected_equally(self):
    expected = audit(self.book, self.candidate)
    self.assertFalse(expected['publishAllowed'])
    self.assertEqual(audit(self.book, self.candidate, self.warm), expected)
    self.assertEqual(audit(self.book, self.candidate, Evidence(), True), expected)

  def test_audio_change(self):
    with (self.book/'track_01.mp3').open('ab') as stream:
      stream.write(b'changed')
    self.assert_rejected_equally()

  def test_epub_change(self):
    (self.book/'original.epub').write_bytes(b'another-edition')
    self.assert_rejected_equally()

  def test_removed_audio(self):
    (self.book/'track_01.mp3').unlink()
    self.assert_rejected_equally()

  def test_added_audio(self):
    shutil.copy2(self.book/'track_01.mp3', self.book/'extra.mp3')
    self.assert_rejected_equally()

  def test_timeline_overlap(self):
    path = self.candidate/'timeline.json'
    rows = json.loads(path.read_text())
    rows[1]['start'] = 7
    path.write_text(json.dumps(rows))
    self.assert_rejected_equally()

  def test_dom_change(self):
    (self.candidate/'text/chapter1.html').write_text('<p id="different">Changed</p>')
    self.assert_rejected_equally()

  def test_stat_invalidation(self):
    self.assertTrue(all(mutation_checks().values()))
