import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from tools.audit_actions_live import build_workflow_rows, collect_recent_runs


class ActionsLiveHealthTests(unittest.TestCase):
    def setUp(self):
        self.cutoff = datetime(2026, 10, 24, tzinfo=timezone.utc)

    def test_repository_run_stream_is_grouped_by_workflow(self):
        workflows = [
            {"id": 1, "name": "Alpha", "path": ".github/workflows/alpha.yml", "state": "active"},
            {"id": 2, "name": "Beta", "path": ".github/workflows/beta.yml", "state": "active"},
        ]
        runs = [
            {"workflow_id": 1, "id": 11, "created_at": "2026-11-22T10:00:00Z", "status": "completed", "conclusion": "failure", "html_url": "https://example.test/11"},
            {"workflow_id": 1, "id": 10, "created_at": "2026-11-21T10:00:00Z", "status": "completed", "conclusion": "success"},
            {"workflow_id": 2, "id": 20, "created_at": "2026-11-22T09:00:00Z", "status": "in_progress", "conclusion": None},
        ]
        rows = build_workflow_rows(workflows, runs, {"alpha.yml", "beta.yml"}, self.cutoff)
        self.assertEqual(rows[0]["latest_run"]["id"], 11)
        self.assertEqual(rows[0]["recent_30d_runs"], 2)
        self.assertEqual(rows[0]["recent_30d_failures"], 1)
        self.assertEqual(rows[0]["recent_failure_urls"], ["https://example.test/11"])
        self.assertEqual(rows[1]["latest_run"]["status"], "in_progress")

    def test_old_runs_do_not_count_toward_recent_window(self):
        workflows = [{"id": 1, "name": "Alpha", "path": ".github/workflows/alpha.yml", "state": "active"}]
        runs = [{"workflow_id": 1, "id": 1, "created_at": "2026-09-01T00:00:00Z", "status": "completed", "conclusion": "failure"}]
        row = build_workflow_rows(workflows, runs, {"alpha.yml"}, self.cutoff)[0]
        self.assertEqual(row["recent_30d_runs"], 0)
        self.assertIsNone(row["latest_run"])

    def test_run_collection_pages_until_cutoff_is_covered(self):
        recent = [
            {"workflow_id": 1, "id": i, "created_at": "2026-11-20T00:00:00Z"}
            for i in range(100)
        ]
        old = [{"workflow_id": 1, "id": 101, "created_at": "2026-10-01T00:00:00Z"}]
        with patch("tools.audit_actions_live.api", side_effect=[
            {"workflow_runs": recent},
            {"workflow_runs": old},
        ]) as mocked:
            runs, pages, covered = collect_recent_runs("owner/repo", self.cutoff)
        self.assertEqual(len(runs), 101)
        self.assertEqual(pages, 2)
        self.assertTrue(covered)
        self.assertEqual(mocked.call_count, 2)


if __name__ == "__main__":
    unittest.main()
