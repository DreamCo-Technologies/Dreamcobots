"""Safety regression: automated issue triage must never close unresolved failures."""
from __future__ import annotations

import contextlib
import io
import json
import os
import unittest
from unittest import mock

from tools.issue_cleaner import clean_issues as cleaner


class IssueCleanerReadOnlyTests(unittest.TestCase):
    def test_read_only_cannot_be_disabled_by_environment(self):
        self.assertTrue(cleaner.DRY_RUN)

    def test_mutation_helpers_do_not_write(self):
        with mock.patch.object(cleaner.subprocess, "run", side_effect=AssertionError("mutation attempted")):
            cleaner.gh_run(["issue", "close", "123"])
            self.assertFalse(cleaner.ensure_labels(123, [], ["ci-failure"]))
            with self.assertRaises(PermissionError):
                cleaner.close_issue(123, "not_planned", "newer failure exists")

    def test_supersession_preserves_all_issues(self):
        def issue(number, title, created):
            return cleaner.Issue(
                number=number,
                title=title,
                author="github-actions[bot]",
                created_at=created,
                updated_at=created,
            )

        records = [
            issue(12, "Actions run 12 failed: Keep Green", "2026-10-23T12:00:00Z"),
            issue(11, "Actions run 11 failed: Keep Green", "2026-10-23T11:00:00Z"),
            issue(10, "Actions run 10 failed: Keep Green", "2026-10-23T10:00:00Z"),
        ]
        output = io.StringIO()
        with (
            mock.patch.object(cleaner, "REPO", "DreamCo-Technologies/Dreamcobots"),
            mock.patch.object(cleaner, "KEEP_PER_WORKFLOW", 2),
            mock.patch.object(cleaner, "fetch_open_issues", return_value=records),
            mock.patch.object(cleaner, "gh_run", side_effect=AssertionError("GitHub mutation attempted")),
            mock.patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": ""}),
            contextlib.redirect_stdout(output),
        ):
            self.assertEqual(cleaner.main(), 0)

        summary = json.loads(output.getvalue()[output.getvalue().rfind("\n{") + 1 :])
        self.assertEqual(summary["scanned"], 3)
        self.assertEqual(summary["closed_superseded_ci"], 0)
        self.assertEqual(summary["closed_dup_root"], 0)
        self.assertEqual(summary["labeled"], 0)
        self.assertEqual(summary["would_close_superseded_ci"], 1)
        self.assertIn("Preserved CI #10", output.getvalue())


if __name__ == "__main__":
    unittest.main()
