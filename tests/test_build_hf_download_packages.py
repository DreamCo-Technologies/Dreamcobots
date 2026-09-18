#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.build_hf_download_packages import main  # noqa: E402


class HfDownloadPackagesTest(unittest.TestCase):
    def test_builds_ten_opt_in_packs(self):
        self.assertEqual(main(), 0)
        index = json.loads((ROOT / "study_packs" / "hf_packages" / "index.json").read_text())
        self.assertEqual(index["count"], 10)
        self.assertFalse(index["covers_entire_huggingface_hub"])
        self.assertFalse(index["automatic_download_in_ci"])
        pack = json.loads((ROOT / "study_packs" / "hf_packages" / "pack.code" / "package.json").read_text())
        self.assertTrue(pack["models"])


if __name__ == "__main__":
    unittest.main()
