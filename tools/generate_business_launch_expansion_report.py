#!/usr/bin/env python3
"""Generate DreamCo business launch and expansion readiness report."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "business_launch_expansion_system.json"
MASTER_REGISTRY_FILE = ROOT / "config" / "master_bot_registry.json"
OUTPUT_JSON = ROOT / "reports" / "business_launch_expansion_report.json"
OUTPUT_MD = ROOT / "reports" / "BUSINESS_LAUNCH_EXPANSION_REPORT.md"


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def build_report():
    config = read_json(CONFIG_FILE, {})
    registry = read_json(MASTER_REGISTRY_FILE, {})
    bots = registry.get("bots", [])
    service_lanes = config.get("service_lanes", [])
    sub_agent_roles = config.get("sub_agent_roles", [])
    client_workflows = config.get("client_workflows", [])
    approval_gates = config.get("permission_model", {}).get("client_must_approve", [])
    blocked = config.get("permission_model", {}).get("blocked_without_professional_review", [])

    lane_packets = []
    for lane in service_lanes:
        lane_packets.append(
            {
                "id": lane["id"],
                "label": lane["label"],
                "purpose": lane["purpose"],
                "deliverables": lane.get("deliverables", []),
                "approval_gates": lane.get("approval_gates", []),
                "dashboard_status": "ready_for_supervised_client_planning",
                "client_prompt": f"Buddy, help me with {lane['label'].lower()} and prepare everything for approval before any live action.",
                "test_packet": {
                    "sandbox_inputs": ["client_goal", "budget_range", "location_or_market", "timeline", "risk_tolerance"],
                    "expected_outputs": lane.get("deliverables", []),
                    "must_not_do": ["spend_money", "submit_forms", "contact_external_parties", "make_legal_tax_claims"],
                },
            }
        )

    summary = {
        "bot_count": len(bots),
        "service_lanes_ready": len(service_lanes),
        "sub_agent_roles_ready": len(sub_agent_roles),
        "client_workflows_ready": len(client_workflows),
        "approval_gates_declared": len(approval_gates),
        "professional_review_blocks": len(blocked),
        "deliverables_declared": sum(len(lane.get("deliverables", [])) for lane in service_lanes),
        "lane_test_packets": len(lane_packets),
        "all_lanes_permissioned": all(lane.get("approval_gates") for lane in service_lanes),
    }

    return {
        "schema": "dreamco.business_launch_expansion_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_config": str(CONFIG_FILE.relative_to(ROOT)),
        "mission": config.get("mission", ""),
        "positioning": config.get("positioning", ""),
        "permission_model": config.get("permission_model", {}),
        "summary": summary,
        "service_lanes": lane_packets,
        "sub_agent_roles": sub_agent_roles,
        "client_workflows": client_workflows,
        "next_actions": [
            "Connect each service lane to a Buddy prompt packet and approval checklist.",
            "Add provider adapters only after credentials, pricing, and client approval are configured.",
            "Keep all filings, purchases, submissions, outreach, hiring, and paid ads blocked until explicit approval.",
        ],
    }


def write_markdown(report):
    summary = report["summary"]
    lines = [
        "# Business Launch and Expansion Report",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Service lanes ready: {summary['service_lanes_ready']}",
        f"- Sub-agent roles ready: {summary['sub_agent_roles_ready']}",
        f"- Client workflows ready: {summary['client_workflows_ready']}",
        f"- Approval gates declared: {summary['approval_gates_declared']}",
        f"- Deliverables declared: {summary['deliverables_declared']}",
        f"- Lane test packets: {summary['lane_test_packets']}",
        "",
        "## Service Lanes",
        "",
    ]
    for lane in report["service_lanes"]:
        lines.append(f"### {lane['label']}")
        lines.append("")
        lines.append(lane["purpose"])
        lines.append("")
        lines.append(f"- Deliverables: {', '.join(lane['deliverables'])}")
        lines.append(f"- Approval gates: {', '.join(lane['approval_gates'])}")
        lines.append("")
    lines.extend(["## Permission Rule", "", report["permission_model"].get("default_mode", ""), ""])
    OUTPUT_MD.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("business launch expansion report is stale; run tools/generate_business_launch_expansion_report.py")
        existing = json.loads(OUTPUT_JSON.read_text())
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if existing_rendered != rendered:
            raise SystemExit("business launch expansion report is stale; run tools/generate_business_launch_expansion_report.py")
        return

    OUTPUT_JSON.write_text(rendered)
    write_markdown(report)
    print(
        f"service_lanes={report['summary']['service_lanes_ready']} "
        f"sub_agents={report['summary']['sub_agent_roles_ready']} "
        f"approval_gates={report['summary']['approval_gates_declared']}"
    )


if __name__ == "__main__":
    main()
