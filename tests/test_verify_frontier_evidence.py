import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.verify_frontier_evidence import SUITE, assess


class FrontierEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.suite = json.loads(SUITE.read_text())
        self.suite["suite_hash"] = hashlib.sha256(SUITE.read_bytes()).hexdigest()

    def test_empty_bundle_is_explicitly_unproven(self):
        result = assess({"schema": "dreamco.buddy.frontier_run_bundle.v1", "claim_context": "live_comparison", "suite_id": self.suite["suite_id"], "suite_hash": self.suite["suite_hash"], "runs": []}, self.suite)
        self.assertFalse(result["claimable"])
        self.assertFalse(result["independent_learning_proven"])
        self.assertIn("missing Buddy subject", result["errors"])

    def test_simulated_results_can_never_be_claimable(self):
        row = {"subject_id": "buddy", "phase": "baseline", "task_id": "route-rental-search", "fixture_hash": "a", "grader_version": "v1", "timestamp": "2026-09-11T00:00:00Z", "latency_ms": 1, "cost_usd": 0, "safety_passed": True, "regression_passed": True, "external_assistance": False, "score": 0.1, "simulated": True}
        result = assess({"schema": "dreamco.buddy.frontier_run_bundle.v1", "claim_context": "live_comparison", "suite_id": self.suite["suite_id"], "suite_hash": self.suite["suite_hash"], "runs": [row]}, self.suite)
        self.assertFalse(result["claimable"])
        self.assertTrue(any("simulated" in item for item in result["errors"]))

    def test_suite_requires_three_repetitions_and_holdouts(self):
        result = assess({"schema": "dreamco.buddy.frontier_run_bundle.v1", "claim_context": "live_comparison", "suite_id": self.suite["suite_id"], "suite_hash": self.suite["suite_hash"], "runs": []}, self.suite)
        self.assertIn("missing named frontier reference subject", result["errors"])
