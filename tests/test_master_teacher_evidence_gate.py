import unittest
from tools.master_teacher_evidence_gate import evaluate


class EvidenceGateTests(unittest.TestCase):
    def test_missing_evidence_blocks(self):
        result = evaluate({})
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["training_launched"])

    def test_exposed_holdout_blocks(self):
        result = evaluate({"holdout_provenance": {"isolated": True, "authorized": True},
                           "contamination_review": {"answer_exposure": True}})
        self.assertEqual(result["status"], "blocked")
        self.assertTrue(any("answer_exposure" in reason for reason in result["reasons"]))

    def test_no_promotion_without_independent_verification(self):
        result = evaluate({"independent_verification": "pending"})
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["promotion_executed"])


if __name__ == "__main__":
    unittest.main()
