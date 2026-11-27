import unittest

from tools.build_buddy_failure_observations import build_observations, build_report


class BuddyFailureObservationTests(unittest.TestCase):
    def test_ignores_successful_and_skipped_jobs(self):
        run = {"id": 7, "name": "CI", "conclusion": "failure", "jobs": [
            {"name": "passed", "conclusion": "success", "steps": []},
            {"name": "not-run", "conclusion": "skipped", "steps": []},
        ]}
        self.assertEqual(build_observations(run), [])

    def test_extracts_failed_step_without_copying_logs(self):
        run = {"id": 9, "name": "Actions Health", "url": "https://github.com/example/repo/actions/runs/9",
               "headSha": "a" * 40, "jobs": [
            {"name": "contract-tests", "conclusion": "failure", "steps": [
                {"name": "Checkout", "conclusion": "success"},
                {"name": "Validate inventory", "conclusion": "failure"},
            ]},
        ]}
        observations = build_observations(run)
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0]["failed_step"], "Validate inventory")
        self.assertEqual(observations[0]["run_id"], "9")
        self.assertNotIn("logs", observations[0])
        self.assertNotIn("stdout", observations[0])

    def test_report_includes_candidates_but_never_marks_them_verified(self):
        run = {"id": 10, "name": "Actions Health", "conclusion": "failure", "jobs": [
            {"name": "contract-tests", "conclusion": "failure", "steps": [
                {"name": "inventory mismatch", "conclusion": "failure"}]}
        ]}
        history = {"records": [{
            "commit": "b" * 40, "subject": "inventory mismatch repair",
            "search_terms": ["inventory", "mismatch"], "changed_paths": ["tools/inventory.py"],
            "test_paths": ["tests/test_inventory.py"], "verified_fix": False,
            "training_eligible": False,
        }]}
        report = build_report(run, history, {"incidents": []})
        self.assertEqual(report["observation_count"], 1)
        candidate = report["recommendations"][0]["recommendation"]["historical_candidates"][0]
        self.assertFalse(candidate["verified_fix"])
        self.assertFalse(candidate["auto_apply_allowed"])
        self.assertFalse(report["policy"]["incident_memory_written"])


if __name__ == "__main__":
    unittest.main()
