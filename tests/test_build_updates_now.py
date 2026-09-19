#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BuildUpdatesNowTest(unittest.TestCase):
    def test_pipeline_script_exists(self):
        self.assertTrue((ROOT / "tools" / "build_updates_now.py").exists())

    def test_required_builders_exist(self):
        for name in (
            "scan_bot_fleet.py",
            "compile_md_bots.py",
            "build_dream_systems.py",
            "place_original_bots.py",
            "register_grok_team.py",
            "prove_buddy_learning.py",
        ):
            self.assertTrue((ROOT / "tools" / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
