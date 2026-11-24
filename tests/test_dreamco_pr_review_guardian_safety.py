from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/dreamco-pr-review-guardian.yml"

class DreamCoPRReviewGuardianSafetyTests(unittest.TestCase):
    def test_new_commits_do_not_cancel_productive_review_runs(self):
        content = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("cancel-in-progress: false", content)

    def test_review_workflow_remains_read_only(self):
        content = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("contents: read", content)
        self.assertIn("pull-requests: read", content)
        self.assertNotIn("contents: write", content)

if __name__ == "__main__":
    unittest.main()
