import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.readalong.readalong_cli import main as cli_main
from tools.readalong.authoritative_validator import (
    ERROR_SCHEMA_INVALID,
    ERROR_TRACK_INVENTORY_MISMATCH,
    ERROR_TIMESTAMP_OVERLAP
)


class TestReadalongCLI(unittest.TestCase):
    def setUp(self):
        from tools.readalong.tests.build_audit_fixtures import make_clean_book, reference_for
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="test_cli_"))
        self.book_dir = make_clean_book(self.tmp_dir / "sample_book")
        (self.book_dir / "text.epub").write_bytes(b"inventory-only")
        self.reference = reference_for(self.book_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_cli_inspect(self):
        sys.argv = ["readalong_cli.py", "inspect", str(self.book_dir)]
        try:
            cli_main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)

    def test_cli_audit_pass(self):
        sys.argv = ["readalong_cli.py", "audit", str(self.book_dir), "--json", "--reference", str(self.reference)]
        try:
            cli_main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)

    def test_cli_audit_fail_on_tampered(self):
        # Break timeline with overlap
        broken_timeline = {
            "schema_version": "2.0.0",
            "book_id": "sample_book",
            "tracks": {
                "01": [
                    {"start": 1.0, "end": 4.0, "fragment": "chapter1.xhtml#p1", "text": "A"},
                    {"start": 3.0, "end": 6.0, "fragment": "chapter1.xhtml#p1", "text": "B"}
                ]
            }
        }
        (self.book_dir / "readalong" / "timeline.json").write_text(json.dumps(broken_timeline))
        sys.argv = ["readalong_cli.py", "audit", str(self.book_dir), "--json"]
        with self.assertRaises(SystemExit) as cm:
            cli_main()
        self.assertEqual(cm.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
