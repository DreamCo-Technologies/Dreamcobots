import argparse
from ..common import parser,read_json,write_json,validate
from .onet import match_onet_tasks

def build(parsed,task_description="",onet_db=None):
    facts=parsed["facts"]; typ=parsed["artifact_type"]; inputs=[]; outputs=[]; rules=[]; edges=[]
    if typ=="code":
        funcs=facts.get("functions",[])
        inputs=[{"operation":"operation_"+str(i+1),"argument_count":f.get("arity",0)} for i,f in enumerate(funcs)]
        outputs=[{"operation":"operation_"+str(i+1),"result_type":"unspecified"} for i,_ in enumerate(funcs)]
        rules=[{"rule":"Implement only abstract operation contracts using owner-approved examples.","verification":"fixture_required"}]
        edges=["Runtime effects and dynamic dispatch are not inferred."]
    elif typ=="api":
        endpoints=facts.get("endpoints",[])
        inputs=[{"operation":"endpoint_"+str(i+1),"method":e.get("method","UNKNOWN"),"path_template":"/abstract/endpoint_"+str(i+1)} for i,e in enumerate(endpoints)]
        outputs=[{"operation":"endpoint_"+str(i+1),"status_code":e.get("status")} for i,e in enumerate(endpoints)]
        rules=[{"rule":"Implement documented public contract only.","verification":"contract_fixture_required"}]
    else:
        columns=facts.get("columns",[])
        inputs=[{"field":"field_"+str(i+1),"types":c.get("inferred_types",[]),"nullable":c.get("null_count",0)>0} for i,c in enumerate(columns)]
        outputs=[{"field":"field_"+str(i+1),"schema_only":True} for i,_ in enumerate(columns)]
        rules=[{"rule":"Treat inferred types as hypotheses until owner confirmation.","verification":"schema_fixture_required"}]
        edges=["No source row values are retained."]
    onet=match_onet_tasks(task_description,onet_db) if onet_db else [{"task_family":"software_requirements_analysis","onet_soc_code":None,"actor":"AI_assisted_human_review","human_required":True,"confidence":"low","review_note":"No local O*NET database configured; no official occupation code is asserted."}]
    return {"schema_version":"dreamco.functional_spec.v1","job_id":parsed["job_id"],"system_label":"user_system_"+parsed["job_id"][:8],"inputs":inputs,"outputs":outputs,"state_rules":rules,"edge_cases":edges,"onet_tasks":onet,"clean_room":{"original_source_available":False,"source_identifiers_removed":True,"generator_input":"functional_spec_only"}}
def main():
    args=argparse.ArgumentParser(description="DreamCo Stage 3 abstract specification")
    args.add_argument("--input",required=True); args.add_argument("--output",required=True)
    args.add_argument("--onet-db"); args.add_argument("--task-description",default="")
    options=args.parse_args(); parsed=read_json(options.input)
    spec=build(parsed,options.task_description,options.onet_db)
    validate(spec,"functional_spec.schema.json"); write_json(options.output,spec)
if __name__=="__main__": main()
