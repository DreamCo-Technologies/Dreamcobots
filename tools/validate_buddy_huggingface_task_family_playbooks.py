"""Validate the 37 Hugging Face task-family playbooks against the repository taxonomy."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TAXONOMY=ROOT/"config/huggingface-task-taxonomy.json"
PLAYBOOKS=ROOT/"config/buddy-huggingface-task-family-playbooks.json"
def validate(taxonomy,playbooks):
 errors=[]
 if taxonomy.get("schema")!="dreamco.huggingface_task_taxonomy.v1": errors.append("unsupported task taxonomy schema")
 if playbooks.get("schema")!="dreamco.huggingface_task_family_playbooks.v1": errors.append("unsupported task playbook schema")
 expected={row.get("id") for row in taxonomy.get("task_families",[]) if isinstance(row,dict)}
 rows=playbooks.get("modules",[])
 actual=[row.get("task_id") for row in rows if isinstance(row,dict)]
 if len(actual)!=len(rows) or len(actual)!=len(set(actual)): errors.append("task IDs must be present and unique")
 if set(actual)!=expected: errors.append(f"task family coverage mismatch: missing={sorted(expected-set(actual))}, extra={sorted(set(actual)-expected)}")
 for row in rows:
  if not isinstance(row,dict): continue
  tid=row.get("task_id","<unknown>")
  for field in ("learning_objectives","ordered_workflow","practice_lab","evaluation_metrics","risk_checks","acceptance_criteria","required_evidence"):
   if not row.get(field): errors.append(f"{tid}: missing {field}")
  if row.get("mastery_status")!="not_assessed": errors.append(f"{tid}: draft cannot claim mastery")
  if len(row.get("ordered_workflow",[]))<6: errors.append(f"{tid}: ordered workflow incomplete")
 if playbooks.get("task_family_count")!=len(rows): errors.append("task family count mismatch")
 return errors
def main():
 taxonomy=json.loads(TAXONOMY.read_text(encoding="utf-8")); playbooks=json.loads(PLAYBOOKS.read_text(encoding="utf-8")); errors=validate(taxonomy,playbooks)
 print(json.dumps({"status":"invalid" if errors else "valid","errors":errors,"task_family_count":len(playbooks.get("modules",[]))},indent=2))
 return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
