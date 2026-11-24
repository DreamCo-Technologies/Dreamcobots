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

    def test_resolved_requires_later_successful_matching_workflow_and_branch(self):
        original = {"workflow_id": 10, "head_branch": "main", "status": "completed", "conclusion": "failure", "run_started_at": "2026-11-23T10:00:00Z"}
        candidate = {"workflow_id": 10, "head_branch": "main", "status": "completed", "conclusion": "success", "run_started_at": "2026-11-23T10:10:00Z"}
        validate_evidence("resolved", "original run", original, candidate)

    def test_resolved_rejects_older_successful_run(self):
        original = {"workflow_id": 10, "head_branch": "main", "status": "completed", "conclusion": "failure", "run_started_at": "2026-11-23T10:00:00Z"}
        candidate = {"workflow_id": 10, "head_branch": "main", "status": "completed", "conclusion": "success", "run_started_at": "2026-11-23T09:59:00Z"}
        with self.assertRaisesRegex(ValueError, "start after the original failed run"):
            validate_evidence("resolved", "original run", original, candidate)

    def test_resolved_rejects_original_run_that_did_not_fail(self):
        original = {"workflow_id": 10, "head_branch": "main", "status": "completed", "conclusion": "success", "run_started_at": "2026-11-23T10:00:00Z"}
        candidate = {"workflow_id": 10, "head_branch": "main", "status": "completed", "conclusion": "success", "run_started_at": "2026-11-23T10:10:00Z"}
        with self.assertRaisesRegex(ValueError, "original run to be a completed failure"):
            validate_evidence("resolved", "original run", original, candidate)

    def test_resolved_rejects_missing_timestamps(self):
        original = {"workflow_id": 10, "head_branch": "main", "status": "completed", "conclusion": "failure"}
        candidate = {"workflow_id": 10, "head_branch": "main", "status": "completed", "conclusion": "success"}
        with self.assertRaisesRegex(ValueError, "requires timestamps"):
            validate_evidence("resolved", "original run", original, candidate)

    def test_resolved_rejects_failed_replacement_run(self):
        original = {"workflow_id": 10, "head_branch": "main", "status": "completed", "conclusion": "failure", "run_started_at": "2026-11-23T10:00:00Z"}
        candidate = {"workflow_id": 10, "head_branch": "main", "status": "completed", "conclusion": "failure", "run_started_at": "2026-11-23T10:10:00Z"}
        with self.assertRaises(ValueError):
            validate_evidence("resolved", "original run", original, candidate)

    def test_resolved_rejects_unrelated_workflow(self):
        original = {"workflow_id": 10, "head_branch": "main", "status": "completed", "conclusion": "failure", "run_started_at": "2026-11-23T10:00:00Z"}
        candidate = {"workflow_id": 11, "head_branch": "main", "status": "completed", "conclusion": "success", "run_started_at": "2026-11-23T10:10:00Z"}
        with self.assertRaises(ValueError):
            validate_evidence("resolved", "original run", original, candidate)

    def test_issue_lifecycle_workflow_declares_dispatch_inputs_in_the_correct_event(self):
        source = (ROOT / ".github/workflows/issue-lifecycle.yml").read_text(encoding="utf-8")
        dispatch = source.split("  push:", 1)[0]
        self.assertIn("  workflow_dispatch:\n    inputs:", dispatch)
        self.assertNotIn("    inputs:", source.split("  push:", 1)[1])
        self.assertNotIn("|| true", source)
        self.assertIn("Failed to create or verify required lifecycle label", source)

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

    def test_continuous_repair_is_artifact_only_and_never_writes_branches(self):
        source = (ROOT / ".github/workflows/buddy-continuous-repair.yml").read_text(encoding="utf-8")
        permissions = source.split("permissions:", 1)[1].split("concurrency:", 1)[0]
        self.assertIn("contents: read", permissions)
        self.assertIn("issues: write", permissions)
        self.assertIn("actions: read", permissions)
        self.assertNotIn("contents: write", permissions)
        self.assertNotIn("pull-requests: write", permissions)
        self.assertNotIn("peter-evans/create-pull-request@", source)
        self.assertNotRegex(source, r"(?m)^\\s*git push(?:\\s|$)")
        self.assertNotIn("force-with-lease", source)
        self.assertIn("actions/upload-artifact@v7", source)
        self.assertIn("Open or update a human-triage issue if verification fails", source)

    def test_retest_requires_active_matching_run(self):
        original = {"workflow_id": 10, "head_branch": "main"}
        candidate = {"workflow_id": 10, "head_branch": "main", "status": "in_progress"}
        validate_evidence("retest", "original run", original, candidate)


if __name__ == "__main__":
    unittest.main()
