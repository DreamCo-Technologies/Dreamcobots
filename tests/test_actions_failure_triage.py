"""Regression tests: no one-issue-per-failed-run Actions publication."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.actions_failure_triage import build_triage, render_summary


class FailureTriageTests(unittest.TestCase):
    def test_empty_input_is_truthful(self):
        report = build_triage([])
        self.assertEqual(report["observed_failures"], 0)
        self.assertEqual(report["group_count"], 0)
        self.assertTrue(report["truth_policy"]["passing_evidence_required_to_close"])

    def test_repeated_failures_are_grouped_not_discarded(self):
        rows = [{"id": i, "name": "Keep Green", "conclusion": "failure", "html_url": f"https://example.invalid/{i}"} for i in range(12)]
        report = build_triage(rows)
        self.assertEqual(report["observed_failures"], 12)
        self.assertEqual(report["group_count"], 1)
        self.assertEqual(report["groups"][0]["count"], 12)
        self.assertEqual(len(report["groups"][0]["sample_runs"]), 3)
        self.assertEqual(report["groups"][0]["status"], "observed")

    def test_distinct_workflows_and_conclusions_remain_separate(self):
        rows = [{"name": "A", "conclusion": "failure"}, {"name": "A", "conclusion": "timed_out"}, {"name": "B", "conclusion": "failure"}]
        self.assertEqual(build_triage(rows)["group_count"], 3)

    def test_rejects_malformed_evidence(self):
        for rows in ({}, [None], [{"name": []}], [{"conclusion": 12}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                build_triage(rows)

    def test_summary_does_not_claim_root_cause_or_resolution(self):
        summary = render_summary(build_triage([{"name": "A", "conclusion": "failure", "id": 7}]))
        self.assertIn("does not prove shared root cause", summary)
        self.assertIn("No issues, comments, PRs", summary)

    def test_cli_preserves_counts_and_writes_json_and_summary(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            inp, out, summary = (base / name for name in ("failures.json", "triage.json", "triage.md"))
            inp.write_text(json.dumps([{"name": "A", "conclusion": "failure", "id": 7}]))
            subprocess.run([sys.executable, "tools/actions_failure_triage.py", "--input", str(inp), "--output", str(out), "--summary", str(summary)], check=True)
            self.assertEqual(json.loads(out.read_text())["observed_failures"], 1)
            self.assertIn("Read-only", summary.read_text())


if __name__ == "__main__":
    unittest.main()
