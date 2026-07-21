"""
Sandbox testing layer for the DreamCo Global AI Learning System.

Simulates containerized execution of classified AI/ML methods and collects
performance metrics (accuracy, convergence rate, resource consumption).
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
import datetime
import uuid

from .tiers import Tier, TierConfig, get_tier_config, FEATURE_SANDBOX
from .classifier import ClassifiedMethod
from framework import GlobalAISourcesFlow  # noqa: F401


class SandboxStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SandboxTestResult:
    """Metrics produced by a single sandbox container run.

    Attributes
    ----------
    id : str
        Unique result identifier (UUID4).
    method_id : str
        ID of the ClassifiedMethod under test.
    status : SandboxStatus
        Final status of the container run.
    accuracy : float | None
        Achieved accuracy on the test workload (0.0–1.0).
    convergence_rate : float | None
        Convergence speed metric (0.0–1.0; higher is faster).
    resource_consumption : float | None
        Average CPU utilisation percentage (0–100).
    runtime_seconds : float | None
        Wall-clock execution time.
    container_id : str
        Simulated Docker/Kubernetes container identifier.
    started_at : datetime.datetime
        UTC timestamp when the container started.
    completed_at : datetime.datetime | None
        UTC timestamp when the container finished (None if still running).
    error : str | None
        Error message if status is FAILED.
    metadata : dict
        Additional run metadata.
    """

    id: str
    method_id: str
    status: SandboxStatus
    accuracy: Optional[float]
    convergence_rate: Optional[float]
    resource_consumption: Optional[float]
    runtime_seconds: Optional[float]
    container_id: str
    started_at: datetime.datetime
    completed_at: Optional[datetime.datetime]
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class SandboxTierError(Exception):
    """Raised when the current tier does not support sandbox testing."""


# ---------------------------------------------------------------------------
# Metric simulation tables keyed by LearningMethodType value
# ---------------------------------------------------------------------------

_METHOD_METRICS = {
    "supervised_learning":      (0.88, 0.80, 42.0, 18.5),
    "unsupervised_learning":    (0.74, 0.65, 55.0, 22.3),
    "reinforcement_learning":   (0.79, 0.58, 72.0, 45.1),
    "semi_supervised_learning": (0.83, 0.72, 48.0, 20.8),
    "self_supervised_learning": (0.85, 0.76, 51.0, 24.7),
    "transfer_learning":        (0.91, 0.88, 38.0, 15.2),
    "federated_learning":       (0.76, 0.62, 65.0, 38.4),
    "meta_learning":            (0.82, 0.70, 58.0, 31.9),
}

_DEFAULT_METRICS = (0.80, 0.70, 50.0, 25.0)


class SandboxTestingLayer:
    """Runs containerised sandbox tests for classified AI/ML methods.

    Parameters
    ----------
    tier : Tier
        Subscription tier (PRO and above enable sandbox testing).
    """

    def __init__(self, tier: Tier) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self._results: List[SandboxTestResult] = []
        self._active_containers: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_test(self, method: ClassifiedMethod) -> SandboxTestResult:
        """Run a containerised sandbox test for the given method.

        Parameters
        ----------
        method : ClassifiedMethod
            The classified learning method to benchmark.

        Returns
        -------
        SandboxTestResult
            Simulated performance metrics from the container run.

        Raises
        ------
        SandboxTierError
            If the current tier does not support sandbox testing or the
            container limit has been reached.
        """
        self._check_tier()
        self._check_container_limit()

        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        container_id = f"dreamco-sandbox-{uuid.uuid4().hex[:12]}"
        self._active_containers += 1

        acc, conv, cpu, runtime = _METHOD_METRICS.get(
            method.method_type.value, _DEFAULT_METRICS
        )

        # Add a small deterministic variation based on novelty_score
        variation = (method.novelty_score - 0.5) * 0.1
        accuracy = round(min(1.0, max(0.0, acc + variation)), 4)
        convergence_rate = round(min(1.0, max(0.0, conv + variation * 0.5)), 4)
        resource_consumption = round(max(0.0, cpu - variation * 20), 2)
        runtime_seconds = round(max(1.0, runtime - variation * 10), 2)

        completed_at = now + datetime.timedelta(seconds=runtime_seconds)
        result = SandboxTestResult(
            id=str(uuid.uuid4()),
            method_id=method.id,
            status=SandboxStatus.COMPLETED,
            accuracy=accuracy,
            convergence_rate=convergence_rate,
            resource_consumption=resource_consumption,
            runtime_seconds=runtime_seconds,
            container_id=container_id,
            started_at=now,
            completed_at=completed_at,
            metadata={
                "method_type": method.method_type.value,
                "novelty_score": method.novelty_score,
                "lab_name": method.lab_name,
                "kubernetes": self.config.has_feature("kubernetes_orchestration"),
            },
        )
        self._results.append(result)
        # Release container slot — simulated containers complete synchronously
        self._active_containers -= 1
        return result

    def run_batch(self, methods: List[ClassifiedMethod]) -> List[SandboxTestResult]:
        """Run sandbox tests for a list of methods.

        Parameters
        ----------
        methods : List[ClassifiedMethod]
            Methods to test.

        Returns
        -------
        List[SandboxTestResult]
            Results in the same order as the input list.
        """
        return [self.run_test(m) for m in methods]

    def get_results(self) -> List[SandboxTestResult]:
        """Return all sandbox test results produced so far."""
        return list(self._results)

    def get_stats(self) -> dict:
        """Return a summary of sandbox testing activity."""
        completed = [r for r in self._results if r.status == SandboxStatus.COMPLETED]
        avg_accuracy = (
            sum(r.accuracy for r in completed if r.accuracy is not None) / len(completed)
            if completed else 0.0
        )
        return {
            "total_runs": len(self._results),
            "completed": len(completed),
            "failed": len([r for r in self._results if r.status == SandboxStatus.FAILED]),
            "average_accuracy": round(avg_accuracy, 4),
            "active_containers": self._active_containers,
            "container_limit": self.config.sandbox_containers,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_tier(self) -> None:
        if not self.config.has_feature(FEATURE_SANDBOX):
            raise SandboxTierError(
                f"Sandbox testing is not available on the {self.config.name} "
                "tier. Upgrade to Pro or Enterprise to enable containerised "
                "testing."
            )

    def _check_container_limit(self) -> None:
        limit = self.config.sandbox_containers
        if limit is not None and self._active_containers >= limit:
            raise SandboxTierError(
                f"Container limit of {limit} reached on the "
                f"{self.config.name} tier. Upgrade to Enterprise for "
                "unlimited Kubernetes-managed containers."
            )
