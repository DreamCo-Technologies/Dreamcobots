#!/usr/bin/env python3
"""Generate DreamCo 24-hour scaling readiness report."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "dreamco_24_hour_scaling.json"
BOT_FOUNDER_REPORT_FILE = ROOT / "reports" / "bot_founder_app_store_report.json"
APP_FOUNDRY_REPORT_FILE = ROOT / "reports" / "app_foundry_readiness.json"
STORAGE_GUARD_FILE = ROOT / "reports" / "storage_guard_report.json"
OUTPUT_JSON = ROOT / "reports" / "dreamco_24_hour_scaling_report.json"
OUTPUT_MD = ROOT / "reports" / "DREAMCO_24_HOUR_SCALING_REPORT.md"


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def build_report():
    config = read_json(CONFIG_FILE, {})
    founder = read_json(BOT_FOUNDER_REPORT_FILE, {})
    foundry = read_json(APP_FOUNDRY_REPORT_FILE, {})
    storage = read_json(STORAGE_GUARD_FILE, {})

    cycles = config.get("daily_cycles", [])
    safe_steps = sum(len(cycle.get("safe_automation", [])) for cycle in cycles)
    approval_steps = sum(len(cycle.get("approval_required", [])) for cycle in cycles)
    infra = config.get("infrastructure_policy", {})
    founder_summary = founder.get("summary", {})
    foundry_summary = foundry.get("summary", {})
    storage_summary = storage.get("summary", {})

    readiness_score = 0
    readiness_score += 20 if len(cycles) >= 6 else len(cycles) * 3
    readiness_score += 15 if safe_steps >= 20 else safe_steps // 2
    readiness_score += 15 if approval_steps >= 20 else approval_steps // 2
    readiness_score += 15 if founder_summary.get("founder_packets", 0) >= 1248 else 0
    readiness_score += 15 if foundry_summary.get("creation_lanes", 0) >= 8 else 0
    readiness_score += 10 if storage_summary.get("storage_ready") else 0
    readiness_score += 10 if infra.get("self_healing") else 0

    return {
        "schema": "dreamco.24_hour_scaling_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_config": str(CONFIG_FILE.relative_to(ROOT)),
        "mission": config.get("mission", ""),
        "default_mode": config.get("default_mode", ""),
        "summary": {
            "readiness_score": min(readiness_score, 100),
            "cycles_defined": len(cycles),
            "safe_automation_steps": safe_steps,
            "cycle_approval_steps": approval_steps,
            "always_blocked_gates": len(config.get("always_blocked_without_owner_approval", [])),
            "scale_lanes": len(config.get("scale_lanes", [])),
            "bot_founder_packets": founder_summary.get("founder_packets", 0),
            "app_store_categories": founder_summary.get("app_store_categories", 0),
            "app_foundry_lanes": foundry_summary.get("creation_lanes", 0),
            "storage_ready": bool(storage_summary.get("storage_ready")),
            "min_replicas": infra.get("min_replicas"),
            "max_replicas": infra.get("max_replicas"),
            "self_healing_enabled": bool(infra.get("self_healing")),
        },
        "infrastructure_policy": infra,
        "daily_cycles": cycles,
        "scale_lanes": config.get("scale_lanes", []),
        "always_blocked_without_owner_approval": config.get("always_blocked_without_owner_approval", []),
        "next_actions": [
            "Connect this report to a scheduled GitHub workflow when the owner approves recurring automation.",
            "Keep cycles in report/draft mode until production credentials, budgets, and approval gates are configured.",
            "Use the review cycle to choose one app-store listing and one bot build to ship next.",
        ],
        "sources": {
            "bot_founder_app_store": str(BOT_FOUNDER_REPORT_FILE.relative_to(ROOT)),
            "app_foundry": str(APP_FOUNDRY_REPORT_FILE.relative_to(ROOT)),
            "storage_guard": str(STORAGE_GUARD_FILE.relative_to(ROOT)),
        },
    }


def write_markdown(report):
    summary = report["summary"]
    lines = [
        "# DreamCo 24-Hour Scaling Report",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Readiness score: {summary['readiness_score']}",
        f"- Daily cycles: {summary['cycles_defined']}",
        f"- Safe automation steps: {summary['safe_automation_steps']}",
        f"- Approval-gated steps: {summary['cycle_approval_steps']}",
        f"- Always-blocked gates: {summary['always_blocked_gates']}",
        f"- Bot founder packets: {summary['bot_founder_packets']}",
        f"- App foundry lanes: {summary['app_foundry_lanes']}",
        f"- Infra replicas: {summary['min_replicas']} to {summary['max_replicas']}",
        "",
        "## Daily Cycles",
        "",
    ]
    for cycle in report["daily_cycles"]:
        lines.append(f"### {cycle['window']} - {cycle['id']}")
        lines.append("")
        lines.append(cycle["purpose"])
        lines.append("")
        lines.append(f"- Safe automation: {', '.join(cycle.get('safe_automation', []))}")
        lines.append(f"- Approval required: {', '.join(cycle.get('approval_required', []))}")
        lines.append("")
    lines.extend(["## Always Blocked Without Approval", ""])
    for gate in report["always_blocked_without_owner_approval"]:
        lines.append(f"- {gate}")
    lines.append("")
    OUTPUT_MD.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("24-hour scaling report is stale; run tools/generate_24_hour_scaling_report.py")
        existing = json.loads(OUTPUT_JSON.read_text())
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if existing_rendered != rendered:
            raise SystemExit("24-hour scaling report is stale; run tools/generate_24_hour_scaling_report.py")
        return

    OUTPUT_JSON.write_text(rendered)
    write_markdown(report)
    print(
        f"scaling_ready={report['summary']['readiness_score']} "
        f"cycles={report['summary']['cycles_defined']} "
        f"blocked_gates={report['summary']['always_blocked_gates']}"
    )


if __name__ == "__main__":
    main()
