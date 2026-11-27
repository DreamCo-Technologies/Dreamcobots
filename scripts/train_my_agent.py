#!/usr/bin/env python3
"""Fail-closed buyer training preflight; backend execution is not enabled."""
import argparse,json
from pathlib import Path
from dreamco_hardware_detector import detect
ROOT=Path(__file__).resolve().parents[1]
def preflight(kit,execute=False):
 mpath=kit/"BUYER_MANIFEST.json"; cpath=kit/"blueprint/config.json"
 if not mpath.is_file() or not cpath.is_file(): raise ValueError("Incomplete buyer kit")
 m=json.loads(mpath.read_text()); json.loads(cpath.read_text())
 if m.get("weights_status")!="UNTRAINED_BLUEPRINT_READY_FOR_TRAINING" or m.get("weights_included") is not False: raise ValueError("Unsafe or inconsistent weight status")
 h=detect(); policy=json.loads((ROOT/"config/authorized-training-datasets/manifest.json").read_text())
 approved=[d for d in policy.get("datasets",[]) if d.get("training_approved") is True and d.get("rights_status")=="APPROVED" and d.get("sha256") and d.get("evidence_reference")]
 blockers=[]
 if not approved: blockers.append("No explicitly approved, rights-evidenced, hash-pinned dataset is admitted.")
 if m.get("tier") not in h.get("candidate_tiers",[]): blockers.append("Detected hardware does not meet advisory tier guidance.")
 if execute: blockers.append("No reviewed training backend adapter is configured; execution is disabled.")
 return {"schema":"dreamco.buyer_training_preflight.v1","status":"BLOCKED" if blockers else "READY_FOR_BACKEND_REVIEW","tier":m.get("tier"),"division":m.get("division"),"weights_status":m["weights_status"],"hardware":h,"approved_dataset_count":len(approved),"blockers":blockers,"training_started":False,"paid_compute_requested":False,"customer_data_uploaded":False}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--kit",type=Path,required=True);p.add_argument("--execute",action="store_true");a=p.parse_args();r=preflight(a.kit,a.execute);print(json.dumps(r,indent=2));return 0 if r["status"]!="BLOCKED" else 2
if __name__=="__main__":raise SystemExit(main())
