# BuddyAI Metrics Collector
# Gathers profitability, computer usage, and task-completion metrics for
# the client dashboard.

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class TaskRecord:
    """Records a single completed task."""

    task_id: str
    task_name: str
    duration_seconds: float
    status: str  # "completed", "failed", "skipped"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "duration_seconds": self.duration_seconds,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ComputeSnapshot:
    """A point-in-time snapshot of compute resource usage."""

    cpu_percent: float       # 0–100
    memory_percent: float    # 0–100
    disk_read_mb: float
    disk_write_mb: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "disk_read_mb": self.disk_read_mb,
            "disk_write_mb": self.disk_write_mb,
            "timestamp": self.timestamp.isoformat(),
        }


class MetricsCollector:
    """
    Collects and aggregates metrics for a single client.

    Tracks:
    - Profitability (earnings over time)
    - Computer resource usage snapshots
    - Individual task records
    """

    def __init__(self, client_id: str) -> None:
        self.client_id = client_id
        self._tasks: List[TaskRecord] = []
        self._compute_snapshots: List[ComputeSnapshot] = []
        self._earnings_timeline: List[Dict] = []  # {"timestamp": ..., "amount": ...}

    # ------------------------------------------------------------------
    # Task tracking
    # ------------------------------------------------------------------

    def record_task(
        self,
        task_id: str,
        task_name: str,
        duration_seconds: float,
        status: str = "completed",
    ) -> TaskRecord:
        """Record a completed (or failed/skipped) task."""
        record = TaskRecord(
            task_id=task_id,
            task_name=task_name,
            duration_seconds=duration_seconds,
            status=status,
        )
        self._tasks.append(record)
        return record

    def get_tasks(self, status: Optional[str] = None) -> List[TaskRecord]:
        """Return task records, optionally filtered by status."""
        if status is None:
            return list(self._tasks)
        return [t for t in self._tasks if t.status == status]

    def tasks_completed_count(self) -> int:
        """Total number of successfully completed tasks."""
        return sum(1 for t in self._tasks if t.status == "completed")

    def average_task_duration(self) -> float:
        """Average duration (seconds) of completed tasks."""
        completed = [t for t in self._tasks if t.status == "completed"]
        if not completed:
            return 0.0
        return round(sum(t.duration_seconds for t in completed) / len(completed), 2)

    # ------------------------------------------------------------------
    # Compute usage
    # ------------------------------------------------------------------

    def record_compute_snapshot(
        self,
        cpu_percent: float,
        memory_percent: float,
        disk_read_mb: float = 0.0,
        disk_write_mb: float = 0.0,
    ) -> ComputeSnapshot:
        """Record a point-in-time compute usage snapshot."""
        snapshot = ComputeSnapshot(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_read_mb=disk_read_mb,
            disk_write_mb=disk_write_mb,
        )
        self._compute_snapshots.append(snapshot)
        return snapshot

    def get_compute_snapshots(self) -> List[ComputeSnapshot]:
        """Return all recorded compute snapshots."""
        return list(self._compute_snapshots)

    def average_cpu_usage(self) -> float:
        """Average CPU usage across all snapshots."""
        if not self._compute_snapshots:
            return 0.0
        return round(
            sum(s.cpu_percent for s in self._compute_snapshots)
            / len(self._compute_snapshots),
            2,
        )

    def average_memory_usage(self) -> float:
        """Average memory usage across all snapshots."""
        if not self._compute_snapshots:
            return 0.0
        return round(
            sum(s.memory_percent for s in self._compute_snapshots)
            / len(self._compute_snapshots),
            2,
        )

    # ------------------------------------------------------------------
    # Profitability
    # ------------------------------------------------------------------

    def record_earning(self, amount: float, timestamp: Optional[datetime] = None) -> None:
        """Log a client-side earnings event."""
        self._earnings_timeline.append(
            {
                "timestamp": (timestamp or datetime.now(timezone.utc)).isoformat(),
                "amount": amount,
            }
        )

    def total_earnings(self) -> float:
        """Cumulative client earnings recorded."""
        return round(sum(e["amount"] for e in self._earnings_timeline), 2)

    def earnings_timeline(self) -> List[Dict]:
        """Return the full earnings timeline (sorted by timestamp ascending)."""
        return sorted(self._earnings_timeline, key=lambda e: e["timestamp"])

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        """Return a summary dict suitable for display on the dashboard."""
        return {
            "client_id": self.client_id,
            "tasks_completed": self.tasks_completed_count(),
            "average_task_duration_seconds": self.average_task_duration(),
            "total_earnings": self.total_earnings(),
            "average_cpu_percent": self.average_cpu_usage(),
            "average_memory_percent": self.average_memory_usage(),
            "total_compute_snapshots": len(self._compute_snapshots),
        }
