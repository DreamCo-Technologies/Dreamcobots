import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "dependency-review.yml"


class DependencyReviewScopeTests(unittest.TestCase):
    def test_review_only_runs_when_dependency_manifests_change(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("detect-dependency-changes:", text)
        self.assertIn('git diff --name-only "origin/$BASE_REF...HEAD"', text)
        self.assertIn("if: needs.detect-dependency-changes.outputs.changed == 'true'", text)
        self.assertIn("actions/dependency-review-action@v5", text)
        self.assertIn("fail-on-severity: high", text)

    def test_workflow_is_still_triggered_for_all_main_pull_requests(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        trigger = text.split("permissions:", 1)[0]
        self.assertIn("pull_request:", trigger)
        self.assertIn("branches: [main]", trigger)
        self.assertNotIn("paths:", trigger)


if __name__ == "__main__":
    unittest.main()
