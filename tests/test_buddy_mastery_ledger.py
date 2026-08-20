import json
import unittest
from pathlib import Path

class MasteryLedgerTests(unittest.TestCase):
    def test_mastery_actions_cover_core_controls(self):
        data = json.loads(Path("website/data/buddy-mastery-ledger-actions.json").read_text())
        ids = {item["id"] for item in data["actions"]}
        expected = {
            "capability-passport",
            "independent-evaluation",
            "transfer-test",
            "mastery-gate",
            "regression-protection",
            "remediation-center",
        }
        self.assertTrue(expected.issubset(ids))

if __name__ == "__main__":
    unittest.main()
