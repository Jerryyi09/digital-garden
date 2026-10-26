"""Reproduction tests for R03-04: Cross-segment DOM splitting must not clone internal IDs."""

import tempfile
import unittest
import os
from unittest.mock import patch
from pathlib import Path
from bs4 import BeautifulSoup

from tools.readalong.stream_projection import prepare_documents, project_stream, normalize_token
from tools.readalong.stream_projection import is_document_already_marked
from tools.readalong.authoritative_validator import DOMFragmentExtractor
from tools.readalong.config import resolve_nltk_data_path


class TestR03DOMIntegrityReproduction(unittest.TestCase):
    def setUp(self):
        environment = patch.dict(os.environ, {"NLTK_DATA": str(resolve_nltk_data_path())})
        environment.start()
        self.addCleanup(environment.stop)

    def test_ninety_nine_percent_marked_still_cannot_skip_last_paragraph(self):
        html = '<html><body><p><span id="c1-segment0">' + 'alpha ' * 200 + '</span></p><p>Unmarked ending.</p></body></html>'
        self.assertFalse(is_document_already_marked(html))
        from tools.readalong.engine.mark_sentence import mark_sentences
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ch.xhtml").write_text(html)
            docs, fragments, tokens = prepare_documents(root, ["ch.xhtml"], mark_sentences)
        self.assertIn("unmarked", tokens)
        self.assertIn("ending", tokens)
        ids = [node["id"] for node in docs["ch.xhtml"].find_all(id=True)]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("c1-segment0", ids)

    def test_mixed_marked_and_unmarked_same_block_preserves_existing_marker(self):
        from tools.readalong.engine.mark_sentence import mark_sentences
        html = '<p><span id="c1-segment0">Already marked.</span> Missing tail.</p>'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ch.xhtml").write_text(html)
            docs, fragments, tokens = prepare_documents(root, ["ch.xhtml"], mark_sentences)
        self.assertEqual(tokens, ["already", "marked", "missing", "tail"])
        soup = docs["ch.xhtml"]
        self.assertEqual(soup.find(id="c1-segment0").get_text(), "Already marked.")
        self.assertFalse(soup.find(id="c1-segment0").find("span"))
        ids = [node["id"] for node in soup.find_all(id=True)]
        self.assertEqual(len(ids), len(set(ids)))

    def test_head_and_comments_do_not_count_as_unmarked_body(self):
        html = '<html><head><title>Metadata</title></head><body><!--note--><p><span id="c1-segment0">Complete.</span></p></body></html>'
        self.assertTrue(is_document_already_marked(html))

    def test_cross_track_split_across_inline_tag_with_id_does_not_clone_id(self):
        """Minimal counterexample per LIB-VERIFY-03 (R03-04):

        <p><span id="c1-segment0">one <em id="inline-ref">two three four five six</em> seven eight nine ten eleven twelve</span></p>
        Audio cuts after fourth word ("four"), so <em id="inline-ref"> crosses track split boundary.
        Expectation:
        - Must NOT create duplicate id="inline-ref" in DOM.
        - Must preserve visible text, inline formatting, and unique reference target semantics.
        """
        html = (
            '<p><span id="c1-segment0">'
            'one <em id="inline-ref">two three four five six</em> seven eight nine ten eleven twelve'
            '</span></p>'
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ch1.xhtml").write_text(html, encoding="utf-8")
            docs, frags, tokens = prepare_documents(root, ["ch1.xhtml"], lambda raw, **kw: raw)

        # Audio words cut after the 4th word:
        # tokens: ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"]
        # Words 0..3 on track 01.mp3, words 4..11 on track 02.mp3
        audio = []
        for i, t in enumerate(tokens):
            track = "01.mp3" if i < 4 else "02.mp3"
            t_start = i if i < 4 else (i - 4)
            audio.append({
                "word": t,
                "start": float(t_start),
                "end": float(t_start + 0.8),
                "audioSourceId": track,
            })

        segments, stats = project_stream(tokens, frags, audio)

        # Verify DOM of modified document
        doc_html = str(docs["ch1.xhtml"])
        soup = BeautifulSoup(doc_html, "html.parser")

        # Find all nodes with id="inline-ref"
        inline_refs = soup.find_all(id="inline-ref")
        all_ids = [node["id"] for node in soup.find_all(id=True)]

        # Under the flawed current code, inline-ref is cloned into both segment spans!
        self.assertEqual(
            len(inline_refs), 1,
            f"Expected exactly 1 node with id='inline-ref', but found {len(inline_refs)} (duplicate cloned IDs: {all_ids})"
        )
        self.assertEqual(
            len(all_ids), len(set(all_ids)),
            f"All IDs in the document must be globally unique, but found duplicates: {all_ids}"
        )

    def test_comment_pseudo_marker_does_not_skip_real_marking(self):
        """Comments containing 'segment0' must not fool idempotency check into skipping sentence marking."""
        html = (
            '<!-- <span id="chapter-segment0">comment fake marker</span> -->'
            '<p>The quick brown fox jumps over the lazy dog in the sunny morning forest.</p>'
        )
        called = False

        def mock_marker(raw, **kw):
            nonlocal called
            called = True
            return raw.replace(
                '<p>The quick',
                '<p><span id="c1-segment0">The quick'
            ).replace('forest.</p>', 'forest.</span></p>')

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ch1.xhtml").write_text(html, encoding="utf-8")
            docs, frags, tokens = prepare_documents(root, ["ch1.xhtml"], mock_marker)

        self.assertTrue(called, "Marker MUST be called when segment string is only in an HTML comment")
        self.assertGreater(len(frags), 0, "Real text must be marked and extracted as fragments")

    def test_partial_pre_marking_does_not_skip_unmarked_paragraphs(self):
        """A document with only one paragraph pre-marked must have unmarked paragraphs marked."""
        html = (
            '<p><span id="c1-segment0">Short title.</span></p>'
            '<p>A very long second paragraph that has not been marked at all and must not be skipped by idempotency.</p>'
        )
        called = False

        def mock_marker(raw, **kw):
            nonlocal called
            called = True
            return raw.replace(
                '<p>A very long',
                '<p><span id="c1-segment1">A very long'
            ).replace('idempotency.</p>', 'idempotency.</span></p>')

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ch1.xhtml").write_text(html, encoding="utf-8")
            docs, frags, tokens = prepare_documents(root, ["ch1.xhtml"], mock_marker)

        self.assertTrue(called, "Marker MUST be called when substantial text in document is unmarked")
        # Both paragraphs should be extracted
        self.assertGreaterEqual(len(frags), 2, "Both paragraphs must have fragments")


if __name__ == "__main__":
    unittest.main()
