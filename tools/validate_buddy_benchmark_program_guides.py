"""Validate individual benchmark program guide coverage against the canonical benchmark index."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"config/buddy-benchmark-index.json"
GUIDES=ROOT/"config/buddy-benchmark-program-guides.json"
def validate(index,guides):
 errors=[]
 if index.get("schema")!="dreamco.benchmark_index_source.v1": errors.append("unsupported benchmark index schema")
 if guides.get("schema")!="dreamco.buddy_benchmark_program_guides.v1": errors.append("unsupported program guide schema")
 expected={p.get("id") for p in index.get("programs",[]) if isinstance(p,dict)}
 rows=guides.get("programs",[])
 actual=[p.get("benchmark_id") for p in rows if isinstance(p,dict)]
 if len(actual)!=len(rows) or len(actual)!=len(set(actual)): errors.append("benchmark program IDs must be present and unique")
 if set(actual)!=expected: errors.append(f"program coverage mismatch: missing={sorted(expected-set(actual))}, extra={sorted(set(actual)-expected)}")
 source={p["id"]:p for p in index.get("programs",[]) if isinstance(p,dict)}
 for row in rows:
  if not isinstance(row,dict): continue
  bid=row.get("benchmark_id","<unknown>")
  canonical=source.get(bid,{})
  for field in ("title","scope","generator","check_command","cadence","benchmark_purpose","methodology","evaluation_metrics","thresholds","baseline_and_comparator","workload_and_environment","reproducibility","holdout_and_contamination_controls","safety_and_permissions","evidence_artifacts","remediation","limitations","review"):
   if row.get(field) in (None,"",[],{}): errors.append(f"{bid}: missing {field}")
  if row.get("generator")!=canonical.get("generator") or row.get("check_command")!=canonical.get("check_command"): errors.append(f"{bid}: canonical command or generator mismatch")
  if row.get("execution_status")!="not_executed_by_guide_generation": errors.append(f"{bid}: guide cannot claim execution")
  if row.get("guide_status")!="original_program_guide_draft_needs_human_review": errors.append(f"{bid}: invalid guide status")
  if row.get("thresholds",{}).get("values") is not None: errors.append(f"{bid}: guide generation must not invent numeric thresholds")
 if guides.get("program_count")!=len(rows): errors.append("program_count mismatch")
 return errors
def main():
 index=json.loads(INDEX.read_text(encoding="utf-8")); guides=json.loads(GUIDES.read_text(encoding="utf-8")); errors=validate(index,guides)
 print(json.dumps({"status":"invalid" if errors else "valid","errors":errors,"program_count":len(guides.get("programs",[]))},indent=2))
 return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
