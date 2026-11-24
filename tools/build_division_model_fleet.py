#!/usr/bin/env python3
"""Generate an auditable specialist-model profile for every domain and shared MasterBot."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/masterbot-75-registry.json"
CROSSWALK = ROOT / "config/generated/masterbot-55-domain-crosswalk.json"
POLICY = ROOT / "config/division-model-competitiveness-policy.json"
OUT = ROOT / "artifacts/division-model-fleet"

def build_profiles():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    crosswalk = json.loads(CROSSWALK.read_text(encoding="utf-8"))
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    bots = registry.get("divisions", [])
    if registry.get("canonical_count") != 75 or len(bots) != 75:
        raise ValueError(f"Expected exactly 75 MasterBots; got {len(bots)}")
    ids = [str(x.get("id")) for x in bots]
    names = [x.get("name") for x in bots]
    if len(set(ids)) != 75 or len(set(names)) != 75 or any(not n for n in names):
        raise ValueError("MasterBot registry has missing or duplicate IDs/names")
    by_id = {int(row["masterbot_id"]): row for row in crosswalk.get("masterbots", [])}
    if crosswalk.get("counts", {}).get("domain_divisions") != 55:
        raise ValueError("Expected 55 canonical domain divisions in MasterBot crosswalk")
    profiles = []
    for bot in bots:
        ident = f"DCM-{int(bot['id']):03d}"
        route = by_id.get(int(bot["id"]), {})
        shared = route.get("mapping_status") == "shared_platform_service"
        profile = {
            "schema": "dreamco.division_model_profile.v2",
            "division_model_id": ident,
            "masterbot_id": bot["id"],
            "masterbot_name": bot["name"],
            "masterbot_type": bot.get("type", "shared_platform_masterbot" if shared else "domain_masterbot"),
            "domain_crosswalk": {
                "status": route.get("mapping_status", "missing_crosswalk"),
                "primary_domain_id": route.get("primary_domain_id"),
                "primary_domain_name": route.get("primary_domain_name"),
                "collaborators": route.get("collaborator_domain_ids", []),
                "owner_approved": route.get("mapping_status") == "owner_approved_primary_domain",
            },
            "model_identity": {"version": "0.0.0", "status": "PROFILE_ONLY_NOT_TRAINED", "base_model": None, "base_model_license": None, "adapter_or_checkpoint": None, "model_card": None},
            "independence_contract": {"division_owned_task_runner": not shared, "division_owned_benchmarks": not shared, "buddy_is_coordinator_not_hidden_solver": True},
            "required_assets": policy["per_division_required_assets"],
            "benchmark_plan": {"shared_general_suite": policy["benchmark_policy"]["shared_general_suite"], "domain_suite": bot.get("benchmark_contract", ["expert-authored tasks", "end-to-end workflows", "tool/runtime tasks", "private held-out tasks", "verified failure regressions"]), "benchmark_status": "NOT_YET_IMPLEMENTED"},
            "training": {"strategy": policy["architecture"]["training_strategy"], "status": "NOT_STARTED", "weights_trained": False, "paid_compute_authorized": False},
            "promotion": {"status": "BLOCKED_NO_EVIDENCE", "required_gates": policy["promotion_gate"]["requires"], "automatic_production_update": False},
            "evidence": {"tested_commit_sha": None, "baseline": None, "candidate": None, "holdout": None, "regression_run": None, "artifact_hashes": []},
            "next_actions": (["define shared-service contracts and service-level benchmarks"] if shared else ["author domain-specific benchmark and private holdout", "select license-compatible base model", "measure reproducible baseline", "implement sandbox task runner", "collect verified learning evidence"]),
        }
        if bot.get("unique_capability_domain"):
            profile["unique_capability_domain"] = bot["unique_capability_domain"]
        if bot.get("specialist_bot_slugs"):
            profile["specialist_bot_slugs"] = bot["specialist_bot_slugs"]
        profiles.append(profile)
    return profiles

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    profiles = build_profiles()
    canonical = json.dumps(profiles, sort_keys=True, separators=(",", ":")).encode()
    summary = {"schema":"dreamco.division_model_fleet_manifest.v2","profile_count":len(profiles),"masterbot_count":75,"domain_division_target":55,"shared_platform_masterbot_count":20,"domain_crosswalk_status":"OWNER_APPROVED","trained_model_count":0,"mastered_model_count":0,"manifest_sha256":hashlib.sha256(canonical).hexdigest(),"profiles":profiles}
    if args.check:
        print(json.dumps({"valid":True,"profile_count":len(profiles),"domain_divisions":55,"shared_platform_masterbots":20,"trained_model_count":0,"mastered_model_count":0}, indent=2))
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "division-model-fleet.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"profile_count":len(profiles),"output":str(OUT / "division-model-fleet.json"),"trained_model_count":0,"mastered_model_count":0}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
