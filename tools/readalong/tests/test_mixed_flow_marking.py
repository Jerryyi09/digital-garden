"""Mixed block/inline flow must preserve layout, references and complete text."""
import unittest
import os
from unittest.mock import patch
from bs4 import BeautifulSoup
from tools.readalong.config import resolve_nltk_data_path

from tools.readalong.engine.mark_sentence import mark_sentences
from tools.readalong.stream_projection import uncovered_text_nodes
from tools.readalong.authoritative_validator import DOMFragmentExtractor


class MixedFlowMarkingTests(unittest.TestCase):
  def setUp(self):
    environment = patch.dict(os.environ, {"NLTK_DATA": str(resolve_nltk_data_path())})
    environment.start()
    self.addCleanup(environment.stop)

  def assert_complete(self, raw):
    original = BeautifulSoup(raw, "lxml")
    marked = mark_sentences(raw, chapter_id="mixed")
    soup = BeautifulSoup(marked, "html.parser")
    self.assertEqual(soup.get_text(), original.get_text())
    self.assertEqual(uncovered_text_nodes(soup), [])
    parser = DOMFragmentExtractor()
    parser.feed(marked)
    parser.close()
    self.assertEqual(parser.duplicate_ids, [])
    for span in soup.find_all("span", id=lambda value: value and "-segment" in value):
      self.assertIsNone(span.find(["p", "li", "ul", "ol", "div", "table", "td"]))
      self.assertIsNone(span.find("span", id=lambda value: value and "-segment" in value))
    return soup

  def test_list_item_has_direct_text_before_and_after_paragraph(self):
    raw = ('<ol><li class="bullets" value="1"><span class="_idfootnotelink">1</span> '
           'You believe that creating your best life is a matter of deciding what you want.'
           '<p>Yet psychological research shows a different result.</p> Then reflect again.</li></ol>')
    soup = self.assert_complete(raw)
    self.assertEqual(soup.li.get("value"), "1")
    self.assertEqual(soup.li.get("class"), ["bullets"])
    self.assertEqual(len(soup.find_all("p")), 1)
    self.assertEqual(soup.find(class_="_idfootnotelink").get_text(), "1")

  def test_legacy_leaf_only_traversal_reproduces_the_gap(self):
    from tools.readalong.engine import mark_sentence as engine
    raw = '<ul><li>Prefix text.<p>Inner paragraph.</p>Suffix text.</li></ul>'
    def leaf_only(root, chapter_id, counter, language, min_words):
      for elem in root.find_all(["p", "li", "div"]):
        if not engine._has_block_children(elem) and engine._has_meaningful_text(elem):
          counter = engine._process_element_preserve_structure(
            elem, chapter_id, counter, language, min_words)
      return counter
    with patch.object(engine, "_mark_flow_content", side_effect=leaf_only):
      legacy = engine.mark_sentences(raw, chapter_id="legacy")
    self.assertGreater(len(uncovered_text_nodes(BeautifulSoup(legacy, "html.parser"))), 0)
    self.assert_complete(raw)

  def test_nested_list_and_inline_wrappers_preserve_references(self):
    raw = ('<div id="parent">Leading <em id="em">emphasis</em>.'
           '<ul><li>Outer <a id="ref" href="#target">link</a>.'
           '<ol><li id="target">Nested item.</li></ol> Outer tail.</li></ul> Final tail.</div>')
    soup = self.assert_complete(raw)
    self.assertEqual(soup.find(id="ref")["href"], "#target")
    self.assertEqual(len(soup.find_all(id="target")), 1)
    self.assertEqual(len(soup.find_all("ol")), 1)
    self.assertEqual(len(soup.find_all("li")), 2)

  def test_inline_wrapper_around_child_block_is_not_flattened(self):
    raw = '<div>Before <span id="wrap">Inside <section>Block text.</section> More.</span> After.</div>'
    soup = self.assert_complete(raw)
    self.assertIsNotNone(soup.find(id="wrap").section)

  def test_body_text_comments_breaks_and_empty_anchors_survive(self):
    raw = ('<html><body>Plain beginning.<!--keep--><section>Section prefix.'
           '<p><a id="empty"></a>Some <em>inline</em><br/> text.</p> Section suffix.</section>'
           ' Plain ending.</body></html>')
    soup = self.assert_complete(raw)
    self.assertEqual(len(soup.find_all(id="empty")), 1)
    self.assertEqual(len(soup.find_all("br")), 1)
    self.assertIn("<!--keep-->", str(soup))

  def test_existing_segment_and_internal_anchor_are_not_nested_or_renamed(self):
    raw = '<p><span id="cmixed-segment1"><a id="target"></a>Existing sentence.</span> New tail.</p>'
    once = mark_sentences(raw, chapter_id="mixed")
    twice = mark_sentences(once, chapter_id="mixed")
    self.assertEqual(once, twice)
    soup = self.assert_complete(raw)
    self.assertEqual(soup.find(id="cmixed-segment1").get_text(), "Existing sentence.")
    self.assertIsNotNone(soup.find(id="cmixed-segment2"))

  def test_table_cells_definition_lists_and_blockquote_tails(self):
    self.assert_complete('<table><tr><td>Cell prefix.<p>Cell paragraph.</p>Cell suffix.</td></tr></table>'
                         '<dl><dt>Term.</dt><dd>Definition.<div>Nested definition.</div>Tail.</dd></dl>'
                         '<blockquote>Quote prefix.<p>Quote paragraph.</p>Quote suffix.</blockquote>')
