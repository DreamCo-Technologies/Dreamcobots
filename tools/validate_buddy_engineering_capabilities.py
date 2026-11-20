#!/usr/bin/env python3
"""Validate Buddy's vibe-coding, reverse-engineering, distillation, and training contract."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/buddy-engineering-capability-contract.json"
REQUIRED = {"vibe_coding", "reverse_engineering", "model_distillation", "model_weight_training", "physical_product_design", "hardware_software_prototyping", "three_dimensional_invention", "startup_creation"}

def validate() -> dict:
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    caps = data.get("capabilities", {})
    missing = sorted(REQUIRED - set(caps))
    if missing:
        raise ValueError(f"Missing capability contracts: {missing}")
    for name in sorted(REQUIRED):
        cap = caps[name]
        if not cap.get("stages") or not cap.get("required_outputs"):
            raise ValueError(f"{name} must define stages and required_outputs")
        if not str(cap.get("status", "")).startswith("CONTRACT_DEFINED_"):
            raise ValueError(f"{name} must be explicitly labeled as contract-defined")
    reverse = caps["reverse_engineering"]
    prohibited = set(reverse.get("prohibited", []))
    for phrase in ("bypass_authentication_or_access_controls", "credential_extraction"):
        if phrase not in prohibited:
            raise ValueError(f"Reverse-engineering safety prohibition missing: {phrase}")
    shared = data.get("shared_requirements", {})
    if shared.get("evidence") is None or shared.get("promotion") is None:
        raise ValueError("Evidence and promotion requirements are mandatory")
    if data["acceptance_gates"]["model_distillation"] is None:
        raise ValueError("Distillation acceptance gates are mandatory")
    if caps["model_distillation"].get("holdout_excluded_from_training") is not True:
        raise ValueError("Private holdout must be excluded from training")
    if caps["model_weight_training"].get("paid_compute_requires_explicit_approval") is not True:
        raise ValueError("Paid compute must require explicit approval")
    if caps["model_weight_training"].get("production_weight_updates_require_separate_explicit_approval") is not True:
        raise ValueError("Production weight updates need separate approval")
    return {"valid": True, "capabilities": sorted(REQUIRED), "operational_claim": False}

def main() -> int:
    print(json.dumps(validate(), indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
