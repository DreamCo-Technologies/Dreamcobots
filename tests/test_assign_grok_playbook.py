#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.assign_grok_playbook import main  # noqa: E402


class AssignPlaybookTest(unittest.TestCase):
    def test_assigns_fleet(self):
        self.assertEqual(main(), 0)
        payload = json.loads((ROOT / "config" / "generated" / "grok-playbook-by-bot.json").read_text())
        self.assertGreaterEqual(payload["bot_count"], 20)
        self.assertGreaterEqual(payload["learn_actions"], 40)
        self.assertFalse(payload["assignments"][0]["live_money"])


if __name__ == "__main__":
    unittest.main()
