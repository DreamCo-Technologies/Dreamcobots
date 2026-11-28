import pytest
from importlib import import_module
_sandbox = import_module("stages.05_sandbox_verifier.__main__")
docker_command = _sandbox.docker_command
similarity = _sandbox.similarity
from stages.training_export import verified_record

def test_sandbox_is_rootless_network_isolated_and_resource_limited():
    cmd = docker_command("/tmp/work")
    assert cmd[cmd.index("--network") + 1] == "none"
    assert "--read-only" in cmd and "--cap-drop=ALL" in cmd
    assert "--pids-limit" in cmd and "--memory" in cmd and "--cpus" in cmd
    assert cmd[cmd.index("--user") + 1] == "65532:65532"

def test_similarity_flags_identical_source():
    assert similarity("def same(): pass", "def same(): pass") == 1.0

def test_training_export_fails_closed():
    with pytest.raises(PermissionError):
        verified_record({}, {"reference_implementation":{"files":[]}}, {"job_id":"x","status":"FAIL","tests_passed":False,"policy_check":"PASS","similarity_score":0.0})

def test_training_export_omits_hidden_reasoning():
    record = verified_record({"inputs":[]}, {"provenance":{"model_id":"mock"},"reference_implementation":{"files":[{"path":"solution.py","content":"pass"}]}}, {"job_id":"x","status":"PASS","tests_passed":True,"policy_check":"PASS","similarity_score":0.1})
    assert "reasoning" not in record and record["test_pass"] is True

def test_stage_five_blocks_without_similarity_reference(tmp_path):
    import json,subprocess,sys
    course=tmp_path/"course.json"; report=tmp_path/"report.json"
    course.write_text(json.dumps({"job_id":"verify-test","reference_implementation":{"files":[{"path":"solution.py","content":"pass"}]},"tests":[{"path":"test_solution.py","content":"def test_ok(): assert True"}]}))
    result=subprocess.run([sys.executable,"-m","stages.05_sandbox_verifier","--input",str(course),"--output",str(report)],capture_output=True,text=True)
    assert result.returncode==2
    saved=json.loads(report.read_text())
    assert saved["status"]=="BLOCKED" and saved["policy_check"]=="FAIL" and not saved["tests_passed"]
