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

if __name__ == "__main__":
    unittest.main()
