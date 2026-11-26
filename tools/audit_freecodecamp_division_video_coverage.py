#!/usr/bin/env python3
"""Audit freeCodeCamp source inventory, video routing, and division curriculum coverage.

This is a read-only inventory audit. It never downloads media/transcripts, trains
models, grants rights, approves division ownership, or promotes runtime status.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("buddy/bootcamp/sources/freecodecamp/catalog.json")
CROSSWALK = Path("config/generated/masterbot-55-domain-crosswalk.json")
PROFILES = Path("config/freecodecamp-division-category-profiles.json")
MASTERBOTS = Path("config/masterbot-65-registry.json")
OVERRIDES = Path("config/freecodecamp-division-routing-overrides.json")
ARTIFACTS = Path("config/buddy-division-specialist-course-artifacts.json")
MODULES = (
    "domain_overview", "core_skills", "tools_and_libraries", "task_playbooks",
    "safety_and_rights", "sandbox_lab", "assessment", "capstone",
)


def _read_json(root: Path, relative: Path, errors: list[str]) -> Any:
    path = root / relative
    if not path.is_file():
        errors.append(f"missing_file:{relative.as_posix()}")
        return None
    if not path.stat().st_size:
        errors.append(f"empty_file:{relative.as_posix()}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid_json:{relative.as_posix()}:{type(exc).__name__}")
        return None


def audit(root: Path = ROOT) -> dict[str, Any]:
    errors: list[str] = []
    catalog = _read_json(root, CATALOG, errors) or {}
    crosswalk = _read_json(root, CROSSWALK, errors) or {}
    profiles = _read_json(root, PROFILES, errors) or {}
    masterbots = _read_json(root, MASTERBOTS, errors) or {}
    overrides = _read_json(root, OVERRIDES, errors) or {}
    artifacts = _read_json(root, ARTIFACTS, errors) or {}

    videos = catalog.get("videos") if isinstance(catalog.get("videos"), list) else []
    categories = catalog.get("categories") if isinstance(catalog.get("categories"), list) else []
    category_ids = {str(row.get("id")) for row in categories if isinstance(row, dict) and row.get("id")}
    video_ids = [str(row.get("video_id", "")) for row in videos if isinstance(row, dict)]
    video_id_counts = Counter(video_ids)
    duplicate_ids = sorted(key for key, count in video_id_counts.items() if key and count > 1)
    missing_video_ids = sum(1 for value in video_ids if not value)
    category_distribution: Counter[str] = Counter()
    invalid_video_categories: list[dict[str, Any]] = []
    unclassified_ids: list[str] = []
    for video in videos:
        assigned = [str(value) for value in video.get("categories", []) if isinstance(value, str)]
        category_distribution.update(assigned)
        unknown = sorted(set(assigned) - category_ids)
        if unknown:
            invalid_video_categories.append({"video_id": video.get("video_id"), "unknown": unknown})
        if not assigned or set(assigned) == {"other_or_unclassified"}:
            unclassified_ids.append(str(video.get("video_id", "")))

    domains = crosswalk.get("domains") if isinstance(crosswalk.get("domains"), list) else []
    bot_rows = masterbots.get("divisions") if isinstance(masterbots.get("divisions"), list) else []
    domain_categories = profiles.get("domain_categories") if isinstance(profiles.get("domain_categories"), dict) else {}
    domain_ids = [str(row.get("domain_id", "")) for row in domains if isinstance(row, dict)]
    profile_ids = set(domain_categories)
    config_rows: list[dict[str, Any]] = []
    for domain_id in domain_ids:
        relative = Path("config/divisions") / f"{domain_id}.json"
        config_path = root / relative
        row: dict[str, Any] = {"domain_id": domain_id, "path": relative.as_posix()}
        if not config_path.is_file():
            row["status"] = "missing"
        elif config_path.stat().st_size == 0:
            row["status"] = "empty"
        else:
            try:
                document = json.loads(config_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                row["status"] = "invalid_json"
            else:
                identity = document.get("identity") if isinstance(document.get("identity"), dict) else {}
                capabilities = document.get("capabilities") if isinstance(document.get("capabilities"), list) else []
                tools = document.get("tools") if isinstance(document.get("tools"), list) else []
                connectors = document.get("connectors") if isinstance(document.get("connectors"), list) else []
                workflows = document.get("workflows") if isinstance(document.get("workflows"), list) else []
                benchmarks = document.get("benchmarks") if isinstance(document.get("benchmarks"), list) else []
                required = ("schema", "identity", "mission", "capabilities", "tools", "connectors",
                            "policies", "dependencies", "workflows", "implementationTasks",
                            "benchmarks", "status")
                missing_fields = [field for field in required if field not in document]
                identity_matches = identity.get("id") == domain_id
                row.update({
                    "status": "valid" if not missing_fields and identity_matches else "incomplete",
                    "schema": document.get("schema"),
                    "identity_matches": identity_matches,
                    "missing_fields": missing_fields,
                    "capability_count": len(capabilities),
                    "tool_count": len(tools),
                    "connector_count": len(connectors),
                    "workflow_count": len(workflows),
                    "benchmark_count": len(benchmarks),
                    "declared_status": document.get("status"),
                })
        if domain_id not in profile_ids:
            row["category_profile_missing"] = True
        config_rows.append(row)

    config_counts = Counter(row["status"] for row in config_rows)
    approval_counts = Counter(
        "approved" if row.get("owner_approval") is True else "pending"
        for row in domains if isinstance(row, dict)
    )
    masterbot_approval_counts = Counter(
        "approved" if row.get("owner_approval") is True else "pending"
        for row in crosswalk.get("masterbots", []) if isinstance(row, dict)
    )
    override_entries = overrides.get("entries") if isinstance(overrides.get("entries"), list) else []
    artifact_rows = artifacts.get("artifacts") if isinstance(artifacts.get("artifacts"), list) else []
    expected_targets = len(domains) + len(bot_rows)
    expected_artifacts = expected_targets * len(MODULES)
    artifact_keys = {
        (str(row.get("target_type")), str(row.get("target_id")), str(row.get("module_id")))
        for row in artifact_rows if isinstance(row, dict)
    }
    duplicate_artifact_count = len(artifact_rows) - len(artifact_keys)
    expected_keys = {
        (kind, target_id, module)
        for kind, ids in (
            ("division", domain_ids),
            ("masterbot", [str(row.get("id")) for row in bot_rows if isinstance(row, dict)]),
        )
        for target_id in ids for module in MODULES
    }
    missing_artifact_count = len(expected_keys - artifact_keys)

    inventory = catalog.get("inventory") if isinstance(catalog.get("inventory"), dict) else {}
    inventory_complete = (
        catalog.get("inventory_status") == "complete"
        and inventory.get("complete") is True
        and inventory.get("expected_entry_count") == len(videos)
        and inventory.get("observed_entry_count") == len(videos)
        and inventory.get("null_entry_count") == 0
        and inventory.get("duplicate_video_id_count") == 0
        and not duplicate_ids and missing_video_ids == 0
    )
    blockers: list[str] = []
    if not inventory_complete:
        blockers.append("freecodecamp_video_inventory_not_proven_complete")
    if len(domain_ids) != 55:
        blockers.append("canonical_domain_count_not_55")
    if len(bot_rows) != 65:
        blockers.append("canonical_masterbot_count_not_65")
    if config_counts["missing"]:
        blockers.append(f"missing_division_configs:{config_counts['missing']}")
    if config_counts["empty"]:
        blockers.append(f"empty_division_configs:{config_counts['empty']}")
    if config_counts["invalid_json"]:
        blockers.append(f"invalid_division_configs:{config_counts['invalid_json']}")
    if config_counts["incomplete"]:
        blockers.append(f"incomplete_division_configs:{config_counts['incomplete']}")
    if any(row.get("category_profile_missing") for row in config_rows):
        blockers.append("division_category_profiles_missing")
    if len(profile_ids) != len(domains):
        blockers.append("division_category_profile_count_mismatch")
    if invalid_video_categories:
        blockers.append(f"videos_with_unknown_categories:{len(invalid_video_categories)}")
    if duplicate_ids or missing_video_ids:
        blockers.append("video_id_integrity_failure")
    if missing_artifact_count:
        blockers.append(f"specialist_course_artifacts_missing:{missing_artifact_count}")
    if duplicate_artifact_count:
        blockers.append(f"duplicate_specialist_course_artifacts:{duplicate_artifact_count}")
    if approval_counts["pending"]:
        blockers.append(f"division_owner_approvals_pending:{approval_counts['pending']}")
    if masterbot_approval_counts["pending"]:
        blockers.append(f"masterbot_owner_approvals_pending:{masterbot_approval_counts['pending']}")
    if catalog.get("video_count") != len(videos):
        blockers.append("declared_video_count_mismatch")

    return {
        "schema": "dreamco.freecodecamp_division_video_coverage_audit.v1",
        "status": "blocked" if blockers else "ready_for_review",
        "catalog": {
            "inventory_status": catalog.get("inventory_status"),
            "generated_at": catalog.get("generated_at"),
            "declared_video_count": catalog.get("video_count"),
            "video_rows": len(videos),
            "category_count": len(category_ids),
            "unclassified_video_count": len(unclassified_ids),
            "unclassified_video_ids": unclassified_ids,
            "category_distribution": dict(sorted(category_distribution.items())),
            "expected_entry_count": inventory.get("expected_entry_count"),
            "observed_entry_count": inventory.get("observed_entry_count"),
            "inventory_complete": inventory_complete,
            "duplicate_video_ids": duplicate_ids,
            "missing_video_id_count": missing_video_ids,
            "invalid_video_category_count": len(invalid_video_categories),
            "invalid_video_categories": invalid_video_categories,
        },
        "division_coverage": {
            "expected_domain_count": 55,
            "crosswalk_domain_count": len(domains),
            "category_profile_count": len(profile_ids),
            "division_config_counts": dict(config_counts),
            "owner_approval_counts": dict(approval_counts),
            "masterbot_owner_approval_counts": dict(masterbot_approval_counts),
            "configs": config_rows,
        },
        "masterbot_coverage": {
            "expected_count": 65,
            "registered_count": len(bot_rows),
            "crosswalk_masterbot_count": len(crosswalk.get("masterbots", [])),
        },
        "specialist_curriculum": {
            "required_modules_per_target": len(MODULES),
            "target_count": expected_targets,
            "required_artifact_slots": expected_artifacts,
            "artifact_rows": len(artifact_rows),
            "missing_artifact_slots": missing_artifact_count,
            "duplicate_artifact_rows": duplicate_artifact_count,
        },
        "video_routing": {
            "curated_override_count": len(override_entries),
            "routing_category_count": len(category_ids),
            "division_category_profile_coverage": len(profile_ids),
        },
        "blockers": blockers,
        "errors": errors,
        "truth_boundary": (
            "This read-only report verifies metadata and curriculum inventory only. "
            "It does not prove video study, transcript rights, model training, runtime "
            "connectivity, capability mastery, division ownership approval, or production readiness."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/FREECODECAMP_DIVISION_VIDEO_COVERAGE.json")
    args = parser.parse_args()
    report = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "video_rows": report["catalog"]["video_rows"],
        "unclassified_video_count": report["catalog"]["unclassified_video_count"],
        "division_config_counts": report["division_coverage"]["division_config_counts"],
        "required_artifact_slots": report["specialist_curriculum"]["required_artifact_slots"],
        "missing_artifact_slots": report["specialist_curriculum"]["missing_artifact_slots"],
        "blockers": report["blockers"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
