"""Regression cases for global lexical correspondence and safe partial DOM cuts."""
import tempfile
import unittest
from pathlib import Path

from tools.readalong.stream_projection import prepare_documents, project_stream
from tools.readalong.authoritative_validator import DOMFragmentExtractor


class ProjectionTests(unittest.TestCase):
  def prepare(self, html):
    temp = tempfile.TemporaryDirectory()
    self.addCleanup(temp.cleanup)
    root = Path(temp.name)
    (root / "chapter.xhtml").write_text(html)
    return prepare_documents(root, ["chapter.xhtml"], lambda raw, **kwargs: raw)

  def words(self, tokens, cut=None):
    return [{"word": w, "start": i if cut is None or i < cut else i-cut,
             "end": (i if cut is None or i < cut else i-cut)+0.9,
             "audioSourceId": "01.mp3" if cut is None or i < cut else "02.mp3"}
            for i, w in enumerate(tokens)]

  def test_same_chapter_and_sentence_continue_across_tracks(self):
    docs, frags, tokens = self.prepare('<p><span id="c1-segment0">'
                                      'one two three <em>four five</em> six seven eight nine ten'
                                      '</span></p>')
    segments, _ = project_stream(tokens, frags, self.words(tokens, 4))
    self.assertEqual([s["audioSourceId"] for s in segments], ["01.mp3", "02.mp3"])
    self.assertEqual([s["text"] for s in segments],
                     ["one two three four", "five six seven eight nine ten"])
    parser = DOMFragmentExtractor()
    parser.feed(str(docs["chapter.xhtml"]))
    parser.close()
    self.assertEqual(parser.duplicate_ids, [])
    for segment in segments:
      self.assertEqual(parser.id_to_text[segment["fragment"]], segment["text"])
    self.assertEqual(docs["chapter.xhtml"].get_text(),
                     'one two three four five six seven eight nine ten')
    self.assertTrue(docs["chapter.xhtml"].find("em"))

  def test_missing_words_never_claim_whole_sentence(self):
    docs, frags, tokens = self.prepare('<p><span id="c1-segment0">'
                                      + ' '.join(f'word{i}' for i in range(30)) + '</span></p>')
    heard = tokens[:12] + tokens[15:]
    segments, stats = project_stream(tokens, frags, self.words(heard))
    self.assertEqual(stats["matchedTokens"], 27)
    self.assertNotIn("word12", ' '.join(s["text"] for s in segments))
    self.assertEqual(len(segments), 2)
    self.assertIn("word12", docs["chapter.xhtml"].get_text())

  def test_repeated_chapter_phrase_does_not_reset_second_track(self):
    common = 'the same recurring phrase appears in both chapters today'
    html = ''.join(f'<p><span id="c1-segment{i}">{text}</span></p>' for i, text in enumerate([
      common + ' first unique opening red apple blue sky',
      common + ' second unique ending green forest quiet sea']))
    _, frags, tokens = self.prepare(html)
    cut = len(frags[0]["words"])
    segments, _ = project_stream(tokens, frags, self.words(tokens, cut))
    self.assertEqual([s["fragment"] for s in segments], ["c1-segment0", "c1-segment1"])
    self.assertEqual(segments[1]["audioSourceId"], "02.mp3")

  def test_repeated_tail_is_diagnosed_not_silently_backtracked(self):
    first = 'one two three four five six seven eight nine ten'
    second = 'red blue green forest apple peach sky water mountain earth'
    _, frags, tokens = self.prepare(f'<p><span id="c1-segment0">{first}</span>'
                                    f'<span id="c1-segment1">{second}</span></p>')
    audio = self.words(tokens + tokens[:10])
    segments, stats = project_stream(tokens, frags, audio)
    self.assertEqual(len(segments), 2)
    self.assertEqual(stats["unmappedAudioRanges"][-1]["reason"], "POSSIBLE_REORDER_OR_REPEAT")
    self.assertEqual(stats["unmappedAudioRanges"][-1]["start"], 20)

  def test_no_match_does_not_create_fallback_or_timestamps(self):
    _, frags, tokens = self.prepare('<span id="c1-segment0">one two three four five six seven eight</span>')
    segments, _ = project_stream(tokens, frags, self.words(["unrelated"] * 10))
    self.assertEqual(segments, [])

  def test_zero_duration_word_is_not_given_a_fabricated_interval(self):
    _, frags, tokens = self.prepare('<span id="c1-segment0">one two three four five six seven eight</span>')
    words = self.words(tokens)
    words[2]["end"] = words[2]["start"]
    segments, stats = project_stream(tokens, frags, words)
    self.assertEqual(len(stats["unusableWordIntervals"]), 1)
    self.assertFalse(any(s["start"] == 2 for s in segments))

  def test_backwards_word_time_is_rejected(self):
    _, frags, tokens = self.prepare('<span id="c1-segment0">one two three four five six seven eight</span>')
    words = self.words(tokens)
    words[2]["end"] = 1
    with self.assertRaises(ValueError):
      project_stream(tokens, frags, words)

  def test_spine_cannot_escape_candidate(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      (root / "text").mkdir()
      (root / "secret.xhtml").write_text("secret")
      with self.assertRaises(ValueError):
        prepare_documents(root / "text", ["../secret.xhtml"], lambda raw, **kw: raw)

  def test_duplicate_input_ids_are_rejected(self):
    with self.assertRaises(ValueError):
      self.prepare('<span id="c1-segment0">hello</span><span id="c1-segment0">again</span>')

  def test_short_isolated_coincidences_are_not_anchors(self):
    _, frags, tokens = self.prepare('<span id="c1-segment0">one two three four five six seven eight</span>')
    segments, _ = project_stream(tokens, frags, self.words(["one", "two", "three"]))
    self.assertEqual(segments, [])
