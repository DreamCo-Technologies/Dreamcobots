#!/usr/bin/env python3
"""Deterministically reconcile Buddy category systems with current source catalogs."""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "config/buddy/category-system-registry.json"
MIRROR_PATH = ROOT / "website/data/category-system-registry.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", normalized.lower())).strip("_") or "category"


def study_record(category: str, source_files: list[str], source_ids: list[str], used_ids: set[str]) -> dict:
    base = f"study_{slug(category)}"
    record_id = base
    suffix = 2
    while record_id in used_ids:
        record_id = f"{base}_{suffix}"
        suffix += 1
    used_ids.add(record_id)
    return {
        "id": record_id,
        "category": category,
        "group": "study",
        "source": source_files[0] if len(source_files) == 1 else "multiple",
        "source_files": source_files,
        "source_resource_ids": source_ids,
        "source_item_count": len(source_ids),
        "section_anchor": f"study-{slug(category)}",
        "lifecycle_status": "catalogued",
        "implementation_status": "not_implemented",
        "verification_status": "not_verified",
        "contract": {
            "mission": f"Dedicated Buddy study and research subsystem for the exact source category {json.dumps(category, ensure_ascii=False)}.",
            "inputs": ["Versioned source records", "Approved task requests", "Policy and provenance metadata"],
            "outputs": ["Category-specific knowledge and artifacts", "Structured status and evidence records", "Recommendations or controlled execution requests"],
            "permissions": ["Least privilege", "No external side effects without required approval"],
            "safety_controls": ["Input validation", "Provenance checks", "Explicit blocked/error states", "Audit trail"],
            "metrics": ["Correctness", "Coverage", "Freshness", "Reliability", "Cost where applicable"],
            "acceptance_criteria": ["Dedicated interface and schema", "Owner assigned", "Unit and integration tests", "Category-specific benchmark or checklist", "Documented failure and rollback behavior"],
            "known_limitations": ["Subsystem is specified but not implemented or runtime-verified."],
            "owner_lane": None,
            "dependencies": ["buddy_master_orchestrator", "buddy_policy_system", "buddy_observability_system"],
        },
    }


def build(root: Path = ROOT) -> tuple[dict, dict]:
    registry_path = root / "config/buddy/category-system-registry.json"
    resource_path = root / "config/buddy/resource-registry.json"
    division_path = root / "config/masterbot-65-registry.json"
    audit_path = root / "reports/BOT_DIVISION_PLACEMENT_AUDIT.md"
    model_path = root / "shared/ai-models.ts"

    registry = load(registry_path)
    resources = load(resource_path)["resources"]
    divisions = load(division_path)["divisions"]
    study_paths = sorted((root / "config").glob("buddy-study-resources-*.json"))
    if not study_paths:
        raise ValueError("No buddy study-resource catalogs were found")

    study_map: dict[str, dict[str, set[str] | list[str]]] = {}
    study_rows = []
    for path in study_paths:
        relative = path.relative_to(root).as_posix()
        for row in load(path)["resources"]:
            category = row[2]
            entry = study_map.setdefault(category, {"files": set(), "ids": []})
            entry["files"].add(relative)
            entry["ids"].append(f"study_resource_{row[0]}")
            study_rows.append(row)

    model_source = model_path.read_text(encoding="utf-8")
    model_categories = re.findall(r'category:\\s*"([^"]+)"', model_source)
    if not model_categories:
        raise ValueError("No model categories found in shared/ai-models.ts")
    model_counts = dict(Counter(model_categories))
    registry_categories = sorted({item["category"] for item in resources})
    model_category_names = sorted(set(model_categories))

    audited_divisions = set(re.findall(
        r"^\\| ([A-Za-z][A-Za-z0-9]+) \\| \\d+ \\|",
        audit_path.read_text(encoding="utf-8"),
        re.MULTILINE,
    ))

    existing = {(item.get("group"), item.get("category")): item for item in registry["systems"]}
    used_ids = {item.get("id") for item in registry["systems"]}
    for category in sorted(study_map):
        entry = study_map[category]
        source_files = sorted(entry["files"])
        source_ids = sorted(entry["ids"])
        item = existing.get(("study", category))
        if item is None:
            item = study_record(category, source_files, source_ids, used_ids)
            registry["systems"].append(item)
            existing[("study", category)] = item
        item["source_files"] = source_files
        item["source_resource_ids"] = source_ids
        item["source_item_count"] = len(source_ids)
        item["source"] = source_files[0] if len(source_files) == 1 else "multiple"
        item.setdefault("section_anchor", f"study-{slug(category)}")

    registry["authority"]["study_resources"] = "config/buddy-study-resources-*.json"
    expected_active = (
        len(registry_categories)
        + len(study_map)
        + len(model_category_names)
        + len(divisions)
    )
    expected_keys = {
        ("registry", category) for category in registry_categories
    } | {
        ("study", category) for category in study_map
    } | {
        ("model", category) for category in model_category_names
    } | {
        ("division", item["name"]) for item in divisions
    }
    legacy = [
        item for item in registry["systems"]
        if (item.get("group"), item.get("category")) not in expected_keys
    ]

    counts = registry["counts"]
    counts.update({
        "registry_categories": len(registry_categories),
        "study_categories": len(study_map),
        "model_categories": len(model_category_names),
        "division_systems": len(divisions),
        "total_category_systems": expected_active,
        "total_records_including_legacy": len(registry["systems"]),
        "legacy_model_categories": len(legacy),
        "model_catalog_entries_by_category": model_counts,
        "resource_registry_records": len(resources),
        "study_resource_records": len(study_rows),
        "study_resource_sets": [path.relative_to(root).as_posix() for path in study_paths],
        "division_count_in_master_registry": len(divisions),
        "division_count_in_placement_audit": len(audited_divisions),
        "division_count_in_master_registry_not_in_placement_audit": len(divisions) - len(audited_divisions),
    })
    return registry, registry


def render(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated files differ from source catalogs")
    args = parser.parse_args()
    registry, mirror = build()
    registry_text = render(registry)
    mirror_text = render(mirror)
    stale = []
    if not REGISTRY_PATH.exists() or REGISTRY_PATH.read_text(encoding="utf-8") != registry_text:
        stale.append(REGISTRY_PATH.relative_to(ROOT).as_posix())
    if not MIRROR_PATH.exists() or MIRROR_PATH.read_text(encoding="utf-8") != mirror_text:
        stale.append(MIRROR_PATH.relative_to(ROOT).as_posix())
    if args.check:
        if stale:
            raise SystemExit("Buddy category-system generated artifacts are stale: " + ", ".join(stale))
        print(f"Buddy category-system generator: PASS ({registry['counts']['study_categories']} study categories; {registry['counts']['study_resource_records']} study resources)")
        return 0
    REGISTRY_PATH.write_text(registry_text, encoding="utf-8")
    MIRROR_PATH.write_text(mirror_text, encoding="utf-8")
    print(f"Buddy category-system registry refreshed ({registry['counts']['total_records_including_legacy']} records)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
