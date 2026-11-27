#!/usr/bin/env python3
"""Validate DreamCo's external-resource registry and fail-closed admission metadata."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"config/dreamco_institute_resource_registry.json"
REQUIRED={"id","name","category","resource_type","acquisition_status","license_status","commercial_training_permission","quarantine_status","source_provenance_required","sha256_required"}
def validate(data):
 errors=[]
 entries=data.get("resources",[])
 if data.get("resource_count")!=100 or len(entries)!=100: errors.append("registry must contain exactly 100 resources")
 ids=[x.get("id") for x in entries]
 if len(set(ids))!=len(ids): errors.append("resource IDs must be unique")
 for item in entries:
  missing=REQUIRED-set(item)
  if missing: errors.append(f"{item.get('id')}: missing fields {sorted(missing)}")
  if item.get("license_status")!="UNVERIFIED" and not item.get("license_evidence"): errors.append(f"{item.get('id')}: license evidence required")
  if item.get("commercial_training_permission")=="APPROVED" and not all(item.get(k) for k in ("license_evidence","source_url","snapshot_sha256","reviewed_by")): errors.append(f"{item.get('id')}: approval evidence incomplete")
  if item.get("quarantine_status")=="APPROVED_FOR_TRAINING" and item.get("commercial_training_permission")!="APPROVED": errors.append(f"{item.get('id')}: training gate cannot pass without permission")
 return errors
def main():
 data=json.loads(REGISTRY.read_text(encoding="utf-8")); errors=validate(data)
 print(json.dumps({"status":"FAIL" if errors else "PASS","resource_count":len(data.get("resources",[])),"errors":errors},indent=2))
 return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
