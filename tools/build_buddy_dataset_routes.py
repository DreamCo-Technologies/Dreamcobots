#!/usr/bin/env python3
"""Build deterministic, discovery-only dataset routes for all canonical MasterBots."""
from __future__ import annotations
import argparse, json, re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/masterbot-75-registry.json"
CROSSWALK = ROOT / "config/generated/masterbot-55-domain-crosswalk.json"
POLICY = ROOT / "config/buddy-dataset-routing-policy.json"
CATALOG = ROOT / "website/data/free-datasets.json"
OUT = ROOT / "artifacts/buddy-dataset-hub/dataset-routes.json"

ALIASES = {
 "DreamFinance": ["finance", "financial", "accounting", "economics"],
 "DreamRealEstate": ["real estate", "property", "housing", "geospatial"],
 "DreamSalesPro": ["sales", "crm", "customer", "marketing"],
 "DreamAIInfra": ["machine learning", "deep learning", "model", "code", "cloud"],
 "DreamRetail": ["retail", "commerce", "product", "recommendation"],
 "DreamProServices": ["business", "professional", "legal", "document"],
 "DreamData": ["data", "database", "sql", "analytics", "tabular"],
 "DreamGlobal": ["language", "multilingual", "translation"],
 "DreamAutomation": ["automation", "workflow", "tool", "agent"],
 "DreamContent": ["text", "language", "writing", "summarization"],
 "DreamTrade": ["trade", "supply chain", "logistics", "market"],
 "DreamMarket": ["market", "economics", "finance", "commerce"],
 "CommandCore": ["instruction", "reasoning", "tool", "agent"],
 "DreamCyber": ["security", "cyber", "network", "code"],
 "DreamHealth": ["health", "medical", "biology"],
 "DreamEducation": ["education", "question answering", "math", "science"],
 "DreamConstruction": ["engineering", "construction", "geometry", "design"],
 "DreamTransport": ["transport", "mobility", "traffic", "logistics"],
 "DreamFood": ["food", "nutrition", "agriculture"],
 "DreamScience": ["science", "physics", "chemistry", "biology"],
 "DreamAgriculture": ["agriculture", "climate", "environment"],
 "DreamProduction": ["manufacturing", "industrial", "engineering"],
 "DreamCrypto": ["finance", "blockchain", "code"],
 "DreamCodeLab": ["code", "programming", "software", "repository"],
 "DreamResearch": ["research", "science", "reasoning", "question answering"],
 "DreamBenchmark": ["benchmark", "evaluation", "reasoning", "code"],
 "DreamKnowledge": ["knowledge", "question answering", "retrieval", "text"],
 "DreamVision": ["image", "vision", "visual", "video"],
 "DreamVoice": ["audio", "speech", "voice"],
 "DreamProduct": ["product", "design", "recommendation", "customer"],
 "DreamSimulation": ["simulation", "physics", "engineering", "math"],
 "DreamDiscovery": ["research", "science", "discovery", "reasoning"],
 "DreamQuality": ["quality", "benchmark", "evaluation", "classification"],
 "DreamResource": ["resource", "catalog", "data", "search"],
 "DreamFuture": ["forecast", "time series", "reasoning", "science"],
 "DreamAffiliate": ["affiliate", "partner marketing", "commission", "publisher", "creator"],
 "DreamAgency": ["agency", "client service", "retainer", "staffing", "consulting"],
 "DreamFoundry": ["model", "fine tuning", "lora", "retrieval", "evaluation"],
 "DreamFranchise": ["franchise", "royalty", "territory", "disclosure", "business expansion"],
 "DreamIntegrations": ["api", "webhook", "integration", "authentication", "idempotency"],
 "DreamLicensing": ["license", "licensing", "intellectual property", "copyright", "royalty"],
 "DreamRobotics": ["robotics", "robot", "simulation", "actuator", "sensor", "safety"],
 "DreamSaaS": ["saas", "subscription", "churn", "onboarding", "billing"],
 "DreamStreaming": ["streaming", "broadcast", "video", "channel", "audience"],
 "DreamTravel": ["travel", "itinerary", "visa", "flight", "hotel", "trip"]
}

def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()

def build() -> dict:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    crosswalk = json.loads(CROSSWALK.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    divisions = registry.get("divisions", [])
    if registry.get("canonical_count") != 75 or len(divisions) != 75:
        raise ValueError("Expected exactly 75 MasterBots")
    route_by_id = {int(row["masterbot_id"]): row for row in crosswalk.get("masterbots", [])}
    if crosswalk.get("counts", {}).get("domain_divisions") != 55:
        raise ValueError("Expected 55 canonical domain routes")
    ids = [str(x.get("id")) for x in divisions]
    names = [x.get("name") for x in divisions]
    if len(set(ids)) != 75 or len(set(names)) != 75 or any(not x for x in names):
        raise ValueError("MasterBot IDs and names must be unique and non-empty")
    rows = catalog.get("datasets", [])
    if not isinstance(rows, list):
        raise ValueError("Dataset catalog must contain a datasets array")
    categories = sorted({norm(x.get("category", "")) for x in rows if x.get("category")})
    routes = []
    for bot in divisions:
        name = bot["name"]
        tags = ALIASES.get(name, [norm(name).replace("dream", "")])
        matches = []
        for row in rows:
            haystack = norm(" ".join([row.get("name", ""), row.get("category", ""), row.get("note", "")]))
            if any(norm(tag) in haystack for tag in tags):
                matches.append(row)
        route = route_by_id.get(int(bot["id"]), {})
        shared_service = route.get("mapping_status") == "shared_platform_service"
        routes.append({
            "masterbot_id": bot["id"], "masterbot": name,
            "lane_id": f"dataset-lane-{bot['id']:03d}",
            "routing_status": "HEURISTIC_DISCOVERY_ONLY",
            "domain_crosswalk_status": route.get("mapping_status"),
            "primary_domain_id": route.get("primary_domain_id"),
            "primary_domain_name": route.get("primary_domain_name"),
            "shared_platform_service": shared_service,
            "primary_tags": tags,
            "shared_foundation_categories": policy["division_routing"]["shared_foundation_categories"],
            "candidate_count": len(matches),
            "candidates": [{
                "dataset_id": row.get("name"), "source": row.get("href"),
                "listed_license": row.get("license"), "category": row.get("category"),
                "catalog_train_flag": bool(row.get("train")),
                "rights_status": "UNVERIFIED_DATASET_CARD_AND_TERMS_REQUIRED",
                "training_status": "DISCOVERY_ONLY_NOT_TRAINING_APPROVED",
                "evaluation_holdout": False
            } for row in matches[:100]],
            "missing_work": ["verify_dataset_card_and_license", "quality_and_privacy_review",
                "create_versioned_manifest_and_split_hashes", "benchmark_domain_fit"],
            "crosswalk_status": route.get("mapping_status", "missing_crosswalk")
        })
    return {
        "schema": "dreamco.buddy_dataset_routes.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy_version": policy["version"], "masterbot_count": len(routes), "domain_division_count": 55, "shared_platform_masterbot_count": 20, "owner_approved_domain_mappings": crosswalk.get("counts", {}).get("owner_approved_domain_mappings", 0),
        "unique_dataset_candidates": len({c["dataset_id"] for r in routes for c in r["candidates"]}),
        "catalog_dataset_count": len(rows), "catalog_source": "website/data/free-datasets.json",
        "catalog_hosted_here": catalog.get("hosted_here", False),
        "catalog_studied_files": catalog.get("studied_files", False),
        "route_mode": "discovery_only",
        "unknown_problem_fallback": policy["unknown_problem_router"]["sequence"],
        "categories": categories, "routes": routes,
        "truth": "A catalog entry or train flag is not rights verification, dataset inspection, training approval, or proof that any model studied or trained on the dataset.",
        "automatic_weight_updates": False
    }

def matches_existing(payload: dict, existing_text: str) -> bool:
    """Compare generated content while preserving its original generation timestamp.

    ``generated_at`` is intentionally volatile metadata. Comparing a freshly
    generated timestamp makes every --check fail even when every route is
    byte-for-byte equivalent apart from that field.
    """
    try:
        existing = json.loads(existing_text)
    except (TypeError, ValueError):
        return False
    expected = dict(payload)
    expected["generated_at"] = existing.get("generated_at")
    return existing_text == json.dumps(expected, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    encoded = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUT.exists() or not matches_existing(payload, OUT.read_text(encoding="utf-8")):
            raise SystemExit(f"Dataset route artifact is stale: {OUT.relative_to(ROOT)}")
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(encoded, encoding="utf-8")
    print(json.dumps({"ok": True, "masterbots": payload["masterbot_count"],
        "catalog_candidates": payload["unique_dataset_candidates"],
        "mode": payload["route_mode"], "weights_trained": False}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
