#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.buddy_scan_hubs import main  # noqa: E402


class BuddyScanHubsTest(unittest.TestCase):
    def test_writes_packages_for_topics(self):
        self.assertEqual(main(), 0)
        index = json.loads((ROOT / "study_packs" / "bot_learning_packages" / "index.json").read_text())
        self.assertGreaterEqual(index["package_count"], 12)
        self.assertFalse(index["automatic_download"])
        self.assertFalse(index["covers_entire_internet"])


if __name__ == "__main__":
    unittest.main()
