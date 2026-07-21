#!/usr/bin/env python3
"""Generate specialized knowledge profiles for every DreamCo bot."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "specialized_bot_knowledge.json"
MASTER_REGISTRY_FILE = ROOT / "config" / "master_bot_registry.json"
SYSTEM_LIBRARY_INDEX_FILE = ROOT / "config" / "generated" / "system_libraries" / "index.json"
BOT_FOUNDER_REPORT_FILE = ROOT / "reports" / "bot_founder_app_store_report.json"
STORAGE_GUARD_FILE = ROOT / "reports" / "storage_guard_report.json"
OUTPUT_JSON = ROOT / "reports" / "specialized_bot_knowledge_report.json"
OUTPUT_MD = ROOT / "reports" / "SPECIALIZED_BOT_KNOWLEDGE_REPORT.md"
PROFILE_SHARD_DIR = ROOT / "reports" / "specialized_bot_knowledge_profiles"


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def words(value):
    return str(value or "").replace("_", " ").replace("-", " ").strip()


def slugify(value):
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in str(value or "dreamco"))
    return "-".join(part for part in cleaned.split("-") if part) or "dreamco"


def capability_labels(bot):
    labels = []
    for capability in bot.get("capabilities") or []:
        if isinstance(capability, dict):
            labels.append(capability.get("label") or capability.get("intent") or "capability")
        else:
            labels.append(str(capability))
    return labels


def founder_by_slug(founder_report):
    packets = founder_report.get("packets") or founder_report.get("dashboard_sample") or []
    return {packet.get("slug"): packet for packet in packets if packet.get("slug")}


def build_profile(bot, config, founder_packet=None):
    slug = bot.get("slug") or bot.get("id")
    name = bot.get("name") or words(slug)
    division = bot.get("division") or "DreamCo"
    category = bot.get("category") or "business"
    caps = capability_labels(bot)
    target_customer = founder_packet.get("target_customer") if founder_packet else f"{words(category)} teams in {division}"
    app_concept = founder_packet.get("autonomous_app_concept", {}) if founder_packet else {}

    domains = []
    for domain in config.get("knowledge_domains", []):
        domains.append(
            {
                "id": domain["id"],
                "label": domain["label"],
                "status": "profile_ready",
                "required_artifacts": domain.get("required_artifacts", []),
                "study_prompt": f"{name} should maintain {domain['label'].lower()} for {target_customer}.",
                "source_policy": "public_or_owner_approved_only",
            }
        )

    return {
        "slug": slug,
        "name": name,
        "emoji": bot.get("emoji", "🤖"),
        "division": division,
        "category": category,
        "target_customer": target_customer,
        "app_concept_name": app_concept.get("name", f"{name} App"),
        "knowledge_domains": domains,
        "capability_seed": caps[:8],
        "specialized_study_queue": [
            f"Build a {words(category)} glossary for {division}.",
            "Map customer pains, buying triggers, and proof needs.",
            "Compare public competitors and substitute workflows.",
            "Turn the bot into a sandbox-tested app-store concept.",
            "Draft marketing, demo, and customer discovery notes for owner review.",
            "Record only useful source-backed lessons with retention metadata.",
        ],
        "memory_policy": {
            "mode": config.get("default_mode"),
            "tiers": [tier["id"] for tier in config.get("memory_tiers", [])],
            "required_metadata": config.get("source_policy", {}).get("required_metadata", []),
            "drop": config.get("source_policy", {}).get("blocked", []),
        },
        "approval_gates": config.get("approval_gates", []),
        "dashboard_status": "ready_for_specialized_learning",
    }


def build_report():
    config = read_json(CONFIG_FILE, {})
    registry = read_json(MASTER_REGISTRY_FILE, {})
    library_index = read_json(SYSTEM_LIBRARY_INDEX_FILE, {})
    founder_report = read_json(BOT_FOUNDER_REPORT_FILE, {})
    storage_guard = read_json(STORAGE_GUARD_FILE, {})
    founders = founder_by_slug(founder_report)
    bots = registry.get("bots", [])
    profiles = [build_profile(bot, config, founders.get(bot.get("slug"))) for bot in bots]
    domain_count = len(config.get("knowledge_domains", []))
    division_counts = Counter(profile["division"] for profile in profiles)
    profile_shards = [
        {
            "division": division,
            "bot_count": count,
            "path": str((PROFILE_SHARD_DIR / f"{slugify(division)}.json").relative_to(ROOT)),
        }
        for division, count in sorted(division_counts.items())
    ]

    summary = {
        "bot_count": len(bots),
        "knowledge_profiles": len(profiles),
        "knowledge_domains": domain_count,
        "bots_with_all_knowledge_domains": sum(
            1 for profile in profiles if len(profile["knowledge_domains"]) == domain_count
        ),
        "bots_with_source_policy": len(profiles),
        "bots_with_memory_policy": len(profiles),
        "bots_with_runtime_tooling_knowledge": sum(
            1 for profile in profiles if any(domain["id"] == "runtime_and_tooling" for domain in profile["knowledge_domains"])
        ),
        "bots_with_safety_approval_knowledge": sum(
            1 for profile in profiles if any(domain["id"] == "safety_and_approval" for domain in profile["knowledge_domains"])
        ),
        "bots_with_app_builder_knowledge": sum(
            1 for profile in profiles if any(domain["id"] == "app_builder_knowledge" for domain in profile["knowledge_domains"])
        ),
        "resource_library_bot_count": library_index.get("bot_count", 0),
        "bot_founder_packets": founder_report.get("summary", {}).get("founder_packets", 0),
        "storage_ready": bool(storage_guard.get("summary", {}).get("storage_ready")),
        "approval_gates": len(config.get("approval_gates", [])),
        "memory_tiers": len(config.get("memory_tiers", [])),
        "profile_shards": len(profile_shards),
    }

    return {
        "schema": "dreamco.specialized_bot_knowledge_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_config": str(CONFIG_FILE.relative_to(ROOT)),
        "source_registry": str(MASTER_REGISTRY_FILE.relative_to(ROOT)),
        "mission": config.get("mission", ""),
        "default_mode": config.get("default_mode", ""),
        "summary": summary,
        "knowledge_domains": config.get("knowledge_domains", []),
        "source_policy": config.get("source_policy", {}),
        "memory_tiers": config.get("memory_tiers", []),
        "approval_gates": config.get("approval_gates", []),
        "top_divisions": [
            {"division": division, "bot_count": count}
            for division, count in division_counts.most_common(15)
        ],
        "dashboard_sample": profiles[:12],
        "profile_storage": {
            "mode": "division_shards",
            "directory": str(PROFILE_SHARD_DIR.relative_to(ROOT)),
            "shards": profile_shards,
        },
        "next_actions": [
            "Connect specialized knowledge profiles to bot prompt libraries.",
            "Use source-backed lesson summaries instead of raw copied content.",
            "Add per-bot knowledge tests before app-store publishing.",
        ],
    }, profiles


def write_profile_shards(report, profiles):
    PROFILE_SHARD_DIR.mkdir(parents=True, exist_ok=True)
    active_names = set()
    profiles_by_division = {}
    for profile in profiles:
        profiles_by_division.setdefault(profile["division"], []).append(profile)

    for division, division_profiles in sorted(profiles_by_division.items()):
        shard_name = f"{slugify(division)}.json"
        active_names.add(shard_name)
        payload = {
            "schema": "dreamco.specialized_bot_knowledge_profiles.v1",
            "generated_at": report["generated_at"],
            "division": division,
            "bot_count": len(division_profiles),
            "profiles": division_profiles,
        }
        (PROFILE_SHARD_DIR / shard_name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    for old_file in PROFILE_SHARD_DIR.glob("*.json"):
        if old_file.name not in active_names:
            old_file.unlink()


def write_markdown(report):
    summary = report["summary"]
    lines = [
        "# Specialized Bot Knowledge Report",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Knowledge profiles: {summary['knowledge_profiles']} / {summary['bot_count']}",
        f"- Knowledge domains per bot: {summary['knowledge_domains']}",
        f"- Bots with all domains: {summary['bots_with_all_knowledge_domains']}",
        f"- Source policy coverage: {summary['bots_with_source_policy']}",
        f"- Memory policy coverage: {summary['bots_with_memory_policy']}",
        f"- Runtime/tooling knowledge: {summary['bots_with_runtime_tooling_knowledge']}",
        f"- Safety/approval knowledge: {summary['bots_with_safety_approval_knowledge']}",
        f"- App builder knowledge: {summary['bots_with_app_builder_knowledge']}",
        f"- Profile shards: {summary['profile_shards']} in `{report['profile_storage']['directory']}`",
        "",
        "## Knowledge Domains",
        "",
    ]
    for domain in report["knowledge_domains"]:
        lines.append(f"### {domain['label']}")
        lines.append("")
        lines.append(domain["purpose"])
        lines.append("")
        lines.append(f"- Artifacts: {', '.join(domain.get('required_artifacts', []))}")
        lines.append("")
    lines.extend(["## Source Policy", "", f"- Allowed: {', '.join(report['source_policy'].get('allowed', []))}", f"- Blocked: {', '.join(report['source_policy'].get('blocked', []))}", ""])
    OUTPUT_MD.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report, profiles = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("specialized bot knowledge report is stale; run tools/generate_specialized_bot_knowledge.py")
        existing = json.loads(OUTPUT_JSON.read_text())
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if existing_rendered != rendered:
            raise SystemExit("specialized bot knowledge report is stale; run tools/generate_specialized_bot_knowledge.py")
        for shard in report["profile_storage"]["shards"]:
            shard_path = ROOT / shard["path"]
            if not shard_path.exists():
                raise SystemExit(f"specialized bot knowledge shard is missing: {shard['path']}")
        return

    OUTPUT_JSON.write_text(rendered)
    write_profile_shards(report, profiles)
    write_markdown(report)
    print(
        f"knowledge_profiles={report['summary']['knowledge_profiles']} "
        f"domains={report['summary']['knowledge_domains']} "
        f"storage_ready={report['summary']['storage_ready']}"
    )


if __name__ == "__main__":
    main()
