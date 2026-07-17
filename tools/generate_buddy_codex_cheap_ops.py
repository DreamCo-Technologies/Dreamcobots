#!/usr/bin/env python3
"""Generate Buddy's Codex-style cheap 24-hour operations contract."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCALING_REPORT = ROOT / "reports" / "dreamco_24_hour_scaling_report.json"
GITHUB_COST_REPORT = ROOT / "reports" / "github_cost_saver_report.json"
MODEL_LIBRARY_REPORT = ROOT / "reports" / "buddy_ai_agent_model_library_report.json"
BUDDY_CONNECTION_REPORT = ROOT / "reports" / "buddy_bot_connection_report.json"
OUTPUT_JSON = ROOT / "reports" / "buddy_codex_cheap_ops.json"
OUTPUT_MD = ROOT / "reports" / "BUDDY_CODEX_CHEAP_OPS.md"


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_report() -> dict[str, Any]:
    scaling = read_json(SCALING_REPORT, {})
    github_cost = read_json(GITHUB_COST_REPORT, {})
    model_library = read_json(MODEL_LIBRARY_REPORT, {})
    connections = read_json(BUDDY_CONNECTION_REPORT, {})

    scaling_summary = scaling.get("summary", {})
    model_summary = model_library.get("summary", {})
    github_summary = github_cost.get("summary", {})
    connection_summary = connections.get("summary", {})
    cost_control = scaling.get("cost_control_policy", {})
    parity_goal = scaling.get("buddy_codex_parity_goal", {})

    codex_style_capabilities = [
        {
            "id": "repo_reader",
            "label": "Repository reader",
            "buddy_can": "Scan files, reports, bot profiles, configs, tests, workflows, and dashboards.",
            "cheap_path": "Use local file reads and generated JSON reports before network calls.",
            "approval": "No approval for read-only local scans.",
        },
        {
            "id": "code_editor",
            "label": "Code editor",
            "buddy_can": "Draft scoped code, config, test, and documentation changes for review.",
            "cheap_path": "Use deterministic templates and smallest-capable AI routes before premium models.",
            "approval": "Owner approval before push, merge, deploy, or destructive edits.",
        },
        {
            "id": "test_runner",
            "label": "Test and debug runner",
            "buddy_can": "Run syntax checks, unit tests, smoke tests, report freshness checks, and failure triage.",
            "cheap_path": "Run locally first; use GitHub Actions only for release evidence or remote-only checks.",
            "approval": "Owner approval before increasing scheduled CI frequency or paid runner usage.",
        },
        {
            "id": "pr_helper",
            "label": "Pull request helper",
            "buddy_can": "Prepare PR summaries, compare goals to repository proof, and queue fixes for failed checks.",
            "cheap_path": "Use cached GitHub triage reports and local diffs before API refreshes.",
            "approval": "Owner approval before closing, merging, rebasing, or force-pushing PR branches.",
        },
        {
            "id": "model_router",
            "label": "AI model router",
            "buddy_can": "Pick local/static/free/cheap/premium model routes based on task risk and quality needs.",
            "cheap_path": "Prefer local reports, cache, Gemini low-cost routes, and small models for drafts.",
            "approval": "Owner approval before paid always-on loops, premium batches, or production customer data.",
        },
        {
            "id": "bot_orchestrator",
            "label": "Bot orchestrator",
            "buddy_can": "Create supervised work packets for every bot so the fleet keeps learning, testing, and packaging.",
            "cheap_path": "Queue work packets and summaries instead of running every bot as a paid live service.",
            "approval": "Owner approval before customer outreach, money movement, deploys, or account changes.",
        },
    ]

    always_on_strategy = {
        "mode": "24_hour_supervised_queue_not_24_hour_paid_compute",
        "plain_english": (
            "Buddy keeps the system moving by rotating cheap local/report-based cycles and queued work packets. "
            "Bots do not need expensive always-on cloud containers to stay useful."
        ),
        "runtime_layers": [
            "static dashboard and generated reports",
            "local scripts on owner laptop",
            "manual or path-gated GitHub Actions",
            "Cloud Run request-based service that sleeps when idle",
            "free or low-cost AI model routes",
            "owner-approved paid production actions",
        ],
        "success_condition": "Every bot has a current packet, status, test path, resource path, and approval boundary.",
    }

    github_free_cheap_plan = {
        "default_hosting": "GitHub Pages for static dashboards and docs when possible.",
        "actions_policy": "Manual, path-gated, short retention, local-first.",
        "runner_policy": "Local laptop first; GitHub-hosted only when needed for proof; paid larger/macOS runners avoided unless approved.",
        "artifact_policy": "1-7 day retention for diagnostics; longer only for release evidence.",
        "estimated_monthly_savings_usd": github_summary.get("estimated_monthly_savings_usd", 0),
        "findings": github_summary.get("finding_count", len(github_cost.get("findings", []))),
    }

    cheap_ai_resource_plan = {
        "default_mode": "free_or_low_cost_first",
        "local_first": True,
        "cache_first": True,
        "low_cost_resources": model_summary.get("low_cost_resources", 0),
        "google_gemini_resources": model_summary.get("google_gemini_resources", 0),
        "premium_requires_reason": True,
        "secret_name": (model_library.get("cost_control") or {}).get("secret_name", "GOOGLE_API_KEY"),
    }

    summary = {
        "codex_style_capabilities": len(codex_style_capabilities),
        "bots_connected_to_buddy": connection_summary.get("buddy_connected_bots", 0),
        "bot_count": connection_summary.get("bot_count", 0),
        "cheap_24_hour_mode": True,
        "min_replicas": scaling_summary.get("min_replicas"),
        "max_replicas": scaling_summary.get("max_replicas"),
        "github_cost_guardrails": len(cost_control.get("github_cost_guardrails", [])),
        "ai_cost_guardrails": len(cost_control.get("ai_cost_guardrails", [])),
        "low_cost_ai_resources": cheap_ai_resource_plan["low_cost_resources"],
        "gemini_resources": cheap_ai_resource_plan["google_gemini_resources"],
        "owner_approval_boundaries": len(parity_goal.get("requires_owner_approval", [])),
        "unlimited_autonomy_claimed": False,
        "billing_bypass_claimed": False,
    }

    return {
        "schema": "dreamco.buddy_codex_cheap_ops.v1",
        "generated_at": utc_now(),
        "mission": "Make Buddy a governed Codex-style coding, debugging, orchestration, and operations teammate while keeping DreamCo free or cheap by default.",
        "summary": summary,
        "always_on_strategy": always_on_strategy,
        "codex_style_capabilities": codex_style_capabilities,
        "github_free_cheap_plan": github_free_cheap_plan,
        "cheap_ai_resource_plan": cheap_ai_resource_plan,
        "cost_control_policy": cost_control,
        "buddy_codex_parity_goal": parity_goal,
        "approval_boundaries": scaling.get("always_blocked_without_owner_approval", []),
        "next_actions": [
            "Keep Cloud Run min instances at 0 and max instances at 1 until revenue supports scale.",
            "Move expensive scheduled workflows to manual or path-gated triggers.",
            "Use Buddy operation packets for 24-hour progress instead of paid always-on bot containers.",
            "Add budget alerts before enabling recurring paid AI, GitHub, or cloud workloads.",
        ],
        "sources": {
            "24_hour_scaling": "reports/dreamco_24_hour_scaling_report.json",
            "github_cost_saver": "reports/github_cost_saver_report.json",
            "ai_agent_model_library": "reports/buddy_ai_agent_model_library_report.json",
            "buddy_connections": "reports/buddy_bot_connection_report.json",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# Buddy Codex Cheap Ops",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Codex-style capabilities: {summary['codex_style_capabilities']}",
        f"- Bot count: {summary['bot_count']}",
        f"- Buddy-connected bots: {summary['bots_connected_to_buddy']}",
        f"- Cheap 24-hour mode: {summary['cheap_24_hour_mode']}",
        f"- Cloud scale target: {summary['min_replicas']} to {summary['max_replicas']}",
        f"- Low-cost AI resources: {summary['low_cost_ai_resources']}",
        f"- Gemini resources: {summary['gemini_resources']}",
        f"- Unlimited autonomy claimed: {summary['unlimited_autonomy_claimed']}",
        "",
        "## Always-On Strategy",
        "",
        report["always_on_strategy"]["plain_english"],
        "",
        "## Codex-Style Capabilities",
        "",
    ]
    for capability in report["codex_style_capabilities"]:
        lines.append(f"- {capability['label']}: {capability['buddy_can']} Cheap path: {capability['cheap_path']}")
    lines.extend(["", "## Approval Boundaries", ""])
    for boundary in report["approval_boundaries"]:
        lines.append(f"- {boundary}")
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("Buddy Codex cheap ops report is missing; run the generator.")
        existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if existing_rendered != rendered:
            raise SystemExit("Buddy Codex cheap ops report is stale; run the generator.")
        return 0

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    write_markdown(report)
    print(
        "codex_cheap_ops=true capabilities={capabilities} bots={bots} low_cost_ai={ai}".format(
            capabilities=report["summary"]["codex_style_capabilities"],
            bots=report["summary"]["bot_count"],
            ai=report["summary"]["low_cost_ai_resources"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
