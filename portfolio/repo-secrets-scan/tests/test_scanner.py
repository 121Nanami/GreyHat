#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from secretscan.entropy import shannon_entropy  # noqa: E402
from secretscan.scanner import scan_tree  # noqa: E402


class ScannerTests(unittest.TestCase):
    def test_finds_fixture_secrets(self) -> None:
        report = scan_tree(ROOT / "testdata" / "fixture_repo")
        ids = {h.rule_id for h in report.hits}
        self.assertIn("aws-access-key", ids)
        self.assertIn("github-pat", ids)
        self.assertIn("stripe-key", ids)
        self.assertIn("jwt", ids)
        self.assertGreaterEqual(report.files_scanned, 3)

    def test_skips_placeholder_in_clean(self) -> None:
        report = scan_tree(ROOT / "testdata" / "fixture_repo")
        clean_hits = [h for h in report.hits if h.path.endswith("clean.txt")]
        self.assertEqual(clean_hits, [])

    def test_entropy(self) -> None:
        self.assertGreater(shannon_entropy("aB3/+=xY9QmPlZ0sTuVw"), 3.5)
        self.assertLess(shannon_entropy("aaaaaaaaaaaaaaaaaaaa"), 1.0)


if __name__ == "__main__":
    unittest.main()
