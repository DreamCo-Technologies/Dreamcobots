"""Original scaffold generator. Its only input is an abstract blueprint."""
import json,re

def build_generation_request(blueprint):
    if blueprint.get("clean_room_constraints",{}).get("source_code_available_to_generator") is not False:raise ValueError("Clean-room invariant violated.")
    safe=dict(blueprint); safe.pop("provenance",None)
    return "Create a wholly original implementation from this abstract blueprint. Do not imitate or request source code. Include validation, error handling, pytest contracts and a human-review checklist. Do not claim equivalence without evidence.\n"+json.dumps(safe,sort_keys=True)
def generate_python_scaffold(blueprint):
    name=re.sub(r"[^a-zA-Z0-9_]+","_",str(blueprint.get("system_name","dreamco_service"))).strip("_").lower() or "dreamco_service"
    methods=[]
    for item in blueprint.get("inputs",[]):
        raw=item.get("name") or item.get("operation") or item.get("endpoint") or "execute"
        method=re.sub(r"[^a-zA-Z0-9_]+","_",str(raw)).strip("_").lower() or "execute"
        methods.append("    def "+method+"(self, payload: dict) -> dict:\n        raise NotImplementedError('Implement from approved contract fixtures.')")
    if not methods:methods=["    def execute(self, payload: dict) -> dict:\n        raise NotImplementedError('Implement from approved contract fixtures.')"]
    module='"""Original DreamCo scaffold; implement from approved contracts only."""\n\nclass Service:\n'+"\n".join(methods)+"\n"
    tests='"""Owner-approved contract tests."""\ndef test_service_imports():\n    from '+name+'.service import Service\n    assert Service is not None\n'
    return {name+"/__init__.py":'"""Clean-room service package."""\n',name+"/service.py":module,"tests/test_"+name+"_contracts.py":tests}
