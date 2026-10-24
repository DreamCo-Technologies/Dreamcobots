"""Provenance and manual-dispatch regression tests for benchmark artifact handoffs."""
from __future__ import annotations

import unittest
from pathlib import Path

from tools.validate_benchmark_upstream_run import verify_run, EXPECTED_WORKFLOW_PATHS

ROOT = Path(__file__).resolve().parents[1]
REPO = "DreamCo-Technologies/Dreamcobots"
BRANCH = "main"
WORKFLOWS = {
    "benchmark-training-queue.yml": "Benchmark Evidence Loop",
    "benchmark-sandbox-manifest.yml": "Benchmark Training Queue",
    "benchmark-training-execution.yml": "Benchmark Training Queue",
}


class BenchmarkUpstreamRunBindingTests(unittest.TestCase):
    def sample(self):
        return {
            "id": 12345,
            "name": "Benchmark Evidence Loop",
            "path": ".github/workflows/benchmark-evidence-loop.yml@main",
            "status": "completed",
            "conclusion": "success",
            "repository": {"full_name": REPO},
            "head_repository": {"full_name": REPO},
            "head_branch": BRANCH,
        }

    def check(self, data):
        return verify_run(data, run_id="12345", expected_name="Benchmark Evidence Loop",
                          repository=REPO, expected_branch=BRANCH)

    def test_valid_completed_same_repository_run(self):
        self.assertEqual(self.check(self.sample()), [])

    def test_untrusted_or_incomplete_upstream_run_rejected(self):
        changes = [
            {"id": 12346}, {"name": "Unrelated Workflow"},
            {"status": "in_progress"}, {"conclusion": "failure"},
            {"repository": {"full_name": "someone/else"}},
            {"head_repository": {"full_name": "someone/fork"}},
            {"head_repository": None},
            {"head_branch": "unrelated-branch"},
            {"head_branch": ""},
            {"head_branch": None},
            {"head_branch": True},
        ]
        for change in changes:
            with self.subTest(change=change):
                self.assertTrue(self.check({**self.sample(), **change}))

    def test_workflow_name_collision_cannot_spoof_artifact_source(self):
        for path in (None, True, 123, "", ".github/workflows/other.yml@main",
                     ".github/workflows/benchmark-evidence-loop.yml",
                     ".github/workflows/benchmark-evidence-loop.yml@",
                     ".github/workflows/benchmark-evidence-loop.yml.bak@main"):
            with self.subTest(path=path):
                self.assertTrue(self.check({**self.sample(), "path": path}))

    def test_registered_training_queue_source_and_pr_ref(self):
        queue = {**self.sample(), "name": "Benchmark Training Queue",
                 "path": ".github/workflows/benchmark-training-queue.yml@main"}
        self.assertEqual(verify_run(queue, run_id="12345", expected_name="Benchmark Training Queue",
                                    repository=REPO, expected_branch=BRANCH), [])
        pr = {**self.sample(), "path": ".github/workflows/benchmark-evidence-loop.yml@refs/pull/14014/merge"}
        self.assertEqual(self.check(pr), [])
        self.assertTrue(verify_run(queue, run_id="12345", expected_name="Not Registered",
                                   repository=REPO, expected_branch=BRANCH))

    def test_missing_current_branch_rejected(self):
        for expected_branch in ("", "  ", None):
            with self.subTest(expected_branch=expected_branch):
                self.assertTrue(verify_run(self.sample(), run_id="12345",
                                           expected_name="Benchmark Evidence Loop",
                                           repository=REPO, expected_branch=expected_branch))

    def test_review_branch_must_match_review_source(self):
        review = {**self.sample(), "head_branch": "codex/consolidated-dreamco-completion"}
        self.assertEqual(verify_run(review, run_id="12345", expected_name="Benchmark Evidence Loop",
                                    repository=REPO, expected_branch="codex/consolidated-dreamco-completion"), [])
        self.assertTrue(self.check(review))

    def test_malformed_run_identity_rejected(self):
        for run_id in ("", "0", "-1", "1e3", "12345;echo", " 12345"):
            with self.subTest(run_id=run_id):
                self.assertTrue(verify_run(self.sample(), run_id=run_id,
                                           expected_name="Benchmark Evidence Loop", repository=REPO,
                                           expected_branch=BRANCH))
        self.assertTrue(self.check(None))

    def test_all_three_manual_workflows_bind_and_validate_upstream_artifacts(self):
        for filename, expected in WORKFLOWS.items():
            with self.subTest(workflow=filename):
                workflow = (ROOT / ".github/workflows" / filename).read_text(encoding="utf-8")
                self.assertIn("source_run_id:", workflow)
                self.assertIn("required: true", workflow)
                self.assertIn("github.event.workflow_run.id || inputs.source_run_id", workflow)
                self.assertIn("python3 tools/validate_benchmark_upstream_run.py", workflow)
                self.assertIn(f'--expected "{expected}"', workflow)
                self.assertIn(expected, EXPECTED_WORKFLOW_PATHS)
                self.assertLess(workflow.index("python3 tools/validate_benchmark_upstream_run.py"),
                                workflow.index("uses: actions/download-artifact@"))
                self.assertIn("actions: read", workflow)
                self.assertIn("contents: read", workflow)
                self.assertNotIn("contents: write", workflow)
                self.assertNotIn("issues: write", workflow)


if __name__ == "__main__":
    unittest.main()
