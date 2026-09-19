#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.grow_fleet_and_playbook import main  # noqa: E402


class FleetGrowthTest(unittest.TestCase):
    def test_grows_ten_divisions_and_playbook(self):
        policy = json.loads((ROOT / "config" / "fleet-growth-policy.json").read_text())
        self.assertTrue(policy["canonical_count_is_a_snapshot_not_a_cap"])
        self.assertEqual(main(), 0)
        self.assertTrue((ROOT / "App_bots" / "DreamFoundry.json").exists())
        play = json.loads((ROOT / "config" / "grok-help-playbook.json").read_text())
        self.assertGreaterEqual(len(play["learn"]), 25)
        self.assertGreaterEqual(len(play["earn"]), 25)


if __name__ == "__main__":
    unittest.main()
