"""Fail-closed behavior for branch health comparisons."""
import subprocess
import unittest
from unittest.mock import patch

from tools import branch_health_daily as health

class BranchHealthFailClosedTests(unittest.TestCase):
    def test_unavailable_comparison_votes_block(self):
        self.assertEqual(health.vote_freshness(None)[0], "block")
        self.assertEqual(health.vote_complete(None)[0], "block")
        votes, score, status = health.review(None, None, None)
        self.assertEqual(status, "blocked")
        self.assertLess(score, 100)
        self.assertTrue(any(v["reviewer"] == "comparison" or v["vote"] == "block" for v in votes))

    def test_git_ahead_behind_error_raises_instead_of_returning_zero(self):
        failure = subprocess.CompletedProcess(["git"], 128, "", "fatal: no merge base")
        with patch.object(health, "git", return_value=failure):
            with self.assertRaisesRegex(RuntimeError, "no merge base"):
                health.local_ahead_behind("unrelated-history")

    def test_git_missing_file_error_raises_instead_of_returning_empty(self):
        failure = subprocess.CompletedProcess(["git"], 128, "", "fatal: no merge base")
        with patch.object(health, "git", return_value=failure):
            with self.assertRaisesRegex(RuntimeError, "no merge base"):
                health.local_missing("unrelated-history")

    def test_local_branch_inventory_uses_api_protection_flags(self):
        branch_line = "origin/example\\tdeadbeef\\t2026-11-09T00:00:00Z"
        completed = subprocess.CompletedProcess(["git"], 0, branch_line, "")
        with patch.object(health, "git", return_value=completed), patch.object(
            health, "api_branches", return_value=[{"name": "example", "protected": True}]
        ):
            rows = health.local_branches()
        self.assertEqual(rows[0]["protected"], True)
        self.assertEqual(rows[0]["protectionStatus"], "api_flag")

    def test_pr_requires_successful_checks_and_approval(self):
        pr = {"number": 7, "head": {"sha": "abc123"}}
        check_payload = {"check_runs": [{"status": "completed", "conclusion": "success"}]}
        status_payload = {"state": "success"}
        approved = [{"user": {"login": "reviewer"}, "submitted_at": "2026-11-09T00:00:00Z", "state": "APPROVED"}]
        with patch.object(health, "gh", side_effect=[check_payload, status_payload]), patch.object(health, "gh_pages", return_value=approved):
            evidence = health.pr_evidence(pr)
        self.assertEqual(evidence["checkState"], "success")
        self.assertEqual(evidence["reviewState"], "approved")
        self.assertEqual(health.vote_merge({"mergeable_state": "clean", "draft": False, "_evidence": evidence})[0], "pass")

    def test_pr_failure_or_missing_review_blocks(self):
        pr = {"number": 8, "head": {"sha": "def456"}}
        check_payload = {"check_runs": [{"status": "completed", "conclusion": "failure"}]}
        status_payload = {"state": "failure"}
        with patch.object(health, "gh", side_effect=[check_payload, status_payload]), patch.object(health, "gh_pages", return_value=[]):
            evidence = health.pr_evidence(pr)
        self.assertEqual(evidence["checkState"], "failure")
        self.assertEqual(evidence["reviewState"], "unreviewed")
        vote, note = health.vote_merge({"mergeable_state": "clean", "draft": False, "_evidence": evidence})
        self.assertEqual(vote, "block")
        self.assertIn("CI evidence", note)

    def test_pr_base_comparison_uses_actual_base(self):
        comparison = {"ahead_by": 3, "behind_by": 2, "files": []}
        with patch.object(health, "gh", return_value=comparison) as request:
            self.assertEqual(health.api_ahead_behind_missing("feature/head", "release/base"), (3, 2, []))
        self.assertIn("/compare/release%2Fbase...feature%2Fhead", request.call_args.args[0])

    def test_markdown_report_includes_all_branches_not_only_first_80(self):
        report = {
            "scannedAt": "2026-11-09T00:00:00+00:00", "branchCount": 101, "prOpen": 0,
            "healthy": 0, "watch": 0, "blocked": 100, "dirty": 0,
            "branches": [{"name": f"branch-{i}", "score": 0, "status": "blocked", "ahead": None,
                          "behind": None, "missingRequired": None} for i in range(100)],
        }
        rendered = health.markdown_report(report)
        self.assertIn("branch-99", rendered)

    def test_report_labels_missing_comparison_as_unverified(self):
        report = {
            "scannedAt": "2026-11-09T00:00:00+00:00",
            "branchCount": 2, "prOpen": 0, "healthy": 0, "watch": 0,
            "blocked": 1, "dirty": 0,
            "branches": [{
                "name": "example", "score": 0, "status": "blocked",
                "ahead": None, "behind": None, "prNumber": None,
                "missingRequired": None, "comparisonStatus": "unavailable",
            }],
        }
        rendered = health.markdown_report(report)
        self.assertIn("unverified (comparison unavailable)", rendered)

if __name__ == "__main__":
    unittest.main()
