import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from buddy.learning.registered_runner import process_events


class RegisteredRunnerTest(unittest.TestCase):
    def test_registered_runner_processes_evidence(self):
        root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            events = temp_path / "events.json"
            out = temp_path / "evidence.json"
            events.write_text(json.dumps({"events": [{
                "event_id": "e1", "event_type": "benchmark", "capability": "coding",
                "success": True, "verified": True, "regression_passed": True, "safety_passed": True
            }]}))
            subprocess.run([sys.executable, str(root / "registered_runner.py"), "--events", str(events), "--out", str(out)], check=True)
            result = json.loads(out.read_text())
            self.assertEqual(result["events_processed"], 1)
            self.assertEqual(result["promotions"], 0)


    def test_invalid_capability_identity_cannot_enter_evidence(self):
        for capability in (None, False, 17, [], {}, "", " \t "):
            with self.subTest(capability=capability):
                with self.assertRaisesRegex(ValueError, "capability must be a nonempty string"):
                    process_events([{
                        "event_id": "e1", "event_type": "benchmark", "capability": capability,
                        "success": True, "verified": True, "regression_passed": True, "safety_passed": True,
                    }])

    def test_valid_workflow_capability_stays_diagnostic_not_promoted(self):
        result = process_events([{
            "event_id": "workflow:fixture", "event_type": "tool_outcome",
            "capability": "workflow_connection", "success": True,
            "verified": False, "regression_passed": False, "safety_passed": True,
        }])
        self.assertEqual(result[0]["capability"], "workflow_connection")
        self.assertTrue(result[0]["learn"])
        self.assertFalse(result[0]["promote"])
