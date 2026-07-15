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
API_SHARD_DIR = OUTPUT_DIR / "apis"
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
    "architecture_patterns",
    "data_models",
    "event_contracts",
    "permission_models",
    "risk_registers",
    "approval_checklists",
    "audit_log_patterns",
    "rate_limit_strategies",
    "retry_strategies",
    "idempotency_patterns",
    "error_taxonomies",
    "fallback_playbooks",
    "incident_response",
    "runbooks",
    "deployment_guides",
    "rollback_guides",
    "release_notes",
    "change_management",
    "versioning_guides",
    "migration_guides",
    "integration_blueprints",
    "connector_catalogs",
    "tool_blueprints",
    "skill_blueprints",
    "agent_prompts",
    "prompt_libraries",
    "evaluation_rubrics",
    "quality_metrics",
    "performance_profiles",
    "load_test_profiles",
    "chaos_test_scenarios",
    "privacy_reviews",
    "data_retention_policies",
    "access_control_guides",
    "secrets_management",
    "threat_models",
    "abuse_prevention",
    "fraud_prevention",
    "legal_review_notes",
    "financial_controls",
    "billing_guides",
    "cost_optimization",
    "unit_economics",
    "revenue_playbooks",
    "monetization_experiments",
    "sales_enablement",
    "proposal_templates",
    "contract_templates",
    "client_intake_forms",
    "discovery_questions",
    "implementation_plans",
    "training_materials",
    "knowledge_base_articles",
    "faq_libraries",
    "troubleshooting_guides",
    "customer_success_playbooks",
    "feedback_loops",
    "user_research",
    "analytics_dashboards",
    "kpi_catalogs",
    "roi_calculators",
    "case_studies",
    "demo_scripts",
    "demo_datasets",
    "sample_projects",
    "reference_apps",
    "code_snippets",
    "package_manifests",
    "dependency_research",
    "license_reviews",
    "vendor_assessments",
    "hosting_options",
    "deployment_targets",
    "infrastructure_templates",
    "database_patterns",
    "queue_patterns",
    "cache_patterns",
    "search_patterns",
    "ai_model_cards",
    "model_routing_rules",
    "fine_tuning_notes",
    "rag_sources",
    "vector_index_guides",
    "data_quality_rules",
    "synthetic_data_recipes",
    "simulation_scenarios",
    "browser_automation_recipes",
    "mobile_automation_recipes",
    "desktop_automation_recipes",
    "iot_device_guides",
    "operating_system_guides",
    "accessibility_reviews",
    "localization_guides",
    "brand_guidelines",
    "content_templates",
    "social_media_playbooks",
    "partnership_maps",
    "funding_resources",
    "procurement_guides",
    "community_resources",
]

TOP_AI_COMPANY_RESOURCE_SEEDS = [
    "OpenAI", "Anthropic", "Google DeepMind", "Microsoft AI", "Meta AI",
    "NVIDIA", "Amazon AGI", "Apple Machine Learning", "xAI", "Mistral AI",
    "Cohere", "Perplexity", "Hugging Face", "Databricks", "Scale AI",
    "Safe Superintelligence", "Inflection AI", "Character.AI", "Runway",
    "Midjourney", "Stability AI", "ElevenLabs", "Synthesia", "HeyGen",
    "Adept", "Anysphere", "Cursor", "Cloud IDE Platform", "Cognition", "Magic",
    "Poolside", "Sourcegraph", "Tabnine", "Codeium", "Glean",
    "Writer", "Jasper", "Harvey", "Hebbia", "Abridge",
    "Tempus AI", "Insilico Medicine", "PathAI", "Owkin", "Recursion",
    "Cerebras", "Groq", "SambaNova", "Together AI", "CoreWeave",
    "Lambda", "VAST Data", "Pinecone", "Weaviate", "Qdrant",
    "LangChain", "LlamaIndex", "Weights & Biases", "Modal", "Replicate",
    "Roboflow", "Labelbox", "Snorkel AI", "Surge AI", "Mercor",
    "Figure AI", "Covariant", "Skild AI", "Physical Intelligence", "Sanctuary AI",
    "Anduril", "Shield AI", "Palantir AI", "C3 AI", "DataRobot",
    "UiPath AI", "ServiceNow AI", "Salesforce AI", "Adobe Firefly", "Canva AI",
    "Notion AI", "Grammarly", "Otter.ai", "Descript", "Pika",
    "Suno", "Udio", "Krea", "Leonardo AI", "DeepSeek",
    "Moonshot AI", "Zhipu AI", "01.AI", "MiniMax", "Baichuan",
    "SenseTime", "iFlytek", "G42", "Aleph Alpha", "MosaicML",
]

BOOTCAMP_PERSONAS = ["owner", "buddy", "client"]

SANDBOX_BOOTCAMP_MODULES = [
    {
        "id": "bootcamp_01_contract",
        "title": "Contract and schema proof",
        "goal": "Prove every request, response, event, and error shape before runtime work.",
        "checks": ["schema_compile", "example_payloads", "negative_contract_cases"],
    },
    {
        "id": "bootcamp_02_fixture_lab",
        "title": "Fixture lab",
        "goal": "Build deterministic happy-path, edge-case, abuse-case, and rollback fixtures.",
        "checks": ["happy_path_fixture", "edge_fixture", "abuse_fixture", "rollback_fixture"],
    },
    {
        "id": "bootcamp_03_api_obstacle_course",
        "title": "API obstacle course",
        "goal": "Exercise auth, rate limits, idempotency, timeouts, retries, and audit logs.",
        "checks": ["auth_gate", "rate_limit", "idempotency", "timeout", "audit_log"],
    },
    {
        "id": "bootcamp_04_safety_ring",
        "title": "Safety ring",
        "goal": "Block live money, outreach, deployment, credential, medical, legal, and security impact by default.",
        "checks": ["no_live_money", "no_live_outreach", "no_secret_leak", "approval_required"],
    },
    {
        "id": "bootcamp_05_builder_drill",
        "title": "Bot builder drill",
        "goal": "Train the operator to build, test, debug, document, and package the bot like a client product.",
        "checks": ["build_packet", "debug_packet", "client_summary", "prospectus_update"],
    },
    {
        "id": "bootcamp_06_failure_replay",
        "title": "Failure replay",
        "goal": "Replay old failures and prove they stay fixed with regression evidence.",
        "checks": ["known_failure_fixture", "regression_test", "fix_evidence", "retest_command"],
    },
    {
        "id": "bootcamp_07_graduation",
        "title": "Graduation review",
        "goal": "Produce a demo-ready, client-safe, production-gated readiness packet.",
        "checks": ["readiness_score", "remaining_risks", "approval_packet", "handoff_notes"],
    },
]

WORLD_CLASS_SANDBOX_PRINCIPLES = [
    "hermetic_by_default",
    "deterministic_fixtures",
    "network_and_secrets_mocked",
    "least_privilege_permissions",
    "api_contract_first",
    "workflow_generated_per_test",
    "negative_tests_before_live_use",
    "human_approval_for_external_impact",
    "audit_log_required",
    "replayable_failure_evidence",
]


def resource_starter_kit(bot: dict[str, Any]) -> list[dict[str, Any]]:
    """Return 100 starter resources personalized to one bot."""
    slug = bot["slug"]
    division = bot["division"]
    resources: list[dict[str, Any]] = []
    for index in range(100):
        category = RESOURCE_CATEGORIES[index % len(RESOURCE_CATEGORIES)]
        company_seed = TOP_AI_COMPANY_RESOURCE_SEEDS[index % len(TOP_AI_COMPANY_RESOURCE_SEEDS)]
        resources.append(
            {
                "id": f"{slug}:resource:{index + 1:03d}",
                "rank": index + 1,
                "category": category,
                "ai_company_practice_seed": company_seed,
                "title": f"{bot['name']} {category.replace('_', ' ').title()} Resource {index + 1:03d}",
                "purpose": (
                    f"Seed {bot['name']} with {category.replace('_', ' ')} evidence, examples, "
                    f"and reusable patterns for {division} work using public, owner-approved lessons "
                    f"inspired by {company_seed} style AI product practice."
                ),
                "source_policy": "prefer_official_or_owner_approved_sources",
                "source_boundaries": [
                    "use_public_documentation_and_original_notes_only",
                    "do_not_copy_private_or_proprietary_company_material",
                    "store_source_url_license_and_refresh_date_when_added",
                ],
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


def capability_items(bot: dict[str, Any], limit: int = 6) -> list[dict[str, Any]]:
    capabilities = bot.get("capabilities", [])
    normalized: list[dict[str, Any]] = []
    for index, capability in enumerate(capabilities[:limit]):
        intent = normalize_slug(capability.get("intent") or capability.get("label") or f"capability-{index + 1}")
        label = capability.get("label") or intent.replace("-", " ").title()
        normalized.append(
            {
                "intent": intent,
                "label": label,
                "risk_level": capability.get("risk_level", "standard"),
                "approval_required": bool(capability.get("approval_required", False)),
                "revenue_generating": bool(capability.get("revenue_generating", False)),
                "spends_money": bool(capability.get("spends_money", False)),
                "external_outreach": bool(capability.get("external_outreach", False)),
            }
        )
    if normalized:
        return normalized
    return [
        {
            "intent": normalize_slug(bot["category"]),
            "label": str(bot["category"]).replace("-", " ").title(),
            "risk_level": "standard",
            "approval_required": False,
            "revenue_generating": False,
            "spends_money": False,
            "external_outreach": False,
        }
    ]


def custom_api_operations(bot: dict[str, Any]) -> list[dict[str, Any]]:
    slug = bot["slug"]
    operations = [
        {
            "operation_id": f"{normalize_slug(slug)}_get_status",
            "method": "GET",
            "path": "/status",
            "approval_required": False,
            "purpose": f"Return runtime, readiness, and approval state for {bot['name']}.",
        },
        {
            "operation_id": f"{normalize_slug(slug)}_get_capabilities",
            "method": "GET",
            "path": "/capabilities",
            "approval_required": False,
            "purpose": f"Return {bot['name']} capabilities, limits, and sandbox options.",
        },
    ]
    for capability in capability_items(bot):
        path_slug = capability["intent"]
        approval_required = capability["approval_required"] or capability["spends_money"] or capability["external_outreach"]
        operations.extend(
            [
                {
                    "operation_id": f"{normalize_slug(slug)}_{path_slug}_plan",
                    "method": "POST",
                    "path": f"/capabilities/{path_slug}/plan",
                    "approval_required": False,
                    "purpose": f"Create a sandbox-first plan for {capability['label']}.",
                    "capability": capability,
                },
                {
                    "operation_id": f"{normalize_slug(slug)}_{path_slug}_sandbox",
                    "method": "POST",
                    "path": f"/capabilities/{path_slug}/sandbox",
                    "approval_required": False,
                    "purpose": f"Run the {capability['label']} bootcamp fixture without live side effects.",
                    "capability": capability,
                },
                {
                    "operation_id": f"{normalize_slug(slug)}_{path_slug}_request_approval",
                    "method": "POST",
                    "path": f"/capabilities/{path_slug}/approval-request",
                    "approval_required": approval_required,
                    "purpose": f"Prepare owner approval packet before live use of {capability['label']}.",
                    "capability": capability,
                },
            ]
        )
    operations.append(
        {
            "operation_id": f"{normalize_slug(slug)}_execute_reviewed_packet",
            "method": "POST",
            "path": "/execute-reviewed-packet",
            "approval_required": True,
            "purpose": f"Execute only a reviewed, approved, audited {bot['name']} operation packet.",
        }
    )
    return operations


def custom_api_schema(bot: dict[str, Any]) -> dict[str, Any]:
    capabilities = capability_items(bot)
    return {
        "request_schema": {
            "type": "object",
            "required": ["goal", "persona", "mode"],
            "properties": {
                "goal": {"type": "string", "description": f"Business problem for {bot['name']} to solve."},
                "persona": {"type": "string", "enum": BOOTCAMP_PERSONAS},
                "mode": {"type": "string", "enum": ["sandbox", "approval_request", "reviewed_live_packet"]},
                "capability": {
                    "type": "string",
                    "enum": [capability["intent"] for capability in capabilities],
                },
                "constraints": {"type": "array", "items": {"type": "string"}},
                "evidence": {"type": "array", "items": {"type": "string"}},
            },
        },
        "response_schema": {
            "type": "object",
            "required": ["bot_slug", "mode", "result", "evidence_log", "approval_required"],
            "properties": {
                "bot_slug": {"const": bot["slug"]},
                "division": {"const": bot["division"]},
                "mode": {"type": "string"},
                "result": {"type": "object"},
                "evidence_log": {"type": "array", "items": {"type": "string"}},
                "approval_required": {"type": "boolean"},
                "next_best_action": {"type": "string"},
            },
        },
    }


def custom_api_fixtures(bot: dict[str, Any]) -> list[dict[str, Any]]:
    fixtures = []
    for capability in capability_items(bot, limit=4):
        fixtures.append(
            {
                "id": f"{bot['slug']}:{capability['intent']}:happy-path",
                "capability": capability["intent"],
                "persona": "client" if capability["revenue_generating"] else "owner",
                "mode": "sandbox",
                "goal": f"Use {bot['name']} to solve a {capability['label']} problem in {bot['division']}.",
                "expected": [
                    "returns_client_safe_plan",
                    "writes_evidence_log",
                    "does_not_take_live_external_action",
                ],
            }
        )
    fixtures.extend(
        [
            {
                "id": f"{bot['slug']}:unauthorized-live-action",
                "mode": "reviewed_live_packet",
                "expected": ["reject_without_owner_approval", "write_approval_request"],
            },
            {
                "id": f"{bot['slug']}:malformed-payload",
                "mode": "sandbox",
                "expected": ["schema_error", "client_safe_error_message"],
            },
        ]
    )
    return fixtures


def custom_api_contract(bot: dict[str, Any]) -> dict[str, Any]:
    capabilities = capability_items(bot)
    return {
        "custom_to_bot": True,
        "division_context": bot["division"],
        "category_context": bot["category"],
        "primary_capabilities": capabilities,
        "business_owner_use_cases": [
            f"Find unsolved {bot['category']} problems for {bot['division']} customers.",
            f"Package {bot['name']} sandbox results into a client-safe offer.",
            f"Request owner approval before any live money, outreach, deployment, or external-impact action.",
        ],
        "buddy_use_cases": [
            "route_to_best_capability",
            "generate_bootcamp_workflow",
            "debug_failed_fixture",
            "prepare_approval_packet",
        ],
        "client_use_cases": [
            "run_safe_demo",
            "see_expected_outputs",
            "understand_limits_and_required_approvals",
        ],
        "schemas": custom_api_schema(bot),
        "fixtures": custom_api_fixtures(bot),
    }


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


def api_index_entry(bot: dict[str, Any]) -> dict[str, Any]:
    division_slug = normalize_slug(bot["division"])
    capabilities = capability_items(bot)
    return {
        "id": f"{bot['slug']}:apis",
        "bot_id": bot["slug"],
        "legacy_registry_id": bot["id"],
        "bot_slug": bot["slug"],
        "bot_name": bot["name"],
        "emoji": bot["emoji"],
        "division": bot["division"],
        "category": bot["category"],
        "version": "1.0.0",
        "status": "generated",
        "owner": "DreamCo Technologies",
        "base_path": f"/api/v1/bots/{bot['slug']}",
        "custom_to_bot": True,
        "operation_count": len(custom_api_operations(bot)),
        "primary_capabilities": [capability["intent"] for capability in capabilities],
        "shard_path": f"config/generated/system_libraries/apis/{division_slug}.json",
        "controls": ["authenticated", "schema_validated", "rate_limited", "retry_after_aware", "audited"],
        "sandbox_bootcamp": f"{bot['slug']}:api-sandbox-bootcamp",
    }


def sandbox_workflow_generator(bot: dict[str, Any], test_name: str, source: str) -> dict[str, Any]:
    slug = bot["slug"]
    workflow_id = f"{slug}-{test_name}-workflow"
    return {
        "id": workflow_id,
        "source": source,
        "generated_workflow_name": f"{bot['name']} {test_name.replace('-', ' ').title()} Workflow",
        "workflow_file": f".github/workflows/generated/{workflow_id}.yml",
        "trigger": "workflow_call",
        "permissions": {"contents": "read", "actions": "read"},
        "timeout_minutes": 15,
        "concurrency": {
            "group": f"{slug}-{test_name}",
            "cancel_in_progress": True,
        },
        "stages": [
            "checkout_readonly",
            "install_locked_dependencies",
            "load_mock_fixtures",
            "run_contract_checks",
            "run_negative_safety_checks",
            "run_bootcamp_persona_drills",
            "write_evidence_packet",
        ],
        "artifacts": [
            f"reports/sandbox_bootcamps/{slug}/{test_name}/summary.json",
            f"reports/sandbox_bootcamps/{slug}/{test_name}/client_notes.md",
        ],
        "live_action_policy": "blocked_unless_owner_approval_packet_is_green",
    }


def api_sandbox_bootcamp(bot: dict[str, Any]) -> dict[str, Any]:
    slug = bot["slug"]
    test_name = "api-sandbox-bootcamp"
    return {
        "id": f"{slug}:{test_name}",
        "name": f"{bot['name']} API Sandbox Bootcamp",
        "audiences": BOOTCAMP_PERSONAS,
        "workflow_generator": sandbox_workflow_generator(bot, test_name, "api_library"),
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
            "client_safe_error_messages",
            "rollback_packet_created",
        ],
        "bootcamp_modules": SANDBOX_BOOTCAMP_MODULES,
        "personas": {
            "owner": [
                "learn_what_the_bot_can_safely_do",
                "approve_or_reject_live_actions",
                "read_client_ready_summary",
            ],
            "buddy": [
                "route_task_to_best_bot",
                "debug_failed_contract",
                "generate_fix_packet",
            ],
            "client": [
                "try_safe_demo_scenario",
                "see_expected_business_value",
                "understand_limits_and_approvals",
            ],
        },
        "graduation_packet": [
            "api_contract_report",
            "workflow_run_summary",
            "sandbox_evidence",
            "risk_and_approval_summary",
            "client_demo_script",
        ],
    }


def sandbox_bootcamp_suite(bot: dict[str, Any]) -> dict[str, Any]:
    slug = bot["slug"]
    test_name = "world-class-sandbox-bootcamp"
    return {
        "id": f"{slug}:{test_name}",
        "name": f"{bot['name']} Bot Building Bootcamp",
        "description": "A replayable sandbox training course for the owner, Buddy, and clients to learn, build, test, debug, and approve the bot safely.",
        "world_class_principles": WORLD_CLASS_SANDBOX_PRINCIPLES,
        "workflow_generator": sandbox_workflow_generator(bot, test_name, "sandbox_library"),
        "api_bootcamp": f"{slug}:api-sandbox-bootcamp",
        "modules": SANDBOX_BOOTCAMP_MODULES,
        "training_tracks": [
            {
                "persona": "owner",
                "goal": "Understand what the bot can sell, demo, approve, and safely operate.",
                "final_exercise": "Approve or reject a live-action packet from sandbox evidence.",
            },
            {
                "persona": "buddy",
                "goal": "Learn routing, debugging, regression replay, and fix-packet generation.",
                "final_exercise": "Repair a seeded failure and regenerate the evidence packet.",
            },
            {
                "persona": "client",
                "goal": "Experience a safe demo that explains value, limits, data handling, and next steps.",
                "final_exercise": "Run a client scenario and receive a prospectus-ready summary.",
            },
        ],
        "pass_criteria": [
            "all_contract_and_negative_tests_green",
            "no_live_external_side_effects",
            "workflow_evidence_packet_created",
            "approval_requirements_visible",
            "client_summary_is_safe_and_plain_language",
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
        bootcamp = api_sandbox_bootcamp(bot)
        return {
            **common,
            "base_path": f"/api/v1/bots/{slug}",
            "operations": custom_api_operations(bot),
            "controls": ["authenticated", "schema_validated", "rate_limited", "retry_after_aware", "audited"],
            "custom_contract": custom_api_contract(bot),
            "sandbox_test_profile": {
                "name": f"{slug}-api-topline-sandbox",
                "network": "mocked_by_default",
                "secrets": "test_values_only",
                "money_movement": "disabled",
                "coverage_goal": f"{slug}_custom_capability_contracts",
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
                    *[fixture["id"] for fixture in custom_api_fixtures(bot)],
                    f"{slug}:rate-limit-window",
                    f"{slug}:approval-required-action",
                ],
            },
            "sandbox_bootcamp": bootcamp,
            "workflow_generator": bootcamp["workflow_generator"],
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
            "sandbox_workflow_generators": [
                sandbox_workflow_generator(bot, "profile-validation-bootcamp", "workflow_library"),
                sandbox_workflow_generator(bot, "api-sandbox-bootcamp", "workflow_library"),
                sandbox_workflow_generator(bot, "world-class-sandbox-bootcamp", "workflow_library"),
            ],
            "bootcamp_outputs": [
                "owner_training_packet",
                "buddy_debug_packet",
                "client_demo_packet",
                "approval_gate_packet",
            ],
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
        bootcamp = sandbox_bootcamp_suite(bot)
        return {
            **common,
            "sandbox": f"{slug}-sandbox",
            "network": "deny_by_default",
            "secrets": "test_values_only",
            "money_movement": "disabled",
            "checks": [
                "deterministic_fixtures",
                "resource_limits",
                "timeout",
                "output_validation",
                "cleanup",
                "api_contract_bootcamp",
                "workflow_generator_presence",
                "owner_buddy_client_training_tracks",
            ],
            "api_contract_sandbox": f"{slug}-api-topline-sandbox",
            "workflow_generator": bootcamp["workflow_generator"],
            "bootcamp_suite": bootcamp,
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
        if name == "resources":
            entries = [resource_index_entry(bot) for bot in bots]
        elif name == "apis":
            entries = [api_index_entry(bot) for bot in bots]
        else:
            entries = [_bot_entry(bot, name) for bot in bots]
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
        if name == "apis":
            by_division: dict[str, list[dict[str, Any]]] = {}
            for bot in bots:
                by_division.setdefault(bot["division"], []).append(_bot_entry(bot, "apis"))
            for division, shard_entries in sorted(by_division.items()):
                division_slug = normalize_slug(division)
                shard_path = API_SHARD_DIR / f"{division_slug}.json"
                shard_payload = {
                    "schema": "dreamco.api_library_shard.v1",
                    "generated_at": generated_at,
                    "generated_from": str(REGISTRY_PATH.relative_to(ROOT)),
                    "library": "apis",
                    "division": division,
                    "division_slug": division_slug,
                    "count": len(shard_entries),
                    "custom_to_bot": True,
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
            "sharded": name in {"apis", "resources"},
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
            "bots_with_api_sandbox_bootcamps": len(bots),
            "bots_with_custom_api_contracts": len(bots),
            "bots_with_sandbox_workflow_generators": len(bots),
            "bots_with_owner_buddy_client_bootcamp_tracks": len(bots),
            "bots_with_top_ai_company_resource_seeds": len(bots),
        },
        "bootcamp_baseline": {
            "name": "World Class Bot Building Sandbox Bootcamp",
            "audiences": BOOTCAMP_PERSONAS,
            "sandbox_principles": WORLD_CLASS_SANDBOX_PRINCIPLES,
            "module_count": len(SANDBOX_BOOTCAMP_MODULES),
            "top_ai_company_resource_seed_count": len(TOP_AI_COMPANY_RESOURCE_SEEDS),
            "source_boundaries": [
                "public_documentation_only",
                "owner_approved_notes_only",
                "no_private_or_proprietary_company_material",
                "record_source_url_license_and_refresh_date",
            ],
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
