import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.readalong.controlled_repair_pipeline import (
    load_repair_state,
    save_repair_state,
    attempt_book_repair_cycle,
    MAX_RETRY_BUDGET
)


class TestControlledRepairPipeline(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="test_pipeline_"))
        self.book_dir = self.tmp_dir / "broken_input_book"
        self.book_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_pipeline_halts_on_corrupted_input(self):
        # Empty directory -> no audio and no epub -> INVALID
        res = attempt_book_repair_cycle(self.book_dir)
        self.assertEqual(res["action"], "HALTED")
        self.assertEqual(res["state"]["status"], "PERMANENT_FAILURE")

        # Second attempt should skip immediately without creating staging
        res2 = attempt_book_repair_cycle(self.book_dir)
        self.assertEqual(res2["action"], "SKIPPED")

    def test_pipeline_retry_budget_exhaustion(self):
        # Initialize state with max attempts
        state = load_repair_state(self.book_dir)
        state["attempts"] = MAX_RETRY_BUDGET
        save_repair_state(self.book_dir, state)

        res = attempt_book_repair_cycle(self.book_dir)
        self.assertEqual(res["action"], "BLOCKED")
        self.assertEqual(res["state"]["status"], "RETRY_BUDGET_EXHAUSTED")


if __name__ == "__main__":
    unittest.main()
