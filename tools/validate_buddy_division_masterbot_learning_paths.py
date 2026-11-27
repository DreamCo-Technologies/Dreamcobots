"""Validate ordered learning paths for every canonical division and MasterBot lane."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATHS=ROOT/"config/buddy-division-masterbot-learning-paths.json"
REGISTRY=ROOT/"config/masterbot-65-registry.json"
CROSSWALK=ROOT/"config/generated/masterbot-55-domain-crosswalk.json"
CONTRACT=ROOT/"shared/division-production-contract.ts"

def validate(paths, registry, crosswalk, contract_text):
 errors=[]
 if paths.get("schema")!="dreamco.division_masterbot_ordered_learning_paths.v1": errors.append("unsupported learning path schema")
 divisions=paths.get("divisions",[])
 lanes=paths.get("masterbot_lanes",[])
 canonical_masterbots=registry.get("divisions",[])
 expected_names=set()
 block_start=contract_text.find("export const DIVISION_DOMAIN_PROFILES")
 block_end=contract_text.find("\n};",block_start)
 if block_start<0 or block_end<0: errors.append("canonical division domain profiles missing")
 else:
  import re
  expected_names=set(re.findall(r"^  ([A-Za-z0-9_]+): \{",contract_text[block_start:block_end],re.M))
 actual_names={row.get("division_name") for row in divisions if isinstance(row,dict)}
 if actual_names!=expected_names: errors.append(f"division coverage mismatch: missing={sorted(expected_names-actual_names)}, extra={sorted(actual_names-expected_names)}")
 expected_ids={row.get("id") for row in canonical_masterbots}
 actual_ids=[row.get("masterbot_id") for row in lanes if isinstance(row,dict)]
 if len(actual_ids)!=len(lanes) or len(actual_ids)!=len(set(actual_ids)): errors.append("MasterBot lane IDs must be present and unique")
 if set(actual_ids)!=expected_ids: errors.append("MasterBot lane coverage does not match canonical registry")
 stage_ids=[row.get("id") for row in paths.get("stage_template",[])]
 if stage_ids!=["mission_and_boundaries","domain_fundamentals","tools_and_software","professional_workflows","specialist_capabilities","benchmark_and_transfer","instructor_and_improvement"]:
  errors.append("ordered stage template is missing or out of order")
 for row in divisions:
  if not row.get("purpose") or not row.get("outcome") or not row.get("boundary") or not row.get("focus_areas"):
   errors.append(f"{row.get('division_name')}: canonical profile details missing")
 for row in lanes:
  mapping=row.get("division_mapping")
  if mapping and (mapping.get("review_required") is not True or mapping.get("owner_approval") is not None):
   errors.append(f"{row.get('masterbot_name')}: proposed mapping must remain unapproved")
 if paths.get("ownership_policy",{}).get("exact_name_match_is_proposal_only") is not True:
  errors.append("exact name matches must remain proposed pending review")
 return errors

def main():
 paths=json.loads(PATHS.read_text(encoding="utf-8"))
 registry=json.loads(REGISTRY.read_text(encoding="utf-8"))
 crosswalk=json.loads(CROSSWALK.read_text(encoding="utf-8"))
 errors=validate(paths,registry,crosswalk,CONTRACT.read_text(encoding="utf-8"))
 print(json.dumps({"status":"invalid" if errors else "valid","errors":errors,"division_count":len(paths.get("divisions",[])),"masterbot_lane_count":len(paths.get("masterbot_lanes",[]))},indent=2))
 return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
