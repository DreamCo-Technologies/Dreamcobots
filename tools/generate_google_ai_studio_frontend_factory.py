#!/usr/bin/env python3
"""Generate Google AI Studio frontend and workflow factory readiness."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "google_ai_studio_frontend_factory.json"
MASTER_REGISTRY_FILE = ROOT / "config" / "master_bot_registry.json"
MODEL_LIBRARY_FILE = ROOT / "reports" / "buddy_ai_agent_model_library_report.json"
REVENUE_PRACTICE_FILE = ROOT / "reports" / "bot_autonomous_revenue_practice.json"
APP_FOUNDRY_FILE = ROOT / "reports" / "app_foundry_readiness.json"
OUTPUT_JSON = ROOT / "reports" / "google_ai_studio_frontend_factory.json"
OUTPUT_MD = ROOT / "reports" / "GOOGLE_AI_STUDIO_FRONTEND_FACTORY.md"


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def bot_preview_rows(bots: list[dict], limit: int = 12) -> list[dict]:
    rows = []
    for bot in bots[:limit]:
        slug = str(bot.get("slug") or bot.get("id") or bot.get("name", "bot")).lower()
        name = bot.get("name") or bot.get("display_name") or slug.replace("-", " ").title()
        division = bot.get("division") or bot.get("division_id") or "CommandCore"
        rows.append(
            {
                "slug": slug,
                "name": name,
                "division": division,
                "frontend_goal": f"Build a client-ready {name} dashboard with status, demo, approval, and revenue-experiment panels.",
                "workflow_mutation_goal": "Generate two safe workflow variants, sandbox test them, and keep the winner.",
                "money_experiment_goal": "Prepare one source-backed daily money experiment without claiming revenue until payment is confirmed.",
                "approval_status": "owner_approval_required_before_live_actions",
            }
        )
    return rows


def build_report():
    config = read_json(CONFIG_FILE, {})
    registry = read_json(MASTER_REGISTRY_FILE, {})
    model_library = read_json(MODEL_LIBRARY_FILE, {})
    revenue = read_json(REVENUE_PRACTICE_FILE, {})
    foundry = read_json(APP_FOUNDRY_FILE, {})

    bots = registry.get("bots", [])
    frontend_loop = config.get("frontend_perfection_loop", [])
    mutation_loop = config.get("bot_workflow_mutation_loop", [])
    roles = config.get("google_ai_studio_roles", [])
    approval_wall = config.get("approval_wall", [])
    prompts = config.get("dashboard_prompts", [])
    revenue_summary = revenue.get("summary", {})
    foundry_summary = foundry.get("summary", {})

    bot_count = len(bots)
    readiness_parts = [
        15 if config.get("secret_policy", {}).get("required_secret") == "GOOGLE_API_KEY" else 0,
        15 if len(frontend_loop) >= 4 else len(frontend_loop) * 3,
        15 if len(mutation_loop) >= 8 else len(mutation_loop),
        15 if len(roles) >= 4 else len(roles) * 3,
        10 if config.get("daily_money_experiment_policy") else 0,
        10 if config.get("model_routing", {}).get("free_or_low_cost_first") else 0,
        10 if revenue_summary.get("bots_with_revenue_practice", 0) >= bot_count and bot_count else 0,
        10 if foundry_summary.get("creation_lanes", 0) >= 8 else 0,
    ]

    summary = {
        "readiness_score": sum(readiness_parts),
        "bot_count": bot_count,
        "frontend_perfection_steps": len(frontend_loop),
        "workflow_mutation_steps": len(mutation_loop),
        "google_ai_studio_roles": len(roles),
        "dashboard_prompts": len(prompts),
        "approval_wall_gates": len(approval_wall),
        "bots_with_frontend_factory_plan": bot_count,
        "bots_with_workflow_mutation_plan": bot_count,
        "bots_with_daily_money_experiment_plan": bot_count,
        "actual_revenue_requires_payment_confirmation": True,
        "google_api_key_secret_required": True,
        "paid_calls_require_owner_approval": True,
        "free_or_low_cost_first": bool(config.get("model_routing", {}).get("free_or_low_cost_first")),
        "revenue_practice_bots": revenue_summary.get("bots_with_revenue_practice", 0),
        "app_foundry_lanes": foundry_summary.get("creation_lanes", 0),
        "model_resources": model_library.get("summary", {}).get("model_resources", 0),
    }

    return {
        "schema": "dreamco.google_ai_studio_frontend_factory_report.v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_config": rel(CONFIG_FILE),
        "mission": config.get("mission", ""),
        "default_mode": config.get("default_mode", ""),
        "secret_policy": config.get("secret_policy", {}),
        "summary": summary,
        "frontend_perfection_loop": frontend_loop,
        "bot_workflow_mutation_loop": mutation_loop,
        "daily_money_experiment_policy": config.get("daily_money_experiment_policy", {}),
        "google_ai_studio_roles": roles,
        "model_routing": config.get("model_routing", {}),
        "dashboard_prompts": prompts,
        "approval_wall": approval_wall,
        "bot_preview": bot_preview_rows(bots),
        "sources": {
            "master_registry": rel(MASTER_REGISTRY_FILE),
            "model_library": rel(MODEL_LIBRARY_FILE),
            "revenue_practice": rel(REVENUE_PRACTICE_FILE),
            "app_foundry": rel(APP_FOUNDRY_FILE),
        },
        "next_actions": [
            "Add GOOGLE_API_KEY only to approved secret stores, never to repository files.",
            "Use the factory to generate frontend task packets before any direct code mutation.",
            "Run visual, build, accessibility, and sandbox revenue checks after each generated frontend change.",
            "Record actual revenue only after Stripe, bank, or platform payment confirmation.",
        ],
    }


def write_markdown(report):
    summary = report["summary"]
    lines = [
        "# Google AI Studio Frontend Factory",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Readiness score: {summary['readiness_score']}",
        f"- Bots with frontend plans: {summary['bots_with_frontend_factory_plan']}",
        f"- Workflow mutation steps: {summary['workflow_mutation_steps']}",
        f"- Daily money experiment plans: {summary['bots_with_daily_money_experiment_plan']}",
        f"- Approval gates: {summary['approval_wall_gates']}",
        "",
        "## Frontend Perfection Loop",
        "",
    ]
    for step in report["frontend_perfection_loop"]:
        lines.append(f"- {step['label']}: {step['purpose']}")
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
            raise SystemExit("Google AI Studio frontend factory report is stale; run tools/generate_google_ai_studio_frontend_factory.py")
        existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if existing_rendered != rendered:
            raise SystemExit("Google AI Studio frontend factory report is stale; run tools/generate_google_ai_studio_frontend_factory.py")
        return

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    write_markdown(report)
    print(
        f"google_ai_studio_frontend_factory_ready={report['summary']['readiness_score']} "
        f"bots={report['summary']['bot_count']} "
        f"workflow_steps={report['summary']['workflow_mutation_steps']}"
    )


if __name__ == "__main__":
    main()
