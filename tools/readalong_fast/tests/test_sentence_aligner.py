"""Unit tests for sentence_aligner DOM refinement logic."""
import unittest
from bs4 import BeautifulSoup

from tools.readalong_fast.sentence_aligner import refine_timeline_by_dom, merge_stream_projection_with_paragraph_fallback


class SentenceAlignerTests(unittest.TestCase):
  def test_refine_paragraph_into_sentences(self):
    html = """
    <html><body>
    <div id="p1">
      <span id="c1-segment1">First sentence here.</span>
      <span id="c1-segment2">Second sentence follows.</span>
    </div>
    </body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    documents = {"text/ch1.xhtml": soup}

    para_timeline = [
      {
        "audioSourceId": "audio.mp3",
        "start": 0.0,
        "end": 6.0,
        "document": "text/ch1.xhtml",
        "fragment": "p1",
        "text": "First sentence here. Second sentence follows.",
        "speechUnitId": "0",
        "occurrenceId": "0"
      }
    ]

    ordered_words = [
      {"word": "First", "start": 0.5, "end": 0.9, "audioSourceId": "audio.mp3"},
      {"word": "sentence", "start": 1.0, "end": 1.5, "audioSourceId": "audio.mp3"},
      {"word": "here", "start": 1.6, "end": 2.2, "audioSourceId": "audio.mp3"},
      {"word": "Second", "start": 3.0, "end": 3.5, "audioSourceId": "audio.mp3"},
      {"word": "sentence", "start": 3.6, "end": 4.1, "audioSourceId": "audio.mp3"},
      {"word": "follows", "start": 4.2, "end": 5.5, "audioSourceId": "audio.mp3"},
    ]

    refined = refine_timeline_by_dom(para_timeline, documents, ordered_words)
    self.assertEqual(len(refined), 2)
    self.assertEqual(refined[0]["fragment"], "c1-segment1")
    self.assertEqual(refined[0]["start"], 0.5)
    self.assertEqual(refined[0]["end"], 2.2)
    self.assertEqual(refined[0]["speechUnitId"], "0")

    self.assertEqual(refined[1]["fragment"], "c1-segment2")
    self.assertEqual(refined[1]["start"], 3.0)
    self.assertEqual(refined[1]["end"], 6.0)
    self.assertEqual(refined[1]["speechUnitId"], "0")

  def test_unmatched_sentence_keeps_paragraph_anchor_and_is_marked_fallback(self):
    soup = BeautifulSoup("""<html><body><div id="p1">
      <span id="c1-segment1">First sentence here.</span>
      <span id="c1-segment2">Second sentence follows.</span>
    </div></body></html>""", "html.parser")
    paragraph = [{"audioSourceId": "audio.mp3", "start": 0.0, "end": 6.0,
      "document": "text/ch1.xhtml", "fragment": "p1", "text": "Paragraph text",
      "speechUnitId": "coarse-1", "occurrenceId": "0"}]
    words = [{"word": "First", "start": .5, "end": .9, "audioSourceId": "audio.mp3"},
      {"word": "sentence", "start": 1., "end": 1.5, "audioSourceId": "audio.mp3"},
      {"word": "here", "start": 1.6, "end": 2.2, "audioSourceId": "audio.mp3"}]
    refined = refine_timeline_by_dom(paragraph, {"ch1.xhtml": soup}, words)
    fallback = next(row for row in refined if row["timingStatus"] == "SENTENCE_FROM_PARAGRAPH")
    self.assertEqual(fallback["fragment"], "p1")
    self.assertEqual(fallback["text"], "First sentence here. Second sentence follows.")
    self.assertEqual(fallback["speechUnitId"], "coarse-1")

  def test_stream_match_replaces_only_its_paragraph_fallback(self):
    projected = [{"audioSourceId": "a", "document": "text/c.xhtml", "fragment": "s1",
      "start": 1.0, "end": 2.0, "timingStatus": "TIMING_UNVERIFIED"}]
    fallback = [{"audioSourceId": "a", "document": "text/c.xhtml", "fragment": "p1",
      "sourceSentenceFragment": "s1", "start": 0.0, "end": 3.0,
      "timingStatus": "SENTENCE_FROM_PARAGRAPH"},
      {"audioSourceId": "a", "document": "text/c.xhtml", "fragment": "p1",
      "sourceSentenceFragment": "s2", "start": 3.0, "end": 6.0,
      "timingStatus": "SENTENCE_FROM_PARAGRAPH"}]
    merged = merge_stream_projection_with_paragraph_fallback(projected, fallback)
    self.assertEqual([row["fragment"] for row in merged], ["s1", "p1"])
    self.assertEqual(merged[-1]["sourceSentenceFragment"], "s2")

  def test_repeated_dom_occurrences_get_distinct_ids(self):
    rows = [{"audioSourceId": "a", "document": "text/c.xhtml", "fragment": "s1",
      "start": 1.0, "end": 2.0, "occurrenceId": "0", "timingStatus": "TIMING_UNVERIFIED"},
      {"audioSourceId": "a", "document": "text/c.xhtml", "fragment": "s1",
      "start": 4.0, "end": 5.0, "occurrenceId": "0", "timingStatus": "TIMING_UNVERIFIED"}]
    merged = merge_stream_projection_with_paragraph_fallback(rows, [])
    self.assertEqual(len({row["occurrenceId"] for row in merged}), 2)

  def test_paragraph_anchor_resolves_across_split_document_path_mismatch(self):
    wrong = BeautifulSoup("<html><body><p id='other'>Different text.</p></body></html>", "html.parser")
    right = BeautifulSoup("<html><body><p id='p1'><span id='s-segment1'>A short paragraph here.</span></p></body></html>", "html.parser")
    coarse = [{"audioSourceId": "a", "start": 1.0, "end": 2.0, "document": "text/wrong.xhtml",
      "fragment": "p1", "text": "A short paragraph here.", "speechUnitId": "u", "occurrenceId": "0"}]
    refined = refine_timeline_by_dom(coarse, {"text/wrong.xhtml": wrong, "text/right.xhtml": right}, [])
    self.assertEqual(refined[0]["document"], "text/text/right.xhtml")
    self.assertEqual(refined[0]["fragment"], "p1")
    self.assertEqual(refined[0]["sourceSentenceFragment"], "s-segment1")

  def test_fallback_is_clamped_to_observed_audio_and_has_unique_occurrence(self):
    soup = BeautifulSoup("<html><body><div id='p1'>Fallback text.</div></body></html>", "html.parser")
    coarse = [
      {"audioSourceId": "a", "start": 9.0, "end": 12.0, "document": "text/c.xhtml",
       "fragment": "p1", "text": "Fallback text.", "speechUnitId": "u", "occurrenceId": "0"},
      {"audioSourceId": "a", "start": 9.0, "end": 12.0, "document": "text/c.xhtml",
       "fragment": "p1", "text": "Fallback text.", "speechUnitId": "u", "occurrenceId": "0"},
    ]
    words = [{"word": "Fallback", "start": 9.1, "end": 9.4, "audioSourceId": "a"}]
    refined = refine_timeline_by_dom(coarse, {"text/c.xhtml": soup}, words, {"a": 9.4})
    self.assertTrue(all(row["end"] <= 9.4 for row in refined))
    self.assertEqual(len({row["occurrenceId"] for row in refined}), 2)

  def test_fallback_recovers_paragraph_when_first_word_is_split_by_inline_markup(self):
    soup = BeautifulSoup("<html><body><p id='p1'><span id='c-segment1'>O</span><span id='c-segment2'>ne day, my students sat together for a long discussion about this important book.</span></p></body></html>", "html.parser")
    coarse = [{"audioSourceId": "a", "start": 1.0, "end": 4.0, "document": "text/c.xhtml",
      "fragment": "stale-id", "text": "One day, my students sat together for a long discussion about this important book.",
      "speechUnitId": "u", "occurrenceId": "0"}]
    refined = refine_timeline_by_dom(coarse, {"text/c.xhtml": soup}, [])
    self.assertEqual(refined[0]["fragment"], "p1")
    self.assertEqual(refined[0]["timingStatus"], "SENTENCE_FROM_PARAGRAPH")

  def test_short_heading_fallback_requires_exact_dom_text(self):
    soup = BeautifulSoup("<html><body><h2 id='heading'><span id='c-segment1'>Creativity and self-actualization</span></h2><p id='p1'><span id='c-segment2'>A paragraph follows this heading with more than enough text to map.</span></p></body></html>", "html.parser")
    coarse = [{"audioSourceId": "a", "start": 1.0, "end": 2.0, "document": "text/c.xhtml",
      "fragment": "stale-heading", "text": "Creativity and self-actualization", "speechUnitId": "u", "occurrenceId": "0"}]
    refined = refine_timeline_by_dom(coarse, {"text/c.xhtml": soup}, [])
    self.assertEqual(refined[0]["fragment"], "heading")
    self.assertEqual(refined[0]["timingStatus"], "SENTENCE_FROM_PARAGRAPH")

  def test_fallback_recovers_paragraph_when_middle_word_splits_across_inline_markup(self):
    soup = BeautifulSoup("<html><body><p id='p1'><span id='c-segment1'>The sign over the Arab Vendor’s stall reads L</span><span id='c-segment2'>INGERIE. He shows Ilsa a lace bed sheet.</span></p></body></html>", "html.parser")
    coarse = [{"audioSourceId": "a", "start": 1.0, "end": 4.0, "document": "text/c.xhtml",
      "fragment": "stale-id", "text": "The sign over the Arab Vendor’s stall reads LINGERIE. He shows Ilsa a lace bed sheet.",
      "speechUnitId": "u", "occurrenceId": "0"}]
    refined = refine_timeline_by_dom(coarse, {"text/c.xhtml": soup}, [])
    self.assertEqual(refined[0]["fragment"], "p1")
    self.assertEqual(refined[0]["timingStatus"], "SENTENCE_FROM_PARAGRAPH")


if __name__ == "__main__":
  unittest.main()
