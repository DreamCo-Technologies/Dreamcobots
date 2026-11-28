"""High-level permissioned orchestration."""
from .intake.router import route_artifact
from .policy_gate import PolicyGate
from .parsers.code import parse_python
from .parsers.treesitter import parse_tree_sitter
from .parsers.api import parse_har,parse_openapi_json
from .parsers.data import parse_csv,parse_json_data
from .spec_builder.builder import build_blueprint

def analyze(filename,content,permission,system_name,purpose=""):
    gate=PolicyGate().authorize_and_scrub(content,permission)
    if not gate.allowed:raise PermissionError(gate.reason)
    artifact=route_artifact(filename,gate.sanitized_content,permission)
    parsers={"python_source":parse_python,"openapi_json":parse_openapi_json,"har":parse_har,"csv":parse_csv,"json":parse_json_data}
    language={"javascript_source":"javascript","typescript_source":"typescript","java_source":"java","go_source":"go","rust_source":"rust"}.get(artifact["artifact_type"])
    if language:parsed=parse_tree_sitter(artifact["content"],language)
    else:
        if artifact["artifact_type"]=="openapi_yaml":raise NotImplementedError("Safe YAML adapter is not installed; parser is disabled.")
        parser=parsers.get(artifact["artifact_type"])
        if parser is None:raise ValueError("Unsupported artifact type: "+artifact["artifact_type"])
        parsed=parser(artifact["content"])
    blueprint=build_blueprint(parsed,system_name,purpose)
    blueprint["policy"]={"authorized":True,"redaction_findings":gate.findings,"source_content_persisted":False}
    blueprint["parser_warnings"]=parsed.get("warnings",[])
    return blueprint
