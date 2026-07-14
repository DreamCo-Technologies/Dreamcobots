#!/usr/bin/env python3
"""Check DreamCo generated libraries and bot memory storage budgets."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLICY_FILE = ROOT / "config/local_first_storage_policy.json"
REPORT_JSON = ROOT / "reports/storage_guard_report.json"
REPORT_MD = ROOT / "reports/STORAGE_GUARD_REPORT.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def size_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def status_for(ok: bool) -> str:
    return "pass" if ok else "fail"


def check_file_size(path: Path, max_mb: float, label: str) -> dict[str, Any]:
    exists = path.exists()
    actual = round(size_mb(path), 3) if exists else None
    ok = exists and actual <= max_mb
    return {
        "name": label,
        "path": rel(path),
        "status": status_for(ok),
        "actual_mb": actual,
        "max_mb": max_mb,
        "message": "within budget" if ok else ("missing file" if not exists else "over budget"),
    }


def check_generated_libraries(policy: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    budgets = policy["size_budgets"]
    paths = policy["generated_library_paths"]
    checks: list[dict[str, Any]] = []

    checks.append(
        check_file_size(
            ROOT / paths["index"],
            budgets["generated_index_max_mb"],
            "system_library_index_budget",
        )
    )
    checks.append(
        check_file_size(
            ROOT / paths["resources_index"],
            budgets["generated_index_max_mb"],
            "resource_manifest_budget",
        )
    )
    for library_path in paths["libraries"]:
        checks.append(
            check_file_size(
                ROOT / library_path,
                budgets["generated_library_max_mb"],
                f"{Path(library_path).stem}_library_budget",
            )
        )

    resource_index_path = ROOT / paths["resources_index"]
    resource_summary = {
        "sharded": False,
        "resource_index_entries": 0,
        "shard_count": 0,
        "resources_per_bot_expected": 100,
        "largest_shard_mb": 0,
        "largest_shard": None,
        "bot_entries_checked": 0,
    }
    resource_failures: list[str] = []

    if resource_index_path.exists():
        resource_index = load_json(resource_index_path)
        resource_summary["sharded"] = resource_index.get("sharded") is True
        resource_summary["resource_index_entries"] = len(resource_index.get("entries", []))
        resource_summary["shard_count"] = len(resource_index.get("shards", []))
        if not resource_summary["sharded"]:
            resource_failures.append("resource index must be sharded")
        if resource_index.get("count") != resource_summary["resource_index_entries"]:
            resource_failures.append("resource index count does not match entries")

        for shard_name in resource_index.get("shards", []):
            shard_path = ROOT / shard_name
            shard_check = check_file_size(
                shard_path,
                budgets["generated_resource_shard_max_mb"],
                f"resource_shard_budget:{Path(shard_name).stem}",
            )
            checks.append(shard_check)
            if shard_check["actual_mb"] is not None and shard_check["actual_mb"] > resource_summary["largest_shard_mb"]:
                resource_summary["largest_shard_mb"] = shard_check["actual_mb"]
                resource_summary["largest_shard"] = shard_check["path"]
            if not shard_path.exists():
                resource_failures.append(f"missing resource shard {shard_name}")
                continue
            shard = load_json(shard_path)
            for entry in shard.get("entries", []):
                resource_summary["bot_entries_checked"] += 1
                resources = entry.get("resources", [])
                if entry.get("resource_count") != len(resources):
                    resource_failures.append(f"{entry.get('bot_id')} resource_count mismatch")
                if len(resources) != resource_summary["resources_per_bot_expected"]:
                    resource_failures.append(f"{entry.get('bot_id')} does not have 100 resources")

    checks.append(
        {
            "name": "resource_sharding_integrity",
            "path": rel(resource_index_path),
            "status": status_for(not resource_failures),
            "actual": resource_summary,
            "max_failures_reported": 10,
            "failures": resource_failures[:10],
            "failure_count": len(resource_failures),
            "message": "resources are sharded and count-safe" if not resource_failures else "resource sharding needs attention",
        }
    )
    return checks, resource_summary


def check_useful_data_policy(policy: dict[str, Any]) -> dict[str, Any]:
    useful_policy = policy.get("useful_data_policy", {})
    keep_categories = useful_policy.get("keep_categories", [])
    drop_categories = useful_policy.get("drop_categories", [])
    required_metadata = useful_policy.get("required_metadata", [])
    score_dimensions = useful_policy.get("score_dimensions", [])
    failures: list[str] = []

    if not useful_policy.get("rule"):
        failures.append("useful_data_policy.rule is required")
    if len(keep_categories) < 5:
        failures.append("useful_data_policy.keep_categories must define at least 5 useful data classes")
    if len(drop_categories) < 5:
        failures.append("useful_data_policy.drop_categories must define at least 5 discard classes")
    for field in ["source", "usefulness_reason", "retention_tier", "dedupe_key", "redaction_state"]:
        if field not in required_metadata:
            failures.append(f"useful_data_policy.required_metadata missing {field}")
    if useful_policy.get("minimum_usefulness_score_to_store", 0) < 1:
        failures.append("minimum_usefulness_score_to_store must be positive")
    if len(score_dimensions) < 3:
        failures.append("score_dimensions must include at least 3 dimensions")

    return {
        "name": "useful_data_policy",
        "path": rel(POLICY_FILE),
        "status": status_for(not failures),
        "keep_categories": len(keep_categories),
        "drop_categories": len(drop_categories),
        "required_metadata": len(required_metadata),
        "score_dimensions": len(score_dimensions),
        "minimum_usefulness_score_to_store": useful_policy.get("minimum_usefulness_score_to_store"),
        "failures": failures,
        "failure_count": len(failures),
        "message": "only useful data policy is active" if not failures else "useful data policy needs attention",
    }


def build_report() -> dict[str, Any]:
    policy = load_json(POLICY_FILE)
    checks, resource_summary = check_generated_libraries(policy)
    checks.append(check_useful_data_policy(policy))
    failed = [check for check in checks if check["status"] != "pass"]
    warnings = []
    if resource_summary["largest_shard_mb"] >= policy["size_budgets"]["generated_resource_shard_max_mb"] * 0.8:
        warnings.append("largest resource shard is at or above 80% of its storage budget")

    return {
        "schema": "dreamco.storage_guard.v1",
        "generated_at": utc_now(),
        "policy_file": rel(POLICY_FILE),
        "summary": {
            "storage_ready": len(failed) == 0,
            "checks": len(checks),
            "failed_checks": len(failed),
            "warnings": len(warnings),
            "memory_tiers": len(policy.get("memory_tiers", [])),
            "partitioning_rules": len(policy.get("partitioning_rules", [])),
            "compaction_rules": len(policy.get("compaction_rules", [])),
            "useful_keep_categories": len(policy.get("useful_data_policy", {}).get("keep_categories", [])),
            "useful_drop_categories": len(policy.get("useful_data_policy", {}).get("drop_categories", [])),
            "useful_required_metadata": len(policy.get("useful_data_policy", {}).get("required_metadata", [])),
            "approval_gates": len(policy.get("approval_gates", [])),
            "largest_resource_shard_mb": resource_summary["largest_shard_mb"],
            "largest_resource_shard": resource_summary["largest_shard"],
            "resource_shard_count": resource_summary["shard_count"],
            "bot_resource_entries_checked": resource_summary["bot_entries_checked"],
        },
        "budgets": policy["size_budgets"],
        "memory_tiers": policy.get("memory_tiers", []),
        "useful_data_policy": policy.get("useful_data_policy", {}),
        "partitioning_rules": policy.get("partitioning_rules", []),
        "compaction_rules": policy.get("compaction_rules", []),
        "checks": checks,
        "warnings": warnings,
        "required_controls": policy.get("required_controls", []),
    }


def write_reports(report: dict[str, Any]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    summary = report["summary"]
    lines = [
        "# DreamCo Storage Guard Report",
        "",
        f"- Generated: {report['generated_at']}",
        f"- Storage ready: {summary['storage_ready']}",
        f"- Checks: {summary['checks']}",
        f"- Failed checks: {summary['failed_checks']}",
        f"- Warnings: {summary['warnings']}",
        f"- Useful keep categories: {summary['useful_keep_categories']}",
        f"- Useful drop categories: {summary['useful_drop_categories']}",
        f"- Useful required metadata fields: {summary['useful_required_metadata']}",
        f"- Largest resource shard: {summary['largest_resource_shard']} ({summary['largest_resource_shard_mb']} MB)",
        f"- Bot resource entries checked: {summary['bot_resource_entries_checked']}",
        "",
        "## Budgets",
        "",
    ]
    for name, value in report["budgets"].items():
        lines.append(f"- `{name}`: {value}")
    lines.extend(["", "## Checks", ""])
    for check in report["checks"]:
        lines.append(f"- `{check['status']}` {check['name']} — {check['message']}")
    if report["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in report["warnings"])
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DreamCo storage budgets and sharding.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any check fails.")
    args = parser.parse_args()

    report = build_report()
    write_reports(report)
    print(
        "storage_ready={ready} checks={checks} failed={failed} largest_shard_mb={largest}".format(
            ready=report["summary"]["storage_ready"],
            checks=report["summary"]["checks"],
            failed=report["summary"]["failed_checks"],
            largest=report["summary"]["largest_resource_shard_mb"],
        )
    )
    if args.strict and not report["summary"]["storage_ready"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
