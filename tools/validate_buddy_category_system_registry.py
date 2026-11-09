#!/usr/bin/env python3
"""Validate Buddy's dedicated category-system registry against source catalogs."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "config/buddy/category-system-registry.json"
RESOURCE_PATH = ROOT / "config/buddy/resource-registry.json"
STUDY_PATH = ROOT / "config/buddy-study-resources-101-200.json"
MODEL_PATH = ROOT / "shared/ai-models.ts"

def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)

def fail(message: str) -> None:
    raise SystemExit(f"Buddy category-system registry: FAIL: {message}")

def main() -> int:
    registry = load_json(REGISTRY_PATH)
    resources = load_json(RESOURCE_PATH)["resources"]
    study_rows = load_json(STUDY_PATH)["resources"]
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
            item["category"]: {resource["id"] for resource in resources if resource["category"] == item["category"]}
            for item in resources
        },
        "study": {
            row[2]: {f"study_resource_{entry[0]}" for entry in study_rows if entry[2] == row[2]}
            for row in study_rows
        },
        "model": {},
    }
    model_block = re.search(r"AI_MODEL_CATEGORIES\s*=\s*\\[(.*?)\\]\s*as const", model_source, re.S)
    if not model_block:
        fail("could not locate AI_MODEL_CATEGORIES in shared/ai-models.ts")
    model_categories = re.findall(r'"([^"]+)"', model_block.group(1))
    model_counts = Counter(re.findall(r'category:\s*"([^"]+)"', model_source))
    expected["model"] = {category: set() for category in model_categories}

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
                fail(f"{group}/{category} source resource IDs do not match source catalog")
            if group == "model" and item.get("source_item_count") != model_counts.get(category, 0):
                fail(f"model/{category} source item count is stale")

    expected_counts = {
        "registry_categories": len(expected["registry"]),
        "study_categories": len(expected["study"]),
        "model_categories": len(expected["model"]),
        "total_category_systems": len(expected_keys),
        "resource_registry_records": len(resources),
        "study_resource_records": len(study_rows),
    }
    for key, value in expected_counts.items():
        if registry.get("counts", {}).get(key) != value:
            fail(f"counts.{key} is stale: expected {value}")

    print(
        "Buddy category-system registry: PASS "
        f"({expected_counts['total_category_systems']} systems; "
        f"{expected_counts['registry_categories']} registry, "
        f"{expected_counts['study_categories']} study, "
        f"{expected_counts['model_categories']} model categories)"
    )
    return 0

if __name__ == "__main__":
    sys.exit(main())
