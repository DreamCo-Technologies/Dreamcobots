"""Allowlist-only export of verified artifacts; never stores hidden reasoning or raw uploads."""
import json,os,math
from pathlib import Path
from .common import validate

def verified_record(functional_spec,course_module,eval_report):
    score=eval_report.get("similarity_score")
    if (eval_report.get("status")!="PASS" or eval_report.get("tests_passed") is not True
        or eval_report.get("policy_check")!="PASS" or not isinstance(score,(int,float))
        or not math.isfinite(score) or not 0<=score<0.25
        or functional_spec.get("clean_room",{}).get("original_source_available") is not False):
        raise PermissionError("Training export requires source-free specs, passing tests, policy PASS and similarity below 0.25.")
    validate(functional_spec,"functional_spec.schema.json")
    validate(course_module,"course_module.schema.json")
    validate(eval_report,"eval_report.schema.json")
    return {"schema_version":"dreamco.verified_training_record.v1","job_id":eval_report["job_id"],"abstract_spec":functional_spec,"generated_code":course_module["reference_implementation"]["files"],"test_pass":True,"similarity_score":score,"policy_check":"PASS","provenance":course_module["provenance"]}

def append_verified_record(functional_spec,course_module,eval_report,path=None):
    record=verified_record(functional_spec,course_module,eval_report)
    target=path or os.environ.get("DREAMCO_TRAINING_EXPORT_PATH")
    if not target: raise RuntimeError("Training export is disabled until DREAMCO_TRAINING_EXPORT_PATH is explicitly configured.")
    destination=Path(target); destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open("a",encoding="utf-8") as stream:
        stream.write(json.dumps(record,sort_keys=True)+"\n")
    return record
