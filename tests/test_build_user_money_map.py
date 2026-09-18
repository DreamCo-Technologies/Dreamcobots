#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.build_user_money_map import main as build_map  # noqa: E402
from tools.run_24h_sandbox_soak import main as soak  # noqa: E402


class UserMoneyMapTest(unittest.TestCase):
    def test_map_and_soak_do_not_charge(self):
        self.assertEqual(build_map(), 0)
        payload = json.loads((ROOT / "config" / "generated" / "user-money-map.json").read_text())
        self.assertGreaterEqual(payload["bot_count"], 20)
        self.assertEqual(payload["stripe"], "sandbox_only")
        self.assertTrue(all(row["autonomous_live_money"] is False for row in payload["bots"]))
        self.assertEqual(soak(), 0)
        tick = json.loads((ROOT / "config" / "generated" / "sandbox-24h-tick.json").read_text())
        self.assertEqual(tick["charges_attempted"], 0)


if __name__ == "__main__":
    unittest.main()
