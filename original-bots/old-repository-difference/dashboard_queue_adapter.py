from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class DashboardQueueAdapter:
    queue_name: str = "dashboard-governance"
    jobs: list[dict[str, Any]] = field(default_factory=list)

    def enqueue(self, job_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        job = {
            "id": f"{self.queue_name}-{len(self.jobs) + 1}",
            "job_type": job_type,
            "payload": payload,
            "status": "queued",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.jobs.append(job)
        return job

    def mark_running(self, job_id: str) -> dict[str, Any] | None:
        return self._set_status(job_id, "running")

    def mark_completed(self, job_id: str) -> dict[str, Any] | None:
        return self._set_status(job_id, "completed")

    def _set_status(self, job_id: str, status: str) -> dict[str, Any] | None:
        for job in self.jobs:
            if job["id"] == job_id:
                job["status"] = status
                job["updated_at"] = datetime.now(timezone.utc).isoformat()
                return job
        return None

    def snapshot(self) -> dict[str, Any]:
        counts = {"queued": 0, "running": 0, "completed": 0}
        for job in self.jobs:
            status = job.get("status", "queued")
            counts[status] = counts.get(status, 0) + 1
        return {
            "queue_name": self.queue_name,
            "job_counts": counts,
            "jobs": list(self.jobs),
        }
