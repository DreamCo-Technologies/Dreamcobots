import json
import unittest
from pathlib import Path

from tools.build_full_system_certification import (
    runtime_connection_evidence_valid,
    work_platform_benchmarks_ready,
)

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "config" / "full-system-operational-certification.json"
BENCH = ROOT / "config" / "system-speed-accuracy-benchmarks.json"
EVIDENCE = ROOT / "config" / "runtime-connection-evidence.json"
WORKFLOW = ROOT / ".github" / "workflows" / "full-system-certification.yml"


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

    def test_full_certification_refreshes_fleet_catalog_before_verification_and_uploads_logs(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        refresh = workflow.index("node --import tsx tools/generate_bot_fleet_catalog.ts")
        repository_registry = workflow.index("python3 tools/generate_repository_test_registry.py")
        fleet_report = workflow.index("node --import tsx tools/run_bot_fleet_e2e.ts --write-only")
        verification = workflow.index("npx tsx tools/run_universal_verification.ts --production")
        self.assertLess(refresh, repository_registry)
        self.assertLess(repository_registry, fleet_report)
        self.assertLess(fleet_report, verification)
        self.assertIn("tmp/dreamco-verification/logs/**", workflow)
        fleet_script = (ROOT / "tools" / "run_bot_fleet_e2e.ts").read_text(encoding="utf-8")
        self.assertIn('process.argv.includes("--write-only")', fleet_script)
        self.assertIn("!writeOnly &&", fleet_script)

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


    def test_runtime_connection_evidence_requires_consistent_counts_and_provenance(self):
        valid = {
            "connection_count": 1,
            "runtime_verified_count": 1,
            "all_declared_runtime_connections_verified": True,
            "connections": [{
                "connection_id": "provider-a",
                "state": "runtime_verified",
                "runtime_verified": True,
                "evidence_reference": "probe-run-123",
                "tested_at": "2026-11-25T12:00:00Z",
            }],
        }
        self.assertTrue(runtime_connection_evidence_valid(valid))
        missing_provenance = json.loads(json.dumps(valid))
        missing_provenance["connections"][0]["evidence_reference"] = None
        self.assertFalse(runtime_connection_evidence_valid(missing_provenance))
        inconsistent_count = json.loads(json.dumps(valid))
        inconsistent_count["runtime_verified_count"] = 0
        self.assertFalse(runtime_connection_evidence_valid(inconsistent_count))

    def test_work_platform_catalog_missing_or_empty_backlog_blocks_certification(self):
        self.assertFalse(work_platform_benchmarks_ready({
            "status": "work_catalog_missing", "task_count": 0,
            "benchmark_case_count": 0, "cases": [],
        }))
        self.assertFalse(work_platform_benchmarks_ready({
            "status": "generated", "task_count": 10,
            "benchmark_case_count": 0, "cases": [],
        }))
        self.assertTrue(work_platform_benchmarks_ready({
            "status": "generated", "task_count": 10,
            "benchmark_case_count": 2, "cases": [{}, {}],
        }))


if __name__ == "__main__":
    unittest.main()
