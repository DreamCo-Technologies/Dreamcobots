import argparse
from ..common import read_json,write_json,validate
from .onet import match_onet_tasks
def build(parsed,task_description="",onet_db=None):
 facts=parsed["facts"]; artifact_type=parsed["artifact_type"]; inputs=[]; outputs=[]; rules=[]; edge_cases=[]
 if artifact_type=="code":
  functions=facts.get("functions",[])
  inputs=[{"operation":"operation_"+str(index+1),"argument_count":function.get("arity",0)} for index,function in enumerate(functions)]
  outputs=[{"operation":"operation_"+str(index+1),"result_type":"unspecified"} for index,_ in enumerate(functions)]
  rules=[{"rule":"Implement only abstract operation contracts using owner-approved examples.","verification":"fixture_required"}]
  edge_cases=["Runtime effects and dynamic dispatch are not inferred."]
 elif artifact_type=="api":
  endpoints=facts.get("endpoints",[])
  inputs=[{"operation":"endpoint_"+str(index+1),"method":endpoint.get("method","UNKNOWN"),"path_template":"/abstract/endpoint_"+str(index+1),"parameter_count":endpoint.get("parameter_count",0),"request_content_types":endpoint.get("request_content_types",[endpoint.get("request_content_type","")]),"request_property_count":endpoint.get("request_property_count",0)} for index,endpoint in enumerate(endpoints)]
  outputs=[{"operation":"endpoint_"+str(index+1),"response_codes":endpoint.get("response_codes",[endpoint.get("status")]),"response_content_types":endpoint.get("response_content_types",[endpoint.get("response_content_type","")])} for index,endpoint in enumerate(endpoints)]
  rules=[{"rule":"Respect documented authentication and rate limits.","verification":"contract_fixture_required","auth_required":[endpoint.get("auth_required",False) for endpoint in endpoints],"rate_limit_hints":[endpoint.get("rate_limit_extensions",endpoint.get("response_header_names",[])) for endpoint in endpoints]}]
 else:
  columns=facts.get("columns",[])
  inputs=[{"field":"field_"+str(index+1),"types":column.get("inferred_types",[]),"nullable":column.get("null_count",0)>0,"candidate_primary_key":column.get("candidate_primary_key",False)} for index,column in enumerate(columns)]
  outputs=[{"field":"field_"+str(index+1),"schema_only":True} for index,_ in enumerate(columns)]
  rules=[{"rule":"Treat inferred types and candidate keys as hypotheses until owner confirmation.","verification":"schema_fixture_required"}]
  edge_cases=["No source row values are retained."]
 onet=match_onet_tasks(task_description,onet_db) if onet_db else [{"task_family":"software_requirements_analysis","onet_soc_code":None,"actor":"AI_assisted_human_review","human_required":True,"confidence":"low","review_note":"No local O*NET database configured; no official occupation code is asserted."}]
 return {"schema_version":"dreamco.functional_spec.v1","job_id":parsed["job_id"],"system_label":"user_system_"+parsed["job_id"][:8],"inputs":inputs,"outputs":outputs,"state_rules":rules,"edge_cases":edge_cases,"onet_tasks":onet,"clean_room":{"original_source_available":False,"source_identifiers_removed":True,"generator_input":"functional_spec_only"}}
def main():
 args=argparse.ArgumentParser(description="DreamCo Stage 3 abstract specification")
 args.add_argument("--input",required=True); args.add_argument("--output",required=True)
 args.add_argument("--onet-db"); args.add_argument("--task-description",default="")
 options=args.parse_args(); parsed=read_json(options.input); validate(parsed,"parsed_facts.schema.json")
 spec=build(parsed,options.task_description,options.onet_db)
 validate(spec,"functional_spec.schema.json"); write_json(options.output,spec)
if __name__=="__main__": main()
