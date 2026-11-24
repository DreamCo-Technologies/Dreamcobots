"""Build complete freeCodeCamp source routes for every Buddy division."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "buddy/bootcamp/sources/freecodecamp/catalog.json"
REGISTRY = ROOT / "config/masterbot-65-registry.json"
OUTPUT = ROOT / "config/generated/freecodecamp-source-routes.json"

ALIASES = {
"finance":{"databases_and_sql","data_science_and_visualization","mathematics_and_statistics","generative_ai_and_llms"},
"real estate":{"databases_and_sql","data_science_and_visualization","software_architecture_and_testing","generative_ai_and_llms"},
"sales":{"generative_ai_and_llms","data_science_and_visualization","backend_and_apis"},
"ai infra":{"generative_ai_and_llms","ai_agents_and_mcp","cloud_devops_and_ci_cd","databases_and_sql","python_and_automation"},
"data":{"databases_and_sql","data_science_and_visualization","machine_learning_and_deep_learning","python_and_automation"},
"automation":{"python_and_automation","ai_agents_and_mcp","backend_and_apis","cloud_devops_and_ci_cd"},
"cyber":{"cybersecurity_and_privacy","linux_networking_and_it","c_cpp_and_systems"},
"code":{"computer_science_and_fundamentals","javascript_and_typescript","python_and_automation","c_cpp_and_systems","software_architecture_and_testing"},
"education":{"computer_science_and_fundamentals","python_and_automation","generative_ai_and_llms"},
"research":{"computer_science_and_fundamentals","data_science_and_visualization","machine_learning_and_deep_learning","mathematics_and_statistics"},
"science":{"data_science_and_visualization","machine_learning_and_deep_learning","mathematics_and_statistics","python_and_automation"},
"game":{"game_development","c_cpp_and_systems","mathematics_and_statistics"},
"content":{"html_css_and_accessibility","javascript_and_typescript","frontend_and_ui_frameworks","data_science_and_visualization"},
"market":{"data_science_and_visualization","databases_and_sql","generative_ai_and_llms"},
"legal":{"cybersecurity_and_privacy","databases_and_sql","generative_ai_and_llms"},
"health":{"data_science_and_visualization","cybersecurity_and_privacy","databases_and_sql","generative_ai_and_llms"},
"transport":{"data_science_and_visualization","backend_and_apis","cloud_devops_and_ci_cd"},
"construction":{"data_science_and_visualization","python_and_automation","software_architecture_and_testing"},
"agriculture":{"data_science_and_visualization","python_and_automation","machine_learning_and_deep_learning"},
"crypto":{"databases_and_sql","cybersecurity_and_privacy","mathematics_and_statistics","backend_and_apis"},
"payments":{"databases_and_sql","cybersecurity_and_privacy","backend_and_apis"},
"admin":{"python_and_automation","databases_and_sql","cloud_devops_and_ci_cd"},
"agents":{"ai_agents_and_mcp","generative_ai_and_llms","python_and_automation"},
"benchmark":{"machine_learning_and_deep_learning","data_science_and_visualization","mathematics_and_statistics","software_architecture_and_testing"},
"knowledge":{"generative_ai_and_llms","databases_and_sql","python_and_automation"},
"robot":{"c_cpp_and_systems","python_and_automation","machine_learning_and_deep_learning"},
"mobile":{"mobile_and_cross_platform","javascript_and_typescript","software_architecture_and_testing"},
"web":{"html_css_and_accessibility","javascript_and_typescript","frontend_and_ui_frameworks","backend_and_apis"},
}
FOUNDATION = {"computer_science_and_fundamentals","html_css_and_accessibility","javascript_and_typescript","python_and_automation","databases_and_sql","software_architecture_and_testing","cybersecurity_and_privacy","cloud_devops_and_ci_cd"}

def normalize_name(value: str) -> str:
    value = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", value)
    value = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", value)
    return value.casefold().replace("dream", " ")

def division_specialties(name: str, known: set[str]) -> set[str]:
    haystack = normalize_name(name)
    result: set[str] = set()
    for alias, categories in ALIASES.items():
        if alias in haystack:
            result.update(categories & known)
    for category in known:
        if category.replace("_", " ") in haystack:
            result.add(category)
    return result

def build_routes(catalog: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    if catalog.get("schema") != "dreamco.freecodecamp_catalog.v1":
        raise ValueError("unsupported freeCodeCamp catalog schema")
    divisions = registry.get("divisions")
    videos = catalog.get("videos")
    categories = catalog.get("categories")
    if not isinstance(divisions, list) or len(divisions) != 65:
        raise ValueError("canonical registry with exactly 65 divisions required")
    if not isinstance(videos, list) or not videos:
        raise ValueError("non-empty source catalog required")
    known = {row["id"] for row in categories}
    specs = {int(d["id"]): division_specialties(d["name"], known) for d in divisions}
    routes = []
    for video in sorted(videos, key=lambda v: v["video_id"]):
        tags = set(video.get("categories") or [])
        if not tags:
            raise ValueError(f"video {video.get('video_id')} has no taxonomy route")
        specialists = sorted(
            division_id for division_id, wanted in specs.items()
            if tags & wanted
        )
        unclassified = "other_or_unclassified" in tags
        routes.append({
            "video_id": video["video_id"],
            "title": video["title"],
            "url": video["url"],
            "categories": sorted(tags),
            "accessible_to_divisions": "all_65",
            "specialty_division_ids": specialists,
            "shared_foundation": bool(tags & FOUNDATION) or not specialists,
            "routing_status": "specialty_and_shared" if specialists else ("unclassified_review" if unclassified else "shared_catalog"),
            "rights_status": "review_required",
            "learning_status": "not_studied",
            "study_allowed": True,
            "media_download_allowed": False,
            "transcript_ingestion_allowed": False,
            "model_training_allowed": False,
            "study_steps": ["open_official_source", "create_original_lesson_notes", "complete_sandbox_exercise", "run_target_benchmark", "run_holdout", "run_regression"],
        })
    division_rows = []
    for division in sorted(divisions, key=lambda d: int(d["id"])):
        division_id = int(division["id"])
        specialty = [r["video_id"] for r in routes if division_id in r["specialty_division_ids"]]
        division_rows.append({
            "division_id": division_id,
            "division_name": division["name"],
            "catalog_access": "all_1740_or_current_catalog_entries",
            "available_video_count": len(routes),
            "specialty_video_count": len(specialty),
            "specialty_video_ids": specialty,
            "shared_catalog_access": True,
            "unclassified_review_access": True,
            "scheduler": "buddy.learning.freecodecamp_source.select_next_for_division",
        })
    return {
        "schema": "dreamco.freecodecamp_source_routes.v1",
        "source_catalog_generated_at": catalog.get("generated_at"),
        "catalog_video_count": len(routes),
        "division_count": len(division_rows),
        "all_videos_accessible_to_all_divisions": True,
        "rights_policy": catalog["rights_policy"],
        "divisions": division_rows,
        "videos": routes,
        "truth_boundary": "Every catalog item is discoverable by every division. Specialty tags rank recommendations, not permission or proven relevance. Opening a source and passing original exercises are required for learning evidence; model training remains separately prohibited pending rights approval.",
    }

def validate(payload: dict[str, Any]) -> None:
    if payload.get("schema") != "dreamco.freecodecamp_source_routes.v1":
        raise ValueError("unsupported route schema")
    if payload.get("division_count") != 65 or len(payload.get("divisions", [])) != 65:
        raise ValueError("routes must include all 65 divisions")
    videos = payload.get("videos", [])
    if len(videos) != payload.get("catalog_video_count") or not videos:
        raise ValueError("every catalog video must have exactly one source route record")
    ids = [v["video_id"] for v in videos]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate video route IDs")
    if not payload.get("all_videos_accessible_to_all_divisions"):
        raise ValueError("all divisions must have catalog access")
    for video in videos:
        if video["accessible_to_divisions"] != "all_65":
            raise ValueError("video route must be available to all 65 divisions")
        if video["rights_status"] != "review_required" or video["model_training_allowed"]:
            raise ValueError("source discovery cannot authorize model training")
        if video["media_download_allowed"] or video["transcript_ingestion_allowed"]:
            raise ValueError("source discovery cannot authorize media or transcript ingestion")
    for division in payload["divisions"]:
        if division["available_video_count"] != len(videos) or not division["shared_catalog_access"]:
            raise ValueError("division does not have complete catalog access")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    payload = build_routes(catalog, registry)
    validate(payload)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != rendered:
            raise SystemExit("source routes are stale; regenerate")
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(json.dumps({"ok": True, "videos": len(payload["videos"]), "divisions": 65,
                      "specialty_routes": sum(len(v["specialty_division_ids"]) for v in payload["videos"]),
                      "all_divisions_have_all_videos": all(d["available_video_count"] == len(payload["videos"]) for d in payload["divisions"])}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
