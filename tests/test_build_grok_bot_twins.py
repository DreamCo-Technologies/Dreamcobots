#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.build_grok_bot_twins import main  # noqa: E402


class GrokTwinsTest(unittest.TestCase):
    def test_generates_twins_and_honest_hf_plan(self):
        self.assertEqual(main(), 0)
        twins = json.loads((ROOT / "config" / "generated" / "grok-bot-twins.json").read_text())
        self.assertGreaterEqual(twins["twin_count"], 20)
        self.assertEqual(twins["canonical_baseline_preserved"], 1051)
        slugs = [row["grok_slug"] for row in twins["twins"]]
        self.assertEqual(len(slugs), len(set(slugs)))
        study = json.loads((ROOT / "config" / "huggingface-two-week-study.json").read_text())
        self.assertFalse(study["truth"]["frontier_parity_proven"])
        self.assertFalse(study["truth"]["master_everything_on_huggingface"])
        self.assertEqual(study["window_days"], 14)


if __name__ == "__main__":
    unittest.main()
