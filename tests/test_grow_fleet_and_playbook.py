#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
import tempfile
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import grow_fleet_and_playbook as builder  # noqa: E402


class FleetGrowthTest(unittest.TestCase):
    def test_grows_ten_divisions_and_playbook(self):
        policy = json.loads((ROOT / "config" / "fleet-growth-policy.json").read_text())
        self.assertTrue(policy["canonical_count_is_a_snapshot_not_a_cap"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            app = root / "App_bots"
            app.mkdir()
            source = ROOT / "App_bots" / "DreamFoundry.json"
            existing = json.loads(source.read_text())
            (app / source.name).write_text(json.dumps(existing))
            with patch.multiple(builder, APP=app, OUT=root / "growth.json", REPORT=root / "growth.md"):
                self.assertEqual(builder.main(), 0)
                result = json.loads((app / source.name).read_text())
                self.assertEqual(result["bots"], existing["bots"])
                before = (app / source.name).read_bytes()
                self.assertEqual(builder.main(), 0)
                self.assertEqual((app / source.name).read_bytes(), before)
                self.assertTrue((app / "DreamTravel.json").exists())
        play = json.loads((ROOT / "config" / "grok-help-playbook.json").read_text())
        self.assertGreaterEqual(len(play["learn"]), 25)
        self.assertGreaterEqual(len(play["earn"]), 25)


if __name__ == "__main__":
    unittest.main()
