from pathlib import Path
import unittest
from tools.run_500_model_benchmarks import build_status

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

    def test_execution_gate_records_blocked_without_fabricating_runs(self):
        status = build_status("standard")
        self.assertEqual(status["status"], "BLOCKED_RUNNER_NOT_IMPLEMENTED")
        self.assertFalse(status["execution_started"])
        self.assertEqual(status["provider_calls"], 0)
        self.assertEqual(status["training_jobs"], 0)
        self.assertEqual(status["verified_results"], 0)
        with self.assertRaises(ValueError):
            build_status("unapproved")

    def test_contract_only_matrix_does_not_install_training_runtime_or_run_full_repo_pytest(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("requirements-media.txt", text)
        self.assertNotIn("requirements-buddy-learning.txt", text)
        self.assertNotIn("torch", text.lower())
        self.assertNotIn("python3 -m pytest -q", text)
        self.assertIn("tests.test_500_model_prospectus_matrix", text)
        self.assertIn("tests.test_benchmark_scope_contract", text)
        self.assertIn("cancel-in-progress: true", text)
        self.assertIn("timeout-minutes: 60", text)

    def test_contract_only_matrix_does_not_run_unavailable_career_pathways_suite(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        # The 500-model workflow validates contracts and evidence readiness only.
        # It does not run the study-pack test suite or claim missing source data passed.
        self.assertNotIn("study_packs/career_pathways/raw/task_statements.csv", text)
        self.assertNotIn("study_packs/career_pathways/tests", text)
        self.assertNotIn("python3 -m pytest -q", text)
        self.assertIn("BLOCKED_RUNNER_NOT_IMPLEMENTED", text)
        self.assertIn("all matrix rows remain unverified", text)

    def test_laptop_test_key_is_not_key_shaped(self):
        text = LAPTOP_RUNNER.read_text(encoding="utf-8")
        self.assertNotIn("sk-local-test-placeholder", text)
        self.assertIn("local-test-placeholder-not-a-key", text)


if __name__ == "__main__":
    unittest.main()
