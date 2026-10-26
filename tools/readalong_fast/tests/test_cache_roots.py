import unittest
from pathlib import Path

from tools.readalong.config import DEFAULT_CACHE_ROOT
from tools.readalong_fast.benchmark import resolve_cache_roots


class CacheRootTests(unittest.TestCase):
    def test_new_asr_goes_to_authoritative_root_by_default(self):
        write, reads = resolve_cache_roots(None, [])
        self.assertEqual(write, DEFAULT_CACHE_ROOT)
        self.assertEqual(reads, [DEFAULT_CACHE_ROOT])

    def test_extra_read_roots_never_change_the_write_root(self):
        write, reads = resolve_cache_roots(None, ["/tmp/old-run/cache"])
        self.assertEqual(write, DEFAULT_CACHE_ROOT)
        self.assertIn(Path("/tmp/old-run/cache"), reads)

    def test_explicit_isolated_write_root_still_reads_authoritative_root(self):
        write, reads = resolve_cache_roots("/tmp/experiment/cache", [])
        self.assertEqual(write, Path("/tmp/experiment/cache"))
        self.assertIn(DEFAULT_CACHE_ROOT, reads)


if __name__ == "__main__":
    unittest.main()
