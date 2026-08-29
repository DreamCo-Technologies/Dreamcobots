import json
import subprocess
import sys
from pathlib import Path


def test_registered_runner_processes_evidence(tmp_path):
    root = Path(__file__).resolve().parent
    events = tmp_path / "events.json"
    out = tmp_path / "evidence.json"
    events.write_text(json.dumps({"events": [{
        "event_id": "e1", "event_type": "benchmark", "capability": "coding",
        "success": True, "verified": True, "regression_passed": True, "safety_passed": True
    }]}))
    subprocess.run([sys.executable, str(root / "registered_runner.py"), "--events", str(events), "--out", str(out)], check=True)
    result = json.loads(out.read_text())
    assert result["events_processed"] == 1
    assert result["promotions"] == 1
