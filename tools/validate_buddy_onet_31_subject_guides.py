"""Validate original O*NET subject guide drafts against the canonical 31-subject inventory."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CURRICULUM=ROOT/"config/buddy-onet-content-model-curriculum.json"
GUIDES=ROOT/"config/buddy-onet-31-subject-study-guides.json"
def validate(curriculum,guides):
 errors=[]
 if curriculum.get("schema")!="dreamco.buddy_onet_content_model_curriculum.v1": errors.append("unsupported O*NET curriculum schema")
 if guides.get("schema")!="dreamco.onet_31_subject_study_guides.v1": errors.append("unsupported subject guide schema")
 expected={x.get("id") for x in curriculum.get("subject_inventory",[]) if isinstance(x,dict)}
 rows=guides.get("subjects",[])
 actual=[x.get("subject_id") for x in rows if isinstance(x,dict)]
 if len(actual)!=len(rows) or len(actual)!=len(set(actual)): errors.append("subject IDs must be present and unique")
 if set(actual)!=expected: errors.append(f"subject coverage mismatch: missing={sorted(expected-set(actual))}, extra={sorted(set(actual)-expected)}")
 for row in rows:
  if not isinstance(row,dict): continue
  sid=row.get("subject_id","<unknown>")
  for field in ("learning_goal","lesson_outline","hands_on_lab","assessment","professional_safeguard","required_evidence","rights_and_source_policy"):
   if not row.get(field): errors.append(f"{sid}: missing {field}")
  if len(row.get("lesson_outline",[]))<3: errors.append(f"{sid}: lesson outline needs at least three steps")
  if row.get("mastery_status")!="not_assessed": errors.append(f"{sid}: guide draft cannot claim mastery")
  if row.get("lesson_status")!="original_draft_needs_human_review": errors.append(f"{sid}: lesson draft must remain in human review")
 if guides.get("source_release")!=curriculum.get("source",{}).get("current_reference_release"): errors.append("source release mismatch")
 if "O*NET 31.0 Database" not in guides.get("attribution",""): errors.append("O*NET attribution missing")
 return errors
def main():
 curriculum=json.loads(CURRICULUM.read_text(encoding="utf-8")); guides=json.loads(GUIDES.read_text(encoding="utf-8")); errors=validate(curriculum,guides)
 print(json.dumps({"status":"invalid" if errors else "valid","errors":errors,"subject_count":len(guides.get("subjects",[]))},indent=2))
 return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
