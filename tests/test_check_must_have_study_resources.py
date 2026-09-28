#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.check_must_have_study_resources import main, valid_resource  # noqa: E402


class MustHaveStudyTest(unittest.TestCase):
    def test_required_values_and_url_host_are_validated(self):
        row = [1001, "Fixture", "docs", "https://example.test/docs", "Study", "Sandbox"]
        self.assertTrue(valid_resource(row))
        for i in range(1, 6):
            invalid = row.copy()
            invalid[i] = " "
            self.assertFalse(valid_resource(invalid))
        for url in ("https://", "https:///docs", "https://[bad", "ftp://example.test", "https://example.test:bad", "https://example.test:65536"):
            invalid = row.copy()
            invalid[3] = url
            self.assertFalse(valid_resource(invalid))

    def test_one_hundred_unique(self):
        self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main()
