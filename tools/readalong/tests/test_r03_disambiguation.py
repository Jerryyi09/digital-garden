"""Reproduction tests for R03-03: Lexical disambiguation without length exemption."""

import tempfile
import unittest
from pathlib import Path

from tools.readalong.stream_projection import (
    prepare_documents,
    project_stream,
    find_reorder_matches,
    normalize_token,
)


class TestR03DisambiguationReproduction(unittest.TestCase):
    def setUp(self):
        # 20 distinct words
        self.repeated_text_20 = (
            "apple banana cherry date elderberry fig grape honeydew kiwi lemon "
            "mango nectarine orange papaya quince raspberry strawberry tangerine ugli voavanga"
        )
        self.tokens_20 = [normalize_token(w) for w in self.repeated_text_20.split()]
        self.assertEqual(len(self.tokens_20), 20)

    def _make_audio(self, tokens, source_id="track1.mp3", start_t=0.0):
        words = []
        t = start_t
        for w in tokens:
            words.append({
                "word": w,
                "start": round(t, 3),
                "end": round(t + 0.4, 3),
                "audioSourceId": source_id,
            })
            t += 0.5
        return words

    def test_minimal_counterexample_20_words_in_two_documents_rejected_as_ambiguous(self):
        """Minimal counterexample per LIB-VERIFY-03 (R03-03):

        Two documents both contain the exact same 20 distinct words.
        Audio only reads that 20-word phrase with NO distinguishing context.
        Expectation:
        - Must detect at least 2 competing book positions.
        - Must NOT accept the first one merely because size >= 16.
        - Must reject automatic selection as ambiguous without operator confirmation.
        """
        html_doc1 = f'<p><span id="doc1-segment0">{self.repeated_text_20}</span></p>'
        html_doc2 = f'<p><span id="doc2-segment0">{self.repeated_text_20}</span></p>'

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "doc1.xhtml").write_text(html_doc1, encoding="utf-8")
            (root / "doc2.xhtml").write_text(html_doc2, encoding="utf-8")
            docs, frags, tokens = prepare_documents(
                root, ["doc1.xhtml", "doc2.xhtml"], lambda raw, **kw: raw
            )

        # Audio reads only the 20-word text once
        audio = self._make_audio(self.tokens_20)

        # In current flawed code, SequenceMatcher in Phase 1 might match doc1 because it appears first,
        # or if treated as unmapped/reorder, b.size >= 16 bypasses ambiguity check!
        # When called without operator confirmation, it must NOT arbitrarily bind to doc1.
        # Specifically, test find_reorder_matches behavior:
        ngrams = {}
        for idx in range(len(tokens) - 6):
            ngrams.setdefault(tuple(tokens[idx:idx+7]), []).append(idx)

        # Both doc1 and doc2 positions exist in ngrams:
        first_ngram = tuple(self.tokens_20[:7])
        self.assertGreaterEqual(len(ngrams.get(first_ngram, [])), 2, "Must have at least 2 book positions")

        unmapped = [{"begin": 0, "end": len(audio)}]
        candidates, diagnostics = find_reorder_matches(
            tokens, [w["word"] for w in audio], audio, unmapped, ngrams, min_block_size=10
        )

        # Under the flawed current code:
        # candidate_blocks has b.size = 20 >= 16, so has_ambiguity is NOT set!
        # It accepts the block and does not flag ambiguity!
        # Under R03-03, candidates must be rejected or marked ambiguous, and NOT accepted as unambiguous:
        self.assertTrue(
            any(
                d.get("reason") in ("POSSIBLE_REORDER_OR_REPEAT", "AMBIGUOUS_REORDER_OR_REPEAT", "AMBIGUOUS_COMPETING_POSITIONS")
                and len(d.get("candidateBookTokenOffsets", [])) >= 2
                for d in diagnostics
            ),
            "Diagnostics must record ambiguity with at least 2 competing offsets"
        )
        # Furthermore, candidates must NOT contain an automatically confirmed/accepted block:
        # If candidates are produced, they must be marked ambiguous or not accepted:
        accepted_unambiguous = [
            c for c in candidates if not c.get("is_ambiguous", False)
        ]
        self.assertEqual(
            len(accepted_unambiguous), 0,
            "Ambiguous 20-word phrase across two documents must NOT be accepted as unambiguous"
        )

    def test_word_length_boundaries_cannot_bypass_ambiguity_check(self):
        """Testing length boundaries 7, 10, 15, 16, 20, 50 words repeated in two places.

        None of them can be declared unambiguous without context evidence.
        """
        words_50 = " ".join([f"token{i}" for i in range(50)])
        for count in [7, 10, 15, 16, 20, 50]:
            sub_phrase = " ".join(words_50.split()[:count])
            sub_tokens = [normalize_token(w) for w in sub_phrase.split()]

            # Build two documents with the identical phrase
            book_tokens = sub_tokens + ["middle", "divider", "words"] + sub_tokens
            ngrams = {}
            for idx in range(len(book_tokens) - 6):
                ngrams.setdefault(tuple(book_tokens[idx:idx+7]), []).append(idx)

            audio = self._make_audio(sub_tokens)
            unmapped = [{"begin": 0, "end": len(audio)}]
            candidates, _ = find_reorder_matches(
                book_tokens, sub_tokens, audio, unmapped, ngrams, min_block_size=min(count, 10)
            )

            # Every discovered candidate must be marked ambiguous because it appears twice in book
            for c in candidates:
                self.assertTrue(
                    c.get("is_ambiguous"),
                    f"Candidate of length {count} must be marked ambiguous when repeated in book"
                )
                self.assertGreaterEqual(
                    len(c.get("competing_offsets", [])), 2,
                    f"Length {count} must list at least 2 competing offsets"
                )

    def test_unambiguous_unique_phrase_is_accepted_as_unambiguous(self):
        """A phrase that exists exactly ONCE in the book is accepted as unambiguous."""
        unique_text = "the majestic golden eagle soared high above the snow capped mountain peaks"
        unique_tokens = [normalize_token(w) for w in unique_text.split()]
        other_text = "completely different background words appearing elsewhere in the library document"
        other_tokens = [normalize_token(w) for w in other_text.split()]
        book_tokens = other_tokens + unique_tokens + other_tokens

        ngrams = {}
        for idx in range(len(book_tokens) - 6):
            ngrams.setdefault(tuple(book_tokens[idx:idx+7]), []).append(idx)

        audio = self._make_audio(unique_tokens)
        unmapped = [{"begin": 0, "end": len(audio)}]
        candidates, _ = find_reorder_matches(
            book_tokens, unique_tokens, audio, unmapped, ngrams, min_block_size=10
        )
        self.assertEqual(len(candidates), 1)
        self.assertFalse(candidates[0].get("is_ambiguous"))
        self.assertEqual(len(candidates[0].get("competing_offsets")), 1)

    def test_invalid_operator_confirmation_does_not_instantiate_ambiguous_candidate(self):
        """Mismatched confirmed_reorders authorization fails to instantiate ambiguous candidate."""
        html_doc1 = f'<p><span id="doc1-segment0">{self.repeated_text_20}</span></p>'
        html_doc2 = f'<p><span id="doc2-segment0">{self.repeated_text_20}</span></p>'

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "doc1.xhtml").write_text(html_doc1, encoding="utf-8")
            (root / "doc2.xhtml").write_text(html_doc2, encoding="utf-8")
            docs, frags, tokens = prepare_documents(
                root, ["doc1.xhtml", "doc2.xhtml"], lambda raw, **kw: raw
            )

        audio = self._make_audio(self.tokens_20)
        # Operator confirmation provides wrong track id
        wrong_confirm = {"wrong_track.mp3"}
        segs, stats = project_stream(tokens, frags, audio, confirmed_reorders=wrong_confirm)
        self.assertEqual(len(segs), 0, "Ambiguous phrase must NOT instantiate with wrong confirmation")


if __name__ == "__main__":
    unittest.main()
