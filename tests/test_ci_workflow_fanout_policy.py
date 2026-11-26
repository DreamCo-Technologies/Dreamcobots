"""Guardrails against launching every expensive workflow on every repository change."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def workflow(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def trigger_block(name: str) -> str:
    return workflow(name).split("jobs:", 1)[0]


class CIWorkflowFanoutPolicyTests(unittest.TestCase):
    def test_expensive_inventory_and_maintenance_jobs_are_opt_in_or_scheduled(self):
        for name in (
            "benchmark-tracker.yml",
            "parallel-benchmark-gap-builders.yml",
            "buddy-actions-test-lab.yml",
            "keep-green.yml",
            "buddy-preventive-engineering.yml",
            "repository-system-watch.yml",
        ):
            block = trigger_block(name)
            self.assertNotIn("\n  push:", block, name)
            self.assertNotIn("\n  pull_request:", block, name)

    def test_run_everything_is_not_a_default_push_fanout(self):
        block = trigger_block("run-everything-now.yml")
        self.assertNotIn("\n  push:", block)
        self.assertIn('default: "standard"', block)
        self.assertIn('cron: "11 5 * * *"', block)

    def test_superbot_inventory_uses_domain_specific_paths(self):
        block = trigger_block("superbot-inventory.yml")
        self.assertNotIn("- '**'", block)
        self.assertIn("App_bots/**", block)
        self.assertIn("config/masterbot-65-registry.json", block)

    def test_500_model_workflow_is_bounded_and_benchmark_scoped(self):
        text = workflow("dreamco-unified-system.yml")
        block = trigger_block("dreamco-unified-system.yml")
        self.assertIn("cancel-in-progress: true", text)
        self.assertIn("timeout-minutes: 60", text)
        for broad in ("'config/**'", "'tools/**'", "'tests/**'", "'docs/**'"):
            self.assertNotIn(broad, block)
        self.assertIn("tools/run_500_model_benchmarks.py", block)

    def test_full_system_certification_is_limited_to_core_and_governance_changes(self):
        block = trigger_block("full-system-certification.yml")
        for broad in ('"tools/**"', '"tests/**"', '"config/**"', '"docs/**"', '"website/**"'):
            self.assertNotIn(broad, block)
        self.assertIn("config/full-system-operational-certification.json", block)
        self.assertIn("tools/build_full_system_certification.py", block)

    def test_site_deployment_does_not_run_for_arbitrary_test_or_tool_changes(self):
        block = trigger_block("deploy-buddy-pages.yml")
        for broad in ('"tests/**"', '"tools/**"', '"config/**"'):
            self.assertNotIn(broad, block)
        self.assertIn('"website/**"', block)
        self.assertIn('"command-center/**"', block)

    def test_production_readiness_runs_on_governance_changes_not_every_push(self):
        block = trigger_block("production-readiness.yml")
        self.assertIn("paths:", block)
        self.assertIn('"governance/**"', block)
        self.assertIn('"config/production-readiness-contract.json"', block)

    def test_production_master_list_schedule_is_not_every_fifteen_minutes(self):
        block = trigger_block("dreamco-production-readiness.yml")
        self.assertNotIn('cron: "*/15 * * * *"', block)
        self.assertIn('cron: "17 */6 * * *"', block)


if __name__ == "__main__":
    unittest.main()
