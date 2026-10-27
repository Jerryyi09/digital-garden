"""An unlocated heading must be timed from the silence its neighbours leave.

A heading, a dedication line or a bare URL carries no coarse paragraph match of
its own, so nothing assigns it a time and the reader never highlights it.  The
audio that speaks it sits in the gap between the previous anchor's last segment
and the next anchor's first segment.

These tests drive ``locate_gap_blocks`` directly.  The window discipline is the
point: an unbounded search would let a short anchor match a coincidental phrase
elsewhere on the track, which is unusable on a multi-hour recording.
"""
import unittest

from bs4 import BeautifulSoup

from tools.readalong_fast.sentence_aligner import locate_gap_blocks


def soup_for(html):
  return BeautifulSoup(html, "html.parser")


def word(text, start, end, track="book.mp3"):
  return {"word": text, "start": start, "end": end, "audioSourceId": track}


def segment(anchor, start, end, text="", document="text/ch1.xhtml", track="book.mp3"):
  return {"audioSourceId": track, "start": start, "end": end, "document": document,
          "fragment": anchor, "sourceSentenceFragment": anchor, "text": text,
          "timingStatus": "SENTENCE_EXACT"}


HEADING_DOC = """
<html><body>
  <p id="c1-segment1">The preceding paragraph of ordinary prose.</p>
  <h2 id="c1-segment2">The Trolley Experiment</h2>
  <p id="c1-segment3">Thought experiments are often used to explore ethics.</p>
</body></html>
"""


class GapBlockTests(unittest.TestCase):
  def test_heading_between_two_located_paragraphs_gets_its_gap_seconds(self):
    documents = {"ch1.xhtml": soup_for(HEADING_DOC)}
    timeline = [
      segment("c1-segment1", 100.0, 104.0, "The preceding paragraph of ordinary prose."),
      segment("c1-segment3", 108.0, 112.0, "Thought experiments are often used to explore ethics."),
    ]
    words = [
      word("the", 105.0, 105.2), word("trolley", 105.2, 105.6),
      word("experiment", 105.6, 106.3),
    ]
    located = locate_gap_blocks(timeline, documents, words)
    self.assertEqual(len(located), 1, located)
    heading = located[0]
    self.assertEqual(heading["fragment"], "c1-segment2")
    self.assertEqual((heading["start"], heading["end"]), (105.0, 106.3))
    self.assertEqual(heading["document"], "text/ch1.xhtml")

  def test_audio_outside_the_gap_is_not_used(self):
    # The same phrase is spoken far away on the track.  The gap holds only
    # unrelated words, so the heading must stay unlocated rather than borrow it.
    documents = {"ch1.xhtml": soup_for(HEADING_DOC)}
    timeline = [
      segment("c1-segment1", 100.0, 104.0),
      segment("c1-segment3", 108.0, 112.0),
    ]
    words = [
      word("something", 105.0, 105.5), word("unrelated", 105.5, 106.0),
      word("the", 900.0, 900.2), word("trolley", 900.2, 900.6),
      word("experiment", 900.6, 901.3),
    ]
    self.assertEqual(locate_gap_blocks(timeline, documents, words), [])

  def test_a_sentence_left_out_of_a_located_paragraph_is_timed_too(self):
    # A URL line sits inside a paragraph whose other sentences did match.  It is
    # not a block of its own, but it is still an unlocated anchor between two
    # located ones.
    documents = {"ch1.xhtml": soup_for(
      '<html><body><p id="fast-abc"><span id="c1-segment1">You can download this chapter at:</span>'
      '<span id="c1-segment2">atomichabits.com/parenting</span></p>'
      '<p id="fast-def"><span id="c1-segment3">The paragraph after it.</span></p></body></html>')}
    timeline = [
      segment("c1-segment1", 200.0, 203.0, "You can download this chapter at:"),
      segment("c1-segment3", 210.0, 214.0, "The paragraph after it."),
    ]
    words = [
      word("atomichabits", 204.0, 204.9), word("com", 204.9, 205.2),
      word("parenting", 205.2, 205.9),
    ]
    located = locate_gap_blocks(timeline, documents, words)
    self.assertEqual([row["fragment"] for row in located], ["c1-segment2"])
    self.assertEqual((located[0]["start"], located[0]["end"]), (204.0, 205.9))

  def test_two_blocks_in_one_silence_do_not_share_the_same_seconds(self):
    documents = {"ch1.xhtml": soup_for(
      '<html><body>'
      '<p id="c1-segment1">First located paragraph.</p>'
      '<h2 id="c1-segment2">Alpha Heading</h2>'
      '<h2 id="c1-segment3">Beta Heading</h2>'
      '<p id="c1-segment4">Second located paragraph.</p>'
      '</body></html>')}
    timeline = [
      segment("c1-segment1", 100.0, 104.0),
      segment("c1-segment4", 112.0, 116.0),
    ]
    words = [
      word("alpha", 105.0, 105.6), word("heading", 105.6, 106.2),
      word("beta", 108.0, 108.5), word("heading", 108.5, 109.1),
    ]
    located = locate_gap_blocks(timeline, documents, words)
    by_anchor = {row["fragment"]: row for row in located}
    self.assertEqual(set(by_anchor), {"c1-segment2", "c1-segment3"})
    self.assertNotEqual(by_anchor["c1-segment2"]["start"], by_anchor["c1-segment3"]["start"])

  def test_a_short_anchor_survives_one_misspelled_proper_noun(self):
    # ASR rendered "atomichabits" as "atomicabits".  A three-word anchor has no
    # room for a ratio test, so it is accepted on the two words that did land.
    documents = {"ch1.xhtml": soup_for(
      '<html><body><p id="fast-abc"><span id="c1-segment1">You can download this chapter at:</span>'
      '<span id="c1-segment2">atomichabits.com/ parenting</span></p>'
      '<p id="fast-def"><span id="c1-segment3">The paragraph after it.</span></p></body></html>')}
    timeline = [
      segment("c1-segment1", 200.0, 203.0, "You can download this chapter at:"),
      segment("c1-segment3", 210.0, 214.0, "The paragraph after it."),
    ]
    words = [
      word("atomicabits", 204.0, 204.7), word(".com", 204.7, 205.4),
      word("-parenting.", 205.4, 206.2),
    ]
    located = locate_gap_blocks(timeline, documents, words)
    self.assertEqual([row["fragment"] for row in located], ["c1-segment2"])

  def test_a_long_anchor_still_needs_its_ratio(self):
    # Relaxing the short-anchor rule must not let a long heading match on a
    # couple of incidental words.
    documents = {"ch1.xhtml": soup_for(
      '<html><body><p id="c1-segment1">First located paragraph.</p>'
      '<h2 id="c1-segment2">The Most Successful Detective of All Time</h2>'
      '<p id="c1-segment3">Second located paragraph.</p></body></html>')}
    timeline = [
      segment("c1-segment1", 100.0, 104.0),
      segment("c1-segment3", 120.0, 124.0),
    ]
    words = [word("the", 108.0, 108.2), word("of", 108.2, 108.4),
             word("all", 108.4, 108.6)]
    self.assertEqual(locate_gap_blocks(timeline, documents, words), [])

  def test_a_following_document_that_reads_earlier_does_not_block_the_tail(self):
    # End matter is read back at the front of the book, so the next document's
    # segments can carry earlier timestamps.  That must not be mistaken for a
    # usable following neighbour.
    documents = {
      "ch1.xhtml": soup_for(
        '<html><body><p id="c1-segment1">First located paragraph.</p>'
        '<h2 id="c1-segment2">The Trolley Experiment</h2></body></html>'),
      "ch2.xhtml": soup_for(
        '<html><body><p id="c2-segment1">Index entry read at the front.</p></body></html>'),
    }
    timeline = [
      segment("c1-segment1", 100.0, 104.0, document="text/ch1.xhtml"),
      segment("c2-segment1", 5.0, 9.0, document="text/ch2.xhtml"),
    ]
    words = [word("the", 105.0, 105.2), word("trolley", 105.2, 105.6),
             word("experiment", 105.6, 106.3)]
    located = locate_gap_blocks(timeline, documents, words)
    self.assertEqual([row["fragment"] for row in located], ["c1-segment2"])
    self.assertEqual((located[0]["start"], located[0]["end"]), (105.0, 106.3))

  def test_no_zero_width_segment_is_emitted(self):
    documents = {"ch1.xhtml": soup_for(HEADING_DOC)}
    timeline = [
      segment("c1-segment1", 100.0, 104.0),
      segment("c1-segment3", 108.0, 112.0),
    ]
    # A single zero-width ASR word can match, but it cannot carry a highlight.
    words = [word("trolley", 105.0, 105.0)]
    for row in locate_gap_blocks(timeline, documents, words):
      self.assertGreater(row["end"], row["start"])


if __name__ == "__main__":
  unittest.main()
