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

    def test_generated_contracts_match_current_canonical_sources(self):
        # A self-consistent generated JSON file can still be stale. Compare
        # every registered suite and source hash to the canonical source tree.
        from tools.benchmark_suite_contracts import build
        stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
        actual = build()
        self.assertEqual(
            stored, actual,
            "Benchmark remediation contracts are stale: regenerate them from "
            "canonical sources; do not treat stale contracts as reviewed evidence.",
        )

    def test_taxonomy_domain_map_is_not_misregistered_as_suites(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from tools.benchmark_suite_contracts import build
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "config").mkdir()
            (root / "config" / "universal-benchmark.json").write_text(
                json.dumps({"domains": {"communication": ["email", "chat"]}}),
                encoding="utf-8",
            )
            (root / "config" / "trust-benchmark-suite.json").write_text(
                json.dumps({"domains": ["privacy"]}), encoding="utf-8",
            )
            result = build(root)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["entries"][0]["suite_id"], "privacy")
        self.assertEqual(result["entries"][0]["review"]["status"],
                         "requires_suite_specific_review")

    def test_malformed_suite_list_still_fails_closed(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from tools.benchmark_suite_contracts import build
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "config").mkdir()
            (root / "config" / "bad-benchmark.json").write_text(
                json.dumps({"suites": {"not_a_suite_list": True}}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "must be a list"):
                build(root)

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

class StrategyInputIntegrityTests(unittest.TestCase):
    """Malformed shared learning inputs must not abort a batch or bypass data rights."""

    def test_invalid_candidate_does_not_abort_valid_sandbox_selection(self):
        from buddy.learning.strategy_policy import select
        good = {"strategy_id": "prompt_optimization", "estimated_cost_usd": 0,
                "pilot_gain_lower_bound": .2, "pilot_receipt_hash": "a" * 64,
                "baseline_revision": "v1", "adapter_verified": True, "compatible": True}
        result = select([None, "bad", good], .1, 0, {}, [], [])
        self.assertEqual(result["selected"], good)
        self.assertEqual(len(result["rejected"]), 2)
        self.assertFalse(result["execution_authorized"])

    def test_malformed_training_records_fail_closed(self):
        from buddy.learning.strategy_policy import validate_data
        valid = {"text": "licensed fixture", "training_allowed": True,
                 "rights_verified": True, "license": "MIT", "provenance": "test"}
        for records in ([None], [{**valid, "text": None}], [{**valid, "text": 42}],
                        [{**valid, "text": "   "}], [{**valid, "license": 42}]):
            with self.subTest(records=records):
                with self.assertRaises(ValueError):
                    validate_data(records, ["heldout"])
        with self.assertRaises(ValueError):
            validate_data([valid], "not-a-heldout-hash-collection")

    def test_bad_weight_training_data_blocks_candidate_without_crash(self):
        from buddy.learning.strategy_policy import select
        model = {"training_allowed": True, "rights_verified": True,
                 "weights_available": True, "ownership": "licensed_open", "license": "MIT"}
        candidate = {"strategy_id": "lora_adapter", "estimated_cost_usd": 0,
                     "pilot_gain_lower_bound": .2, "pilot_receipt_hash": "a" * 64,
                     "baseline_revision": "v1", "adapter_verified": True, "compatible": True}
        result = select([candidate], .1, 0, model, [None], ["heldout"])
        self.assertIsNone(result["selected"])
        self.assertEqual(len(result["rejected"]), 1)
        self.assertFalse(result["production_ready"])


if __name__ == "__main__":
    unittest.main()
