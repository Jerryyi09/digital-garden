"""Real screening false negatives and adversarial anchor controls."""
import unittest

from tools.readalong_fast.matcher import ParagraphIndex, tokens


# Frozen screenEvidence and corresponding EPUB windows, not corrected ASR text.
SAMPLES = [
  (
    "in gales in groves, gentlemen, brave as lions, gentler's lambs, virtuous as no one ever is, always well dressed, and weeping like tombstone urns. And so for",
    "apron pocket and from which the good old maid herself would devour long chapters in the intervals of her task they were always and only about love lovers paramours persecuted ladies fainting in lonely pavilions postilions killed at every stage horses ridden to death on every page gloomy forests troubled hearts oaths sobs tears and kisses skiffs by moonlight nightingales in groves gentlemen brave as lions gentle as lambs virtuous as no one ever is always well dressed and weeping like tombstone urns and so for six months at the age of fifteen emma soiled her hands with the greasy dust of those old lending libraries with walter scott later she became enamored of things historical dreamed of studded leather chests guardrooms and troubadors she would have liked to live in some old manor like one of those long bodiced chatelaines who under the trefoiled ogives would spend her days elbow on stone sill and chin in hand watching a white plumed horseman come galloping from the depths of the countryside",
  ),
  (
    "Stref endopodia and Stref exopodia, or to be more exact, the various malformations of the foot,",
    "to be able to lean on something more solid than love charles urged by her and by the apothecary allowed himself to be persuaded he sent to rouen for the volume by doctor duval and every evening his head in his hands he immersed himself in reading it while charles was studying pes equinus varus and valgus that is strephocatopodia strephendopodia and strephexopodia or to be more exact the various malformations of the foot downward inward and outward along with strephypopodia and strephanopodia in other words downward torsion and upward straightening monsieur homais by every kind of argument was exhorting the innkeeper s stableboy to submit to the operation you may possibly feel just a slight pain it s a simple prick like a mild bloodletting less than the extirpation of certain types of corns hippolyte as he thought about it was rolling his eyes in bewilderment in any case the pharmacist went on this has nothing to do with",
  ),
  (
    "The thousand a-cues your man would calm down. All the more reason to try something. They couldn't possibly fail to locate 3000 francs. Besides, Leong could sign for it instead of her. Go on!",
    "she revealed the trouble she was in for charles was ignorant of everything her mother in law detested her p re rouault could do nothing but he l on must set about finding this indispensable sum how do you expect me to how spineless you re being she exclaimed then he said stupidly you re exaggerating how bad it is perhaps with a thousand ecus your man would calm down all the more reason to try something they couldn t possibly fail to locate three thousand francs besides l on could sign for it instead of her go on try you must hurry oh try try i will love you so much he went out came back after an hour and said with a solemn face i went to three people no use they sat face to face on either side of the fireplace motionless silent emma was shrugging her shoulders and tapping her feet impatiently then he heard her murmur if i were in your place i would certainly know where to find it well where in your",
  ),
]


class AnchorRegressionTests(unittest.TestCase):
  def make_index(self, text):
    book = tokens(text)
    return ParagraphIndex(book, [{"offset": 0, "length": len(book),
      "document": "chapter.html", "fragment": "p", "text": text}])

  def test_real_bovary_three_screen_samples(self):
    for heard, text in SAMPLES:
      with self.subTest(heard=heard):
        index = self.make_index(text)
        match = index.locate(heard)
        self.assertIsNotNone(match)
        self.assertGreaterEqual(match["score"], .72)
        self.assertLessEqual(match["end"]-match["start"], max(len(tokens(heard))*1.8, len(tokens(heard))+12))
        self.assertLess(index.metrics["comparedBookTokens"], 4000)

  def test_lone_anchor_cannot_match_otherwise_wrong_material(self):
    index = self.make_index("one two three four five six seven eight nine ten")
    self.assertIsNone(index.locate("one two three four five unrelated purple elephants roam distant frozen mountains today"))

  def test_same_phrase_in_two_documents_stays_ambiguous(self):
    phrase = tokens(SAMPLES[0][0])
    book = phrase+["padding"]*250+phrase
    index = ParagraphIndex(book, [
      {"offset": 0, "length": len(phrase)+250, "document": "a", "fragment": "p"},
      {"offset": len(phrase)+250, "length": len(phrase), "document": "b", "fragment": "p"}])
    self.assertIsNone(index.locate(SAMPLES[0][0]))

  def test_unicode_apostrophes_and_accents_have_consistent_tokens(self):
    self.assertEqual(tokens("Léon couldn’t sign; naïve café."), tokens("Leon couldn't sign; naive cafe."))

  def test_context_does_not_make_two_word_phrase_safe(self):
    self.assertIsNone(self.make_index("who is there in the room").locate("who is", 0))

  def test_vote_bucket_alignment_does_not_change_real_sample_result(self):
    heard, text = SAMPLES[1]
    for shift in range(64):
      with self.subTest(shift=shift):
        index = self.make_index(" ".join(f"pad{i}" for i in range(shift))+" "+text)
        self.assertIsNotNone(index.locate(heard))

  def test_global_anchor_can_jump_backwards_for_anthology_order(self):
    first = tokens("the early story has a unique passage about a wooden ship sailing home")
    later = tokens("the later story describes a bright moon above a silent mountain lake")
    book = first+[f"pad{i}" for i in range(300)]+later
    split = len(first)+300
    index = ParagraphIndex(book, [
      {"offset": 0, "length": split, "document": "first", "fragment": "p"},
      {"offset": split, "length": len(later), "document": "later", "fragment": "p"}])
    self.assertEqual(index.locate(" ".join(first), split)["paragraph"]["document"], "first")


if __name__ == "__main__":
  unittest.main()
