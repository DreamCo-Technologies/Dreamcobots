import json,subprocess,sys
import pytest
from importlib import import_module
from stages.training_export import verified_record
_sandbox=import_module("stages.05_sandbox_verifier.__main__")
docker_command=_sandbox.docker_command
similarity=_sandbox.similarity

def test_sandbox_command_enforces_isolation_and_limits():
    cmd=docker_command("/tmp/work")
    assert cmd[cmd.index("--network")+1]=="none"
    assert "--read-only" in cmd and "--cap-drop=ALL" in cmd
    assert "--pids-limit" in cmd and "--memory" in cmd and "--memory-swap" in cmd and "--cpus" in cmd
    assert cmd[cmd.index("--user")+1]=="65532:65532"

def test_similarity_flags_identical_source():
    assert similarity("def same(): pass","def same(): pass")==1.0

def test_training_export_fails_closed():
    with pytest.raises(PermissionError):
        verified_record({},{"reference_implementation":{"files":[]}},{"job_id":"x","status":"FAIL","tests_passed":False,"policy_check":"PASS","similarity_score":0.0})

def test_training_export_omits_hidden_reasoning():
    record=verified_record(
      {"schema_version":"dreamco.functional_spec.v1","job_id":"x","system_label":"x","inputs":[],"outputs":[],"state_rules":[],"edge_cases":[],"onet_tasks":[],"clean_room":{"original_source_available":False,"source_identifiers_removed":True,"generator_input":"functional_spec_only"}},
      {"schema_version":"dreamco.course_module.v1","job_id":"x","module_title":"x","learning_objectives":["x"],"reference_implementation":{"language":"python","files":[{"path":"solution.py","content":"pass"}]},"tests":[{"path":"test_solution.py","content":"def test_x(): assert True"}],"challenges":[{"step":1,"instruction":"x","success_criteria":"x"}],"provenance":{"model_id":"mock","model_license":"DreamCo-Proprietary","source_onet_id":None,"generation_mode":"mock"}},
      {"schema_version":"dreamco.eval_report.v1","job_id":"x","status":"PASS","tests_passed":True,"similarity_score":0.1,"policy_check":"PASS","sandbox":{"network_disabled":True,"rootless_requested":True,"timed_out":False,"exit_code":0}})
    assert "reasoning" not in record and record["test_pass"] is True

def test_stage_five_blocks_without_similarity_reference(tmp_path):
    course=tmp_path/"course.json"; report=tmp_path/"report.json"
    course.write_text(json.dumps({"schema_version":"dreamco.course_module.v1","job_id":"verify-test","module_title":"x","learning_objectives":["x"],"reference_implementation":{"language":"python","files":[{"path":"solution.py","content":"pass"}]},"tests":[{"path":"test_solution.py","content":"def test_ok(): assert True"}],"challenges":[{"step":1,"instruction":"x","success_criteria":"x"}],"provenance":{"model_id":"mock","model_license":"DreamCo-Proprietary","source_onet_id":None,"generation_mode":"mock"}}))
    result=subprocess.run([sys.executable,"-m","stages.05_sandbox_verifier","--input",str(course),"--output",str(report)],capture_output=True,text=True)
    assert result.returncode==2
    saved=json.loads(report.read_text())
    assert saved["status"]=="BLOCKED" and saved["policy_check"]=="FAIL" and not saved["tests_passed"]

def test_training_export_rejects_nan_similarity():
    import math
    spec={"schema_version":"dreamco.functional_spec.v1","job_id":"x","system_label":"x","inputs":[],"outputs":[],"state_rules":[],"edge_cases":[],"onet_tasks":[],"clean_room":{"original_source_available":False,"source_identifiers_removed":True,"generator_input":"functional_spec_only"}}
    course={"schema_version":"dreamco.course_module.v1","job_id":"x","module_title":"x","learning_objectives":["x"],"reference_implementation":{"language":"python","files":[{"path":"solution.py","content":"pass"}]},"tests":[{"path":"test.py","content":"def test_x(): assert True"}],"challenges":[{"step":1,"instruction":"x","success_criteria":"x"}],"provenance":{"model_id":"mock","model_license":"DreamCo-Proprietary","source_onet_id":None,"generation_mode":"mock"}}
    report={"schema_version":"dreamco.eval_report.v1","job_id":"x","status":"PASS","tests_passed":True,"similarity_score":float("nan"),"policy_check":"PASS","sandbox":{"network_disabled":True,"rootless_requested":True,"timed_out":False,"exit_code":0}}
    with pytest.raises(PermissionError): verified_record(spec,course,report)
