"""V3 regression: verdicts must separate a matched pairing from a mismatched one.

The real-book calibration lives in
private/readalong-library-reviews/asr-batch-screening-closeout-20261025/, but it
needs caches that are not in the repo. These tests pin the decision boundary those
books produced, using the same located ratios, so a threshold edit that would
misjudge them fails here instead.
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.readalong_fast.sampling import (MAX_SAMPLE_BLOCKS, MIN_SAMPLE_TOKENS,
  MISMATCH_BLOCK_VETO, MISMATCH_LOCATED_UPPER_CEILING, MIN_MEASURE_SECONDS, SAMPLE_BLOCKS,
  VERDICT_BORDERLINE, VERDICT_MISMATCH, VERDICT_MODERATE, VERDICT_PASS, classify,
  extend_strata, stratified_blocks, verdict_runs_full_book)


def samples(located_ratio, blocks=SAMPLE_BLOCKS, seconds=1800.0, tokens=4000):
  """Sampled blocks whose located ratio matches a real calibration observation."""
  observed = seconds
  missing = seconds*(1-located_ratio)
  return [{"observedSeconds": observed, "missingSeconds": missing, "tokens": tokens}
          for _ in range(blocks)]


class CalibratedVerdictTests(unittest.TestCase):
  def test_matched_pairings_pass(self):
    # Anna+Garnett 0.983 and Pride 1.0 were both SAMPLE_PASS.
    for ratio in (0.983, 1.0, 0.9947):
      self.assertEqual(classify(samples(ratio))[0], VERDICT_PASS, ratio)

  def test_constructed_mismatches_are_rejected(self):
    # Same audio against another book's EPUB: Anna 0.0, Pride 0.0, Flow 0.0.
    for ratio in (0.0, 0.005):
      self.assertEqual(classify(samples(ratio))[0], VERDICT_MISMATCH, ratio)

  def test_real_edition_mismatches_are_rejected(self):
    # The four real same-book-different-edition mismatches, at their measured
    # overall located ratios. These are the cases the old rule missed, because
    # an edition mismatch still matches a few stray fragments (0.05-0.10).
    for ratio in (0.0164, 0.0368, 0.0717, 0.1521):
      self.assertEqual(classify(samples(ratio))[0], VERDICT_MISMATCH, ratio)

  def test_lowest_rated_good_book_is_not_a_mismatch(self):
    # Resurrection at 0.40 is the closest good book to the mismatch band; it must
    # stay out, and its block at 0.55 must not tip it over either.
    verdict, detail = classify(samples(0.40))
    self.assertNotEqual(verdict, VERDICT_MISMATCH)
    self.assertGreater(detail["locatedUpper"], MISMATCH_LOCATED_UPPER_CEILING)

  def test_partial_books_never_reach_a_decisive_verdict(self):
    # O'Hongry 0.6395 and Gone with the Wind 0.7554 were MODERATE/BORDERLINE,
    # and neither may skip the full run.
    for ratio in (0.6395, 0.7554, 0.4011):
      verdict, _ = classify(samples(ratio))
      self.assertNotIn(verdict, (VERDICT_PASS, VERDICT_MISMATCH), ratio)
      self.assertTrue(verdict_runs_full_book(verdict), ratio)

  def test_one_well_located_block_vetoes_a_mismatch(self):
    # An anthology whose other strata are empty still has matching content, so a
    # block above the veto must downgrade it rather than drop the book. The block
    # is short, so the interval alone would still read as a mismatch.
    mixed = samples(0.0, blocks=SAMPLE_BLOCKS-1) + samples(1.0, blocks=1, seconds=120.0)
    verdict, detail = classify(mixed)
    self.assertLess(detail["locatedUpper"], MISMATCH_LOCATED_UPPER_CEILING)
    self.assertGreaterEqual(detail["maxBlockLocatedRatio"], MISMATCH_BLOCK_VETO)
    self.assertNotEqual(verdict, VERDICT_MISMATCH)
    self.assertEqual(detail["reason"], "A_BLOCK_MATCHES")

  def test_short_strata_are_not_sampled(self):
    # Midsummer Night's Dream had 129s and 160s remnants that carried too few
    # tokens to judge; the plan must not spend a stratum on them.
    tracks = [{"audioSourceId": "a.mp3", "duration": 10000.0},
              {"audioSourceId": "b.mp3", "duration": 700.0}]
    blocks = stratified_blocks(tracks)
    self.assertTrue(all(b["measureDuration"] >= MIN_MEASURE_SECONDS for b in blocks))
    self.assertTrue(all(b["start"] % 1800.0 == 0 for b in blocks),
                    "sampled blocks must stay on the full run's grid to be cache hits")

  def test_many_short_tracks_are_sampled_by_whole_track(self):
    # Great Expectations has 179 short tracks; the 1800s grid alone yielded 2
    # strata. Those books must fall back to whole tracks, one per stratum.
    tracks = [{"audioSourceId": f"{i:03d}.mp3", "duration": 300.0} for i in range(179)]
    blocks = stratified_blocks(tracks)
    self.assertEqual(len(blocks), SAMPLE_BLOCKS)
    self.assertEqual(len({b["audioSourceId"] for b in blocks}), SAMPLE_BLOCKS)
    self.assertTrue(all(b["start"] == 0.0 for b in blocks))
    self.assertTrue(all(b["measureDuration"] >= MIN_MEASURE_SECONDS for b in blocks))


class TokenFloorTests(unittest.TestCase):
  """The evidence floor is on the sample total, not on each block.

  Great Expectations' whole-track strata carry 120-205 tokens each, so a per-block
  floor of 200 rejected a book whose six samples were unanimous at located ratio
  0.0. The total is what says whether there is enough evidence to decide."""
  def test_thin_blocks_are_decisive_when_the_total_is_enough(self):
    # 8 blocks x 170 tokens = 1360, over the 1200 floor, each block under 200.
    thin = samples(0.0, blocks=8, tokens=170)
    self.assertEqual(classify(thin)[0], VERDICT_MISMATCH)

  def test_a_thin_total_still_runs_the_book(self):
    verdict, detail = classify(samples(0.0, blocks=6, tokens=100))
    self.assertEqual(verdict, VERDICT_BORDERLINE)
    self.assertEqual(detail["reason"], "INSUFFICIENT_ASR_TOKENS")

  def test_the_floor_is_the_six_block_total(self):
    self.assertEqual(MIN_SAMPLE_TOKENS, SAMPLE_BLOCKS*200)

  def test_extension_appends_unsampled_whole_tracks_only(self):
    tracks = [{"audioSourceId": f"{i:03d}.mp3", "duration": 60.0} for i in range(179)]
    first = stratified_blocks(tracks)
    extra = extend_strata(tracks, first)
    seen = {b["audioSourceId"] for b in first}
    self.assertTrue(extra, "a thin sample must be able to grow")
    self.assertTrue(all(b["audioSourceId"] not in seen for b in extra))
    self.assertTrue(all(b["start"] == 0.0 for b in extra))
    self.assertLessEqual(len(first)+len(extra), MAX_SAMPLE_BLOCKS)


if __name__ == "__main__":
  unittest.main()
