"""Runtime adapter exposing every freeCodeCamp catalog item to Buddy's study scheduler."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Iterable
from buddy.learning.study_resource_scheduler import Capability, Resource, choose_next

ROOT = Path(__file__).resolve().parents[2]
ROUTES = ROOT / "config/generated/freecodecamp-source-routes.json"

def load_routes(path: Path = ROUTES) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "dreamco.freecodecamp_source_routes.v1" or payload.get("division_count") != 65:
        raise ValueError("invalid or incomplete freeCodeCamp source routes")
    return payload

def resources_for_division(division_id: int, path: Path = ROUTES) -> list[Resource]:
    if not isinstance(division_id, int) or not 1 <= division_id <= 65:
        raise ValueError("division_id must be between 1 and 65")
    payload = load_routes(path)
    division = next((d for d in payload["divisions"] if d["division_id"] == division_id), None)
    if division is None or division["available_video_count"] != payload["catalog_video_count"]:
        raise ValueError("division route is incomplete")
    specialty_ids = set(division["specialty_video_ids"])
    resources = []
    for index, video in enumerate(payload["videos"], 1):
        categories = tuple(video["categories"])
        methods = ("open_official_source", "write_original_notes", "sandbox_exercise", "target_benchmark", "holdout", "regression")
        resource = Resource(id=index, name=video["title"], category=" ".join(categories), url=video["url"], methods=methods)
        resources.append(resource)
    # Keep stable resource IDs and return the full shared catalog. The caller's
    # capability gaps and recently studied IDs drive the actual selection.
    return resources

def select_next_for_division(division_id: int, gaps: Iterable[Capability], *, recent: set[int] | None = None,
                             path: Path = ROUTES) -> Resource | None:
    resources = resources_for_division(division_id, path)
    return choose_next(resources, gaps, recent=recent)

def route_summary(path: Path = ROUTES) -> dict:
    payload = load_routes(path)
    return {"source": "freeCodeCamp.org", "catalog_video_count": payload["catalog_video_count"],
            "division_count": payload["division_count"], "all_divisions_have_full_access": True,
            "learning_is_automatic": False, "next_step": "select lesson, study authorized source, practice, benchmark and record evidence"}
