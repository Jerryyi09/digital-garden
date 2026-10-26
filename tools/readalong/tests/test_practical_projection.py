"""Practical recovery must retain real word intervals and visible text."""
import tempfile
import unittest
from pathlib import Path
from tools.readalong.stream_projection import prepare_documents, project_stream


class PracticalProjectionTests(unittest.TestCase):
  def prepare(self, paragraphs):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      (root / "c.html").write_text("".join(f'<p><span id="c-segment{i}">{p}</span></p>' for i, p in enumerate(paragraphs)))
      return prepare_documents(root, ["c.html"], lambda raw, **kw: raw)

  def audio(self, words):
    return [{"word": word, "start": i*.5, "end": i*.5+.4, "audioSourceId": "a"} for i, word in enumerate(words)]

  def test_unique_repeat_mode_recovers_physical_occurrences(self):
    text = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu"
    _, frags, tokens = self.prepare([text])
    rows, stats = project_stream(tokens, frags, self.audio(tokens*3), confirmed_reorders="auto_unique")
    self.assertEqual(len(rows), 3)
    self.assertEqual(stats["matchedTokens"], len(tokens)*3)
    self.assertEqual([r["occurrenceId"] for r in rows], ["0", "1", "2"])

  def test_anchored_spelling_error_recovers_without_invented_time(self):
    text = "one two three four five six seven eight extraordinary red blue green gold purple pink orange white black"
    _, frags, tokens = self.prepare([text])
    heard = tokens[:]
    heard[8] = "extraordnary"
    rows, stats = project_stream(tokens, frags, self.audio(heard))
    self.assertEqual(stats["fuzzyMatchedTokens"], 1)
    self.assertEqual(len(rows), 1)
    self.assertEqual(rows[0]["start"], 0)
    self.assertEqual(rows[0]["end"], self.audio(heard)[-1]["end"])
    self.assertLess(rows[0]["matchedWordRatio"], 1)
    self.assertIn("extraordinary", rows[0]["text"])

  def test_long_pause_inside_matching_sentence_remains_a_real_gap(self):
    _, frags, tokens = self.prepare(["alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu"])
    heard = self.audio(tokens)
    for word in heard[6:]:
      word["start"] += 40
      word["end"] += 40
    rows, _ = project_stream(tokens, frags, heard)
    self.assertEqual(len(rows), 2)
    self.assertGreater(rows[1]["start"] - rows[0]["end"], 40)
