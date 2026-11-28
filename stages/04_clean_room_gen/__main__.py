import argparse
from ..common import read_json,write_json,validate
def mock_module(spec):
 title="Learning module: "+spec["system_label"]
 return {"schema_version":"dreamco.course_module.v1","job_id":spec["job_id"],"module_title":title,"learning_objectives":["Describe the abstract inputs and outputs.","Implement the contract using original code.","Verify edge cases with automated tests."],"reference_implementation":{"language":"python","files":[{"path":"solution.py","content":"def execute(payload):\n    if not isinstance(payload, dict):\n        raise TypeError('payload must be a mapping')\n    return {'accepted': True, 'field_count': len(payload)}\n"}]},"tests":[{"path":"test_solution.py","content":"from solution import execute\ndef test_accepts_mapping():\n    assert execute({'x': 1}) == {'accepted': True, 'field_count': 1}\n"}],"challenges":[{"step":1,"instruction":"Inspect the contract and list required inputs.","success_criteria":"Input fields are identified."},{"step":2,"instruction":"Implement the abstract operation with original code.","success_criteria":"Reference tests pass."},{"step":3,"instruction":"Add a negative test for invalid input.","success_criteria":"The negative test passes."}],"provenance":{"model_id":"dreamco-mock-generator-v1","model_license":"DreamCo-Proprietary","source_onet_id":None,"generation_mode":"mock"}}
def main():
 args=argparse.ArgumentParser(description="DreamCo Stage 4 clean-room generator")
 args.add_argument("--input",required=True); args.add_argument("--output",required=True); args.add_argument("--mock",action="store_true")
 options=args.parse_args(); spec=read_json(options.input); validate(spec,"functional_spec.schema.json")
 if spec.get("clean_room",{}).get("original_source_available") is not False: raise ValueError("Generator rejects source-bearing specifications.")
 if spec.get("clean_room",{}).get("source_identifiers_removed") is not True: raise ValueError("Generator requires source identifiers to be removed.")
 if not options.mock: raise RuntimeError("No model adapter configured. Use --mock for deterministic CI or configure an approved local model adapter.")
 module=mock_module(spec); validate(module,"course_module.schema.json"); write_json(options.output,module)
if __name__=="__main__": main()
