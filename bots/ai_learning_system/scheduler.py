"""
Automation scheduler for the DreamCo Global AI Learning System.

Manages recurring jobs that drive continuous ingestion, re-classification,
re-ranking, and strategy evolution in the background.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
import datetime
import uuid

from .tiers import Tier, TierConfig, get_tier_config, FEATURE_SCHEDULER
from framework import GlobalAISourcesFlow  # noqa: F401


class ScheduleFrequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class JobStatus(Enum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ScheduledJob:
    """A recurring automation job.

    Attributes
    ----------
    id : str
        Unique job identifier (UUID4).
    name : str
        Human-readable job name.
    frequency : ScheduleFrequency
        How often the job should recur.
    last_run : datetime.datetime | None
        UTC timestamp of the most recent execution.
    next_run : datetime.datetime
        UTC timestamp of the next scheduled execution.
    status : JobStatus
        Current job status.
    run_count : int
        Total number of successful executions.
    metadata : dict
        Extra configuration for the job.
    """

    id: str
    name: str
    frequency: ScheduleFrequency
    last_run: Optional[datetime.datetime]
    next_run: datetime.datetime
    status: JobStatus
    run_count: int = 0
    metadata: dict = field(default_factory=dict)


class SchedulerTierError(Exception):
    """Raised when the current tier does not support the automation scheduler."""


class JobNotFoundError(Exception):
    """Raised when a requested job ID does not exist."""


_FREQUENCY_DELTAS = {
    ScheduleFrequency.DAILY: datetime.timedelta(days=1),
    ScheduleFrequency.WEEKLY: datetime.timedelta(weeks=1),
    ScheduleFrequency.MONTHLY: datetime.timedelta(days=30),
}


class AutomationScheduler:
    """Schedules and runs recurring automation jobs.

    Parameters
    ----------
    tier : Tier
        Subscription tier (FREE and above support scheduling).
    """

    def __init__(self, tier: Tier) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self._jobs: dict = {}  # id -> ScheduledJob

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def schedule_job(
        self,
        name: str,
        frequency: ScheduleFrequency,
    ) -> ScheduledJob:
        """Register a new recurring automation job.

        Parameters
        ----------
        name : str
            Human-readable job name.
        frequency : ScheduleFrequency
            Recurrence interval.

        Returns
        -------
        ScheduledJob
            The newly created job record.

        Raises
        ------
        SchedulerTierError
            If the current tier does not support the scheduler.
        """
        self._check_tier()
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        next_run = now + _FREQUENCY_DELTAS[frequency]
        job = ScheduledJob(
            id=str(uuid.uuid4()),
            name=name,
            frequency=frequency,
            last_run=None,
            next_run=next_run,
            status=JobStatus.SCHEDULED,
            metadata={"created_at": now.isoformat()},
        )
        self._jobs[job.id] = job
        return job

    def run_job(self, job_id: str) -> ScheduledJob:
        """Simulate executing a scheduled job.

        Updates last_run, next_run, run_count, and status.

        Parameters
        ----------
        job_id : str
            ID of the job to execute.

        Returns
        -------
        ScheduledJob
            The updated job record.

        Raises
        ------
        JobNotFoundError
            If the job ID does not exist.
        SchedulerTierError
            If the current tier does not support the scheduler.
        """
        self._check_tier()
        job = self._get(job_id)
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        job.status = JobStatus.COMPLETED
        job.last_run = now
        job.next_run = now + _FREQUENCY_DELTAS[job.frequency]
        job.run_count += 1
        job.metadata["last_run_at"] = now.isoformat()
        return job

    def get_jobs(self) -> List[ScheduledJob]:
        """Return all registered jobs."""
        return list(self._jobs.values())

    def get_due_jobs(
        self,
        as_of: Optional[datetime.datetime] = None,
    ) -> List[ScheduledJob]:
        """Return all jobs whose next_run is on or before *as_of*.

        Parameters
        ----------
        as_of : datetime.datetime | None
            Reference time. Defaults to ``datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)``.

        Returns
        -------
        List[ScheduledJob]
            Jobs that are due to run.
        """
        if as_of is None:
            as_of = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        return [
            j for j in self._jobs.values()
            if j.next_run <= as_of and j.status != JobStatus.RUNNING
        ]

    def get_stats(self) -> dict:
        """Return a summary of scheduler activity."""
        status_counts: dict = {}
        for j in self._jobs.values():
            key = j.status.value
            status_counts[key] = status_counts.get(key, 0) + 1
        total_runs = sum(j.run_count for j in self._jobs.values())
        return {
            "total_jobs": len(self._jobs),
            "total_runs": total_runs,
            "by_status": status_counts,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_tier(self) -> None:
        if not self.config.has_feature(FEATURE_SCHEDULER):
            raise SchedulerTierError(
                f"The automation scheduler is not available on the "
                f"{self.config.name} tier. Please upgrade."
            )

    def _get(self, job_id: str) -> ScheduledJob:
        if job_id not in self._jobs:
            raise JobNotFoundError(f"Job '{job_id}' not found.")
        return self._jobs[job_id]
