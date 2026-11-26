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


if __name__ == "__main__":
    unittest.main()
