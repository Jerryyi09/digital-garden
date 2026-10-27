"""A paragraph-wide fallback anchor must survive sentence marking.

The coarse paragraph pass assigns ``fast-*`` ids to block elements the EPUB
left unlabelled.  Sentence marking runs later, from disk.  If those ids never
reach disk, marking cannot preserve them and every ``SENTENCE_FROM_PARAGRAPH``
row ends up pointing at an id that no longer exists, which the audit reports
as ``DOM_REFERENCE_BROKEN``.

These tests drive the real two-pass handoff (``prepare_paragraphs`` ->
persist -> ``prepare_documents``) over synthetic EPUB documents covering the
three unlabelled block shapes observed in production.
"""
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from tools.readalong.authoritative_validator import DOMFragmentExtractor
from tools.readalong.engine.mark_sentence import mark_sentences
from tools.readalong.stream_projection import prepare_documents
from tools.readalong_fast.matcher import tokens
from tools.readalong_fast.pipeline import prepare_coarse_documents


# Each case is an unlabelled block element that the coarse pass must adopt.
# ``blocks`` counts the paragraph contexts the case is expected to produce.
UNLABELLED_BLOCKS = {
  "smallcaps": (1, "Chapter1.xhtml",
    '<html><body><p class="para">'
    'Y<span class="smallCaps">OU DON\'T KNOW ABOUT ME</span> without reading a book '
    'by the name of The Adventures of Huckleberry Finn, but that ain\'t no matter. '
    'That book was made by Mr. Mark Twain, and he told the truth, mainly.</p></body></html>'
  ),
  "dedication": (1, "black47.xhtml",
    '<html><body><p><em>Memoirs of the Due d\'Angouleme, and the life of Napoleon '
    'by the same author, form a sequel to this little work, which the writer '
    'offers to the reader as a token of respectful remembrance.</em></p></body></html>'
  ),
  "heading": (2, "black51.xhtml",
    '<html><body><h2>Chapter 16 One o\'Clock in the Morning</h2>'
    '<p>Julien found the night air cold against his face as he climbed the '
    'ladder, and he counted each rung twice before trusting his weight to it.</p>'
    '</body></html>'
  ),
}


def run_two_pass_handoff(root, spine):
  """Drive the production handoff: coarse pass, persist, then sentence marking."""
  docs, paragraphs, _ = prepare_coarse_documents(root, spine, [])
  sent_docs, _, _ = prepare_documents(root, spine, mark_sentences)
  return docs, paragraphs, sent_docs


def dom_ids(soup):
  parser = DOMFragmentExtractor()
  parser.feed(str(soup))
  parser.close()
  return parser.id_to_text


class ParagraphAnchorSurvivesMarkingTests(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.root = Path(self.temp.name)

  def write_case(self, case):
    blocks, name, html = UNLABELLED_BLOCKS[case]
    (self.root / name).write_text(html, encoding="utf-8")
    return blocks, name

  def test_unlabelled_block_gets_an_id_that_reaches_the_marked_dom(self):
    for case in UNLABELLED_BLOCKS:
      with self.subTest(case=case):
        blocks, name = self.write_case(case)
        _, paragraphs, sent_docs = run_two_pass_handoff(self.root, [name])
        self.assertEqual(len(paragraphs), blocks)
        anchor = paragraphs[0]["fragment"]
        self.assertTrue(anchor.startswith("fast-"), anchor)
        # The anchor the timeline will carry must exist in the DOM that ships.
        self.assertIn(anchor, dom_ids(sent_docs[name]))

  def test_fallback_anchor_text_matches_the_paragraph_payload(self):
    # A SENTENCE_FROM_PARAGRAPH row keeps the paragraph anchor and the paragraph
    # text, so the audit's canonical comparison must find them equal.
    for case in UNLABELLED_BLOCKS:
      with self.subTest(case=case):
        blocks, name = self.write_case(case)
        _, paragraphs, sent_docs = run_two_pass_handoff(self.root, [name])
        anchor = paragraphs[0]["fragment"]
        payload = tokens(paragraphs[0]["text"])
        dom_text = tokens(dom_ids(sent_docs[name])[anchor])
        self.assertEqual(payload, dom_text)

  def test_oversized_block_split_anchors_are_published_verbatim(self):
    # A publisher that ships a whole chapter as one block triggers the coarse
    # splitter.  The ids it mints are the ones the coarse timeline hands out, so
    # they must be the ids the published DOM carries: a sentence pass that
    # rewrote them would leave every one of those anchors dangling.
    name = "chapter01.xhtml"
    body = " ".join(f"Word{i} for the paragraph" for i in range(400))
    (self.root / name).write_text(f"<html><body><p>{body}</p></body></html>", encoding="utf-8")
    docs, paragraphs, sent_docs = run_two_pass_handoff(self.root, [name])
    self.assertGreater(len(paragraphs), 1,
      "the coarse splitter should have engaged on a 400-word block")
    soup = sent_docs[name]
    published = dom_ids(soup)
    for paragraph in paragraphs:
      self.assertIn(paragraph["fragment"], published,
        f"coarse split anchor {paragraph['fragment']} is missing from the published DOM")

  def test_audit_accepts_every_fallback_anchor(self):
    # End-to-end against the audit predicate: no DOM_REFERENCE_BROKEN may fire
    # for a paragraph fallback built from the two-pass handoff.
    from tools.readalong.authoritative_validator import canonical_text
    for case in UNLABELLED_BLOCKS:
      with self.subTest(case=case):
        _, name = self.write_case(case)
        _, paragraphs, sent_docs = run_two_pass_handoff(self.root, [name])
        parser = DOMFragmentExtractor()
        parser.feed(str(sent_docs[name]))
        parser.close()
        paragraph = paragraphs[0]
        anchor = paragraph["fragment"]
        dom_text = parser.id_to_text.get(anchor, "")
        self.assertEqual(canonical_text(dom_text), canonical_text(paragraph["text"]),
          f"{case}: fallback anchor {anchor} does not resolve to its paragraph text")


if __name__ == "__main__":
  unittest.main()
