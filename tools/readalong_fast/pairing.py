"""Try EPUB editions against shared observed audio samples, without deleting any."""
import hashlib
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

from tools.readalong.authoritative_validator import safe_path
from tools.readalong.batch_candidate_remapper import atomic_json
from tools.readalong.input_inventory import safe_extract_epub
from tools.readalong.universal_stream_aligner import get_spine_htmls
from tools.readalong_fast.matcher import ParagraphIndex, prepare_paragraphs


def choose_edition(candidates):
  """Several matching editions are acceptable; choose one deterministically."""
  passing = [c for c in candidates if c.get('locatedSamples', 0) >= 2]
  if passing:
    return max(passing, key=lambda c: (c['locatedSamples'], c['meanScore'], c['epubSha256']))
  # Byte-different EPUB copies with identical indexed text do not need an
  # operator to delete one. This shortcut does not assert audio compatibility.
  valid = [c for c in candidates if c.get('englishTextHint') is True]
  if len(valid) >= 2 and len({c['textSha256'] for c in valid}) == 1:
    return max(valid, key=lambda c: c['epubSha256'])
  return None


def pair_epubs(unit, output, cache, inputs):
  """Use up to three shared cache-first samples once, not once per edition."""
  book, output = Path(unit['book_dir']), Path(output)
  total = sum(t['measured_duration'] for t in unit['audio_tracks'])
  cap = max(t['measured_duration'] for t in unit['audio_tracks'])+1
  samples, cache_misses = [], []
  for fraction in (.1, .5, .85):
    position = total*fraction
    for track in unit['audio_tracks']:
      if position >= track['measured_duration']:
        position -= track['measured_duration']
        continue
      audio = safe_path(book, track['rel_to_book'])
      inputs.verify(audio, track['sha256'])
      duration = inputs.duration(audio, track['measured_duration']) if track['measured_duration'] > 1800 else track['measured_duration']
      start = max(0, min(position, duration-15))
      try:
        rows = cache.screen_clip(audio, track['sha256'], duration, cap, start, min(15, duration))
      except RuntimeError as exc:
        if not str(exc).startswith('CACHE_MISS:'):
          raise
        cache_misses.append({'audioSourceId': track['rel_to_book'], 'start': start, 'error': str(exc)})
      else:
        if not any(s['audioSourceId'] == track['rel_to_book'] and abs(s['start']-start) < .001 for s in samples):
          samples.append({'audioSourceId': track['rel_to_book'], 'start': start,
            'text': ' '.join(r['text'] for r in rows if not r.get('timingRejected'))})
      break
  results, by_sha = [], {}
  for i, candidate in enumerate(unit['epubs']):
    path = safe_path(book, candidate['rel_to_book'])
    inputs.verify(path, candidate['sha256'])
    root = output/'pairing'/str(i)
    try:
      safe_extract_epub(path, root)
      _, paragraphs, words = prepare_paragraphs(root, get_spine_htmls(path))
    except (ValueError, KeyError, ET.ParseError, zipfile.BadZipFile) as exc:
      results.append({'epubSha256': candidate['sha256'], 'path': candidate['rel_to_book'], 'error': str(exc)})
      continue
    index = ParagraphIndex(words, paragraphs)
    matches = [index.locate_detailed(s['text']) for s in samples]
    found = [m['match'] for m in matches if m['match'] is not None]
    common = {'the', 'and', 'of', 'to', 'in', 'is', 'was', 'a', 'he', 'she', 'that', 'it', 'with', 'for'}
    results.append({'epubSha256': candidate['sha256'], 'path': candidate['rel_to_book'],
      'locatedSamples': len(found), 'meanScore': sum(m['score'] for m in found)/max(1, len(found)),
      'matches': matches, 'textSha256': hashlib.sha256(' '.join(words).encode()).hexdigest(),
      'englishTextHint': len(words) >= 80 and sum(w in common for w in words)/len(words) >= .05})
    by_sha[candidate['sha256']] = candidate
  selected = choose_edition(results)
  atomic_json(output/'epub-pairing.json', {'candidates': results, 'samples': samples, 'cacheMisses': cache_misses,
    'selectedEpubSha256': selected['epubSha256'] if selected else None,
    'decision': 'SELECTED_MATCHING_OR_TEXT_EQUIVALENT_EDITION' if selected else 'PAIRING_EVIDENCE_REQUIRED',
    'originalEpubsUnchanged': True})
  if selected is None:
    raise ValueError('PAIRING_EVIDENCE_REQUIRED: multiple EPUBs tried; no reliable paired edition yet')
  return {**unit, 'epubs': [by_sha[selected['epubSha256']]]}
