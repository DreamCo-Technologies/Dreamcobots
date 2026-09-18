#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.place_original_bots import infer_owner, main, parse_category  # noqa: E402


class PlaceOriginalBotsTest(unittest.TestCase):
    def test_keyword_routing(self):
        self.assertEqual(infer_owner("Penny Stock Trading Bot", "DreamAgents"), "DreamFinance")
        self.assertEqual(infer_owner("Contracts Legal Bot", "DreamAgents"), "DreamLegal")
        self.assertEqual(infer_owner("YouTube Streaming Bot", "DreamAgents"), "DreamContent")

    def test_category_one_has_twenty_five_bots(self):
        path = ROOT / "original-bots" / "autonomous-income-network" / "category-1-digital-saas.md"
        rows = parse_category(path)
        self.assertEqual(len(rows), 25)
        self.assertEqual(rows[0]["display_name"], "SaaS Builder Bot")

    def test_placer_writes_ledger(self):
        rc = main()
        self.assertEqual(rc, 0)
        payload = json.loads((ROOT / "config" / "generated" / "original-bot-placement.json").read_text())
        self.assertGreaterEqual(payload["placed_count"], 200)
        self.assertEqual(payload["canonical_baseline_preserved"], 1051)


if __name__ == "__main__":
    unittest.main()
