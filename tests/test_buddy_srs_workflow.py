from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BuddySRSWorkflowTests(unittest.TestCase):
    def test_workflow_has_manual_dispatch(self):
        workflow = (ROOT / ".github/workflows/buddy-spaced-repetition-tests.yml").read_text(encoding="utf-8")
        self.assertIn("  workflow_dispatch:", workflow)

    def test_push_and_pull_request_filters_cover_scheduler_schema_and_dependencies(self):
        workflow = (ROOT / ".github/workflows/buddy-spaced-repetition-tests.yml").read_text(encoding="utf-8")
        for path in ("buddy/learning/srs/**", "requirements-buddy-learning.txt", "shared/schema.ts", "migrations/**", "tests/test_buddy_srs_*.py"):
            self.assertGreaterEqual(workflow.count(f"      - '{path}'"), 2, path)


if __name__ == "__main__":
    unittest.main()
