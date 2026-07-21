"""
DreamCo Empire OS — Main Entry Point

Composes all Empire OS modules into a single, unified platform:

  • Empire HQ          — real-time empire overview and command
  • Divisions          — organise bots by specialisation
  • Bot Fleet          — manage all 877+ bots (activate, speed, autonomy)
  • Deal Analyzer      — score and rank business opportunities
  • Formula Vault      — store and execute reusable formulas
  • Learning Matrix    — AI mentorship and skill progression
  • AI Leaders         — track strategic AI decision-makers
  • AI Models Hub      — manage and switch pre-trained models
  • AI Ecosystem       — visualise AI agent relationships
  • Orchestration      — multi-bot collaborative pipelines
  • Marketplace        — buy/sell bots, tools, and integrations
  • Crypto Tracker     — crypto portfolio and signal tracking
  • Payments Hub       — payment flow and billing management
  • Biz Launch         — guided new-business launcher
  • Code Lab           — automation code sandbox
  • Loans & Deals      — financing and deal consolidation
  • Debug Intel        — bot debugging and error hub
  • Revenue Tracker    — gross/net revenue analytics
  • Pricing Engine     — pricing optimisation and A/B testing
  • Connections        — API and integration registry
  • Time Capsule       — data archival and historical insights
  • Cost Tracking      — operational cost analytics
  • Autonomy Control   — empire-wide bot autonomy management

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

Usage
-----
    from bots.dreamco_empire_os import DreamCoEmpireOS, Tier

    empire = DreamCoEmpireOS(tier=Tier.PRO)
    empire.bot_fleet.register_bot("Lead Scraper", category="marketing", profit_per_day_usd=180)
    empire.bot_fleet.activate_bot("Lead Scraper")
    print(empire.dashboard())
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.dreamco_empire_os.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_EMPIRE_HQ,
    FEATURE_DIVISIONS,
    FEATURE_BOT_FLEET,
    FEATURE_DEAL_ANALYZER,
    FEATURE_FORMULA_VAULT,
    FEATURE_LEARNING_MATRIX,
    FEATURE_AI_LEADERS,
    FEATURE_AI_MODELS_HUB,
    FEATURE_AI_ECOSYSTEM,
    FEATURE_ORCHESTRATION,
    FEATURE_MARKETPLACE,
    FEATURE_CRYPTO,
    FEATURE_PAYMENTS,
    FEATURE_BIZ_LAUNCH,
    FEATURE_CODE_LAB,
    FEATURE_LOANS_DEALS,
    FEATURE_DEBUG_INTEL,
    FEATURE_REVENUE,
    FEATURE_PRICING,
    FEATURE_CONNECTIONS,
    FEATURE_TIME_CAPSULE,
    FEATURE_COST_TRACKING,
    FEATURE_AUTONOMY,
)
from bots.dreamco_empire_os.empire_hq import EmpireHQ
from bots.dreamco_empire_os.bot_fleet import BotFleet, BotSpeed, BotStatus
from bots.dreamco_empire_os.deal_analyzer import DealAnalyzer, DealType, RiskLevel
from bots.dreamco_empire_os.formula_vault import FormulaVault, FormulaCategory
from bots.dreamco_empire_os.learning_matrix import LearningMatrix, LearningDomain
from bots.dreamco_empire_os.ai_leaders import AILeaders, LeaderRole, LeaderStatus
from bots.dreamco_empire_os.orchestration import Orchestration
from bots.dreamco_empire_os.marketplace import Marketplace, ListingCategory
from bots.dreamco_empire_os.revenue_tracker import RevenueTracker
from bots.dreamco_empire_os.cost_tracking import CostTracking, CostCategory
from bots.dreamco_empire_os.modules import (
    Divisions,
    AIModelsHub,
    AIEcosystem,
    CryptoTracker,
    PaymentsHub,
    BizLaunch,
    CodeLab,
    LoansDeals,
    DebugIntel,
    DebugLevel,
    PricingEngine,
    Connections,
    TimeCapsule,
    AutonomyControl,
    AutonomyMode,
)

from datetime import datetime, timezone


class DreamCoEmpireOSError(Exception):
    """Raised when an Empire OS operation cannot be completed."""


class DreamCoTierError(DreamCoEmpireOSError):
    """Raised when a feature is not available on the current tier."""


class DreamCoEmpireOS:
    """
    DreamCo Empire OS — full-stack AI empire management platform.

    Instantiate with a tier (FREE / PRO / ENTERPRISE) to gain access
    to the corresponding set of modules and capabilities.
    """

    def __init__(self, tier: Tier = Tier.FREE, operator_name: str = "Empire Operator") -> None:
        self.tier = tier
        self.operator_name = operator_name
        self._config: TierConfig = get_tier_config(tier)
        self._created_at = datetime.now(timezone.utc).isoformat()

        # Always-available modules
        self.empire_hq = EmpireHQ()
        self.bot_fleet = BotFleet()
        self.deal_analyzer = DealAnalyzer()
        self.formula_vault = FormulaVault()
        self.revenue_tracker = RevenueTracker()
        self.cost_tracking = CostTracking()
        self.divisions = Divisions()

        # PRO+ modules (initialised for all tiers, access-controlled at method level)
        self.learning_matrix = LearningMatrix()
        self.ai_leaders = AILeaders()
        self.ai_models_hub = AIModelsHub()
        self.ai_ecosystem = AIEcosystem()
        self.orchestration = Orchestration()
        self.marketplace = Marketplace()
        self.crypto_tracker = CryptoTracker()
        self.payments_hub = PaymentsHub()
        self.biz_launch = BizLaunch()
        self.code_lab = CodeLab()
        self.loans_deals = LoansDeals()
        self.debug_intel = DebugIntel()
        self.pricing_engine = PricingEngine()
        self.connections = Connections()
        self.time_capsule = TimeCapsule()
        self.autonomy_control = AutonomyControl()

    # ------------------------------------------------------------------
    # Tier utilities
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        if not self._config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            suggestion = f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)." if upgrade else ""
            raise DreamCoTierError(
                f"Feature '{feature}' is not available on the {self._config.name} tier.{suggestion}"
            )

    def can_access(self, feature: str) -> bool:
        return self._config.has_feature(feature)

    def get_tier_info(self) -> dict:
        return {
            "tier": self.tier.value,
            "name": self._config.name,
            "price_usd_monthly": self._config.price_usd_monthly,
            "max_bots": self._config.max_bots,
            "features": self._config.features,
            "support_level": self._config.support_level,
        }

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def dashboard(self) -> dict:
        """Return a comprehensive snapshot of the entire DreamCo Empire OS."""
        self._require(FEATURE_EMPIRE_HQ)

        fleet_stats = self.bot_fleet.get_fleet_stats()
        self.empire_hq.set_active_bots(fleet_stats["running"])

        revenue_summary = self.revenue_tracker.get_summary()
        self.empire_hq.record_revenue(0)  # sync without double-adding

        return {
            "title": "DreamCo Empire OS",
            "operator": self.operator_name,
            "tier": self.tier.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "empire_hq": self.empire_hq.snapshot(),
            "bot_fleet": fleet_stats,
            "revenue": revenue_summary,
            "costs": self.cost_tracking.get_summary(),
            "upgrade_available": get_upgrade_path(self.tier) is not None,
        }

    def super_dashboard_snapshot(self) -> dict[str, float | int | str]:
        """Return a compact metrics payload consumed by dashboards.super_dashboard."""
        data = self.dashboard()
        fleet = data.get("bot_fleet", {})
        revenue = data.get("revenue", {})
        return {
            "active_bots": int(fleet.get("running", 0)),
            "healthy_bots": int(fleet.get("running", 0)),
            "unhealthy_bots": int(fleet.get("stopped", 0)),
            "fleet_total": int(fleet.get("total", 0)),
            "revenue_24h": float(revenue.get("today_revenue", 0.0) or 0.0),
            "revenue_total": float(revenue.get("total_revenue", 0.0) or 0.0),
            "tier": str(data.get("tier", self.tier.value)),
        }

    # ------------------------------------------------------------------
    # Bot Fleet helpers
    # ------------------------------------------------------------------

    def activate_bot(self, name: str) -> dict:
        self._require(FEATURE_BOT_FLEET)
        return self.bot_fleet.activate_bot(name)

    def set_fleet_speed(self, speed: BotSpeed) -> dict:
        self._require(FEATURE_BOT_FLEET)
        return self.bot_fleet.set_fleet_speed(speed)

    # ------------------------------------------------------------------
    # Learning Matrix helpers
    # ------------------------------------------------------------------

    def learn(self, learner_id: str, lesson_id: str) -> dict:
        self._require(FEATURE_LEARNING_MATRIX)
        return self.learning_matrix.complete_lesson(learner_id, lesson_id)

    # ------------------------------------------------------------------
    # Orchestration helpers
    # ------------------------------------------------------------------

    def run_pipeline(self, pipeline_id: str) -> dict:
        self._require(FEATURE_ORCHESTRATION)
        return self.orchestration.run_pipeline(pipeline_id)

    # ------------------------------------------------------------------
    # Chat interface (BuddyAI-compatible)
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """
        Process a natural-language command for the Empire OS.

        Returns a JSON-serialisable response dict compatible with BuddyAI routing.
        """
        msg = message.lower().strip()

        if "dashboard" in msg or "status" in msg or "overview" in msg:
            return {"message": "Empire OS dashboard loaded.", "data": self.dashboard()}

        if "fleet" in msg or "bot" in msg:
            return {"message": "Bot fleet stats retrieved.", "data": self.bot_fleet.get_fleet_stats()}

        if "revenue" in msg or "money" in msg or "income" in msg:
            return {"message": "Revenue summary retrieved.", "data": self.revenue_tracker.get_summary()}

        if "deal" in msg:
            return {"message": "Deal analyzer ready. Add deals via empire.deal_analyzer.add_deal().",
                    "data": self.deal_analyzer.get_summary()}

        if "formula" in msg:
            return {"message": "Formula vault ready.", "data": self.formula_vault.get_stats()}

        if "learn" in msg or "lesson" in msg or "matrix" in msg:
            return {"message": "Learning matrix ready.", "data": self.learning_matrix.get_stats()}

        if "cost" in msg or "spend" in msg or "expense" in msg:
            return {"message": "Cost tracking summary retrieved.", "data": self.cost_tracking.get_summary()}

        return {
            "message": (
                f"DreamCo Empire OS online. You have access to: "
                f"{len(self._config.features)} modules. Type 'dashboard' for an overview."
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
