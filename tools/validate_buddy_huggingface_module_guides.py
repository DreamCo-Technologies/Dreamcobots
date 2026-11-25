"""Validate Hugging Face ecosystem study-guide coverage against the canonical learning map."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAP=ROOT/"config/buddy-huggingface-full-learning-map.json"
GUIDES=ROOT/"config/buddy-huggingface-18-ecosystem-module-guides.json"
def validate(source,guides):
 errors=[]
 if source.get("schema")!="dreamco.huggingface_full_learning_map.v1": errors.append("unsupported Hugging Face learning map schema")
 if guides.get("schema")!="dreamco.huggingface_18_ecosystem_module_guides.v1": errors.append("unsupported module guide schema")
 expected={x.get("id") for x in source.get("ecosystem_modules",[]) if isinstance(x,dict)}
 rows=guides.get("modules",[])
 actual=[x.get("module_id") for x in rows if isinstance(x,dict)]
 if len(actual)!=len(rows) or len(actual)!=len(set(actual)): errors.append("module IDs must be present and unique")
 if set(actual)!=expected: errors.append(f"module coverage mismatch: missing={sorted(expected-set(actual))}, extra={sorted(set(actual)-expected)}")
 course_ids={x.get("id") for x in source.get("official_courses",[]) if isinstance(x,dict)}
 mapped={x.get("id") for x in guides.get("official_courses",[]) if isinstance(x,dict)}
 if mapped!=course_ids: errors.append("official course link inventory mismatch")
 for row in rows:
  if not isinstance(row,dict): continue
  mid=row.get("module_id","<unknown>")
  for field in ("learning_objectives","lesson_sequence","hands_on_lab","assessment","failure_cases","required_evidence","rights_policy"):
   if not row.get(field): errors.append(f"{mid}: missing {field}")
  if len(row.get("lesson_sequence",[]))<3: errors.append(f"{mid}: lesson sequence incomplete")
  if row.get("execution_status")!="guide_draft_not_studied_or_benchmarked": errors.append(f"{mid}: invalid completion status")
 if guides.get("ecosystem_module_count")!=len(rows): errors.append("module count mismatch")
 return errors
def main():
 source=json.loads(MAP.read_text(encoding="utf-8")); guides=json.loads(GUIDES.read_text(encoding="utf-8")); errors=validate(source,guides)
 print(json.dumps({"status":"invalid" if errors else "valid","errors":errors,"module_count":len(guides.get("modules",[])),"official_course_count":len(guides.get("official_courses",[]))},indent=2))
 return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
