"""Permission-gated study attempts with guaranteed temporary workspace cleanup.

This is an execution boundary, not a downloader. A study adapter must receive
this context and place every temporary file it creates inside context.workspace.
Evidence and original DreamCo-authored notes must be persisted elsewhere.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Any
from urllib.parse import urlparse

from buddy.learning.study_artifact_cleanup import study_download_workspace

_ALLOWED = {"open_official_page", "download_media", "ingest_transcript", "derive_original_lesson"}
_RESTRICTED = {"download_media", "ingest_transcript"}


@dataclass(frozen=True)
class StudyAuthorization:
    source_name: str
    source_url: str
    review_status: str
    allowed_operations: frozenset[str] = frozenset({"open_official_page"})
    evidence_ref: str | None = None


@dataclass(frozen=True)
class StudyContext:
    workspace: Path
    source_name: str
    source_url: str
    allowed_operations: frozenset[str]
    media_download_allowed: bool
    transcript_ingestion_allowed: bool
    model_training_allowed: bool = False


def validate_authorization(auth: StudyAuthorization) -> None:
    parsed = urlparse(auth.source_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise PermissionError("study source must be an HTTPS URL")
    unknown = set(auth.allowed_operations) - _ALLOWED
    if unknown:
        raise PermissionError(f"unknown study operations: {sorted(unknown)}")
    if auth.review_status not in {"pending", "approved", "restricted", "rejected", "public_metadata_only"}:
        raise PermissionError("invalid rights review status")
    if auth.review_status in {"restricted", "rejected"} and auth.allowed_operations:
        raise PermissionError("restricted or rejected sources cannot be studied")
    if auth.review_status != "approved" and set(auth.allowed_operations) & _RESTRICTED:
        raise PermissionError("media and transcript operations require explicit approved rights evidence")
    if set(auth.allowed_operations) & _RESTRICTED and not auth.evidence_ref:
        raise PermissionError("media and transcript permissions require a rights evidence reference")


def run_study_attempt(
    authorization: StudyAuthorization,
    study: Callable[[StudyContext], Any],
    workspace_root: Path,
) -> dict:
    """Run one attempt; remove its workspace after success, error, or cancellation."""
    validate_authorization(authorization)
    with study_download_workspace(workspace_root) as workspace:
        context = StudyContext(
            workspace=workspace,
            source_name=authorization.source_name,
            source_url=authorization.source_url,
            allowed_operations=authorization.allowed_operations,
            media_download_allowed="download_media" in authorization.allowed_operations,
            transcript_ingestion_allowed="ingest_transcript" in authorization.allowed_operations,
        )
        result = study(context)
    # Do not include workspace paths or temporary content in durable evidence.
    return {
        "status": "study_attempt_completed",
        "source_name": authorization.source_name,
        "source_url": authorization.source_url,
        "rights_review_status": authorization.review_status,
        "rights_evidence_ref": authorization.evidence_ref,
        "media_downloaded": context.media_download_allowed,
        "transcript_ingested": context.transcript_ingestion_allowed,
        "model_training_allowed": False,
        "result": result,
        "temporary_workspace_erased": not workspace.exists(),
    }
