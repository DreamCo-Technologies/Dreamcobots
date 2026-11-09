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
