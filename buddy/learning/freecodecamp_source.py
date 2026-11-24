"""Runtime adapter exposing every freeCodeCamp catalog item to Buddy's study scheduler."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Iterable
from buddy.learning.study_resource_scheduler import Capability, Resource, choose_next, study_plan
from buddy.learning.study_artifact_cleanup import study_download_workspace

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
    # choose_next evaluates gaps once per candidate; materialize generators so
    # every candidate receives the same complete gap set.
    gap_list = list(gaps)
    return choose_next(resources, gap_list, recent=recent)

def route_summary(path: Path = ROUTES) -> dict:
    payload = load_routes(path)
    return {"source": "freeCodeCamp.org", "catalog_video_count": payload["catalog_video_count"],
            "division_count": payload["division_count"], "all_divisions_have_full_access": True,
            "learning_is_automatic": False, "next_step": "select lesson, study authorized source, practice, benchmark and record evidence"}


def plan_next_lesson(division_id: int, capability: Capability, *, recent: set[int] | None = None,
                     path: Path = ROUTES) -> dict | None:
    """Return the next official-source lesson and the scheduler's evidence loop."""
    resource = select_next_for_division(division_id, [capability], recent=recent, path=path)
    if resource is None:
        return None
    plan = study_plan(resource, capability)
    plan.update({
        "source_url": resource.url,
        "division_id": division_id,
        "source": "freeCodeCamp.org",
        "rights_status": "review_required",
        "media_download_allowed": False,
        "transcript_ingestion_allowed": False,
        "model_training_allowed": False,
        "completion_status": "queued_not_studied",
        "temporary_workspace_policy": "erase_on_success_failure_or_cancellation",
        "workspace_context_manager": "buddy.learning.study_artifact_cleanup.study_download_workspace",
    })
    return plan
