from __future__ import annotations

import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from bots.media_runtime.assets import AssetRecord, LocalAssetStore
from bots.media_runtime.inference_gateway import InferenceGateway, ProviderFailure


def _utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


class JobState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    RETRYING = "retrying"
    VALIDATING = "validating"
    TRANSCODING = "transcoding"


@dataclass
class RenderJob:
    job_id: str
    owner: str
    media_type: str
    operation: str
    payload: dict[str, Any]
    provider_chain: list[str]
    state: JobState = JobState.QUEUED
    progress_percent: int = 0
    current_stage: str = "queued"
    estimated_duration_sec: int = 0
    attempts: int = 0
    max_retries: int = 2
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)
    started_at: str | None = None
    completed_at: str | None = None
    failure_reason: str | None = None
    artifact_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "owner": self.owner,
            "media_type": self.media_type,
            "operation": self.operation,
            "payload": self.payload,
            "provider_chain": self.provider_chain,
            "state": self.state.value,
            "progress_percent": self.progress_percent,
            "current_stage": self.current_stage,
            "estimated_duration_sec": self.estimated_duration_sec,
            "attempts": self.attempts,
            "max_retries": self.max_retries,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "failure_reason": self.failure_reason,
            "artifact_ids": self.artifact_ids,
        }


class MediaJobRuntime:
    """Queue-backed render runtime with deterministic lifecycle state progression."""

    def __init__(self, asset_store: LocalAssetStore | None = None, gateway: InferenceGateway | None = None) -> None:
        self.asset_store = asset_store or LocalAssetStore()
        self.gateway = gateway or InferenceGateway()
        self.jobs: dict[str, RenderJob] = {}
        self._queue: deque[str] = deque()

    def create_job(
        self,
        *,
        owner: str,
        media_type: str,
        operation: str,
        payload: dict[str, Any],
        provider_chain: list[str],
        estimated_duration_sec: int = 60,
        max_retries: int = 2,
    ) -> RenderJob:
        job = RenderJob(
            job_id=f"job_{uuid.uuid4().hex[:14]}",
            owner=owner,
            media_type=media_type,
            operation=operation,
            payload=payload,
            provider_chain=provider_chain,
            estimated_duration_sec=estimated_duration_sec,
            max_retries=max_retries,
        )
        self.jobs[job.job_id] = job
        self._queue.append(job.job_id)
        return job

    def process_next(
        self,
        *,
        media_format: str,
        content_type: str,
        lineage: list[str] | None = None,
        extra_metadata: dict[str, Any] | None = None,
        retention_days: int = 30,
    ) -> tuple[RenderJob, AssetRecord]:
        if not self._queue:
            raise RuntimeError("No queued jobs")

        job = self.jobs[self._queue.popleft()]
        job.state = JobState.RUNNING
        job.current_stage = "provider_execution"
        job.progress_percent = 10
        job.started_at = _utc_now()
        job.updated_at = _utc_now()

        while True:
            job.attempts += 1
            try:
                provider_result = self.gateway.run(
                    {
                        "media_type": job.media_type,
                        "operation": job.operation,
                        **job.payload,
                    },
                    provider_chain=job.provider_chain,
                )
                job.current_stage = "artifact_persistence"
                job.progress_percent = 70
                job.updated_at = _utc_now()

                metadata = {
                    "media_type": job.media_type,
                    "operation": job.operation,
                    "attempts": job.attempts,
                    **provider_result.metadata,
                }
                if extra_metadata:
                    metadata.update(extra_metadata)

                asset = self.asset_store.persist(
                    owner=job.owner,
                    originating_job=job.job_id,
                    provider=provider_result.provider,
                    media_format=media_format,
                    content_type=content_type,
                    content_bytes=provider_result.payload_bytes,
                    metadata=metadata,
                    lineage=lineage,
                    retention_days=retention_days,
                )

                job.current_stage = "validating"
                job.state = JobState.VALIDATING
                job.progress_percent = 90
                job.updated_at = _utc_now()

                if not asset.storage_path:
                    raise RuntimeError("Asset persistence failed validation")

                job.state = JobState.COMPLETED
                job.current_stage = "completed"
                job.progress_percent = 100
                job.completed_at = _utc_now()
                job.updated_at = _utc_now()
                job.artifact_ids.append(asset.asset_id)
                return job, asset
            except ProviderFailure as exc:
                if job.attempts <= job.max_retries:
                    job.state = JobState.RETRYING
                    job.current_stage = "retrying"
                    job.progress_percent = min(95, 20 + (job.attempts * 20))
                    job.failure_reason = str(exc)
                    job.updated_at = _utc_now()
                    time.sleep(0.01 * (2 ** (job.attempts - 1)))
                    continue
                job.state = JobState.FAILED
                job.current_stage = "failed"
                job.progress_percent = 100
                job.failure_reason = str(exc)
                job.completed_at = _utc_now()
                job.updated_at = _utc_now()
                raise

    def queue_size(self) -> int:
        return len(self._queue)

    def get_job(self, job_id: str) -> RenderJob | None:
        return self.jobs.get(job_id)
