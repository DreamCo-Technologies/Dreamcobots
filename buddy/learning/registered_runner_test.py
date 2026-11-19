import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class RegisteredRunnerTest(unittest.TestCase):
    def run_events(self, events):
        root = Path(__file__).resolve().parent
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        temp_path = Path(temp_dir.name)
        events_path = temp_path / "events.json"
        output_path = temp_path / "evidence.json"
        events_path.write_text(json.dumps({"events": events}), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(root / "registered_runner.py"),
             "--events", str(events_path), "--out", str(output_path)],
            capture_output=True,
            text=True,
        )
        return result, output_path

    def valid_event(self):
        return {
            "event_id": "e1",
            "event_type": "benchmark",
            "capability": "coding",
            "success": True,
            "verified": True,
            "regression_passed": True,
            "safety_passed": True,
            "external_assistance": False,
            "evidence_refs": ["artifact://runs/run-1/evidence.json"],
            "run_id": "run-1",
            "commit_sha": "a" * 40,
            "baseline_ref": "artifact://runs/run-1/baseline.json",
            "holdout_ref": "artifact://runs/run-1/holdout.json",
            "regression_ref": "artifact://runs/run-1/regression.json",
            "safety_ref": "artifact://runs/run-1/safety.json",
        }

    def test_registered_runner_promotes_only_complete_provenance(self):
        result, output_path = self.run_events([self.valid_event()])
        self.assertEqual(result.returncode, 0, result.stderr)
        evidence = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(evidence["events_processed"], 1)
        self.assertEqual(evidence["promotions"], 1)
        self.assertEqual(evidence["results"][0]["run_id"], "run-1")
        self.assertEqual(evidence["results"][0]["evidence_refs"], ["artifact://runs/run-1/evidence.json"])

    def test_registered_runner_keeps_missing_provenance_unpromoted(self):
        event = self.valid_event()
        event["holdout_ref"] = ""
        result, output_path = self.run_events([event])
        self.assertEqual(result.returncode, 0, result.stderr)
        evidence = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(evidence["promotions"], 0)
        self.assertIn("holdout_ref", evidence["results"][0]["reason"])

    def test_registered_runner_rejects_truthy_string_booleans(self):
        event = self.valid_event()
        event["verified"] = "false"
        result, _ = self.run_events([event])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("verified must be a JSON boolean", result.stderr)


if __name__ == "__main__":
    unittest.main()
