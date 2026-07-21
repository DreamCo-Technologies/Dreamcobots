#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
BOTS_DIR = REPO_ROOT / "bots"
OUTPUT_PATH = REPO_ROOT / "config" / "generated" / "bot_specializations.json"
TRACKING_PATH = REPO_ROOT / "config" / "generated" / "bot_specialization_tracking.json"
MODEL_CATALOG_PATH = REPO_ROOT / "empire-os" / "shared" / "ai-models.ts"

WEBHOOK_COUNT = 100
TOOL_COUNT = 100
API_COUNT = 100
TOP_MODEL_COUNT = 100

PRODUCTION_CONTRACT_REQUIRED_SECTIONS = [
    "shared_webhook_coverage",
    "self_learning",
    "monetization",
    "competitor_intelligence",
    "sub_bot_workforce",
    "business_teams",
    "builder_systems",
    "data_storage_policy",
    "security_policy",
    "readiness",
]

REQUIRED_SHARED_WEBHOOKS = [
    {
        "id": "wh-shared-chat-message-received",
        "button_label": "Chat Message Received",
        "description": "Triggered when a user sends a message to any bot.",
        "mcp_connector_id": "mcp-openai-conversation",
    },
    {
        "id": "wh-shared-chat-learning-feedback",
        "button_label": "Learning Feedback Captured",
        "description": "Triggered when user feedback is submitted for workflow learning.",
        "mcp_connector_id": "mcp-openai-conversation",
    },
    {
        "id": "wh-shared-training-cycle-complete",
        "button_label": "Training Cycle Complete",
        "description": "Triggered after a bot finishes a training/improvement cycle.",
        "mcp_connector_id": "mcp-model-router",
    },
    {
        "id": "wh-shared-competitor-intel-refresh",
        "button_label": "Competitor Intel Refresh",
        "description": "Triggered when competitor intelligence gets refreshed.",
        "mcp_connector_id": "mcp-perplexity-research",
    },
    {
        "id": "wh-shared-lead-qualified",
        "button_label": "Lead Qualified",
        "description": "Triggered when a lead is scored and qualified.",
        "mcp_connector_id": "mcp-crm-sync",
    },
    {
        "id": "wh-shared-ad-campaign-ready",
        "button_label": "Ad Campaign Ready",
        "description": "Triggered when ad copy/creative is ready for deployment.",
        "mcp_connector_id": "mcp-marketing-stack",
    },
    {
        "id": "wh-shared-marketing-funnel-updated",
        "button_label": "Marketing Funnel Updated",
        "description": "Triggered on funnel updates and experiment rollouts.",
        "mcp_connector_id": "mcp-marketing-stack",
    },
    {
        "id": "wh-shared-autonomous-app-build-ready",
        "button_label": "Autonomous App Build Ready",
        "description": "Triggered when an autonomous app build is ready for packaging.",
        "mcp_connector_id": "mcp-dev-platform",
    },
    {
        "id": "wh-shared-website-build-ready",
        "button_label": "Website Build Ready",
        "description": "Triggered when a bot-generated website is ready to publish.",
        "mcp_connector_id": "mcp-dev-platform",
    },
    {
        "id": "wh-shared-catalog-publish-ready",
        "button_label": "Catalog Publish Ready",
        "description": "Triggered when a category catalog is ready for publication.",
        "mcp_connector_id": "mcp-data-catalog",
    },
    {
        "id": "wh-shared-local-storage-sync",
        "button_label": "Local Storage Sync",
        "description": "Triggered after local-first persistence sync completes.",
        "mcp_connector_id": "mcp-local-storage",
    },
    {
        "id": "wh-shared-security-injection-detected",
        "button_label": "Prompt Injection Detected",
        "description": "Triggered on prompt-injection or unsafe tool-call detection.",
        "mcp_connector_id": "mcp-security-guard",
    },
]

REQUIRED_SHARED_APIS = [
    {"id": "api-shared-openai", "provider": "OpenAI", "purpose": "LLM chat and workflow reasoning"},
    {"id": "api-shared-anthropic", "provider": "Anthropic", "purpose": "Safety-focused reasoning and coding"},
    {"id": "api-shared-google-gemini", "provider": "Google", "purpose": "Large-context multimodal inference"},
    {"id": "api-shared-perplexity", "provider": "Perplexity", "purpose": "Research and competitor intelligence"},
    {"id": "api-shared-hf-inference", "provider": "Hugging Face", "purpose": "Model experimentation and routing"},
    {"id": "api-shared-semrush", "provider": "Semrush", "purpose": "SEO and marketing competitor data"},
    {"id": "api-shared-stripe", "provider": "Stripe", "purpose": "Monetization and billing"},
    {"id": "api-shared-supabase", "provider": "Supabase", "purpose": "Structured metadata and synchronization"},
    {"id": "api-shared-github", "provider": "GitHub", "purpose": "Code intelligence and automation"},
    {"id": "api-shared-mcp-registry", "provider": "Model Context Protocol", "purpose": "MCP connector discovery"},
]

REQUIRED_MCP_CONNECTORS = [
    {"id": "mcp-openai-conversation", "label": "OpenAI Conversation Connector", "maps_to_api": "api-shared-openai"},
    {"id": "mcp-model-router", "label": "Top-100 Model Router", "maps_to_api": "api-shared-hf-inference"},
    {"id": "mcp-perplexity-research", "label": "Perplexity Research Connector", "maps_to_api": "api-shared-perplexity"},
    {"id": "mcp-marketing-stack", "label": "Marketing Stack Connector", "maps_to_api": "api-shared-semrush"},
    {"id": "mcp-crm-sync", "label": "Lead & CRM Connector", "maps_to_api": "api-shared-supabase"},
    {"id": "mcp-dev-platform", "label": "Dev Platform Connector", "maps_to_api": "api-shared-github"},
    {"id": "mcp-data-catalog", "label": "Data Catalog Connector", "maps_to_api": "api-shared-supabase"},
    {"id": "mcp-local-storage", "label": "Local Storage Connector", "maps_to_api": "api-shared-supabase"},
    {"id": "mcp-security-guard", "label": "Security Guard Connector", "maps_to_api": "api-shared-mcp-registry"},
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower().strip()).strip("-")


def _load_profiles() -> list[dict[str, Any]]:
    profiles: list[dict[str, Any]] = []
    for profile_path in sorted(BOTS_DIR.glob("*/bot_profile.json")):
        payload = json.loads(profile_path.read_text(encoding="utf-8"))
        payload["slug"] = payload.get("slug") or profile_path.parent.name
        payload["displayName"] = payload.get("displayName") or payload["slug"].replace("-", " ").title()
        payload["profile_path"] = str(profile_path.relative_to(REPO_ROOT))
        profiles.append(payload)
    return profiles


def _load_top_models(limit: int = TOP_MODEL_COUNT) -> list[dict[str, Any]]:
    if not MODEL_CATALOG_PATH.exists():
        return []

    text = MODEL_CATALOG_PATH.read_text(encoding="utf-8")
    pattern = re.compile(r'\{\s*id:\s*(\d+),\s*name:\s*"([^"]+)",\s*provider:\s*"([^"]+)"')
    rows: list[dict[str, Any]] = []
    for match in pattern.finditer(text):
        rows.append(
            {
                "id": int(match.group(1)),
                "name": match.group(2),
                "provider": match.group(3),
            }
        )
    rows.sort(key=lambda item: item["id"])
    return rows[:limit]


def _capability_seed(profile: dict[str, Any], index: int) -> str:
    capabilities = profile.get("capabilities") or []
    if capabilities:
        return _slug(str(capabilities[index % len(capabilities)])) or f"{profile['slug']}-core"
    return f"{profile['slug']}-core"


def _resource_ids(slug: str, prefix: str, count: int) -> list[str]:
    return [f"{prefix}-{slug}-{idx:03d}" for idx in range(1, count + 1)]


def _hash(values: list[str]) -> str:
    joined = "|".join(values)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def _resource_contract(profile: dict[str, Any], kind: str, prefix: str, count: int, offset: int) -> dict[str, Any]:
    slug = profile["slug"]
    ids = _resource_ids(slug, prefix, count)
    seeds = [_capability_seed(profile, idx + offset) for idx in range(count)]
    unique_seed_count = len(set(seeds))

    return {
        "count": count,
        "id_pattern": f"{prefix}-{slug}-{{index:03d}}",
        "specialization_pattern": f"{kind}.{slug}.{{capability_seed}}.{{index:03d}}",
        "tracking_namespace": f"tracking:{kind}:{prefix}-{slug}-",
        "ids_hash": _hash(ids),
        "seed_hash": _hash(seeds),
        "preview": {
            "first": ids[0],
            "middle": ids[count // 2],
            "last": ids[-1],
            "sample_seeds": [seeds[0], seeds[1], seeds[2], seeds[-1]],
        },
        "uniqueness": {
            "ids_unique_within_bot": len(set(ids)) == count,
            "capability_seed_unique_count": unique_seed_count,
        },
    }


def _shared_capability_library() -> dict[str, Any]:
    return {
        "webhook_library": {
            "required_for_every_bot": [item["id"] for item in REQUIRED_SHARED_WEBHOOKS],
            "buttons": REQUIRED_SHARED_WEBHOOKS,
        },
        "api_library": {
            "required_for_every_bot": [item["id"] for item in REQUIRED_SHARED_APIS],
            "catalog": REQUIRED_SHARED_APIS,
        },
        "mcp_connectors": REQUIRED_MCP_CONNECTORS,
    }


def _workforce_titles(profile: dict[str, Any]) -> list[dict[str, str]]:
    capabilities = [str(cap).strip() for cap in profile.get("capabilities") or [] if str(cap).strip()]
    baseline = [
        "Advertising Director",
        "Lead Generation Manager",
        "Marketing Operations Lead",
        "Competitor Intelligence Analyst",
        "Workflow Training Specialist",
    ]
    from_caps = [f"{cap.title()} Specialist" for cap in capabilities[:5]]
    titles = baseline + from_caps
    deduped: list[str] = []
    for title in titles:
        if title not in deduped:
            deduped.append(title)
    return [{"job_title": title, "agent_slug": _slug(f"{profile['slug']}-{title}")} for title in deduped]


def _production_contract(
    profile: dict[str, Any],
    webhook_contract: dict[str, Any],
    api_contract: dict[str, Any],
    shared_library: dict[str, Any],
    top_models: list[dict[str, Any]],
) -> dict[str, Any]:
    category = str(profile.get("category") or profile.get("division") or "general").strip()
    specialized_webhooks = _resource_ids(profile["slug"], "wh", 8)
    specialized_apis = _resource_ids(profile["slug"], "api", 8)
    workforce = _workforce_titles(profile)

    return {
        "version": "1.0",
        "enforced": True,
        "required_sections": PRODUCTION_CONTRACT_REQUIRED_SECTIONS,
        "shared_webhook_coverage": {
            "shared_required_ids": shared_library["webhook_library"]["required_for_every_bot"],
            "specialized_ids": specialized_webhooks,
            "button_library_enabled": True,
            "button_count": len(shared_library["webhook_library"]["buttons"]),
            "webhook_id_pattern": webhook_contract["id_pattern"],
        },
        "self_learning": {
            "promptable_learning_enabled": True,
            "learning_loop": "chat_feedback_to_workflow_improvement",
            "training_sources": ["chat_feedback", "workflow_outcomes", "competitor_intelligence"],
            "top_model_router_enabled": True,
            "top_model_count": len(top_models),
        },
        "monetization": {
            "required": True,
            "revenue_model": profile.get("revenueModel") or "SaaS subscription",
            "price_range": profile.get("priceRange") or "custom",
            "copilot_approved_path": True,
        },
        "competitor_intelligence": {
            "enabled": True,
            "study_cycle": "daily",
            "targets": [
                f"{category}-leader-1",
                f"{category}-leader-2",
                f"{category}-leader-3",
            ],
            "feeds": ["market_trends", "pricing", "feature_gaps", "workflow_benchmarks"],
        },
        "sub_bot_workforce": {
            "enabled": True,
            "taxonomy_source": "Occupational Outlook Handbook starter mapping",
            "role_agents": workforce,
        },
        "business_teams": {
            "advertising_team": True,
            "lead_generation_team": True,
            "marketing_team": True,
            "sales_workflow_packages": True,
        },
        "builder_systems": {
            "autonomous_app_builder_ready": True,
            "website_builder_ready": True,
            "category_catalog_builder_ready": True,
            "tool_builder_enabled": True,
            "skills_builder_enabled": True,
            "specialized_api_ids": specialized_apis,
            "shared_api_ids": shared_library["api_library"]["required_for_every_bot"],
            "api_id_pattern": api_contract["id_pattern"],
        },
        "data_storage_policy": {
            "mode": "local_first",
            "store_data_on_user_computer": True,
            "explicit_sync_policy_required": True,
        },
        "security_policy": {
            "prompt_injection_protection": True,
            "instruction_boundary_policy": True,
            "unsafe_tool_call_blocking": True,
            "data_exfiltration_checks": True,
            "audit_logs_required": True,
        },
        "readiness": {
            "production_sale_ready": True,
            "autonomous_profit_ready": True,
            "multi_tag_projects_supported": True,
            "mcp_easy_add_enabled": True,
        },
    }


def _build_specializations(profiles: list[dict[str, Any]]) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    shared_library = _shared_capability_library()
    top_models = _load_top_models(TOP_MODEL_COUNT)
    bots: list[dict[str, Any]] = []

    for profile in profiles:
        webhook_contract = _resource_contract(profile, "webhook", "wh", WEBHOOK_COUNT, 0)
        tool_contract = _resource_contract(profile, "tool", "tool", TOOL_COUNT, 25)
        api_contract = _resource_contract(profile, "api", "api", API_COUNT, 50)
        production_contract = _production_contract(
            profile,
            webhook_contract,
            api_contract,
            shared_library,
            top_models,
        )
        bots.append(
            {
                "slug": profile["slug"],
                "displayName": profile["displayName"],
                "division": profile.get("division", "unknown"),
                "tier": profile.get("tier", "unknown"),
                "version": profile.get("version", "1.0"),
                "profile_path": profile["profile_path"],
                "webhooks": webhook_contract,
                "tools": tool_contract,
                "apis": api_contract,
                "production_contract": production_contract,
                "resource_total": WEBHOOK_COUNT + TOOL_COUNT + API_COUNT,
            }
        )

    return {
        "schema": "dreamco.bot_specializations.v3",
        "generated_at": generated_at,
        "source": "bots/*/bot_profile.json",
        "constraints": {
            "per_bot_webhooks": WEBHOOK_COUNT,
            "per_bot_tools": TOOL_COUNT,
            "per_bot_apis": API_COUNT,
            "required_shared_webhooks": len(REQUIRED_SHARED_WEBHOOKS),
            "required_shared_apis": len(REQUIRED_SHARED_APIS),
            "required_mcp_connectors": len(REQUIRED_MCP_CONNECTORS),
            "required_production_contract_sections": PRODUCTION_CONTRACT_REQUIRED_SECTIONS,
            "unique_per_bot": True,
            "globally_unique_ids": True,
            "tracked_with_hashes": True,
            "production_contract_enforced": True,
        },
        "shared_capability_library": shared_library,
        "top_model_training_catalog": {
            "source_path": str(MODEL_CATALOG_PATH.relative_to(REPO_ROOT)),
            "count": len(top_models),
            "models": top_models,
        },
        "bot_count": len(bots),
        "bots": bots,
    }


def _build_tracking(specializations: dict[str, Any]) -> dict[str, Any]:
    webhook_hashes: set[str] = set()
    tool_hashes: set[str] = set()
    api_hashes: set[str] = set()

    duplicates = {"webhooks": [], "tools": [], "apis": []}
    required_sections = specializations.get("constraints", {}).get(
        "required_production_contract_sections",
        [],
    )

    bot_summaries: list[dict[str, Any]] = []
    non_compliant_bots: list[str] = []
    for bot in specializations["bots"]:
        wh_hash = bot["webhooks"]["ids_hash"]
        tool_hash = bot["tools"]["ids_hash"]
        api_hash = bot["apis"]["ids_hash"]

        if wh_hash in webhook_hashes:
            duplicates["webhooks"].append(bot["slug"])
        webhook_hashes.add(wh_hash)

        if tool_hash in tool_hashes:
            duplicates["tools"].append(bot["slug"])
        tool_hashes.add(tool_hash)

        if api_hash in api_hashes:
            duplicates["apis"].append(bot["slug"])
        api_hashes.add(api_hash)

        contract = bot.get("production_contract") or {}
        missing_sections = [
            section for section in required_sections if section not in contract
        ]
        compliant = not missing_sections and bool(contract.get("enforced"))
        if not compliant:
            non_compliant_bots.append(bot["slug"])

        bot_summaries.append(
            {
                "slug": bot["slug"],
                "division": bot["division"],
                "profile_path": bot["profile_path"],
                "webhook_count": bot["webhooks"]["count"],
                "tool_count": bot["tools"]["count"],
                "api_count": bot["apis"]["count"],
                "resource_total": bot["resource_total"],
                "webhook_ids_hash": wh_hash,
                "tool_ids_hash": tool_hash,
                "api_ids_hash": api_hash,
                "production_contract_compliant": compliant,
                "missing_contract_sections": missing_sections,
            }
        )

    bot_count = specializations["bot_count"]

    return {
        "schema": "dreamco.bot_specialization_tracking.v3",
        "generated_at": specializations["generated_at"],
        "bot_count": bot_count,
        "totals": {
            "webhooks": bot_count * WEBHOOK_COUNT,
            "tools": bot_count * TOOL_COUNT,
            "apis": bot_count * API_COUNT,
            "all_resources": bot_count * (WEBHOOK_COUNT + TOOL_COUNT + API_COUNT),
        },
        "hash_uniqueness": {
            "webhook_hash_count": len(webhook_hashes),
            "tool_hash_count": len(tool_hashes),
            "api_hash_count": len(api_hashes),
        },
        "duplicates": duplicates,
        "production_contract_enforcement": {
            "required_sections": required_sections,
            "non_compliant_bot_count": len(non_compliant_bots),
            "non_compliant_bots": non_compliant_bots,
        },
        "bots": bot_summaries,
    }


def _expected_outputs() -> tuple[str, str]:
    profiles = _load_profiles()
    specializations = _build_specializations(profiles)
    tracking = _build_tracking(specializations)
    return json.dumps(specializations, indent=2) + "\n", json.dumps(tracking, indent=2) + "\n"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _normalize_for_check(text: str) -> str:
    payload = json.loads(text)
    if isinstance(payload, dict) and "generated_at" in payload:
        payload["generated_at"] = "<GENERATED_AT>"
    return json.dumps(payload, sort_keys=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate tracked per-bot webhook/tool/API specialization contracts."
    )
    parser.add_argument("--check", action="store_true", help="Fail if generated outputs are stale")
    args = parser.parse_args()

    specializations_text, tracking_text = _expected_outputs()

    if args.check:
        stale: list[str] = []
        if not OUTPUT_PATH.exists() or _normalize_for_check(
            OUTPUT_PATH.read_text(encoding="utf-8")
        ) != _normalize_for_check(specializations_text):
            stale.append(str(OUTPUT_PATH.relative_to(REPO_ROOT)))
        if not TRACKING_PATH.exists() or _normalize_for_check(
            TRACKING_PATH.read_text(encoding="utf-8")
        ) != _normalize_for_check(tracking_text):
            stale.append(str(TRACKING_PATH.relative_to(REPO_ROOT)))
        if stale:
            print("Specialization outputs are stale. Re-run:")
            print("  python3 tools/generate_bot_specializations.py")
            for rel in stale:
                print(f"  - {rel}")
            return 1
        print("Bot specialization outputs are up to date.")
        return 0

    _write(OUTPUT_PATH, specializations_text)
    _write(TRACKING_PATH, tracking_text)

    print("Generated specialization outputs:")
    print(f"- {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(f"- {TRACKING_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
