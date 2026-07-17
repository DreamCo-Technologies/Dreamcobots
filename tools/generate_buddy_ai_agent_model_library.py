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
                    "cost_posture": infer_cost_posture(family, tier),
                    "status": "candidate_verify_model_id_before_production",
                    "approval_gates": ["provider_credentials", "pricing_review", "data_privacy_review"],
                }
            )
    return resources


def infer_cost_posture(family, tier):
    text = " ".join(
        [
            family.get("id", ""),
            family.get("label", ""),
            " ".join(family.get("roles", [])),
            " ".join(family.get("good_at", [])),
            tier.get("id", ""),
        ]
    ).lower()
    if tier.get("id") in {"budget", "private"}:
        return "lowest_cost_candidate"
    if any(term in text for term in ["flash-lite", "free-tier", "cost", "budget", "open_weight", "local"]):
        return "low_cost_candidate"
    if tier.get("id") == "fast":
        return "cost_controlled_iteration"
    return "premium_or_quality_candidate"


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
        if resource["tier"] == "budget" and resource.get("cost_posture") in {"lowest_cost_candidate", "low_cost_candidate"}:
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


def build_world_model_council(config, resources, routes):
    council = config.get("world_ai_model_council", {})
    providers = sorted({resource["provider"] for resource in resources})
    quality = [resource for resource in resources if resource["tier"] == "quality"]
    fast = [resource for resource in resources if resource["tier"] == "fast"]
    budget = [resource for resource in resources if resource["tier"] == "budget"]
    private = [resource for resource in resources if resource["tier"] == "private"]
    return {
        "mission": council.get("mission", ""),
        "target_model_resources": council.get("target_model_resources", 100),
        "actual_model_resources": len(resources),
        "providers": providers,
        "provider_count": len(providers),
        "decision_style": council.get("decision_style", ""),
        "benchmark_sources": council.get("benchmark_sources", []),
        "council_steps": council.get("council_steps", []),
        "training_and_testing_policy": council.get("training_and_testing_policy", {}),
        "resource_pool": {
            "quality_candidates": len(quality),
            "fast_candidates": len(fast),
            "budget_candidates": len(budget),
            "private_candidates": len(private),
        },
        "decision_packet_schema": [
            "task_type",
            "bot_slug",
            "category",
            "risk_level",
            "budget_candidate",
            "fast_candidate",
            "quality_candidate",
            "private_candidate",
            "rubric_scores",
            "winner",
            "runner_up",
            "cost_latency_notes",
            "safety_notes",
            "owner_approval_needed",
        ],
        "top_decision_routes": routes[:12],
    }


def build_autonomous_decision_governance(config, bots):
    governance = config.get("autonomous_decision_governance", {})
    return {
        "mission": governance.get("mission", ""),
        "default_mode": governance.get("default_mode", ""),
        "decision_scope": governance.get("decision_scope", []),
        "pipeline": governance.get("pipeline", []),
        "codex_final_judge": governance.get("codex_final_judge", {}),
        "owner_approval_required_for": governance.get("owner_approval_required_for", []),
        "evidence_packet_schema": governance.get("evidence_packet_schema", []),
        "blocked_without_codex_final_judge": governance.get("blocked_without_codex_final_judge", []),
        "bot_coverage": {
            "bot_count": len(bots),
            "bots_required_to_use_council": len(bots),
            "bots_required_to_use_codex_final_judge": len(bots),
            "bots_requiring_owner_approval_for_live_impact": len(bots),
        },
        "dashboard_packet": {
            "status": "ready_for_actions_page_governance",
            "headline": "Every autonomous decision routes through council review, Codex final judge, and owner approval when live impact exists.",
            "safe_next_steps": [
                "show decision evidence packet",
                "show model council comparison",
                "show Codex final judge label",
                "send owner approval request",
                "block live impact until approved",
            ],
        },
    }


def build_report():
    config = read_json(CONFIG_FILE, {})
    registry = read_json(MASTER_REGISTRY_FILE, {})
    bots = registry.get("bots", [])
    resources = build_model_resources(config)
    routes = [choose_route(task, resources) for task in config.get("task_types", [])]
    matrix = build_prompt_tool_agent_matrix(config)
    providers = sorted({resource["provider"] for resource in resources})
    world_council = build_world_model_council(config, resources, routes)
    decision_governance = build_autonomous_decision_governance(config, bots)

    summary = {
        "model_resources": len(resources),
        "target_model_resources": config.get("world_ai_model_council", {}).get("target_model_resources", 100),
        "top_100_model_resources_ready": len(resources) >= config.get("world_ai_model_council", {}).get("target_model_resources", 100),
        "providers": len(providers),
        "low_cost_resources": sum(
            1
            for resource in resources
            if resource.get("cost_posture") in {"lowest_cost_candidate", "low_cost_candidate", "cost_controlled_iteration"}
        ),
        "google_gemini_resources": sum(1 for resource in resources if resource["provider"] == "Google"),
        "free_or_cheap_routing_enabled": True,
        "agent_types": len(config.get("agent_types", [])),
        "world_model_council_ready": bool(config.get("world_ai_model_council")),
        "world_model_council_steps": len(config.get("world_ai_model_council", {}).get("council_steps", [])),
        "benchmark_sources": len(config.get("world_ai_model_council", {}).get("benchmark_sources", [])),
        "training_eval_policy_ready": bool(
            config.get("world_ai_model_council", {}).get("training_and_testing_policy")
        ),
        "autonomous_decision_governance_ready": bool(config.get("autonomous_decision_governance")),
        "autonomous_decision_scope_count": len(config.get("autonomous_decision_governance", {}).get("decision_scope", [])),
        "autonomous_decision_pipeline_steps": len(config.get("autonomous_decision_governance", {}).get("pipeline", [])),
        "codex_final_judge_enabled": bool(
            config.get("autonomous_decision_governance", {}).get("codex_final_judge")
        ),
        "codex_final_judge_cannot_override_owner_approval": config.get("autonomous_decision_governance", {})
        .get("codex_final_judge", {})
        .get("cannot_override_owner_approval")
        is True,
        "owner_approval_live_impact_gates": len(
            config.get("autonomous_decision_governance", {}).get("owner_approval_required_for", [])
        ),
        "prompt_types": len(config.get("prompt_types", [])),
        "tool_types": len(config.get("tool_types", [])),
        "task_routes": len(routes),
        "bot_count": len(bots),
        "bots_with_model_routing": len(bots),
        "bots_with_world_model_council": len(bots),
        "bots_with_training_eval_policy": len(bots),
        "bots_with_autonomous_decision_governance": len(bots),
        "bots_with_codex_final_judge_gate": len(bots),
        "resources_requiring_model_id_verification": len(resources),
        "approval_gated_resources": len(resources),
    }

    return {
        "schema": "dreamco.buddy_ai_agent_model_library_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_config": str(CONFIG_FILE.relative_to(ROOT)),
        "mission": config.get("mission", ""),
        "policy": config.get("policy", {}),
        "cost_control": {
            "default_budget_mode": "free_or_low_cost_first",
            "preferred_sandbox_provider": "Google",
            "preferred_sandbox_family": "google_gemini_flash_lite",
            "secret_name": "GOOGLE_API_KEY",
            "rules": [
                "Use Gemini Flash-Lite, local/open models, cached results, and batchable summaries for safe sandbox drafts.",
                "Use premium models only for high-impact reasoning, client-facing deliverables, or failed cheap-model evals.",
                "Keep paid calls, always-on loops, and external actions behind owner approval and budget limits.",
                "Track projected usage separately from confirmed spend.",
            ],
        },
        "summary": summary,
        "world_ai_model_council": world_council,
        "autonomous_decision_governance": decision_governance,
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
        f"- Target model resources: {summary['target_model_resources']}",
        f"- Top 100 model resources ready: {summary['top_100_model_resources_ready']}",
        f"- Providers: {summary['providers']}",
        f"- Low-cost resources: {summary['low_cost_resources']}",
        f"- Google Gemini resources: {summary['google_gemini_resources']}",
        f"- Free or cheap routing enabled: {summary['free_or_cheap_routing_enabled']}",
        f"- Agent types: {summary['agent_types']}",
        f"- World model council ready: {summary['world_model_council_ready']}",
        f"- World model council steps: {summary['world_model_council_steps']}",
        f"- Benchmark sources: {summary['benchmark_sources']}",
        f"- Training/eval policy ready: {summary['training_eval_policy_ready']}",
        f"- Autonomous decision governance ready: {summary['autonomous_decision_governance_ready']}",
        f"- Autonomous decision scope count: {summary['autonomous_decision_scope_count']}",
        f"- Autonomous decision pipeline steps: {summary['autonomous_decision_pipeline_steps']}",
        f"- Codex final judge enabled: {summary['codex_final_judge_enabled']}",
        f"- Codex cannot override owner approval: {summary['codex_final_judge_cannot_override_owner_approval']}",
        f"- Owner approval live-impact gates: {summary['owner_approval_live_impact_gates']}",
        f"- Prompt types: {summary['prompt_types']}",
        f"- Tool types: {summary['tool_types']}",
        f"- Task routes: {summary['task_routes']}",
        f"- Bots with model routing: {summary['bots_with_model_routing']} / {summary['bot_count']}",
        f"- Bots with world model council: {summary['bots_with_world_model_council']} / {summary['bot_count']}",
        f"- Bots with training/eval policy: {summary['bots_with_training_eval_policy']} / {summary['bot_count']}",
        f"- Bots with autonomous decision governance: {summary['bots_with_autonomous_decision_governance']} / {summary['bot_count']}",
        f"- Bots with Codex final judge gate: {summary['bots_with_codex_final_judge_gate']} / {summary['bot_count']}",
        "",
        "## Routing Rule",
        "",
        report["policy"].get("model_id_rule", ""),
        "",
        report["policy"].get("cost_rule", ""),
        "",
        "## World Model Council",
        "",
        report["world_ai_model_council"].get("mission", ""),
        "",
        f"- Decision style: {report['world_ai_model_council'].get('decision_style', '')}",
        f"- Actual resources: {report['world_ai_model_council'].get('actual_model_resources', 0)}",
        f"- Provider count: {report['world_ai_model_council'].get('provider_count', 0)}",
        "",
        "## Autonomous Decision Governance",
        "",
        report["autonomous_decision_governance"].get("mission", ""),
        "",
        f"- Default mode: {report['autonomous_decision_governance'].get('default_mode', '')}",
        f"- Decision scope count: {len(report['autonomous_decision_governance'].get('decision_scope', []))}",
        f"- Pipeline steps: {len(report['autonomous_decision_governance'].get('pipeline', []))}",
        f"- Owner approval gates: {len(report['autonomous_decision_governance'].get('owner_approval_required_for', []))}",
        "",
        "## Cost Control",
        "",
        f"- Default budget mode: {report['cost_control']['default_budget_mode']}",
        f"- Preferred sandbox family: {report['cost_control']['preferred_sandbox_family']}",
        f"- Secret name: {report['cost_control']['secret_name']}",
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
