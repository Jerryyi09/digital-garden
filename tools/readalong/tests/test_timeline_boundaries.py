"""Timing repair must never invent an interval to pass overlap validation."""
import unittest
from tools.readalong.timeline_boundaries import resolve_boundaries


def segment(a, b):
  return {"audioSourceId": "a", "start": a, "end": b, "fragment": str(a)}


class BoundaryTests(unittest.TestCase):
  def test_small_overlap_preserves_evidence_and_never_extends(self):
    source = [segment(0, 1), segment(.98, 2)]
    result, repairs = resolve_boundaries(source)
    self.assertEqual(result[0]["end"], .99)
    self.assertEqual(result[1]["start"], .99)
    self.assertEqual(result[0]["observedInterval"], {"start": 0, "end": 1})
    self.assertEqual(source[0]["end"], 1)
    self.assertEqual(len(repairs), 1)

  def test_never_manufactures_duration_for_swallowed_segment(self):
    for second in (segment(.5, .6), segment(.98, .99), segment(.5, 2)):
      with self.assertRaises(ValueError):
        resolve_boundaries([segment(0, 1), second])

  def test_track_boundaries_and_valid_intervals_unchanged(self):
    source = [segment(0, 1), segment(1, 2), {**segment(0, 1), "audioSourceId": "b"}]
    result, repairs = resolve_boundaries(source)
    self.assertEqual(result, source)
    self.assertFalse(repairs)

  def test_invalid_observed_intervals_are_rejected(self):
    for a, b in ((1, 1), (2, 1), (-1, 1), (0, float("nan")), (True, 2)):
      with self.assertRaises(ValueError):
        resolve_boundaries([segment(a, b)])
