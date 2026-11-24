#!/usr/bin/env python3
"""Build Buddy's full-fleet division, specialist-portfolio and opportunity execution map."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "config/bots/bot-manifests.generated.json"
DOMAIN_SOURCE = ROOT / "shared/division-production-contract.ts"
MASTERBOTS = ROOT / "config/masterbot-65-registry.json"
CROSSWALK = ROOT / "config/generated/masterbot-45-domain-crosswalk.json"
CHARTERS = ROOT / "config/supplemental-portfolio-capability-charters.json"
MONEY_REGISTRY = ROOT / "money_os/config/bot_registry.json"
REVENUE_LANES = ROOT / "money_os/config/revenue_lanes_expanded.json"
OPPORTUNITY_SOURCES = ROOT / "money_os/data/opportunity_sources.json"
MONETIZATION = ROOT / "money_os/config/monetization_matrix.json"
OUT = ROOT / "config/generated/buddy-fleet-execution-map.json"

def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).casefold())

def slug_norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value).casefold()).strip("-")

def domain_names(source: str) -> list[str]:
    pattern = re.compile(r"^  ([A-Za-z][A-Za-z0-9]+): \{\n([\s\S]*?)^  \},?$", re.MULTILINE)
    names = [m.group(1) for m in pattern.finditer(source)
             if "purpose:" in m.group(2) and "focusAreas:" in m.group(2)]
    if len(names) != 45 or len({norm(x) for x in names}) != 45:
        raise ValueError(f"Expected exactly 45 unique canonical domains, found {len(names)}")
    return names

def load_source_bots() -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path in sorted((ROOT / "App_bots").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        division = data.get("division") or path.stem
        for bot in data.get("bots", []):
            slug = str(bot.get("slug", "")).strip()
            if slug:
                result[slug].append({
                    **bot, "_source_division": division,
                    "_source_path": path.relative_to(ROOT).as_posix(),
                })
    return result

def load_lane_index(lanes: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in lanes.get("lanes", [])}

REVENUE_TERMS = (
    "revenue", "money", "income", "affiliate", "lead", "sales", "deal", "coupon",
    "price", "resale", "grant", "contract", "real-estate", "property", "foreclosure",
    "settlement", "unclaimed", "fiverr", "freelance", "job", "ecommerce", "shopify",
    "amazon", "store", "marketplace", "subscription", "saas", "sponsor", "creator",
    "monetiz", "funding", "procurement", "rfp", "tax", "rebate", "savings", "bill",
    "invoice", "receivable", "parts", "equipment", "vehicle", "insurance", "royalty",
    "licensing", "digital-product", "business-acquisition", "wealth", "arbitrage",
    "investing", "merchant", "checkout", "payout", "commission", "pricing",
)
REGISTRY_LANE_MAP = {
    "services": ("freelance_bid_intel", "professional_services"),
    "grants_contracts": ("rfp_matcher", "grants_contracts"),
    "real_estate": ("business_acquisition", "property_opportunities"),
    "settlements_claims": ("warranty_recall", "settlements"),
    "lead_generation": ("local_service_leads", "professional_services"),
    "revenue_orchestration": ("enterprise_automation", "software_partners"),
    "software_services": ("enterprise_automation", "software_partners"),
    "jobs": ("freelance_bid_intel", "jobs_gigs"),
    "wealth_opportunities": ("business_acquisition", "business_marketplaces"),
    "compute_or_digital_assets": ("digital_asset_scout", "licensed_data"),
    "orchestration": ("enterprise_automation", "software_partners"),
}
REVENUE_EVENT_MAP = {
    "affiliate": "commission_confirmed_by_network",
    "lead_fee": "lead_accepted_or_qualified_by_buyer",
    "qualified_lead": "lead_accepted_or_qualified_by_buyer",
    "permitted_lead_fee": "lead_accepted_or_qualified_by_buyer",
    "subscription": "successful_billing_event",
    "monthly_fee": "successful_billing_event",
    "service_fee": "invoice_paid",
    "proposal_service": "invoice_paid",
    "audit_fee": "invoice_paid",
    "setup_fee": "invoice_paid",
    "marketplace_fee": "completed_transaction_minus_refunds",
    "brokerage_fee": "completed_transaction_minus_refunds",
    "referral": "commission_confirmed_by_network",
    "usage_fee": "metered_usage_billed",
    "data_license": "licensed_delivery_paid",
    "savings_share": "contractually_verified_savings_event",
    "b2b_fee": "lead_accepted_or_qualified_by_buyer",
    "professional_referral": "permitted_referral_fee_confirmed",
}
LANE_RULES = [
    (("affiliate", "partner", "commission"), "parts_arbitrage", "affiliate_offers"),
    (("rfp", "procurement", "government-contract", "grant"), "rfp_matcher", "grants_contracts"),
    (("settlement", "unclaimed", "claim"), "warranty_recall", "settlements"),
    (("real-estate", "foreclosure", "property", "home-buyer"), "business_acquisition", "property_opportunities"),
    (("coupon", "deal", "price-drop", "clearance"), "price_drops", "price_drops"),
    (("vehicle", "auto", "car"), "auto_opportunities", "auto_opportunities"),
    (("equipment", "parts", "inventory"), "equipment_arbitrage", "equipment_supply"),
    (("insurance",), "insurance_leads", "insurance_opportunities"),
    (("tax", "incentive"), "tax_incentives", "grants_contracts"),
    (("rebate", "energy"), "energy_rebates", "grants_contracts"),
    (("bill", "utility", "telecom", "savings"), "bill_audit", "price_drops"),
    (("invoice", "receivable", "ar-recovery"), "ar_recovery", "grants_contracts"),
    (("freelance", "fiverr", "gig", "service", "agency"), "freelance_bid_intel", "professional_services"),
    (("job", "career", "resume", "application"), "freelance_bid_intel", "jobs_gigs"),
    (("creator", "sponsor", "stream", "video", "content"), "creator_sponsorship", "creator_marketplaces"),
    (("digital-product", "ebook", "course", "template"), "digital_products", "digital_products"),
    (("saas",), "micro_saas", "software_partners"),
    (("api", "developer-platform"), "api_marketplace", "software_partners"),
    (("automation", "workflow", "software"), "enterprise_automation", "software_partners"),
    (("data", "dataset", "analytics"), "data_quality", "licensed_data"),
    (("business", "startup", "acquisition"), "business_acquisition", "business_marketplaces"),
]

def revenue_route(bot: dict[str, Any], registry: dict[str, Any], lane_index: dict[str, dict[str, Any]],
                  source_categories: dict[str, Any]) -> dict[str, Any] | None:
    text = " ".join(str(bot.get(k, "")) for k in ("slug", "name", "category", "division")).casefold()
    slug = slug_norm(bot.get("slug", ""))
    registered = []
    for row in registry.get("bots", []):
        path_slug = slug_norm(str(row.get("path", "")).split("/")[-1])
        if slug in {path_slug, path_slug.removesuffix("-bot")} or path_slug in {slug, slug + "-bot"}:
            registered.append(row)
    new_registry = [row for row in registry.get("new_money_os_bots", [])
                    if slug_norm(row.get("name", "")) == slug]
    keyword_hit = any(term in text for term in REVENUE_TERMS)
    if not registered and not new_registry and not keyword_hit:
        return None

    registered_lane = registered[0].get("lane") if registered else None
    lane_id = registered_lane if registered_lane in lane_index else None
    registry_source_group = None
    if registered_lane and registered_lane in REGISTRY_LANE_MAP:
        lane_id, registry_source_group = REGISTRY_LANE_MAP[registered_lane]
    if lane_id not in lane_index:
        for terms, candidate, _source in LANE_RULES:
            if any(term in text for term in terms):
                lane_id = candidate
                break
    if lane_id not in lane_index:
        lane_id = "local_service_leads"
    lane = lane_index.get(lane_id, {})
    source_group = next((group for terms, _candidate, group in LANE_RULES
                         if any(term in text for term in terms)), registry_source_group or "jobs_gigs")
    approved_sources = source_categories.get("categories", {}).get(source_group, [])
    if not approved_sources:
        approved_sources = ["official_job_or_marketplace_apis"]
    monetization = lane.get("monetization", ["subscription"])
    return {
        "candidate": True,
        "classification": "registered_money_os_bot" if registered or new_registry else "keyword_candidate_requires_review",
        "money_os_registration": registered[0] if registered else (new_registry[0] if new_registry else None),
        "revenue_lane": lane_id,
        "value_hypothesis": lane.get("value", "qualified opportunity or service outcome"),
        "monetization_options": monetization,
        "verified_revenue_event_types": sorted({REVENUE_EVENT_MAP.get(option, "verified_contractual_payment_event") for option in monetization}),
        "approved_source_categories": approved_sources,
        "source_policy": "Use only authorized official feeds, licensed APIs, user-supplied data or explicitly approved connectors.",
        "workflow": [
            "discover opportunity from an approved source",
            "verify source freshness, terms, eligibility and provenance",
            "score fit, expected value, cost, risk and confidence",
            "prepare a distinct offer and fulfillment plan",
            "simulate unit economics and downside before any external action",
            "request the required owner approval for outreach, contract, spend or payment",
            "execute only through approved runtime connectors and bounded permissions",
            "record the verified conversion, billing, accepted lead or paid invoice event",
            "send outcomes and failure evidence to Buddy for reviewed learning",
        ],
        "revenue_event_required": True,
        "forecast_is_not_revenue": True,
        "live_status": "plan_only",
        "live_actions_allowed": False,
        "owner_live_enable_required": True,
    }

def build() -> dict[str, Any]:
    manifests = json.loads(MANIFESTS.read_text(encoding="utf-8"))
    if manifests.get("summary", {}).get("bots") != len(manifests.get("bots", [])):
        raise ValueError("Bot manifest summary count does not match its profile list")
    domains = domain_names(DOMAIN_SOURCE.read_text(encoding="utf-8"))
    domain_by_key = {norm(x): x for x in domains}
    master = json.loads(MASTERBOTS.read_text(encoding="utf-8"))
    if master.get("canonical_count") != 65 or len(master.get("divisions", [])) != 65:
        raise ValueError("Expected the 65-entry MasterBot registry")
    crosswalk = json.loads(CROSSWALK.read_text(encoding="utf-8"))
    master_by_domain = {norm(row["domain_name"]): row.get("masterbot_id")
                        for row in crosswalk.get("domains", [])}
    if len(crosswalk.get("domains", [])) != 45:
        raise ValueError("Expected 45 domain crosswalk rows")
    charters = json.loads(CHARTERS.read_text(encoding="utf-8"))
    portfolio_by_name = {row["portfolio"]: row for row in charters.get("portfolios", [])}
    if len(portfolio_by_name) != 10:
        raise ValueError("Expected ten specialist portfolio charters")
    source_bots = load_source_bots()
    registry = json.loads(MONEY_REGISTRY.read_text(encoding="utf-8"))
    lanes = load_lane_index(json.loads(REVENUE_LANES.read_text(encoding="utf-8")))
    sources = json.loads(OPPORTUNITY_SOURCES.read_text(encoding="utf-8"))
    monetization = json.loads(MONETIZATION.read_text(encoding="utf-8"))
    shared_ids = list(range(46, 66))
    records = []
    division_counts = Counter()
    status_counts = Counter()
    revenue_lanes_count = Counter()
    duplicate_groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    seen_slugs: set[str] = set()

    for bot in sorted(manifests["bots"], key=lambda x: x.get("slug", "")):
        slug = str(bot.get("slug", "")).strip()
        if not slug:
            raise ValueError("Manifest contains a bot without a slug")
        source_rows = source_bots.get(slug, [])
        source = source_rows[0] if source_rows else {}
        source_division = str(source.get("_source_division") or bot.get("division") or "").strip()
        source_portfolio = source_division if source_division in portfolio_by_name else None
        charter = portfolio_by_name.get(source_portfolio) if source_portfolio else None
        if charter:
            owner = charter["owner"]
            specialist = next((item for item in charter["bots"] if item[0] == slug), None)
        elif norm(bot.get("division", "")) in domain_by_key:
            owner = domain_by_key[norm(bot.get("division", ""))]
            specialist = None
        else:
            owner = "DreamDiscovery"
            specialist = None

        masterbot_id = master_by_domain.get(norm(owner)) if owner != "DreamDiscovery" else 62
        route_status = "mapped_to_canonical_domain" if owner != "DreamDiscovery" and masterbot_id else "discovery_review_required"
        flags = list(bot.get("flags", []))
        if len(source_rows) > 1 or "duplicate_profile" in flags or slug in seen_slugs:
            duplicate_status = "duplicate_or_conflicting_profile_review"
        else:
            duplicate_status = "unique_profile_candidate"
        seen_slugs.add(slug)

        signature_parts = [str(source.get("category") or bot.get("category") or "")]
        signature_parts.extend(str(x) for x in (source.get("capabilities") or []))
        signature = "|".join(sorted(norm(x) for x in signature_parts if x))
        duplicate_groups[(norm(owner), signature)].append(slug)

        revenue = revenue_route(bot, registry, lanes, sources)
        if revenue:
            revenue_lanes_count[revenue["revenue_lane"]] += 1
        capabilities = specialist[2] if specialist else [str(x) for x in source.get("capabilities", [])]
        if not capabilities:
            capabilities = [f"needs_capability_discovery:{bot.get('category') or 'unclassified'}"]

        record = {
            "slug": slug,
            "name": bot.get("name") or slug,
            "source_division": source_division or bot.get("division"),
            "canonical_owner_division": owner,
            "supplemental_portfolio": source_portfolio,
            "specialist_capability_domain": charter["unique_domain"] if charter else None,
            "specialist_mission": charter["mission"] if charter else None,
            "specialist_bot_scope": {
                "purpose": specialist[1],
                "capabilities_to_implement_and_test": specialist[2],
                "approved_source_types": specialist[3],
                "monetization_options": specialist[4],
                "verified_revenue_event": specialist[5],
            } if specialist else None,
            "capabilities": capabilities,
            "source_paths": bot.get("sources", []),
            "declared_integrations": bot.get("api", []),
            "engine": bot.get("engine"),
            "execution_ceiling": bot.get("ceiling"),
            "existing_run_policy": bot.get("run"),
            "profile_flags": flags,
            "duplicate_review_status": duplicate_status,
            "division_route": {
                "status": route_status,
                "primary_masterbot_id": masterbot_id,
                "primary_masterbot_name": master["divisions"][masterbot_id - 1]["name"] if masterbot_id else None,
                "shared_platform_masterbot_ids": shared_ids,
                "unresolved_owner_goes_to": "DreamDiscovery" if route_status != "mapped_to_canonical_domain" else None,
                "owner_approval_required_for_remap": True,
            },
            "buddy_execution": {
                "orchestrator": "Buddy",
                "queue": "dependency_aware_governed_task_queue",
                "learning_route": "evidence_backed_reviewed_learning",
                "benchmark_route": "bot_capability_and_division_holdout_benchmarks",
                "progress_events": ["queued","started","blocked","completed","failed","verified","promoted"],
                "failure_recovery": "capture structured failure fingerprint, retrieve verified lessons, create bounded repair task, rerun original and regression tests",
            },
            "commercial_plan": revenue or {
                "candidate": False,
                "classification": "internal_capability_or_no_verified_commercial_signal",
                "value_hypothesis": f"Deliver a measurable internal or customer outcome for {owner}",
                "route": "Buddy routes this bot to its canonical division and dependent workflows; no direct revenue claim until a distinct buyer, offer and fulfillment route are validated.",
                "live_status": "not_applicable_or_unverified",
                "live_actions_allowed": False,
            },
            "execution_plan_status": "plan_only_not_runtime_proof",
            "learning_status": "curriculum_and_evidence_required_not_trained_by_generation",
        }
        records.append(record)
        division_counts[owner] += 1
        status_counts[route_status] += 1

    duplicate_sets = [
        {"canonical_owner_division": owner, "capability_signature": signature,
         "bot_slugs": sorted(slugs), "requires_review": True}
        for (owner, signature), slugs in sorted(duplicate_groups.items())
        if len(slugs) > 1
    ]
    revenue_count = sum(1 for row in records if row["commercial_plan"].get("candidate"))
    supplemental_count = sum(1 for row in records if row["supplemental_portfolio"])
    app_bot_count = sum(1 for row in records if any(str(x).startswith("App_bots/") for x in row["source_paths"]))
    payload = {
        "schema": "dreamco.buddy_fleet_execution_map.v1",
        "status": "full_catalog_planned_runtime_evidence_pending",
        "counts": {
            "manifest_bot_profiles": len(records),
            "canonical_business_divisions": 45,
            "supplemental_specialist_portfolios": len(portfolio_by_name),
            "bots_in_supplemental_portfolios": supplemental_count,
            "profiles_with_app_bots_source": app_bot_count,
            "profiles_without_app_bots_source": len(records) - app_bot_count,
            "revenue_candidates_with_plans": revenue_count,
            "internal_or_unclassified_profiles": len(records) - revenue_count,
            "mapped_to_canonical_domain": status_counts["mapped_to_canonical_domain"],
            "discovery_review_required": status_counts["discovery_review_required"],
            "duplicate_capability_groups_for_review": len(duplicate_sets),
            "shared_platform_masterbots": len(shared_ids),
            "live_enabled_bots": 0,
        },
        "division_profile_counts": dict(sorted(division_counts.items())),
        "revenue_lane_candidate_counts": dict(sorted(revenue_lanes_count.items())),
        "portfolio_charters": [
            {"portfolio": row["portfolio"], "canonical_owner": row["owner"],
             "unique_domain": row["unique_domain"], "bot_count": len(row["bots"]),
             "collaborators": row["collaborators"]}
            for row in charters["portfolios"]
        ],
        "monetization_truth_policy": monetization["default_rules"],
        "global_rules": [
            "All manifest profiles receive a Buddy route, a primary canonical owner or DreamDiscovery review route, and a plan record.",
            "Only evidence-backed, permissioned, owner-approved execution may leave plan_only.",
            "Declared API names are integration targets, not proof that credentials or live connections exist.",
            "Duplicate capability groups are flagged for review; do not launch competing copies of the same offer.",
            "Forecasts, generated plans and simulated sales are never recorded as realized revenue.",
            "All external writes, outreach, ad spend, contracts, payments, refunds and payouts remain governed by explicit permissions.",
            "Every successful execution must write verifiable outcome evidence and a learning/benchmark event.",
        ],
        "bots": records,
        "duplicate_capability_groups": duplicate_sets,
        "truth_boundary": "This is a deterministic plan and routing map for the complete generated bot manifest. It does not prove runtime availability, integrations, customer demand, revenue, learning or production readiness.",
    }
    return payload

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("Buddy fleet execution map is stale; regenerate and review it.")
        print(json.dumps(payload["counts"], indent=2, sort_keys=True))
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(rendered, encoding="utf-8")
    print(json.dumps(payload["counts"], indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
