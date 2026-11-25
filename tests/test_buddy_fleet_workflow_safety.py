from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/buddy-fleet-execution-map.yml"


class BuddyFleetWorkflowSafetyTests(unittest.TestCase):
    def test_generated_outputs_use_reviewed_pull_request_not_direct_main_push(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("peter-evans/create-pull-request@v7", text)
        self.assertIn("branch: automation/buddy-fleet-generated", text)
        self.assertIn("base: main", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("persist-credentials: true", text)
        self.assertIn("persist-credentials: false", text)
        self.assertIn("cancel-in-progress: false", text)

    def test_pr_validation_is_read_only_and_outputs_are_artifacts(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("permissions:\n  contents: read", text)
        self.assertIn("actions/upload-artifact@v7", text)
        self.assertIn("owner-review-gated", text)
        self.assertIn("privileged execution remains disabled", text)


if __name__ == "__main__":
    unittest.main()
