"""Guardrails for the Markdown audit automation's write boundary."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/buddy-markdown-gap-audit.yml"


class MarkdownGapAuditWorkflowSafetyTests(unittest.TestCase):
    def test_workflow_never_pushes_directly_to_main(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"(?m)^\s*git push(?:\s|$)")
        self.assertIn("peter-evans/create-pull-request@v7", text)
        self.assertIn("branch: automation/markdown-gap-audit", text)
        self.assertIn("base: main", text)
        self.assertIn("delete-branch: false", text)
        self.assertIn("group: buddy-markdown-gap-audit-${{ github.run_id }}", text)
        self.assertIn("cancel-in-progress: false", text)

    def test_only_publish_job_has_write_permissions(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^permissions:\n  contents: read$")
        self.assertRegex(text, r"(?ms)^  propose:\n.*?^    permissions:\n      contents: write\n      pull-requests: write")
        self.assertIn("persist-credentials: false", text)

    def test_pull_request_validation_is_read_only_and_does_not_publish(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("  validate:", text)
        self.assertIn("github.event_name == 'pull_request'", text)
        self.assertIn("python3 tools/audit_markdown_implementation_gaps.py --check", text)
        self.assertIn("  propose:", text)
        self.assertIn("needs: generate", text)


if __name__ == "__main__":
    unittest.main()
