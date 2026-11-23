import unittest

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

    def test_retest_requires_active_matching_run(self):
        original = {"workflow_id": 10, "head_branch": "main"}
        candidate = {"workflow_id": 10, "head_branch": "main", "status": "in_progress"}
        validate_evidence("retest", "original run", original, candidate)


if __name__ == "__main__":
    unittest.main()
