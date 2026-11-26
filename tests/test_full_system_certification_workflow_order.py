import unittest
from pathlib import Path


class FullSystemCertificationWorkflowOrderTests(unittest.TestCase):
    def test_evidence_producers_run_before_production_verification(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/full-system-certification.yml").read_text(encoding="utf-8")
        steps = [
            "Re-verify fleet E2E and inherit canonical sandbox evidence",
            "Run speed and accuracy benchmarks",
            "Smoke-test built production runtime",
            "Run full production verification",
        ]
        positions = [workflow.index(f"- name: {step}") for step in steps]
        self.assertEqual(positions, sorted(positions))

    def test_fleet_e2e_generation_precedes_fleet_report_verification(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/full-system-certification.yml").read_text(encoding="utf-8")
        self.assertLess(
            workflow.index("npm run buddy:fleet:e2e"),
            workflow.index("Run full production verification"),
        )


    def test_fleet_e2e_generator_precedes_read_only_fleet_check(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/full-system-certification.yml").read_text(encoding="utf-8")
        generator_step = workflow.index("- name: Regenerate canonical fleet end-to-end evidence")
        fleet_check_step = workflow.index("- name: Re-verify fleet E2E and inherit canonical sandbox evidence")
        production_step = workflow.index("- name: Run full production verification")
        generator_block = workflow[generator_step:fleet_check_step]
        fleet_check_command = workflow.index("npm run buddy:fleet:e2e", fleet_check_step)
        self.assertIn("run: node --import tsx tools/run_bot_fleet_e2e.ts", generator_block)
        self.assertLess(generator_step, fleet_check_step)
        self.assertLess(fleet_check_command, production_step)

    def test_pr_receipt_is_report_only_while_main_certification_stays_strict(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/full-system-certification.yml").read_text(encoding="utf-8")
        step = workflow.index("- name: Build full certification receipt")
        summary = workflow.index("- name: Build live-user readiness", step)
        block = workflow[step:summary]
        self.assertIn("if: always()", block)
        self.assertIn("continue-on-error: ${{ github.event_name == 'pull_request' }}", block)

    def test_fleet_catalog_is_refreshed_after_legacy_recovery(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/full-system-certification.yml").read_text(encoding="utf-8")
        recovery = workflow.index("- name: Recover and unify legacy bot system")
        refresh = workflow.index("- name: Refresh fleet catalog after legacy bot recovery")
        fleet_e2e = workflow.index("- name: Regenerate canonical fleet end-to-end evidence")
        production = workflow.index("- name: Run full production verification")
        block = workflow[refresh:fleet_e2e]
        self.assertIn("node --import tsx tools/generate_bot_fleet_catalog.ts", block)
        self.assertLess(recovery, refresh)
        self.assertLess(refresh, fleet_e2e)
        self.assertLess(fleet_e2e, production)


    def test_change_impact_policy_changes_trigger_full_certification(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/full-system-certification.yml").read_text(encoding="utf-8")
        pull_request_paths = workflow.split("  pull_request:", 1)[1].split("  workflow_dispatch:", 1)[0]
        push_paths = workflow.split("  push:", 1)[1].split("\\npermissions:", 1)[0]
        required = (
            "config/change-impact-test-policy.json",
            "tests/test_change_impact_test_policy.py",
        )
        for path in required:
            self.assertIn(f'"{path}"', pull_request_paths)
            self.assertIn(f'"{path}"', push_paths)

if __name__ == "__main__":
    unittest.main()
