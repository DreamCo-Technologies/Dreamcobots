from __future__ import annotations

from framework import GlobalAISourcesFlow  # noqa: F401

import math
import time
from datetime import datetime
from typing import Any

from bots.media_runtime.assets import AssetRecord, LocalAssetStore
from bots.media_runtime.queue import QueuePriority
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
        self._telemetry: dict[str, Any] = {
            "execution_count": 0,
            "failure_count": 0,
            "total_execution_ms": 0.0,
            "provider_latency_ms": {},
            "queue_depth_max": 0,
            "artifact_size_bytes_total": 0,
            "retry_attempts_total": 0,
            "updated_at": None,
        }

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
        tier: str = "free",
        priority: QueuePriority = QueuePriority.NORMAL,
        latency_target_ms: int = 1500,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        start = time.perf_counter()
        resolved_provider_chain = self._provider_chain_for(media_type, provider_chain)
        duration = estimated_duration_sec if estimated_duration_sec is not None else max(10, int(math.ceil(len(str(payload)) / 4)))
        queue_depth_before = self.runtime.queue_size()
        try:
            self.runtime.create_job(
                owner=self.owner,
                media_type=media_type,
                operation=operation,
                payload=payload,
                provider_chain=resolved_provider_chain,
                estimated_duration_sec=duration,
                max_retries=max_retries,
                tier=tier,
                priority=priority,
            )
            completed_job, primary_asset = self.runtime.process_next(
                media_format=output_format,
                content_type=output_content_type,
                lineage=lineage,
                extra_metadata=extra_metadata,
                retention_days=retention_days,
                policy_context={
                    "tier": tier,
                    "media_type": media_type,
                    "latency_target_ms": latency_target_ms,
                },
                allow_degraded=tier in {"pro", "enterprise"},
            )
        except Exception:
            self._telemetry["failure_count"] += 1
            self._telemetry["updated_at"] = datetime.utcnow().isoformat() + "Z"
            raise
        elapsed_ms = (time.perf_counter() - start) * 1000
        self._update_telemetry(
            elapsed_ms=elapsed_ms,
            provider=primary_asset.provider,
            artifact_size=primary_asset.bytes_size,
            attempts=completed_job.attempts,
            queue_depth=max(queue_depth_before, self.runtime.queue_size()),
            queue_snapshot=self.runtime.queue_snapshot(),
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

    def _update_telemetry(
        self,
        *,
        elapsed_ms: float,
        provider: str,
        artifact_size: int,
        attempts: int,
        queue_depth: int,
        queue_snapshot: dict[str, Any],
    ) -> None:
        self._telemetry["execution_count"] += 1
        self._telemetry["total_execution_ms"] += elapsed_ms
        self._telemetry["artifact_size_bytes_total"] += artifact_size
        self._telemetry["queue_depth_max"] = max(self._telemetry["queue_depth_max"], queue_depth)
        self._telemetry["queue_dead_letter_count"] = queue_snapshot.get("dead_letter_count", 0)
        self._telemetry["queue_canceled_count"] = queue_snapshot.get("canceled_count", 0)
        self._telemetry["retry_attempts_total"] += max(0, attempts - 1)
        provider_latency = self._telemetry["provider_latency_ms"]
        provider_latency[provider] = provider_latency.get(provider, 0.0) + elapsed_ms
        self._telemetry["updated_at"] = datetime.utcnow().isoformat() + "Z"

    def telemetry_snapshot(self) -> dict[str, Any]:
        executions = self._telemetry["execution_count"]
        provider_latency = self._telemetry["provider_latency_ms"]
        provider_avg_latency = {
            provider: round(total / executions, 3) if executions else 0.0
            for provider, total in provider_latency.items()
        }
        avg_ms = self._telemetry["total_execution_ms"] / executions if executions else 0.0
        return {
            **self._telemetry,
            "avg_execution_ms": round(avg_ms, 3),
            "provider_avg_latency_ms": provider_avg_latency,
            "provider_governance": self.runtime.gateway.provider_governance_snapshot(),
            "queue_snapshot": self.runtime.queue_snapshot(),
            "runtime_slo": self.runtime.slo_snapshot(),
            "asset_graph": self.asset_store.graph_snapshot(),
        }
