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
    return {"id": run_id, "name": name, "conclusion": conclusion, "updated_at": updated_at, "status": status, "head_sha": "a" * 40, "head_branch": "main", "path": ".github/workflows/keep-green.yml", "repository": {"full_name": "DreamCo-Technologies/Dreamcobots"}, "html_url": f"https://github.com/DreamCo-Technologies/Dreamcobots/actions/runs/{run_id}"}


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

    def test_other_branch_cannot_supply_main_evidence(self):
        other = run(conclusion="success")
        other["head_branch"] = "codex/consolidated-dreamco-completion"
        self.assertEqual(observations({"workflow_runs": [other]}, now=NOW, max_age_hours=6)[0]["conclusion"], "unknown")

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
        self.assertIn("status=completed&branch=main&per_page=30", args[2])
        self.assertEqual(mock_run.call_args.kwargs["timeout"], 30)
        mock_run.side_effect = subprocess.CalledProcessError(1, args)
        with self.assertRaises(subprocess.CalledProcessError):
            collect("DreamCo-Technologies/Dreamcobots", now=NOW, max_age_hours=6)

    def test_unrelated_workflow_path_cannot_supply_success(self):
        forged = run(conclusion="success")
        forged["path"] = ".github/workflows/other.yml"
        self.assertEqual(observations({"workflow_runs": [forged]}, now=NOW, max_age_hours=6)[0]["conclusion"], "unknown")

    def test_cross_repository_or_untrusted_run_url_cannot_supply_success(self):
        for field, bad in (("repository", {"full_name": "someone/other"}), ("html_url", "https://example.org/redirect"), ("repository", None)):
            with self.subTest(field=field, bad=bad):
                forged = run(conclusion="success")
                forged[field] = bad
                self.assertEqual(observations({"workflow_runs": [forged]}, now=NOW, max_age_hours=6, expected_repo="DreamCo-Technologies/Dreamcobots")[0]["conclusion"], "unknown")

    def test_missing_or_malformed_commit_cannot_supply_success(self):
        for bad in ("abc123", "", None, 123, True):
            with self.subTest(bad=bad):
                forged = run(conclusion="success")
                forged["head_sha"] = bad
                self.assertEqual(observations({"workflow_runs": [forged]}, now=NOW, max_age_hours=6)[0]["conclusion"], "unknown")

    def test_newer_invalid_run_prevents_stale_success_fallback(self):
        older = run(run_id=41, conclusion="success", updated_at="2026-10-24T05:10:00Z")
        newer = run(run_id=42, conclusion="failure")
        newer["path"] = ".github/workflows/other.yml"
        result = observations({"workflow_runs": [older, newer]}, now=NOW, max_age_hours=6)
        self.assertEqual(result[0]["conclusion"], "unknown")
        self.assertEqual(result[0]["evidence_status"], "latest_run_invalid_provenance")

    def test_expected_repository_must_match(self):
        result = observations({"workflow_runs": [run(conclusion="success")]}, now=NOW, max_age_hours=6, expected_repo="other/repo")
        self.assertEqual(result[0]["conclusion"], "unknown")

    def test_github_workflow_run_ref_paths_are_accepted(self):
        # GitHub REST workflow-run payloads use path@ref (e.g. @main).
        for suffix in ("@main", "@refs/heads/main", ""):
            with self.subTest(suffix=suffix):
                item = run(conclusion="success")
                item["path"] += suffix
                result = observations({"workflow_runs": [item]}, now=NOW, max_age_hours=6,
                                      expected_repo="DreamCo-Technologies/Dreamcobots")
                self.assertEqual(result[0]["conclusion"], "success")
                self.assertEqual(result[0]["evidence_status"], "observed")

    def test_unrelated_workflow_refs_never_supply_success(self):
        for bad_path in (
            ".github/workflows/keep-green.yml@other-branch",
            ".github/workflows/keep-green.yml@refs/heads/other-branch",
            ".github/workflows/other.yml@main",
            ".github/workflows/keep-green.yml@",
        ):
            with self.subTest(path=bad_path):
                item = run(conclusion="success")
                item["path"] = bad_path
                result = observations({"workflow_runs": [item]}, now=NOW, max_age_hours=6,
                                      expected_repo="DreamCo-Technologies/Dreamcobots")
                self.assertEqual(result[0]["conclusion"], "unknown")
                self.assertEqual(result[0]["evidence_status"], "latest_run_invalid_provenance")

    def test_unhashable_conclusions_fail_closed_without_crashing(self):
        for invalid in ([], {}, ["success"], {"status": "success"}):
            with self.subTest(invalid=invalid):
                item = run(conclusion=invalid)
                item["path"] = ".github/workflows/keep-green.yml@main"
                result = observations({"workflow_runs": [item]}, now=NOW, max_age_hours=6,
                                      expected_repo="DreamCo-Technologies/Dreamcobots")
                self.assertEqual(result[0]["conclusion"], "unknown")
                self.assertEqual(result[0]["evidence_status"], "latest_run_invalid_provenance")

    def test_invalid_repo_rejected_without_network(self):
        with patch("tools.greenkeeper_observations.subprocess.run") as mock_run:
            with self.assertRaises(ValueError):
                collect("owner/repo;echo BAD", now=NOW, max_age_hours=6)
            mock_run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
