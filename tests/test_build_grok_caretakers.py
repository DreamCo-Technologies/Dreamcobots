#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.build_grok_caretakers import main  # noqa: E402


class GrokCaretakersTest(unittest.TestCase):
    def test_proposed_ten_and_caretakers(self):
        spec = json.loads((ROOT / "config" / "proposed-10-divisions.json").read_text())
        self.assertEqual(len(spec["divisions"]), 10)
        self.assertEqual(spec["canonical_baseline_preserved"], 1051)
        self.assertEqual(main(), 0)
        out = json.loads((ROOT / "config" / "generated" / "grok-caretakers.json").read_text())
        self.assertGreaterEqual(out["count"], 10)


if __name__ == "__main__":
    unittest.main()
