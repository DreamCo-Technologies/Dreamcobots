from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ProductionReadinessWorkflowTests(unittest.TestCase):
    def test_pull_request_runs_inventory_but_not_strict_production_certification(self):
        workflow = (ROOT / ".github/workflows/production-readiness.yml").read_text(encoding="utf-8")
        self.assertIn("  pull_request:", workflow)
        strict = workflow[workflow.index("      - name: Run production contract strict gate"):workflow.index("      - name: Upload evidence report")]
        self.assertIn("if: github.event_name != 'pull_request'", strict)
        self.assertIn("      - name: Explain report-only pull request result", strict)
        self.assertIn("if: github.event_name == 'pull_request'", strict)
        self.assertIn("read-only production-readiness inventory", strict)

    def test_push_and_scheduled_runs_remain_fail_closed(self):
        workflow = (ROOT / ".github/workflows/production-readiness.yml").read_text(encoding="utf-8")
        strict = workflow[workflow.index("      - name: Run production contract strict gate"):workflow.index("      - name: Explain report-only pull request result")]
        self.assertIn("if: github.event_name != 'pull_request'", strict)
        self.assertIn("python3 tools/production_readiness_gate.py --strict", strict)
        self.assertIn("npm run production:certification", strict)


    def test_non_pr_runs_resolve_revision_bound_evidence_before_inventory(self):
        workflow = (ROOT / ".github/workflows/production-readiness.yml").read_text(encoding="utf-8")
        resolver = workflow.index("      - name: Build revision-bound production evidence manifest")
        inventory = workflow.index("      - name: Run evidence inventory")
        self.assertLess(resolver, inventory)
        self.assertIn("if: github.event_name != 'pull_request'", workflow[resolver:inventory])
        self.assertIn("--wait-seconds 600", workflow[resolver:inventory])
        self.assertIn("DREAMCO_PRODUCTION_EVIDENCE_MANIFEST=", workflow[resolver:inventory])

if __name__ == "__main__":
    unittest.main()
