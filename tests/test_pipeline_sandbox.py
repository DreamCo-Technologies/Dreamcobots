import pytest
from importlib import import_module\n_sandbox=import_module("stages.05_sandbox_verifier.__main__")\ndocker_command=_sandbox.docker_command\nsimilarity=_sandbox.similarity
from stages.training_export import verified_record
def test_sandbox_is_rootless_network_isolated_and_resource_limited():
    cmd=docker_command("/tmp/work")
    assert "--network" in cmd and cmd[cmd.index("--network")+1]=="none"
    assert "--read-only" in cmd and "--cap-drop=ALL" in cmd and "--pids-limit" in cmd
    assert "--memory" in cmd and "--cpus" in cmd and "--user" in cmd
def test_similarity_flags_identical_source():
    assert similarity("def same(): pass","def same(): pass")==1.0
def test_training_export_fails_closed():
    with pytest.raises(PermissionError):
        verified_record({},{"reference_implementation":{"files":[]}},{"job_id":"x","status":"FAIL","tests_passed":False,"policy_check":"PASS","similarity_score":0.0})
def test_training_export_omits_reasoning():
    record=verified_record({"inputs":[]},{"provenance":{"model_id":"mock"},"reference_implementation":{"files":[{"path":"solution.py","content":"pass"}]}},{"job_id":"x","status":"PASS","tests_passed":True,"policy_check":"PASS","similarity_score":0.1})
    assert "reasoning" not in record and record["test_pass"] is True
