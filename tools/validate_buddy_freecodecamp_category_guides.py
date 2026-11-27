"""Validate original freeCodeCamp category guide coverage against the source taxonomy."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"buddy/bootcamp/sources/freecodecamp/catalog.json"
GUIDES=ROOT/"config/buddy-freecodecamp-22-category-study-guides.json"
def validate(catalog,guides):
 errors=[]
 if catalog.get("schema")!="dreamco.freecodecamp_catalog.v1": errors.append("unsupported freeCodeCamp catalog schema")
 if guides.get("schema")!="dreamco.freecodecamp_22_category_study_guides.v1": errors.append("unsupported category guide schema")
 expected={row.get("id") for row in catalog.get("categories",[]) if isinstance(row,dict)}
 rows=guides.get("categories",[])
 actual=[row.get("category_id") for row in rows if isinstance(row,dict)]
 if len(actual)!=len(rows) or len(actual)!=len(set(actual)): errors.append("category IDs must be present and unique")
 if set(actual)!=expected: errors.append(f"category coverage mismatch: missing={sorted(expected-set(actual))}, extra={sorted(set(actual)-expected)}")
 if guides.get("category_count")!=len(rows): errors.append("category count mismatch")
 for row in rows:
  if not isinstance(row,dict): continue
  cid=row.get("category_id","<unknown>")
  for field in ("learning_goal","ordered_units","capstone_project","assessment","evaluation_dimensions","evidence_required","rights_and_safety"):
   if not row.get(field): errors.append(f"{cid}: missing {field}")
  if len(row.get("ordered_units",[]))<4: errors.append(f"{cid}: ordered units incomplete")
  if row.get("mastery_status")!="not_assessed": errors.append(f"{cid}: draft cannot claim mastery")
  if row.get("status")!="original_category_guide_draft_needs_human_review": errors.append(f"{cid}: invalid draft status")
 if guides.get("source_inventory_status")!=catalog.get("inventory_status"): errors.append("source inventory status mismatch")
 return errors
def main():
 catalog=json.loads(CATALOG.read_text(encoding="utf-8")); guides=json.loads(GUIDES.read_text(encoding="utf-8")); errors=validate(catalog,guides)
 print(json.dumps({"status":"invalid" if errors else "valid","errors":errors,"category_count":len(guides.get("categories",[])),"source_inventory_status":guides.get("source_inventory_status")},indent=2))
 return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
