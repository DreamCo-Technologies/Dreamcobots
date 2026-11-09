#!/usr/bin/env python3
"""Validate Buddy category-system records against repository source catalogs."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
REGISTRY_PATH = CONFIG / "buddy/category-system-registry.json"
RESOURCE_PATH = CONFIG / "buddy/resource-registry.json"
DIVISION_PATH = CONFIG / "masterbot-65-registry.json"
DIVISION_AUDIT_PATH = ROOT / "reports/BOT_DIVISION_PLACEMENT_AUDIT.md"
MODEL_PATH = ROOT / "shared/ai-models.ts"

def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)

def fail(message: str) -> None:
    raise SystemExit(f"Buddy category-system registry: FAIL: {message}")

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate without modifying files")
    parser.parse_args()

    registry = load_json(REGISTRY_PATH)
    resources = load_json(RESOURCE_PATH)["resources"]
    study_paths = sorted(CONFIG.glob("buddy-study-resources-*.json"))
    if not study_paths:
        fail("no buddy-study-resources-*.json catalogs found")
    study_sets = [(path.relative_to(ROOT).as_posix(), load_json(path)["resources"]) for path in study_paths]
    study_rows = [row for _, rows in study_sets for row in rows]
    division_registry = load_json(DIVISION_PATH)
    division_audit = DIVISION_AUDIT_PATH.read_text(encoding="utf-8")
    model_source = MODEL_PATH.read_text(encoding="utf-8")

    if registry.get("schema") != "dreamco.buddy.category_system_registry.v1":
        fail("unexpected or missing schema identifier")
    systems = registry.get("systems")
    if not isinstance(systems, list):
        fail("systems must be an array")
    ids = [item.get("id") for item in systems]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        fail("subsystem IDs must be present and unique")

    expected = {
        "registry": {
            category: {resource["id"] for resource in resources if resource["category"] == category}
            for category in {resource["category"] for resource in resources}
        },
        "study": {
            category: {f"study_resource_{row[0]}" for row in study_rows if row[2] == category}
            for category in {row[2] for row in study_rows}
        },
        "model": {},
        "division": {
            item["name"]: {f"division_{item['id']}"}
            for item in division_registry["divisions"]
        },
    }

    model_block = re.search(r"AI_MODEL_CATEGORIES\s*=\s*\[(.*?)\]\s*as const", model_source, re.S)
    if not model_block:
        fail("could not locate AI_MODEL_CATEGORIES in shared/ai-models.ts")
    model_categories = re.findall(r'"([^"]+)"', model_block.group(1))
    model_counts = Counter(re.findall(r'category:\s*"([^"]+)"', model_source))
    expected["model"] = {category: set() for category in model_categories}

    audited_divisions = set(re.findall(r"^\| ([A-Za-z][A-Za-z0-9]+) \| \d+ \|", division_audit, re.M))
    if len(audited_divisions) != 45:
        fail(f"expected 45 distinct divisions in placement audit; found {len(audited_divisions)}")

    actual = {(item.get("group"), item.get("category")): item for item in systems}
    expected_keys = {(group, category) for group, categories in expected.items() for category in categories}
    if set(actual) != expected_keys:
        missing = sorted(expected_keys - set(actual))
        extra = sorted(set(actual) - expected_keys)
        fail(f"category mismatch; missing={missing}; extra={extra}")

    required_contract_fields = {
        "mission", "inputs", "outputs", "permissions", "safety_controls",
        "metrics", "acceptance_criteria", "known_limitations", "owner_lane", "dependencies",
    }
    for group, categories in expected.items():
        for category, expected_ids in categories.items():
            item = actual[(group, category)]
            if item.get("lifecycle_status") != "catalogued":
                fail(f"{group}/{category} must remain catalogued until evidence supports promotion")
            if item.get("implementation_status") not in {"not_implemented", "in_progress", "implemented"}:
                fail(f"{group}/{category} has invalid implementation_status")
            if item.get("verification_status") not in {"not_verified", "verified_with_evidence", "failed", "blocked"}:
                fail(f"{group}/{category} has invalid verification_status")
            contract = item.get("contract") or {}
            missing_fields = required_contract_fields - set(contract)
            if missing_fields:
                fail(f"{group}/{category} missing contract fields: {sorted(missing_fields)}")
            if group != "model" and set(item.get("source_resource_ids", [])) != expected_ids:
                fail(f"{group}/{category} source IDs do not match source catalog")
            if group == "study":
                expected_files = sorted(path for path, rows in study_sets if any(row[2] == category for row in rows))
                if sorted(item.get("source_files", [])) != expected_files:
                    fail(f"study/{category} source file list is stale")
            if group == "model" and item.get("source_item_count") != model_counts.get(category, 0):
                fail(f"model/{category} source item count is stale")
            if group == "division":
                expected_status = "present_in_45_division_sources" if category in audited_divisions else "candidate_only_in_65_registry"
                if item.get("reconciliation_status") != expected_status:
                    fail(f"division/{category} reconciliation status is stale")

    study_ids = [row[0] for row in study_rows]
    if len(study_ids) != len(set(study_ids)):
        fail("study resource IDs must be unique across all study catalogs")

    expected_counts = {
        "registry_categories": len(expected["registry"]),
        "study_categories": len(expected["study"]),
        "model_categories": len(expected["model"]),
        "division_systems": len(expected["division"]),
        "total_category_systems": len(expected_keys),
        "resource_registry_records": len(resources),
        "study_resource_records": len(study_rows),
        "division_count_in_master_registry": len(division_registry["divisions"]),
        "division_count_in_45_profile_audit": len(audited_divisions),
        "division_count_conflict_only_in_65_registry": len(expected["division"]) - len(audited_divisions),
    }
    counts = registry.get("counts", {})
    for key, value in expected_counts.items():
        if counts.get(key) != value:
            fail(f"counts.{key} is stale: expected {value}")
    if sorted(counts.get("study_resource_sets", [])) != sorted(path for path, _ in study_sets):
        fail("counts.study_resource_sets does not match the study catalog files")

    print(
        "Buddy category-system registry: PASS "
        f"({expected_counts['total_category_systems']} systems; "
        f"{expected_counts['registry_categories']} registry, "
        f"{expected_counts['study_categories']} study, "
        f"{expected_counts['model_categories']} model, "
        f"{expected_counts['division_systems']} divisions; "
        f"{expected_counts['study_resource_records']} study records)"
    )
    return 0

if __name__ == "__main__":
    sys.exit(main())
