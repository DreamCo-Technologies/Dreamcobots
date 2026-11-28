import json,subprocess,sys,pathlib
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
    dump(spec,{"schema_version":"dreamco.functional_spec.v1","job_id":"abc12345","system_label":"user_system","inputs":[],"outputs":[],"state_rules":[],"edge_cases":[],"onet_tasks":[],"clean_room":{"original_source_available":False}})
    assert run("stages.04_clean_room_gen",spec,out).returncode!=0
    assert run("stages.04_clean_room_gen",spec,out,"--mock").returncode==0

def test_static_parsers_cover_openapi_har_and_csv():
    from importlib import import_module
    parse = import_module("stages.02_intake_parser.__main__").parse
    openapi=parse('{"openapi":"3.0.0","paths":{"/items":{"get":{},"post":{}}}}',"openapi_json")
    assert openapi=={"endpoints":[{"method":"GET","path":"/items"},{"method":"POST","path":"/items"}]}
    har=parse('{"log":{"entries":[{"request":{"method":"GET","url":"https://example.test/orders?token=secret"},"response":{"status":200}}]}}',"har")
    assert har["endpoints"]==[{"method":"GET","path":"/orders","status":200}]
    csv=parse("id,name\\n1,A\\n2,B\\n","csv")
    assert csv["row_count"]==2 and csv["columns"][0]["name"]=="field_1"
