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
        fleet_check_command = workflow.index("npm run buddy:fleet:e2e", fleet_check_step)
        self.assertLess(generator_step, fleet_check_step)
        self.assertLess(generator_step, fleet_check_step)
        self.assertLess(fleet_check_command, production_step)

if __name__ == "__main__":
    unittest.main()
