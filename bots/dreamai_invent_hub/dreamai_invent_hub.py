"""
DreamAIInvent Hub — Main Bot

Positions DreamCo as a global hub where AI meets inventors by integrating:
  • Partnership Matchmaking  — connect AI developers, inventors, and manufacturers
  • Inventor Toolkit         — design bot, financial projections, manufacturing simulator, patent AI
  • R&D Marketplace          — electronics directory, forums, prototyping tools, test outcomes

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

Usage
-----
    from bots.dreamai_invent_hub import DreamAIInventHub, Tier

    hub = DreamAIInventHub(tier=Tier.PRO)
    matches = hub.find_matches("SEED-INV-001")
    session = hub.start_design_session("Smart Glove", "iot", "prototype")
    print(hub.dashboard())
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.dreamai_invent_hub.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_BASIC_MATCHMAKING,
    FEATURE_ADVANCED_MATCHMAKING,
    FEATURE_INVENTOR_TOOLKIT,
    FEATURE_DESIGN_BOT,
    FEATURE_FINANCIAL_PROJECTION,
    FEATURE_MANUFACTURING_SIMULATOR,
    FEATURE_PATENT_SUPPORT,
    FEATURE_FORUMS,
    FEATURE_MARKETPLACE_LISTING,
    FEATURE_MARKETPLACE_BROWSE,
    FEATURE_LICENSING_TEMPLATES,
    FEATURE_REVENUE_SHARING,
    FEATURE_IOT_MATCHMAKING,
    FEATURE_PROTOTYPING_LAB,
    FEATURE_PARTNERSHIP_ANALYTICS,
    FEATURE_API_ACCESS,
    FEATURE_WHITE_LABEL,
    FEATURE_IOT_LAB,
)
from bots.dreamai_invent_hub.matchmaking import (
    MatchmakingEngine,
    Profile,
    ProfileType,
    CollaborationType,
    MatchStatus,
)
from bots.dreamai_invent_hub.inventor_toolkit import (
    InventorToolkit,
    DesignDomain,
    DesignStage,
    ManufacturingMethod,
    PatentType,
)
from bots.dreamai_invent_hub.marketplace import (
    RDMarketplace,
    DirectoryCategory,
    ServiceType,
    ForumCategory,
    PostType,
    ListingStatus,
)
from framework import GlobalAISourcesFlow  # noqa: F401  — GLOBAL AI SOURCES FLOW


class DreamAIInventHubTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class DreamAIInventHub:
    """
    DreamAIInvent Hub — the central platform where AI meets inventors.

    Connects AI developers, inventors, and robotics/electronics manufacturers
    through intelligent matchmaking, a rich inventor toolkit, and an
    expanding R&D marketplace.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)

        # GLOBAL AI SOURCES FLOW — mandatory pipeline
        self.flow = GlobalAISourcesFlow(bot_name="DreamAIInventHub")

        # Core subsystems
        self.matchmaking = MatchmakingEngine()
        self.toolkit = InventorToolkit()
        self.marketplace = RDMarketplace()

        # Session counters
        self._match_usage: int = 0
        self._toolkit_usage: int = 0

    # ------------------------------------------------------------------
    # Tier guard helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            upgrade_msg = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly:.0f}/mo)."
                if upgrade
                else ""
            )
            raise DreamAIInventHubTierError(
                f"Feature '{feature}' is not available on the {self.config.name} tier.{upgrade_msg}"
            )

    def _check_match_limit(self) -> None:
        limit = self.config.max_matches_per_month
        if limit is not None and self._match_usage >= limit:
            raise DreamAIInventHubTierError(
                f"Monthly match limit ({limit}) reached on the {self.config.name} tier. "
                "Upgrade to access more matches."
            )

    def _check_toolkit_limit(self) -> None:
        limit = self.config.max_toolkit_sessions_per_month
        if limit is not None and self._toolkit_usage >= limit:
            raise DreamAIInventHubTierError(
                f"Monthly toolkit session limit ({limit}) reached on the {self.config.name} tier. "
                "Upgrade for unlimited sessions."
            )

    # ------------------------------------------------------------------
    # Matchmaking
    # ------------------------------------------------------------------

    def register_profile(self, profile: Profile) -> str:
        """Register a participant profile in the matchmaking engine."""
        return self.matchmaking.register_profile(profile)

    def find_matches(
        self,
        profile_id: str,
        collaboration_type: CollaborationType | None = None,
        min_score: float = 0.3,
        limit: int = 10,
    ) -> list:
        """Return ranked partnership matches for a given profile."""
        self._require_feature(FEATURE_BASIC_MATCHMAKING)
        self._check_match_limit()
        self._match_usage += 1
        return self.matchmaking.find_matches(
            profile_id=profile_id,
            collaboration_type=collaboration_type,
            min_score=min_score,
            limit=limit,
        )

    def create_match(
        self,
        requester_id: str,
        partner_id: str,
        collaboration_type: CollaborationType,
        project_description: str,
        proposed_terms: dict | None = None,
    ):
        """Initiate a match request between two profiles."""
        self._require_feature(FEATURE_BASIC_MATCHMAKING)
        return self.matchmaking.create_match(
            requester_id=requester_id,
            partner_id=partner_id,
            collaboration_type=collaboration_type,
            project_description=project_description,
            proposed_terms=proposed_terms,
        )

    def get_terms_template(self, collaboration_type: CollaborationType) -> dict:
        """Return a licensing/revenue-sharing/co-dev terms template."""
        self._require_feature(FEATURE_LICENSING_TEMPLATES)
        return self.matchmaking.generate_terms_template(collaboration_type)

    # ------------------------------------------------------------------
    # Inventor Toolkit
    # ------------------------------------------------------------------

    def start_design_session(
        self,
        product_name: str,
        domain: str,
        stage: str,
        requirements: list | None = None,
    ):
        """Start an AI design session for a product concept."""
        self._require_feature(FEATURE_DESIGN_BOT)
        self._check_toolkit_limit()
        self._toolkit_usage += 1
        domain_enum = DesignDomain(domain)
        stage_enum = DesignStage(stage)
        return self.toolkit.design_bot.start_session(
            product_name=product_name,
            domain=domain_enum,
            stage=stage_enum,
            requirements=requirements,
        )

    def project_revenue(
        self,
        unit_price_usd: float,
        units_year1: int,
        growth_rate_pct: float = 50.0,
        years: int = 5,
    ) -> list:
        """Generate a multi-year revenue projection for a hardware product."""
        self._require_feature(FEATURE_FINANCIAL_PROJECTION)
        return self.toolkit.financial_projection.project_revenue(
            unit_price_usd=unit_price_usd,
            units_year1=units_year1,
            growth_rate_pct=growth_rate_pct,
            years=years,
        )

    def break_even_analysis(
        self,
        fixed_costs_usd: float,
        unit_price_usd: float,
        unit_cost_usd: float,
    ) -> dict:
        """Calculate break-even point for a hardware product."""
        self._require_feature(FEATURE_FINANCIAL_PROJECTION)
        return self.toolkit.financial_projection.break_even_analysis(
            fixed_costs_usd=fixed_costs_usd,
            unit_price_usd=unit_price_usd,
            unit_cost_usd=unit_cost_usd,
        )

    def simulate_manufacturing(
        self,
        method: str,
        units: int,
        material_cost_per_unit_usd: float = 0.0,
    ):
        """Simulate a manufacturing scenario."""
        self._require_feature(FEATURE_MANUFACTURING_SIMULATOR)
        method_enum = ManufacturingMethod(method)
        return self.toolkit.manufacturing_simulator.simulate(
            method=method_enum,
            units=units,
            material_cost_per_unit_usd=material_cost_per_unit_usd,
        )

    def compare_manufacturing_methods(self, units: int) -> list:
        """Compare all manufacturing methods for a given production volume."""
        self._require_feature(FEATURE_MANUFACTURING_SIMULATOR)
        return self.toolkit.manufacturing_simulator.compare_methods(units=units)

    def create_patent_dossier(
        self,
        invention_title: str,
        description: str,
        patent_type: str = "provisional",
    ):
        """Create a patent dossier for an invention."""
        self._require_feature(FEATURE_PATENT_SUPPORT)
        pt_enum = PatentType(patent_type)
        return self.toolkit.patent_support.create_dossier(
            invention_title=invention_title,
            description=description,
            patent_type=pt_enum,
        )

    # ------------------------------------------------------------------
    # Marketplace
    # ------------------------------------------------------------------

    def search_directory(
        self,
        query: str = "",
        category: str | None = None,
        min_rating: float = 0.0,
        verified_only: bool = False,
    ) -> list:
        """Search the R&D marketplace directory."""
        self._require_feature(FEATURE_MARKETPLACE_BROWSE)
        cat_enum = DirectoryCategory(category) if category else None
        return self.marketplace.search_directory(
            query=query,
            category=cat_enum,
            min_rating=min_rating,
            verified_only=verified_only,
        )

    def create_forum_post(
        self,
        author_id: str,
        title: str,
        content: str,
        category: str = "general",
        post_type: str = "discussion",
        tags: list | None = None,
    ):
        """Create a forum post in the R&D marketplace."""
        self._require_feature(FEATURE_FORUMS)
        cat_enum = ForumCategory(category)
        type_enum = PostType(post_type)
        return self.marketplace.create_post(
            author_id=author_id,
            title=title,
            content=content,
            category=cat_enum,
            post_type=type_enum,
            tags=tags,
        )

    def submit_prototyping_tool(
        self,
        author_id: str,
        name: str,
        description: str,
        tool_type: str,
        demo_url: str = "",
        source_url: str = "",
        tags: list | None = None,
    ):
        """Submit a live prototyping tool to the marketplace."""
        self._require_feature(FEATURE_PROTOTYPING_LAB)
        return self.marketplace.submit_tool(
            author_id=author_id,
            name=name,
            description=description,
            tool_type=tool_type,
            demo_url=demo_url,
            source_url=source_url,
            tags=tags,
        )

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def dashboard(self) -> dict:
        """Return a high-level overview of the hub's activity."""
        all_matches = self.matchmaking.list_matches()
        all_profiles = self.matchmaking.list_profiles()
        all_listings = list(self.marketplace._listings.values())
        all_posts = list(self.marketplace._posts.values())
        all_tools = list(self.marketplace._tools.values())

        match_stats = {
            "total": len(all_matches),
            "pending": sum(1 for m in all_matches if m.status == MatchStatus.PENDING),
            "in_progress": sum(1 for m in all_matches if m.status == MatchStatus.IN_PROGRESS),
            "completed": sum(1 for m in all_matches if m.status == MatchStatus.COMPLETED),
        }

        return {
            "bot": "DreamAIInvent Hub",
            "tier": self.config.name,
            "price_usd_monthly": self.config.price_usd_monthly,
            "mission": "Where AI meets inventors — connecting developers, inventors & manufacturers",
            "profiles_registered": len(all_profiles),
            "matches": match_stats,
            "match_usage_this_month": self._match_usage,
            "toolkit_usage_this_month": self._toolkit_usage,
            "marketplace": {
                "directory_listings": len(all_listings),
                "forum_posts": len(all_posts),
                "prototyping_tools": len(all_tools),
            },
            "toolkit": self.toolkit.summary(),
        }

    def upgrade_info(self) -> dict | None:
        """Return information about the next tier upgrade."""
        upgrade = get_upgrade_path(self.tier)
        if not upgrade:
            return None
        return {
            "current_tier": self.config.name,
            "next_tier": upgrade.name,
            "next_tier_price_usd": upgrade.price_usd_monthly,
            "additional_features": [
                f for f in upgrade.features if f not in self.config.features
            ],
        }
