"""
Deployment orchestration for the DreamCo Global AI Learning System.

Simulates Kubernetes rolling updates and rollbacks for deploying hybrid
AI strategies to DreamCo bot applications.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
import datetime
import uuid

from .tiers import Tier, TierConfig, get_tier_config, FEATURE_DEPLOYMENT
from .hybrid_engine import HybridStrategy
from framework import GlobalAISourcesFlow  # noqa: F401


class DeploymentStatus(Enum):
    PENDING = "pending"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    ROLLING_UPDATE = "rolling_update"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class BotApplication(Enum):
    REAL_ESTATE = "real_estate_valuation"
    TRADING = "stock_trading"
    CUSTOMER_SUPPORT = "customer_support"
    FRAUD_DETECTION = "fraud_detection"
    ANALYTICS = "business_analytics"


@dataclass
class Deployment:
    """A deployed hybrid strategy running inside a bot application.

    Attributes
    ----------
    id : str
        Unique deployment identifier (UUID4).
    strategy_id : str
        ID of the HybridStrategy being deployed.
    bot_application : BotApplication
        Target DreamCo bot application.
    status : DeploymentStatus
        Current deployment status.
    version : str
        Semantic version string (derived from strategy generation).
    kubernetes_namespace : str
        Kubernetes namespace (simulated).
    replicas : int
        Number of running replicas.
    deployed_at : datetime.datetime | None
        UTC timestamp when the deployment became active.
    metrics : dict
        Live performance metrics snapshot.
    """

    id: str
    strategy_id: str
    bot_application: BotApplication
    status: DeploymentStatus
    version: str
    kubernetes_namespace: str
    replicas: int
    deployed_at: Optional[datetime.datetime]
    metrics: dict = field(default_factory=dict)


class DeploymentTierError(Exception):
    """Raised when the current tier does not support deployment orchestration."""


class DeploymentNotFoundError(Exception):
    """Raised when a requested deployment ID does not exist."""


_APP_REPLICAS = {
    BotApplication.REAL_ESTATE: 3,
    BotApplication.TRADING: 5,
    BotApplication.CUSTOMER_SUPPORT: 4,
    BotApplication.FRAUD_DETECTION: 6,
    BotApplication.ANALYTICS: 2,
}

_APP_NAMESPACES = {
    BotApplication.REAL_ESTATE: "dreamco-realestate",
    BotApplication.TRADING: "dreamco-trading",
    BotApplication.CUSTOMER_SUPPORT: "dreamco-support",
    BotApplication.FRAUD_DETECTION: "dreamco-fraud",
    BotApplication.ANALYTICS: "dreamco-analytics",
}


def _make_version(generation: int) -> str:
    major = 1 + generation // 10
    minor = generation % 10
    return f"{major}.{minor}.0"


class DeploymentOrchestrator:
    """Deploys hybrid strategies to DreamCo bot applications via Kubernetes.

    Parameters
    ----------
    tier : Tier
        Subscription tier (PRO and above enable deployment orchestration).
    """

    def __init__(self, tier: Tier) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self._deployments: dict = {}  # id -> Deployment

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def deploy(
        self,
        strategy: HybridStrategy,
        application: BotApplication,
    ) -> Deployment:
        """Deploy a hybrid strategy to the target bot application.

        Simulates a Kubernetes rolling update deployment.

        Parameters
        ----------
        strategy : HybridStrategy
            The strategy to deploy.
        application : BotApplication
            The target bot application.

        Returns
        -------
        Deployment
            The active deployment record.

        Raises
        ------
        DeploymentTierError
            If the current tier does not support deployment.
        """
        self._check_tier()
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        deployment = Deployment(
            id=str(uuid.uuid4()),
            strategy_id=strategy.id,
            bot_application=application,
            status=DeploymentStatus.DEPLOYED,
            version=_make_version(strategy.generation),
            kubernetes_namespace=_APP_NAMESPACES[application],
            replicas=_APP_REPLICAS[application],
            deployed_at=now,
            metrics={
                "fitness_score": strategy.fitness_score,
                "accuracy": strategy.accuracy,
                "convergence_rate": strategy.convergence_rate,
                "resource_consumption": strategy.resource_consumption,
                "generation": strategy.generation,
            },
        )
        self._deployments[deployment.id] = deployment
        return deployment

    def rolling_update(
        self,
        deployment_id: str,
        new_strategy: HybridStrategy,
    ) -> Deployment:
        """Perform a zero-downtime rolling update on an existing deployment.

        Parameters
        ----------
        deployment_id : str
            ID of the deployment to update.
        new_strategy : HybridStrategy
            The new strategy to roll out.

        Returns
        -------
        Deployment
            The updated deployment record.

        Raises
        ------
        DeploymentNotFoundError
            If the deployment ID does not exist.
        DeploymentTierError
            If the current tier does not support deployment.
        """
        self._check_tier()
        deployment = self._get(deployment_id)
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        deployment.strategy_id = new_strategy.id
        deployment.status = DeploymentStatus.DEPLOYED
        deployment.version = _make_version(new_strategy.generation)
        deployment.deployed_at = now
        deployment.metrics.update({
            "fitness_score": new_strategy.fitness_score,
            "accuracy": new_strategy.accuracy,
            "convergence_rate": new_strategy.convergence_rate,
            "resource_consumption": new_strategy.resource_consumption,
            "generation": new_strategy.generation,
            "last_rolling_update": now.isoformat(),
        })
        return deployment

    def rollback(self, deployment_id: str) -> Deployment:
        """Roll back a deployment to the ROLLED_BACK status.

        Parameters
        ----------
        deployment_id : str
            ID of the deployment to roll back.

        Returns
        -------
        Deployment
            The rolled-back deployment record.

        Raises
        ------
        DeploymentNotFoundError
            If the deployment ID does not exist.
        DeploymentTierError
            If the current tier does not support deployment.
        """
        self._check_tier()
        deployment = self._get(deployment_id)
        deployment.status = DeploymentStatus.ROLLED_BACK
        rolled_back_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat()
        deployment.metrics["rolled_back_at"] = rolled_back_at
        return deployment

    def get_deployments(self) -> List[Deployment]:
        """Return all deployment records."""
        return list(self._deployments.values())

    def get_stats(self) -> dict:
        """Return a summary of deployment activity."""
        status_counts: dict = {}
        for d in self._deployments.values():
            key = d.status.value
            status_counts[key] = status_counts.get(key, 0) + 1
        return {
            "total_deployments": len(self._deployments),
            "by_status": status_counts,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_tier(self) -> None:
        if not self.config.has_feature(FEATURE_DEPLOYMENT):
            raise DeploymentTierError(
                f"Deployment orchestration is not available on the "
                f"{self.config.name} tier. Upgrade to Pro or Enterprise."
            )

    def _get(self, deployment_id: str) -> Deployment:
        if deployment_id not in self._deployments:
            raise DeploymentNotFoundError(
                f"Deployment '{deployment_id}' not found."
            )
        return self._deployments[deployment_id]
