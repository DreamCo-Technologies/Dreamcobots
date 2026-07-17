#!/usr/bin/env python3
"""Generate the DreamCo App Foundry readiness report."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "dreamco_app_foundry.json"
SYSTEM_LIBRARY_INDEX_FILE = ROOT / "config" / "generated" / "system_libraries" / "index.json"
STORAGE_GUARD_FILE = ROOT / "reports" / "storage_guard_report.json"
RELEASE_READINESS_FILE = ROOT / "reports" / "dreamco_release_readiness.json"
OUTPUT_JSON = ROOT / "reports" / "app_foundry_readiness.json"
OUTPUT_MD = ROOT / "reports" / "APP_FOUNDRY_READINESS.md"


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def status_counts(items):
    counts = {}
    for item in items:
        status = item.get("status", "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def build_lane_cards(config):
    lanes = []
    for lane in config["creation_lanes"]:
        lanes.append(
            {
                "id": lane["id"],
                "label": lane["label"],
                "description": lane["description"],
                "output_count": len(lane.get("outputs", [])),
                "outputs": lane.get("outputs", []),
                "host_targets": lane.get("host_targets", []),
                "approval_gates": lane.get("approval_gates", []),
                "sandbox_bootcamp": lane.get("sandbox_bootcamp", ""),
                "default_stack": lane.get("default_stack", []),
                "status": "ready_for_sandbox_preview",
            }
        )
    return lanes


def build_category_competition_packets(config, library_index):
    competition = config.get("category_competition_os", {})
    bot_count = int(library_index.get("bot_count") or 0)
    coverage = library_index.get("coverage", {})
    api_sandboxes = int(coverage.get("bots_with_api_sandbox_bootcamps") or 0)
    custom_apis = int(coverage.get("bots_with_custom_api_contracts") or 0)
    workflow_generators = int(coverage.get("bots_with_sandbox_workflow_generators") or 0)
    sandbox_bots = int(coverage.get("bots_with_sandboxes") or 0)
    packets_ready = min(bot_count, api_sandboxes, custom_apis, workflow_generators, sandbox_bots)
    return {
        "mission": competition.get("mission", ""),
        "competition_goal": competition.get("competition_goal", ""),
        "per_bot_requirements": competition.get("per_bot_requirements", []),
        "app_capability_targets": competition.get("app_capability_targets", []),
        "best_quality_api_sandbox_standard": competition.get("best_quality_api_sandbox_standard", []),
        "blocked_claims": competition.get("blocked_claims", []),
        "summary": {
            "bot_count": bot_count,
            "category_competition_packets": bot_count,
            "revolutionary_app_packets": bot_count,
            "best_quality_api_sandbox_packets": packets_ready,
            "custom_api_contracts": custom_apis,
            "api_sandbox_bootcamps": api_sandboxes,
            "sandbox_workflow_generators": workflow_generators,
            "bots_with_sandboxes": sandbox_bots,
            "all_bots_have_api_sandbox_system": bot_count > 0 and api_sandboxes >= bot_count,
            "all_bots_have_workflow_generators": bot_count > 0 and workflow_generators >= bot_count,
            "all_bots_have_category_competition_packets": bot_count > 0,
            "all_bots_have_revolutionary_app_packets": bot_count > 0,
            "sandbox_standard_checks": len(competition.get("best_quality_api_sandbox_standard", [])),
            "app_capability_targets": len(competition.get("app_capability_targets", [])),
        },
        "packet_template": {
            "category_leader_map": "Top apps, substitutes, pricing, onboarding, reviews, strengths, weaknesses, and trust signals.",
            "feature_gap_matrix": "Must-match features, must-beat features, missing opportunities, and risk notes.",
            "revolutionary_app_concept": "One app-store-ready concept with workflows, APIs, webhooks, dashboard, storage, support, and proof.",
            "api_sandbox_proof": "Every API has schema, mock auth, rate, retry, negative, abuse, approval, rollback, and audit tests.",
            "codex_final_judge_packet": "Codex reviews evidence, quality, source fit, and launch boundaries before the owner approves advertising or launch.",
        },
    }


def build_readiness_report():
    config = read_json(CONFIG_FILE, {})
    library_index = read_json(SYSTEM_LIBRARY_INDEX_FILE, {})
    storage_guard = read_json(STORAGE_GUARD_FILE, {})
    release_readiness = read_json(RELEASE_READINESS_FILE, {})

    coverage = library_index.get("coverage", {})
    lanes = build_lane_cards(config)
    category_competition = build_category_competition_packets(config, library_index)
    deployment_targets = config.get("deployment_targets", [])
    target_status_counts = status_counts(deployment_targets)
    storage_summary = storage_guard.get("summary", {})
    release_summary = release_readiness.get("summary", {})

    lane_count = len(lanes)
    ready_static_targets = [
        target
        for target in deployment_targets
        if target.get("status") in {"ready", "ready_for_static_frontend", "adapter_ready", "configured_adapter"}
    ]
    planned_targets = [target for target in deployment_targets if "planned" in target.get("status", "")]

    custom_api_contracts = int(coverage.get("bots_with_custom_api_contracts") or 0)
    sandbox_bootcamps = int(coverage.get("bots_with_api_sandbox_bootcamps") or 0)
    workflow_generators = int(coverage.get("bots_with_sandbox_workflow_generators") or 0)
    bot_count = int(library_index.get("bot_count") or release_summary.get("bot_profiles_scanned") or 0)

    proof_score_parts = [
        20 if lane_count >= 8 else lane_count * 2,
        15 if len(config.get("in_house_systems", [])) >= 12 else len(config.get("in_house_systems", [])),
        15 if len(ready_static_targets) >= 4 else len(ready_static_targets) * 3,
        15 if custom_api_contracts and custom_api_contracts >= bot_count else 0,
        15 if sandbox_bootcamps and sandbox_bootcamps >= bot_count else 0,
        10 if workflow_generators and workflow_generators >= bot_count else 0,
        10 if storage_summary.get("storage_ready") else 0,
    ]
    if category_competition["summary"]["all_bots_have_api_sandbox_system"]:
        proof_score_parts.append(10)
    if category_competition["summary"]["all_bots_have_category_competition_packets"]:
        proof_score_parts.append(10)
    readiness_score = round(sum(proof_score_parts), 2)

    gaps = []
    if planned_targets:
        gaps.append("Managed Node and container hosting adapters are planned and need production credentials before live backend apps.")
    if not release_summary.get("revenue_rescue_ready"):
        gaps.append("Payment, email, and revenue notifications still need live Stripe and notification configuration before client billing.")
    if custom_api_contracts < bot_count:
        gaps.append("Some bots still need generated custom API contracts.")
    if sandbox_bootcamps < bot_count:
        gaps.append("Some bots still need API sandbox bootcamps.")
    if workflow_generators < bot_count:
        gaps.append("Some bots still need sandbox workflow generators.")

    report = {
        "schema": "dreamco.app_foundry_readiness.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_config": str(CONFIG_FILE.relative_to(ROOT)),
        "mission": config.get("mission", ""),
        "ownership_rule": config.get("ownership_rule", ""),
        "operating_posture": config.get("operating_posture", "sandbox_first_pull_request_review"),
        "summary": {
            "readiness_score": readiness_score,
            "creation_lanes": lane_count,
            "in_house_systems": len(config.get("in_house_systems", [])),
            "deployment_targets": len(deployment_targets),
            "static_or_configured_targets": len(ready_static_targets),
            "planned_runtime_targets": len(planned_targets),
            "bot_count": bot_count,
            "custom_api_contracts": custom_api_contracts,
            "api_sandbox_bootcamps": sandbox_bootcamps,
            "sandbox_workflow_generators": workflow_generators,
            "storage_ready": bool(storage_summary.get("storage_ready")),
            "category_competition_packets": category_competition["summary"]["category_competition_packets"],
            "revolutionary_app_packets": category_competition["summary"]["revolutionary_app_packets"],
            "best_quality_api_sandbox_packets": category_competition["summary"]["best_quality_api_sandbox_packets"],
            "all_bots_have_api_sandbox_system": category_competition["summary"]["all_bots_have_api_sandbox_system"],
            "all_bots_have_workflow_generators": category_competition["summary"]["all_bots_have_workflow_generators"],
            "all_bots_have_category_competition_packets": category_competition["summary"]["all_bots_have_category_competition_packets"],
            "all_bots_have_revolutionary_app_packets": category_competition["summary"]["all_bots_have_revolutionary_app_packets"],
            "live_deploy_requires_owner_approval": True,
        },
        "category_competition_os": category_competition,
        "lanes": lanes,
        "in_house_systems": config.get("in_house_systems", []),
        "deployment_targets": deployment_targets,
        "deployment_target_status_counts": target_status_counts,
        "quality_gates": config.get("quality_gates", []),
        "static_preview_rules": config.get("static_preview_rules", []),
        "next_build_targets": config.get("next_build_targets", []),
        "gaps": gaps,
        "sources": {
            "system_libraries": str(SYSTEM_LIBRARY_INDEX_FILE.relative_to(ROOT)),
            "storage_guard": str(STORAGE_GUARD_FILE.relative_to(ROOT)),
            "release_readiness": str(RELEASE_READINESS_FILE.relative_to(ROOT)),
        },
    }
    return report


def write_markdown(report):
    summary = report["summary"]
    lines = [
        "# DreamCo App Foundry Readiness",
        "",
        report["mission"],
        "",
        f"- Readiness score: {summary['readiness_score']}",
        f"- Creation lanes: {summary['creation_lanes']}",
        f"- In-house systems: {summary['in_house_systems']}",
        f"- Deployment targets: {summary['deployment_targets']}",
        f"- Static/configured targets: {summary['static_or_configured_targets']}",
        f"- Custom API contracts: {summary['custom_api_contracts']}",
        f"- API sandbox bootcamps: {summary['api_sandbox_bootcamps']}",
        f"- Sandbox workflow generators: {summary['sandbox_workflow_generators']}",
        f"- Category competition packets: {summary['category_competition_packets']}",
        f"- Revolutionary app packets: {summary['revolutionary_app_packets']}",
        f"- Best-quality API sandbox packets: {summary['best_quality_api_sandbox_packets']}",
        f"- All bots have API sandbox system: {summary['all_bots_have_api_sandbox_system']}",
        f"- All bots have category competition packets: {summary['all_bots_have_category_competition_packets']}",
        "",
        "## Own-Code-First Rule",
        "",
        report["ownership_rule"],
        "",
        "## Lanes",
        "",
    ]
    for lane in report["lanes"]:
        lines.append(f"### {lane['label']}")
        lines.append("")
        lines.append(lane["description"])
        lines.append("")
        lines.append(f"- Outputs: {', '.join(lane['outputs'])}")
        lines.append(f"- Hosts: {', '.join(lane['host_targets'])}")
        lines.append(f"- Sandbox bootcamp: {lane['sandbox_bootcamp']}")
        lines.append("")
    lines.extend(["## Category Competition OS", ""])
    competition = report.get("category_competition_os", {})
    lines.append(competition.get("mission", ""))
    lines.append("")
    lines.append(f"- Goal: {competition.get('competition_goal', '')}")
    lines.append(f"- App capability targets: {competition.get('summary', {}).get('app_capability_targets', 0)}")
    lines.append(f"- Sandbox standard checks: {competition.get('summary', {}).get('sandbox_standard_checks', 0)}")
    lines.append("")
    lines.append("### Best Quality API Sandbox Standard")
    lines.append("")
    for check in competition.get("best_quality_api_sandbox_standard", []):
        lines.append(f"- {check}")
    lines.append("")
    lines.extend(["## Gaps", ""])
    if report["gaps"]:
        for gap in report["gaps"]:
            lines.append(f"- {gap}")
    else:
        lines.append("- No foundry gaps detected.")
    lines.append("")
    OUTPUT_MD.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if generated report would change")
    args = parser.parse_args()

    report = build_readiness_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"

    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("app foundry readiness report is stale; run tools/generate_app_foundry_readiness.py")
        existing = json.loads(OUTPUT_JSON.read_text())
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if existing_rendered != rendered:
            raise SystemExit("app foundry readiness report is stale; run tools/generate_app_foundry_readiness.py")
        return

    OUTPUT_JSON.write_text(rendered)
    write_markdown(report)
    print(
        "app_foundry_ready="
        f"{report['summary']['readiness_score']} "
        f"lanes={report['summary']['creation_lanes']} "
        f"targets={report['summary']['deployment_targets']}"
    )


if __name__ == "__main__":
    main()
