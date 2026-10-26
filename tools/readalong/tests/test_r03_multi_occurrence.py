"""Reproduction tests for R03-02: True multi-occurrence support without losing re-read occurrences."""

import unittest
from bs4 import BeautifulSoup

from tools.readalong.stream_projection import prepare_documents, project_stream, normalize_token


class TestR03MultiOccurrenceReproduction(unittest.TestCase):
    def setUp(self):
        self.text_a = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu"
        self.text_b = "red blue green yellow orange purple black white silver gold brown pink"
        self.tokens_a = [normalize_token(w) for w in self.text_a.split()]
        self.tokens_b = [normalize_token(w) for w in self.text_b.split()]

    def _make_audio_stream(self, pattern, track_id="track1.mp3", start_time=0.0):
        # pattern is a list of token lists, e.g. [self.tokens_a, self.tokens_b, ...]
        audio = []
        cur_t = start_time
        for group in pattern:
            for w in group:
                audio.append({
                    "word": w,
                    "start": round(cur_t, 3),
                    "end": round(cur_t + 0.4, 3),
                    "audioSourceId": track_id,
                })
                cur_t += 0.5
        return audio

    def test_reproduce_six_occurrences_a_b_a_b_a_b(self):
        """Minimal reproduction: Text has paragraphs A and B.

        Audio reads A B A B A B.
        Expectation: Exactly 6 independent paragraph occurrences (3 for A, 3 for B),
        with distinct physical timestamps and correct occurrence identities, NOT 4.
        """
        html = (
            f'<p><span id="c1-segment0">{self.text_a}</span></p>'
            f'<p><span id="c1-segment1">{self.text_b}</span></p>'
        )
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "c1.xhtml").write_text(html, encoding="utf-8")
            docs, frags, tokens = prepare_documents(root, ["c1.xhtml"], lambda raw, **kw: raw)

        # Pattern: A B A B A B
        pattern = [
            self.tokens_a, self.tokens_b,
            self.tokens_a, self.tokens_b,
            self.tokens_a, self.tokens_b,
        ]
        audio = self._make_audio_stream(pattern)

        # Under the current implementation, this only generates 4 segments because
        # active_reorder_positions is keyed on book offset, overwriting earlier re-reads.
        segments, stats = project_stream(tokens, frags, audio, confirmed_reorders=True)

        # Strict assertion per LIB-VERIFY-03 (R03-02):
        self.assertEqual(
            len(segments), 6,
            f"Expected 6 independent occurrences (A B A B A B), but got {len(segments)} segments"
        )

        # Verify 3 occurrences of segment0 and 3 of segment1
        seg0_list = [s for s in segments if s["fragment"] == "c1-segment0"]
        seg1_list = [s for s in segments if s["fragment"] == "c1-segment1"]
        self.assertEqual(len(seg0_list), 3, "Expected 3 occurrences of segment0")
        self.assertEqual(len(seg1_list), 3, "Expected 3 occurrences of segment1")

        # Verify monotonicity of timestamps across all 6 segments
        for i in range(len(segments) - 1):
            self.assertLessEqual(
                segments[i]["end"], segments[i + 1]["start"],
                f"Segment {i} ({segments[i]['fragment']}) overlaps with next segment {i+1} ({segments[i+1]['fragment']})"
            )

    def test_same_paragraph_re_read_three_and_five_times(self):
        """Single paragraph re-read 3 times and 5 times produces 3 and 5 occurrences."""
        import tempfile
        from pathlib import Path
        html = f'<p><span id="c1-segment0">{self.text_a}</span></p>'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "c1.xhtml").write_text(html, encoding="utf-8")
            _, frags, tokens = prepare_documents(root, ["c1.xhtml"], lambda raw, **kw: raw)

        # 3 times
        audio_3 = self._make_audio_stream([self.tokens_a, self.tokens_a, self.tokens_a])
        segs_3, _ = project_stream(tokens, frags, audio_3, confirmed_reorders=True)
        self.assertEqual(len(segs_3), 3, f"Expected 3 occurrences, got {len(segs_3)}")
        self.assertEqual([s["occurrenceId"] for s in segs_3], ["0", "1", "2"])

        # 5 times
        audio_5 = self._make_audio_stream([self.tokens_a] * 5)
        segs_5, _ = project_stream(tokens, frags, audio_5, confirmed_reorders=True)
        self.assertEqual(len(segs_5), 5, f"Expected 5 occurrences, got {len(segs_5)}")
        self.assertEqual([s["occurrenceId"] for s in segs_5], ["0", "1", "2", "3", "4"])

    def test_re_reading_with_unrelated_interludes_between_repeats(self):
        """Unrelated words (e.g. narrator cough/speech) between repeats must not fuse sentences."""
        import tempfile
        from pathlib import Path
        html = f'<p><span id="c1-segment0">{self.text_a}</span></p>'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "c1.xhtml").write_text(html, encoding="utf-8")
            _, frags, tokens = prepare_documents(root, ["c1.xhtml"], lambda raw, **kw: raw)

        unrelated = ["cough", "throat", "clearing", "pause", "interlude"]
        audio = self._make_audio_stream([self.tokens_a, unrelated, self.tokens_a])
        segs, stats = project_stream(tokens, frags, audio, confirmed_reorders=True)
        self.assertEqual(len(segs), 2)
        # There should be an unmapped gap between seg 0 and seg 1 containing unrelated words
        self.assertGreater(segs[1]["start"], segs[0]["end"] + 1.0)
        self.assertEqual(segs[0]["occurrenceId"], "0")
        self.assertEqual(segs[1]["occurrenceId"], "1")

    def test_cross_track_re_reading(self):
        """Same paragraph read in track1.mp3, and re-read in track2.mp3."""
        import tempfile
        from pathlib import Path
        html = f'<p><span id="c1-segment0">{self.text_a}</span></p>'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "c1.xhtml").write_text(html, encoding="utf-8")
            _, frags, tokens = prepare_documents(root, ["c1.xhtml"], lambda raw, **kw: raw)

        audio_t1 = self._make_audio_stream([self.tokens_a], track_id="01.mp3", start_time=0.0)
        audio_t2 = self._make_audio_stream([self.tokens_a], track_id="02.mp3", start_time=0.0)
        segs, _ = project_stream(tokens, frags, audio_t1 + audio_t2, confirmed_reorders=True)
        self.assertEqual(len(segs), 2)
        self.assertEqual(segs[0]["audioSourceId"], "01.mp3")
        self.assertEqual(segs[1]["audioSourceId"], "02.mp3")

    def test_missing_one_occurrence_in_acoustic_reference_fails_pass(self):
        """Acoustic reference missing any occurrence must reject PASS."""
        from tools.readalong.acoustic_evaluator import evaluate_acoustic_accuracy, occurrence_key
        timeline = [
            {"audioSourceId": "t1.mp3", "document": "text/c1.xhtml", "fragment": "c1-seg0", "occurrenceId": "0", "start": 0.0, "end": 5.0},
            {"audioSourceId": "t1.mp3", "document": "text/c1.xhtml", "fragment": "c1-seg0", "occurrenceId": "1", "start": 10.0, "end": 15.0},
        ]
        # Reference only has occurrence 0
        ref_data = {
            occurrence_key(timeline[0]): {"start": 0.0, "end": 5.0},
        }
        res = evaluate_acoustic_accuracy(timeline, ref_data)
        self.assertFalse(res["passed"], "Missing second occurrence reference MUST NOT pass")
        self.assertEqual(res["status"], "COVERAGE_INSUFFICIENT")


if __name__ == "__main__":
    unittest.main()
