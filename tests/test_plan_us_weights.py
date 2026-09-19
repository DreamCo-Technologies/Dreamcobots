#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.plan_us_weights import main  # noqa: E402


class UsWeightsTest(unittest.TestCase):
    def test_plan_is_honest(self):
        self.assertEqual(main(), 0)
        spec = json.loads((ROOT / "config" / "us-weight-system.json").read_text())
        self.assertFalse(spec["trained_weights_exist"])
        plan = json.loads((ROOT / "config" / "generated" / "us-weight-plan.json").read_text())
        self.assertEqual(plan["next_train_target"], "dream-edge")


if __name__ == "__main__":
    unittest.main()
