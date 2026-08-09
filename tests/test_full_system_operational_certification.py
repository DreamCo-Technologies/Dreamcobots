import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "config" / "full-system-operational-certification.json"
BENCH = ROOT / "config" / "system-speed-accuracy-benchmarks.json"
EVIDENCE = ROOT / "config" / "runtime-connection-evidence.json"


class FullSystemOperationalCertificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.program = json.loads(PROGRAM.read_text(encoding="utf-8"))
        cls.bench = json.loads(BENCH.read_text(encoding="utf-8"))
        cls.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_certification_covers_build_run_connections_speed_and_accuracy(self):
        dims = set(self.program["certification_dimensions"])
        for required in {
            "repository_structure", "types_and_syntax", "dependencies", "security", "governed_tests",
            "fleet_catalog", "fleet_e2e", "sandbox_coverage", "resource_connections", "model_routing",
            "data_storage", "public_site", "production_build", "deployment_smoke", "rollback_recovery",
            "observability", "speed", "accuracy"
        }:
            self.assertIn(required, dims)
        self.assertGreaterEqual(len(dims), 30)

    def test_connection_claims_require_runtime_probe(self):
        self.assertIn("successful runtime probe", self.program["connection_rule"].lower())
        self.assertIn("runtime_verified", self.program["connection_truth_states"])
        self.assertIn("do not add runtime_verified", self.evidence["truth_rule"].lower())

    def test_accuracy_is_strict_for_deterministic_tests(self):
        self.assertIn("100% pass rate", self.program["accuracy_rule"])
        for row in self.bench["accuracy_benchmarks"]:
            self.assertEqual(row["minimum"], 1.0)

    def test_speed_has_explicit_hard_budgets(self):
        self.assertGreaterEqual(len(self.bench["speed_benchmarks"]), 8)
        for row in self.bench["speed_benchmarks"]:
            self.assertGreater(row["hard_budget_seconds"], 0)
        self.assertTrue(self.bench["regression_policy"]["fail_only_on_hard_budget"])

    def test_full_claim_is_environment_specific(self):
        truth = self.program["truth_rule"].lower()
        self.assertIn("commit- and environment-specific", truth)
        self.assertIn("must never claim", truth)
        self.assertIn("runtime evidence", truth)

    def test_external_api_accuracy_is_not_faked_by_local_tests(self):
        self.assertIn("external apis", self.bench["truth_rule"].lower())
        self.assertIn("their own runtime latency", self.bench["truth_rule"].lower())


if __name__ == "__main__":
    unittest.main()
