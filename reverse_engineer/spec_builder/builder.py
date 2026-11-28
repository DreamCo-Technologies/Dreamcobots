"""Build a source-minimized functional blueprint."""
import hashlib

def build_blueprint(parsed,system_name,purpose=""):
    facts=parsed["facts"]; typ=parsed["artifact_type"]; inputs=[]; outputs=[]; transitions=[]; rules=[]; edges=list(parsed.get("warnings",[])); deps=facts.get("dependencies",[])
    if typ=="code":
        inputs=[{"name":f["name"],"parameters":f.get("parameters",[]),"parameter_count":f.get("parameter_node_count",len(f.get("parameters",[]))),"kind":f["kind"]} for f in facts.get("functions",[])]
        outputs=[{"operation":f["name"],"return_annotation_present":f["returns_annotation_present"]} for f in facts.get("functions",[])]
        transitions=facts.get("control_flow",[]); rules=[{"rule":"Reimplement behavior only from approved abstract contracts and owner-provided examples.","verification":"fixture_required"}]
        edges.append("Static analysis cannot infer runtime side effects, dynamic behavior or external service behavior.")
    elif typ=="api":
        inputs=[{"endpoint":e["path"],"method":e["method"]} for e in facts.get("endpoints",[])]
        outputs=[{"endpoint":e["path"],"method":e["method"],"response_codes":e.get("response_codes",e.get("status_codes",[]))} for e in facts.get("endpoints",[])]
        rules=[{"rule":"Implement documented contracts only where authorized examples establish behavior.","verification":"contract_fixture_required"}]
        edges.append("Authentication, authorization and rate limits require explicit owner-supplied specification.")
    elif typ=="data":
        inputs=[{"name":c["name"],"types":c["inferred_types"],"nullable":c["null_count"]>0} for c in facts.get("columns",[])]
        outputs=[{"schema":c["name"]} for c in facts.get("columns",[])]
        rules=[{"rule":"Treat inferred types and candidate keys as hypotheses until owner confirmation.","verification":"schema_fixture_required"}]
        edges.append("No row values or personal data are included in the blueprint.")
    else:edges.append("Unsupported artifact type.")
    onet=[{"task_family":"software_requirements_analysis","onet_soc_code":None,"match_basis":"functional decomposition","actor":"AI_assisted_human_review","confidence":"low","human_required":True,"review_note":"Resolve exact identifiers against an authorized current O*NET dataset; no official code is asserted."}]
    return {"schema_version":"dreamco.reverse_engineering.blueprint.v1","artifact_type":typ,"language":facts.get("language"),"system_name":system_name,"purpose":purpose,"inputs":inputs,"outputs":outputs,"state_transitions":transitions,"business_rules":rules,"edge_cases":edges,"dependencies":deps,"onet_mapping":onet,"provenance":{"parser":"deterministic","facts_keys_sha256":hashlib.sha256(repr(sorted(facts.keys())).encode()).hexdigest(),"source_content_embedded":False},"clean_room_constraints":{"source_code_available_to_generator":False,"generator_input":"blueprint_only","no_security_bypass":True,"owner_review_required":True}}
