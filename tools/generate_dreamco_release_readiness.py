#!/usr/bin/env python3
"""Generate the DreamCo release readiness comparison report.

This report compares the DreamCo 1.0 plan against repository evidence so the
Actions dashboard can show what is complete, active, blocked, and next.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
CONFIG_DIR = ROOT / "config"
SCORECARD_FILE = CONFIG_DIR / "dreamco_1_0_consolidation_scorecard.json"


@dataclass(frozen=True)
class Evidence:
    status: str
    proof: list[str]
    missing: list[str]


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report read failures as evidence.
        return {"_error": str(exc)}


def git_branch() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "branch", "--show-current"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def file_exists(relative_path: str) -> bool:
    return (ROOT / relative_path).exists()


def evidence_from_requirements(requirements: dict[str, str]) -> Evidence:
    proof: list[str] = []
    missing: list[str] = []
    for label, relative_path in requirements.items():
        if file_exists(relative_path):
            proof.append(f"{label}: {relative_path}")
        else:
            missing.append(f"{label}: {relative_path}")
    if missing and proof:
        status = "active"
    elif missing:
        status = "blocked"
    else:
        status = "complete"
    return Evidence(status=status, proof=proof, missing=missing)


def first_ten_status(scorecard: dict[str, Any]) -> list[dict[str, Any]]:
    definitions = {
        "correct_registry_and_readme_counts": {
            "title": "Correct registry and README counts",
            "requirements": {
                "README truth copy": "README.md",
                "Consolidation scorecard": "config/dreamco_1_0_consolidation_scorecard.json",
                "Capability inventory": "reports/buddy_capability_inventory.json",
            },
            "next": "Keep all public claims tied to generated reports.",
        },
        "classify_all_profiles_by_implementation_status": {
            "title": "Classify all profiles by implementation status",
            "requirements": {
                "Buddy capability inventory": "reports/buddy_capability_inventory.json",
                "Bot production contract validator": "tools/validate_bot_production_contracts.py",
                "Generated smoke results": "reports/generated_bot_smoke_results.json",
            },
            "next": "Normalize every profile with runtime, tests, permissions, and maturity evidence.",
        },
        "triage_open_pull_requests": {
            "title": "Triage open pull requests",
            "requirements": {
                "GitHub triage report": "reports/github_triage_report.json",
                "Repository stewardship report": "reports/repository_stewardship_report.json",
                "Goal consolidation map": "config/github_goal_consolidation.json",
            },
            "next": "Sort the open PR queue into merge, rebuild, replace, duplicate, and close candidates.",
        },
        "repair_required_ci_pipeline": {
            "title": "Repair required CI pipeline",
            "requirements": {
                "Repository steward": "tools/repository_steward.py",
                "Storage guard": "tools/storage_guard.py",
                "Bot connection guard": "tools/buddy_bot_connection_guard.py",
            },
            "next": "Make one required CI path green before expanding optional workflows.",
        },
        "complete_command_center_consolidation_decision": {
            "title": "Complete Command Center consolidation decision",
            "requirements": {
                "Command Center component": "dreamco-control-tower/frontend/src/components/CommandCenter.jsx",
                "Buddy Command Center component": "dreamco-control-tower/frontend/src/components/BuddyCommandCenter.jsx",
                "Actions page command surface": "dreamco-control-tower/frontend/src/components/ActionsPage.jsx",
            },
            "next": "Keep one official dashboard path and retire duplicate dashboard experiments only after coverage is preserved.",
        },
        "make_buddy_use_master_registry_for_real_routing": {
            "title": "Make Buddy use the registry for real routing",
            "requirements": {
                "Master registry": "config/master_bot_registry.json",
                "Buddy master registry adapter": "BuddyAI/master_registry.py",
                "Buddy connection guard": "tools/buddy_bot_connection_guard.py",
            },
            "next": "Replace any first-match routing with scored registry routing and fallback plans.",
        },
        "enforce_approval_risk_spending_and_autonomy": {
            "title": "Enforce approval, risk, spending, and autonomy",
            "requirements": {
                "High-risk approval registry": "config/production_approvals/high_risk_bot_approvals.json",
                "Local-first storage policy": "config/local_first_storage_policy.json",
                "Autonomous business policy": "config/autonomous_business_engine.json",
            },
            "next": "Turn approval policies into runtime gates with audit entries and user confirmation states.",
        },
        "launch_bot_fleet_and_failure_center": {
            "title": "Launch Bot Fleet and Failure Center",
            "requirements": {
                "Actions page": "dreamco-control-tower/frontend/src/components/ActionsPage.jsx",
                "GitHub triage report": "reports/github_triage_report.json",
                "Repository stewardship report": "reports/repository_stewardship_report.json",
            },
            "next": "Connect dashboard queues to backend actions for retest packets, not silent live changes.",
        },
        "make_five_bot_products_work_end_to_end": {
            "title": "Make five bot products work end to end",
            "requirements": {
                "Company builder operating model": "config/dreamco_company_builder_operating_model.json",
                "Prospectus pages": "docs/bots",
                "Stripe revenue rescue": "reports/stripe_revenue_rescue_report.json",
            },
            "next": "Pick the five first paid offers and prove signup, sandbox, dashboard, support, and payment paths.",
        },
        "publish_dreamco_1_0_readiness_scorecard": {
            "title": "Publish DreamCo 1.0 readiness scorecard",
            "requirements": {
                "Release readiness generator": "tools/generate_dreamco_release_readiness.py",
                "Scorecard docs": "docs/DREAMCO_1_0_CONSOLIDATION_SCORECARD.md",
                "Top 100 docs": "docs/DREAMCO_TOP_100_UPDATE_BACKLOG.md",
            },
            "next": "Keep this generated report visible in Actions and refresh it before every PR.",
        },
    }

    ordered = scorecard.get("first_ten_updates", [])
    items: list[dict[str, Any]] = []
    for update_id in ordered:
        definition = definitions.get(
            update_id,
            {
                "title": update_id.replace("_", " ").title(),
                "requirements": {},
                "next": "Add evidence requirements for this update.",
            },
        )
        evidence = evidence_from_requirements(definition["requirements"])
        items.append(
            {
                "id": update_id,
                "title": definition["title"],
                "status": evidence.status,
                "proof": evidence.proof,
                "missing": evidence.missing,
                "next": definition["next"],
            },
        )
    return items


def apply_runtime_status_overrides(items: list[dict[str, Any]], reports: dict[str, Any]) -> list[dict[str, Any]]:
    inventory_summary = reports["inventory"].get("summary", {})
    steward_summary = reports["steward"].get("summary", {})
    stripe_summary = reports["stripe"].get("summary", {})
    bot_count = int(inventory_summary.get("bot_profiles_scanned", 0) or 0)
    production_ready = int(inventory_summary.get("production_ready_bots", 0) or 0)
    failed_runs = int(steward_summary.get("failed_workflow_runs", 0) or 0)
    open_prs = int(steward_summary.get("open_prs", 0) or 0)
    restart_queue = int(steward_summary.get("restart_queue", 0) or 0)
    revenue_ready = bool(stripe_summary.get("revenue_rescue_ready"))

    active_overrides: dict[str, str] = {}
    if bot_count and production_ready < bot_count:
        active_overrides["classify_all_profiles_by_implementation_status"] = (
            "Profiles are inventoried, but not every bot is production-ready yet."
        )
    if open_prs or restart_queue:
        active_overrides["triage_open_pull_requests"] = (
            "Triage exists, but open PRs and restart/retest work still remain."
        )
    if failed_runs:
        active_overrides["repair_required_ci_pipeline"] = (
            "Local quality gates are clean, but failed workflow runs still need retest or repair."
        )
        active_overrides["launch_bot_fleet_and_failure_center"] = (
            "The failure center is visible, but failed workflow work is still active."
        )
    active_overrides["make_buddy_use_master_registry_for_real_routing"] = (
        "Registry and connection proof exist; scored live routing, fallbacks, and cancellation still need deeper runtime enforcement."
    )
    active_overrides["enforce_approval_risk_spending_and_autonomy"] = (
        "Approval policies exist; runtime enforcement and audit logging still need full proof."
    )
    if not revenue_ready:
        active_overrides["make_five_bot_products_work_end_to_end"] = (
            "Product packaging exists, but revenue rescue is not ready, so paid end-to-end proof remains active."
        )

    adjusted: list[dict[str, Any]] = []
    for item in items:
        override = active_overrides.get(item["id"])
        if override and item["status"] == "complete":
            item = {
                **item,
                "status": "active",
                "next": override,
            }
        adjusted.append(item)
    return adjusted


def group_status(scorecard: dict[str, Any], reports: dict[str, Any]) -> list[dict[str, Any]]:
    inventory_summary = reports["inventory"].get("summary", {})
    steward_summary = reports["steward"].get("summary", {})
    storage_summary = reports["storage"].get("summary", {})
    stripe_summary = reports["stripe"].get("summary", {})
    productivity_summary = reports["productivity"].get("summary", {})
    ops_report = reports["ops"] if isinstance(reports["ops"], dict) else {"count": len(reports["ops"])}

    group_evidence = {
        "repository_stability": {
            "metrics": {
                "open_prs": steward_summary.get("open_prs", 0),
                "failed_workflow_runs": steward_summary.get("failed_workflow_runs", 0),
                "failed_quality_checks": steward_summary.get("failed_quality_checks", 0),
            },
            "status": "active" if steward_summary.get("failed_quality_checks", 1) == 0 else "blocked",
            "next": "Use the cleanroom queue to reduce stale PRs and failed workflow runs.",
        },
        "bot_truth_registry": {
            "metrics": {
                "profiles_scanned": inventory_summary.get("bot_profiles_scanned", 0),
                "production_ready_bots": inventory_summary.get("production_ready_bots", 0),
                "placeholder_review": inventory_summary.get("placeholder_marker_bots", 0),
            },
            "status": "active",
            "next": "Continue turning profiles into runtime-proven bots with direct tests.",
        },
        "public_docs_identity": {
            "metrics": {
                "scorecard_docs": int(file_exists("docs/DREAMCO_1_0_CONSOLIDATION_SCORECARD.md")),
                "top_100_docs": int(file_exists("docs/DREAMCO_TOP_100_UPDATE_BACKLOG.md")),
                "progress_docs": int(file_exists("docs/DREAMCO_PROGRESS_WEEKEND.md")),
            },
            "status": "complete",
            "next": "Refresh docs from generated evidence instead of manual claims.",
        },
        "buddy_control_plane": {
            "metrics": {
                "buddy_connected_bots": reports["connections"].get("summary", {}).get("buddy_connected_bots", 0),
                "actions_testable_bots": reports["connections"].get("summary", {}).get("actions_page_testable_bots", 0),
                "ops_packets": ops_report.get("count", 0),
            },
            "status": "active",
            "next": "Add scored routing, cancellation, and approval inbox actions.",
        },
        "operational_dashboard": {
            "metrics": {
                "productivity_score": productivity_summary.get("productivity_score", 0),
                "storage_ready": storage_summary.get("storage_ready", False),
                "revenue_rescue_ready": stripe_summary.get("revenue_rescue_ready", False),
            },
            "status": "active" if storage_summary.get("storage_ready") else "blocked",
            "next": "Keep dashboard-backed checks green and connect revenue fixes to real offer evidence.",
        },
        "trustworthy_autonomy": {
            "metrics": {
                "approval_gates": storage_summary.get("approval_gates", 0),
                "approval_gated_bots": productivity_summary.get("approval_gated_bots", 0),
                "storage_failed_checks": storage_summary.get("failed_checks", 0),
            },
            "status": "active" if storage_summary.get("failed_checks", 1) == 0 else "blocked",
            "next": "Convert policies into runtime enforcement, audit log, export/delete, shadow tests, and rollback.",
        },
    }

    groups: list[dict[str, Any]] = []
    for group in scorecard.get("top_100_update_groups", []):
        evidence = group_evidence.get(group["id"], {})
        groups.append(
            {
                "id": group["id"],
                "title": group["id"].replace("_", " ").title(),
                "planned_updates": group.get("count", 0),
                "status": evidence.get("status", "active"),
                "metrics": evidence.get("metrics", {}),
                "focus": group.get("focus", []),
                "first_move": group.get("first_move"),
                "next": evidence.get("next", "Continue evidence-backed implementation."),
            },
        )
    return groups


def summarize(first_ten: list[dict[str, Any]], groups: list[dict[str, Any]], reports: dict[str, Any]) -> dict[str, Any]:
    completed = sum(1 for item in first_ten if item["status"] == "complete")
    active = sum(1 for item in first_ten if item["status"] == "active")
    blocked = sum(1 for item in first_ten if item["status"] == "blocked")
    group_complete = sum(1 for item in groups if item["status"] == "complete")
    group_active = sum(1 for item in groups if item["status"] == "active")
    group_blocked = sum(1 for item in groups if item["status"] == "blocked")
    first_ten_score = ((completed + (active * 0.5)) / max(len(first_ten), 1)) * 45
    group_score = ((group_complete + (group_active * 0.5)) / max(len(groups), 1)) * 30
    steward_summary = reports["steward"].get("summary", {})
    storage_summary = reports["storage"].get("summary", {})
    stripe_summary = reports["stripe"].get("summary", {})
    quality_score = 10 if steward_summary.get("failed_quality_checks", 1) == 0 else 0
    storage_score = 8 if storage_summary.get("storage_ready") else 0
    revenue_score = 7 if stripe_summary.get("revenue_rescue_ready") else 0
    readiness_score = round(first_ten_score + group_score + quality_score + storage_score + revenue_score, 2)
    return {
        "release_readiness_score": min(100, readiness_score),
        "first_ten_complete": completed,
        "first_ten_active": active,
        "first_ten_blocked": blocked,
        "top_100_groups_complete": group_complete,
        "top_100_groups_active": group_active,
        "top_100_groups_blocked": group_blocked,
        "open_prs": reports["steward"].get("summary", {}).get("open_prs", 0),
        "open_issues": reports["steward"].get("summary", {}).get("open_issues", 0),
        "failed_workflow_runs": reports["steward"].get("summary", {}).get("failed_workflow_runs", 0),
        "failed_quality_checks": reports["steward"].get("summary", {}).get("failed_quality_checks", 0),
        "production_ready_bots": reports["inventory"].get("summary", {}).get("production_ready_bots", 0),
        "bot_profiles_scanned": reports["inventory"].get("summary", {}).get("bot_profiles_scanned", 0),
        "storage_ready": reports["storage"].get("summary", {}).get("storage_ready", False),
        "revenue_rescue_ready": reports["stripe"].get("summary", {}).get("revenue_rescue_ready", False),
    }


def build_report() -> dict[str, Any]:
    scorecard = read_json(SCORECARD_FILE, {})
    reports = {
        "inventory": read_json(REPORT_DIR / "buddy_capability_inventory.json", {}),
        "steward": read_json(REPORT_DIR / "repository_stewardship_report.json", {}),
        "storage": read_json(REPORT_DIR / "storage_guard_report.json", {}),
        "stripe": read_json(REPORT_DIR / "stripe_revenue_rescue_report.json", {}),
        "productivity": read_json(REPORT_DIR / "buddy_productivity_tracker.json", {}),
        "connections": read_json(REPORT_DIR / "buddy_bot_connection_report.json", {}),
        "ops": read_json(REPORT_DIR / "buddy_ops_queue.json", {"count": 0, "operations": []}),
    }
    first_ten = apply_runtime_status_overrides(first_ten_status(scorecard), reports)
    groups = group_status(scorecard, reports)
    summary = summarize(first_ten, groups, reports)
    blocked_items = [item for item in first_ten if item["status"] == "blocked"]
    active_items = [item for item in first_ten if item["status"] == "active"]

    return {
        "schema": "dreamco.release_readiness.v1",
        "generated_at": iso_now(),
        "branch": git_branch(),
        "mission": scorecard.get("mission", "Make DreamCo reliable, demonstrable, and evidence-backed."),
        "summary": summary,
        "first_ten_updates": first_ten,
        "top_100_groups": groups,
        "already_done": [item for item in first_ten if item["status"] == "complete"],
        "currently_building": active_items,
        "blocked_or_unproven": blocked_items,
        "next_actions": [
            "Refresh capability, stewardship, storage, Stripe, and bot connection reports before every release PR.",
            "Reduce the PR restart queue before adding more bots or major dashboard surfaces.",
            "Promote five bot products only after signup, sandbox, payment, support, and dashboard proof all exist.",
            "Keep Buddy supervised for live money, outreach, deployment, credential, and customer-impacting actions.",
        ],
        "sources": {
            "scorecard": str(SCORECARD_FILE.relative_to(ROOT)),
            "capability_inventory": "reports/buddy_capability_inventory.json",
            "repository_stewardship": "reports/repository_stewardship_report.json",
            "storage_guard": "reports/storage_guard_report.json",
            "stripe_revenue_rescue": "reports/stripe_revenue_rescue_report.json",
            "buddy_bot_connections": "reports/buddy_bot_connection_report.json",
        },
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# DreamCo Release Readiness",
        "",
        f"Generated: {report['generated_at']}",
        f"Branch: `{report.get('branch') or 'unknown'}`",
        "",
        "## Summary",
        "",
        f"- **Release readiness score**: {summary['release_readiness_score']}",
        f"- **First ten complete**: {summary['first_ten_complete']}",
        f"- **First ten active**: {summary['first_ten_active']}",
        f"- **First ten blocked/unproven**: {summary['first_ten_blocked']}",
        f"- **Open PRs**: {summary['open_prs']}",
        f"- **Open issues**: {summary['open_issues']}",
        f"- **Failed workflow runs**: {summary['failed_workflow_runs']}",
        f"- **Failed quality checks**: {summary['failed_quality_checks']}",
        f"- **Production-ready bots**: {summary['production_ready_bots']}",
        "",
        "## First Ten Updates",
        "",
    ]
    for item in report["first_ten_updates"]:
        lines.append(f"- **{item['title']}**: {item['status']}")
        if item["missing"]:
            lines.append(f"  - Next: {item['next']}")

    lines += ["", "## Top 100 Groups", ""]
    for group in report["top_100_groups"]:
        lines.append(f"- **{group['title']}**: {group['status']} ({group['planned_updates']} planned updates)")
        lines.append(f"  - Next: {group['next']}")

    lines += ["", "## Next Actions", ""]
    for action in report["next_actions"]:
        lines.append(f"- {action}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when blocked/unproven items remain.")
    args = parser.parse_args()

    REPORT_DIR.mkdir(exist_ok=True)
    report = build_report()
    (REPORT_DIR / "dreamco_release_readiness.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_markdown(report, REPORT_DIR / "DREAMCO_RELEASE_READINESS.md")
    print(json.dumps(report["summary"], indent=2))

    if args.strict and report["summary"]["first_ten_blocked"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
