import tempfile
import unittest
from pathlib import Path

from tools.readalong.full_inventory_scanner import build_full_inventory


class TestFullInventoryScanner(unittest.TestCase):

  def test_case_a_multivolume_subdirectories(self):
    """Case A: Root has no EPUB, but subdirectories have their own EPUBs."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = Path(tmpdir) / "历史"
      collection = root / "文明的故事"
      vol1 = collection / "Vol 1"
      vol2 = collection / "Vol 2"
      vol1.mkdir(parents=True)
      vol2.mkdir(parents=True)

      (vol1 / "book1.epub").write_bytes(b"dummy epub")
      (vol1 / "01.mp3").write_bytes(b"audio")
      (vol2 / "book2.epub").write_bytes(b"dummy epub")
      (vol2 / "01.mp3").write_bytes(b"audio")

      run_dir = Path(tmpdir) / "run"
      run_dir.mkdir()

      inv = build_full_inventory([root], run_dir)
      units = inv["units"]

      self.assertEqual(len(units), 2)
      unit_ids = [u["unit_id"] for u in units]
      self.assertIn("历史/文明的故事/Vol 1", unit_ids)
      self.assertIn("历史/文明的故事/Vol 2", unit_ids)
      for u in units:
        self.assertTrue(u["is_subvolume"])
        self.assertEqual(u["parent_work"], "文明的故事")
        self.assertEqual(len(u["epubs"]), 1)
        self.assertEqual(len(u["audio_tracks"]), 1)

  def test_case_b_multidisc_relative_natural_sorting(self):
    """Case B: Single EPUB with multiple Disc audio subdirectories must sort naturally by relative path."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = Path(tmpdir) / "哲学"
      book = root / "Utopia"
      disc1 = book / "Disc 01"
      disc2 = book / "Disc 02"
      disc1.mkdir(parents=True)
      disc2.mkdir(parents=True)

      (book / "utopia.epub").write_bytes(b"dummy epub")
      (disc1 / "01 Disc 01.mp3").write_bytes(b"audio")
      (disc1 / "02 Disc 01.mp3").write_bytes(b"audio")
      (disc2 / "01 Disc 02.mp3").write_bytes(b"audio")
      (disc2 / "02 Disc 02.mp3").write_bytes(b"audio")

      run_dir = Path(tmpdir) / "run"
      run_dir.mkdir()

      inv = build_full_inventory([root], run_dir)
      units = inv["units"]

      self.assertEqual(len(units), 1)
      unit = units[0]
      self.assertEqual(unit["unit_id"], "哲学/Utopia")
      self.assertFalse(unit["is_subvolume"])
      self.assertEqual(len(unit["audio_tracks"]), 4)

      # Tracks MUST be sorted by relative path: Disc 01/01 -> Disc 01/02 -> Disc 02/01 -> Disc 02/02
      track_rels = [t["rel_to_book"] for t in unit["audio_tracks"]]
      expected = [
        "Disc 01/01 Disc 01.mp3",
        "Disc 01/02 Disc 01.mp3",
        "Disc 02/01 Disc 02.mp3",
        "Disc 02/02 Disc 02.mp3"
      ]
      self.assertEqual(track_rels, expected)


if __name__ == "__main__":
  unittest.main()
