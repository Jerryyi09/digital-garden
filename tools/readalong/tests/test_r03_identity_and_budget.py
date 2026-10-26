"""Tests for R03-05: Run identity, predecessor evidence chain and budget inheritance."""

import json
from pathlib import Path
import tempfile
import unittest

from tools.readalong.batch_candidate_remapper import (
    BatchRemapper,
    code_identity,
)
from tools.readalong.validator import compute_sha256


class TestR03IdentityAndBudget(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.code_sha = code_identity()

    def tearDown(self):
        self.tmp.cleanup()

    def _create_mock_run(self, name: str, units: list, predecessor_dir: Path | None = None, records: dict | None = None):
        run_dir = self.root / name
        run_dir.mkdir(parents=True, exist_ok=True)

        inv_data = {"schema_version": 1, "units": units}
        inv_path = run_dir / "inventory.json"
        inv_path.write_text(json.dumps(inv_data))
        inv_sha = compute_sha256(inv_path)

        identity = {"inventorySha256": inv_sha, "codeSha256": self.code_sha}

        # Inspection fixtures do not fabricate a gate. Live execution is tested
        # separately using decodable audio and real authoritative audits.

        if records is not None:
            results_path = run_dir / "results.json"
            results_path.write_text(json.dumps({
                "schema_version": 3,
                "identity": identity,
                "records": records,
            }))

        run_meta = {
            "run_id": name,
            "code_sha256": self.code_sha,
            "inventory_sha256": inv_sha,
            "predecessor": str(predecessor_dir) if predecessor_dir else None,
            "predecessor_results_sha256": compute_sha256(predecessor_dir / "results.json")
              if predecessor_dir and (predecessor_dir / "results.json").is_file() else None,
        }
        (run_dir / "run.json").write_text(json.dumps(run_meta))
        return run_dir

    def test_predecessor_budget_inherited_and_exhausted_units_blocked(self):
        """Cross-directory run must genuinely inherit prior attempts.

        When prior attempts == 2 (exhausted), the new run MUST NOT reset attempts to 0.
        """
        unit_a = {
            "unit_id": "cat/book_exhausted",
            "book_dir": str(self.root / "book_exhausted"),
            "audio_tracks": [{"rel_to_book": "01.mp3", "sha256": "abc", "measured_duration": 10.0}],
            "epubs": [{"rel_to_book": "book.epub", "sha256": "def", "valid_zip": True}],
            "detected_languages": ["en"],
        }
        # Predecessor run had exhausted budget (attempts=2)
        pred_records = {
            "cat/book_exhausted": {
                "unitId": "cat/book_exhausted",
                "attempts": 2,
                "activeStatusBefore": "FAILED",
                "candidateStatusAfter": "FAILED",
                "blockingReason": "Prior attempt failed",
                "workflow_completed": True,
            }
        }
        pred_dir = self._create_mock_run("run_predecessor", [unit_a], records=pred_records)

        # New run inherits from predecessor
        new_dir = self._create_mock_run("run_new", [unit_a], predecessor_dir=pred_dir)

        remapper = BatchRemapper(new_dir)
        # Record for book_exhausted must have inherited attempts == 2
        rec = remapper.ledger["records"].get("cat/book_exhausted")
        self.assertIsNotNone(rec, "Record must exist in new ledger from predecessor")
        self.assertEqual(rec["attempts"], 2, "Attempts must be inherited from predecessor (not reset to 0)")

    def test_run_results_identity_mismatch_refused(self):
        """If run.json code/inventory sha differs from results.json, execution must be refused."""
        unit = {
            "unit_id": "cat/book1",
            "book_dir": str(self.root / "book1"),
            "audio_tracks": [{"rel_to_book": "01.mp3", "sha256": "abc", "measured_duration": 10.0}],
            "epubs": [{"rel_to_book": "book.epub", "sha256": "def", "valid_zip": True}],
            "detected_languages": ["en"],
        }
        run_dir = self._create_mock_run("run_mismatch", [unit])
        # Corrupt run.json code sha
        run_json_path = run_dir / "run.json"
        meta = json.loads(run_json_path.read_text())
        meta["code_sha256"] = "different_corrupt_sha"
        run_json_path.write_text(json.dumps(meta))

        with self.assertRaises(ValueError) as ctx:
            BatchRemapper(run_dir)
        self.assertIn("identity mismatch", str(ctx.exception).lower())

    def test_nonexistent_predecessor_refused(self):
        """Specifying a nonexistent predecessor directory must raise an error, not silently ignore."""
        unit = {
            "unit_id": "cat/book1",
            "book_dir": str(self.root / "book1"),
            "audio_tracks": [{"rel_to_book": "01.mp3", "sha256": "abc", "measured_duration": 10.0}],
            "epubs": [{"rel_to_book": "book.epub", "sha256": "def", "valid_zip": True}],
            "detected_languages": ["en"],
        }
        run_dir = self._create_mock_run("run_bad_pred", [unit], predecessor_dir=self.root / "nonexistent_pred")

        with self.assertRaises(RuntimeError) as ctx:
            BatchRemapper(run_dir)
        self.assertIn("predecessor", str(ctx.exception).lower())

    def test_predecessor_modified_after_initial_load_is_rejected(self):
        unit = {"unit_id": "cat/book", "book_dir": str(self.root / "book")}
        predecessor = self._create_mock_run("old", [unit], records={"cat/book": {"attempts": 1}})
        new = self._create_mock_run("new", [unit], predecessor_dir=predecessor)
        remapper = BatchRemapper(new)
        data = json.loads((predecessor / "results.json").read_text())
        data["records"]["cat/book"]["attempts"] = 0
        (predecessor / "results.json").write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            remapper._load_ledger()


if __name__ == "__main__":
    unittest.main()
