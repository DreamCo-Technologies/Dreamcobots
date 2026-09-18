#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.register_grok_team import REQUIRED, main  # noqa: E402


class RegisterGrokTeamTest(unittest.TestCase):
    def test_team_file_has_required_slugs(self):
        team = json.loads((ROOT / "team" / "grok-team.json").read_text())
        slugs = {bot["slug"] for bot in team["bots"]}
        self.assertTrue(REQUIRED.issubset(slugs))
        self.assertEqual(team["canonical_baseline_preserved"], 1051)
        self.assertFalse(team["live_money_outreach"])

    def test_register_writes_registry(self):
        self.assertEqual(main(), 0)
        payload = json.loads((ROOT / "config" / "generated" / "grok-team-registry.json").read_text())
        self.assertEqual(payload["count"], 10)
        self.assertFalse(payload["missing_required"])


if __name__ == "__main__":
    unittest.main()
