"""
strategy_deployer.py — Deploys hybrid strategies across DreamCo bots.

Orchestrates the rollout of newly evolved AI strategies, managing
versioning, staging, and production promotion for bot deployments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class DeploymentRecord:
    """Records a single strategy deployment event."""

    deployment_id: str
    strategy_id: str
    target_bots: List[str]
    status: str  # "pending" | "deployed" | "rolled_back" | "failed"
    deployed_at: Optional[str] = None
    rolled_back_at: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class StrategyDeployer:
    """
    Deploys AI strategies to one or more DreamCo bots.

    Parameters
    ----------
    staging_mode : bool
        When ``True``, deployments are staged and must be explicitly
        promoted to production via :meth:`promote`.
    """

    def __init__(self, staging_mode: bool = False):
        self.staging_mode = staging_mode
        self._records: Dict[str, DeploymentRecord] = {}
        self._staged: List[str] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def deploy(
        self,
        deployment_id: str,
        strategy_id: str,
        target_bots: List[str],
        config: Optional[Dict[str, Any]] = None,
    ) -> DeploymentRecord:
        """
        Deploy *strategy_id* to *target_bots*.

        Parameters
        ----------
        deployment_id : str
            Unique identifier for this deployment.
        strategy_id : str
            Identifier of the strategy/pipeline to deploy.
        target_bots : list[str]
            Names of the bots that should receive the strategy.
        config : dict | None
            Optional deployment configuration.

        Returns
        -------
        DeploymentRecord
        """
        if deployment_id in self._records:
            raise ValueError(f"Deployment '{deployment_id}' already exists.")
        if not target_bots:
            raise ValueError("target_bots must not be empty.")

        record = DeploymentRecord(
            deployment_id=deployment_id,
            strategy_id=strategy_id,
            target_bots=list(target_bots),
            status="pending",
            config=config or {},
        )

        if self.staging_mode:
            self._staged.append(deployment_id)
        else:
            record.status = "deployed"
            record.deployed_at = datetime.now(timezone.utc).isoformat()

        self._records[deployment_id] = record
        return record

    def promote(self, deployment_id: str) -> DeploymentRecord:
        """Promote a staged deployment to production."""
        record = self._get(deployment_id)
        if record.status != "pending":
            raise ValueError(
                f"Deployment '{deployment_id}' is not pending "
                f"(status: {record.status})."
            )
        record.status = "deployed"
        record.deployed_at = datetime.now(timezone.utc).isoformat()
        if deployment_id in self._staged:
            self._staged.remove(deployment_id)
        return record

    def rollback(self, deployment_id: str) -> DeploymentRecord:
        """Roll back a previously deployed strategy."""
        record = self._get(deployment_id)
        if record.status not in ("deployed",):
            raise ValueError(
                f"Cannot roll back deployment with status '{record.status}'."
            )
        record.status = "rolled_back"
        record.rolled_back_at = datetime.now(timezone.utc).isoformat()
        return record

    def get_record(self, deployment_id: str) -> DeploymentRecord:
        """Retrieve a deployment record by ID."""
        return self._get(deployment_id)

    def list_deployments(self, status: Optional[str] = None) -> List[DeploymentRecord]:
        """Return all deployment records, optionally filtered by *status*."""
        records = list(self._records.values())
        if status is not None:
            records = [r for r in records if r.status == status]
        return records

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, deployment_id: str) -> DeploymentRecord:
        if deployment_id not in self._records:
            raise KeyError(f"Deployment '{deployment_id}' not found.")
        return self._records[deployment_id]
