#!/usr/bin/env python3
"""Generate one auditable specialist-model profile for every canonical MasterBot."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/masterbot-65-registry.json"
POLICY = ROOT / "config/division-model-competitiveness-policy.json"
OUT = ROOT / "artifacts/division-model-fleet"

def build_profiles():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    bots = registry.get("divisions", [])
    if registry.get("canonical_count") != 65 or len(bots) != 65:
        raise ValueError(f"Expected exactly 65 canonical MasterBots; got {len(bots)}")
    ids = [str(x.get("id")) for x in bots]
    names = [x.get("name") for x in bots]
    if len(set(ids)) != 65 or len(set(names)) != 65 or any(not n for n in names):
        raise ValueError("MasterBot registry has missing or duplicate IDs/names")
    profiles = []
    for bot in bots:
        ident = f"DCM-{int(bot['id']):03d}"
        profile = {
            "schema": "dreamco.division_model_profile.v1",
            "division_model_id": ident,
            "masterbot_id": bot["id"],
            "masterbot_name": bot["name"],
            "domain_crosswalk": {"status": "UNRESOLVED_REQUIRES_45_DOMAIN_RECONCILIATION", "primary_domain_id": None, "collaborators": []},
            "model_identity": {"version": "0.0.0", "status": "PROFILE_ONLY_NOT_TRAINED", "base_model": None, "base_model_license": None, "adapter_or_checkpoint": None, "model_card": None},
            "independence_contract": {"division_owned_task_runner": True, "division_owned_benchmarks": True, "buddy_is_coordinator_not_hidden_solver": True},
            "required_assets": policy["per_division_required_assets"],
            "benchmark_plan": {"shared_general_suite": policy["benchmark_policy"]["shared_general_suite"], "domain_suite": ["expert-authored tasks", "end-to-end workflows", "tool/runtime tasks", "private held-out tasks", "verified failure regressions"], "benchmark_status": "NOT_YET_IMPLEMENTED"},
            "training": {"strategy": policy["architecture"]["training_strategy"], "status": "NOT_STARTED", "weights_trained": False, "paid_compute_authorized": False},
            "promotion": {"status": "BLOCKED_NO_EVIDENCE", "required_gates": policy["promotion_gate"]["requires"], "automatic_production_update": False},
            "evidence": {"tested_commit_sha": None, "baseline": None, "candidate": None, "holdout": None, "regression_run": None, "artifact_hashes": []},
            "next_actions": ["reconcile authoritative 45-domain ownership", "select license-compatible base model", "author division-specific benchmark and private holdout", "measure reproducible baseline", "implement sandbox task runner"]
        }
        profiles.append(profile)
    return profiles

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    profiles = build_profiles()
    canonical = json.dumps(profiles, sort_keys=True, separators=(",", ":")).encode()
    summary = {"schema":"dreamco.division_model_fleet_manifest.v1","profile_count":len(profiles),"masterbot_count":65,"domain_division_target":45,"domain_crosswalk_status":"UNRESOLVED","trained_model_count":0,"mastered_model_count":0,"manifest_sha256":hashlib.sha256(canonical).hexdigest(),"profiles":profiles}
    if args.check:
        print(json.dumps({"valid":True,"profile_count":len(profiles),"trained_model_count":0,"mastered_model_count":0}, indent=2))
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "division-model-fleet.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"profile_count":len(profiles),"output":str(OUT / "division-model-fleet.json"),"trained_model_count":0,"mastered_model_count":0}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
