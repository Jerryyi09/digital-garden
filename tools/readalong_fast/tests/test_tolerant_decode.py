"""Measured frame PTS can preserve playback time; guessed repair cannot."""
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools.readalong_fast.decoding import pcm_timeline, remap_segments
from tools.readalong_fast.pipeline import SpeechCache, normalize_native


def line(n, pts, samples):
  return f'[Parsed_ashowinfo_2 @ 0x1] n:{n} pts:{pts} pts_time:0 fmt:flt channels:1 chlayout:mono rate:16000 nb_samples:{samples}'


class TimelineDecodeTests(unittest.TestCase):
  def timing(self):
    # A real packet-time hole at 2..2.5s; compact PCM itself is only 4.5s long.
    return pcm_timeline(b'\0'*(72000*4), line(0, 0, 32000)+'\n'+line(1, 40000, 40000), 100, 5)

  def test_loss_does_not_shift_later_audio_half_a_second_early(self):
    timing = self.timing()
    self.assertEqual(timing['missingIntervals'], [{'start': 102, 'end': 102.5}])
    row = remap_segments([{'start': 103, 'end': 104, 'text': 'later speech'}], timing)[0]
    self.assertEqual((row['start'], row['end']), (103.5, 104.5))
    self.assertFalse(row.get('decodeTimingRejected'))

  def test_segment_crossing_loss_is_not_split_by_invented_word_timestamps(self):
    row = remap_segments([{'start': 101, 'end': 103, 'text': 'crosses loss'}], self.timing())[0]
    self.assertTrue(row['decodeTimingRejected'])
    clean, diag = normalize_native([row], 100, 105)
    self.assertTrue(clean[0]['timingRejected'])
    self.assertEqual(diag[0]['reason'], 'DECODE_TIMELINE_UNTRUSTED')

  def test_decode_error_marks_nearby_frames_suspect_even_without_a_time_hole(self):
    stderr = line(0, 0, 32000)+'\n[aac @ 0x1] Error decoding packet\n'+line(1, 32000, 48000)
    timing = pcm_timeline(b'\0'*(80000*4), stderr, 0, 5)
    self.assertTrue(timing['suspectIntervals'])
    self.assertTrue(remap_segments([{'start': 3, 'end': 4, 'text': 'suspect'}], timing)[0]['decodeTimingRejected'])

  def test_unmeasured_nonmonotonic_or_unaccounted_pcm_stays_untrusted(self):
    for stderr in ['', line(0, 0, 1000), line(0, 0, 40000)+'\n'+line(1, 30000, 40000)]:
      with self.subTest(stderr=stderr), self.assertRaises(ValueError):
        pcm_timeline(b'\0'*(80000*4), stderr, 0, 5)

  def test_filter_reinitialization_with_monotonic_pts_is_not_audio_loss(self):
    text = line(0, 0, 32000)+'\n'+line(0, 32000, 48000).replace('0x1', '0x2')
    timing = pcm_timeline(b'\0'*(80000*4), text, 0, 5)
    self.assertEqual(len(timing['windows']), 1)
    self.assertFalse(timing['missingIntervals'])

  def test_small_monotonic_frame_timestamp_overlap_is_localized_and_quarantined(self):
    stderr = '\n'.join([
      line(0, 0, 32000), line(1, 32000, 32000),
      line(2, 63680, 32000), line(3, 95680, 32000),
    ])
    timing = pcm_timeline(b'\0'*(8*16000*4), stderr, 100, 8)
    self.assertEqual(len(timing['windows']), 2)
    self.assertEqual(len(timing['suspectIntervals']), 1)
    clean = remap_segments([{'start': 100.5, 'end': 101.0, 'text': 'safe'},
      {'start': 104.1, 'end': 105.0, 'text': 'near overlap'}], timing)
    self.assertFalse(clean[0].get('decodeTimingRejected'))
    self.assertTrue(clean[1]['decodeTimingRejected'])

  def test_missing_pts_keeps_chunk_partial_and_never_calls_asr(self):
    with tempfile.TemporaryDirectory() as tmp:
      cache = SpeechCache(Path(tmp), [], 'a'*64)
      response = SimpleNamespace(stdout=b'\0'*(72000*4), stderr=b'[mp3 @ 0x1] Header missing', returncode=0)
      with patch('tools.readalong_fast.decoding.subprocess.run', return_value=response), \
           patch('tools.readalong_fast.pipeline.transcription_backend') as backend:
        rows = cache.chunk(Path('unused'), 'b'*64, 0, 5)
        cached = cache.chunk(Path('unused'), 'b'*64, 0, 5)
      self.assertFalse(backend.called)
      self.assertTrue(rows[0]['decodeUnavailable'])
      self.assertTrue(cached[0]['timingRejected'])
      self.assertTrue(cached[0]['decodeUnavailable'])

  def test_allow_new_asr_retries_previously_unavailable_cached_chunk(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      old, new = root/'old', root/'new'
      old.mkdir()
      cache = SpeechCache(new, [old], 'a'*64, asr_engine='serial')
      sha, duration = 'b'*64, 2.0
      params = cache.chunk_params(sha, 0.0, duration)
      key = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
      stale = [{'start': 0.0, 'end': duration, 'text': '',
        'decodeUnavailable': True, 'timingRejected': True}]
      (old/(key+'.json')).write_text(json.dumps({"parameters": params,
        "segments": stale, "rawSegments": stale, "decodedEnd": duration,
        "decodeAudit": {"status": "QUARANTINE"}}), encoding='utf-8')
      pcm = b'\0'*(int(duration*16000)*4)
      transcript = {'segments': [{'start': .1, 'end': 1.5, 'text': 'recovered words'}]}
      with patch('tools.readalong_fast.pipeline.decode_pcm', return_value=(pcm,
          {'status': 'FULL', 'timelineEnd': duration})), \
           patch('tools.readalong_fast.pipeline.transcription_backend', return_value=lambda *args, **kwargs: transcript):
        rows = cache.chunk(Path('unused.wav'), sha, 0.0, duration)
      self.assertEqual([row['text'] for row in rows], ['recovered words'])
      self.assertEqual(cache.stats['newAsrAudioSeconds'], duration)
      self.assertIn('RETRY_PREVIOUSLY_UNAVAILABLE_DECODE', {d['reason'] for d in cache.diagnostics})

  def test_word_cache_retries_empty_previously_unavailable_chunk(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      old, new = root/'old', root/'new'
      old.mkdir()
      cache = SpeechCache(new, [old], 'a'*64, asr_engine='words')
      sha, duration = 'b'*64, 2.0
      params = cache.chunk_params(sha, 0.0, duration)
      key = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
      stale = [{'start': 0.0, 'end': duration, 'text': '',
        'decodeUnavailable': True, 'timingRejected': True}]
      (old/(key+'.json')).write_text(json.dumps({"parameters": params,
        "segments": stale, "rawSegments": stale, "words": [], "decodedEnd": duration,
        "decodeAudit": {"status": "QUARANTINE"}}), encoding='utf-8')
      pcm = b'\0'*(int(duration*16000)*4)
      rows = [{'start': .1, 'end': 1.5, 'text': 'recovered words'}]
      words = [{'start': .1, 'end': .5, 'word': 'recovered'}, {'start': .6, 'end': 1.5, 'word': 'words'}]
      with patch('tools.readalong_fast.pipeline.decode_pcm', return_value=(pcm,
          {'status': 'FULL', 'timelineEnd': duration})), \
           patch.object(cache, 'transcribe_words_batched', return_value=(rows, words)):
        recovered = cache.chunk_words(Path('unused.wav'), sha, 0.0, duration)
      self.assertEqual([word['word'] for word in recovered], ['recovered', 'words'])
      self.assertEqual(cache.stats['newAsrAudioSeconds'], duration)
      self.assertIn('RETRY_PREVIOUSLY_UNAVAILABLE_WORD_CACHE', {d['reason'] for d in cache.diagnostics})

  def test_measured_recovery_reuses_corrected_cache_and_preserves_rejected_segments(self):
    with tempfile.TemporaryDirectory() as tmp:
      cache = SpeechCache(Path(tmp), [], 'a'*64)
      first = SimpleNamespace(stdout=b'\0'*(72000*4), stderr=b'', returncode=0)
      probe = SimpleNamespace(stdout=b'\0'*(72000*4), stderr=(line(0, 0, 32000)+'\n'+line(1, 40000, 40000)).encode(), returncode=0)
      backend = unittest.mock.Mock(return_value={'segments': [
        {'start': 1, 'end': 3, 'text': 'spans missing frames'}, {'start': 3, 'end': 4, 'text': 'valid later'}]})
      with patch('tools.readalong_fast.decoding.subprocess.run', side_effect=[first, probe]), \
           patch('tools.readalong_fast.pipeline.transcription_backend', return_value=backend):
        rows = cache.chunk(Path('unused'), 'b'*64, 100, 5)
        cached = cache.chunk(Path('unused'), 'b'*64, 100, 5)
      self.assertTrue(rows[0]['timingRejected'])
      self.assertTrue(cached[0]['timingRejected'])
      self.assertEqual(rows[-1]['start'], 103.5)
      self.assertEqual(cached[-1]['start'], 103.5)
      self.assertEqual(backend.call_count, 1)
