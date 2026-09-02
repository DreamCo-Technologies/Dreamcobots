import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


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
            self.assertEqual(result["promotions"], 1)
