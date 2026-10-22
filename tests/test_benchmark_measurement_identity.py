"""Reject duplicate or malformed measurement identities without discarding legitimate gaps."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/benchmark_gap_closure.py"


def run_case(tmp_path, data):
    source = tmp_path / "in.json"
    output = tmp_path / "out.json"
    source.write_text(json.dumps(data))
    proc = subprocess.run([sys.executable, str(SCRIPT), str(source), "--output", str(output)],
                          cwd=tmp_path, capture_output=True, text=True)
    return proc, output


def test_duplicate_identity_rejected_for_records_object(tmp_path):
    item = {"division_id": "d1", "benchmark_id": "reasoning", "baseline": 50, "target": 80}
    proc, output = run_case(tmp_path, {"records": [item, item]})
    assert proc.returncode != 0
    assert not output.exists()


def test_duplicate_identity_rejected_for_raw_list(tmp_path):
    a = {"division_id": 1, "benchmark_id": "coding", "baseline": 60, "target": 80}
    b = {"division_id": "1", "benchmark_id": "coding", "baseline": 80, "target": 80}
    proc, output = run_case(tmp_path, [a, b])
    assert proc.returncode != 0
    assert not output.exists()


def test_distinct_measurements_remain_supported(tmp_path):
    rows = [
        {"division_id": "d1", "benchmark_id": "reasoning", "baseline": 50, "target": 80},
        {"division_id": "d1", "benchmark_id": "coding", "baseline": 60, "target": 80},
    ]
    proc, output = run_case(tmp_path, {"records": rows})
    assert proc.returncode == 0, proc.stderr
    assert [r["status"] for r in json.loads(output.read_text())["records"]] == ["open", "open"]


def test_malformed_measurement_fails_closed(tmp_path):
    proc, output = run_case(tmp_path, {"records": [None]})
    assert proc.returncode != 0
    assert not output.exists()


def test_present_but_null_identity_fails_closed(tmp_path):
    proc, output = run_case(tmp_path, {"records": [{"division_id": "d1", "benchmark_id": None, "baseline": 40, "target": 50}]})
    assert proc.returncode != 0
    assert not output.exists()


def test_missing_identity_stays_visibly_blocked(tmp_path):
    proc, output = run_case(tmp_path, {"records": [{"division_id": "d1", "baseline": 40, "target": 50}]})
    assert proc.returncode == 0
    assert json.loads(output.read_text())["records"][0]["status"] == "blocked"
