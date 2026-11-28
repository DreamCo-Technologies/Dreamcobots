import json,subprocess,sys,pathlib
import pytest
ROOT=pathlib.Path(__file__).resolve().parents[1]

def run(module,source,target,*args):
    return subprocess.run([sys.executable,"-m",module,"--input",str(source),"--output",str(target),*args],cwd=ROOT,capture_output=True,text=True)

def dump(path,obj):
    path.write_text(json.dumps(obj))

def test_five_stage_cli_happy_path(tmp_path):
    raw=tmp_path/"raw.json"; manifest=tmp_path/"manifest.json"; parsed=tmp_path/"parsed.json"; spec=tmp_path/"spec.json"; course=tmp_path/"course.json"
    dump(raw,{"job_id":"pipeline-test-01","artifact_type":"python","content":"def add(left,right):\n return left+right\n","permission":{"authorized":True,"target_kind":"user_owned"}})
    assert run("stages.01_policy_gate",raw,manifest).returncode==0
    assert run("stages.02_intake_parser",manifest,parsed).returncode==0
    assert run("stages.03_spec_and_onet",parsed,spec).returncode==0
    assert run("stages.04_clean_room_gen",spec,course,"--mock").returncode==0
    result=json.loads(course.read_text())
    assert result["schema_version"]=="dreamco.course_module.v1"
    assert result["provenance"]["generation_mode"]=="mock"

def test_policy_blocks_missing_permission(tmp_path):
    raw=tmp_path/"raw.json"; out=tmp_path/"out.json"
    dump(raw,{"content":"hello","permission":{}})
    result=run("stages.01_policy_gate",raw,out)
    assert result.returncode==2
    assert json.loads(out.read_text())["policy"]["audit_code"]=="PERMISSION_REQUIRED"

def test_policy_redacts_secrets_and_pii(tmp_path):
    raw=tmp_path/"raw.json"; out=tmp_path/"out.json"
    dump(raw,{"content":"AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF email joe@example.com SSN 123-45-6789","permission":{"authorized":True,"target_kind":"user_owned"}})
    assert run("stages.01_policy_gate",raw,out).returncode==0
    sanitized=json.loads(out.read_text())["sanitized_text"]
    assert "AKIA1234567890ABCDEF" not in sanitized
    assert "joe@example.com" not in sanitized and "123-45-6789" not in sanitized

def test_policy_blocks_prohibited_access(tmp_path):
    raw=tmp_path/"raw.json"; out=tmp_path/"out.json"
    dump(raw,{"content":"x","permission":{"authorized":True,"target_kind":"user_owned","drm_circumvention":True}})
    assert run("stages.01_policy_gate",raw,out).returncode==2
    assert json.loads(out.read_text())["policy"]["audit_code"]=="PROHIBITED_ACCESS"

def test_parser_never_executes_uploaded_python(tmp_path):
    marker=tmp_path/"executed"; raw=tmp_path/"raw.json"; manifest=tmp_path/"manifest.json"; parsed=tmp_path/"parsed.json"
    dump(raw,{"artifact_type":"python","content":f"open('{marker}','w').write('unsafe')","permission":{"authorized":True,"target_kind":"user_owned"}})
    assert run("stages.01_policy_gate",raw,manifest).returncode==0
    assert run("stages.02_intake_parser",manifest,parsed).returncode==0
    assert not marker.exists()

def test_spec_uses_abstract_operation_names(tmp_path):
    parsed=tmp_path/"parsed.json"; spec_path=tmp_path/"spec.json"
    dump(parsed,{"schema_version":"dreamco.parsed_facts.v1","job_id":"abc12345","artifact_type":"code","source_sha256":"0"*64,"facts":{"functions":[{"arity":2}],"control_flow":[]}})
    assert run("stages.03_spec_and_onet",parsed,spec_path).returncode==0
    text=spec_path.read_text()
    assert "customerSecretFunctionName" not in text and "operation_1" in text

def test_generator_requires_explicit_mock_and_source_free_spec(tmp_path):
    spec=tmp_path/"spec.json"; out=tmp_path/"course.json"
    dump(spec,{"schema_version":"dreamco.functional_spec.v1","job_id":"abc12345","system_label":"user_system","inputs":[],"outputs":[],"state_rules":[],"edge_cases":[],"onet_tasks":[],"clean_room":{"original_source_available":False,"source_identifiers_removed":True,"generator_input":"functional_spec_only"}})
    assert run("stages.04_clean_room_gen",spec,out).returncode!=0
    assert run("stages.04_clean_room_gen",spec,out,"--mock").returncode==0


def test_generator_rejects_specs_with_source_identifiers(tmp_path):
    spec=tmp_path/"spec.json"; out=tmp_path/"course.json"
    dump(spec,{"schema_version":"dreamco.functional_spec.v1","job_id":"abc12345","system_label":"user_system","inputs":[],"outputs":[],"state_rules":[],"edge_cases":[],"onet_tasks":[],"clean_room":{"original_source_available":False,"source_identifiers_removed":False,"generator_input":"functional_spec_only"}})
    result=run("stages.04_clean_room_gen",spec,out,"--mock")
    assert result.returncode!=0

def test_static_parsers_cover_openapi_har_and_csv():
    from importlib import import_module
    parse = import_module("stages.02_intake_parser.__main__").parse
    openapi=parse('{"openapi":"3.0.0","paths":{"/items":{"get":{},"post":{}}}}',"openapi_json")
    assert [(endpoint["method"],endpoint["path"]) for endpoint in openapi["endpoints"]]==[("GET","/items"),("POST","/items")]
    assert openapi["endpoints"][0]["response_codes"]==[]
    har=parse('{"log":{"entries":[{"request":{"method":"GET","url":"https://example.test/orders?token=secret"},"response":{"status":200,"headers":[{"name":"X-RateLimit-Remaining","value":"42"}]}}]}}',"har")
    assert har["endpoints"][0]["method"]=="GET" and har["endpoints"][0]["path"]=="/orders" and har["endpoints"][0]["status"]==200
    assert har["endpoints"][0]["response_header_names"]==["x-ratelimit-remaining"]
    assert "secret" not in json.dumps(har) and "42" not in json.dumps(har)
    csv=parse("id,name\n1,A\n2,B\n","csv")
    assert csv["row_count"]==2 and csv["columns"][0]["name"]=="field_1"

def test_local_onet_catalog_is_read_only_and_deterministic(tmp_path):
    import sqlite3
    from importlib import import_module
    database=tmp_path/"onet.sqlite"
    connection=sqlite3.connect(database)
    connection.execute("CREATE TABLE onet_tasks (soc_code TEXT, task_id TEXT, task TEXT)")
    connection.execute("INSERT INTO onet_tasks VALUES (?,?,?)",("15-1252.00","task-1","Develop software applications and analyze user requirements"))
    connection.commit(); connection.close()
    match=import_module("stages.03_spec_and_onet.onet").match_onet_tasks
    result=match("software applications user requirements",str(database))
    assert result[0]["onet_soc_code"]=="15-1252.00"
    assert result[0]["human_required"] is True

def test_training_export_rejects_nan_similarity():
    import math
    from stages.training_export import verified_record
    spec={"schema_version":"dreamco.functional_spec.v1","job_id":"x","system_label":"x","inputs":[],"outputs":[],"state_rules":[],"edge_cases":[],"onet_tasks":[],"clean_room":{"original_source_available":False,"source_identifiers_removed":True,"generator_input":"functional_spec_only"}}
    course={"schema_version":"dreamco.course_module.v1","job_id":"x","module_title":"x","learning_objectives":["x"],"reference_implementation":{"language":"python","files":[{"path":"solution.py","content":"pass"}]},"tests":[{"path":"test.py","content":"def test_x(): assert True"}],"challenges":[{"step":1,"instruction":"x","success_criteria":"x"}],"provenance":{"model_id":"mock","model_license":"DreamCo-Proprietary","source_onet_id":None,"generation_mode":"mock"}}
    report={"schema_version":"dreamco.eval_report.v1","job_id":"x","status":"PASS","tests_passed":True,"similarity_score":float("nan"),"policy_check":"PASS","sandbox":{"network_disabled":True,"rootless_requested":True,"timed_out":False,"exit_code":0}}
    with pytest.raises(PermissionError): verified_record(spec,course,report)

def test_policy_blocks_localhost_target(tmp_path):
    raw=tmp_path/"raw.json"; out=tmp_path/"out.json"
    dump(raw,{"content":"public api spec","source_url":"http://127.0.0.1/admin","permission":{"authorized":True,"target_kind":"public_api"}})
    assert run("stages.01_policy_gate",raw,out).returncode==2
    assert json.loads(out.read_text())["policy"]["audit_code"]=="RESTRICTED_DOMAIN"

def test_policy_rejects_zip_bomb_metadata(tmp_path):
    import base64,io,zipfile
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,"w",compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("payload.txt","A"*(2*1024*1024))
    raw=tmp_path/"raw.json"; out=tmp_path/"out.json"
    dump(raw,{"content":"archive intake","archive_base64":base64.b64encode(buffer.getvalue()).decode(),"permission":{"authorized":True,"target_kind":"user_owned"}})
    assert run("stages.01_policy_gate",raw,out).returncode==2
    assert json.loads(out.read_text())["policy"]["audit_code"]=="ARCHIVE_LIMIT_EXCEEDED"


def test_non_python_languages_use_tree_sitter_not_python_ast(monkeypatch):
    import sys
    from types import ModuleType
    from importlib import import_module
    calls=[]
    fake=ModuleType("reverse_engineer.parsers.treesitter")
    def fake_parse(source,language):
        calls.append(language)
        return {"facts":{"functions":[{"parameter_node_count":2}],"control_flow":[],"dependencies":["sample"]}}
    fake.parse_tree_sitter=fake_parse
    monkeypatch.setitem(sys.modules,"reverse_engineer.parsers.treesitter",fake)
    parse=import_module("stages.02_intake_parser.__main__").parse
    expected={"javascript_source":"javascript","typescript_source":"typescript","java_source":"java","go_source":"go","rust_source":"rust"}
    for kind,language in expected.items():
        result=parse("not valid Python syntax: {",kind)
        assert result["language"]==language
        assert result["functions"]==[{"arity":2}]
    assert calls==list(expected.values())


def test_har_parser_redacts_dynamic_path_identifiers():
    from importlib import import_module
    parse=import_module("stages.02_intake_parser.__main__").parse
    har={"log":{"entries":[
        {"request":{"method":"GET","url":"https://api.example.test/users/123456/orders/550e8400-e29b-41d4-a716-446655440000?token=private"},"response":{"status":200}},
        {"request":{"method":"GET","url":"https://api.example.test/accounts/person@example.com"},"response":{"status":200}}
    ]}}
    result=parse(json.dumps(har),"har")
    paths=[item["path"] for item in result["endpoints"]]
    assert paths==["/users/{id}/orders/{id}","/accounts/{id}"]
    assert "123456" not in json.dumps(result)
    assert "person@example.com" not in json.dumps(result)


def test_har_parser_does_not_retain_arbitrary_content_type_header_values():
    from importlib import import_module
    parse=import_module("stages.02_intake_parser.__main__").parse
    har={"log":{"entries":[
        {"request":{"method":"POST","url":"https://api.example.test/items","headers":[{"name":"Content-Type","value":"application/json; boundary=private@example.com"}]},"response":{"status":200,"headers":[{"name":"Content-Type","value":"person@example.com"}]}}
    ]}}
    result=parse(json.dumps(har),"har")
    endpoint=result["endpoints"][0]
    assert endpoint["request_content_type"]=="application/json"
    assert endpoint["response_content_type"]=="unspecified"
    assert "private@example.com" not in json.dumps(result)
    assert "person@example.com" not in json.dumps(result)


def test_stage_paths_reject_external_ci_paths_without_test_context(tmp_path, monkeypatch):
    from stages.common import safe_stage_path
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    with pytest.raises(ValueError):
        safe_stage_path(tmp_path / "outside.json")


def test_stage_paths_allow_repo_paths_and_pytest_temp_paths(tmp_path, monkeypatch):
    from stages.common import REPO_ROOT, safe_stage_path
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/test_pipeline_stages.py::test")
    assert safe_stage_path(REPO_ROOT / "reports" / "out.json") == REPO_ROOT / "reports" / "out.json"
    assert safe_stage_path(tmp_path / "fixture.json") == tmp_path / "fixture.json"
