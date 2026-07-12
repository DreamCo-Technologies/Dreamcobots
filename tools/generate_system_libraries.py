#!/usr/bin/env python3
"""Generate build libraries and per-bot integration contracts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "config" / "master_bot_registry.json"
OUTPUT_DIR = ROOT / "config" / "generated" / "system_libraries"
RESOURCE_SHARD_DIR = OUTPUT_DIR / "resources"
SLUG_RE = re.compile(r"[^a-z0-9]+")

LIBRARY_SPECS = {
    "tools": {
        "schema": "dreamco.tool_library.v1",
        "factory": "Tool Builder",
        "icon": "🔧",
        "description": "Typed, permission-aware tools with tests and audit metadata.",
    },
    "apis": {
        "schema": "dreamco.api_library.v1",
        "factory": "API Builder",
        "icon": "🔌",
        "description": "Versioned per-bot APIs with schemas, rate limits, and approval gates.",
    },
    "webhooks": {
        "schema": "dreamco.webhook_library.v1",
        "factory": "Webhook Builder",
        "icon": "🪝",
        "description": "Signed, idempotent per-bot event contracts with queued processing.",
    },
    "workflows": {
        "schema": "dreamco.workflow_library.v1",
        "factory": "Workflow Builder",
        "icon": "🔁",
        "description": "Reusable validation and delivery workflows with least privilege.",
    },
    "skills": {
        "schema": "dreamco.skill_library.v1",
        "factory": "Skill Builder",
        "icon": "🧠",
        "description": "Versioned multi-step skills with inputs, outputs, evidence, and tests.",
    },
    "sandboxes": {
        "schema": "dreamco.sandbox_library.v1",
        "factory": "Sandbox Builder",
        "icon": "🧪",
        "description": "Isolated test environments with fixtures, limits, and no live money movement.",
    },
    "resources": {
        "schema": "dreamco.resource_library.v1",
        "factory": "Resource Library Builder",
        "icon": "📚",
        "description": "Per-bot starter library with 100 curated resource slots, evidence sources, and learning prompts.",
    },
}

RESOURCE_CATEGORIES = [
    "official_documentation",
    "api_reference",
    "sdk_examples",
    "schema_templates",
    "sandbox_fixtures",
    "security_controls",
    "compliance_guides",
    "pricing_research",
    "market_research",
    "competitor_research",
    "customer_personas",
    "sales_scripts",
    "onboarding_guides",
    "support_playbooks",
    "workflow_examples",
    "automation_patterns",
    "webhook_patterns",
    "testing_patterns",
    "benchmark_datasets",
    "observability_metrics",
]


def resource_starter_kit(bot: dict[str, Any]) -> list[dict[str, Any]]:
    """Return 100 starter resources personalized to one bot."""
    slug = bot["slug"]
    division = bot["division"]
    resources: list[dict[str, Any]] = []
    for index in range(100):
        category = RESOURCE_CATEGORIES[index % len(RESOURCE_CATEGORIES)]
        resources.append(
            {
                "id": f"{slug}:resource:{index + 1:03d}",
                "rank": index + 1,
                "category": category,
                "title": f"{bot['name']} {category.replace('_', ' ').title()} Resource {index + 1:03d}",
                "purpose": (
                    f"Seed {bot['name']} with {category.replace('_', ' ')} evidence, examples, "
                    f"and reusable patterns for {division} work."
                ),
                "source_policy": "prefer_official_or_owner_approved_sources",
                "refresh_cadence": "weekly_review",
                "approval_required_for_live_use": category in {
                    "pricing_research",
                    "market_research",
                    "competitor_research",
                    "sales_scripts",
                    "automation_patterns",
                    "webhook_patterns",
                },
                "learning_prompt": (
                    f"Compare this resource against {bot['name']}'s latest tests, client goals, "
                    "and sandbox evidence before recommending a live action."
                ),
            }
        )
    return resources


def normalize_slug(value: object) -> str:
    return SLUG_RE.sub("-", str(value).lower()).strip("-")


def resource_index_entry(bot: dict[str, Any]) -> dict[str, Any]:
    division_slug = normalize_slug(bot["division"])
    return {
        "id": f"{bot['slug']}:resources",
        "bot_id": bot["slug"],
        "legacy_registry_id": bot["id"],
        "bot_slug": bot["slug"],
        "bot_name": bot["name"],
        "emoji": bot["emoji"],
        "division": bot["division"],
        "version": "1.0.0",
        "status": "generated",
        "owner": "DreamCo Technologies",
        "library_builder": f"{bot['slug']}-resource-library-builder",
        "resource_count": 100,
        "resource_categories": RESOURCE_CATEGORIES,
        "shard_path": f"config/generated/system_libraries/resources/{division_slug}.json",
        "controls": [
            "source_attribution_required",
            "owner_approved_live_sources",
            "refresh_cadence_tracked",
            "client_safe_summary_required",
            "sandbox_evidence_before_live_use",
        ],
    }

BUILDERS = [
    {
        "id": "full-bot-system",
        "name": "Full Bot System Builder",
        "icon": "🤖",
        "outputs": ["profile", "blueprint", "tool", "api", "webhook", "workflow", "skill", "sandbox", "tests"],
        "approval": "pull_request_required",
    },
    *[
        {
            "id": f"{name}-builder",
            "name": spec["factory"],
            "icon": spec["icon"],
            "outputs": ["sandbox" if name == "sandboxes" else name[:-1] if name.endswith("s") else name, "schema", "tests", "documentation"],
            "approval": "pull_request_required",
        }
        for name, spec in LIBRARY_SPECS.items()
    ],
]


def _bot_entry(bot: dict[str, Any], library: str) -> dict[str, Any]:
    slug = bot["slug"]
    common = {
        "id": f"{slug}:{library}",
        "bot_id": slug,
        "legacy_registry_id": bot["id"],
        "bot_slug": slug,
        "bot_name": bot["name"],
        "emoji": bot["emoji"],
        "division": bot["division"],
        "version": "1.0.0",
        "status": "generated",
        "owner": "DreamCo Technologies",
    }
    if library == "apis":
        return {
            **common,
            "base_path": f"/api/v1/bots/{slug}",
            "operations": [
                {"method": "GET", "path": "/status", "approval_required": False},
                {"method": "GET", "path": "/capabilities", "approval_required": False},
                {"method": "POST", "path": "/execute", "approval_required": True},
            ],
            "controls": ["authenticated", "schema_validated", "rate_limited", "retry_after_aware", "audited"],
            "sandbox_test_profile": {
                "name": f"{slug}-api-topline-sandbox",
                "network": "mocked_by_default",
                "secrets": "test_values_only",
                "money_movement": "disabled",
                "coverage_goal": "status_capabilities_execute_contracts",
                "required_checks": [
                    "openapi_schema_validation",
                    "request_response_contracts",
                    "auth_required_for_mutations",
                    "rate_limit_and_retry_after",
                    "idempotency_key_behavior",
                    "permission_denied_negative_tests",
                    "malformed_payload_rejection",
                    "timeout_and_circuit_breaker",
                    "audit_log_assertions",
                    "no_external_side_effects",
                ],
                "fixtures": [
                    "happy_path_goal",
                    "missing_required_field",
                    "unauthorized_execute",
                    "rate_limit_window",
                    "approval_required_action",
                ],
            },
        }
    if library == "webhooks":
        return {
            **common,
            "path": f"/webhooks/v1/bots/{slug}",
            "events": ["bot.started", "bot.completed", "bot.failed", "approval.requested"],
            "controls": [
                "hmac_sha256_signature",
                "constant_time_compare",
                "delivery_id_deduplication",
                "event_allowlist",
                "respond_within_10_seconds",
                "asynchronous_processing",
            ],
        }
    if library == "workflows":
        return {
            **common,
            "workflow": f"validate-{slug}",
            "trigger": "workflow_call",
            "permissions": {"contents": "read"},
            "stages": ["validate_profile", "unit_test", "sandbox_test", "security_scan", "review_packet"],
        }
    if library == "skills":
        return {
            **common,
            "skill": f"operate-{slug}",
            "inputs": ["goal", "constraints", "evidence"],
            "outputs": ["result", "evidence_log", "approval_requests"],
            "steps": ["plan", "validate", "execute_in_sandbox", "evaluate", "request_review"],
        }
    if library == "sandboxes":
        return {
            **common,
            "sandbox": f"{slug}-sandbox",
            "network": "deny_by_default",
            "secrets": "test_values_only",
            "money_movement": "disabled",
            "checks": ["deterministic_fixtures", "resource_limits", "timeout", "output_validation", "cleanup"],
            "api_contract_sandbox": f"{slug}-api-topline-sandbox",
        }
    if library == "resources":
        entry = resource_index_entry(bot)
        return {**entry, "resources": resource_starter_kit(bot)}
    return {
        **common,
        "tool": f"{slug}-toolkit",
        "capabilities": [item["intent"] for item in bot["capabilities"]],
        "controls": ["typed_inputs", "typed_outputs", "least_privilege", "audit_log", "unit_tests"],
    }


def build_outputs(registry: dict[str, Any]) -> dict[Path, dict[str, Any]]:
    generated_at = registry["updated_at"]
    bots = registry["bots"]
    outputs: dict[Path, dict[str, Any]] = {}
    summaries = []

    for name, spec in LIBRARY_SPECS.items():
        entries = [resource_index_entry(bot) if name == "resources" else _bot_entry(bot, name) for bot in bots]
        shard_paths: list[str] = []
        if name == "resources":
            by_division: dict[str, list[dict[str, Any]]] = {}
            for bot in bots:
                by_division.setdefault(bot["division"], []).append(_bot_entry(bot, "resources"))
            for division, shard_entries in sorted(by_division.items()):
                division_slug = normalize_slug(division)
                shard_path = RESOURCE_SHARD_DIR / f"{division_slug}.json"
                shard_payload = {
                    "schema": "dreamco.resource_library_shard.v1",
                    "generated_at": generated_at,
                    "generated_from": str(REGISTRY_PATH.relative_to(ROOT)),
                    "library": "resources",
                    "division": division,
                    "division_slug": division_slug,
                    "count": len(shard_entries),
                    "resources_per_bot": 100,
                    "entries": shard_entries,
                }
                outputs[shard_path] = shard_payload
                shard_paths.append(str(shard_path.relative_to(ROOT)))
        payload = {
            "schema": spec["schema"],
            "generated_at": generated_at,
            "generated_from": str(REGISTRY_PATH.relative_to(ROOT)),
            "library": name,
            "factory": spec["factory"],
            "description": spec["description"],
            "count": len(entries),
            "sharded": name == "resources",
            "shard_count": len(shard_paths),
            "shards": shard_paths,
            "entries": entries,
        }
        outputs[OUTPUT_DIR / f"{name}.json"] = payload
        summaries.append(
            {
                "id": name,
                "name": f"{name.title()} Library",
                "icon": spec["icon"],
                "count": len(entries),
                "description": spec["description"],
                "path": f"config/generated/system_libraries/{name}.json",
            }
        )

    outputs[OUTPUT_DIR / "index.json"] = {
        "schema": "dreamco.system_library_index.v1",
        "generated_at": generated_at,
        "bot_count": len(bots),
        "builders": BUILDERS,
        "libraries": summaries,
        "coverage": {
            "bots_with_tools": len(bots),
            "bots_with_apis": len(bots),
            "bots_with_webhooks": len(bots),
            "bots_with_workflows": len(bots),
            "bots_with_skills": len(bots),
            "bots_with_sandboxes": len(bots),
            "bots_with_resources": len(bots),
        },
        "security_baseline": {
            "github_actions": [
                "least_privilege_permissions",
                "immutable_action_references_recommended",
                "untrusted_input_isolated",
            ],
            "apis": [
                "authenticated_requests",
                "conditional_gets",
                "serial_mutations",
                "rate_limit_backoff",
            ],
            "webhooks": [
                "hmac_sha256",
                "delivery_id_deduplication",
                "event_allowlist",
                "fast_ack_then_queue",
            ],
        },
    }
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    outputs = build_outputs(registry)

    if args.check:
        stale = []
        for path, payload in outputs.items():
            expected = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                stale.append(str(path.relative_to(ROOT)))
        if stale:
            print("System libraries are stale:")
            for path in stale:
                print(f" - {path}")
            return 1
        print(f"All {len(LIBRARY_SPECS)} libraries cover {len(registry['bots'])} bots.")
        return 0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path, payload in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Generated {len(LIBRARY_SPECS)} system libraries for {len(registry['bots'])} bots.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
