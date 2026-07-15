#!/usr/bin/env python3
"""Generate Buddy's prompt, tool, agent, and AI model-resource routing library."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "buddy_ai_agent_model_library.json"
MASTER_REGISTRY_FILE = ROOT / "config" / "master_bot_registry.json"
OUTPUT_JSON = ROOT / "reports" / "buddy_ai_agent_model_library_report.json"
OUTPUT_MD = ROOT / "reports" / "BUDDY_AI_AGENT_MODEL_LIBRARY_REPORT.md"


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def words(value):
    return str(value or "").replace("_", " ").replace("-", " ").strip()


def slug(value):
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in str(value or "item"))
    return "-".join(part for part in cleaned.split("-") if part) or "item"


def build_model_resources(config):
    resources = []
    tiers = config.get("resource_tiers", [])
    for family in config.get("model_families", []):
        for tier in tiers:
            resource_id = f"{family['id']}__{tier['id']}"
            resources.append(
                {
                    "id": resource_id,
                    "provider": family["provider"],
                    "family_id": family["id"],
                    "label": f"{family['label']} - {tier['label']}",
                    "tier": tier["id"],
                    "roles": family.get("roles", []),
                    "best_tasks": family.get("best_tasks", []),
                    "good_at": family.get("good_at", []),
                    "bad_at": family.get("bad_at", []),
                    "use_when": tier["use_when"],
                    "tradeoff": tier["tradeoff"],
                    "status": "candidate_verify_model_id_before_production",
                    "approval_gates": ["provider_credentials", "pricing_review", "data_privacy_review"],
                }
            )
    return resources


def choose_route(task, resources):
    scoring = []
    for resource in resources:
        score = 0
        if task in resource.get("best_tasks", []):
            score += 10
        if "coding" in task and "coding" in resource.get("roles", []):
            score += 4
        if "image" in task and "image" in resource.get("roles", []):
            score += 4
        if "video" in task and "video" in resource.get("roles", []):
            score += 4
        if "voice" in task and ("voice" in resource.get("roles", []) or "tts" in resource.get("roles", [])):
            score += 4
        if "research" in task and ("web_search" in resource.get("roles", []) or "research" in resource.get("roles", [])):
            score += 4
        if resource["tier"] == "quality":
            score += 2
        if resource["tier"] == "fast":
            score += 1
        if score:
            scoring.append((score, resource))
    scoring.sort(key=lambda item: (-item[0], item[1]["provider"], item[1]["id"]))
    picks = [item[1] for item in scoring[:4]]
    if not picks:
        picks = [resource for resource in resources if resource["tier"] == "quality"][:4]
    return {
        "task_type": task,
        "primary_resource": picks[0]["id"],
        "fallback_resources": [resource["id"] for resource in picks[1:]],
        "selection_reason": "Ranked by declared best_tasks, roles, quality tier, and safe fallback coverage.",
        "required_evals": ["task_success", "cost_latency", "source_quality", "safety_gate", "user_value"],
    }


def build_prompt_tool_agent_matrix(config):
    prompt_types = config.get("prompt_types", [])
    tool_types = config.get("tool_types", [])
    agent_types = config.get("agent_types", [])
    matrix = []
    for agent in agent_types:
        agent_id = agent["id"]
        if "coding" in agent_id or "debugging" in agent_id or "tool" in agent_id:
            prompts = ["task_brief", "tool_contract", "code_review", "test_generation", "sandbox_runbook"]
            tools = ["file_reader", "code_editor", "test_runner", "api_client", "approval_gate"]
        elif "creative" in agent_id or "voice" in agent_id:
            prompts = ["task_brief", "visual_prompt", "voice_consent", "rubric_eval", "handoff_summary"]
            tools = ["image_generator", "image_editor", "video_generator", "text_to_speech", "approval_gate"]
        elif "research" in agent_id or "business" in agent_id or "sales" in agent_id:
            prompts = ["retrieval_grounded", "customer_discovery", "offer_builder", "critique", "handoff_summary"]
            tools = ["browser_research", "vector_search", "reranker", "spreadsheet_builder", "notification_sender"]
        else:
            prompts = prompt_types[:5]
            tools = tool_types[:5]
        matrix.append(
            {
                "agent_type": agent_id,
                "label": agent["label"],
                "prompt_types": [item for item in prompts if item in prompt_types],
                "tool_types": [item for item in tools if item in tool_types],
                "best_for": agent.get("best_for", []),
                "avoid_for": agent.get("avoid_for", []),
            }
        )
    return matrix


def bot_routes(bots, routes):
    route_by_task = {route["task_type"]: route for route in routes}
    samples = []
    for bot in bots[:12]:
        category = words(bot.get("category") or bot.get("division") or "business").lower()
        if "code" in category or "app" in category:
            task = "coding"
        elif "art" in category or "design" in category:
            task = "image_generation"
        elif "sales" in category or "market" in category:
            task = "sales_copy"
        elif "data" in category or "finance" in category:
            task = "data_extraction"
        else:
            task = "workflow_automation"
        route = route_by_task.get(task) or routes[0]
        samples.append(
            {
                "slug": bot.get("slug") or bot.get("id"),
                "name": bot.get("name"),
                "division": bot.get("division"),
                "task_type": task,
                "primary_resource": route["primary_resource"],
                "fallback_resources": route["fallback_resources"],
            }
        )
    return samples


def build_report():
    config = read_json(CONFIG_FILE, {})
    registry = read_json(MASTER_REGISTRY_FILE, {})
    bots = registry.get("bots", [])
    resources = build_model_resources(config)
    routes = [choose_route(task, resources) for task in config.get("task_types", [])]
    matrix = build_prompt_tool_agent_matrix(config)
    providers = sorted({resource["provider"] for resource in resources})

    summary = {
        "model_resources": len(resources),
        "providers": len(providers),
        "agent_types": len(config.get("agent_types", [])),
        "prompt_types": len(config.get("prompt_types", [])),
        "tool_types": len(config.get("tool_types", [])),
        "task_routes": len(routes),
        "bot_count": len(bots),
        "bots_with_model_routing": len(bots),
        "resources_requiring_model_id_verification": len(resources),
        "approval_gated_resources": len(resources),
    }

    return {
        "schema": "dreamco.buddy_ai_agent_model_library_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_config": str(CONFIG_FILE.relative_to(ROOT)),
        "mission": config.get("mission", ""),
        "policy": config.get("policy", {}),
        "summary": summary,
        "providers": providers,
        "provider_docs": config.get("provider_docs", []),
        "model_resources": resources,
        "task_routes": routes,
        "agent_prompt_tool_matrix": matrix,
        "bot_route_sample": bot_routes(bots, routes),
        "best_practice_routing_order": [
            "Classify task type and risk.",
            "Select a quality resource for hard or client-facing work.",
            "Use fast or budget resources for sandbox iteration.",
            "Use private resources for sensitive inputs only after privacy review.",
            "Run evals before trusting output.",
            "Escalate to owner approval before external, paid, credential, customer, or production impact.",
        ],
    }


def write_markdown(report):
    summary = report["summary"]
    lines = [
        "# Buddy AI Agent Model Library Report",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Model resources: {summary['model_resources']}",
        f"- Providers: {summary['providers']}",
        f"- Agent types: {summary['agent_types']}",
        f"- Prompt types: {summary['prompt_types']}",
        f"- Tool types: {summary['tool_types']}",
        f"- Task routes: {summary['task_routes']}",
        f"- Bots with model routing: {summary['bots_with_model_routing']} / {summary['bot_count']}",
        "",
        "## Routing Rule",
        "",
        report["policy"].get("model_id_rule", ""),
        "",
        "## Top Task Routes",
        "",
    ]
    for route in report["task_routes"][:12]:
        lines.append(f"- {words(route['task_type']).title()}: {route['primary_resource']}")
    lines.extend(["", "## Agent Types", ""])
    for item in report["agent_prompt_tool_matrix"]:
        lines.append(f"- {item['label']}: prompts={', '.join(item['prompt_types'])}; tools={', '.join(item['tool_types'])}")
    OUTPUT_MD.write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("Buddy AI agent model library report is stale; run tools/generate_buddy_ai_agent_model_library.py")
        existing = json.loads(OUTPUT_JSON.read_text())
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if existing_rendered != rendered:
            raise SystemExit("Buddy AI agent model library report is stale; run tools/generate_buddy_ai_agent_model_library.py")
        return

    OUTPUT_JSON.write_text(rendered)
    write_markdown(report)
    print(
        f"model_resources={report['summary']['model_resources']} "
        f"agent_types={report['summary']['agent_types']} "
        f"task_routes={report['summary']['task_routes']}"
    )


if __name__ == "__main__":
    main()
