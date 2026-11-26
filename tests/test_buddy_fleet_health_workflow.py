import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "buddy-fleet-health.yml"


class BuddyFleetHealthWorkflowTests(unittest.TestCase):
    def test_generated_e2e_evidence_is_refreshed_before_strict_check(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        refresh = workflow.index("node --import tsx tools/run_bot_fleet_e2e.ts\\n")
        strict_check = workflow.index("run: npm run buddy:fleet:e2e", refresh)
        self.assertLess(refresh, strict_check)
        self.assertIn("Validate fleet health workflow contract", workflow)

    def test_fleet_health_still_runs_real_runtime_and_contract_tests(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("npm run buddy:fleet", workflow)
        self.assertIn("npm run buddy:fleet-quality", workflow)
        self.assertIn("tests/bot-fleet-catalog.test.ts", workflow)
        self.assertIn("tests/fleet-runtime.test.ts", workflow)
        self.assertIn("tests/fleet-quality-program.test.ts", workflow)


if __name__ == "__main__":
    unittest.main()
