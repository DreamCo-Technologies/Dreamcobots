import json,os,pathlib,subprocess,sys
import pytest
pytestmark=pytest.mark.skipif(os.getenv("DREAMCO_RUN_ROOTLESS_DOCKER_TESTS")!="1",reason="requires an explicitly enabled rootless Docker integration environment")
ROOT=pathlib.Path(__file__).resolve().parents[1]
def invoke(tmp_path,solution,test_source,timeout=10):
    course=tmp_path/"course.json"; report=tmp_path/"report.json"; reference=tmp_path/"authorized-reference.txt"
    reference.write_text("abstract interface independent reference material unrelated to generated implementation")
    module={"schema_version":"dreamco.course_module.v1","job_id":"rootless-integration","module_title":"integration","learning_objectives":["test isolation"],"reference_implementation":{"language":"python","files":[{"path":"solution.py","content":solution}]},"tests":[{"path":"test_solution.py","content":test_source}],"challenges":[{"step":1,"instruction":"test","success_criteria":"sandbox"}],"provenance":{"model_id":"integration-fixture","model_license":"DreamCo-Proprietary","source_onet_id":None,"generation_mode":"test"}}
    course.write_text(json.dumps(module))
    return subprocess.run([sys.executable,"-m","stages.05_sandbox_verifier","--input",str(course),"--output",str(report),"--reference",str(reference),"--timeout",str(timeout)],cwd=ROOT,capture_output=True,text=True,timeout=timeout+8),report

def test_broken_generated_code_is_rejected(tmp_path):
    result,report=invoke(tmp_path,"def add(a,b): return a+b","from solution import add\ndef test_wrong(): assert add(1,2)==4")
    assert result.returncode==2
    assert json.loads(report.read_text())["status"]=="FAIL"

def test_infinite_loop_is_killed_and_reported(tmp_path):
    result,report=invoke(tmp_path,"def hang():\n while True: pass","from solution import hang\ndef test_hangs(): hang()",timeout=10)
    assert result.returncode==2
    saved=json.loads(report.read_text())
    assert saved["status"]=="FAIL" and saved["sandbox"]["timed_out"] is True
