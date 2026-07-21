#!/usr/bin/env python3
"""Generate DreamCo AI data package library coverage."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "ai_data_package_library.json"
MASTER_REGISTRY_FILE = ROOT / "config" / "master_bot_registry.json"
OUTPUT_JSON = ROOT / "reports" / "ai_data_package_library_report.json"
OUTPUT_MD = ROOT / "reports" / "AI_DATA_PACKAGE_LIBRARY_REPORT.md"


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def words(value):
    return str(value or "").replace("_", " ").replace("-", " ").strip()


def choose_package_types(bot, package_types):
    division = str(bot.get("division") or "").lower()
    category = str(bot.get("category") or "").lower()
    by_id = {item["id"]: item for item in package_types}
    ids = ["instruction_tuning", "eval_benchmark", "agent_simulation"]
    if "code" in division or "agent" in division or "ai" in division:
        ids.extend(["tool_calling", "code_agent_tasks", "rag_knowledge_base"])
    elif "sales" in division or "market" in division or "biz" in division:
        ids.extend(["synthetic_business_cases", "contract_opportunity_data", "conversation_safety"])
    elif "transport" in division or "construction" in division or "real" in division:
        ids.extend(["contract_opportunity_data", "vision_labeling", "synthetic_business_cases"])
    elif "arts" in division or "content" in division or "social" in division:
        ids.extend(["vision_labeling", "audio_voice_safe", "conversation_safety"])
    elif "data" in division or "finance" in division:
        ids.extend(["rag_knowledge_base", "domain_glossary", "synthetic_business_cases"])
    elif "health" in division or "legal" in division or "education" in division:
        ids.extend(["domain_glossary", "conversation_safety", "eval_benchmark"])
    elif "dataset" in category or "data" in category:
        ids.extend(["rag_knowledge_base", "domain_glossary", "tool_calling"])
    else:
        ids.extend(["domain_glossary", "rag_knowledge_base", "synthetic_business_cases"])

    selected = []
    for item_id in ids:
        if item_id in by_id and item_id not in selected:
            selected.append(item_id)
    return selected[:6]


def build_bot_blueprint(bot, config):
    package_types = choose_package_types(bot, config.get("package_types", []))
    slug = bot.get("slug") or bot.get("id")
    name = bot.get("name") or words(slug).title()
    division = bot.get("division") or "DreamCo"
    return {
        "slug": slug,
        "name": name,
        "division": division,
        "category": bot.get("category") or "business",
        "package_types": package_types,
        "langchain_use": ["document_loader", "text_splitter", "metadata_normalizer", "retrieval_eval_set"],
        "quality_gates": config.get("quality_gates", []),
        "rights_required": config.get("rights_policy", {}).get("required_metadata", []),
        "approval_gates": config.get("approval_gates", []),
        "sample_package_name": f"{name} Training and Eval Data Pack",
        "sample_buyer_use": f"Train, evaluate, or retrieve knowledge for {words(division)} workflows.",
        "dashboard_status": "ready_for_rights_cleared_data_packaging",
    }


def build_report():
    config = read_json(CONFIG_FILE, {})
    registry = read_json(MASTER_REGISTRY_FILE, {})
    bots = registry.get("bots", [])
    blueprints = [build_bot_blueprint(bot, config) for bot in bots]
    package_counts = Counter(package_type for blueprint in blueprints for package_type in blueprint["package_types"])
    division_counts = Counter(blueprint["division"] for blueprint in blueprints)

    summary = {
        "bot_count": len(bots),
        "bot_package_blueprints": len(blueprints),
        "package_types_ready": len(config.get("package_types", [])),
        "quality_gates_ready": len(config.get("quality_gates", [])),
        "commercial_models_ready": len(config.get("commercial_models", [])),
        "approval_gates": len(config.get("approval_gates", [])),
        "required_rights_metadata": len(config.get("rights_policy", {}).get("required_metadata", [])),
        "allowed_source_types": len(config.get("rights_policy", {}).get("allowed_sources", [])),
        "blocked_source_types": len(config.get("rights_policy", {}).get("blocked_sources", [])),
        "langchain_ready": bool(config.get("langchain", {}).get("required")),
        "langchain_packages": len(config.get("langchain", {}).get("javascript_packages", [])),
        "sellable_package_samples": len(blueprints[:12]),
    }

    return {
        "schema": "dreamco.ai_data_package_library_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_config": str(CONFIG_FILE.relative_to(ROOT)),
        "mission": config.get("mission", ""),
        "positioning": config.get("positioning", ""),
        "langchain": config.get("langchain", {}),
        "rights_policy": config.get("rights_policy", {}),
        "summary": summary,
        "package_types": config.get("package_types", []),
        "quality_gates": config.get("quality_gates", []),
        "commercial_models": config.get("commercial_models", []),
        "approval_gates": config.get("approval_gates", []),
        "top_package_types": [
            {"package_type": package_type, "bot_count": count}
            for package_type, count in package_counts.most_common(12)
        ],
        "top_divisions": [
            {"division": division, "bot_count": count}
            for division, count in division_counts.most_common(12)
        ],
        "dashboard_sample": blueprints[:12],
        "next_actions": [
            "Add sample JSONL manifests for only rights-cleared synthetic or owned data.",
            "Wire LangChain loaders, splitters, and eval dataset builders after dependency installation.",
            "Create buyer data cards with license, provenance, quality scores, and blocked uses.",
        ],
    }


def write_markdown(report):
    summary = report["summary"]
    lines = [
        "# AI Data Package Library Report",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Bot package blueprints: {summary['bot_package_blueprints']} / {summary['bot_count']}",
        f"- Package types ready: {summary['package_types_ready']}",
        f"- Quality gates ready: {summary['quality_gates_ready']}",
        f"- Commercial models ready: {summary['commercial_models_ready']}",
        f"- Rights metadata fields: {summary['required_rights_metadata']}",
        f"- LangChain ready: {summary['langchain_ready']}",
        "",
        "## Package Types",
        "",
    ]
    for package_type in report["package_types"]:
        lines.append(f"### {package_type['label']}")
        lines.append("")
        lines.append(package_type["buyer_use"])
        lines.append("")
        lines.append(f"- Formats: {', '.join(package_type.get('formats', []))}")
        lines.append(f"- Must include: {', '.join(package_type.get('must_include', []))}")
        lines.append("")
    lines.extend(["## Rights Rule", "", "Only rights-cleared, source-backed, consent-safe packages may be sold or licensed.", ""])
    OUTPUT_MD.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("AI data package library report is stale; run tools/generate_ai_data_package_library.py")
        existing = json.loads(OUTPUT_JSON.read_text())
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if existing_rendered != rendered:
            raise SystemExit("AI data package library report is stale; run tools/generate_ai_data_package_library.py")
        return

    OUTPUT_JSON.write_text(rendered)
    write_markdown(report)
    print(
        f"bot_package_blueprints={report['summary']['bot_package_blueprints']} "
        f"package_types={report['summary']['package_types_ready']} "
        f"langchain_ready={report['summary']['langchain_ready']}"
    )


if __name__ == "__main__":
    main()
