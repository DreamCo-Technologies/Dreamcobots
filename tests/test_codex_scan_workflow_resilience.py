"""Ensure read-only scan diagnostics survive earlier contract failures."""
from pathlib import Path
import unittest

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/codex-scan-only.yml"


class CodexScanWorkflowResilienceTests(unittest.TestCase):
    def test_scan_runs_after_failed_validation(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        scan = text.split("      - name: Scan source without executing application code", 1)[1]
        scan = scan.split("      - name:", 1)[0]
        self.assertIn("if: ${{ !cancelled() }}", scan)
        self.assertIn("python3 tools/codex_scan.py", scan)

    def test_contract_checks_remain_fail_closed(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("python3 -m unittest tests.test_proposal_registry tests.test_codex_scan tests.test_superbot_crosswalk tests.test_codex_scan_workflow_resilience", text)
        self.assertIn("python3 tools/build_superbot_crosswalk.py --check", text)

    def test_artifact_upload_remains_unconditional(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: codex-scan-grok-work-orders", text)
        self.assertIn("if: always()", text)


if __name__ == "__main__":
    unittest.main()
