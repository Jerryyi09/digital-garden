"""Real physical-source audit, practical publication, pinned reading and rollback."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import sys
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from tools.readalong.tests.build_audit_fixtures import make_clean_book
from tools.readalong.practical_publisher import audit_practical, publish_practical, rollback_practical, exclude_readalong, accepts_practical_metrics


class PracticalPublicationTests(unittest.TestCase):
  def setUp(self):
    self.tmp = tempfile.TemporaryDirectory()
    self.addCleanup(self.tmp.cleanup)
    self.root = Path(self.tmp.name)
    self.book = make_clean_book(self.root/'book')
    (self.book/'original.epub').write_bytes(b'synthetic-epub')
    self.candidate = self.root/'candidate'
    shutil.copytree(self.book/'readalong', self.candidate)
    manifest = json.loads((self.candidate/'readalong.manifest.json').read_text())
    manifest.update(sampleAligned=False, sourceEpubSha256=hashlib.sha256(b'synthetic-epub').hexdigest())
    self.manifest = self.candidate/'readalong.manifest.json'
    self.manifest.write_text(json.dumps(manifest))
    (self.candidate/'projection.json').write_text(json.dumps({'audioTokens': 100, 'matchedTokens': 98}))

  def test_no_reference_needed_and_strict_status_is_not_faked(self):
    result = audit_practical(self.book, self.candidate)
    self.assertTrue(result['publishAllowed'], result)
    self.assertEqual(result['decision'], 'PUBLISH_WITH_GAPS')
    self.assertFalse(result['acousticAccuracyVerified'])
    self.assertNotEqual(result['certificationStatus'], 'PASS')

  def test_more_than_five_percent_is_excluded_not_pending_review(self):
    (self.candidate/'projection.json').write_text(json.dumps({'audioTokens': 100, 'matchedTokens': 94}))
    result = audit_practical(self.book, self.candidate)
    self.assertFalse(result['publishAllowed'])
    self.assertEqual(result['decision'], 'EXCLUDE_READALONG')

  def test_overlap_stays_a_hard_failure(self):
    path = self.candidate/'timeline.json'
    rows = json.loads(path.read_text())
    rows[1]['start'] = 7
    path.write_text(json.dumps(rows))
    self.assertFalse(audit_practical(self.book, self.candidate)['publishAllowed'])

  def test_physical_audio_or_epub_change_is_rejected(self):
    (self.book/'original.epub').write_bytes(b'different-edition')
    self.assertFalse(audit_practical(self.book, self.candidate)['publishAllowed'])
    (self.book/'original.epub').write_bytes(b'synthetic-epub')
    with (self.book/'track_01.mp3').open('ab') as stream:
      stream.write(b'changed')
    self.assertFalse(audit_practical(self.book, self.candidate)['publishAllowed'])

  def test_real_directory_publication_pins_assets_and_rolls_back(self):
    previous = json.loads((self.book/'readalong/readalong.manifest.json').read_text())
    previous_payload = {p.relative_to(self.book/'readalong').as_posix(): p.read_bytes()
      for p in (self.book/'readalong').rglob('*') if p.is_file()}
    original_audio = (self.book/'track_01.mp3').read_bytes()
    published = publish_practical(self.book, self.candidate)
    self.assertTrue(published['success'], published)
    manifest = json.loads((self.book/'readalong/readalong.manifest.json').read_text())
    revision = self.book/'.readalong_revisions'/manifest['assetRevision']
    self.assertTrue((revision/manifest['timeline']).is_file())
    timeline = json.loads((revision/manifest['timeline']).read_text())
    self.assertTrue(all((revision/s['document']).is_file() for s in timeline))
    self.assertEqual((self.book/'track_01.mp3').read_bytes(), original_audio)
    restored = rollback_practical(self.book, manifest['assetRevision'])
    self.assertTrue(restored['success'])
    self.assertEqual(json.loads((self.book/'readalong/readalong.manifest.json').read_text()), previous)
    restored_payload = {p.relative_to(self.book/'readalong').as_posix(): p.read_bytes()
      for p in (self.book/'readalong').rglob('*') if p.is_file()}
    self.assertEqual(restored_payload, previous_payload)
    self.assertTrue(revision.exists())

  def test_dry_run_does_not_replace_active(self):
    original = (self.book/'readalong/readalong.manifest.json').read_bytes()
    self.assertTrue(publish_practical(self.book, self.candidate, dry_run=True)['success'])
    self.assertEqual((self.book/'readalong/readalong.manifest.json').read_bytes(), original)
    self.assertFalse((self.book/'.readalong_revisions').exists())

  def test_candidate_mutated_during_copy_never_commits(self):
    original = (self.book/'readalong/readalong.manifest.json').read_bytes()
    copytree = shutil.copytree
    def changed(*args, **kwargs):
      result = copytree(*args, **kwargs)
      (self.candidate/'timeline.json').write_text('[]')
      return result
    with patch('tools.readalong.practical_publisher.shutil.copytree', side_effect=changed):
      with self.assertRaises(ValueError):
        publish_practical(self.book, self.candidate)
    self.assertEqual((self.book/'readalong/readalong.manifest.json').read_bytes(), original)

  def test_legacy_strict_publisher_still_requires_its_reference(self):
    from tools.readalong.controlled_publisher import publish_staging_to_active
    self.assertFalse(publish_staging_to_active(self.book, self.candidate)['success'])

  def test_actual_controlled_cli_accepts_practical_dry_run_without_reference(self):
    from tools.readalong.readalong_cli import main
    with patch.object(sys, 'argv', ['readalong', 'publish-practical', str(self.book), str(self.candidate), '--dry-run']), \
         redirect_stdout(StringIO()) as output:
      with self.assertRaises(SystemExit) as exit_result:
        main()
    self.assertEqual(exit_result.exception.code, 0)
    self.assertTrue(json.loads(output.getvalue())['success'])

  def test_exclusion_is_reversible_and_retains_audio_and_legacy_assets(self):
    original = (self.book/'readalong/readalong.manifest.json').read_bytes()
    audio = (self.book/'track_01.mp3').read_bytes()
    result = exclude_readalong(self.book, 'Exceeds practical tolerance')
    self.assertTrue(result['success'])
    manifest = json.loads((self.book/'readalong/readalong.manifest.json').read_text())
    self.assertFalse(manifest['readalongEnabled'])
    self.assertTrue((self.book/'readalong/text/chapter1.html').is_file())
    self.assertEqual((self.book/'track_01.mp3').read_bytes(), audio)
    self.assertTrue(rollback_practical(self.book, manifest['assetRevision'])['success'])
    self.assertEqual(json.loads((self.book/'readalong/readalong.manifest.json').read_text()), json.loads(original))

  def test_default_publish_cli_uses_personal_standard_not_reference_gate(self):
    from tools.readalong.readalong_cli import main
    with patch.object(sys, 'argv', ['readalong', 'publish', str(self.book), str(self.candidate), '--dry-run']), \
         redirect_stdout(StringIO()) as output:
      with self.assertRaises(SystemExit) as exit_result:
        main()
    self.assertEqual(exit_result.exception.code, 0)
    self.assertTrue(json.loads(output.getvalue())['success'])

  def test_lock_is_shared_with_strict_publisher(self):
    from tools.readalong.controlled_publisher import BookPublishLock
    with BookPublishLock(self.book):
      result = publish_practical(self.book, self.candidate)
    self.assertEqual(result['code'], 'ERR_PUBLISH_LOCKED')

  def test_source_mutated_during_copy_never_commits(self):
    original = (self.book/'readalong/readalong.manifest.json').read_bytes()
    copytree = shutil.copytree
    def changed(*args, **kwargs):
      result = copytree(*args, **kwargs)
      with (self.book/'track_01.mp3').open('ab') as stream:
        stream.write(b'changed-during-copy')
      return result
    with patch('tools.readalong.practical_publisher.shutil.copytree', side_effect=changed):
      with self.assertRaisesRegex(ValueError, 'Physical audio/EPUB changed'):
        publish_practical(self.book, self.candidate)
    self.assertEqual((self.book/'readalong/readalong.manifest.json').read_bytes(), original)

  def test_short_unobserved_gaps_are_not_invented_as_speech_errors(self):
    metrics = {'unmappedLexicalEstimate': .03, 'significantTimelineGapRatio': .06,
      'longUnobservedTimelineGapRatio': .01, 'unobservedDecodeSeconds': 0, 'physicalAudioSeconds': 1000}
    self.assertTrue(accepts_practical_metrics(metrics))
    self.assertFalse(accepts_practical_metrics({**metrics, 'longUnobservedTimelineGapRatio': .06}))
    self.assertFalse(accepts_practical_metrics({**metrics, 'unobservedDecodeSeconds': 60}))

  def test_controlled_cli_staging_inside_book_is_allowed_but_active_is_not(self):
    staging = self.book/('.readalong_staging_'+'a'*32)
    shutil.copytree(self.candidate, staging)
    self.assertTrue(publish_practical(self.book, staging, dry_run=True)['success'])
    with self.assertRaises(ValueError):
      publish_practical(self.book, self.book/'readalong', dry_run=True)

  def test_explicit_publication_ban_cannot_be_bypassed_by_scope_fields(self):
    result = audit_practical(self.book, self.candidate, {'publishAllowed': False})
    self.assertFalse(result['publishAllowed'])
    self.assertIn('forbids publication', result['reasons'][0])

  def test_accepted_publication_explicitly_enables_follow_along(self):
    manifest = json.loads(self.manifest.read_text())
    manifest['readalongEnabled'] = False
    self.manifest.write_text(json.dumps(manifest))
    self.assertTrue(publish_practical(self.book, self.candidate)['success'])
    self.assertTrue(json.loads((self.book/'readalong/readalong.manifest.json').read_text())['readalongEnabled'])
