#!/usr/bin/env python3
"""Generate Buddy productivity tracking across owner, client, and bot outcomes."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - reports should capture read issues.
        return {"_error": str(exc)}


def current_branch() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "branch", "--show-current"],
            cwd=ROOT,
            text=True,
        ).strip()
    except Exception:
        return None


def percent(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def top_capabilities(inventory: dict[str, Any], limit: int = 20) -> list[tuple[str, int]]:
    counter: Counter[str] = Counter()
    for bot in inventory.get("bots", []):
        for capability in bot.get("capabilities", []):
            if isinstance(capability, str):
                label = capability
            else:
                label = capability.get("label") or capability.get("intent")
            if label:
                counter[str(label)] += 1
    return counter.most_common(limit)


def build_tracker() -> dict[str, Any]:
    inventory = read_json(REPORT_DIR / "buddy_capability_inventory.json", {})
    steward = read_json(REPORT_DIR / "repository_stewardship_report.json", {})
    platform = read_json(REPORT_DIR / "dreamco_platform_audit.json", {})
    cost = read_json(REPORT_DIR / "github_cost_saver_report.json", {})
    triage = read_json(REPORT_DIR / "github_triage_report.json", {})

    inv_summary = inventory.get("summary", {})
    steward_summary = steward.get("summary", {})
    platform_readiness = platform.get("readiness", {})
    cost_findings = cost.get("findings", [])
    estimated_savings = round(
        sum(float(finding.get("estimated_monthly_savings_usd", 0) or 0) for finding in cost_findings),
        2,
    )
    bot_count = int(inv_summary.get("bot_profiles_scanned", 0) or 0)
    production_ready = int(inv_summary.get("production_ready_bots", 0) or 0)
    runtime_ready = int(inv_summary.get("executable_runtime_ready_bots", 0) or 0)
    approval_gated = int(inv_summary.get("buddy_money_approval_required_bots", 0) or 0)
    failed_workflows = int(steward_summary.get("failed_workflow_runs", 0) or 0)
    open_prs = int(steward_summary.get("open_prs", 0) or 0)
    open_issues = int(steward_summary.get("open_issues", 0) or 0)

    productivity_score = max(
        0.0,
        min(
            100.0,
            percent(runtime_ready, bot_count) * 0.25
            + percent(production_ready, bot_count) * 0.25
            + (100 if inv_summary.get("all_system_libraries_cover_profiled_bots") else 0) * 0.15
            + (100 if steward_summary.get("failed_quality_checks", 1) == 0 else 0) * 0.15
            + max(0, 100 - min(open_prs + open_issues + failed_workflows, 100)) * 0.20,
        ),
    )

    learning_loops = [
        {
            "name": "Capability inventory loop",
            "tracks": ["bot readiness", "tests", "production gates", "approval risk"],
            "helps": "Buddy knows which bots are demo-ready, test-ready, and blocked.",
        },
        {
            "name": "Repository cleanroom loop",
            "tracks": ["pull requests", "issues", "workflow failures", "syntax gates"],
            "helps": "Buddy keeps work queues organized before merge or client demo.",
        },
        {
            "name": "Cost saver loop",
            "tracks": ["Actions minutes", "artifacts", "caches", "paid feature risk"],
            "helps": "Buddy points to lower-cost ways to keep the system running.",
        },
        {
            "name": "Platform audit loop",
            "tracks": ["AI company readiness", "system libraries", "trust controls"],
            "helps": "Buddy can package bots as client-facing companies, departments, or employees.",
        },
    ]

    return {
        "schema": "dreamco.buddy_productivity_tracker.v1",
        "generated_at": iso_now(),
        "branch": current_branch(),
        "mission": "Track everything useful for helping the owner, clients, and bots become more productive.",
        "summary": {
            "productivity_score": round(productivity_score, 2),
            "bot_count": bot_count,
            "runtime_ready_bots": runtime_ready,
            "production_ready_bots": production_ready,
            "approval_gated_bots": approval_gated,
            "open_prs": open_prs,
            "open_issues": open_issues,
            "failed_workflow_runs": failed_workflows,
            "failed_quality_checks": int(steward_summary.get("failed_quality_checks", 0) or 0),
            "estimated_monthly_savings_usd": estimated_savings,
            "tracked_learning_loops": len(learning_loops),
        },
        "owner_productivity": {
            "tracks": [
                "next best build task",
                "repo cleanup burden",
                "money-saving opportunities",
                "approval-gated live actions",
                "demo readiness",
            ],
            "current_focus": [
                f"Push branch with {open_prs} open PRs and {open_issues} open issues still reported upstream.",
                f"Retest or resolve {failed_workflows} failed workflow run(s).",
                f"Review cost-saver findings worth about ${estimated_savings}/month before increasing paid automation.",
            ],
        },
        "client_productivity": {
            "tracks": [
                "demo-ready bots",
                "client-facing prospectus pages",
                "safe sandbox test packets",
                "department/company packaging",
                "trust and approval evidence",
            ],
            "ready_to_show": [
                "Buddy Trust Layer",
                "Actions dashboard",
                "Bot test catalog",
                "Repository cleanroom",
                "System library coverage",
            ],
        },
        "bot_productivity": {
            "tracks": [
                "runtime readiness",
                "test readiness",
                "tool/API/webhook/workflow/skill/sandbox coverage",
                "high-risk approval status",
                "learning-loop evidence",
            ],
            "coverage": {
                "runtime_ready_percent": percent(runtime_ready, bot_count),
                "production_ready_percent": percent(production_ready, bot_count),
                "approval_gated_percent": percent(approval_gated, bot_count),
                "platform_ready_bots": platform_readiness.get("fully_coded_bots", runtime_ready),
            },
        },
        "learning_loops": learning_loops,
        "top_capabilities": top_capabilities(inventory),
        "next_actions": [
            "Keep the productivity tracker visible in the Actions dashboard.",
            "Use the cleanroom queue to close duplicate or already-covered work after owner approval.",
            "Turn top capabilities into client packages with prospectus pages and sandbox demos.",
            "Prioritize workflow failures because they block the cleanroom from becoming ready.",
            "Apply cost-saver recommendations before adding more scheduled automation.",
        ],
        "sources": {
            "buddy_inventory": "reports/buddy_capability_inventory.json",
            "repository_stewardship": "reports/repository_stewardship_report.json",
            "platform_audit": "reports/dreamco_platform_audit.json",
            "cost_saver": "reports/github_cost_saver_report.json",
            "github_triage": "reports/github_triage_report.json",
        },
        "triage_snapshot": triage.get("summary", {}),
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# Buddy Productivity Tracker",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Summary",
        "",
        f"- **Productivity score**: {summary['productivity_score']}",
        f"- **Bots tracked**: {summary['bot_count']}",
        f"- **Runtime-ready bots**: {summary['runtime_ready_bots']}",
        f"- **Production-ready bots**: {summary['production_ready_bots']}",
        f"- **Approval-gated bots**: {summary['approval_gated_bots']}",
        f"- **Open PRs**: {summary['open_prs']}",
        f"- **Open issues**: {summary['open_issues']}",
        f"- **Failed workflow runs**: {summary['failed_workflow_runs']}",
        f"- **Failed quality checks**: {summary['failed_quality_checks']}",
        f"- **Estimated monthly savings**: ${summary['estimated_monthly_savings_usd']}",
        "",
        "## Learning Loops",
        "",
    ]
    for loop in report["learning_loops"]:
        lines.append(f"- **{loop['name']}**: {loop['helps']}")

    lines += ["", "## Next Actions", ""]
    for action in report["next_actions"]:
        lines.append(f"- {action}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    report = build_tracker()
    (REPORT_DIR / "buddy_productivity_tracker.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_markdown(report, REPORT_DIR / "BUDDY_PRODUCTIVITY_TRACKER.md")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
