#!/usr/bin/env python3
"""Generate Buddy people-search and job-qualification lookup coverage."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "people_job_qualification_system.json"
MASTER_REGISTRY_FILE = ROOT / "config" / "master_bot_registry.json"
OUTPUT_JSON = ROOT / "reports" / "people_job_qualification_report.json"
OUTPUT_MD = ROOT / "reports" / "PEOPLE_JOB_QUALIFICATION_REPORT.md"


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def words(value):
    return str(value or "").replace("_", " ").replace("-", " ").strip()


def choose_lanes(bot, lanes):
    division = str(bot.get("division") or "").lower()
    category = str(bot.get("category") or "").lower()
    available = {lane["id"] for lane in lanes}
    selected = ["candidate_resume_match", "employee_role_fit", "sales_people_research"]
    if "construction" in division or "transport" in division or "health" in division or "legal" in division:
        selected.extend(["license_certification_checklist", "contractor_vendor_match"])
    elif "sales" in division or "market" in division or "cust" in division:
        selected.extend(["sales_people_research", "contractor_vendor_match"])
    elif "admin" in division or "biz" in division or "global" in division:
        selected.extend(["relocation_workforce_match", "contractor_vendor_match"])
    elif "lead" in category or "recruit" in category:
        selected.extend(["sales_people_research", "candidate_resume_match"])
    else:
        selected.extend(["contractor_vendor_match", "relocation_workforce_match"])
    deduped = []
    for lane in selected:
        if lane in available and lane not in deduped:
            deduped.append(lane)
    return deduped[:5]


def build_bot_blueprint(bot, config):
    lanes = choose_lanes(bot, config.get("qualification_lanes", []))
    slug = bot.get("slug") or bot.get("id")
    name = bot.get("name") or words(slug).title()
    division = bot.get("division") or "DreamCo"
    return {
        "slug": slug,
        "name": name,
        "division": division,
        "category": bot.get("category") or "business",
        "qualification_lanes": lanes,
        "buddy_roles": config.get("buddy_bot_roles", []),
        "privacy_metadata": config.get("privacy_policy", {}).get("required_metadata", []),
        "approval_gates": config.get("approval_gates", []),
        "blocked_uses": config.get("blocked_uses", []),
        "sample_lookup_prompt": (
            f"Prepare a privacy-safe people or job-qualification lookup packet for {name}. "
            "Use only public or owner-approved sources, cite evidence, flag gaps, and require human review."
        ),
        "dashboard_status": "ready_for_permissioned_people_lookup",
    }


def build_report():
    config = read_json(CONFIG_FILE, {})
    registry = read_json(MASTER_REGISTRY_FILE, {})
    bots = registry.get("bots", [])
    blueprints = [build_bot_blueprint(bot, config) for bot in bots]
    lane_counts = Counter(lane for blueprint in blueprints for lane in blueprint["qualification_lanes"])
    division_counts = Counter(blueprint["division"] for blueprint in blueprints)

    summary = {
        "bot_count": len(bots),
        "bot_people_lookup_blueprints": len(blueprints),
        "qualification_lanes_ready": len(config.get("qualification_lanes", [])),
        "approval_gates_declared": len(config.get("approval_gates", [])),
        "blocked_uses_declared": len(config.get("blocked_uses", [])),
        "allowed_source_types": len(config.get("privacy_policy", {}).get("allowed_sources", [])),
        "blocked_source_types": len(config.get("privacy_policy", {}).get("blocked_sources", [])),
        "privacy_metadata_fields": len(config.get("privacy_policy", {}).get("required_metadata", [])),
        "qualification_scoring_factors": len(config.get("qualification_scoring", [])),
        "buddy_bot_roles": len(config.get("buddy_bot_roles", [])),
        "human_review_required": True,
    }

    return {
        "schema": "dreamco.people_job_qualification_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_config": str(CONFIG_FILE.relative_to(ROOT)),
        "mission": config.get("mission", ""),
        "default_mode": config.get("default_mode", ""),
        "privacy_policy": config.get("privacy_policy", {}),
        "summary": summary,
        "qualification_lanes": config.get("qualification_lanes", []),
        "approval_gates": config.get("approval_gates", []),
        "blocked_uses": config.get("blocked_uses", []),
        "qualification_scoring": config.get("qualification_scoring", []),
        "top_qualification_lanes": [
            {"qualification_lane": lane, "bot_count": count}
            for lane, count in lane_counts.most_common(8)
        ],
        "top_divisions": [
            {"division": division, "bot_count": count}
            for division, count in division_counts.most_common(12)
        ],
        "dashboard_sample": blueprints[:12],
        "next_actions": [
            "Connect only approved public-source and self-provided profile inputs.",
            "Create human-review packets for hiring, recruiting, client, contractor, and vendor decisions.",
            "Keep background checks, contact, hiring/rejection, data export, and automated recruiting blocked until approval.",
        ],
    }


def write_markdown(report):
    summary = report["summary"]
    lines = [
        "# People Search and Job Qualification Report",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Bot people lookup blueprints: {summary['bot_people_lookup_blueprints']} / {summary['bot_count']}",
        f"- Qualification lanes ready: {summary['qualification_lanes_ready']}",
        f"- Approval gates declared: {summary['approval_gates_declared']}",
        f"- Blocked uses declared: {summary['blocked_uses_declared']}",
        f"- Privacy metadata fields: {summary['privacy_metadata_fields']}",
        f"- Human review required: {summary['human_review_required']}",
        "",
        "## Qualification Lanes",
        "",
    ]
    for lane in report["qualification_lanes"]:
        lines.append(f"### {lane['label']}")
        lines.append("")
        lines.append(lane["purpose"])
        lines.append("")
        lines.append(f"- Outputs: {', '.join(lane.get('outputs', []))}")
        lines.append("")
    lines.extend(["## Blocked Uses", ""])
    for blocked in report["blocked_uses"]:
        lines.append(f"- {blocked}")
    OUTPUT_MD.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("people job qualification report is stale; run tools/generate_people_job_qualification_report.py")
        existing = json.loads(OUTPUT_JSON.read_text())
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if existing_rendered != rendered:
            raise SystemExit("people job qualification report is stale; run tools/generate_people_job_qualification_report.py")
        return

    OUTPUT_JSON.write_text(rendered)
    write_markdown(report)
    print(
        f"people_lookup_blueprints={report['summary']['bot_people_lookup_blueprints']} "
        f"qualification_lanes={report['summary']['qualification_lanes_ready']} "
        f"human_review_required={report['summary']['human_review_required']}"
    )


if __name__ == "__main__":
    main()
