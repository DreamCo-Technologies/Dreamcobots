#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.prove_buddy_learning import main  # noqa: E402


class ProveBuddyLearningTest(unittest.TestCase):
    def test_proof_pack_shows_learning_delta(self):
        self.assertEqual(main(), 0)
        payload = json.loads((ROOT / "config" / "generated" / "buddy-learning-proof.json").read_text())
        self.assertTrue(payload["proven"])
        self.assertGreater(
            payload["cycle"]["after"]["progress"]["native_pass_rate"],
            payload["cycle"]["before"]["progress"]["native_pass_rate"],
        )
        self.assertTrue((ROOT / "reports" / "BUDDY_LEARNING_PROOF.md").exists())
        self.assertTrue((ROOT / "evidence" / "buddy-learning-history.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
