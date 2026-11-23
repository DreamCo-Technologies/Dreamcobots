import json
import os
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch

from tools import audit_actions_live as live
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

    def test_rate_limit_writes_explicit_unavailable_report_without_claiming_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(live, "OUT_JSON", root / "live.json"), \
                 patch.object(live, "PUBLIC_JSON", root / "public.json"), \
                 patch.object(live, "OUT_MD", root / "live.md"), \
                 patch.dict(os.environ, {"GITHUB_REPOSITORY": "owner/repo"}), \
                 patch("tools.audit_actions_live.api", side_effect=live.LiveAuditUnavailable("GitHub API 403 rate limit")):
                self.assertEqual(live.main(), 0)
            payload = json.loads((root / "live.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "unavailable")
            self.assertFalse(payload["run_window_coverage_complete"])
            self.assertIn("no run is inferred", payload["run_window_note"])
            self.assertIn("UNAVAILABLE", (root / "live.md").read_text(encoding="utf-8"))

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

    def test_safe_repair_stages_generated_actions_health_report(self):
        source = (ROOT / ".github" / "workflows" / "buddy-ci-safe-repair.yml").read_text(encoding="utf-8")
        self.assertIn("website/data/actions-health-report.json", source)
        self.assertEqual(source.count("config/generated/file-prospectus"), 1)
