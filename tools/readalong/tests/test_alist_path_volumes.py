"""Unit test for alist_audio_path with multi-volume subdirectories."""
from pathlib import Path
import unittest

from tools.readalong.candidate_safety import alist_audio_path


class AlistAudioPathTests(unittest.TestCase):
  def test_volume_subdirectory_includes_category(self):
    book_dir = Path("/Users/jerryyi/Desktop/寒假/未命名文件夹/心智成长/Great Mental Models/Volume 1- General Thinking Concepts [2018]")
    audio_file = book_dir / "General Thinking Concepts.m4b"
    res = alist_audio_path(book_dir, audio_file, "/750HD/有声书")
    expected = "/750HD/有声书/心智成长/Great Mental Models/Volume 1- General Thinking Concepts [2018]/General Thinking Concepts.m4b"
    self.assertEqual(res, expected)

  def test_standard_depth2_book(self):
    book_dir = Path("/Users/jerryyi/Desktop/寒假/未命名文件夹/文学作品/包法利夫人")
    audio_file = book_dir / "01 Chapter - 001.mp3"
    res = alist_audio_path(book_dir, audio_file, "/750HD/有声书")
    expected = "/750HD/有声书/文学作品/包法利夫人/01 Chapter - 001.mp3"
    self.assertEqual(res, expected)


if __name__ == "__main__":
  unittest.main()
