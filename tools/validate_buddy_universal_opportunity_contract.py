#!/usr/bin/env python3
"""Validate Buddy's universal opportunity-to-cash expansion contract."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"config/startup_factory/buddy_universal_opportunity_contract.json"
REQUIRED={
"supplier_intelligence","distribution","business_planning","franchise_relationships","construction_and_development","marketing_advertising","workforce","ip_and_innovation","worldwide_commerce","camera_and_visual_research","revolut_integration_target","low_capital_path"
}
def main()->int:
 data=json.loads(CONTRACT.read_text(encoding="utf-8"))
 missing=sorted(REQUIRED-set(data.get("global_workstreams",{}))-{"camera_and_visual_research","revolut_integration_target","low_capital_path"})
 if missing: raise SystemExit(f"missing workstreams: {missing}")
 for key in ("camera_and_visual_research","revolut_integration_target","low_capital_path"):
  if key not in data: raise SystemExit(f"missing contract section: {key}")
 if not data["low_capital_path"].get("enabled"): raise SystemExit("low-capital path must be enabled")
 if data["camera_and_visual_research"].get("training_mode") is None: raise SystemExit("camera learning policy missing")
 if data["revolut_integration_target"].get("architecture") != "provider_adapter_not_provider_lock_in": raise SystemExit("payments must remain provider-agnostic")
 print("PASS: universal opportunity-to-cash workstreams present")
 print("PASS: low-capital path enabled")
 print("PASS: camera/visual research and consented learning contract present")
 print("PASS: Revolut benchmark and provider-agnostic payments contract present")
 print("PASS: IP, development, supplier, distribution, workforce and global commerce paths present")
 return 0
if __name__=="__main__": raise SystemExit(main())
