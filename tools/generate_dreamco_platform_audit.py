#!/usr/bin/env python3
"""Generate a DreamCo platform audit for Buddy and the Actions dashboard."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def count_files(pattern: str) -> int:
    return sum(1 for _ in ROOT.glob(pattern))


def load_bot_profiles() -> list[dict[str, Any]]:
    profiles = []
    for path in sorted((ROOT / "bots").glob("*/bot_profile.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        data["_path"] = str(path.relative_to(ROOT))
        data["_has_runtime"] = (path.parent / "runtime.py").exists()
        profiles.append(data)
    return profiles


def summarize_bots(profiles: list[dict[str, Any]]) -> dict[str, Any]:
    divisions = Counter(profile.get("division", "Unassigned") for profile in profiles)
    tiers = Counter(profile.get("tier", "unknown") for profile in profiles)
    categories = Counter(profile.get("category", "uncategorized") for profile in profiles)
    return {
        "profiles": len(profiles),
        "runtimes": sum(1 for profile in profiles if profile["_has_runtime"]),
        "division_count": len(divisions),
        "top_divisions": divisions.most_common(12),
        "tiers": dict(sorted(tiers.items())),
        "top_categories": categories.most_common(12),
    }


def summarize_libraries() -> dict[str, Any]:
    library_dir = ROOT / "config" / "generated" / "system_libraries"
    counts: dict[str, int] = {}
    for path in sorted(library_dir.glob("*.json")):
        if path.name == "index.json":
            continue
        data = read_json(path, {})
        if isinstance(data, dict):
            if isinstance(data.get("items"), list):
                counts[path.stem] = len(data["items"])
            elif isinstance(data.get("contracts"), list):
                counts[path.stem] = len(data["contracts"])
            elif isinstance(data.get(path.stem), list):
                counts[path.stem] = len(data[path.stem])
            else:
                counts[path.stem] = count_nested_records(data)
        elif isinstance(data, list):
            counts[path.stem] = len(data)
    return {
        "library_count": len(counts),
        "coverage_counts": counts,
        "all_cover_bots": len(set(counts.values())) == 1 if counts else False,
    }


def count_nested_records(value: Any) -> int:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        return sum(count_nested_records(item) for item in value.values())
    return 0


def build_audit() -> dict[str, Any]:
    profiles = load_bot_profiles()
    bot_summary = summarize_bots(profiles)
    libraries = summarize_libraries()
    inventory = read_json(ROOT / "reports" / "buddy_capability_inventory.json", {})
    triage = read_json(ROOT / "reports" / "github_triage_report.json", {})
    cost_saver = read_json(ROOT / "reports" / "github_cost_saver_report.json", {})
    operating_model = read_json(ROOT / "config" / "dreamco_company_builder_operating_model.json", {})
    goals = read_json(ROOT / "config" / "github_goal_consolidation.json", {})

    readiness = inventory.get("summary", {})
    high_risk = readiness.get("buddy_money_approval_required_bots", 0)
    production_ready = readiness.get("production_ready_bots", 0)

    return {
        "schema": "dreamco.platform_audit.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo": "DreamCo-Technologies/Dreamcobots",
        "positioning": operating_model.get("positioning", {}),
        "bot_fleet": bot_summary,
        "system_libraries": libraries,
        "automation": {
            "workflow_count": count_files(".github/workflows/*.yml") + count_files(".github/workflows/*.yaml"),
            "test_file_count": count_files("tests/**/*.py"),
            "frontend_test_count": count_files("dreamco-control-tower/frontend/src/**/*.test.jsx"),
            "reports_count": count_files("reports/*"),
        },
        "readiness": {
            "fully_coded_bots": readiness.get("fully_coded_bots", bot_summary["runtimes"]),
            "production_ready_bots": production_ready,
            "approval_gated_bots": high_risk,
            "all_bots_have_runtime": bot_summary["profiles"] == bot_summary["runtimes"],
            "all_system_libraries_cover_profiled_bots": readiness.get("all_system_libraries_cover_profiled_bots", libraries["all_cover_bots"]),
        },
        "forever_systems": [
            "Buddy capability inventory",
            "GitHub triage scan",
            "GitHub cost saver bot",
            "Generated bot smoke tests",
            "Global learning system",
            "System library builders",
            "Actions dashboard and GitHub Pages preview",
        ],
        "trust_controls": operating_model.get("approval_gates", []),
        "github_cleanup": {
            "open_prs_reported": triage.get("summary", {}).get("open_prs", 0),
            "open_issues_reported": triage.get("summary", {}).get("open_issues", 0),
            "pr_restart_queue": triage.get("summary", {}).get("pr_restart_queue", 0),
            "current_goal_decisions": {
                "pull_requests": len(goals.get("pull_requests", [])),
                "issues": len(goals.get("issues", [])),
                "keep_items": sum(1 for item in goals.get("issues", []) if str(item.get("decision", "")).startswith("keep")),
                "archive_items": sum(1 for item in goals.get("issues", []) if "archive" in str(item.get("decision", ""))),
            },
        },
        "cost_control": cost_saver.get("summary", {}),
        "executive_assessment": [
            "DreamCo is already organized as an AI workforce operating system, not just a bot list.",
            "Buddy should be presented as the trust interface: evidence, approvals, risk gates, and client-ready explanations.",
            "The immediate product focus should be turning bot runtimes into sellable AI companies, departments, and employees.",
            "The strategic backlog should keep Revenue OS, living divisions, skill runtime, ontology, and connector goals.",
            "Older upload/import issues should become archive references unless they contain missing unique assets.",
        ],
        "next_build_targets": [
            "Per-bot company prospectus generated from bot_profile.json",
            "Book of Associations and partnership resource library",
            "Universal sales representative workflow for each bot",
            "Skill manifest runtime with sandboxed execution",
            "Live division telemetry feeding the Actions dashboard",
            "PR duplicate cleanup after current dashboard branch is pushed",
        ],
    }


def write_markdown(audit: dict[str, Any], path: Path) -> None:
    readiness = audit["readiness"]
    cleanup = audit["github_cleanup"]
    cost = audit.get("cost_control", {})
    lines = [
        "# DreamCo Platform Audit",
        "",
        f"Generated: {audit['generated_at']}",
        "",
        "## Executive Positioning",
        "",
        audit.get("positioning", {}).get("promise", "Buddy is the trust layer for DreamCo."),
        "",
        "## Fleet Readiness",
        "",
        f"- Bot profiles scanned locally: {audit['bot_fleet']['profiles']}",
        f"- Bot runtimes present locally: {audit['bot_fleet']['runtimes']}",
        f"- Production-ready bots from inventory: {readiness['production_ready_bots']}",
        f"- Approval-gated bots: {readiness['approval_gated_bots']}",
        f"- System libraries: {audit['system_libraries']['library_count']}",
        f"- Workflow files: {audit['automation']['workflow_count']}",
        f"- Python test files: {audit['automation']['test_file_count']}",
        "",
        "## Buddy Trust Layer",
        "",
        "Buddy should be the face of AI and human trust: every client-facing claim should connect to evidence, tests, approvals, and a visible risk state.",
        "",
        "Trust gates:",
        *[f"- {gate}" for gate in audit.get("trust_controls", [])],
        "",
        "## Forever Systems",
        "",
        *[f"- {system}" for system in audit["forever_systems"]],
        "",
        "## GitHub Goal Cleanup",
        "",
        f"- Open PRs in latest triage report: {cleanup['open_prs_reported']}",
        f"- Open issues in latest triage report: {cleanup['open_issues_reported']}",
        f"- PR restart queue: {cleanup['pr_restart_queue']}",
        f"- Consolidated issue decisions: {cleanup['current_goal_decisions']['issues']}",
        f"- Strategic goals kept: {cleanup['current_goal_decisions']['keep_items']}",
        f"- Archive/reference items: {cleanup['current_goal_decisions']['archive_items']}",
        "",
        "## Cost Control",
        "",
        f"- Cost saver findings: {cost.get('finding_count', 0)}",
        f"- High severity cost risks: {cost.get('high_severity', 0)}",
        f"- Estimated monthly avoidable risk: ${cost.get('estimated_monthly_savings_usd', 0)}",
        "",
        "## Next Build Targets",
        "",
        *[f"- {target}" for target in audit["next_build_targets"]],
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    audit = build_audit()
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "dreamco_platform_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    write_markdown(audit, reports / "DREAMCO_PLATFORM_AUDIT.md")
    print(json.dumps({
        "report": "reports/DREAMCO_PLATFORM_AUDIT.md",
        "bot_profiles": audit["bot_fleet"]["profiles"],
        "bot_runtimes": audit["bot_fleet"]["runtimes"],
        "production_ready": audit["readiness"]["production_ready_bots"],
        "approval_gated": audit["readiness"]["approval_gated_bots"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
