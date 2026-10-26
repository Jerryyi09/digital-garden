"""The fixed screening regression library must stay green.

`sampling_regression` is the gate a threshold edit has to pass before it ships;
this wrapper puts it in the normal test run so a change to `sampling.py` cannot
land without it being executed. It reads only recorded block evidence, so it
costs no ASR.
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.readalong_fast import sampling_regression


class SamplingRegressionTests(unittest.TestCase):
  def test_library_matches_every_recorded_verdict(self):
    self.assertEqual(sampling_regression.main([]), 0,
      "a screening threshold changed a calibrated verdict; see the failure list above")


if __name__ == "__main__":
  unittest.main()
