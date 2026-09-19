#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.build_hf_capability_packs import main  # noqa: E402


class HfPacksTest(unittest.TestCase):
    def test_materializes_six_packs_train_off(self):
        self.assertEqual(main(), 0)
        index = json.loads((ROOT / "study_packs" / "index.json").read_text())
        self.assertEqual(index["count"], 6)
        self.assertFalse(index["train_in_default_ci"])
        card = (ROOT / "study_packs" / "pack.code" / "CARD.md").read_text()
        self.assertIn("automatic weight download: no", card)


if __name__ == "__main__":
    unittest.main()
