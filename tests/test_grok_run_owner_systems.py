#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.grok_run_owner_systems import feel, main  # noqa: E402


class GrokOwnerSystemsTest(unittest.TestCase):
    def test_missing_is_not_failure(self):
        vibe = feel([{"state": "missing", "ok": True}, {"state": "passed", "ok": True}])
        self.assertEqual(vibe["failed"], 0)
        self.assertEqual(vibe["mood"], "sharp")

    def test_operator_runs(self):
        self.assertIn(main(), (0, 1))
        self.assertTrue((ROOT / "reports" / "BUDDY_FEEL.md").exists())


if __name__ == "__main__":
    unittest.main()
