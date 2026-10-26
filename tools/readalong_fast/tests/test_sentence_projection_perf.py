"""Regression coverage for repeated DOM recovery and unmatched trailing tracks."""
import time
import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup
from tools.readalong_fast import sentence_aligner
from tools.readalong.stream_projection import project_stream


class SentenceProjectionPerformanceTests(unittest.TestCase):
  def test_multitrack_repeated_recovery_and_unmatched_tail_is_bounded(self):
    text = "One day the students discussed the important question about this book together."
    paragraphs = ''.join(
      f'<p id="p{i}"><span id="c{i}-segment1">O</span>'
      f'<span id="c{i}-segment2">ne day the students discussed the important question about this book together.</span></p>'
      for i in range(100))
    soup = BeautifulSoup(f'<html><body>{paragraphs}</body></html>', 'html.parser')
    coarse = [{"audioSourceId": f"track{track}", "start": row * 3., "end": row * 3. + 2.,
               "document": "text/c.xhtml", "fragment": "stale", "text": text}
              for track in range(3) for row in range(100)]
    words = [{"audioSourceId": f"track{track}", "start": i * .2, "end": i * .2 + .1,
              "word": "unrelated"} for track in range(3, 6) for i in range(1000)]
    started = time.perf_counter()
    with patch.object(sentence_aligner, "SequenceMatcher", wraps=sentence_aligner.SequenceMatcher) as matcher:
      refined = sentence_aligner.refine_timeline_by_dom(coarse, {"c.xhtml": soup}, words)
      # Repeated stale IDs must not repeat the whole-document fuzzy search.
      self.assertLess(matcher.call_count, 350)
    _, stats = project_stream([f"token{i}" for i in range(3000)], [], words)
    elapsed = time.perf_counter() - started
    self.assertLess(elapsed, 3.0)
    self.assertTrue(refined)
    self.assertTrue(all(row["audioSourceId"] in {"track0", "track1", "track2"} for row in refined))
    self.assertEqual(stats["matchedTokens"], 0)

  def test_interval_index_keeps_long_overlapping_and_unsorted_words(self):
    html = '<p id="p"><span id="s-segment1">First sentence here.</span><span id="s-segment2">Second sentence follows.</span></p>'
    words = [{"audioSourceId": "a", "word": word, "start": start, "end": end}
             for word, start, end in [("First", 0., 9.), ("sentence", 7., 7.2), ("here", 8., 8.2),
                                      ("Second", 9., 9.2), ("sentence", 9.3, 9.5), ("follows", 9.6, 9.8)]]
    coarse = [{"audioSourceId": "a", "start": 8., "end": 10., "document": "text/c.xhtml", "fragment": "p"}]
    ordered = sentence_aligner.refine_timeline_by_dom(coarse, {"c.xhtml": BeautifulSoup(html, 'html.parser')}, words)
    # An out-of-order irrelevant word forces the legacy full-filter fallback.
    extra = {"audioSourceId": "a", "word": "outside", "start": 0., "end": .1}
    unordered = sentence_aligner.refine_timeline_by_dom(coarse, {"c.xhtml": BeautifulSoup(html, 'html.parser')}, words + [extra])
    self.assertEqual(ordered, unordered)

  def test_recovered_id_is_visible_to_later_cross_document_lookup(self):
    documents = {"right.xhtml": BeautifulSoup('<p><span id="s-segment1">Exact paragraph text.</span></p>', 'html.parser'),
                 "wrong.xhtml": BeautifulSoup('<p>Other paragraph.</p>', 'html.parser')}
    base = {"audioSourceId": "a", "start": 1., "end": 2., "document": "text/right.xhtml",
            "fragment": "recovered", "text": "Exact paragraph text."}
    rows = sentence_aligner.refine_timeline_by_dom([base, {**base, "document": "text/wrong.xhtml", "start": 3., "end": 4.}], documents, [])
    self.assertEqual(rows[0]["fragment"], "recovered")
    self.assertEqual(rows[1]["document"], "text/right.xhtml")
    self.assertEqual(rows[1]["fragment"], "recovered")

class IndexedProjectionEquivalenceTests(unittest.TestCase):
  def test_matches_standard_algorithm_with_repeats_ties_and_reorders(self):
    from collections import defaultdict
    from difflib import SequenceMatcher
    from random import Random
    from tools.readalong.stream_projection import indexed_matching_blocks
    rng = Random(20261026)
    cases = [(['a'] * 80, ['a'] * 100), (list('abcdefghij') * 5, list('abcdefghij') * 3),
             ([], []), (list('abcdefg'), list('abcdefg'))]
    for case in range(400):
      book = [rng.choice('abc') for _ in range(rng.randint(0,120))]
      audio = [rng.choice('abc') for _ in range(rng.randint(0,120))]
      if case % 2 and book:
        audio[rng.randrange(len(audio)+1):] = book[rng.randrange(len(book)):]
      cases.append((book, audio))
    for book, audio in cases:
      index = defaultdict(list)
      for i in range(len(book)-6):
        index[tuple(book[i:i+7])].append(i)
      for minimum in (7, 10):
        expected = [b for b in SequenceMatcher(None, book, audio, autojunk=False).get_matching_blocks() if b.size >= minimum]
        self.assertEqual(indexed_matching_blocks(book, audio, index, minimum), expected)

  def test_unmatched_trailing_tracks_do_not_invoke_global_sequence_matcher(self):
    import tools.readalong.stream_projection as projection
    book = [f'body{i}' for i in range(12000)]
    heard = book[:2000] + [f'appendix{i}' for i in range(8000)]
    words = [{'word': word, 'audioSourceId': str(i // 2000), 'start': (i % 2000) * .2,
              'end': (i % 2000) * .2 + .1} for i, word in enumerate(heard)]
    started = time.perf_counter()
    with patch.object(projection, 'SequenceMatcher', wraps=projection.SequenceMatcher) as matcher:
      _, stats = projection.project_stream(book, [], words)
    self.assertEqual(matcher.call_count, 0)
    self.assertEqual(stats['primaryMatchedTokens'], 2000)
    self.assertEqual(stats['reorderMatchedTokens'], 0)
    self.assertLess(time.perf_counter() - started, 2.0)

class FallbackMergeIndexTests(unittest.TestCase):
  def test_index_preserves_overlap_ties_and_excludes_touching_boundaries(self):
    fallback = [{"audioSourceId": "a", "document": "text/c", "fragment": f"p{i}",
                 "start": float(i*2), "end": float(i*2+2), "text": f"paragraph{i}"} for i in range(3)]
    projected = [{"audioSourceId": "a", "document": "text/c", "fragment": "fine",
                  "start": 1., "end": 3.},
                 {"audioSourceId": "a", "document": "text/c", "fragment": "boundary", "start": 6., "end": 7.}]
    merged = sentence_aligner.merge_stream_projection_with_paragraph_fallback(projected, fallback)
    self.assertEqual(merged[0]["fragment"], "p0")
    self.assertEqual(merged[1]["fragment"], "p2")
    self.assertEqual(merged[2]["fragment"], "boundary")

  def test_many_disjoint_fallbacks_do_not_require_cartesian_scan(self):
    fallback = [{"audioSourceId": "a", "document": "text/c", "fragment": f"p{i}",
                 "start": float(i*2), "end": float(i*2+2), "text": str(i)} for i in range(6000)]
    projected = [{"audioSourceId": "a", "document": "text/c", "fragment": f"s{i}",
                  "start": float(i*2)+.2, "end": float(i*2)+.8} for i in range(6000)]
    started = time.perf_counter()
    merged = sentence_aligner.merge_stream_projection_with_paragraph_fallback(projected, fallback)
    self.assertLess(time.perf_counter()-started, 2.)
    self.assertEqual(len(merged), 6000)
    self.assertTrue(all(row['fragment'] == f'p{i}' for i,row in enumerate(merged)))
