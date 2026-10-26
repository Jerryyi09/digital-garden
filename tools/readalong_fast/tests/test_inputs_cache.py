"""Language metadata and cache geometry must not manufacture input blockers."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from tools.readalong.batch_candidate_remapper import input_blocker
from tools.readalong_fast.pipeline import SpeechCache, InputCache, file_hash, generate
from tools.readalong_fast.pairing import choose_edition


class InputAndCacheTests(unittest.TestCase):
  def unit(self, languages):
    return {'audio_tracks': [{}], 'epubs': [{'valid_zip': True}], 'detected_languages': languages}

  def test_eng_and_unknown_metadata_are_not_non_english_audio(self):
    for languages in [['eng'], ['en_US'], ['UND'], ['unknown'], [], ['en', 'zh']]:
      with self.subTest(languages=languages):
        self.assertIsNone(input_blocker(self.unit(languages)))
    self.assertEqual(input_blocker(self.unit(['zh'])), 'LANGUAGE_REQUIRES_REVIEW')

  def test_direct_user_confirmation_has_precedence_over_metadata(self):
    unit = self.unit(['zh'])
    unit['languageOverride'] = {'language': 'en', 'source': 'direct_user_confirmation'}
    self.assertIsNone(input_blocker(unit))

  def test_fast_pipeline_can_try_multiple_epubs_without_deleting_any(self):
    unit = self.unit(['en'])
    unit['epubs'] *= 2
    self.assertIsNone(input_blocker(unit, allow_epub_pairing=True))
    self.assertEqual(input_blocker(unit), 'MULTI_EPUB')

  def test_any_reliably_matching_edition_is_acceptable(self):
    choices = [{'epubSha256': 'a', 'locatedSamples': 0, 'meanScore': 0},
      {'epubSha256': 'b', 'locatedSamples': 3, 'meanScore': .9},
      {'epubSha256': 'c', 'locatedSamples': 2, 'meanScore': 1}]
    self.assertEqual(choose_edition(choices)['epubSha256'], 'b')
    self.assertIsNone(choose_edition(choices[:1]))

  def test_single_english_hint_alone_is_not_audio_pairing_evidence(self):
    candidate = {'epubSha256': 'a', 'locatedSamples': 0, 'meanScore': 0,
      'englishTextHint': True, 'textSha256': 'same'}
    self.assertIsNone(choose_edition([candidate]))
    self.assertIsNotNone(choose_edition([candidate, {**candidate, 'epubSha256': 'b'}]))

  def cache(self, root, duration=100.00004, model='a'*64):
    params = {'sourceSha256': 'b'*64, 'modelSha256': model, 'start': 0.0, 'duration': duration,
      'language': 'en', 'word_timestamps': False, 'sampleRate': 16000, 'engine': 'mlx-segment-v1'}
    key = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
    rows = [{'start': 40, 'end': 55, 'text': 'the existing transcript already covers this sample'}]
    (root/(key+'.json')).write_text(json.dumps({'parameters': params, 'segments': rows}))

  def test_fifteen_second_screen_reuses_long_native_cache_without_asr(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      self.cache(root)
      cache = SpeechCache(root/'new', [root], 'a'*64, True)
      with patch('tools.readalong_fast.pipeline.transcription_backend', side_effect=AssertionError('ASR forbidden')):
        rows = cache.screen_clip(Path('unused'), 'b'*64, 100, 101, 42)
      self.assertTrue(rows)
      self.assertEqual(cache.stats['nativeContainingCacheHits'], 1)

  def test_display_rounding_does_not_invalidate_source_bound_native_cache(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      self.cache(root)
      cache = SpeechCache(root/'new', [root], 'a'*64, True)
      self.assertTrue(cache.chunk(Path('unused'), 'b'*64, 0.0, 100.0))

  def test_wrong_model_or_source_does_not_become_a_cache_hit(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      self.cache(root, model='c'*64)
      cache = SpeechCache(root/'new', [root], 'a'*64, True)
      with self.assertRaisesRegex(RuntimeError, 'CACHE_MISS'):
        cache.chunk(Path('unused'), 'b'*64, 0, 100)

  def test_real_generation_selects_matching_epub_and_counts_shared_probes(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      book = root/'book'
      book.mkdir()
      (book/'a.mp3').write_bytes(b'audio-fixture')
      text = 'alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu'
      epubs = []
      for name, body in [('wrong', 'nothing in this edition resembles the audio story at all'), ('right', text)]:
        path = book/(name+'.epub')
        with zipfile.ZipFile(path, 'w') as archive:
          archive.writestr('META-INF/container.xml', '<container><rootfiles><rootfile full-path="content.opf"/></rootfiles></container>')
          archive.writestr('content.opf', '<package><manifest><item id="c" href="c.html"/></manifest><spine><itemref idref="c"/></spine></package>')
          archive.writestr('c.html', '<html><body><p>'+body+'</p></body></html>')
        epubs.append({'rel_to_book': path.name, 'sha256': file_hash(path)})
      unit = {'book_dir': str(book), 'epubs': epubs,
        'audio_tracks': [{'rel_to_book': 'a.mp3', 'sha256': file_hash(book/'a.mp3'), 'measured_duration': 100}]}
      original = json.dumps(unit, sort_keys=True)
      cache = SpeechCache(root/'cache', [], 'a'*64, True)
      def probe(*args):
        cache.stats['screenCachedProbes'] += 1
        return [{'start': args[4], 'end': args[4]+15, 'text': text}]
      def block(*args):
        start, duration = args[2], args[3]
        return [{'start': start+i*15.0, 'end': start+i*15.0+15, 'text': text}
                for i in range(max(1, int(duration//15)))]
      with patch.object(cache, 'screen_clip', side_effect=probe) as probes, \
           patch.object(cache, 'chunk', side_effect=block), \
           patch.object(cache, 'whole_legacy_track', return_value=[{'start': 0, 'end': 100, 'text': text}]):
        report = generate(unit, root/'candidate', cache, InputCache(root/'inputs.json'))
      self.assertEqual(probes.call_count, 3)
      pairing = json.loads((root/'candidate/epub-pairing.json').read_text())
      self.assertEqual(pairing['selectedEpubSha256'], epubs[1]['sha256'])
      self.assertEqual(report['speechCacheStats']['screenCachedProbes'], 3)
      self.assertEqual(json.dumps(unit, sort_keys=True), original)
      self.assertTrue(all(file_hash(book/e['rel_to_book']) == e['sha256'] for e in epubs))

  def test_rejected_timing_does_not_resurrect_when_containing_cache_reused(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      self.cache(root)
      path = next(root.glob('*.json'))
      payload = json.loads(path.read_text())
      payload['segments'][0]['timingRejected'] = True
      path.write_text(json.dumps(payload))
      cache = SpeechCache(root/'new', [root], 'a'*64, True)
      self.assertTrue(cache.chunk(Path('unused'), 'b'*64, 0, 100)[0]['timingRejected'])
