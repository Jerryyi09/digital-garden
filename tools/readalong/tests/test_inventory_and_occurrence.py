#!/usr/bin/env python3
"""
Test suite for RA-04 (Input Inventory & Safe EPUB) and RA-05 (Reversible Token Model).
"""

import unittest
from pathlib import Path

from tools.readalong.input_inventory import natural_sort_key, build_book_inventory, generate_cache_key
from tools.readalong.occurrence_model import tokenize_reversible, build_fragment_occurrence_entry
from tools.readalong.tests.build_audit_fixtures import FIXTURES_DIR


class TestInventoryAndOccurrence(unittest.TestCase):

    def test_natural_sort_tracks(self):
        """Must order track 1, track 2, track 10 correctly."""
        raw = ["track 10.mp3", "track 1.mp3", "track 2.mp3"]
        ordered = sorted(raw, key=natural_sort_key)
        self.assertEqual(ordered, ["track 1.mp3", "track 2.mp3", "track 10.mp3"])

    def test_reversible_tokenization(self):
        """Raw characters in text must match token slice exactly."""
        raw = "Hello, world! It’s a bright-morning."
        tokens = tokenize_reversible(raw)
        self.assertTrue(len(tokens) >= 5)
        for t in tokens:
            self.assertEqual(raw[t.char_start:t.char_end], t.raw_token)

    def test_strong_cache_key_generation(self):
        """Different audio sha or parameters must produce different cache keys."""
        k1 = generate_cache_key("audio_sha_A", "model_tiny", {"dur": 1800})
        k2 = generate_cache_key("audio_sha_A", "model_tiny", {"dur": 3600})
        k3 = generate_cache_key("audio_sha_B", "model_tiny", {"dur": 1800})
        self.assertNotEqual(k1, k2)
        self.assertNotEqual(k1, k3)


if __name__ == "__main__":
    unittest.main()
