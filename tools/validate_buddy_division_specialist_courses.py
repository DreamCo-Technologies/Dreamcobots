"""Validate 55 original specialist course drafts against canonical division profiles."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"shared/division-production-contract.ts"
COURSES=ROOT/"config/buddy-55-division-specialist-course-drafts.json"
def validate(source_text,courses):
 errors=[]
 if courses.get("schema")!="dreamco.buddy_55_division_specialist_course_drafts.v1": errors.append("unsupported specialist course schema")
 start=source_text.find("export const DIVISION_DOMAIN_PROFILES")
 end=source_text.find("\n};",start)
 expected=set(re.findall(r"^  ([A-Za-z0-9_]+): \{",source_text[start:end],re.M)) if start>=0 and end>=0 else set()
 rows=courses.get("divisions",[])
 actual=[row.get("division_name") for row in rows if isinstance(row,dict)]
 if len(actual)!=len(rows) or len(actual)!=len(set(actual)): errors.append("division course names must be present and unique")
 if set(actual)!=expected: errors.append(f"division course coverage mismatch: missing={sorted(expected-set(actual))}, extra={sorted(set(actual)-expected)}")
 for row in rows:
  if not isinstance(row,dict): continue
  name=row.get("division_name","<unknown>")
  if not row.get("purpose") or not row.get("outcome") or not row.get("boundary"): errors.append(f"{name}: canonical profile fields missing")
  focus=set(row.get("focus_areas",[])); units=row.get("ordered_units",[])
  if {unit.get("title") for unit in units if isinstance(unit,dict)}!=focus: errors.append(f"{name}: every focus area must have exactly one specialist unit")
  if len(units)!=len(focus): errors.append(f"{name}: duplicate or missing specialist units")
  for unit in units:
   if not isinstance(unit,dict): continue
   for field in ("learning_objective","lesson_outline","lab","assessment","required_evidence"):
    if not unit.get(field): errors.append(f"{name}/{unit.get('title')}: missing {field}")
   if unit.get("status")!="original_specialist_unit_draft_needs_human_review": errors.append(f"{name}/{unit.get('title')}: invalid unit status")
  if row.get("course_status")!="original_specialist_course_draft_needs_human_review": errors.append(f"{name}: invalid course status")
  if row.get("mastery_status")!="not_assessed": errors.append(f"{name}: draft cannot claim mastery")
 if courses.get("division_count")!=len(rows): errors.append("division_count mismatch")
 if courses.get("unit_count")!=sum(len(row.get("ordered_units",[])) for row in rows): errors.append("unit_count mismatch")
 return errors
def main():
 courses=json.loads(COURSES.read_text(encoding="utf-8")); errors=validate(SOURCE.read_text(encoding="utf-8"),courses)
 print(json.dumps({"status":"invalid" if errors else "valid","errors":errors,"division_count":len(courses.get("divisions",[])),"unit_count":courses.get("unit_count")},indent=2))
 return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
