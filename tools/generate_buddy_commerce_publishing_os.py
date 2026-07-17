#!/usr/bin/env python3
"""Generate Buddy commerce, publishing, download, and money-research readiness."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "buddy_commerce_publishing_os.json"
MASTER_REGISTRY_FILE = ROOT / "config" / "master_bot_registry.json"
APP_FOUNDRY_REPORT_FILE = ROOT / "reports" / "app_foundry_readiness.json"
BUSINESS_REPORT_FILE = ROOT / "reports" / "business_launch_expansion_report.json"
APP_CATEGORY_REPORT_FILE = ROOT / "reports" / "app_category_catalog.json"
OUTPUT_JSON = ROOT / "reports" / "buddy_commerce_publishing_os.json"
OUTPUT_MD = ROOT / "reports" / "BUDDY_COMMERCE_PUBLISHING_OS.md"


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def build_report():
    config = read_json(CONFIG_FILE, {})
    registry = read_json(MASTER_REGISTRY_FILE, {})
    foundry = read_json(APP_FOUNDRY_REPORT_FILE, {})
    business = read_json(BUSINESS_REPORT_FILE, {})
    app_catalog = read_json(APP_CATEGORY_REPORT_FILE, {})

    bots = registry.get("bots", [])
    commerce_lanes = config.get("commerce_lanes", [])
    download_targets = config.get("download_targets", [])
    store_targets = config.get("app_store_targets", [])
    approval_wall = config.get("approval_wall", [])
    task_layers = config.get("task_manager_layers", [])
    app_categories = app_catalog.get("app_categories", [])

    lane_cards = []
    for lane in commerce_lanes:
        lane_cards.append(
            {
                "id": lane["id"],
                "label": lane["label"],
                "safe_actions": lane.get("safe_actions", []),
                "approval_required": lane.get("approval_required", []),
                "evidence": lane.get("evidence", []),
                "dashboard_status": "ready_for_buddy_supervised_packet",
                "buddy_prompt": f"Buddy, prepare a supervised {lane['label'].lower()} packet and stop before any live external action.",
                "sandbox_test": {
                    "inputs": ["client_goal", "target_market", "budget_limit", "device_or_platform", "approval_owner"],
                    "expected_outputs": lane.get("evidence", []),
                    "must_not_do": lane.get("approval_required", []),
                },
            }
        )

    download_cards = []
    for target in download_targets:
        download_cards.append(
            {
                **target,
                "buddy_release_packet": {
                    "version": "draft",
                    "required_before_release": ["test_evidence", "privacy_review", "rollback_path", "owner_publish_approval"],
                    "status": target.get("status", "planned"),
                },
            }
        )

    readiness_parts = [
        15 if commerce_lanes else 0,
        15 if download_targets else 0,
        15 if store_targets else 0,
        15 if task_layers else 0,
        15 if app_categories else 0,
        10 if foundry.get("summary", {}).get("readiness_score", 0) else 0,
        10 if business.get("summary", {}).get("service_lanes_ready", 0) else 0,
        5 if approval_wall else 0,
    ]

    summary = {
        "readiness_score": sum(readiness_parts),
        "bot_count": len(bots),
        "commerce_lanes": len(commerce_lanes),
        "download_targets": len(download_targets),
        "app_store_targets": len(store_targets),
        "task_manager_layers": len(task_layers),
        "app_categories": len(app_categories),
        "approval_wall_gates": len(approval_wall),
        "safe_actions": sum(len(lane.get("safe_actions", [])) for lane in commerce_lanes),
        "live_actions_blocked": sum(len(lane.get("approval_required", [])) for lane in commerce_lanes),
        "download_packets_ready": sum(1 for target in download_targets if "ready" in target.get("status", "")),
        "store_packets_ready": len(store_targets),
        "web_research_policy_ready": bool(config.get("web_research_policy")),
        "can_sell_domains_after_approval": any(lane.get("id") == "domains" for lane in commerce_lanes),
        "can_prepare_app_store_submissions": bool(store_targets),
        "can_prepare_device_downloads": bool(download_targets),
        "can_research_autonomous_money": any(lane.get("id") == "web_money_research" for lane in commerce_lanes),
    }

    return {
        "schema": "dreamco.buddy_commerce_publishing_os_report.v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_config": rel(CONFIG_FILE),
        "mission": config.get("mission", ""),
        "positioning": config.get("positioning", ""),
        "default_mode": config.get("default_mode", ""),
        "summary": summary,
        "commerce_lanes": lane_cards,
        "download_targets": download_cards,
        "app_store_targets": store_targets,
        "task_manager_layers": task_layers,
        "web_research_policy": config.get("web_research_policy", {}),
        "approval_wall": approval_wall,
        "sources": {
            "app_foundry": rel(APP_FOUNDRY_REPORT_FILE),
            "business_launch_expansion": rel(BUSINESS_REPORT_FILE),
            "app_category_catalog": rel(APP_CATEGORY_REPORT_FILE),
            "master_registry": rel(MASTER_REGISTRY_FILE),
        },
        "next_actions": [
            "Add PWA manifest and install-ready icons to the Buddy dashboard.",
            "Create store-specific release packets for the first Buddy web app, mobile shell, and desktop shell.",
            "Connect registrar, store, and payment adapters only through secrets plus owner approval.",
            "Keep web money research source-backed and draft-only until the owner approves outreach, payment, or publishing.",
        ],
    }


def write_markdown(report):
    summary = report["summary"]
    lines = [
        "# Buddy Commerce and Publishing OS",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Readiness score: {summary['readiness_score']}",
        f"- Commerce lanes: {summary['commerce_lanes']}",
        f"- Download targets: {summary['download_targets']}",
        f"- App-store targets: {summary['app_store_targets']}",
        f"- Task manager layers: {summary['task_manager_layers']}",
        f"- Approval gates: {summary['approval_wall_gates']}",
        "",
        "## Commerce Lanes",
        "",
    ]
    for lane in report["commerce_lanes"]:
        lines.append(f"### {lane['label']}")
        lines.append("")
        lines.append(f"- Safe actions: {', '.join(lane['safe_actions'])}")
        lines.append(f"- Approval required: {', '.join(lane['approval_required'])}")
        lines.append("")
    lines.extend(["## Download Targets", ""])
    for target in report["download_targets"]:
        lines.append(f"- {target['label']}: {target['goal']} ({target['status']})")
    lines.extend(["", "## Approval Wall", ""])
    for gate in report["approval_wall"]:
        lines.append(f"- {gate}")
    lines.append("")
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("Buddy commerce publishing OS report is stale; run tools/generate_buddy_commerce_publishing_os.py")
        existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if existing_rendered != rendered:
            raise SystemExit("Buddy commerce publishing OS report is stale; run tools/generate_buddy_commerce_publishing_os.py")
        return

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    write_markdown(report)
    print(
        f"commerce_lanes={report['summary']['commerce_lanes']} "
        f"download_targets={report['summary']['download_targets']} "
        f"store_targets={report['summary']['app_store_targets']} "
        f"readiness={report['summary']['readiness_score']}"
    )


if __name__ == "__main__":
    main()
