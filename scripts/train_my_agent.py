#!/usr/bin/env python3
"""Fail-closed buyer training preflight; no training backend is enabled."""
import argparse,json
from pathlib import Path
try:
    from .dreamco_hardware_detector import detect
except ImportError:
    from dreamco_hardware_detector import detect
ROOT=Path(__file__).resolve().parents[1]
def preflight(kit,execute=False):
    mpath=kit/"BUYER_MANIFEST.json"; cpath=kit/"blueprint/config.json"
    if not mpath.is_file() or not cpath.is_file(): raise ValueError("Incomplete buyer kit")
    manifest=json.loads(mpath.read_text(encoding="utf-8"))
    config=json.loads(cpath.read_text(encoding="utf-8"))
    blockers=[]
    if manifest.get("weights_status")!="UNTRAINED_BLUEPRINT_READY_FOR_TRAINING" or manifest.get("weights_included") is not False:
        blockers.append("Buyer kit weight-status contract failed")
    if config.get("weights_status")!="UNTRAINED_BLUEPRINT_READY_FOR_TRAINING" or config.get("initialization")!="random":
        blockers.append("Architecture config must be a random-initialization untrained blueprint")
    hardware=detect()
    if manifest.get("tier") not in hardware.get("candidate_tiers",[]):
        blockers.append("Detected hardware does not meet advisory tier guidance")
    dataset_manifest=ROOT/"config/authorized-training-datasets/manifest.json"
    approved=[]
    if not dataset_manifest.is_file():
        blockers.append("Authorized training dataset manifest is missing")
    else:
        policy=json.loads(dataset_manifest.read_text(encoding="utf-8"))
        approved=[d for d in policy.get("datasets",[]) if d.get("training_approved") is True and d.get("rights_status")=="APPROVED" and d.get("sha256") and d.get("evidence_reference")]
        if not approved: blockers.append("No explicitly approved, rights-evidenced, hash-pinned dataset is admitted")
    if execute: blockers.append("No reviewed training backend adapter is configured; execution is disabled")
    return {"schema":"dreamco.buyer_training_preflight.v1","status":"BLOCKED" if blockers else "READY_FOR_BACKEND_REVIEW","tier":manifest.get("tier"),"division":manifest.get("division"),"weights_status":manifest.get("weights_status"),"parameter_count_verified":manifest.get("parameter_count_verified",False),"hardware":hardware,"approved_dataset_count":len(approved),"blockers":blockers,"training_started":False,"paid_compute_requested":False,"customer_data_uploaded":False}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit",type=Path,required=True)
    parser.add_argument("--execute",action="store_true",help="Execution remains disabled until a reviewed backend adapter exists")
    args=parser.parse_args(); result=preflight(args.kit,args.execute)
    print(json.dumps(result,indent=2))
    return 0 if result["status"]!="BLOCKED" else 2
if __name__=="__main__": raise SystemExit(main())
