#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.plan_pass_all_500 import main  # noqa: E402


class PassAll500Test(unittest.TestCase):
    def test_does_not_claim_victory(self):
        self.assertEqual(main(), 0)
        spec = json.loads((ROOT / "config" / "pass-all-500-benchmarks.json").read_text())
        self.assertEqual(spec["target_count"], 500)
        self.assertTrue(spec["missing_evidence_is_not_a_pass"])
        out = json.loads((ROOT / "config" / "generated" / "pass-all-500-plan.json").read_text())
        self.assertFalse(out["claim_all_500_passed"])


if __name__ == "__main__":
    unittest.main()
