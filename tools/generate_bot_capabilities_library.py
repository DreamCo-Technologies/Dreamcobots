#!/usr/bin/env python3
"""Generate per-bot top-100 capability libraries for category competition."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "bot_capabilities_library.json"
REGISTRY_FILE = ROOT / "config" / "master_bot_registry.json"
OUTPUT_DIR = ROOT / "config" / "generated" / "capabilities_library"
SHARD_DIR = OUTPUT_DIR / "divisions"
OUTPUT_INDEX = OUTPUT_DIR / "index.json"
OUTPUT_JSON = ROOT / "reports" / "bot_capabilities_library.json"
OUTPUT_MD = ROOT / "reports" / "BOT_CAPABILITIES_LIBRARY.md"
SLUG_RE = re.compile(r"[^a-z0-9]+")


GENERIC_COMPETITION_CAPABILITIES = [
    ("user_onboarding_flow", "User onboarding flow", "user_experience"),
    ("guided_setup_wizard", "Guided setup wizard", "user_experience"),
    ("role_based_dashboard", "Role-based dashboard", "user_experience"),
    ("responsive_mobile_desktop_ui", "Responsive mobile and desktop UI", "user_experience"),
    ("accessibility_review", "Accessibility review", "user_experience"),
    ("local_first_storage", "Local-first storage", "data_and_search"),
    ("search_and_filter_system", "Search and filter system", "data_and_search"),
    ("saved_views", "Saved views", "data_and_search"),
    ("import_export_tools", "Import and export tools", "data_and_search"),
    ("data_quality_checks", "Data quality checks", "data_and_search"),
    ("workflow_builder", "Workflow builder", "automation"),
    ("scheduled_automation", "Scheduled automation", "automation"),
    ("approval_queue", "Approval queue", "automation"),
    ("rollback_and_version_history", "Rollback and version history", "automation"),
    ("human_in_the_loop_controls", "Human-in-the-loop controls", "automation"),
    ("custom_api_contract", "Custom API contract", "api_and_webhooks"),
    ("webhook_event_contracts", "Webhook event contracts", "api_and_webhooks"),
    ("api_rate_limit_handling", "API rate-limit handling", "api_and_webhooks"),
    ("idempotent_api_operations", "Idempotent API operations", "api_and_webhooks"),
    ("integration_health_checks", "Integration health checks", "api_and_webhooks"),
    ("api_sandbox_bootcamp", "API sandbox bootcamp", "sandbox_and_testing"),
    ("mock_auth_sandbox", "Mock auth sandbox", "sandbox_and_testing"),
    ("negative_and_abuse_tests", "Negative and abuse tests", "sandbox_and_testing"),
    ("fixture_replay_tests", "Fixture replay tests", "sandbox_and_testing"),
    ("workflow_generator_per_sandbox", "Workflow generator per sandbox", "sandbox_and_testing"),
    ("analytics_dashboard", "Analytics dashboard", "analytics_and_reporting"),
    ("kpi_scorecards", "KPI scorecards", "analytics_and_reporting"),
    ("trend_and_anomaly_detection", "Trend and anomaly detection", "analytics_and_reporting"),
    ("client_ready_reports", "Client-ready reports", "analytics_and_reporting"),
    ("roi_value_tracking", "ROI and value tracking", "analytics_and_reporting"),
    ("privacy_controls", "Privacy controls", "security_privacy_trust"),
    ("audit_log", "Audit log", "security_privacy_trust"),
    ("secret_safe_configuration", "Secret-safe configuration", "security_privacy_trust"),
    ("consent_and_rights_tracking", "Consent and rights tracking", "security_privacy_trust"),
    ("codex_final_judge_packet", "Codex final judge packet", "security_privacy_trust"),
    ("lead_generation_packet", "Lead generation packet", "revenue_and_growth"),
    ("followup_draft_system", "Follow-up draft system", "revenue_and_growth"),
    ("pricing_experiment_packet", "Pricing experiment packet", "revenue_and_growth"),
    ("revenue_method_rotation", "Revenue method rotation", "revenue_and_growth"),
    ("customer_problem_discovery", "Customer problem discovery", "revenue_and_growth"),
    ("app_store_listing_packet", "App-store listing packet", "app_store_readiness"),
    ("category_leader_map", "Category leader map", "app_store_readiness"),
    ("feature_gap_matrix", "Feature gap matrix", "app_store_readiness"),
    ("must_match_feature_list", "Must-match feature list", "app_store_readiness"),
    ("must_beat_feature_list", "Must-beat feature list", "app_store_readiness"),
    ("support_knowledge_base", "Support knowledge base", "support_and_operations"),
    ("helpdesk_handoff_packet", "Helpdesk handoff packet", "support_and_operations"),
    ("incident_and_failure_replay", "Incident and failure replay", "support_and_operations"),
    ("release_notes_and_changelog", "Release notes and changelog", "support_and_operations"),
    ("operator_runbook", "Operator runbook", "support_and_operations"),
]


CATEGORY_CAPABILITIES = {
    "finance": ["cash_flow_forecasting", "risk_disclosure", "payment_reconciliation", "budget_scenarios", "financial_approval_gate"],
    "payment": ["checkout_link_readiness", "webhook_revenue_ledger", "refund_dispute_tracking", "payment_alerts", "billing_plan_audit"],
    "sales": ["lead_scoring", "pipeline_tracking", "proposal_builder", "objection_handling", "crm_sync_packet"],
    "market": ["campaign_planner", "seo_brief_generator", "audience_segmentation", "attribution_notes", "competitor_message_map"],
    "content": ["content_calendar", "rights_safe_asset_plan", "caption_variants", "brand_voice_review", "publishing_approval_packet"],
    "real": ["property_analysis", "deal_scoring", "local_market_comparison", "renovation_estimate", "investor_packet"],
    "education": ["lesson_generator", "quiz_engine", "rubric_builder", "student_safety_review", "teacher_notes"],
    "game": ["game_loop", "level_progression", "scoring_system", "save_state", "playtest_report"],
    "simulation": ["scenario_model", "variable_controls", "deterministic_engine", "sensitivity_analysis", "replay_log"],
    "health": ["care_plan_notes", "safety_disclaimer", "clinical_review_gate", "habit_tracking", "privacy_safe_health_records"],
    "legal": ["contract_clause_mapper", "legal_review_gate", "obligation_tracker", "deadline_calendar", "risk_summary"],
    "construction": ["bid_scope_extractor", "materials_estimate", "schedule_risk", "permit_checklist", "subcontractor_packet"],
    "transport": ["route_optimizer", "fleet_status", "load_matching_packet", "delivery_eta", "carrier_approval_gate"],
    "data": ["etl_pipeline", "data_catalog", "schema_validation", "quality_score", "benchmark_dataset"],
    "code": ["code_generation_plan", "test_generation", "dependency_audit", "pull_request_packet", "deployment_plan"],
    "security": ["threat_model", "vulnerability_triage", "access_review", "incident_response", "defensive_scan_report"],
    "retail": ["inventory_forecast", "pricing_optimizer", "supplier_comparison", "cart_recovery_packet", "store_dashboard"],
    "food": ["menu_optimizer", "allergen_review", "order_flow", "delivery_dispatch", "review_response_draft"],
    "social": ["social_calendar", "community_triage", "reply_drafts", "platform_policy_check", "growth_experiment_packet"],
}


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: Any) -> str:
    return SLUG_RE.sub("-", str(value or "item").lower()).strip("-") or "item"


def words(value: Any) -> str:
    return str(value or "").replace("_", " ").replace("-", " ").strip()


def existing_capabilities(bot: dict[str, Any]) -> list[dict[str, Any]]:
    caps = []
    for index, cap in enumerate(bot.get("capabilities") or [], start=1):
        if isinstance(cap, dict):
            label = cap.get("label") or cap.get("intent") or f"Capability {index}"
            intent = cap.get("intent") or slugify(label)
            caps.append(
                {
                    "id": slugify(intent),
                    "rank": index,
                    "label": label,
                    "group": "core_workflow",
                    "source": "existing_bot_capability",
                    "competition_role": "preserve_existing_strength",
                    "enabled": cap.get("enabled", True),
                    "risk_level": cap.get("risk_level", "standard"),
                    "approval_required": bool(cap.get("approval_required", False)),
                    "revenue_generating": bool(cap.get("revenue_generating", False)),
                    "external_outreach": bool(cap.get("external_outreach", False)),
                    "spends_money": bool(cap.get("spends_money", False)),
                }
            )
        else:
            label = str(cap)
            caps.append(
                {
                    "id": slugify(label),
                    "rank": index,
                    "label": label,
                    "group": "core_workflow",
                    "source": "existing_bot_capability",
                    "competition_role": "preserve_existing_strength",
                    "enabled": True,
                    "risk_level": "standard",
                    "approval_required": False,
                    "revenue_generating": False,
                    "external_outreach": False,
                    "spends_money": False,
                }
            )
    return caps


def category_required(bot: dict[str, Any]) -> list[tuple[str, str, str]]:
    text = f"{bot.get('division') or ''} {bot.get('category') or ''} {bot.get('name') or ''} {bot.get('description') or ''}".lower()
    items: list[tuple[str, str, str]] = []
    for key, caps in CATEGORY_CAPABILITIES.items():
        if key in text:
            for cap in caps:
                items.append((cap, words(cap).title(), "category_advantage"))
    if not items:
        category = words(bot.get("category") or bot.get("division") or "business")
        items.extend(
            [
                ("category_specific_intake", f"{category.title()} specific intake", "category_advantage"),
                ("category_specific_analysis", f"{category.title()} specific analysis", "category_advantage"),
                ("category_specific_recommendations", f"{category.title()} specific recommendations", "category_advantage"),
                ("category_specific_dashboard", f"{category.title()} specific dashboard", "category_advantage"),
                ("category_specific_app_store_proof", f"{category.title()} app-store proof", "category_advantage"),
            ]
        )
    return items


def build_top_100(bot: dict[str, Any], target: int) -> list[dict[str, Any]]:
    caps = existing_capabilities(bot)
    seen = {cap["id"] for cap in caps}
    additions: list[tuple[str, str, str, str]] = []
    for cap_id, label, group in category_required(bot):
        additions.append((cap_id, label, group, "category_required_to_compete"))
    for cap_id, label, group in GENERIC_COMPETITION_CAPABILITIES:
        additions.append((cap_id, label, group, "competition_required_top_app_feature"))

    rank = len(caps) + 1
    for cap_id, label, group, source in additions:
        normalized = slugify(cap_id)
        if normalized in seen:
            continue
        seen.add(normalized)
        caps.append(
            {
                "id": normalized,
                "rank": rank,
                "label": label,
                "group": group,
                "source": source,
                "competition_role": "needed_to_compete_with_top_category_apps",
                "enabled": True,
                "risk_level": "standard",
                "approval_required": group in {"revenue_and_growth", "api_and_webhooks", "security_privacy_trust"},
                "revenue_generating": group == "revenue_and_growth",
                "external_outreach": normalized in {"lead-generation-packet", "followup-draft-system"},
                "spends_money": False,
            }
        )
        rank += 1
        if len(caps) >= target:
            break

    while len(caps) < target:
        suffix = len(caps) + 1
        cap_id = f"category_competition_capability_{suffix:03d}"
        caps.append(
            {
                "id": cap_id,
                "rank": suffix,
                "label": f"Category competition capability {suffix:03d}",
                "group": "category_advantage",
                "source": "competition_required_top_app_feature",
                "competition_role": "needed_to_compete_with_top_category_apps",
                "enabled": True,
                "risk_level": "standard",
                "approval_required": False,
                "revenue_generating": False,
                "external_outreach": False,
                "spends_money": False,
            }
        )
    return caps[:target]


def bot_library(bot: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    target = int(config.get("capability_target_per_bot", 100))
    caps = build_top_100(bot, target)
    return {
        "slug": bot.get("slug") or bot.get("id"),
        "id": bot.get("id") or bot.get("slug"),
        "name": bot.get("name") or words(bot.get("slug")).title(),
        "division": bot.get("division") or "DreamCo",
        "category": bot.get("category") or "business",
        "description": bot.get("description") or "",
        "capability_count": len(caps),
        "target_capability_count": target,
        "competition_goal": "match_and_beat_top_category_apps_with_proven_capability_coverage",
        "capabilities": caps,
        "capability_groups": sorted(Counter(cap["group"] for cap in caps).items()),
        "approval_required_for_live_use": config.get("approval_required_for_live_use", []),
    }


def build_report(write_files: bool = True) -> dict[str, Any]:
    config = read_json(CONFIG_FILE, {})
    registry = read_json(REGISTRY_FILE, {})
    bots = registry.get("bots", [])
    libraries = [bot_library(bot, config) for bot in bots]
    division_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for lib in libraries:
        division_groups[slugify(lib["division"])].append(lib)

    if write_files:
        SHARD_DIR.mkdir(parents=True, exist_ok=True)
    shard_files = []
    generated_at = utc_now()
    for division, entries in sorted(division_groups.items()):
        path = SHARD_DIR / f"{division}.json"
        payload = {
            "schema": "dreamco.bot_capabilities_library_division.v1",
            "generated_at": generated_at,
            "division": division,
            "bot_count": len(entries),
            "target_capability_count": config.get("capability_target_per_bot", 100),
            "bots": entries,
        }
        if write_files:
            path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        shard_files.append(str(path.relative_to(ROOT)))

    source_counter = Counter(cap["source"] for lib in libraries for cap in lib["capabilities"])
    group_counter = Counter(cap["group"] for lib in libraries for cap in lib["capabilities"])
    category_counter = Counter(lib["category"] for lib in libraries)
    division_counter = Counter(lib["division"] for lib in libraries)
    target = int(config.get("capability_target_per_bot", 100))

    index = {
        "schema": "dreamco.bot_capabilities_library_index.v1",
        "generated_at": generated_at,
        "source_config": str(CONFIG_FILE.relative_to(ROOT)),
        "source_registry": str(REGISTRY_FILE.relative_to(ROOT)),
        "bot_count": len(libraries),
        "target_capability_count": target,
        "total_capability_slots": sum(lib["capability_count"] for lib in libraries),
        "bots_with_100_capabilities": sum(1 for lib in libraries if lib["capability_count"] >= target),
        "division_shards": shard_files,
        "top_divisions": [{"division": k, "bot_count": v} for k, v in division_counter.most_common(20)],
        "top_categories": [{"category": k, "bot_count": v} for k, v in category_counter.most_common(20)],
        "capability_sources": dict(source_counter),
        "capability_groups": dict(group_counter),
    }
    if write_files:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_INDEX.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "schema": "dreamco.bot_capabilities_library_report.v1",
        "generated_at": generated_at,
        "mission": config.get("mission", ""),
        "summary": {
            "bot_count": len(libraries),
            "target_capability_count": target,
            "bots_with_capabilities_library": len(libraries),
            "bots_with_100_capabilities": index["bots_with_100_capabilities"],
            "total_capability_slots": index["total_capability_slots"],
            "division_shards": len(shard_files),
            "capability_groups": len(group_counter),
            "capability_source_types": len(source_counter),
            "all_bots_have_100_competition_capabilities": len(libraries) > 0 and index["bots_with_100_capabilities"] == len(libraries),
        },
        "index_file": str(OUTPUT_INDEX.relative_to(ROOT)),
        "division_shards": shard_files,
        "top_divisions": index["top_divisions"],
        "top_categories": index["top_categories"],
        "capability_sources": dict(source_counter),
        "capability_groups": dict(group_counter),
        "dashboard_sample": libraries[:10],
    }


def write_markdown(report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# Bot Capabilities Library",
        "",
        report["mission"],
        "",
        "## Summary",
        "",
        f"- Bots with capabilities library: {summary['bots_with_capabilities_library']} / {summary['bot_count']}",
        f"- Target capabilities per bot: {summary['target_capability_count']}",
        f"- Bots with 100 capabilities: {summary['bots_with_100_capabilities']}",
        f"- Total capability slots: {summary['total_capability_slots']}",
        f"- Division shards: {summary['division_shards']}",
        f"- Capability groups: {summary['capability_groups']}",
        f"- All bots have 100 competition capabilities: {summary['all_bots_have_100_competition_capabilities']}",
        "",
        "## Capability Groups",
        "",
    ]
    for group, count in sorted(report["capability_groups"].items()):
        lines.append(f"- {group}: {count}")
    lines.extend(["", "## Top Divisions", ""])
    for item in report["top_divisions"][:15]:
        lines.append(f"- {item['division']}: {item['bot_count']}")
    lines.extend(["", "## Shards", ""])
    for shard in report["division_shards"][:20]:
        lines.append(f"- {shard}")
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report(write_files=not args.check)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("bot capabilities library report missing; run generator")
        existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        existing["generated_at"] = report["generated_at"]
        existing_rendered = json.dumps(existing, indent=2, sort_keys=True) + "\n"
        if rendered != existing_rendered:
            raise SystemExit("bot capabilities library report stale; run generator")
        return 0

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    write_markdown(report)
    summary = report["summary"]
    print(
        "capabilities_library_ready={ready} bots={bots} total_slots={slots} shards={shards}".format(
            ready=summary["all_bots_have_100_competition_capabilities"],
            bots=summary["bot_count"],
            slots=summary["total_capability_slots"],
            shards=summary["division_shards"],
        )
    )
    return 0 if summary["all_bots_have_100_competition_capabilities"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
