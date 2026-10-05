import unittest

from buddy.builder.model_selection import select
from buddy.builder.promotion_gate import promote


class EvidenceGateTest(unittest.TestCase):
    def test_missing_runs_do_not_promote(self) -> None:
        decision = promote({"quality": 1, "failure_rate": 0}, {"runs": 1, "quality": 2, "failure_rate": 0})
        self.assertFalse(decision["promoted"])

    def test_selection_does_not_claim_weight_changes(self) -> None:
        choice = select("code")
        self.assertFalse(choice["weight_modification"])
        self.assertEqual(choice["model"], "local-note")


if __name__ == "__main__":
    unittest.main()
