"""
AI Brain — central intelligence module that wires together the Decision Engine,
State Manager, and Metrics Tracker into a cohesive autonomous system.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from typing import Optional

from bots.ai_brain.tiers import Tier, TierConfig, get_tier_config, get_upgrade_path
from bots.ai_brain.tiers import (
    FEATURE_DECISION_ENGINE,
    FEATURE_PERSISTENT_MEMORY,
    FEATURE_REAL_METRICS,
    FEATURE_AUTO_SCALE,
    FEATURE_RECOVERY_BOT,
    FEATURE_FULL_AUTONOMY,
)
from bots.ai_brain.decision_engine import DecisionEngine
from bots.ai_brain.state_manager import StateManager
from bots.ai_brain.metrics_tracker import MetricsTracker


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class AIBrainError(Exception):
    """Base exception for AI Brain errors."""


class AIBrainTierError(AIBrainError):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# AI Brain
# ---------------------------------------------------------------------------

class AIBrain:
    """
    DreamCo AI Brain — autonomous decision-making, persistent memory, and
    real metrics tracking.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling which features are available.
    state_path : str, optional
        Custom path for the state JSON file.
    leads_path : str, optional
        Custom path for leads data file.
    deals_path : str, optional
        Custom path for deals data file.
    """

    def __init__(
        self,
        tier: Tier = Tier.FREE,
        state_path: Optional[str] = None,
        leads_path: Optional[str] = None,
        deals_path: Optional[str] = None,
    ) -> None:
        self.tier = tier
        self._config: TierConfig = get_tier_config(tier)
        self._decision_engine = DecisionEngine(
            auto_generate_bots=self._config.has_feature(FEATURE_FULL_AUTONOMY)
        )
        self._state_manager: Optional[StateManager] = None
        self._metrics_tracker: Optional[MetricsTracker] = None

        if self._config.has_feature(FEATURE_PERSISTENT_MEMORY):
            self._state_manager = StateManager(state_path=state_path)

        if self._config.has_feature(FEATURE_REAL_METRICS):
            self._metrics_tracker = MetricsTracker(
                leads_path=leads_path,
                deals_path=deals_path,
            )

    # ------------------------------------------------------------------
    # Tier enforcement
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        if not self._config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            hint = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)."
                if upgrade
                else ""
            )
            raise AIBrainTierError(
                f"Feature '{feature}' requires {self._config.name} tier.{hint}"
            )

    # ------------------------------------------------------------------
    # Core think/decide cycle
    # ------------------------------------------------------------------

    def think(self, override_metrics: Optional[dict] = None) -> dict:
        """
        Run a full think cycle: gather metrics, make a decision, persist state.

        Parameters
        ----------
        override_metrics : dict, optional
            Override real metrics with custom values (for testing).

        Returns
        -------
        dict
            Contains: decision, metrics, and optional bot_to_create.
        """
        self._require(FEATURE_DECISION_ENGINE)

        # Gather metrics
        if override_metrics:
            metrics = override_metrics
        elif self._metrics_tracker is not None:
            metrics = self._metrics_tracker.get_metrics()
        else:
            metrics = {"revenue": 0.0, "leads": 0}

        # Make decision
        decision = self._decision_engine.run(metrics)

        # Determine if bot creation is needed (ENTERPRISE)
        bot_to_create: Optional[str] = None
        if self._config.has_feature(FEATURE_FULL_AUTONOMY):
            bot_to_create = self._decision_engine.evaluate_for_bot_creation(
                metrics.get("revenue", 0)
            )

        # Persist state
        if self._state_manager is not None:
            self._state_manager.record_decision(decision)
            if metrics.get("revenue"):
                self._state_manager.set("total_revenue", metrics["revenue"])
            if metrics.get("leads"):
                self._state_manager.set("total_leads", metrics["leads"])

        result = {
            "decision": decision,
            "metrics": metrics,
            "bot_to_create": bot_to_create,
            "tier": self.tier.value,
        }

        return result

    # ------------------------------------------------------------------
    # State access
    # ------------------------------------------------------------------

    def get_state(self) -> dict:
        """Return the current persisted state."""
        if self._state_manager:
            return self._state_manager.get_full_state()
        return {}

    def get_decision_log(self) -> list[dict]:
        """Return the full decision history."""
        return self._decision_engine.get_decision_log()

    def get_metrics(self) -> dict:
        """Return current real metrics."""
        if self._metrics_tracker:
            return self._metrics_tracker.get_metrics()
        return {"revenue": 0.0, "leads": 0}

    # ------------------------------------------------------------------
    # Framework entry points
    # ------------------------------------------------------------------

    def run(self) -> str:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        result = self.think()
        return (
            f"🧠 AI Brain decision: {result['decision']}. "
            f"Revenue: ${result['metrics'].get('revenue', 0):.2f}. "
            f"Leads: {result['metrics'].get('leads', 0)}."
        )

    def process(self, payload: dict) -> dict:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        return self.think(override_metrics=payload.get("metrics"))
