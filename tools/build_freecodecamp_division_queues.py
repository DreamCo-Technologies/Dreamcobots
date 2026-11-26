"""Build deterministic, rights-gated freeCodeCamp study queues for all 55 domain divisions.

This creates curriculum assignments from public metadata only. It does not watch
videos, ingest transcripts, train weights, or claim learning/mastery.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "buddy/bootcamp/sources/freecodecamp/catalog.json"
CROSSWALK = ROOT / "config/generated/masterbot-55-domain-crosswalk.json"
OUTPUT = ROOT / "config/generated/freecodecamp-division-learning-queues.json"
FOUNDATION = {
    "computer_science_and_fundamentals",
    "python_and_automation",
    "databases_and_sql",
    "software_architecture_and_testing",
    "cybersecurity_and_privacy",
    "generative_ai_and_llms",
    "ai_agents_and_mcp",
    "cloud_devops_and_ci_cd",
}
ALIASES = {
    "finance": {"databases_and_sql", "data_science_and_visualization", "mathematics_and_statistics", "generative_ai_and_llms"},
    "real estate": {"databases_and_sql", "data_science_and_visualization", "software_architecture_and_testing", "generative_ai_and_llms"},
    "sales": {"generative_ai_and_llms", "data_science_and_visualization", "backend_and_apis"},
    "ai infra": {"generative_ai_and_llms", "ai_agents_and_mcp", "cloud_devops_and_ci_cd", "databases_and_sql", "python_and_automation"},
    "data": {"databases_and_sql", "data_science_and_visualization", "machine_learning_and_deep_learning", "python_and_automation"},
    "automation": {"python_and_automation", "ai_agents_and_mcp", "backend_and_apis", "cloud_devops_and_ci_cd"},
    "cyber": {"cybersecurity_and_privacy", "linux_networking_and_it", "c_cpp_and_systems"},
    "code": {"computer_science_and_fundamentals", "javascript_and_typescript", "python_and_automation", "c_cpp_and_systems", "software_architecture_and_testing"},
    "education": {"computer_science_and_fundamentals", "python_and_automation", "generative_ai_and_llms"},
    "research": {"computer_science_and_fundamentals", "data_science_and_visualization", "machine_learning_and_deep_learning", "mathematics_and_statistics"},
    "science": {"data_science_and_visualization", "machine_learning_and_deep_learning", "mathematics_and_statistics", "python_and_automation"},
    "game": {"game_development", "c_cpp_and_systems", "mathematics_and_statistics"},
    "content": {"html_css_and_accessibility", "javascript_and_typescript", "frontend_and_ui_frameworks", "data_science_and_visualization"},
    "market": {"data_science_and_visualization", "databases_and_sql", "generative_ai_and_llms"},
    "legal": {"cybersecurity_and_privacy", "databases_and_sql", "generative_ai_and_llms"},
    "health": {"data_science_and_visualization", "cybersecurity_and_privacy", "databases_and_sql", "generative_ai_and_llms"},
    "transport": {"data_science_and_visualization", "backend_and_apis", "cloud_devops_and_ci_cd"},
    "construction": {"data_science_and_visualization", "python_and_automation", "software_architecture_and_testing"},
    "agriculture": {"data_science_and_visualization", "python_and_automation", "machine_learning_and_deep_learning"},
    "crypto": {"databases_and_sql", "cybersecurity_and_privacy", "mathematics_and_statistics", "backend_and_apis"},
    "payments": {"databases_and_sql", "cybersecurity_and_privacy", "backend_and_apis"},
    "admin": {"python_and_automation", "databases_and_sql", "cloud_devops_and_ci_cd"},
    "agents": {"ai_agents_and_mcp", "generative_ai_and_llms", "python_and_automation"},
    "benchmark": {"machine_learning_and_deep_learning", "data_science_and_visualization", "mathematics_and_statistics", "software_architecture_and_testing"},
    "knowledge": {"generative_ai_and_llms", "databases_and_sql", "python_and_automation"},
    "robot": {"c_cpp_and_systems", "python_and_automation", "machine_learning_and_deep_learning"},
    "mobile": {"mobile_and_cross_platform", "javascript_and_typescript", "software_architecture_and_testing"},
    "web": {"html_css_and_accessibility", "javascript_and_typescript", "frontend_and_ui_frameworks", "backend_and_apis"},
}
# Curated FreeCodeCamp taxonomy routing for every canonical domain division.
# This maps learning subjects, not bot ownership, production permissions, or mastery.
# The 55-domain / 65-MasterBot ownership crosswalk remains separately review-gated.
DOMAIN_CATEGORY_MAP: dict[str, set[str]] = {
    "commandcore": {"computer_science_and_fundamentals", "software_architecture_and_testing", "python_and_automation", "ai_agents_and_mcp", "cloud_devops_and_ci_cd"},
    "dreamaiinfra": {"machine_learning_and_deep_learning", "generative_ai_and_llms", "ai_agents_and_mcp", "python_and_automation", "cloud_devops_and_ci_cd"},
    "dreamadmin": {"python_and_automation", "databases_and_sql", "cloud_devops_and_ci_cd", "software_architecture_and_testing"},
    "dreamagents": {"ai_agents_and_mcp", "generative_ai_and_llms", "backend_and_apis", "python_and_automation", "software_architecture_and_testing"},
    "dreamagriculture": {"data_science_and_visualization", "machine_learning_and_deep_learning", "python_and_automation", "mathematics_and_statistics"},
    "dreamarts": {"html_css_and_accessibility", "frontend_and_ui_frameworks", "javascript_and_typescript", "game_development"},
    "dreamautomation": {"python_and_automation", "ai_agents_and_mcp", "backend_and_apis", "cloud_devops_and_ci_cd"},
    "dreambizlaunch": {"career_and_interview_skills", "data_science_and_visualization", "backend_and_apis", "software_architecture_and_testing"},
    "dreamcodelab": {"computer_science_and_fundamentals", "html_css_and_accessibility", "javascript_and_typescript", "python_and_automation", "backend_and_apis", "software_architecture_and_testing"},
    "dreamconstruction": {"data_science_and_visualization", "python_and_automation", "software_architecture_and_testing", "cloud_devops_and_ci_cd"},
    "dreamcontent": {"html_css_and_accessibility", "javascript_and_typescript", "frontend_and_ui_frameworks", "data_science_and_visualization"},
    "dreamcrypto": {"databases_and_sql", "cybersecurity_and_privacy", "mathematics_and_statistics", "backend_and_apis"},
    "dreamcustintel": {"data_science_and_visualization", "databases_and_sql", "machine_learning_and_deep_learning", "python_and_automation"},
    "dreamcyber": {"cybersecurity_and_privacy", "linux_networking_and_it", "c_cpp_and_systems", "backend_and_apis"},
    "dreamdata": {"databases_and_sql", "data_science_and_visualization", "machine_learning_and_deep_learning", "python_and_automation", "mathematics_and_statistics"},
    "dreamdecision": {"mathematics_and_statistics", "data_science_and_visualization", "machine_learning_and_deep_learning", "software_architecture_and_testing"},
    "dreameducation": {"computer_science_and_fundamentals", "python_and_automation", "frontend_and_ui_frameworks", "generative_ai_and_llms"},
    "dreamempire": {"computer_science_and_fundamentals", "data_science_and_visualization", "ai_agents_and_mcp", "software_architecture_and_testing"},
    "dreamentfinance": {"databases_and_sql", "data_science_and_visualization", "mathematics_and_statistics", "python_and_automation"},
    "dreamfinance": {"databases_and_sql", "data_science_and_visualization", "mathematics_and_statistics", "python_and_automation"},
    "dreamflow": {"python_and_automation", "backend_and_apis", "cloud_devops_and_ci_cd", "ai_agents_and_mcp"},
    "dreamfood": {"data_science_and_visualization", "databases_and_sql", "python_and_automation", "backend_and_apis"},
    "dreamglobal": {"software_architecture_and_testing", "databases_and_sql", "cloud_devops_and_ci_cd", "data_science_and_visualization"},
    "dreamhealth": {"data_science_and_visualization", "databases_and_sql", "cybersecurity_and_privacy", "machine_learning_and_deep_learning"},
    "dreaminfluence": {"html_css_and_accessibility", "frontend_and_ui_frameworks", "javascript_and_typescript", "data_science_and_visualization"},
    "dreamlegal": {"cybersecurity_and_privacy", "databases_and_sql", "generative_ai_and_llms", "software_architecture_and_testing"},
    "dreamloans": {"databases_and_sql", "data_science_and_visualization", "mathematics_and_statistics", "backend_and_apis"},
    "dreammaintenance": {"python_and_automation", "cloud_devops_and_ci_cd", "c_cpp_and_systems", "data_science_and_visualization"},
    "dreammarket": {"data_science_and_visualization", "databases_and_sql", "frontend_and_ui_frameworks", "backend_and_apis"},
    "dreammilitary": {"cybersecurity_and_privacy", "linux_networking_and_it", "c_cpp_and_systems", "mathematics_and_statistics"},
    "dreamops": {"python_and_automation", "cloud_devops_and_ci_cd", "databases_and_sql", "software_architecture_and_testing"},
    "dreampayments": {"backend_and_apis", "databases_and_sql", "cybersecurity_and_privacy", "software_architecture_and_testing"},
    "dreampersonalcare": {"mobile_and_cross_platform", "frontend_and_ui_frameworks", "cybersecurity_and_privacy", "data_science_and_visualization"},
    "dreamplanetary": {"data_science_and_visualization", "machine_learning_and_deep_learning", "mathematics_and_statistics", "python_and_automation"},
    "dreamproservices": {"career_and_interview_skills", "backend_and_apis", "python_and_automation", "software_architecture_and_testing"},
    "dreamproduction": {"python_and_automation", "cloud_devops_and_ci_cd", "c_cpp_and_systems", "software_architecture_and_testing"},
    "dreamprotection": {"cybersecurity_and_privacy", "linux_networking_and_it", "c_cpp_and_systems", "backend_and_apis"},
    "dreamrealestate": {"databases_and_sql", "data_science_and_visualization", "backend_and_apis", "python_and_automation"},
    "dreamretail": {"data_science_and_visualization", "databases_and_sql", "frontend_and_ui_frameworks", "mobile_and_cross_platform"},
    "dreamsalespro": {"data_science_and_visualization", "career_and_interview_skills", "backend_and_apis", "python_and_automation"},
    "dreamscience": {"data_science_and_visualization", "machine_learning_and_deep_learning", "mathematics_and_statistics", "python_and_automation"},
    "dreamsocial": {"frontend_and_ui_frameworks", "javascript_and_typescript", "databases_and_sql", "cybersecurity_and_privacy"},
    "dreamtrade": {"databases_and_sql", "mathematics_and_statistics", "backend_and_apis", "cybersecurity_and_privacy"},
    "dreamtransport": {"data_science_and_visualization", "backend_and_apis", "cloud_devops_and_ci_cd", "python_and_automation"},
    "gametitan": {"game_development", "c_cpp_and_systems", "mathematics_and_statistics", "software_architecture_and_testing"},
    "dreamaffiliate": {"data_science_and_visualization", "html_css_and_accessibility", "javascript_and_typescript", "backend_and_apis"},
    "dreamagency": {"career_and_interview_skills", "data_science_and_visualization", "frontend_and_ui_frameworks", "backend_and_apis"},
    "dreamfoundry": {"computer_science_and_fundamentals", "software_architecture_and_testing", "backend_and_apis", "cloud_devops_and_ci_cd"},
    "dreamfranchise": {"career_and_interview_skills", "data_science_and_visualization", "backend_and_apis", "python_and_automation"},
    "dreamintegrations": {"backend_and_apis", "ai_agents_and_mcp", "cloud_devops_and_ci_cd", "cybersecurity_and_privacy"},
    "dreamlicensing": {"cybersecurity_and_privacy", "databases_and_sql", "software_architecture_and_testing", "career_and_interview_skills"},
    "dreamrobotics": {"c_cpp_and_systems", "python_and_automation", "machine_learning_and_deep_learning", "mathematics_and_statistics"},
    "dreamsaas": {"frontend_and_ui_frameworks", "backend_and_apis", "databases_and_sql", "cloud_devops_and_ci_cd", "software_architecture_and_testing"},
    "dreamstreaming": {"backend_and_apis", "cloud_devops_and_ci_cd", "javascript_and_typescript", "linux_networking_and_it"},
    "dreamtravel": {"data_science_and_visualization", "backend_and_apis", "mobile_and_cross_platform", "cloud_devops_and_ci_cd"},
}

def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")

def _division_categories(name: str, subject_terms: list[str], known: set[str], domain_id: str | None = None) -> tuple[set[str], bool]:
    # Explicit canonical profiles win over name heuristics. This is curriculum
    # categorization only; MasterBot ownership approval remains separate.
    explicit = DOMAIN_CATEGORY_MAP.get(domain_id or "")
    if explicit is not None:
        selected = explicit & known
        return selected, bool(selected)
    raw = " ".join([name, *subject_terms])
    raw = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", raw)
    raw = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", raw)
    haystack = raw.casefold().replace("dream", " ")
    selected = set()
    for alias, categories in ALIASES.items():
        if alias in haystack:
            selected.update(categories & known)
    # Only exact taxonomy IDs/labels/keywords can add a category; never infer
    # an unrelated specialty from a generic word like "pro" or "global".
    for category_id in known:
        if category_id.replace("_", " ") in haystack:
            selected.add(category_id)
    return selected, bool(selected)

def build_queues(catalog: dict[str, Any], crosswalk: dict[str, Any], limit: int = 30, *, allow_partial: bool = False) -> dict[str, Any]:
    if catalog.get("schema") != "dreamco.freecodecamp_catalog.v1":
        raise ValueError("unsupported freeCodeCamp catalog schema")
    videos = catalog.get("videos")
    categories = catalog.get("categories")
    domains = crosswalk.get("domains")
    if not isinstance(videos, list) or not videos:
        raise ValueError("non-empty freeCodeCamp catalog required")
    inventory = catalog.get("inventory") or {}
    complete_inventory = (
        catalog.get("inventory_status") == "complete"
        and inventory.get("complete") is True
        and inventory.get("expected_entry_count") == len(videos)
        and inventory.get("observed_entry_count") == len(videos)
        and inventory.get("null_entry_count") == 0
        and inventory.get("duplicate_video_id_count") == 0
    )
    provisional_inventory = (
        allow_partial
        and catalog.get("inventory_status") == "partial"
        and inventory.get("complete") is False
        and inventory.get("observed_entry_count") == len(videos)
        and inventory.get("null_entry_count") == 0
        and inventory.get("duplicate_video_id_count") == 0
    )
    if not complete_inventory and not provisional_inventory:
        raise ValueError("verified complete freeCodeCamp inventory required, or pass allow_partial=True for a clearly provisional queue with verified observed-row integrity")
    if not isinstance(domains, list) or len(domains) != 55:
        raise ValueError("canonical 55-domain crosswalk required")
    domain_ids = [row.get("domain_id") for row in domains]
    if len(set(domain_ids)) != 55 or any(not isinstance(x, str) or not x for x in domain_ids):
        raise ValueError("55 domain profiles must have unique non-empty IDs")
    mapped = [row for row in domains if row.get("mapping_status") == "proposed_exact_name_match"]
    unassigned = [row for row in domains if row.get("mapping_status") == "unresolved"]
    if len(mapped) != 45 or len(unassigned) != 10:
        raise ValueError("crosswalk must preserve 45 core domains and 10 supplemental profiles")
    known = {row["id"] for row in categories}
    rows = []
    for domain in sorted(domains, key=lambda row: row["domain_id"]):
        domain_id = domain["domain_id"]
        name = domain["domain_name"]
        subject_terms = [name, name.replace("Dream", "")]
        targeted, has_mapping = _division_categories(name, subject_terms, known, domain_id)
        required = FOUNDATION | targeted
        scored = []
        for video in videos:
            tags = set(video.get("categories") or [])
            overlap = tags & required
            if not overlap:
                continue
            # Foundation lessons are useful to every division. Subject matches
            # rank above foundation-only material, with stable tie-breaking.
            specialty = overlap & targeted
            score = (len(specialty) * 10) + len(overlap)
            scored.append((score, video))
        scored.sort(key=lambda item: (-item[0], item[1].get("upload_date") or "", item[1]["video_id"]))
        selected = scored[:limit]
        rows.append({
            "domain_id": domain_id,
            "domain_name": name,
            "masterbot_id": domain.get("masterbot_id"),
            "mapping_status": domain.get("mapping_status"),
            "owner_review_required": domain.get("review_required", True),
            "queue_status": "subject_routed" if has_mapping else "foundation_only_owner_mapping_pending",
            "target_categories": sorted(targeted),
            "shared_foundation_categories": sorted(FOUNDATION & known),
            "items": [{
                "video_id": video["video_id"],
                "title": video["title"],
                "url": video["url"],
                "categories": sorted(set(video.get("categories") or [])),
                "priority_score": score,
                "assignment_status": "queued_not_studied",
                "rights_status": "review_required",
                "media_download_allowed": False,
                "transcript_ingestion_allowed": False,
                "training_eligible": False,
                "evidence_required": ["original_lesson_or_notes", "sandbox_exercise", "targeted_benchmark", "holdout", "regression"],
            } for score, video in selected],
            "queue_count": len(selected),
            "truth_boundary": "Queued metadata is not evidence that the division watched, learned, trained on, or mastered this lesson.",
        })
    return {
        "schema": "dreamco.freecodecamp_division_learning_queues.v1",
        "source_catalog_generated_at": catalog.get("generated_at"),
        "source_inventory_status": catalog.get("inventory_status"),
        "source_inventory": inventory,
        "queue_mode": "complete_verified_inventory" if complete_inventory else "provisional_partial_inventory",
        "coverage_warning": None if complete_inventory else "Only observed catalog entries are queued. The full historical freeCodeCamp video archive is not verified; do not claim complete source coverage.",
        "domain_count": len(rows),
        "catalog_video_count": len(videos),
        "queue_limit_per_domain": limit,
        "rights_policy": catalog["rights_policy"],
        "domains": rows,
        "truth_boundary": "Queues prioritize study candidates only. Rights review and independent learning evidence are required before training or mastery claims.",
    }

def validate(payload: dict[str, Any]) -> None:
    rows = payload.get("domains", [])
    if payload.get("schema") != "dreamco.freecodecamp_division_learning_queues.v1" or len(rows) != 55:
        raise ValueError("exactly 55 domain queues are required")
    source_inventory = payload.get("source_inventory") or {}
    complete_inventory = (
        payload.get("queue_mode") == "complete_verified_inventory"
        and payload.get("source_inventory_status") == "complete"
        and source_inventory.get("complete") is True
        and source_inventory.get("expected_entry_count") == payload.get("catalog_video_count")
        and source_inventory.get("observed_entry_count") == payload.get("catalog_video_count")
    )
    provisional_inventory = (
        payload.get("queue_mode") == "provisional_partial_inventory"
        and payload.get("source_inventory_status") == "partial"
        and source_inventory.get("complete") is False
        and source_inventory.get("observed_entry_count") == payload.get("catalog_video_count")
        and source_inventory.get("null_entry_count") == 0
        and source_inventory.get("duplicate_video_id_count") == 0
        and bool(payload.get("coverage_warning"))
    )
    if not complete_inventory and not provisional_inventory:
        raise ValueError("domain queues must retain complete inventory evidence or an explicit provisional partial-inventory warning")
    ids = [row["domain_id"] for row in rows]
    if len(set(ids)) != 55:
        raise ValueError("domain IDs must be unique")
    if sum(row.get("mapping_status") == "proposed_exact_name_match" for row in rows) != 45:
        raise ValueError("exactly 45 core domain proposals must be retained")
    if sum(row.get("mapping_status") == "unresolved" for row in rows) != 10:
        raise ValueError("exactly 10 supplemental domains must remain unresolved until owner review")
    for row in rows:
        if row["queue_count"] != len(row["items"]):
            raise ValueError("queue_count does not match item count")
        for item in row["items"]:
            if item["assignment_status"] != "queued_not_studied":
                raise ValueError("queue generation cannot claim study completion")
            if item["training_eligible"] or item["media_download_allowed"] or item["transcript_ingestion_allowed"]:
                raise ValueError("metadata discovery cannot authorize training or media ingestion")
            if item["rights_status"] != "review_required":
                raise ValueError("every source item must retain rights review")

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--allow-partial", action="store_true", help="Build a provisional queue from observed entries only; never claim full archive coverage.")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        raise SystemExit("--limit must be between 1 and 100")
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    crosswalk = json.loads(CROSSWALK.read_text(encoding="utf-8"))
    payload = build_queues(catalog, crosswalk, args.limit, allow_partial=args.allow_partial)
    validate(payload)
    if args.allow_partial and args.out == OUTPUT:
        args.out = OUTPUT.with_name("freecodecamp-provisional-division-learning-queues.json")
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != rendered:
            raise SystemExit("domain queues are stale; regenerate them")
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(json.dumps({"ok": True, "queue_mode": payload["queue_mode"], "domains": 55, "catalog_videos": len(catalog["videos"]),
                      "queued_items": sum(row["queue_count"] for row in payload["domains"]),
                      "subject_routed": sum(row["queue_status"] == "subject_routed" for row in payload["domains"]),
                      "foundation_only": sum(row["queue_status"] != "subject_routed" for row in payload["domains"])}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
