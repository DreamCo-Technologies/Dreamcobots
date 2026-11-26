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
APPROVALS = ROOT / "config/review/freecodecamp-supplemental-domain-learning-approval.json"
OUTPUT = ROOT / "config/generated/freecodecamp-division-learning-queues.json"
PROFILE_PATH = ROOT / "config/freecodecamp-division-category-profiles.json"
_PROFILE = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
if _PROFILE.get("schema") != "dreamco.freecodecamp_division_category_profiles.v1":
    raise ValueError("unsupported FreeCodeCamp division category profile schema")
FOUNDATION = set(_PROFILE.get("shared_foundation_categories", []))
DOMAIN_CATEGORY_MAP: dict[str, set[str]] = {
    str(domain_id): set(categories)
    for domain_id, categories in _PROFILE.get("domain_categories", {}).items()
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


def _approved_supplemental_learning_routes(known: set[str], domains: list[dict[str, Any]]) -> dict[str, set[str]]:
    """Load owner-approved learning categories without approving MasterBot ownership."""
    if not APPROVALS.is_file():
        raise ValueError("supplemental learning-route approval manifest is required")
    document = json.loads(APPROVALS.read_text(encoding="utf-8"))
    if document.get("schema") != "dreamco.freecodecamp_supplemental_learning_approval.v1":
        raise ValueError("unsupported supplemental learning-route approval schema")
    if document.get("approval_scope") != "freecodecamp_learning_categories_only":
        raise ValueError("supplemental approval must be limited to learning categories")
    domain_by_id = {str(row.get("domain_id")): row for row in domains}
    approved: dict[str, set[str]] = {}
    for entry in document.get("approved_routes", []):
        domain_id = str(entry.get("domain_id", ""))
        if not domain_id or domain_id in approved:
            raise ValueError("supplemental learning approval IDs must be unique and non-empty")
        domain = domain_by_id.get(domain_id)
        if domain is None:
            # Small synthetic fixtures intentionally omit the canonical supplemental rows.
            continue
        if domain.get("mapping_status") != "unresolved" or domain.get("masterbot_id") is not None:
            raise ValueError(f"learning-only approval cannot alter MasterBot ownership: {domain_id}")
        if entry.get("owner_approved") is not True or entry.get("approved_by") != "repository_owner":
            raise ValueError(f"explicit repository-owner approval is required: {domain_id}")
        if not str(entry.get("approval_reference", "")).strip():
            raise ValueError(f"approval reference is required: {domain_id}")
        categories = set(entry.get("categories", []))
        canonical = DOMAIN_CATEGORY_MAP.get(domain_id, set()) & known
        if not canonical or categories != canonical:
            raise ValueError(f"approved learning categories must match the curated domain profile: {domain_id}")
        approved[domain_id] = categories
    canonical_domain_ids = set(DOMAIN_CATEGORY_MAP)
    if set(domain_by_id) == canonical_domain_ids:
        unresolved_ids = {key for key, row in domain_by_id.items() if row.get("mapping_status") == "unresolved"}
        if set(approved) != unresolved_ids:
            raise ValueError("every unresolved canonical domain needs an explicit learning-only approval")
    return approved

def build_queues(catalog: dict[str, Any], crosswalk: dict[str, Any], limit: int | None = None, *, allow_partial: bool = False) -> dict[str, Any]:
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
    approved_supplemental = _approved_supplemental_learning_routes(known, domains)
    rows = []
    for domain in sorted(domains, key=lambda row: row["domain_id"]):
        domain_id = domain["domain_id"]
        name = domain["domain_name"]
        subject_terms = [name, name.replace("Dream", "")]
        targeted, has_mapping = _division_categories(name, subject_terms, known, domain_id)
        # Category-level learning approval is separate from MasterBot ownership.
        # The ten supplemental domains may receive subject lessons while their
        # MasterBot ownership remains unresolved and unassigned.
        learning_only_approval = domain_id in approved_supplemental
        if domain.get("mapping_status") != "proposed_exact_name_match":
            targeted = approved_supplemental.get(domain_id, set())
            has_mapping = bool(targeted)
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
        selected = scored if limit is None else scored[:limit]
        rows.append({
            "domain_id": domain_id,
            "domain_name": name,
            "masterbot_id": domain.get("masterbot_id"),
            "mapping_status": domain.get("mapping_status"),
            "owner_review_required": domain.get("review_required", True),
            "learning_route_status": "owner_approved_learning_only" if learning_only_approval else ("owner_mapping_pending" if domain.get("mapping_status") == "unresolved" else "proposed_subject_categories"),
            "masterbot_ownership_status": "unresolved" if domain.get("mapping_status") == "unresolved" else "proposed_exact_name_match",
            "queue_status": ("subject_routed_learning_only_owner_mapping_pending" if learning_only_approval else "subject_routed" if has_mapping else "foundation_only_owner_mapping_pending"),
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
    assigned_video_ids = {
        item["video_id"] for row in rows for item in row["items"]
    }
    classified_video_ids = {
        video["video_id"] for video in videos
        if set(video.get("categories") or []) and set(video.get("categories") or []) != {"other_or_unclassified"}
    }
    unrouted_video_ids = sorted(classified_video_ids - assigned_video_ids)
    if unrouted_video_ids:
        categories_by_id = {
            video["video_id"]: sorted(set(video.get("categories") or []))
            for video in videos if video["video_id"] in set(unrouted_video_ids)
        }
        samples = {video_id: categories_by_id[video_id] for video_id in unrouted_video_ids[:10]}
        raise ValueError(
            f"{len(unrouted_video_ids)} classified videos have no division category route; "
            f"add reviewed category profiles or explicit triage routes: {samples}"
        )
    unclassified_video_count = sum(
        set(video.get("categories") or []) == {"other_or_unclassified"}
        for video in videos
    )
    return {
        "schema": "dreamco.freecodecamp_division_learning_queues.v1",
        "source_catalog_generated_at": catalog.get("generated_at"),
        "source_inventory_status": catalog.get("inventory_status"),
        "source_inventory": inventory,
        "queue_mode": "complete_verified_inventory" if complete_inventory else "provisional_partial_inventory",
        "coverage_warning": None if complete_inventory else "Only observed catalog entries are queued. The full historical freeCodeCamp video archive is not verified; do not claim complete source coverage.",
        "domain_count": len(rows),
        "catalog_video_count": len(videos),
        "classified_video_count": len(classified_video_ids),
        "unclassified_video_count": unclassified_video_count,
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
        if row.get("mapping_status") == "unresolved":
            if row.get("masterbot_id") is not None or row.get("masterbot_ownership_status") != "unresolved":
                raise ValueError("learning-route approval cannot assign unresolved MasterBot ownership")
            if row.get("target_categories"):
                if row.get("learning_route_status") != "owner_approved_learning_only" or row.get("queue_status") != "subject_routed_learning_only_owner_mapping_pending":
                    raise ValueError("supplemental specialist routes require explicit learning-only owner approval")
                if not any(set(row["target_categories"]) & set(item.get("categories") or []) for item in row["items"]):
                    raise ValueError("owner-approved supplemental route has no matching observed video")
            else:
                if row.get("queue_status") != "foundation_only_owner_mapping_pending":
                    raise ValueError("unapproved supplemental domains must remain foundation-only")
                foundation = set(row.get("shared_foundation_categories") or [])
                if not foundation or any(not (foundation & set(item.get("categories") or [])) for item in row["items"]):
                    raise ValueError("unapproved supplemental queues may contain shared foundation lessons only")
        elif row.get("mapping_status") == "proposed_exact_name_match":
            if row.get("target_categories") and row.get("queue_status") != "subject_routed":
                raise ValueError("mapped core domain proposals must use the specialist route")
            if not row.get("target_categories") and row.get("queue_status") != "foundation_only_owner_mapping_pending":
                raise ValueError("core domains without a category profile must remain foundation-only")
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
    parser.add_argument("--limit", type=int, default=None, help="Optional per-division cap; default queues every relevant observed video.")
    parser.add_argument("--allow-partial", action="store_true", help="Build a provisional queue from observed entries only; never claim full archive coverage.")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        raise SystemExit("--limit must be a positive integer when supplied")
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
                      "classified_videos": payload["classified_video_count"],
                      "unclassified_triage_videos": payload["unclassified_video_count"],
                      "subject_routed": sum(bool(row["target_categories"]) for row in payload["domains"]),
                      "learning_only_owner_mapping_pending": sum(row["queue_status"] == "subject_routed_learning_only_owner_mapping_pending" for row in payload["domains"]),
                      "foundation_only": sum(not row["target_categories"] for row in payload["domains"])}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
