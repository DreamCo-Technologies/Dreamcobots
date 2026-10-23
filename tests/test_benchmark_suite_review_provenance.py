"""Suite registry templates are remediation designs, not review attestations."""
import json
import unittest
from tools.benchmark_suite_contracts import contract, OUTPUT

STAGES = ["measure_and_pin_before_evidence","diagnose_root_cause","propose_smallest_shared_safe_fix_with_rollback","apply_only_in_review_branch_or_sandbox","run_targeted_tests_and_benchmark","compare_before_after_evidence","retest_dependent_suites_and_review_or_remain_blocked"]

class BenchmarkSuiteReviewProvenanceTests(unittest.TestCase):
    def test_template_requires_suite_specific_review(self):
        row = contract({"id": "synthetic"}, "config/synthetic.json")
        self.assertEqual(row["review"]["status"], "requires_suite_specific_review")
        self.assertIsNone(row["review"]["reviewer"])
        self.assertEqual(row["remediation_design"], STAGES)
        self.assertFalse(row["production_ready"])

    def test_all_registered_suites_remain_unverified(self):
        registry = json.loads(OUTPUT.read_text(encoding="utf-8"))
        rows = registry["entries"]
        self.assertEqual(registry["count"], len(rows))
        self.assertGreater(len(rows), 0)
        self.assertEqual(len({row["suite_id"] for row in rows}), len(rows))
        for row in rows:
            with self.subTest(suite=row["suite_id"]):
                self.assertEqual(row["review"]["status"], "requires_suite_specific_review")
                self.assertIsNone(row["review"]["reviewer"])
                self.assertEqual(row["remediation_design"], STAGES)
                self.assertFalse(row["production_ready"])
                self.assertEqual(row["gap_state"], "unknown")
                self.assertTrue(row["definition_sha256"])


class StrategyPromotionGuardTests(unittest.TestCase):
    """Ensure shared learning policy cannot certify a safety regression or false rollback."""

    def _proposal(self):
        baseline = {"revision": "v1", "quality": .5, "safety": 1,
                    "factuality": 1, "retention": 1}
        runs = [
            {"id": str(i), "seed": i, "quality": .7, "safety": 1,
             "factuality": 1, "retention": 1, "cost_usd": 0,
             "latency_ms": 1, "heldout": True, "uncontaminated": True,
             "rights_verified": True, "regression_passed": True,
             "receipt_hash": "a" * 64, "config_hash": "b" * 64,
             "hardware": "fixture"}
            for i in range(3)
        ]
        return baseline, {"baseline_revision": "v1", "runs": runs,
                          "rollback_revision": "v1"}

    def test_safety_regression_rejected_despite_tolerance(self):
        from buddy.learning.strategy_policy import promotion
        baseline, proposal = self._proposal()
        self.assertTrue(promotion(proposal, baseline, max_regression=.02)["eligible_for_review"])
        proposal["runs"][0]["safety"] = .99
        decision = promotion(proposal, baseline, max_regression=.02)
        self.assertFalse(decision["eligible_for_review"])
        self.assertFalse(decision["production_ready"])

    def test_rollback_must_match_actual_baseline(self):
        from buddy.learning.strategy_policy import promotion
        baseline, proposal = self._proposal()
        for revision in ("nonexistent", "v0", "", None):
            with self.subTest(rollback_revision=revision):
                proposal["rollback_revision"] = revision
                decision = promotion(proposal, baseline)
                self.assertFalse(decision["eligible_for_review"])
                self.assertFalse(decision["mastery"])

if __name__ == "__main__":
    unittest.main()
