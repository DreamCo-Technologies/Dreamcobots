"""Coverage matrix for the canonical 65-MasterBot registry; never invent O*NET mappings."""
from __future__ import annotations
import json
from pathlib import Path
def build_matrix(registry_path: str|Path, curriculum_path: str|Path|None=None)->dict:
    registry=json.loads(Path(registry_path).read_text())
    divisions=registry.get("divisions",[])
    if len(divisions)!=65 or sorted(x.get("id") for x in divisions)!=list(range(1,66)):
        raise ValueError("canonical MasterBot registry must contain unique IDs 1..65")
    curricula={}
    if curriculum_path and Path(curriculum_path).exists():
        data=json.loads(Path(curriculum_path).read_text())
        curricula={str(x.get("division_id")):x for x in data.get("divisions",data.get("artifacts",[]))}\n        curricula_by_name={str(x.get("division_name","")).casefold():x for x in data.get("divisions",data.get("artifacts",[])) if x.get("division_name")}
    rows=[]
    for d in sorted(divisions,key=lambda x:x["id"]):
        c=curricula.get(str(d["id"])) or curricula_by_name.get(str(d["name"]).casefold(),{})
        rows.append({"division_id":d["id"],"division_name":d["name"],
          "curriculum_status":c.get("status","not_yet_mapped"),
          "onet_task_codes":c.get("onet_task_codes",[]),
          "onet_mapping_status":c.get("onet_mapping_status","unverified_not_mapped"),
          "tools":c.get("tools",[]),"competencies":c.get("competencies",[]),
          "readiness":"BLOCKED_UNTIL_OWNER_REVIEW" if not c.get("owner_reviewed") else "OWNER_REVIEWED"})
    return {"schema":"dreamco.bootcamp_division_matrix.v1","canonical_registry":"config/masterbot-65-registry.json",
      "division_count":65,"mapped_curricula":sum(r["curriculum_status"] not in ("not_yet_mapped","") for r in rows),
      "verified_onet_mappings":sum(r["onet_mapping_status"]=="verified" and bool(r["onet_task_codes"]) for r in rows),
      "ready_divisions":sum(r["readiness"]=="OWNER_REVIEWED" for r in rows),
      "truth_boundary":"No O*NET task code is inferred from a division name. Unverified mappings remain explicitly unmapped.",
      "divisions":rows}
