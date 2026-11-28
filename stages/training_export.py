"""Allowlist-only export of verified artifacts; never stores hidden reasoning or raw uploads."""
import json,os
from pathlib import Path

def verified_record(functional_spec,course_module,eval_report):
    if eval_report.get("status")!="PASS" or eval_report.get("tests_passed") is not True or eval_report.get("policy_check")!="PASS" or eval_report.get("similarity_score",1)>=0.25:
        raise PermissionError("Training export requires passing tests, policy PASS and similarity below 0.25.")
    return {"schema_version":"dreamco.verified_training_record.v1","job_id":eval_report["job_id"],"abstract_spec":functional_spec,"generated_code":course_module["reference_implementation"]["files"],"test_pass":True,"similarity_score":eval_report["similarity_score"],"policy_check":"PASS","provenance":course_module["provenance"]}
def append_verified_record(record,path=None):
    target=path or os.environ.get("DREAMCO_TRAINING_EXPORT_PATH")
    if not target: raise RuntimeError("Training export is disabled until DREAMCO_TRAINING_EXPORT_PATH is explicitly configured.")
    p=Path(target); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("a",encoding="utf-8") as f:f.write(json.dumps(record,sort_keys=True)+"\\n")
