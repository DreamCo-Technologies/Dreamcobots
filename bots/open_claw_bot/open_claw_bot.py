"""
Open Claw Bot — Main Entry Point

A specialised AI-powered bot that generates Open Claw strategies for
bots and clients within the DreamCobots ecosystem.

Core capabilities:
  • Strategy Engine  — generates ranked strategies (aggressive, balanced,
                        conservative, scalping, long-term, arbitrage, etc.)
  • AI Model Hub     — trend prediction, risk classification, signal
                        generation, ensemble ranking, NLP advice
  • Client Manager   — per-client profiles, preferences, and ROI tracking
  • Scenario Sim     — Monte-Carlo-style scenario simulation
  • Bot Strategies   — dedicated strategy generation for DreamCobots bots

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.open_claw_bot import OpenClawBot, Tier

    bot = OpenClawBot(tier=Tier.PRO)

    # Add a client
    client = bot.add_client("Alice", "alice@example.com")

    # Generate a strategy for the client
    strategy = bot.generate_strategy(
        name="Alice Growth Strategy",
        strategy_type="balanced",
        client_id=client.client_id,
    )

    # Chat interface
    response = bot.chat("Generate an aggressive strategy for crypto trading")
    print(response["message"])
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401

from bots.open_claw_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_STRATEGY_ENGINE,
    FEATURE_AI_MODELS,
    FEATURE_CLIENT_MANAGER,
    FEATURE_DATA_ANALYSIS,
    FEATURE_CUSTOM_RULES,
    FEATURE_ML_ENSEMBLE,
    FEATURE_REALTIME_SIGNALS,
    FEATURE_BOT_STRATEGIES,
    FEATURE_SCENARIO_SIM,
    FEATURE_ADVANCED_ML,
)
from bots.open_claw_bot.strategy_engine import (
    StrategyEngine,
    Strategy,
    StrategyType,
    StrategyStatus,
    RiskLevel,
    DataPoint,
    STRATEGY_RULE_TEMPLATES,
)
from bots.open_claw_bot.ai_models import (
    AIModelHub,
    AIModel,
    ModelFamily,
    InferenceResult,
)
from bots.open_claw_bot.client_manager import (
    ClientManager,
    ClientProfile,
    ClientPreferences,
    ClientStatus,
    GoalType,
)
from typing import Optional


class OpenClawBotError(Exception):
    """Raised when an Open Claw Bot operation fails."""


class OpenClawBotTierError(OpenClawBotError):
    """Raised when a feature is not available on the current tier."""


# Mapping of string aliases to StrategyType enum values for the chat interface
_STRATEGY_TYPE_ALIASES: dict = {
    "aggressive": StrategyType.AGGRESSIVE,
    "balanced": StrategyType.BALANCED,
    "conservative": StrategyType.CONSERVATIVE,
    "scalping": StrategyType.SCALPING,
    "scalp": StrategyType.SCALPING,
    "long_term": StrategyType.LONG_TERM,
    "long-term": StrategyType.LONG_TERM,
    "long term": StrategyType.LONG_TERM,
    "arbitrage": StrategyType.ARBITRAGE,
    "momentum": StrategyType.MOMENTUM,
    "mean_reversion": StrategyType.MEAN_REVERSION,
    "mean reversion": StrategyType.MEAN_REVERSION,
}

_RISK_ALIASES: dict = {
    "low": RiskLevel.LOW,
    "medium": RiskLevel.MEDIUM,
    "high": RiskLevel.HIGH,
    "extreme": RiskLevel.EXTREME,
}


class OpenClawBot:
    """
    Open Claw Bot — AI-driven strategy generation bot.

    Generates, ranks, and manages Open Claw strategies for DreamCobots
    bots and human clients using a suite of AI/ML models.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling client limits and feature access.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)

        # Core subsystems
        self.strategy_engine = StrategyEngine()
        self.ai_models = AIModelHub(load_defaults=True)
        self.client_manager = ClientManager(max_clients=self.config.max_clients)

        self._strategy_counter: int = 0

    # ------------------------------------------------------------------
    # Feature gate
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            raise OpenClawBotTierError(
                f"Feature '{feature}' is not available on the {self.config.name} tier. "
                f"Upgrade to access it."
            )

    # ------------------------------------------------------------------
    # Client management (delegated)
    # ------------------------------------------------------------------

    def add_client(
        self,
        name: str,
        email: str,
        max_risk_pct: float = 5.0,
        preferred_types: Optional[list] = None,
        goals: Optional[list] = None,
    ) -> ClientProfile:
        """Register a new client."""
        self._require_feature(FEATURE_CLIENT_MANAGER)
        prefs = ClientPreferences(
            max_risk_pct=max_risk_pct,
            preferred_strategy_types=list(preferred_types or []),
            goals=list(goals or []),
        )
        return self.client_manager.add_client(name, email, preferences=prefs)

    def get_client(self, client_id: str) -> ClientProfile:
        return self.client_manager.get_client(client_id)

    def list_clients(self) -> list[ClientProfile]:
        return self.client_manager.list_clients()

    # ------------------------------------------------------------------
    # Strategy generation
    # ------------------------------------------------------------------

    def generate_strategy(
        self,
        name: str,
        strategy_type: str = "balanced",
        risk_level: str = "medium",
        client_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        custom_rules: Optional[list] = None,
        custom_params: Optional[dict] = None,
    ) -> Strategy:
        """
        Generate an Open Claw strategy.

        Parameters
        ----------
        name : str
            Human-readable strategy name.
        strategy_type : str
            One of: aggressive, balanced, conservative, scalping,
            long_term, arbitrage, momentum, mean_reversion.
        risk_level : str
            One of: low, medium, high, extreme.
        client_id : str | None
            Attach to a registered client.
        bot_id : str | None
            Attach to a specific DreamCobots bot.
        custom_rules : list | None
            Extra rules to prepend (PRO+ only).
        custom_params : dict | None
            Additional parameters stored with the strategy.
        """
        self._require_feature(FEATURE_STRATEGY_ENGINE)

        stype = _STRATEGY_TYPE_ALIASES.get(strategy_type.lower(), StrategyType.BALANCED)
        rlevel = _RISK_ALIASES.get(risk_level.lower(), RiskLevel.MEDIUM)

        if custom_rules:
            self._require_feature(FEATURE_CUSTOM_RULES)

        if client_id is not None:
            client = self.client_manager.get_client(client_id)
            # Merge client custom rules into the strategy
            if client.preferences.custom_rules and not custom_rules:
                custom_rules = client.preferences.custom_rules

        strategy = self.strategy_engine.generate_strategy(
            name=name,
            strategy_type=stype,
            risk_level=rlevel,
            custom_rules=custom_rules,
            custom_params=custom_params,
            client_id=client_id,
            bot_id=bot_id,
        )

        if client_id is not None:
            self.client_manager.assign_strategy(client_id, strategy.strategy_id)

        return strategy

    def rank_strategies(
        self,
        client_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        use_ml: bool = False,
    ) -> list[Strategy]:
        """
        Return strategies ranked by expected value.

        Set *use_ml=True* to apply the ensemble ML ranker (PRO+).
        """
        strategies = self.strategy_engine.rank_strategies(
            client_id=client_id, bot_id=bot_id
        )
        if use_ml and strategies:
            self._require_feature(FEATURE_ML_ENSEMBLE)
            scores = [s.to_dict() for s in strategies]
            result = self.ai_models.rank_strategies_ml(scores)
            ranked_dicts = result.prediction.get("ranked_strategies", scores)
            id_order = [d["strategy_id"] for d in ranked_dicts]
            strat_map = {s.strategy_id: s for s in strategies}
            strategies = [strat_map[sid] for sid in id_order if sid in strat_map]
        return strategies

    # ------------------------------------------------------------------
    # AI model inference
    # ------------------------------------------------------------------

    def analyse_trend(self, data_series: list[float]) -> InferenceResult:
        """Use the trend predictor to forecast direction."""
        self._require_feature(FEATURE_AI_MODELS)
        return self.ai_models.predict_trend(data_series)

    def assess_risk(self, features: dict) -> InferenceResult:
        """Classify the risk level for a feature set."""
        self._require_feature(FEATURE_AI_MODELS)
        return self.ai_models.classify_risk(features)

    def get_signals(self, market_data: dict) -> InferenceResult:
        """Generate entry/exit trading signals."""
        self._require_feature(FEATURE_REALTIME_SIGNALS)
        return self.ai_models.generate_signals(market_data)

    def nlp_advise(self, query: str) -> InferenceResult:
        """Get a natural-language strategy recommendation."""
        self._require_feature(FEATURE_AI_MODELS)
        return self.ai_models.advise_nlp(query)

    # ------------------------------------------------------------------
    # Scenario simulation
    # ------------------------------------------------------------------

    def simulate_scenario(
        self, strategy_id: str, market_conditions: dict
    ) -> dict:
        """Simulate a strategy under given market conditions."""
        self._require_feature(FEATURE_SCENARIO_SIM)
        return self.strategy_engine.simulate_scenario(strategy_id, market_conditions)

    # ------------------------------------------------------------------
    # Data ingestion
    # ------------------------------------------------------------------

    def ingest_data(self, metric: str, value: float, source: str = "", timestamp: str = "") -> None:
        """Feed a data point into the strategy engine analysis buffer."""
        self._require_feature(FEATURE_DATA_ANALYSIS)
        dp = DataPoint(
            timestamp=timestamp or "now",
            metric=metric,
            value=value,
            source=source,
        )
        self.strategy_engine.ingest_data(dp)

    def get_data_stats(self) -> dict:
        """Return stats on the ingested data buffer."""
        self._require_feature(FEATURE_DATA_ANALYSIS)
        return self.strategy_engine.get_buffer_stats()

    # ------------------------------------------------------------------
    # System overview
    # ------------------------------------------------------------------

    def dashboard(self) -> dict:
        """Return a full Open Claw Bot dashboard snapshot."""
        return {
            "tier": self.config.name,
            "price_usd_monthly": self.config.price_usd_monthly,
            "total_strategies": len(self.strategy_engine.list_strategies()),
            "active_strategies": len(
                self.strategy_engine.list_strategies(status=StrategyStatus.ACTIVE)
            ),
            "total_clients": len(self.client_manager.list_clients()),
            "active_clients": len(
                self.client_manager.list_clients(status=ClientStatus.ACTIVE)
            ),
            "ai_models_ready": len(self.ai_models.list_models(ready_only=True)),
            "data_buffer_stats": self.strategy_engine.get_buffer_stats(),
            "features": self.config.features,
        }

    def describe_tier(self) -> str:
        """Return a human-readable tier description."""
        cfg = self.config
        upgrade = get_upgrade_path(self.tier)
        lines = [
            f"Open Claw Bot — {cfg.name} Tier",
            f"Price: ${cfg.price_usd_monthly:.2f}/month",
            f"Max clients: {cfg.max_clients or 'Unlimited'}",
            f"Max analyses/day: {cfg.max_analyses_per_day or 'Unlimited'}",
            f"Support: {cfg.support_level}",
            f"Features: {', '.join(cfg.features)}",
        ]
        if upgrade:
            lines.append(
                f"Upgrade available: {upgrade.name} at ${upgrade.price_usd_monthly:.2f}/month"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # BuddyAI-compatible chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """
        Handle a natural-language message and return a response dict.

        This method makes OpenClawBot compatible with the BuddyAI orchestrator.
        """
        msg = message.lower().strip()

        # Strategy generation intent
        for alias, stype in _STRATEGY_TYPE_ALIASES.items():
            if alias in msg:
                strategy = self.generate_strategy(
                    name=f"Auto: {stype.value.title()} Strategy",
                    strategy_type=stype.value,
                )
                return {
                    "response": "open_claw",
                    "message": (
                        f"Generated '{strategy.name}' — "
                        f"Expected ROI: {strategy.expected_roi_pct}%, "
                        f"Confidence: {strategy.confidence_score:.0%}."
                    ),
                    "data": strategy.to_dict(),
                }

        if any(k in msg for k in ("dashboard", "overview", "status")):
            return {
                "response": "open_claw",
                "message": "Here is your Open Claw Bot dashboard.",
                "data": self.dashboard(),
            }

        if any(k in msg for k in ("client", "clients")):
            clients = [c.to_dict() for c in self.client_manager.list_clients()]
            return {
                "response": "open_claw",
                "message": f"You have {len(clients)} client(s).",
                "data": {"clients": clients},
            }

        if any(k in msg for k in ("model", "ai", "ml")):
            models = [m.to_dict() for m in self.ai_models.list_models(ready_only=True)]
            return {
                "response": "open_claw",
                "message": f"{len(models)} AI model(s) ready.",
                "data": {"models": models},
            }

        if any(k in msg for k in ("rank", "best", "top")):
            top = self.rank_strategies()[:5]
            return {
                "response": "open_claw",
                "message": f"Top {len(top)} strategies by expected value.",
                "data": {"strategies": [s.to_dict() for s in top]},
            }

        if any(k in msg for k in ("tier", "upgrade", "plan")):
            return {
                "response": "open_claw",
                "message": self.describe_tier(),
                "data": {},
            }

        # Default NLP advice
        try:
            result = self.nlp_advise(message)
            rec = result.prediction.get("recommended_strategy_type", "balanced")
            return {
                "response": "open_claw",
                "message": f"I recommend a '{rec}' strategy. {result.explanation}",
                "data": result.to_dict(),
            }
        except OpenClawBotTierError:
            pass

        return {
            "response": "open_claw",
            "message": (
                "Open Claw Bot ready. Ask me to generate a strategy, rank strategies, "
                "analyse data, or manage clients."
            ),
            "data": {},
        }

    # ------------------------------------------------------------------
    # BuddyAI registration helper
    # ------------------------------------------------------------------

    def register_with_buddy(self, buddy_bot_instance) -> None:
        """Register this OpenClawBot instance with a BuddyAI orchestrator."""
        buddy_bot_instance.register_bot("open_claw", self)
