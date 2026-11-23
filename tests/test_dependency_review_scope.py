import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "dependency-review.yml"


class DependencyReviewScopeTests(unittest.TestCase):
    def test_detector_covers_common_dependency_manifests_and_workflow_actions(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("detect-dependency-changes:", text)
        self.assertIn('git diff --name-only "origin/$BASE_REF...HEAD"', text)
        for pattern in ("yarn\\\\.lock", "pnpm-lock\\\\.yaml", "Gemfile", "composer\\\\.(json|lock)", "^\\\\.github/workflows/.*\\\\.ya?ml$"):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_dependency_review_job_runs_and_records_explicit_not_applicable(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        job_lines = text.splitlines()
        job_index = job_lines.index("  dependency-review:")
        self.assertEqual(job_lines[job_index + 1], "    needs: detect-dependency-changes")
        self.assertEqual(job_lines[job_index + 2], "    runs-on: ubuntu-latest")
        self.assertIn("id: review", text)
        self.assertIn("if: needs.detect-dependency-changes.outputs.changed == 'true'", text)
        self.assertIn("Verify dependency review evidence or explicit not-applicable state", text)
        self.assertIn("if: always()", text)
        self.assertIn("REVIEW_OUTCOME", text)
        self.assertIn("Dependency applicability is unknown; failing closed.", text)
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
