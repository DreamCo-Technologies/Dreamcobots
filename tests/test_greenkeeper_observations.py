"""Offline regression tests for bounded Greenkeeper workflow evidence."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.greenkeeper_observations import collect, observations

NOW = datetime(2026, 10, 24, 6, 0, tzinfo=timezone.utc)


def run(*, run_id=42, name="Keep Green", conclusion="failure", updated_at="2026-10-24T05:50:00Z", status="completed"):
    return {"id": run_id, "name": name, "conclusion": conclusion, "updated_at": updated_at, "status": status, "head_sha": "abc123", "html_url": "https://github.com/example/repo/actions/runs/42"}


class GreenkeeperObservationsTests(unittest.TestCase):
    def test_latest_valid_completed_keep_green_run_is_used(self):
        data = {"workflow_runs": [run(run_id=41, conclusion="success", updated_at="2026-10-24T05:10:00Z"), run(), run(name="Unrelated Workflow", run_id=99)]}
        rows = observations(data, now=NOW, max_age_hours=6)
        self.assertEqual(rows[0]["conclusion"], "failure")
        self.assertEqual(rows[0]["run_id"], 42)
        self.assertEqual(rows[0]["evidence_status"], "observed")

    def test_stale_or_missing_data_never_becomes_success(self):
        for payload in ({"workflow_runs": []}, {"workflow_runs": [run(updated_at="2026-10-22T05:50:00Z")]}, {"workflow_runs": [run(status="in_progress")]}):
            with self.subTest(payload=payload):
                self.assertEqual(observations(payload, now=NOW, max_age_hours=6)[0]["conclusion"], "unknown")

    def test_malformed_run_identity_never_becomes_success(self):
        for invalid in (True, "42", 0, -1):
            with self.subTest(invalid=invalid):
                self.assertEqual(observations({"workflow_runs": [run(run_id=invalid, conclusion="success")]}, now=NOW, max_age_hours=6)[0]["conclusion"], "unknown")

    def test_malformed_response_fails_closed(self):
        for bad in ([], {}, {"workflow_runs": "not an array"}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                observations(bad, now=NOW, max_age_hours=6)

    def test_invalid_window_fails_closed(self):
        with self.assertRaises(ValueError):
            observations({"workflow_runs": []}, now=NOW, max_age_hours=0)
        with self.assertRaises(ValueError):
            observations({"workflow_runs": []}, now=NOW, max_age_hours=25)

    @patch("tools.greenkeeper_observations.subprocess.run")
    def test_api_is_read_only_bounded_and_failures_propagate(self, mock_run):
        mock_run.return_value.stdout = json.dumps({"workflow_runs": [run()]})
        rows = collect("DreamCo-Technologies/Dreamcobots", now=NOW, max_age_hours=6)
        self.assertEqual(rows[0]["conclusion"], "failure")
        args = mock_run.call_args.args[0]
        self.assertEqual(args[:2], ["gh", "api"])
        self.assertIn("status=completed&per_page=30", args[2])
        self.assertEqual(mock_run.call_args.kwargs["timeout"], 30)
        mock_run.side_effect = subprocess.CalledProcessError(1, args)
        with self.assertRaises(subprocess.CalledProcessError):
            collect("DreamCo-Technologies/Dreamcobots", now=NOW, max_age_hours=6)

    def test_invalid_repo_rejected_without_network(self):
        with patch("tools.greenkeeper_observations.subprocess.run") as mock_run:
            with self.assertRaises(ValueError):
                collect("owner/repo;echo BAD", now=NOW, max_age_hours=6)
            mock_run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
