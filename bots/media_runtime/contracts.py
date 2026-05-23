from __future__ import annotations

from datetime import datetime
from typing import Any

from framework import GlobalAISourcesFlow  # noqa: F401

MEDIA_LIFECYCLE_REQUIRED_FIELDS = (
    "job_id",
    "status",
    "project_id",
    "asset_ids",
    "preview_assets",
    "lineage",
    "signed_urls",
    "provider",
    "created_at",
)


def _utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def build_media_lifecycle_contract(
    *,
    job: dict[str, Any],
    primary_asset: dict[str, Any],
    preview_assets: list[dict[str, Any]] | None = None,
    lineage: dict[str, Any] | None = None,
    project_id: str | None = None,
) -> dict[str, Any]:
    preview_assets = preview_assets or []
    all_assets = [primary_asset, *preview_assets]
    resolved_job_id = str(job.get("job_id", ""))
    return {
        "job_id": resolved_job_id,
        "status": job.get("state", "queued"),
        "project_id": project_id or f"media_project_{resolved_job_id}",
        "asset_ids": [asset["asset_id"] for asset in all_assets],
        "preview_assets": [asset["asset_id"] for asset in preview_assets],
        "lineage": lineage or {},
        "signed_urls": [asset["delivery_url"] for asset in all_assets],
        "provider": primary_asset.get("provider", "unknown"),
        "created_at": job.get("created_at", _utc_now()),
    }


def validate_media_lifecycle_contract(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    missing = [field for field in MEDIA_LIFECYCLE_REQUIRED_FIELDS if field not in payload]
    if missing:
        return False, missing

    type_errors: list[str] = []
    if not isinstance(payload["asset_ids"], list):
        type_errors.append("asset_ids")
    if not isinstance(payload["preview_assets"], list):
        type_errors.append("preview_assets")
    if not isinstance(payload["lineage"], dict):
        type_errors.append("lineage")
    if not isinstance(payload["signed_urls"], list):
        type_errors.append("signed_urls")

    return len(type_errors) == 0, type_errors
