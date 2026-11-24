from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/dreamco-unified-system.yml"
LAPTOP_RUNNER = ROOT / "tools/run_buddy_laptop_app.mjs"


class FiveHundredModelWorkflowScopeTests(unittest.TestCase):
    def test_benchmark_workflow_never_falls_back_to_unrelated_full_system_runner(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("tools/run_500_model_benchmarks.py", text)
        self.assertNotIn("--fallback tools/run_everything_now.py", text)
        self.assertIn("BLOCKED_RUNNER_NOT_IMPLEMENTED", text)
        self.assertIn("all matrix rows remain unverified", text)

    def test_benchmark_workflow_does_not_install_unrelated_media_stack(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("requirements-media.txt", text)
        self.assertIn("requirements-buddy-learning.txt", text)

    def test_missing_career_pathways_source_data_is_reported_as_skipped_not_passed(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("study_packs/career_pathways/raw/task_statements.csv", text)
        self.assertIn("SKIPPED: study_packs/career_pathways/tests", text)
        self.assertIn("--ignore=study_packs/career_pathways/tests", text)

    def test_laptop_test_key_is_not_key_shaped(self):
        text = LAPTOP_RUNNER.read_text(encoding="utf-8")
        self.assertNotIn("sk-local-test-placeholder", text)
        self.assertIn("local-test-placeholder-not-a-key", text)


if __name__ == "__main__":
    unittest.main()
