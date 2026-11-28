import json,pytest
from reverse_engineer.intake.router import detect_artifact
from reverse_engineer.policy_gate import PolicyGate
from reverse_engineer.parsers.code import parse_python
from reverse_engineer.parsers.api import parse_openapi_json,parse_har
from reverse_engineer.parsers.data import parse_csv,parse_json_data
from reverse_engineer.spec_builder.builder import build_blueprint
from reverse_engineer.clean_room_gen.generator import build_generation_request,generate_python_scaffold
from reverse_engineer.service import analyze
OWNER={"authorized":True,"target_kind":"user_owned"}
def test_permission_and_bypass():
    gate=PolicyGate(); assert not gate.authorize_and_scrub("x",{}).allowed; assert not gate.authorize_and_scrub("x",{**OWNER,"bypass_requested":True}).allowed
def test_redaction():
    r=PolicyGate().authorize_and_scrub("api_key='TEST_FIXTURE_CREDENTIAL' email a@b.com 123-45-6789",OWNER); assert r.allowed; assert "sk-abcdefghijklmnopqrstuvwxyz" not in r.sanitized_content; assert "a@b.com" not in r.sanitized_content; assert "123-45-6789" not in r.sanitized_content
def test_open_source_license_gate():
    gate=PolicyGate(); assert not gate.authorize_and_scrub("x",{"authorized":True,"target_kind":"open_source"}).allowed
    assert gate.authorize_and_scrub("x",{"authorized":True,"target_kind":"open_source","license_id":"MIT"}).allowed
    assert not gate.authorize_and_scrub("x",{"authorized":True,"target_kind":"open_source","license_id":"UNKNOWN"}).allowed
def test_detection():
    assert detect_artifact("a.py","def f(): pass")=="python_source"; assert detect_artifact("api.json",'{"openapi":"3.0.0","paths":{}}')=="openapi_json"; assert detect_artifact("x.csv","id,name\n1,A")=="csv"
def test_python_ast():
    p=parse_python("def add(left,right):\n if left: return right\n"); assert p["facts"]["functions"][0]["parameters"]==["left","right"]; assert "source_text" not in p["facts"]
def test_openapi_and_har():
    p=parse_openapi_json(json.dumps({"openapi":"3.0.0","paths":{"/x":{"get":{"responses":{"200":{}}}}}})); assert p["facts"]["endpoints"][0]["method"]=="GET"
    h=parse_har(json.dumps({"log":{"entries":[{"request":{"method":"GET","url":"https://x.test/items?token=secret"},"response":{"status":200}}]}})); assert "token" not in json.dumps(h["facts"]); assert h["facts"]["endpoints"][0]["path"]=="/items"
def test_data_metadata_only():
    c=parse_csv("id,name\n1,Alice\n2,Bob\n"); assert "Alice" not in json.dumps(c["facts"]); assert c["facts"]["columns"][0]["name"]=="id"
    j=parse_json_data('[{"id":1},{"id":2}]'); assert j["facts"]["row_count"]==2
def test_blueprint_generator_is_source_free():
    p=parse_python("def hello(name): return name"); b=build_blueprint(p,"Greeting"); prompt=build_generation_request(b); assert "def hello(name)" not in prompt; assert "source_code_available_to_generator" in prompt; assert any(x.endswith("service.py") for x in generate_python_scaffold(b))
def test_generator_rejects_source_access():
    with pytest.raises(ValueError):build_generation_request({"clean_room_constraints":{"source_code_available_to_generator":True}})
def test_fixture_and_similarity():
    g=PolicyGate(); assert g.verify_equivalence([{"ok":True}],[{"ok":True}]).allowed; assert not g.verify_equivalence([1],[2]).allowed; assert not g.similarity_audit("def a(): return 1","def a(): return 1").allowed
def test_end_to_end():
    b=analyze("service.py","def create_item(name): return name",OWNER,"Inventory"); assert b["schema_version"]=="dreamco.reverse_engineering.blueprint.v1"; assert b["policy"]["source_content_persisted"] is False

def test_tree_sitter_blueprint_preserves_signature_metadata():
    parsed={"artifact_type":"code","facts":{"language":"typescript","functions":[{"name":"save","kind":"function","parameters":[],"parameter_node_count":3,"returns_annotation_present":True}],"control_flow":[],"dependencies":[]},"warnings":[]}
    blueprint=build_blueprint(parsed,"TypeScript service")
    assert blueprint["language"]=="typescript"
    assert blueprint["inputs"][0]["parameter_count"]==3
