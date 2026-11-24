"""Build deterministic, rights-gated freeCodeCamp study queues for all 65 divisions.

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
REGISTRY = ROOT / "config/masterbot-65-registry.json"
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
def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")

def _division_categories(name: str, subject_terms: list[str], known: set[str]) -> tuple[set[str], bool]:
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

def build_queues(catalog: dict[str, Any], registry: dict[str, Any], limit: int = 30) -> dict[str, Any]:
    if catalog.get("schema") != "dreamco.freecodecamp_catalog.v1":
        raise ValueError("unsupported freeCodeCamp catalog schema")
    videos = catalog.get("videos")
    categories = catalog.get("categories")
    divisions = registry.get("divisions")
    if not isinstance(videos, list) or not videos:
        raise ValueError("non-empty freeCodeCamp catalog required")
    if not isinstance(divisions, list) or len(divisions) != 65:
        raise ValueError("canonical 65-division registry required")
    known = {row["id"] for row in categories}
    rows = []
    for division in sorted(divisions, key=lambda row: int(row["id"])):
        division_id = int(division["id"])
        name = division["name"]
        subject_terms = [name, name.replace("Dream", "")]
        targeted, has_mapping = _division_categories(name, subject_terms, known)
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
            "division_id": division_id,
            "division_name": name,
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
        "division_count": len(rows),
        "catalog_video_count": len(videos),
        "queue_limit_per_division": limit,
        "rights_policy": catalog["rights_policy"],
        "divisions": rows,
        "truth_boundary": "Queues prioritize study candidates only. Rights review and independent learning evidence are required before training or mastery claims.",
    }

def validate(payload: dict[str, Any]) -> None:
    rows = payload.get("divisions", [])
    if payload.get("schema") != "dreamco.freecodecamp_division_learning_queues.v1" or len(rows) != 65:
        raise ValueError("exactly 65 division queues are required")
    ids = [row["division_id"] for row in rows]
    if len(set(ids)) != 65:
        raise ValueError("division IDs must be unique")
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
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        raise SystemExit("--limit must be between 1 and 100")
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    payload = build_queues(catalog, registry, args.limit)
    validate(payload)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != rendered:
            raise SystemExit("division queues are stale; regenerate them")
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(json.dumps({"ok": True, "divisions": 65, "catalog_videos": len(catalog["videos"]),
                      "queued_items": sum(row["queue_count"] for row in payload["divisions"]),
                      "subject_routed": sum(row["queue_status"] == "subject_routed" for row in payload["divisions"]),
                      "foundation_only": sum(row["queue_status"] != "subject_routed" for row in payload["divisions"])}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
