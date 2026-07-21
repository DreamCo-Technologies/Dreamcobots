"""
Big Bro AI — Main Entry Point

Composes all Big Bro AI sub-systems into a single, unified platform:

  • Personality Engine      — hard-coded character, tone, and core rules
  • Memory System           — consent-based user life profiles
  • Mentor Engine           — multi-domain mentoring (money, tech, life, relationships)
  • Bot Factory             — automated bot creation with prospectuses & readiness scores
  • Continuous Study Engine — modular knowledge crawlers that keep Big Bro sharp
  • Prospectus System       — structured bot specification & ROI bridge documents
  • Courses-as-Systems      — progressive courses with automation hooks
  • Route & GPS Intelligence — local/national resource routing
  • Sales & Monetization    — income streams, compound interest, revenue tracking
  • Catalog & Franchise     — product catalog + franchise network management
  • Master Dashboard        — unified command-and-control panel

Big Bro runs on any device with a browser — computer, tablet, phone, Xbox One.
No downloads. No installs.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.big_bro_ai import BigBroAI, Tier

    big_bro = BigBroAI(tier=Tier.PRO, name="Big Bro")
    response = big_bro.chat("What's the fastest way to make $100 today?")
    print(response["message"])
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.big_bro_ai.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_MEMORY_SYSTEM,
    FEATURE_BOT_FACTORY,
    FEATURE_CONTINUOUS_STUDY,
    FEATURE_PROSPECTUS,
    FEATURE_COURSES_SYSTEM,
    FEATURE_ROUTE_GPS,
    FEATURE_SALES_MONETIZATION,
    FEATURE_CATALOG,
    FEATURE_FRANCHISE_ENGINE,
    FEATURE_MASTER_DASHBOARD,
    FEATURE_RELATIONSHIP_MENTOR,
)
from bots.big_bro_ai.personality import (
    PersonalityEngine,
    RelationshipTier,
    RoastMode,
    BIG_BRO_CORE_RULES,
    DREAMCO_PHILOSOPHY,
    BIG_BRO_SIGNATURES,
)
from bots.big_bro_ai.memory_system import MemorySystem, MemorySystemError
from bots.big_bro_ai.mentor_engine import MentorEngine, MentorDomain
from bots.big_bro_ai.bot_factory import BotFactory, BotCategory, BotFactoryError
from bots.big_bro_ai.continuous_study import (
    ContinuousStudyEngine,
    KnowledgeDomain,
    ContinuousStudyError,
)
from bots.big_bro_ai.prospectus import ProspectusSystem, ROIBridge, ProspectusStatus
from bots.big_bro_ai.courses_system import CoursesSystem, CourseCategory, CoursesSystemError
from bots.big_bro_ai.route_gps import RouteGPSIntelligence, ResourceCategory, RouteType
from bots.big_bro_ai.sales_monetization import (
    SalesMonetizationEngine,
    IncomeStreamType,
)
from bots.big_bro_ai.catalog_franchise import (
    CatalogFranchiseEngine,
    CatalogCategory,
    FranchiseStatus,
    CatalogFranchiseError,
)
from bots.big_bro_ai.master_dashboard import MasterDashboard, AlertLevel

from framework import GlobalAISourcesFlow


class BigBroAIError(Exception):
    """Raised when a Big Bro AI operation cannot be completed."""


class BigBroTierError(BigBroAIError):
    """Raised when a feature is not available on the current tier."""


class BigBroAI:
    """
    Big Bro AI — Digital big brother, mentor, money teacher, and
    autonomous platform builder.

    Composes all nine core layers of the Big Bro AI Ecosystem and
    exposes a unified BuddyAI-compatible ``chat()`` interface.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature availability.
    name : str
        Custom name for this Big Bro instance.
    city : str
        City context for Route & GPS Intelligence.
    state : str
        State/province context for Route & GPS Intelligence.
    """

    def __init__(
        self,
        tier: Tier = Tier.FREE,
        name: str = "Big Bro",
        city: str = "",
        state: str = "",
    ) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self.name = name

        # ------------------------------------------------------------------
        # GLOBAL AI SOURCES FLOW — mandatory pipeline
        # ------------------------------------------------------------------
        self.flow = GlobalAISourcesFlow(bot_name="BigBroAI")

        # ------------------------------------------------------------------
        # Core Layers
        # ------------------------------------------------------------------

        # 1. Big Bro Core — Personality Engine
        self.personality = PersonalityEngine(custom_name=name)

        # 2. Memory System
        self.memory = MemorySystem(
            max_profiles=self.config.max_memory_profiles
        )

        # 3. Mentor Engine
        self.mentor = MentorEngine()

        # 4. Bot Factory
        self.bot_factory = BotFactory(max_bots=self.config.max_bots)

        # 5. Continuous Study Engine
        self.study_engine = ContinuousStudyEngine(
            enabled=self.config.has_feature(FEATURE_CONTINUOUS_STUDY)
        )

        # 6. Prospectus System
        self.prospectus_system = ProspectusSystem()

        # 7. Courses-as-Systems
        self.courses = CoursesSystem()

        # 8. Route & GPS Intelligence
        self.route_gps = RouteGPSIntelligence(
            default_city=city, default_state=state
        )

        # 9. Sales & Monetization Engine
        self.sales = SalesMonetizationEngine()

        # 10. Catalog + Franchise Engine
        self.catalog = CatalogFranchiseEngine()

        # 11. Master Dashboard
        self.dashboard = MasterDashboard(big_bro_name=name, tier=tier.value)

        # ------------------------------------------------------------------
        # Run the pipeline
        # ------------------------------------------------------------------
        self._run_pipeline()

    # ------------------------------------------------------------------
    # Pipeline
    # ------------------------------------------------------------------

    def _run_pipeline(self) -> None:
        """Run the GLOBAL AI SOURCES FLOW pipeline and populate dashboard."""
        try:
            self.flow.run_pipeline()
        except Exception:
            pass

        self._refresh_dashboard()

    def _refresh_dashboard(self) -> None:
        """Push fresh summaries from all sub-systems into the dashboard."""
        self.dashboard.update_panel(
            "memory_system", {"profile_count": self.memory.profile_count()}
        )
        self.dashboard.update_panel("bot_factory", self.bot_factory.factory_report())
        self.dashboard.update_panel("continuous_study", self.study_engine.study_report())
        self.dashboard.update_panel(
            "prospectus_system", self.prospectus_system.system_report()
        )
        self.dashboard.update_panel(
            "courses_system", self.courses.revenue_summary()
        )
        self.dashboard.update_panel("route_gps", self.route_gps.gps_report())
        self.dashboard.update_panel(
            "sales_monetization", self.sales.revenue_dashboard()
        )
        self.dashboard.update_panel(
            "catalog_franchise", self.catalog.catalog_report()
        )

    # ------------------------------------------------------------------
    # BuddyAI-compatible chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str, user_id: str = "guest") -> dict:
        """
        Process a chat message and return a structured response.

        Parameters
        ----------
        message : str
            The user's message.
        user_id : str
            User identifier for memory lookup.

        Returns
        -------
        dict
            ``{"message": str, "source": "BigBroAI", "tier": str}``
        """
        msg_lower = message.lower()

        # Greeting / introduction
        if any(kw in msg_lower for kw in ("hello", "hi", "hey", "who are you", "introduce")):
            profile = self.memory.get_profile(user_id)
            if profile:
                reply = self.personality.greet(profile.name)
                recall = self.memory.recall(user_id)
                return self._response(f"{reply}\n\n{recall}")
            return self._response(self.personality.introduce())

        # Money / income questions
        if any(kw in msg_lower for kw in ("money", "income", "earn", "make", "revenue", "dollar")):
            result = self.mentor.teach(user_id, MentorDomain.MONEY)
            return self._response(result["lesson"])

        # Tech questions
        if any(kw in msg_lower for kw in ("tech", "code", "api", "ai", "automate", "build")):
            result = self.mentor.teach(user_id, MentorDomain.TECH)
            return self._response(result["lesson"])

        # Relationship questions
        if any(
            kw in msg_lower
            for kw in ("relationship", "dating", "girl", "confidence", "reject")
        ):
            result = self.mentor.teach(user_id, MentorDomain.RELATIONSHIPS)
            return self._response(result["lesson"])

        # Daily task
        if any(kw in msg_lower for kw in ("task", "today", "what should", "daily")):
            task = self.mentor.daily_task(user_id)
            return self._response(f"Today's task: {task}")

        # DreamCo philosophy
        if any(kw in msg_lower for kw in ("dreamco", "system", "philosophy", "passive")):
            return self._response(self.personality.teach_philosophy("core"))

        # Dashboard / status
        if any(kw in msg_lower for kw in ("dashboard", "status", "report", "stats")):
            self._refresh_dashboard()
            kpis = self.dashboard.kpi_summary()
            return self._response(
                f"Big Bro Status:\n"
                f"• Revenue: ${kpis['total_revenue_usd']}\n"
                f"• MRR: ${kpis['mrr_usd']}\n"
                f"• Bots Created: {kpis['total_bots_created']}\n"
                f"• Active Franchises: {kpis['active_franchises']}\n"
                f"• Knowledge Patterns: {kpis['knowledge_patterns']}"
            )

        # Upgrade prompt
        if "upgrade" in msg_lower or "tier" in msg_lower:
            upgrade = get_upgrade_path(self.tier)
            if upgrade:
                return self._response(
                    f"You're on {self.config.name}. "
                    f"Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo) "
                    f"to unlock more bots, more AI models, and more income tools."
                )
            return self._response("You're already on the top tier. Let's build.")

        # Default — signature wisdom
        return self._response(self.personality.get_signature(len(message) % len(BIG_BRO_SIGNATURES)))

    def process(self, message: str, **kwargs) -> dict:
        """Alias for chat() — BuddyAI process() compatibility."""
        return self.chat(message, **kwargs)

    # ------------------------------------------------------------------
    # Personality helpers (delegated)
    # ------------------------------------------------------------------

    def introduce(self, community_mode: bool = False) -> str:
        """Return Big Bro's introduction script."""
        return self.personality.introduce(community_mode)

    def greet(
        self,
        user_name: str,
        relationship: RelationshipTier = RelationshipTier.NEW_USER,
    ) -> str:
        """Return a personalised greeting."""
        return self.personality.greet(user_name, relationship)

    def roast(self, excuse: str) -> str:
        """Return a roast targeting an excuse (never a person's appearance)."""
        return self.personality.roast(excuse)

    def defend(
        self,
        target_name: str,
        relationship: RelationshipTier = RelationshipTier.CREATOR,
    ) -> str:
        """Return a defense response."""
        return self.personality.defend(target_name, relationship)

    def set_roast_mode(self, mode: RoastMode) -> None:
        """Change the active roast mode."""
        self.personality.roast_mode = mode

    # ------------------------------------------------------------------
    # Memory helpers (delegated)
    # ------------------------------------------------------------------

    def create_user(
        self,
        user_id: str,
        name: str,
        nickname: str = "",
        how_we_met: str = "",
        relationship_tier: str = "new_user",
    ) -> dict:
        """Create a user profile."""
        self._require_feature(FEATURE_MEMORY_SYSTEM)
        profile = self.memory.create_profile(
            user_id, name, nickname, how_we_met, relationship_tier
        )
        self._refresh_dashboard()
        return self.memory.summary(user_id)

    def remember(self, user_id: str) -> str:
        """Return what Big Bro remembers about *user_id*."""
        return self.memory.recall(user_id)

    def log_life_event(
        self, user_id: str, situation: str, note: str, tags: list[str] | None = None
    ) -> dict:
        """Log a life event to a user's memory profile."""
        entry = self.memory.log_memory(user_id, situation, note, tags)
        return entry.to_dict()

    # ------------------------------------------------------------------
    # Mentor helpers (delegated)
    # ------------------------------------------------------------------

    def teach(self, user_id: str, domain: MentorDomain, topic: str | None = None) -> dict:
        """Deliver a lesson to *user_id* in *domain*."""
        return self.mentor.teach(user_id, domain, topic)

    def progress_report(self, user_id: str) -> dict:
        """Return the mentor progress report for *user_id*."""
        return self.mentor.progress_report(user_id)

    # ------------------------------------------------------------------
    # Bot Factory helpers (delegated)
    # ------------------------------------------------------------------

    def create_bot(
        self,
        name: str,
        category: BotCategory,
        mission: str,
        **kwargs,
    ) -> dict:
        """Create a new bot via the Bot Factory."""
        self._require_feature(FEATURE_BOT_FACTORY)
        bot = self.bot_factory.create_bot(name, category, mission, **kwargs)
        self._refresh_dashboard()
        return bot.to_dict()

    def factory_report(self) -> dict:
        """Return the Bot Factory summary report."""
        return self.bot_factory.factory_report()

    # ------------------------------------------------------------------
    # Prospectus helpers (delegated)
    # ------------------------------------------------------------------

    def create_prospectus(self, bot_name: str, **kwargs) -> dict:
        """Create a bot prospectus."""
        self._require_feature(FEATURE_PROSPECTUS)
        p = self.prospectus_system.create(bot_name, **kwargs)
        return p.to_dict()

    # ------------------------------------------------------------------
    # Course helpers (delegated)
    # ------------------------------------------------------------------

    def list_courses(self, category: CourseCategory | None = None) -> list[dict]:
        """List available courses."""
        return [c.to_dict() for c in self.courses.list_courses(category)]

    def enroll_in_course(self, user_id: str, course_id: str) -> dict:
        """Enroll *user_id* in a course."""
        self._require_feature(FEATURE_COURSES_SYSTEM)
        enrollment = self.courses.enroll(user_id, course_id)
        return enrollment.to_dict()

    # ------------------------------------------------------------------
    # Route & GPS helpers (delegated)
    # ------------------------------------------------------------------

    def find_resources(self, need: str, city: str | None = None) -> list[dict]:
        """Find resources matching *need*."""
        self._require_feature(FEATURE_ROUTE_GPS)
        routes = self.route_gps.navigate(need, city)
        return [r.to_dict() for r in routes]

    # ------------------------------------------------------------------
    # Sales & Monetization helpers (delegated)
    # ------------------------------------------------------------------

    def revenue_dashboard(self) -> dict:
        """Return the sales revenue dashboard."""
        self._require_feature(FEATURE_SALES_MONETIZATION)
        return self.sales.revenue_dashboard()

    def project_income(self, daily_users: int, price_per_user: float) -> dict:
        """Project income from *daily_users* paying *price_per_user*."""
        return self.sales.project_goal(daily_users, price_per_user)

    def compound_interest(
        self,
        principal: float,
        rate: float,
        periods: int,
    ) -> dict:
        """Calculate compound interest."""
        return self.sales.calculate_compound(principal, rate, periods)

    # ------------------------------------------------------------------
    # Catalog & Franchise helpers (delegated)
    # ------------------------------------------------------------------

    def browse_catalog(self, tag: str | None = None) -> list[dict]:
        """Browse the product catalog."""
        self._require_feature(FEATURE_CATALOG)
        return [i.to_dict() for i in self.catalog.search_catalog(tag=tag)]

    def open_franchise(
        self, owner_name: str, territory: str, monthly_fee_usd: float = 99.0
    ) -> dict:
        """Open a new franchise."""
        self._require_feature(FEATURE_FRANCHISE_ENGINE)
        franchise = self.catalog.open_franchise(owner_name, territory, monthly_fee_usd)
        self._refresh_dashboard()
        return franchise.to_dict()

    # ------------------------------------------------------------------
    # Master Dashboard
    # ------------------------------------------------------------------

    def get_dashboard(self) -> dict:
        """Return the full master dashboard snapshot."""
        self._require_feature(FEATURE_MASTER_DASHBOARD)
        self._refresh_dashboard()
        return self.dashboard.snapshot()

    def get_dashboard_for_device(self, device: str = "browser") -> dict:
        """Return a device-optimised dashboard (browser/tablet/mobile/xbox)."""
        self._refresh_dashboard()
        return self.dashboard.export_for_device(device)

    # ------------------------------------------------------------------
    # Tier information
    # ------------------------------------------------------------------

    def tier_info(self) -> dict:
        """Return tier configuration details."""
        return {
            "tier": self.tier.value,
            "name": self.config.name,
            "price_usd_monthly": self.config.price_usd_monthly,
            "max_bots": self.config.max_bots,
            "max_memory_profiles": self.config.max_memory_profiles,
            "max_ai_models": self.config.max_ai_models,
            "features": self.config.features,
            "support_level": self.config.support_level,
        }

    def upgrade_info(self) -> dict | None:
        """Return the next tier upgrade info, or None if already at top."""
        upgrade = get_upgrade_path(self.tier)
        if upgrade is None:
            return None
        return {
            "tier": upgrade.tier.value,
            "name": upgrade.name,
            "price_usd_monthly": upgrade.price_usd_monthly,
            "features": upgrade.features,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            raise BigBroTierError(
                f"Feature '{feature}' is not available on the "
                f"{self.config.name} tier. Upgrade to unlock it."
            )

    def _response(self, message: str) -> dict:
        return {
            "message": message,
            "source": "BigBroAI",
            "name": self.name,
            "tier": self.tier.value,
        }
