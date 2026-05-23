from __future__ import annotations

from framework import GlobalAISourcesFlow  # noqa: F401

import math
from typing import Any

from bots.media_runtime.assets import AssetRecord, LocalAssetStore
from bots.media_runtime.runtime import MediaJobRuntime, RenderJob
from bots.media_runtime.state import AssetRegistry, RenderJobRepository


class MediaEngine:
    """Centralized media execution wrapper with standardized provider routing and asset handling."""

    _DEFAULT_PROVIDER_ROUTES: dict[str, list[str]] = {
        "audio": ["elevenlabs", "openai", "ffmpeg-local"],
        "video": ["ffmpeg-local", "openai", "elevenlabs"],
        "image": ["openai", "ffmpeg-local", "elevenlabs"],
    }

    def __init__(
        self,
        *,
        owner: str,
        runtime: MediaJobRuntime,
        asset_store: LocalAssetStore,
        job_repository: RenderJobRepository | None = None,
        asset_registry: AssetRegistry | None = None,
        provider_routes: dict[str, list[str]] | None = None,
    ) -> None:
        self.owner = owner
        self.runtime = runtime
        self.asset_store = asset_store
        self.job_repository = job_repository
        self.asset_registry = asset_registry
        self.provider_routes = provider_routes or self._DEFAULT_PROVIDER_ROUTES

    def _provider_chain_for(self, media_type: str, provider_chain: list[str] | None) -> list[str]:
        if provider_chain:
            return provider_chain
        return self.provider_routes.get(media_type, ["openai", "ffmpeg-local"])

    def execute_render(
        self,
        *,
        operation: str,
        media_type: str,
        payload: dict[str, Any],
        output_format: str,
        output_content_type: str,
        provider_chain: list[str] | None = None,
        lineage: list[str] | None = None,
        extra_metadata: dict[str, Any] | None = None,
        retention_days: int = 30,
        estimated_duration_sec: int | None = None,
        max_retries: int = 2,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        resolved_provider_chain = self._provider_chain_for(media_type, provider_chain)
        duration = estimated_duration_sec if estimated_duration_sec is not None else max(10, int(math.ceil(len(str(payload)) / 4)))
        self.runtime.create_job(
            owner=self.owner,
            media_type=media_type,
            operation=operation,
            payload=payload,
            provider_chain=resolved_provider_chain,
            estimated_duration_sec=duration,
            max_retries=max_retries,
        )
        completed_job, primary_asset = self.runtime.process_next(
            media_format=output_format,
            content_type=output_content_type,
            lineage=lineage,
            extra_metadata=extra_metadata,
            retention_days=retention_days,
        )
        self._record_job(completed_job)
        self._record_asset(primary_asset)
        return completed_job.to_dict(), primary_asset.to_dict()

    def persist_artifact(
        self,
        *,
        originating_job: str,
        provider: str,
        media_format: str,
        content_type: str,
        content_bytes: bytes,
        metadata: dict[str, Any] | None = None,
        lineage: list[str] | None = None,
        retention_days: int = 30,
    ) -> dict[str, Any]:
        asset = self.asset_store.persist(
            owner=self.owner,
            originating_job=originating_job,
            provider=provider,
            media_format=media_format,
            content_type=content_type,
            content_bytes=content_bytes,
            lineage=lineage,
            metadata=metadata,
            retention_days=retention_days,
        )
        self._record_asset(asset)
        return asset.to_dict()

    def _record_job(self, job: RenderJob) -> None:
        if self.job_repository:
            self.job_repository.save(job.to_dict())

    def _record_asset(self, asset: AssetRecord) -> None:
        if self.asset_registry:
            self.asset_registry.register(asset.to_dict())
