import unittest
from tools.generate_github_control_tower import PUBLIC_REPOSITORIES, summarize_checks, summarize_reviews, summarize_status

class ControlTowerSummaryTests(unittest.TestCase):
    def test_failure_is_not_ready(self):
        x=summarize_checks([{"name":"unit","status":"completed","conclusion":"success"},{"name":"security","status":"completed","conclusion":"failure"}])
        self.assertEqual(x["readiness"],"checks_failing")
        self.assertEqual(x["failures"][0]["name"],"security")
    def test_pending_is_not_passing(self):
        x=summarize_checks([{"name":"build","status":"in_progress","conclusion":None}])
        self.assertEqual(x["readiness"],"checks_pending")
    def test_all_green_still_requires_review(self):
        x=summarize_checks([{"name":"unit","status":"completed","conclusion":"success"},{"name":"lint","status":"completed","conclusion":"skipped"}])
        self.assertEqual(x["readiness"],"checks_passed_review_still_required")
    def test_no_checks_is_not_green(self):
        self.assertEqual(summarize_checks([])["readiness"],"no_check_runs")
    def test_review_summary_uses_latest_state_per_reviewer(self):
        summary = summarize_reviews([
            {"user": {"login": "reviewer"}, "state": "COMMENTED", "submitted_at": "2026-01-01T00:00:00Z"},
            {"user": {"login": "reviewer"}, "state": "APPROVED", "submitted_at": "2026-01-02T00:00:00Z"},
            {"user": {"login": "owner"}, "state": "CHANGES_REQUESTED", "submitted_at": "2026-01-03T00:00:00Z"},
        ])
        self.assertEqual(summary["reviewers"], 2)
        self.assertEqual(summary["counts"]["approved"], 1)
        self.assertEqual(summary["counts"]["changes_requested"], 1)

    def test_commit_status_contexts_are_kept(self):
        x=summarize_status({"state":"failure","statuses":[{"context":"build","state":"failure","target_url":"https://example.invalid"}]})
        self.assertEqual(x["state"],"failure")
        self.assertEqual(x["contexts"][0]["context"],"build")
    def test_public_repository_allowlist_is_explicit(self):
        self.assertEqual(set(PUBLIC_REPOSITORIES), {
            "DreamCo-Technologies/Dreamcobots",
            "ireanjordan24/Dreamcobots-frontier-trust",
            "ireanjordan24/Dreamcobots-Grok-Revolutionary",
        })

if __name__=="__main__": unittest.main()
