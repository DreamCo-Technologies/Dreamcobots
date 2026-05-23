from __future__ import annotations

from framework import GlobalAISourcesFlow  # noqa: F401

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from bots.media_runtime.assets import AssetRecord, LocalAssetStore
from bots.media_runtime.inference_gateway import InferenceGateway, ProviderFailure
from bots.media_runtime.queue import DurableMediaQueue, QueuePriority


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
    canceled_at: str | None = None
    failure_reason: str | None = None
    failure_class: str | None = None
    retry_classification: str | None = None
    artifact_ids: list[str] = field(default_factory=list)
    priority: str = QueuePriority.NORMAL.name.lower()
    tier: str = "free"
    queue_entered_at: str = field(default_factory=_utc_now)
    queue_latency_ms: float = 0.0

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
            "canceled_at": self.canceled_at,
            "failure_reason": self.failure_reason,
            "failure_class": self.failure_class,
            "retry_classification": self.retry_classification,
            "artifact_ids": self.artifact_ids,
            "priority": self.priority,
            "tier": self.tier,
            "queue_entered_at": self.queue_entered_at,
            "queue_latency_ms": self.queue_latency_ms,
        }


class MediaJobRuntime:
    """Queue-backed render runtime with deterministic lifecycle state progression."""

    def __init__(
        self,
        asset_store: LocalAssetStore | None = None,
        gateway: InferenceGateway | None = None,
        queue: DurableMediaQueue | None = None,
        *,
        max_queue_depth: int = 500,
        max_concurrency: int = 4,
    ) -> None:
        self.asset_store = asset_store or LocalAssetStore()
        self.gateway = gateway or InferenceGateway()
        self.jobs: dict[str, RenderJob] = {}
        self._queue = queue or DurableMediaQueue(max_depth=max_queue_depth)
        self.max_concurrency = max(1, max_concurrency)
        self._active_executions = 0
        self._metrics: dict[str, float] = {
            "jobs_created": 0.0,
            "jobs_completed": 0.0,
            "jobs_failed": 0.0,
            "jobs_canceled": 0.0,
            "jobs_retried": 0.0,
            "queue_latency_ms_total": 0.0,
        }

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
        priority: QueuePriority = QueuePriority.NORMAL,
        tier: str = "free",
    ) -> RenderJob:
        if self.queue_size() >= self._queue.max_depth:
            raise RuntimeError("Queue saturation threshold reached")
        job = RenderJob(
            job_id=f"job_{uuid.uuid4().hex[:14]}",
            owner=owner,
            media_type=media_type,
            operation=operation,
            payload=payload,
            provider_chain=provider_chain,
            estimated_duration_sec=estimated_duration_sec,
            max_retries=max_retries,
            priority=priority.name.lower(),
            tier=tier,
        )
        self.jobs[job.job_id] = job
        self._queue.enqueue(job.job_id, priority=priority, tier=tier)
        self._metrics["jobs_created"] += 1
        return job

    def process_next(
        self,
        *,
        media_format: str,
        content_type: str,
        lineage: list[str] | None = None,
        extra_metadata: dict[str, Any] | None = None,
        retention_days: int = 30,
        worker_id: str = "worker_default",
        policy_context: dict[str, Any] | None = None,
        allow_degraded: bool = False,
    ) -> tuple[RenderJob, AssetRecord]:
        if self._active_executions >= self.max_concurrency:
            raise RuntimeError("worker_concurrency_saturated")

        job_id = self._queue.dequeue(worker_id=worker_id, lease_seconds=max(30, int(retention_days)))
        if not job_id:
            raise RuntimeError("No queued jobs")

        job = self.jobs[job_id]
        if job.state == JobState.CANCELED:
            self._queue.ack(job.job_id)
            self._metrics["jobs_canceled"] += 1
            raise RuntimeError("Queued job was canceled")

        job.state = JobState.RUNNING
        job.current_stage = "provider_execution"
        job.progress_percent = 10
        job.started_at = _utc_now()
        job.updated_at = _utc_now()
        started_at = time.perf_counter()
        self._active_executions += 1
        queue_latency_ms = (datetime.fromisoformat(job.started_at.rstrip("Z")) - datetime.fromisoformat(job.queue_entered_at.rstrip("Z"))).total_seconds() * 1000
        job.queue_latency_ms = max(0.0, queue_latency_ms)
        self._metrics["queue_latency_ms_total"] += job.queue_latency_ms

        try:
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
                    policy_context={
                        "media_type": job.media_type,
                        "tier": job.tier,
                        **(policy_context or {}),
                    },
                    allow_degraded=allow_degraded,
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
                    self._queue.ack(job.job_id)
                    self._metrics["jobs_completed"] += 1
                    return job, asset
                except ProviderFailure as exc:
                    job.retry_classification = self._classify_retry(exc)
                    if job.attempts <= job.max_retries:
                        job.state = JobState.RETRYING
                        job.current_stage = "retrying"
                        job.progress_percent = min(95, 20 + (job.attempts * 20))
                        job.failure_reason = str(exc)
                        job.failure_class = "provider_failure"
                        job.updated_at = _utc_now()
                        self._queue.retry(job.job_id, reason=str(exc), delay_seconds=0.01 * (2 ** (job.attempts - 1)))
                        self._metrics["jobs_retried"] += 1
                        time.sleep(0.01 * (2 ** (job.attempts - 1)))
                        continue
                    job.state = JobState.FAILED
                    job.current_stage = "failed"
                    job.progress_percent = 100
                    job.failure_reason = str(exc)
                    job.failure_class = "provider_failure"
                    job.completed_at = _utc_now()
                    job.updated_at = _utc_now()
                    self._queue.dead_letter(job.job_id, reason=str(exc))
                    self._metrics["jobs_failed"] += 1
                    raise
        finally:
            self._active_executions = max(0, self._active_executions - 1)
            job.estimated_duration_sec = max(1, int(time.perf_counter() - started_at))

    def queue_size(self) -> int:
        return self._queue.snapshot()["depth"]

    def get_job(self, job_id: str) -> RenderJob | None:
        return self.jobs.get(job_id)

    def cancel_job(self, job_id: str, *, reason: str = "user_cancelled") -> bool:
        job = self.jobs.get(job_id)
        if not job:
            return False
        canceled = self._queue.cancel(job_id, reason=reason)
        if canceled:
            job.state = JobState.CANCELED
            job.current_stage = "canceled"
            job.progress_percent = 100
            job.failure_reason = reason
            job.canceled_at = _utc_now()
            job.updated_at = _utc_now()
            self._metrics["jobs_canceled"] += 1
        return canceled

    def recover_stalled_jobs(self, *, stall_after_seconds: int = 120) -> int:
        return self._queue.recover_stalled(stall_after_seconds=stall_after_seconds)

    def queue_snapshot(self) -> dict[str, Any]:
        return self._queue.snapshot()

    def slo_snapshot(self) -> dict[str, Any]:
        completed_or_failed = self._metrics["jobs_completed"] + self._metrics["jobs_failed"]
        retry_ratio = (self._metrics["jobs_retried"] / max(1.0, completed_or_failed))
        queue_latency_ms_avg = self._metrics["queue_latency_ms_total"] / max(1.0, self._metrics["jobs_created"])
        failure_ratio = self._metrics["jobs_failed"] / max(1.0, completed_or_failed)
        slo = {
            "retry_ratio": round(retry_ratio, 4),
            "queue_latency_ms_avg": round(queue_latency_ms_avg, 3),
            "failure_ratio": round(failure_ratio, 4),
            "thresholds": {"retry_ratio_max": 0.3, "queue_latency_ms_avg_max": 2500.0, "failure_ratio_max": 0.2},
        }
        slo["status"] = (
            "green"
            if slo["retry_ratio"] <= slo["thresholds"]["retry_ratio_max"]
            and slo["queue_latency_ms_avg"] <= slo["thresholds"]["queue_latency_ms_avg_max"]
            and slo["failure_ratio"] <= slo["thresholds"]["failure_ratio_max"]
            else "degraded"
        )
        return slo

    @staticmethod
    def _classify_retry(exc: Exception) -> str:
        message = str(exc).lower()
        transient_markers = ("timeout", "rate", "temporary", "saturated")
        return "transient" if any(marker in message for marker in transient_markers) else "permanent"
