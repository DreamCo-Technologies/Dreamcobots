"""
DreamCo Quantum Decision Bot

A Reality Optimization System that simulates thousands of outcome paths,
assigns probabilities, and collapses to the highest-return, lowest-risk
decision — enabling autonomous, intelligent money-making across all
DreamCo bot domains.

Inspired by quantum physics concepts:
  • Superposition          — every decision exists as all possibilities
  • Wave Function Collapse — the system picks the single best reality
  • Quantum Entanglement   — all bots update together instantly
  • Monte Carlo Simulation — thousands of realities tested before acting

Usage
-----
    from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

    bot = QuantumDecisionBot(tier=Tier.PRO)
    result = bot.decide({"base_profit": 10000, "risk": 5.0})
    opps = bot.scan_opportunities(top_n=5)
    plan = bot.route_bot("real_estate_bot", {"base_profit": 40000, "risk": 7})
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# GLOBAL AI SOURCES FLOW
from framework import GlobalAISourcesFlow  # noqa: F401

from bots.quantum_decision_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_SIMULATION,
    FEATURE_QUANTUM_DECISION,
    FEATURE_PROBABILITY_MODEL,
    FEATURE_DIMENSION_MAPPER,
    FEATURE_BOT_ROUTER,
    FEATURE_MONEY_ENGINE,
    FEATURE_HYPER_SIMULATION,
    FEATURE_SELF_IMPROVING_AI,
    FEATURE_GOD_MODE,
    FEATURE_AUTONOMOUS_EXECUTION,
    FEATURE_MULTI_PATH_TRACKER,
)
from bots.quantum_decision_bot.probability_model import ProbabilityModel
from bots.quantum_decision_bot.simulation_engine import run_simulations, summarise_outcomes
from bots.quantum_decision_bot.quantum_engine import QuantumEngine
from bots.quantum_decision_bot.dimension_mapper import DimensionMapper
from bots.quantum_decision_bot.bot_router import BotRouter
from bots.quantum_decision_bot.money_engine import MoneyEngine

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class QuantumDecisionBotError(Exception):
    """Base exception for QuantumDecisionBot errors."""


class QuantumTierError(QuantumDecisionBotError):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# QuantumDecisionBot
# ---------------------------------------------------------------------------

class QuantumDecisionBot:
    """
    DreamCo QuantumOS — Reality Optimization System.

    Instantiate with a tier to gain access to the corresponding feature set.

    Parameters
    ----------
    tier : Tier
        Subscription tier: FREE / PRO / ENTERPRISE.
    operator_name : str
        Display name for the operator.
    """

    def __init__(
        self,
        tier: Tier = Tier.FREE,
        operator_name: str = "DreamCo Operator",
    ) -> None:
        self.tier = tier
        self.operator_name = operator_name
        self._config: TierConfig = get_tier_config(tier)
        self._created_at = datetime.now(timezone.utc).isoformat()

        # Core engines — always instantiated, access-controlled at method level
        self.probability_model = ProbabilityModel()
        self.quantum_engine = QuantumEngine(
            probability_model=self.probability_model,
            simulation_runs=self._config.max_simulation_runs,
        )
        self.dimension_mapper = DimensionMapper()
        self.bot_router = BotRouter(engine=self.quantum_engine)
        self.money_engine = MoneyEngine(engine=self.quantum_engine)

        # Multi-path tracker — tracks parallel live paths
        self._active_paths: List[dict] = []

    # ------------------------------------------------------------------
    # Tier utilities
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        if not self._config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            msg = f"Feature '{feature}' is not available on the {self._config.name} tier."
            if upgrade:
                msg += f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)."
            raise QuantumTierError(msg)

    def can_access(self, feature: str) -> bool:
        return self._config.has_feature(feature)

    def get_tier_info(self) -> dict:
        return {
            "tier": self.tier.value,
            "name": self._config.name,
            "price_usd_monthly": self._config.price_usd_monthly,
            "max_simulation_runs": self._config.max_simulation_runs,
            "max_active_paths": self._config.max_active_paths,
            "features": self._config.features,
        }

    # ------------------------------------------------------------------
    # Core quantum decision
    # ------------------------------------------------------------------

    def decide(self, context: dict) -> dict:
        """
        Run the quantum decision engine on *context* and return the best
        reality path with alternatives and risk warning.

        Available on: FREE, PRO, ENTERPRISE.
        """
        self._require(FEATURE_QUANTUM_DECISION)
        result = self.quantum_engine.decide(context)

        # Track active paths (PRO+)
        if self.can_access(FEATURE_MULTI_PATH_TRACKER):
            max_paths = self._config.max_active_paths
            self._active_paths.append(result["best_path"])
            if len(self._active_paths) > max_paths:
                self._active_paths = self._active_paths[-max_paths:]

        return result

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------

    def simulate(self, scenario: dict, runs: Optional[int] = None) -> dict:
        """
        Run a Monte Carlo simulation for *scenario* and return a summary.

        Available on: FREE (10 runs max), PRO (1000 runs max),
        ENTERPRISE (10 000 runs max).
        """
        self._require(FEATURE_SIMULATION)
        effective_runs = min(
            runs or self._config.max_simulation_runs,
            self._config.max_simulation_runs,
        )
        outcomes = run_simulations(scenario, runs=effective_runs)
        return summarise_outcomes(outcomes)

    # ------------------------------------------------------------------
    # Dimension mapping
    # ------------------------------------------------------------------

    def map_dimensions(self, context: dict) -> dict:
        """
        Map a decision context to its time/capital/risk/scale dimensions.

        Available on: PRO, ENTERPRISE.
        """
        self._require(FEATURE_DIMENSION_MAPPER)
        profile = self.dimension_mapper.map(context)
        optimality = self.dimension_mapper.optimality_score(profile)
        return {"dimensions": profile, "optimality_score": optimality}

    # ------------------------------------------------------------------
    # Bot router (entangled network)
    # ------------------------------------------------------------------

    def route_bot(self, bot_name: str, context: dict) -> dict:
        """
        Route *bot_name*'s decision through the Quantum Engine and return
        a tailored action plan.

        Available on: PRO, ENTERPRISE.
        """
        self._require(FEATURE_BOT_ROUTER)
        return self.bot_router.route(bot_name, context)

    def route_all_bots(self, bot_contexts: Dict[str, dict]) -> List[dict]:
        """
        Route multiple bots simultaneously — simulating entangled updates.

        Available on: PRO, ENTERPRISE.
        """
        self._require(FEATURE_BOT_ROUTER)
        return self.bot_router.route_all(bot_contexts)

    def network_status(self) -> dict:
        """
        Return the current state of the entangled bot network.

        Available on: PRO, ENTERPRISE.
        """
        self._require(FEATURE_BOT_ROUTER)
        return self.bot_router.network_status()

    # ------------------------------------------------------------------
    # Money engine (autonomous scanning)
    # ------------------------------------------------------------------

    def scan_opportunities(
        self,
        filter_type: Optional[str] = None,
        top_n: int = 5,
    ) -> dict:
        """
        Autonomously scan income opportunities and return quantum-ranked list.

        Available on: PRO, ENTERPRISE.
        """
        self._require(FEATURE_MONEY_ENGINE)
        return self.money_engine.scan(filter_type=filter_type, top_n=top_n)

    def execute_plan(self, opportunity: dict) -> dict:
        """
        Generate a step-by-step execution plan for a specific opportunity.

        Available on: PRO, ENTERPRISE.
        """
        self._require(FEATURE_MONEY_ENGINE)
        return self.money_engine.execute_plan(opportunity)

    def add_opportunity(self, opportunity: dict) -> None:
        """
        Register a custom income opportunity in the money engine scanner.

        Available on: PRO, ENTERPRISE.
        """
        self._require(FEATURE_MONEY_ENGINE)
        self.money_engine.add_opportunity(opportunity)

    # ------------------------------------------------------------------
    # Self-improving AI (ENTERPRISE)
    # ------------------------------------------------------------------

    def learn(
        self, scenario_name: str, predicted_score: float, actual_profit: float
    ) -> dict:
        """
        Teach the probability model from a real-world outcome.

        Available on: ENTERPRISE.
        """
        self._require(FEATURE_SELF_IMPROVING_AI)
        return self.probability_model.learn(scenario_name, predicted_score, actual_profit)

    def get_model_weights(self) -> dict:
        """
        Return the current probability model weights.

        Available on: ENTERPRISE.
        """
        self._require(FEATURE_SELF_IMPROVING_AI)
        return self.probability_model.get_weights()

    # ------------------------------------------------------------------
    # Multi-path tracker
    # ------------------------------------------------------------------

    def get_active_paths(self) -> List[dict]:
        """
        Return currently tracked parallel decision paths.

        Available on: PRO, ENTERPRISE.
        """
        self._require(FEATURE_MULTI_PATH_TRACKER)
        return list(self._active_paths)

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def dashboard(self) -> dict:
        """
        Return a full snapshot of the QuantumOS state.

        Available on: FREE, PRO, ENTERPRISE.
        """
        self._require(FEATURE_QUANTUM_DECISION)
        history = self.quantum_engine.get_path_history()
        best_ever = (
            max(history, key=lambda p: p["score"]) if history else None
        )
        return {
            "title": "DreamCo QuantumOS",
            "operator": self.operator_name,
            "tier": self.tier.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "simulation_runs": self._config.max_simulation_runs,
            "paths_evaluated": len(history),
            "best_path_ever": best_ever,
            "active_paths": len(self._active_paths),
            "model_weights": self.probability_model.get_weights(),
            "learning_iterations": self.probability_model.get_history_count(),
        }

    # ------------------------------------------------------------------
    # Chat interface (BuddyAI-compatible)
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """
        Process a natural-language command for the QuantumOS.

        Returns a JSON-serialisable response dict compatible with BuddyAI
        routing.
        """
        msg = message.lower().strip()

        if any(k in msg for k in ("dashboard", "status", "overview")):
            return {"message": "QuantumOS dashboard loaded.", "data": self.dashboard()}

        if any(k in msg for k in ("decide", "decision", "best path", "quantum")):
            try:
                result = self.decide({})
                return {"message": "Quantum decision complete.", "data": result}
            except QuantumTierError as e:
                return {"message": str(e)}

        if any(k in msg for k in ("simulate", "simulation", "monte carlo")):
            try:
                result = self.simulate({"base_profit": 10_000, "risk": 5.0})
                return {"message": "Simulation complete.", "data": result}
            except QuantumTierError as e:
                return {"message": str(e)}

        if any(k in msg for k in ("opportunity", "opportunities", "money", "scan")):
            try:
                result = self.scan_opportunities()
                return {"message": "Opportunity scan complete.", "data": result}
            except QuantumTierError as e:
                return {"message": str(e)}

        if any(k in msg for k in ("tier", "upgrade", "plan")):
            return {"message": "Tier info retrieved.", "data": self.get_tier_info()}

        if any(k in msg for k in ("network", "bots", "entangle")):
            try:
                return {"message": "Bot network status.", "data": self.network_status()}
            except QuantumTierError as e:
                return {"message": str(e)}

        return {
            "message": (
                "DreamCo QuantumOS online. Commands: dashboard | decide | "
                "simulate | opportunities | tier | network"
            ),
            "tier": self.tier.value,
            "operator": self.operator_name,
        }

    # ------------------------------------------------------------------
    # process() — framework compatibility
    # ------------------------------------------------------------------

    def process(self, payload: dict) -> dict:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        command = payload.get("command", "")
        return self.chat(command)


# ---------------------------------------------------------------------------
# Module-level run() — DreamCo OS orchestrator interface
# ---------------------------------------------------------------------------

def run() -> Dict[str, Any]:
    """
    Module-level entry point required by the DreamCo OS orchestrator.

    Runs a default quantum scan and returns the top opportunity result.
    """
    bot = QuantumDecisionBot(tier=Tier.PRO)
    scan = bot.scan_opportunities(top_n=3)
    top = scan.get("top_opportunity") or {}
    return {
        "status": "success",
        "leads": scan.get("total_scanned", 0),
        "leads_generated": scan.get("total_scanned", 0),
        "revenue": int(top.get("base_profit", 0)),
        "top_opportunity": top.get("name", ""),
        "quantum_score": round(top.get("quantum_score", 0.0), 2),
        "ranked_opportunities": [
            {"name": o["name"], "score": round(o["quantum_score"], 2)}
            for o in scan.get("ranked_opportunities", [])
        ],
    }
