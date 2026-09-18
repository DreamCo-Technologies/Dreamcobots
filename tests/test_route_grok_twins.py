#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.build_grok_bot_twins import main as build_twins  # noqa: E402
from tools.route_grok_twins import main as route_main  # noqa: E402


class RouteGrokTwinsTest(unittest.TestCase):
    def test_route_after_twins_exist(self):
        self.assertEqual(build_twins(), 0)
        self.assertEqual(route_main(), 0)
        self.assertTrue((ROOT / "config" / "generated" / "grok-twin-route.json").exists())


if __name__ == "__main__":
    unittest.main()
