#!/usr/bin/env python3
"""Generate deterministic, untrained learning-model kit manifests for all 65 MasterBot lanes."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/masterbot-65-registry.json"
CONTRACT = ROOT / "config/dreamco-universal-division-mastery-contract.json"
OUT = ROOT / "config/generated/division-learning-model-kits"
TIERS = {
    "nano_18m": {
        "target_parameters": 18_000_000,
        "role": "fast classification, routing and narrow domain tasks",
        "status": "BLUEPRINT_TARGET_NOT_INSTANTIATED",
    },
    "core_120m": {
        "target_parameters": 120_000_000,
        "role": "domain task execution and multi-step workflows",
        "status": "BLUEPRINT_TARGET_NOT_INSTANTIATED",
    },
    "master_teacher": {
        "target_parameters": None,
        "role": "curriculum instruction, evaluation, explanation and verifier orchestration",
        "status": "ARCHITECTURE_AND_SIZE_TO_BE_DEFINED",
    },
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    if not slug:
        raise ValueError(f"Invalid division name: {value!r}")
    return slug


def build_manifests() -> dict[str, dict]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    divisions = registry.get("divisions", [])
    expected = contract["inventory_contract"]["masterbot_learning_lanes_expected"]
    if registry.get("canonical_count") != expected or len(divisions) != expected:
        raise ValueError(f"Expected {expected} canonical MasterBot lanes; found {len(divisions)}")
    ids = [int(row["id"]) for row in divisions]
    names = [row["name"] for row in divisions]
    if len(set(ids)) != expected or len(set(names)) != expected:
        raise ValueError("MasterBot registry contains duplicate IDs or names")
    if set(ids) != set(range(1, expected + 1)):
        raise ValueError("MasterBot IDs must be the complete canonical 1..65 range")

    manifests = {}
    for division in divisions:
        division_id = int(division["id"])
        division_name = division["name"]
        slug = slugify(division_name)
        for tier_id, tier in TIERS.items():
            payload = {
                "schema": "dreamco.division_learning_model_kit.v1",
                "status": tier["status"],
                "division": {
                    "masterbot_id": division_id,
                    "masterbot_name": division_name,
                    "lane_id": f"masterbot-{division_id:02d}",
                    "domain_crosswalk_ref": "config/generated/masterbot-55-domain-crosswalk.json",
                    "domain_mapping_status": "REVIEW_REQUIRED_NOT_AUTHORIZED",
                },
                "kit": {
                    "id": tier_id,
                    "target_parameters": tier["target_parameters"],
                    "role": tier["role"],
                    "parameter_count_verified": False,
                    "weights_present": False,
                    "training_authorized": False,
                },
                "curriculum_contract_ref": "config/dreamco-universal-division-mastery-contract.json",
                "evidence_requirements": [
                    "source_provenance_and_rights",
                    "privacy_and_retention_review",
                    "dataset_hashes_and_split_isolation",
                    "reproducible_training_configuration",
                    "independent_holdout_evaluation",
                    "safety_and_regression_results",
                    "human_release_approval",
                ],
                "training": {
                    "status": "NOT_STARTED",
                    "backend": None,
                    "dataset_manifest": None,
                    "checkpoint_sha256": None,
                    "paid_compute_approved": False,
                },
                "release": {
                    "status": "BLOCKED_UNTIL_EVIDENCE_AND_HUMAN_APPROVAL",
                    "marketplace_eligible": False,
                    "production_eligible": False,
                },
            }
            path = f"config/generated/division-learning-model-kits/masterbot_{division_id:02d}_{slug}/{tier_id}.json"
            manifests[path] = payload
    if len(manifests) != expected * len(TIERS):
        raise ValueError("Generated learning model kit count does not equal 65 x 3")
    return manifests


def write_manifests(manifests: dict[str, dict]) -> None:
    for relative_path, payload in manifests.items():
        destination = ROOT / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check_manifests(manifests: dict[str, dict]) -> list[str]:
    errors = []
    expected_paths = set(manifests)
    for relative_path, payload in manifests.items():
        destination = ROOT / relative_path
        if not destination.is_file():
            errors.append(f"missing: {relative_path}")
            continue
        try:
            actual = json.loads(destination.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON: {relative_path}: {exc}")
            continue
        if actual != payload:
            errors.append(f"stale or modified: {relative_path}")
    if OUT.exists():
        actual_paths = {
            path.relative_to(ROOT).as_posix()
            for path in OUT.rglob("*.json")
        }
        for unexpected in sorted(actual_paths - expected_paths):
            errors.append(f"unexpected: {unexpected}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write all 195 deterministic manifests")
    mode.add_argument("--check", action="store_true", help="verify all 195 manifests without writing")
    args = parser.parse_args()
    manifests = build_manifests()
    if args.write:
        write_manifests(manifests)
        print(json.dumps({"status": "GENERATED_BLUEPRINTS_NOT_TRAINED", "manifest_count": len(manifests), "output": str(OUT.relative_to(ROOT))}))
        return 0
    errors = check_manifests(manifests)
    if errors:
        print(json.dumps({"status": "BLOCKED", "expected": len(manifests), "errors": errors[:100]}, indent=2))
        return 1
    print(json.dumps({"status": "VALIDATED_BLUEPRINTS_NOT_TRAINED", "manifest_count": len(manifests)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
