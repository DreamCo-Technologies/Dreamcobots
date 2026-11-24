"""Runtime adapter exposing every freeCodeCamp catalog item to Buddy's study scheduler."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from buddy.learning.permissioned_study_worker import StudyAuthorization, run_study_attempt
from typing import Iterable
from buddy.learning.study_resource_scheduler import Capability, Resource, choose_next, study_plan

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "buddy/bootcamp/sources/freecodecamp/catalog.json"
REGISTRY = ROOT / "config/masterbot-65-registry.json"
ROUTES = CATALOG

def stable_resource_id(video_id: str) -> int:
    """Return a deterministic scheduler ID that survives catalog reordering."""
    if not isinstance(video_id, str) or not video_id.strip():
        raise ValueError("video_id must be a non-empty string")
    value = int.from_bytes(hashlib.sha256(video_id.encode("utf-8")).digest()[:8], "big") & 0x7FFFFFFFFFFFFFFF
    return value or 1


def load_routes(path: Path = ROUTES) -> dict:
    """Load the canonical catalog directly; accept generated routes for compatibility/tests."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") == "dreamco.freecodecamp_catalog.v1":
        videos = payload.get("videos")
        inventory = payload.get("inventory") or {}
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        divisions = registry.get("divisions", [])
        if (
            payload.get("inventory_status") != "complete"
            or not isinstance(videos, list)
            or not videos
            or payload.get("video_count") != len(videos)
            or inventory.get("complete") is not True
            or inventory.get("expected_entry_count") != len(videos)
            or inventory.get("observed_entry_count") != len(videos)
            or inventory.get("null_entry_count") != 0
            or inventory.get("duplicate_video_id_count") != 0
            or len(divisions) != 65
        ):
            raise ValueError("freeCodeCamp catalog is not a verified complete inventory")
        return {
            "schema": "dreamco.freecodecamp_runtime_catalog.v1",
            "division_count": 65,
            "catalog_video_count": len(videos),
            "divisions": [
                {"division_id": int(row["id"]), "available_video_count": len(videos)}
                for row in divisions
            ],
            "videos": videos,
        }
    if payload.get("schema") != "dreamco.freecodecamp_source_routes.v1" or payload.get("division_count") != 65:
        raise ValueError("invalid or incomplete freeCodeCamp source routes")
    inventory = payload.get("source_inventory") or {}
    if (
        payload.get("source_inventory_status") != "complete"
        or inventory.get("complete") is not True
        or inventory.get("observed_entry_count") != payload.get("catalog_video_count")
    ):
        raise ValueError("source routes do not contain verified complete catalog evidence")
    return payload

def resources_for_division(division_id: int, path: Path = ROUTES) -> list[Resource]:
    if not isinstance(division_id, int) or not 1 <= division_id <= 65:
        raise ValueError("division_id must be between 1 and 65")
    payload = load_routes(path)
    division = next((d for d in payload["divisions"] if d["division_id"] == division_id), None)
    if division is None or division["available_video_count"] != payload["catalog_video_count"]:
        raise ValueError("division route is incomplete")
    resources = []
    seen_ids: dict[int, str] = {}
    for video in payload["videos"]:
        video_id = video["video_id"]
        resource_id = stable_resource_id(video_id)
        previous = seen_ids.get(resource_id)
        if previous is not None and previous != video_id:
            raise ValueError(f"stable resource ID collision between {previous} and {video_id}")
        seen_ids[resource_id] = video_id
        categories = tuple(video["categories"])
        methods = ("open_official_source", "write_original_notes", "sandbox_exercise", "target_benchmark", "holdout", "regression")
        resource = Resource(id=resource_id, name=video["title"], category=" ".join(categories), url=video["url"], methods=methods)
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


def execute_study_plan(plan: dict, authorization: StudyAuthorization, study, workspace_root: Path) -> dict:
    """Execute a queued plan through the permission and cleanup boundary.

    The caller must supply a rights-reviewed operation set. freeCodeCamp plans
    default to metadata-only; they cannot download media or ingest transcripts.
    """
    if plan.get("completion_status") != "queued_not_studied":
        raise ValueError("only a queued, not-yet-studied plan can be executed")
    if plan.get("source_url") != authorization.source_url:
        raise ValueError("study authorization URL does not match the selected plan")
    if plan.get("source") != authorization.source_name:
        raise ValueError("study authorization source does not match the selected plan")
    if plan.get("media_download_allowed") is not False or plan.get("transcript_ingestion_allowed") is not False:
        raise PermissionError("freeCodeCamp catalog plans do not authorize media or transcript ingestion")
    result = run_study_attempt(authorization, study, workspace_root)
    result["division_id"] = plan["division_id"]
    result["resource_id"] = plan["resource_id"]
    result["completion_status"] = "attempted_evidence_pending"
    return result
