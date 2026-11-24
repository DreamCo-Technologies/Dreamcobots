"""FreeCodeCamp metadata routes and evidence-gated study plans."""
import json
import shutil
import tempfile
from pathlib import Path
from typing import Iterable
from buddy.learning.permissioned_study_worker import StudyAuthorization, StudyContext
from buddy.learning.study_resource_scheduler import Capability, Resource, choose_next

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROUTES = ROOT / "artifacts/buddy-dataset-hub/freecodecamp-routes.json"

def resources_for_division(division_id: int, path=DEFAULT_ROUTES) -> list[dict]:
    if not isinstance(division_id, int) or not 1 <= division_id <= 65:
        raise ValueError("division id must be between 1 and 65")
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not any(x.get("id") == division_id for x in payload.get("divisions", [])):
        raise ValueError(f"division {division_id} is not in the canonical registry")
    return list(payload.get("videos", []))

def select_next_for_division(division_id: int, gaps: Iterable[Capability], *, path=DEFAULT_ROUTES, recent: set[int] | None = None):
    videos = resources_for_division(division_id, path)
    resources = [Resource(id=i, name=v["title"], category=" ".join(v.get("categories", [])), url=v["url"]) for i, v in enumerate(videos)]
    selected = choose_next(resources, gaps, recent=recent)
    return videos[selected.id] if selected is not None else None

def plan_next_lesson(division_id: int, capability: Capability, *, path=DEFAULT_ROUTES, recent: set[int] | None = None):
    video = select_next_for_division(division_id, [capability], path=path, recent=recent)
    if video is None:
        return None
    return {
        "division_id": division_id, "video_id": video["video_id"], "source": "freeCodeCamp.org",
        "source_url": video["url"], "title": video["title"], "categories": list(video.get("categories", [])),
        "steps": ["open_official_page", "record_source_metadata_and_provenance",
                  "extract_original_concepts_without_copying_course_material", "create_original_practice_task",
                  "practice_in_sandbox", "run_targeted_benchmark", "record_evidence_and_retest"],
        "completion_status": "queued_not_studied",
        "transcript_status": video.get("transcript_status", "not_ingested_rights_gate"),
        "media_download_allowed": False, "transcript_ingestion_allowed": False,
        "model_training_allowed": False, "execution_status": "PLAN_ONLY_NOT_EXECUTED",
    }

def execute_study_plan(plan: dict, authorization: StudyAuthorization, study_callback, workspace_root):
    if authorization.source != plan.get("source"):
        raise ValueError("study authorization source does not match plan")
    if authorization.source_url != plan.get("source_url"):
        raise ValueError("study authorization URL does not match plan")
    if authorization.scope != "public_metadata_only":
        raise ValueError("study scope is not authorized for this metadata-only worker")
    if "open_official_page" not in authorization.allowed_actions:
        raise ValueError("study authorization does not permit opening the official page")
    root = Path(workspace_root)
    root.mkdir(parents=True, exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix="freecodecamp-study-", dir=root))
    result = None
    try:
        result = study_callback(StudyContext(workspace=workspace))
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
    return {
        "completion_status": "attempted_evidence_pending", "study_result": result,
        "temporary_workspace_erased": not workspace.exists(), "media_download_allowed": False,
        "transcript_ingestion_allowed": False, "model_training_allowed": False,
    }
