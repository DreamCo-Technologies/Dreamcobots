import unittest
from tools.buddy_learning_income_engine import (
    distill_task, execution_decision, opportunity_score, propose_learning_example
)


class LearningIncomeEngineTests(unittest.TestCase):
    def test_deterministic_packet(self):
        a = distill_task("  Research   local leads ", domain="sales")
        b = distill_task("Research local leads", domain="sales")
        self.assertEqual(a.task_id, b.task_id)
        self.assertEqual(a.risk, "low")

    def test_money_requires_approval(self):
        p = distill_task("Send payment to vendor", mode="execute")
        self.assertEqual(p.risk, "high")
        self.assertFalse(execution_decision(p, adapter_verified=True)["allowed"])
        self.assertTrue(execution_decision(p, approved=True, adapter_verified=True)["allowed"])

    def test_adapter_is_mandatory(self):
        p = distill_task("Create a draft", mode="execute")
        self.assertEqual(execution_decision(p, approved=True)["reason"], "unverified_adapter")

    def test_no_learning_without_consent(self):
        p = distill_task("Summarize public docs")
        with self.assertRaises(PermissionError):
            propose_learning_example(p, outcome="success", evidence=("run:1",))

    def test_holdout_not_trainable(self):
        p = distill_task("Summarize public docs", consent_to_learn=True)
        x = propose_learning_example(p, outcome="success", evidence=("run:1",), holdout=True)
        self.assertFalse(x["training_eligible"])

    def test_evidence_required(self):
        p = distill_task("Summarize public docs", consent_to_learn=True)
        with self.assertRaises(ValueError):
            propose_learning_example(p, outcome="success", evidence=())

    def test_opportunity_not_revenue_claim(self):
        x = opportunity_score(demand=.8, margin=.7, repeatability=.9,
                              automation_readiness=.8, risk=.2, evidence_quality=.3)
        self.assertFalse(x["verified_revenue"])
        self.assertTrue(x["needs_market_validation"])

    def test_bad_scores(self):
        with self.assertRaises(ValueError):
            opportunity_score(demand=2, margin=.7, repeatability=.9,
                              automation_readiness=.8, risk=.2, evidence_quality=.3)


if __name__ == "__main__":
    unittest.main()
