import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from tools.issue_lifecycle import transition_labels, validate_evidence


class IssueLifecycleTests(unittest.TestCase):
    def test_status_transition_preserves_non_status_labels(self):
        self.assertEqual(
            transition_labels(["ci-failure", "severity:high", "status:new"], "fixing"),
            ["ci-failure", "severity:high", "status:fixing"],
        )

    def test_resolved_requires_successful_matching_workflow_and_branch(self):
        original = {"workflow_id": 10, "head_branch": "main"}
        candidate = {"workflow_id": 10, "head_branch": "main", "status": "completed", "conclusion": "success"}
        validate_evidence("resolved", "original run", original, candidate)

    def test_resolved_rejects_failed_replacement_run(self):
        original = {"workflow_id": 10, "head_branch": "main"}
        candidate = {"workflow_id": 10, "head_branch": "main", "status": "completed", "conclusion": "failure"}
        with self.assertRaises(ValueError):
            validate_evidence("resolved", "original run", original, candidate)

    def test_resolved_rejects_unrelated_workflow(self):
        original = {"workflow_id": 10, "head_branch": "main"}
        candidate = {"workflow_id": 11, "head_branch": "main", "status": "completed", "conclusion": "success"}
        with self.assertRaises(ValueError):
            validate_evidence("resolved", "original run", original, candidate)

    def test_failure_watch_uses_event_payload_and_survives_api_rate_limits(self):
        source = (ROOT / ".github/workflows/actions-failure-watch.yml").read_text(encoding="utf-8")
        self.assertNotIn('gh api "repos/$GITHUB_REPOSITORY/actions/runs/$RUN_ID"', source)
        self.assertIn("if gh api --paginate", source)
        self.assertIn('availability: "unavailable"', source)
        self.assertIn("Job metadata unavailable:", source)

    def test_workflow_run_handlers_use_per_event_concurrency_keys(self):
        paths = [
            ".github/workflows/actions-failure-watch.yml",
            ".github/workflows/issue-intelligence.yml",
            ".github/workflows/buddy-continuous-repair.yml",
            ".github/workflows/greenkeeper-root-cause.yml",
            ".github/workflows/greenkeeper-orchestrator.yml",
        ]
        for relative in paths:
            with self.subTest(workflow=relative):
                source = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("${{ github.event.workflow_run.id || github.run_id }}", source)
                self.assertIn("cancel-in-progress: false", source)

    def test_retest_requires_active_matching_run(self):
        original = {"workflow_id": 10, "head_branch": "main"}
        candidate = {"workflow_id": 10, "head_branch": "main", "status": "in_progress"}
        validate_evidence("retest", "original run", original, candidate)


if __name__ == "__main__":
    unittest.main()
