"""
Bot Library — DreamCo Global Bot Communication Network.

Catalogs and registers all preexisting DreamCo bots so they can be
discovered, configured, and operated through the GBN.

Each entry in the library describes a bot's identity, capabilities,
category, tier support, and how to instantiate it.  The library acts
as the single source of truth for "which bots exist in DreamCo."
"""

from __future__ import annotations

import sys
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BotCategory(Enum):
    FINANCE = "finance"
    REAL_ESTATE = "real_estate"
    CRYPTO = "crypto"
    AUTOMATION = "automation"
    AI = "ai"
    MARKETPLACE = "marketplace"
    FREELANCE = "freelance"
    LEAD_GEN = "lead_gen"
    EDUCATION = "education"
    GOVERNMENT = "government"
    JOB = "job"
    MINING = "mining"
    PAYMENTS = "payments"
    DEVELOPER_TOOLS = "developer_tools"
    BUSINESS = "business"
    MARKETING = "marketing"
    APP = "app"
    OCCUPATIONAL = "occupational"
    SYSTEM = "system"
    OTHER = "other"


class BotStatus(Enum):
    ACTIVE = "active"
    BETA = "beta"
    DEPRECATED = "deprecated"
    MAINTENANCE = "maintenance"


# ---------------------------------------------------------------------------
# Bot entry
# ---------------------------------------------------------------------------

@dataclass
class BotEntry:
    """
    Metadata record for a single DreamCo bot in the library.

    Attributes
    ----------
    bot_id : str
        Unique identifier (snake_case, e.g. ``"financial_literacy_bot"``).
    display_name : str
        Human-readable name.
    description : str
        Short description of the bot's purpose.
    category : BotCategory
        Functional category.
    module_path : str
        Module filesystem path relative to the repo root, using dots as
        separators (e.g. ``"bots.financial_literacy_bot.financial_literacy_bot"``).
        Note: paths containing hyphens or leading digits are filesystem
        references and cannot be imported directly via ``importlib``; use
        ``importlib.util.spec_from_file_location`` with the resolved path.
    class_name : str
        Class name inside the module.
    version : str
        Current version string.
    tiers_supported : list[str]
        Tiers available (``["free", "pro", "enterprise"]``).
    status : BotStatus
        Operational status.
    capabilities : list[str]
        Key feature tags.
    owner_id : str
        Default owner / team.
    registered_at : str
        ISO-8601 UTC registration timestamp.
    """

    bot_id: str
    display_name: str
    description: str
    category: BotCategory
    module_path: str
    class_name: str
    version: str = "1.0.0"
    tiers_supported: list = field(default_factory=lambda: ["free", "pro", "enterprise"])
    status: BotStatus = BotStatus.ACTIVE
    capabilities: list = field(default_factory=list)
    owner_id: str = "dreamco"
    registered_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "bot_id": self.bot_id,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category.value,
            "module_path": self.module_path,
            "class_name": self.class_name,
            "version": self.version,
            "tiers_supported": list(self.tiers_supported),
            "status": self.status.value,
            "capabilities": list(self.capabilities),
            "owner_id": self.owner_id,
            "registered_at": self.registered_at,
        }


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class BotLibraryError(Exception):
    """Base exception for BotLibrary errors."""


class BotAlreadyRegistered(BotLibraryError):
    """Raised when a bot_id is already in the library."""


class BotNotFound(BotLibraryError):
    """Raised when a bot_id is not found in the library."""


# ---------------------------------------------------------------------------
# Bot Library
# ---------------------------------------------------------------------------

class BotLibrary:
    """
    Registry and catalogue of all DreamCo bots.

    Usage::

        library = BotLibrary()
        library.populate_dreamco_bots()   # registers all built-in bots
        entries = library.list_bots()
        entry   = library.get_bot("financial_literacy_bot")
    """

    def __init__(self) -> None:
        self._bots: dict[str, BotEntry] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, entry: BotEntry, *, overwrite: bool = False) -> BotEntry:
        """
        Add a bot to the library.

        Parameters
        ----------
        entry : BotEntry
            The bot to register.
        overwrite : bool
            When *True*, silently replace an existing entry with the same ID.

        Raises
        ------
        BotAlreadyRegistered
            If *overwrite* is False and the bot_id already exists.
        """
        if entry.bot_id in self._bots and not overwrite:
            raise BotAlreadyRegistered(
                f"Bot '{entry.bot_id}' is already registered. "
                "Use overwrite=True to replace it."
            )
        self._bots[entry.bot_id] = entry
        return entry

    def unregister(self, bot_id: str) -> None:
        """Remove a bot from the library."""
        self._bots.pop(bot_id, None)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_bot(self, bot_id: str) -> BotEntry:
        """
        Return the BotEntry for *bot_id*.

        Raises
        ------
        BotNotFound
        """
        if bot_id not in self._bots:
            raise BotNotFound(f"Bot '{bot_id}' not found in the library.")
        return self._bots[bot_id]

    def list_bots(
        self,
        category: Optional[BotCategory] = None,
        status: Optional[BotStatus] = None,
    ) -> list[dict]:
        """
        Return all bots, optionally filtered by category and/or status.
        """
        entries = self._bots.values()
        if category is not None:
            entries = [e for e in entries if e.category == category]
        if status is not None:
            entries = [e for e in entries if e.status == status]
        return [e.to_dict() for e in entries]

    def search(self, query: str) -> list[dict]:
        """
        Full-text search across bot_id, display_name, description, and capabilities.
        """
        q = query.lower()
        results = []
        for entry in self._bots.values():
            haystack = " ".join([
                entry.bot_id,
                entry.display_name,
                entry.description,
                " ".join(entry.capabilities),
            ]).lower()
            if q in haystack:
                results.append(entry.to_dict())
        return results

    def count(self) -> int:
        """Return total number of registered bots."""
        return len(self._bots)

    def get_stats(self) -> dict:
        """Return library statistics."""
        by_category: dict[str, int] = {}
        by_status: dict[str, int] = {}
        for entry in self._bots.values():
            by_category[entry.category.value] = by_category.get(entry.category.value, 0) + 1
            by_status[entry.status.value] = by_status.get(entry.status.value, 0) + 1
        return {
            "total_bots": len(self._bots),
            "by_category": by_category,
            "by_status": by_status,
        }

    # ------------------------------------------------------------------
    # Bulk load of all DreamCo bots
    # ------------------------------------------------------------------

    def populate_dreamco_bots(self) -> None:
        """Register all preexisting DreamCo bots in the library."""
        for entry in _DREAMCO_BOTS:
            self.register(entry, overwrite=True)


# ---------------------------------------------------------------------------
# Prebuilt catalogue — all DreamCo bots
# ---------------------------------------------------------------------------

_DREAMCO_BOTS: list[BotEntry] = [
    BotEntry(
        bot_id="resource_eligibility_bot",
        display_name="211 Resource Eligibility Bot",
        description="Matches users with local social services and resource programs.",
        category=BotCategory.GOVERNMENT,
        module_path="bots.211-resource-eligibility-bot.bot",
        class_name="ResourceEligibilityBot",
        capabilities=["resource_lookup", "eligibility_check", "referral"],
    ),
    BotEntry(
        bot_id="affiliate_bot",
        display_name="Affiliate Bot",
        description="Manages affiliate marketing programs, tracking, and payouts.",
        category=BotCategory.MARKETING,
        module_path="bots.affiliate_bot.affiliate_bot",
        class_name="AffiliateBot",
        capabilities=["affiliate_tracking", "commission", "link_generation"],
    ),
    BotEntry(
        bot_id="revenue_engine_bot",
        display_name="Revenue Engine Bot",
        description=(
            "DreamCo automated income infrastructure. Orchestrates Stripe + PayPal "
            "payments, affiliate auto-income, AI digital-product selling, and a "
            "real-estate deal pipeline with cross-stream revenue tracking."
        ),
        category=BotCategory.FINANCE,
        module_path="bots.revenue_engine_bot.revenue_engine_bot",
        class_name="RevenueEngineBot",
        capabilities=[
            "stripe_payments",
            "paypal_orders",
            "affiliate_automation",
            "digital_product_selling",
            "real_estate_deals",
            "revenue_tracking",
            "income_orchestration",
        ],
    ),
    BotEntry(
        bot_id="ai_models_integration",
        display_name="AI Models Integration Bot",
        description="Connects DreamCo bots with external AI models and APIs.",
        category=BotCategory.AI,
        module_path="bots.ai-models-integration.ai_models_integration",
        class_name="AIModelsIntegration",
        capabilities=["openai", "model_routing", "inference"],
    ),
    BotEntry(
        bot_id="ai_side_hustle_bot",
        display_name="AI Side Hustle Bot",
        description="Generates and manages AI-powered income streams.",
        category=BotCategory.BUSINESS,
        module_path="bots.ai-side-hustle-bots.bot",
        class_name="AISideHustleBot",
        capabilities=["income_generation", "gig_economy", "automation"],
    ),
    BotEntry(
        bot_id="ai_chatbot",
        display_name="AI Chatbot",
        description="General-purpose conversational AI for DreamCo users.",
        category=BotCategory.AI,
        module_path="bots.ai_chatbot.chatbot",
        class_name="AIchatbot",
        capabilities=["conversation", "nlp", "intent_detection"],
    ),
    BotEntry(
        bot_id="ai_learning_system",
        display_name="AI Learning System",
        description="Adaptive learning engine that evolves bot capabilities over time.",
        category=BotCategory.EDUCATION,
        module_path="bots.ai_learning_system.ai_learning_system",
        class_name="AILearningSystem",
        capabilities=["adaptive_learning", "analytics", "classifier"],
    ),
    BotEntry(
        bot_id="ai_level_up_bot",
        display_name="AI Level-Up Bot",
        description="Helps users learn AI skills through structured courses and challenges.",
        category=BotCategory.EDUCATION,
        module_path="bots.ai_level_up_bot.ai_level_up_bot",
        class_name="AILevelUpBot",
        capabilities=["skill_tree", "courses", "token_marketplace", "ai_agents"],
    ),
    BotEntry(
        bot_id="app_builder_bot",
        display_name="App Builder Bot",
        description="Generates and scaffolds full-stack applications on demand.",
        category=BotCategory.DEVELOPER_TOOLS,
        module_path="bots.app_builder_bot.app_builder_bot",
        class_name="AppBuilderBot",
        capabilities=["code_generation", "scaffolding", "deployment"],
    ),
    BotEntry(
        bot_id="big_bro_ai",
        display_name="Big Bro AI",
        description="Central AI mentor, coach, and bot factory for the DreamCo ecosystem.",
        category=BotCategory.AI,
        module_path="bots.big_bro_ai.big_bro_ai",
        class_name="BigBroAI",
        capabilities=[
            "mentorship", "bot_factory", "personality_engine",
            "courses", "memory_system", "sales_monetization",
        ],
    ),
    BotEntry(
        bot_id="bot_generator",
        display_name="Bot Generator",
        description="Generates new bots from specs using code generation and templates.",
        category=BotCategory.DEVELOPER_TOOLS,
        module_path="bots.bot_generator.code_generator",
        class_name="CodeGenerator",
        capabilities=["code_generation", "benchmarking", "revenue_tracking"],
    ),
    BotEntry(
        bot_id="bot_generator_bot",
        display_name="Bot Generator Bot",
        description="High-level bot that orchestrates bot creation workflows.",
        category=BotCategory.DEVELOPER_TOOLS,
        module_path="bots.bot_generator_bot.bot_generator_bot",
        class_name="BotGeneratorBot",
        capabilities=["bot_creation", "template_engine", "deployment"],
    ),
    BotEntry(
        bot_id="buddy_bot",
        display_name="Buddy Bot",
        description=(
            "DreamCo's most human-like AI companion. Features natural conversation, "
            "emotion detection, long-term memory, 3D avatars, AR/VR presence, voice "
            "synthesis and cloning (consent-gated), creativity tools, gamified "
            "productivity, and dynamic personas (mentor, friend, coach, cheerleader)."
        ),
        category=BotCategory.AI,
        module_path="bots.buddy_bot.buddy_bot",
        class_name="BuddyBot",
        capabilities=[
            "conversational_ai",
            "emotion_detection",
            "long_term_memory",
            "milestone_tracker",
            "avatar_3d",
            "ar_vr_presence",
            "voice_synthesis",
            "voice_cloning",
            "gan_image_mimicry",
            "holographic_projection",
            "multilingual",
            "creativity_engine",
            "storytelling",
            "songwriting",
            "gamified_productivity",
            "dynamic_personas",
            "conflict_resolution",
            "wellness_tracker",
            "ethical_ai",
        ],
    ),
    BotEntry(
        bot_id="buddy_os",
        display_name="Buddy OS",
        description="Mobile-first OS framework for managing DreamCo bots on-device.",
        category=BotCategory.SYSTEM,
        module_path="bots.buddy_os.buddy_os",
        class_name="BuddyOS",
        capabilities=["device_manager", "bluetooth", "cast_engine", "app_framework"],
    ),
    BotEntry(
        bot_id="car_flipping_bot",
        display_name="Car Flipping Bot",
        description="Automates car research, valuation, and flipping workflows.",
        category=BotCategory.BUSINESS,
        module_path="bots.car_flipping_bot.car_flipping_bot",
        class_name="CarFlippingBot",
        capabilities=["valuation", "listing", "deal_analysis"],
    ),
    BotEntry(
        bot_id="ci_auto_fix_bot",
        display_name="CI Auto-Fix Bot",
        description="Automatically detects and fixes CI pipeline failures.",
        category=BotCategory.DEVELOPER_TOOLS,
        module_path="bots.ci_auto_fix_bot.ci_auto_fix_bot",
        class_name="CIAutoFixBot",
        capabilities=["ci_monitoring", "auto_fix", "github_integration"],
    ),
    BotEntry(
        bot_id="control_center",
        display_name="Control Center",
        description="Central hub for monitoring, deploying, and managing all DreamCo bots.",
        category=BotCategory.SYSTEM,
        module_path="bots.control_center.control_center",
        class_name="ControlCenter",
        capabilities=["bot_registry", "heartbeat", "github_integration", "dashboard"],
    ),
    BotEntry(
        bot_id="crypto_bot",
        display_name="Crypto Bot",
        description="Crypto trading, portfolio management, and mining automation.",
        category=BotCategory.CRYPTO,
        module_path="bots.crypto_bot.crypto_bot",
        class_name="CryptoBot",
        capabilities=["trading", "portfolio", "mining", "price_feed", "dashboard"],
    ),
    BotEntry(
        bot_id="deal_finder_bot",
        display_name="Deal Finder Bot",
        description="Scouts deals across multiple platforms and alerts on opportunities.",
        category=BotCategory.BUSINESS,
        module_path="bots.deal_finder_bot.deal_finder_bot",
        class_name="DealFinderBot",
        capabilities=["deal_scouting", "alerts", "comparison"],
    ),
    BotEntry(
        bot_id="dreamco_empire_os",
        display_name="DreamCo Empire OS",
        description="Master operating system for running the full DreamCo business empire.",
        category=BotCategory.SYSTEM,
        module_path="bots.dreamco_empire_os.empire_os",
        class_name="EmpireOS",
        capabilities=[
            "ai_leaders", "bot_fleet", "marketplace", "deal_analyzer",
            "revenue_tracker", "cost_tracking", "orchestration",
        ],
    ),
    BotEntry(
        bot_id="dreamco_payments",
        display_name="DreamCo Payments",
        description="Unified payment processing, account management, and reporting.",
        category=BotCategory.PAYMENTS,
        module_path="bots.dreamco_payments.dreamco_payments",
        class_name="DreamcoPayments",
        capabilities=["stripe", "account_manager", "payment_processor", "reporting"],
    ),
    BotEntry(
        bot_id="financial_literacy_bot",
        display_name="Financial Literacy Bot",
        description="Educates users on credit building, OPM strategies, and investing.",
        category=BotCategory.FINANCE,
        module_path="bots.financial_literacy_bot.financial_literacy_bot",
        class_name="FinancialLiteracyBot",
        capabilities=[
            "credit_tips", "credit_alerts", "investment_calculator",
            "opm_strategies", "education_paths", "community",
        ],
    ),
    BotEntry(
        bot_id="fiverr_bot",
        display_name="Fiverr Bot",
        description="Full freelance marketplace: gigs, proposals, milestones, payments.",
        category=BotCategory.FREELANCE,
        module_path="bots.fiverr_bot.fiverr_bot",
        class_name="FiverrBot",
        capabilities=[
            "freelancer_registration", "gig_posting", "proposals",
            "milestones", "stripe_payments", "admin_dashboard",
        ],
    ),
    BotEntry(
        bot_id="government_contract_grant_bot",
        display_name="Government Contract & Grant Bot",
        description="Identifies, applies for, and tracks government contracts and grants.",
        category=BotCategory.GOVERNMENT,
        module_path="bots.government-contract-grant-bot.government_contract_grant_bot",
        class_name="GovernmentContractGrantBot",
        capabilities=["contract_search", "grant_search", "application_tracking"],
    ),
    BotEntry(
        bot_id="job_titles_bot",
        display_name="Job Titles Bot",
        description="AI job-role database, generator, and cost-justification engine.",
        category=BotCategory.JOB,
        module_path="bots.job_titles_bot.job_titles_bot",
        class_name="JobTitlesBot",
        capabilities=["job_database", "role_generation", "cost_justification", "trainer"],
    ),
    BotEntry(
        bot_id="mining_bot",
        display_name="Mining Bot",
        description="Automates resource and crypto mining workflows.",
        category=BotCategory.MINING,
        module_path="bots.mining_bot.mining_bot",
        class_name="MiningBot",
        capabilities=["crypto_mining", "resource_tracking", "profit_analysis"],
    ),
    BotEntry(
        bot_id="legal_money_bot",
        display_name="LegalMoneyBot",
        description=(
            "AI-powered legal claim discovery, eligibility scoring, settlement "
            "maximization, and auto-filing assistant. Connects users with "
            "contingency-based attorneys."
        ),
        category=BotCategory.FINANCE,
        module_path="bots.legal_money_bot.legal_money_bot",
        class_name="LegalMoneyBot",
        capabilities=[
            "claim_finder",
            "eligibility_scoring",
            "settlement_maximizer",
            "lawyer_matching",
            "auto_filing",
            "referral_tracking",
            "notifications",
        ],
    ),
    BotEntry(
        bot_id="money_finder_bot",
        display_name="Money Finder Bot",
        description="Discovers income opportunities, grants, and financial resources.",
        category=BotCategory.FINANCE,
        module_path="bots.money_finder_bot.money_finder_bot",
        class_name="MoneyFinderBot",
        capabilities=["opportunity_discovery", "grants", "income_streams"],
    ),
    BotEntry(
        bot_id="multi_source_lead_scraper",
        display_name="Multi-Source Lead Scraper",
        description="Aggregates leads from multiple sources with scoring and CRM export.",
        category=BotCategory.LEAD_GEN,
        module_path="bots.multi_source_lead_scraper.lead_scraper",
        class_name="MultiSourceLeadScraper",
        capabilities=["lead_scraping", "lead_scoring", "crm_export"],
    ),
    BotEntry(
        bot_id="open_claw_bot",
        display_name="OpenClaw Bot",
        description="AI-powered strategy engine for trading, clients, and market intel.",
        category=BotCategory.AI,
        module_path="bots.open_claw_bot.open_claw_bot",
        class_name="OpenClawBot",
        capabilities=[
            "strategy_engine", "ai_models", "client_manager",
            "data_analysis", "ml_ensemble", "realtime_signals",
        ],
    ),
    BotEntry(
        bot_id="real_estate_bot",
        display_name="Real Estate Bot",
        description="Property search, valuation, deal analysis, and rental management.",
        category=BotCategory.REAL_ESTATE,
        module_path="bots.real_estate_bot.real_estate_bot",
        class_name="RealEstateBot",
        capabilities=["property_search", "valuation", "deal_analysis", "rental"],
    ),
    BotEntry(
        bot_id="selenium_job_application_bot",
        display_name="Selenium Job Application Bot",
        description="Automates job applications across multiple platforms.",
        category=BotCategory.JOB,
        module_path="bots.selenium-job-application-bot.bot",
        class_name="SeleniumJobApplicationBot",
        capabilities=["job_search", "auto_apply", "form_filling"],
    ),
    BotEntry(
        bot_id="software_bot",
        display_name="Software Bot",
        description="Builds, tests, and deploys software projects end-to-end.",
        category=BotCategory.DEVELOPER_TOOLS,
        module_path="bots.software_bot.software_bot",
        class_name="SoftwareBot",
        capabilities=["code_generation", "testing", "deployment", "devops"],
    ),
    BotEntry(
        bot_id="alidropship_money_bot",
        display_name="AliDropship Money Bot",
        description=(
            "Autonomous DreamCo-level dropshipping empire: finds winning products, "
            "builds WordPress + AliDropship stores, prices for profit, auto-fulfills "
            "orders, drives TikTok/Facebook traffic, and scales winners automatically."
        ),
        category=BotCategory.BUSINESS,
        module_path="bots.alidropship_money_bot.alidropship_money_bot",
        class_name="AliDropshipMoneyBot",
        capabilities=[
            "product_discovery",
            "store_builder",
            "pricing_engine",
            "auto_fulfillment",
            "tiktok_viral_bot",
            "facebook_ads_bot",
            "influencer_outreach",
            "scaling_engine",
            "multi_store",
            "self_marketing_network",
        ],
    ),
    BotEntry(
        bot_id="cinecore_bot",
        display_name="DreamCo CineCore Bot",
        description=(
            "AI-Powered Commercial & Video Creation System. Automates script "
            "generation, AI video creation (Runway/Pika), voiceovers, multi-platform "
            "ad distribution, legal lead generation, AI deal closing, Stripe billing, "
            "CRM, bulk commercial generation, and self-healing system monitoring."
        ),
        category=BotCategory.MARKETING,
        module_path="bots.cinecore_bot.cinecore_bot",
        class_name="CineCoreBot",
        capabilities=[
            "script_generation",
            "ai_video_generation",
            "voiceover_creation",
            "platform_optimization",
            "lead_generation",
            "business_scoring",
            "ai_closer",
            "stripe_billing",
            "analytics_engine",
            "bulk_generator",
            "self_healing",
            "crm",
            "auto_posting",
        ],
    ),
    # -- Category bots --
    BotEntry(
        bot_id="app_bots_category",
        display_name="App Bots (Category)",
        description="Collection of app-building and mobile development bots.",
        category=BotCategory.APP,
        module_path="App_bots.feature_1",
        class_name="AppBotFeature",
        capabilities=["app_development", "mobile", "scaffolding"],
    ),
    BotEntry(
        bot_id="business_bots_category",
        display_name="Business Bots (Category)",
        description="Bots for automating business operations and workflows.",
        category=BotCategory.BUSINESS,
        module_path="Business_bots.feature_1",
        class_name="BusinessBotFeature",
        capabilities=["business_automation", "workflows", "reporting"],
    ),
    BotEntry(
        bot_id="fiverr_bots_category",
        display_name="Fiverr Bots (Category)",
        description="Freelance-focused bots for Fiverr-style platforms.",
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.feature_1",
        class_name="FiverrBotFeature",
        capabilities=["freelancing", "gig_management", "proposals"],
    ),
    BotEntry(
        bot_id="marketing_bots_category",
        display_name="Marketing Bots (Category)",
        description="Bots for campaign management, lead gen, and brand growth.",
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.feature_1",
        class_name="MarketingBotFeature",
        capabilities=["campaigns", "lead_gen", "seo", "social_media"],
    ),
    BotEntry(
        bot_id="occupational_bots_category",
        display_name="Occupational Bots (Category)",
        description="Career and occupation-specific automation bots.",
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.feature_1",
        class_name="OccupationalBotFeature",
        capabilities=["career", "job_market", "skills"],
    ),
    BotEntry(
        bot_id="real_estate_bots_category",
        display_name="Real Estate Bots (Category)",
        description="Real estate analysis and management bots collection.",
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.feature_1",
        class_name="RealEstateBotFeature",
        capabilities=["property_analysis", "market_data", "rental"],
    ),
    BotEntry(
        bot_id="enterprise_integrations_bot",
        display_name="Enterprise Integrations Bot",
        description=(
            "Unified gateway for Big Tech & AI services (Google Cloud AI, IBM Watson, "
            "Microsoft Azure AI, Nvidia AI, AWS), Big Data/Analytics (Databricks, "
            "Palantir, Snowflake, Tableau), Communication & Collaboration (Slack, "
            "Teams, Zoom), subscription resales, and proprietary Dream AI Models."
        ),
        category=BotCategory.AI,
        module_path="bots.enterprise_integrations_bot.enterprise_integrations_bot",
        class_name="EnterpriseIntegrationsBot",
        capabilities=[
            "google_cloud_ai", "ibm_watson", "azure_ai", "nvidia_ai", "aws_ai",
            "databricks", "palantir", "snowflake", "tableau",
            "slack", "teams", "zoom",
            "dream_llm", "dream_vision", "dream_voice", "dream_code",
            "dream_analytics", "dream_collab",
            "subscription_resales", "multi_provider_routing",
        ],
    ),
    BotEntry(
        bot_id="stack_and_profit_bot",
        display_name="Stack & Profit AI Bot",
        description=(
            "DreamCo $1,000 Launch Plan bot. Orchestrates dealBot, pennyBot, "
            "receiptBot, flipBot, and couponBot with AI profit ranking and alert "
            "engine. Covers clearance, penny deals, receipt cashback, local flips, "
            "and coupon stacking across 50+ real deal sources."
        ),
        category=BotCategory.MARKETPLACE,
        module_path="bots.stack_and_profit_bot.stack_and_profit_bot",
        class_name="StackAndProfitBot",
        capabilities=[
            "deal_scanning", "penny_deals", "receipt_cashback",
            "flip_finding", "coupon_stacking", "profit_calculator",
            "ai_ranking", "deal_alerts", "affiliate_links",
            "referral_system", "premium_subscription",
        ],
    ),
    BotEntry(
        bot_id="model_router_bot",
        display_name="DreamCo Model Router",
        description=(
            "AI brain switchboard for all DreamCo bots. Classifies incoming tasks "
            "and routes them to the optimal AI provider: Anthropic for coding, "
            "OpenAI for general tasks, Google for vision, Mistral for cost-efficient "
            "scale, Cohere for search/RAG, and xAI for real-time data. Includes a "
            "ResourceManager action layer (email, CRM, payments, data) so agents can "
            "take real-world actions after model inference."
        ),
        category=BotCategory.AI,
        module_path="ai.router_agent",
        class_name="RouterAgent",
        capabilities=[
            "model_routing",
            "task_classification",
            "multi_provider",
            "coding_tasks",
            "vision_tasks",
            "search_rag",
            "real_time_data",
            "cost_optimisation",
            "resource_manager",
            "email_action",
            "crm_action",
            "payment_action",
            "data_fetch",
        ],
    ),
    BotEntry(
        bot_id="quantum_decision_bot",
        display_name="Quantum Decision Bot",
        description=(
            "DreamCo Reality Optimization System. Simulates thousands of outcome "
            "paths using Monte Carlo methods, assigns probabilities, and collapses to "
            "the highest-return decision path. Features a multi-dimensional decision "
            "mapper (time/capital/risk/scale), an entangled bot network router that "
            "propagates decisions to all connected bots instantly, and an autonomous "
            "money scanner that ranks income opportunities by quantum score."
        ),
        category=BotCategory.AI,
        module_path="bots.quantum_decision_bot.quantum_decision_bot",
        class_name="QuantumDecisionBot",
        capabilities=[
            "quantum_decision_engine",
            "monte_carlo_simulation",
            "probability_model",
            "wave_function_collapse",
            "dimension_mapper",
            "entangled_bot_router",
            "autonomous_money_scanner",
            "multi_path_tracker",
            "self_improving_ai",
            "god_mode",
        ],
    ),
    BotEntry(
        bot_id="public_lead_engine",
        display_name="Public Lead Engine",
        description=(
            "Scrapes public business data (Google Places, Yelp, and more) to find "
            "leads with weak marketing signals, scores them for outreach opportunity, "
            "generates call scripts, and automates CRM export."
        ),
        category=BotCategory.LEAD_GEN,
        module_path="bots.public_lead_engine.public_lead_engine",
        class_name="PublicLeadEngine",
        capabilities=[
            "google_places_search",
            "yelp_search",
            "rating_filter",
            "weak_marketing_filter",
            "ad_score",
            "script_generation",
            "outreach_draft",
            "crm_export",
            "multi_api",
            "ai_opportunity_score",
            "bulk_search",
            "analytics",
            "white_label",
        ],
    ),
    BotEntry(
        bot_id="cinecore_lead_engine",
        display_name="CineCore Lead Engine",
        description=(
            "Finds and qualifies leads in the film, media, and entertainment industry "
            "by scraping public directories, scoring opportunities, and generating "
            "outreach scripts tailored to the cinematic sector."
        ),
        category=BotCategory.LEAD_GEN,
        module_path="bots.cinecore_lead_engine.cinecore_lead_engine",
        class_name="CineCoreLeadEngine",
        capabilities=[
            "business_scan",
            "script_generation",
            "crm_export",
            "lead_scoring",
            "outreach_draft",
            "analytics",
        ],
    ),
    BotEntry(
        bot_id="god_mode_bot",
        display_name="God Mode Bot",
        description=(
            "DreamCo's Autonomous Business Operator. Orchestrates five specialised "
            "engines: AutoClientHunter for lead scraping, AutoCloser for 7-stage "
            "negotiation, PaymentAutoCollector for subscription billing, ViralEngine "
            "for trend-driven content, and SelfImprovingAI for continuous performance "
            "optimisation. Tier-gated from FREE to ENTERPRISE."
        ),
        category=BotCategory.BUSINESS,
        module_path="bots.god_mode_bot.god_mode_bot",
        class_name="GodModeBot",
        capabilities=[
            "lead_hunting",
            "auto_closing",
            "payment_collection",
            "viral_engine",
            "self_improving_ai",
            "god_mode",
            "niche_targeting",
            "subscription_billing",
            "analytics",
        ],
    ),
    BotEntry(
        bot_id="sql_bot",
        display_name="SQL Bot",
        description=(
            "AI-powered SQL bot for dynamic database operations. Executes safe, "
            "validated SQL queries for data insertion, updates, analytical reports, "
            "and schema inspection. Includes query safety guardrails that block "
            "destructive operations, a natural language query interface, and automated "
            "database integrity checks."
        ),
        category=BotCategory.DEVELOPER_TOOLS,
        module_path="bots.sql_bot.sql_bot",
        class_name="SQLBot",
        capabilities=[
            "query_execution",
            "query_validation",
            "safety_guardrails",
            "data_insertion",
            "data_update",
            "analytical_reports",
            "schema_inspection",
            "integrity_checks",
            "natural_language_sql",
            "sqlite_backend",
        ],
    ),
    BotEntry(
        bot_id="company_lookup_bot",
        display_name="Company Lookup Bot",
        description=(
            "Autonomous company research system. Looks up companies via GitHub "
            "Actions workflow_dispatch triggers, fetches data from Crunchbase, "
            "Clearbit, and a built-in catalogue, saves results to "
            "data/companies.json, and sends Slack notifications with integration "
            "recommendations."
        ),
        category=BotCategory.BUSINESS,
        module_path="bots.company_lookup_bot.company_lookup_bot",
        class_name="CompanyLookupBot",
        capabilities=[
            "company_lookup",
            "crunchbase_integration",
            "clearbit_integration",
            "data_enrichment",
            "slack_notifications",
            "integration_recommendations",
            "csv_export",
            "bulk_import",
            "github_actions_trigger",
        ],
    ),
    BotEntry(
        bot_id="integration_feedback_bot",
        display_name="Integration Feedback Bot",
        description=(
            "Tracks WordPress, Wix, Streamlit, MySQL, Docker, Terraform, and other "
            "platform integration tasks. Logs every success and failure with timestamps "
            "and reasons to data/integration_log.json, sends real-time Slack and Discord "
            "notifications, provides platform-specific auto-heal suggestions, and supports "
            "daily/weekly/monthly analytics reporting."
        ),
        category=BotCategory.AUTOMATION,
        module_path="bots.integration_feedback_bot.integration_feedback_bot",
        class_name="IntegrationFeedbackBot",
        capabilities=[
            "integration_tracking",
            "slack_notifications",
            "discord_notifications",
            "auto_heal",
            "analytics",
            "period_analytics",
            "csv_export",
            "webhook_delivery",
            "webhook_signing",
            "wordpress_support",
            "wix_support",
            "streamlit_support",
            "mysql_support",
            "docker_support",
            "terraform_support",
            "github_actions_trigger",
        ],
    ),

    # -- Category Bots: App / Business / Fiverr / Marketing / Occupational / Real Estate --

    BotEntry(
        bot_id="app_ab_testing_bot",
        display_name="App Ab Testing Bot",
        description=(
            "Manages A/B test experiments for mobile apps, tracks variants, measures conversions, and surfaces winning configurations."
        ),
        category=BotCategory.APP,
        module_path="App_bots.ab_testing_bot",
        class_name="ABTestingBot",
        capabilities=["ab_testing", "experiment_management", "split_testing", "analytics"],
    ),
    BotEntry(
        bot_id="accessibility_bot",
        display_name="Accessibility Bot",
        description=(
            "Audits mobile apps for WCAG accessibility compliance, flags issues, and generates remediation recommendations."
        ),
        category=BotCategory.APP,
        module_path="App_bots.accessibility_bot",
        class_name="AccessibilityBot",
        capabilities=["accessibility_audit", "wcag_compliance", "a11y"],
    ),
    BotEntry(
        bot_id="analytics_bot",
        display_name="Analytics Bot",
        description=(
            "Aggregates in-app analytics events, builds usage dashboards, and surfaces actionable growth insights."
        ),
        category=BotCategory.APP,
        module_path="App_bots.analytics_bot",
        class_name="AnalyticsBot",
        capabilities=["analytics", "metrics", "reporting", "data_insights"],
    ),
    BotEntry(
        bot_id="api_rate_limiter_bot",
        display_name="Api Rate Limiter Bot",
        description=(
            "Monitors and enforces API rate limits, queues requests intelligently, and alerts on quota exhaustion."
        ),
        category=BotCategory.APP,
        module_path="App_bots.api_rate_limiter_bot",
        class_name="APIRateLimiterBot",
        capabilities=["rate_limiting", "api_management", "throttling"],
    ),
    BotEntry(
        bot_id="app_store_optimizer_bot",
        display_name="App Store Optimizer Bot",
        description=(
            "Optimizes App Store listings with keyword research, metadata suggestions, and rating improvement strategies."
        ),
        category=BotCategory.APP,
        module_path="App_bots.app_store_optimizer_bot",
        class_name="AppStoreOptimizerBot",
        capabilities=["aso", "keyword_optimization", "app_store", "ratings"],
    ),
    BotEntry(
        bot_id="beta_tester_bot",
        display_name="Beta Tester Bot",
        description=(
            "Manages beta testing programs, collects structured feedback, triages bugs, and tracks issue resolution."
        ),
        category=BotCategory.APP,
        module_path="App_bots.beta_tester_bot",
        class_name="BetaTesterBot",
        capabilities=["beta_testing", "qa", "feedback_collection", "bug_reporting"],
    ),
    BotEntry(
        bot_id="books_app_bot",
        display_name="Books App Bot",
        description=(
            "Powers book discovery, reading progress tracking, library organisation, and personalised reading recommendations."
        ),
        category=BotCategory.APP,
        module_path="App_bots.books_app_bot",
        class_name="BooksAppBot",
        capabilities=["books", "reading", "library", "content_discovery"],
    ),
    BotEntry(
        bot_id="business_app_bot",
        display_name="Business App Bot",
        description=(
            "Automates business productivity workflows, document handling, and enterprise team collaboration tools."
        ),
        category=BotCategory.APP,
        module_path="App_bots.business_app_bot",
        class_name="BusinessAppBot",
        capabilities=["business_tools", "productivity", "enterprise"],
    ),
    BotEntry(
        bot_id="churn_predictor_bot",
        display_name="Churn Predictor Bot",
        description=(
            "Uses ML signals to predict users at risk of churning and triggers targeted retention campaigns."
        ),
        category=BotCategory.APP,
        module_path="App_bots.churn_predictor_bot",
        class_name="ChurnPredictorBot",
        capabilities=["churn_prediction", "retention", "ml", "analytics"],
    ),
    BotEntry(
        bot_id="crash_reporter_bot",
        display_name="Crash Reporter Bot",
        description=(
            "Captures, groups, and prioritises crash reports with stack traces and device context."
        ),
        category=BotCategory.APP,
        module_path="App_bots.crash_reporter_bot",
        class_name="CrashReporterBot",
        capabilities=["crash_reporting", "error_tracking", "monitoring"],
    ),
    BotEntry(
        bot_id="deep_link_bot",
        display_name="Deep Link Bot",
        description=(
            "Generates and validates deep links for seamless in-app navigation and deferred user routing."
        ),
        category=BotCategory.APP,
        module_path="App_bots.deep_link_bot",
        class_name="DeepLinkBot",
        capabilities=["deep_linking", "navigation", "user_routing"],
    ),
    BotEntry(
        bot_id="education_app_bot",
        display_name="Education App Bot",
        description=(
            "Manages course content, quizzes, progress tracking, and adaptive learning paths for education apps."
        ),
        category=BotCategory.APP,
        module_path="App_bots.education_app_bot",
        class_name="EducationAppBot",
        capabilities=["education", "learning", "courses", "quizzes"],
    ),
    BotEntry(
        bot_id="entertainment_app_bot",
        display_name="Entertainment App Bot",
        description=(
            "Curates and serves entertainment content including video, audio, and interactive media experiences."
        ),
        category=BotCategory.APP,
        module_path="App_bots.entertainment_app_bot",
        class_name="EntertainmentAppBot",
        capabilities=["entertainment", "media", "content"],
    ),
    BotEntry(
        bot_id="finance_app_bot",
        display_name="Finance App Bot",
        description=(
            "Handles personal finance features including budgeting, spend tracking, and payment integrations."
        ),
        category=BotCategory.APP,
        module_path="App_bots.finance_app_bot",
        class_name="FinanceAppBot",
        capabilities=["finance", "budgeting", "payments", "banking"],
    ),
    BotEntry(
        bot_id="food_drink_app_bot",
        display_name="Food Drink App Bot",
        description=(
            "Manages restaurant discovery, menu browsing, order placement, and food delivery workflows."
        ),
        category=BotCategory.APP,
        module_path="App_bots.food_drink_app_bot",
        class_name="FoodDrinkAppBot",
        capabilities=["food", "restaurants", "ordering", "delivery"],
    ),
    BotEntry(
        bot_id="games_app_bot",
        display_name="Games App Bot",
        description=(
            "Implements gaming features including leaderboards, achievements, in-game events, and social play."
        ),
        category=BotCategory.APP,
        module_path="App_bots.games_app_bot",
        class_name="GamesAppBot",
        capabilities=["games", "gaming", "leaderboards", "achievements"],
    ),
    BotEntry(
        bot_id="gamification_bot",
        display_name="Gamification Bot",
        description=(
            "Adds points, badges, streaks, and reward systems to drive user engagement and retention."
        ),
        category=BotCategory.APP,
        module_path="App_bots.gamification_bot",
        class_name="GamificationBot",
        capabilities=["gamification", "rewards", "engagement", "points"],
    ),
    BotEntry(
        bot_id="health_fitness_app_bot",
        display_name="Health Fitness App Bot",
        description=(
            "Tracks workouts, nutrition, health metrics, and personalised fitness goal progress."
        ),
        category=BotCategory.APP,
        module_path="App_bots.health_fitness_app_bot",
        class_name="HealthFitnessAppBot",
        capabilities=["health", "fitness", "workout", "nutrition"],
    ),
    BotEntry(
        bot_id="in_app_purchase_bot",
        display_name="In App Purchase Bot",
        description=(
            "Manages in-app purchase flows, product catalogues, receipt validation, and subscription state."
        ),
        category=BotCategory.APP,
        module_path="App_bots.in_app_purchase_bot",
        class_name="InAppPurchaseBot",
        capabilities=["iap", "monetization", "purchases", "subscriptions"],
    ),
    BotEntry(
        bot_id="kids_family_app_bot",
        display_name="Kids Family App Bot",
        description=(
            "Provides family-friendly features including parental controls, educational content, and safe experiences."
        ),
        category=BotCategory.APP,
        module_path="App_bots.kids_family_app_bot",
        class_name="KidsFamilyAppBot",
        capabilities=["kids", "family", "parental_controls", "education"],
    ),
    BotEntry(
        bot_id="lifestyle_app_bot",
        display_name="Lifestyle App Bot",
        description=(
            "Supports lifestyle tracking including habits, wellness routines, and daily goal completion."
        ),
        category=BotCategory.APP,
        module_path="App_bots.lifestyle_app_bot",
        class_name="LifestyleAppBot",
        capabilities=["lifestyle", "wellness", "habits"],
    ),
    BotEntry(
        bot_id="localization_bot",
        display_name="Localization Bot",
        description=(
            "Automates app localisation with string extraction, translation management, and locale testing."
        ),
        category=BotCategory.APP,
        module_path="App_bots.localization_bot",
        class_name="LocalizationBot",
        capabilities=["localization", "i18n", "translation", "multi_language"],
    ),
    BotEntry(
        bot_id="medical_app_bot",
        display_name="Medical App Bot",
        description=(
            "Supports medical app workflows including patient data, appointment scheduling, and telemedicine features."
        ),
        category=BotCategory.APP,
        module_path="App_bots.medical_app_bot",
        class_name="MedicalAppBot",
        capabilities=["medical", "healthcare", "telemedicine"],
    ),
    BotEntry(
        bot_id="monetization_bot",
        display_name="Monetization Bot",
        description=(
            "Implements and optimises multiple monetisation strategies including ads, subscriptions, and IAPs."
        ),
        category=BotCategory.APP,
        module_path="App_bots.monetization_bot",
        class_name="MonetizationBot",
        capabilities=["monetization", "revenue", "ads", "subscriptions"],
    ),
    BotEntry(
        bot_id="music_app_bot",
        display_name="Music App Bot",
        description=(
            "Powers music streaming, playlist management, social listening, and personalised audio recommendations."
        ),
        category=BotCategory.APP,
        module_path="App_bots.music_app_bot",
        class_name="MusicAppBot",
        capabilities=["music", "streaming", "playlists", "audio"],
    ),
    BotEntry(
        bot_id="navigation_app_bot",
        display_name="Navigation App Bot",
        description=(
            "Provides turn-by-turn navigation, route optimisation, real-time traffic, and location services."
        ),
        category=BotCategory.APP,
        module_path="App_bots.navigation_app_bot",
        class_name="NavigationAppBot",
        capabilities=["navigation", "maps", "gps", "routing"],
    ),
    BotEntry(
        bot_id="news_app_bot",
        display_name="News App Bot",
        description=(
            "Aggregates and personalises news feeds, manages subscriptions, and drives content engagement."
        ),
        category=BotCategory.APP,
        module_path="App_bots.news_app_bot",
        class_name="NewsAppBot",
        capabilities=["news", "articles", "feed", "content"],
    ),
    BotEntry(
        bot_id="onboarding_funnel_bot",
        display_name="Onboarding Funnel Bot",
        description=(
            "Designs and optimises user onboarding flows to maximise activation and reduce time-to-value."
        ),
        category=BotCategory.APP,
        module_path="App_bots.onboarding_funnel_bot",
        class_name="OnboardingFunnelBot",
        capabilities=["onboarding", "user_flow", "conversion", "tutorial"],
    ),
    BotEntry(
        bot_id="payment_gateway_bot",
        display_name="Payment Gateway Bot",
        description=(
            "Integrates and manages payment gateway connections, checkout flows, and transaction processing."
        ),
        category=BotCategory.APP,
        module_path="App_bots.payment_gateway_bot",
        class_name="PaymentGatewayBot",
        capabilities=["payments", "gateway", "checkout", "transactions"],
    ),
    BotEntry(
        bot_id="performance_monitor_bot",
        display_name="Performance Monitor Bot",
        description=(
            "Monitors app performance metrics including load times, frame rates, and resource usage."
        ),
        category=BotCategory.APP,
        module_path="App_bots.performance_monitor_bot",
        class_name="PerformanceMonitorBot",
        capabilities=["performance", "monitoring", "apm", "metrics"],
    ),
    BotEntry(
        bot_id="personalization_bot",
        display_name="Personalization Bot",
        description=(
            "Delivers ML-powered personalisation for content recommendations and tailored user experiences."
        ),
        category=BotCategory.APP,
        module_path="App_bots.personalization_bot",
        class_name="PersonalizationBot",
        capabilities=["personalization", "recommendations", "ml", "user_profiles"],
    ),
    BotEntry(
        bot_id="photo_video_app_bot",
        display_name="Photo Video App Bot",
        description=(
            "Handles photo and video capture, editing, storage, and sharing features for media apps."
        ),
        category=BotCategory.APP,
        module_path="App_bots.photo_video_app_bot",
        class_name="PhotoVideoAppBot",
        capabilities=["photos", "video", "editing", "media"],
    ),
    BotEntry(
        bot_id="productivity_app_bot",
        display_name="Productivity App Bot",
        description=(
            "Powers task management, note-taking, calendar integration, and team productivity workflows."
        ),
        category=BotCategory.APP,
        module_path="App_bots.productivity_app_bot",
        class_name="ProductivityAppBot",
        capabilities=["productivity", "tasks", "notes", "calendar"],
    ),
    BotEntry(
        bot_id="push_notification_bot",
        display_name="Push Notification Bot",
        description=(
            "Manages push notification campaigns, segmentation, scheduling, and delivery analytics."
        ),
        category=BotCategory.APP,
        module_path="App_bots.push_notification_bot",
        class_name="PushNotificationBot",
        capabilities=["push_notifications", "alerts", "messaging"],
    ),
    BotEntry(
        bot_id="reference_app_bot",
        display_name="Reference App Bot",
        description=(
            "Provides reference content management including dictionaries, encyclopaedias, and knowledge bases."
        ),
        category=BotCategory.APP,
        module_path="App_bots.reference_app_bot",
        class_name="ReferenceAppBot",
        capabilities=["reference", "dictionary", "knowledge_base"],
    ),
    BotEntry(
        bot_id="referral_program_bot",
        display_name="Referral Program Bot",
        description=(
            "Automates referral program mechanics including invite generation, tracking, and reward fulfilment."
        ),
        category=BotCategory.APP,
        module_path="App_bots.referral_program_bot",
        class_name="ReferralProgramBot",
        capabilities=["referrals", "growth", "viral", "rewards"],
    ),
    BotEntry(
        bot_id="review_collector_bot",
        display_name="Review Collector Bot",
        description=(
            "Prompts users for reviews at optimal moments, analyses feedback, and manages app store ratings."
        ),
        category=BotCategory.APP,
        module_path="App_bots.review_collector_bot",
        class_name="ReviewCollectorBot",
        capabilities=["reviews", "ratings", "feedback", "nps"],
    ),
    BotEntry(
        bot_id="session_tracker_bot",
        display_name="Session Tracker Bot",
        description=(
            "Tracks user session data including duration, screens visited, events, and engagement depth."
        ),
        category=BotCategory.APP,
        module_path="App_bots.session_tracker_bot",
        class_name="SessionTrackerBot",
        capabilities=["sessions", "analytics", "user_behavior"],
    ),
    BotEntry(
        bot_id="shopping_app_bot",
        display_name="Shopping App Bot",
        description=(
            "Manages shopping experiences including product discovery, cart management, and checkout optimisation."
        ),
        category=BotCategory.APP,
        module_path="App_bots.shopping_app_bot",
        class_name="ShoppingAppBot",
        capabilities=["shopping", "ecommerce", "cart", "checkout"],
    ),
    BotEntry(
        bot_id="social_networking_app_bot",
        display_name="Social Networking App Bot",
        description=(
            "Powers social networking features including feeds, profiles, connections, and community tools."
        ),
        category=BotCategory.APP,
        module_path="App_bots.social_networking_app_bot",
        class_name="SocialNetworkingAppBot",
        capabilities=["social", "networking", "community", "feed"],
    ),
    BotEntry(
        bot_id="social_sharing_bot",
        display_name="Social Sharing Bot",
        description=(
            "Enables viral sharing mechanics, generates shareable content, and tracks social growth metrics."
        ),
        category=BotCategory.APP,
        module_path="App_bots.social_sharing_bot",
        class_name="SocialSharingBot",
        capabilities=["social_sharing", "viral", "sharing", "growth"],
    ),
    BotEntry(
        bot_id="sports_app_bot",
        display_name="Sports App Bot",
        description=(
            "Delivers live sports scores, team stats, player profiles, and personalised sports content."
        ),
        category=BotCategory.APP,
        module_path="App_bots.sports_app_bot",
        class_name="SportsAppBot",
        capabilities=["sports", "scores", "teams", "stats"],
    ),
    BotEntry(
        bot_id="subscription_manager_bot",
        display_name="Subscription Manager Bot",
        description=(
            "Manages subscription plans, billing cycles, upgrades, downgrades, and renewal reminders."
        ),
        category=BotCategory.APP,
        module_path="App_bots.subscription_manager_bot",
        class_name="SubscriptionManagerBot",
        capabilities=["subscriptions", "billing", "plans", "renewals"],
    ),
    BotEntry(
        bot_id="travel_app_bot",
        display_name="Travel App Bot",
        description=(
            "Powers travel booking including flights, hotels, itinerary planning, and trip management."
        ),
        category=BotCategory.APP,
        module_path="App_bots.travel_app_bot",
        class_name="TravelAppBot",
        capabilities=["travel", "booking", "flights", "hotels"],
    ),
    BotEntry(
        bot_id="user_feedback_bot",
        display_name="User Feedback Bot",
        description=(
            "Collects structured user feedback via surveys, NPS, and in-app prompts with actionable reporting."
        ),
        category=BotCategory.APP,
        module_path="App_bots.user_feedback_bot",
        class_name="UserFeedbackBot",
        capabilities=["user_feedback", "surveys", "nps", "insights"],
    ),
    BotEntry(
        bot_id="user_retention_bot",
        display_name="User Retention Bot",
        description=(
            "Implements lifecycle re-engagement strategies to bring back lapsed users with personalised campaigns."
        ),
        category=BotCategory.APP,
        module_path="App_bots.user_retention_bot",
        class_name="UserRetentionBot",
        capabilities=["retention", "engagement", "re_engagement", "lifecycle"],
    ),
    BotEntry(
        bot_id="user_segmentation_bot",
        display_name="User Segmentation Bot",
        description=(
            "Segments users into cohorts based on behaviour, demographics, and value for targeted campaigns."
        ),
        category=BotCategory.APP,
        module_path="App_bots.user_segmentation_bot",
        class_name="UserSegmentationBot",
        capabilities=["segmentation", "cohorts", "analytics", "targeting"],
    ),
    BotEntry(
        bot_id="utilities_app_bot",
        display_name="Utilities App Bot",
        description=(
            "Provides utility app features including calculators, converters, system tools, and file managers."
        ),
        category=BotCategory.APP,
        module_path="App_bots.utilities_app_bot",
        class_name="UtilitiesAppBot",
        capabilities=["utilities", "tools", "system"],
    ),
    BotEntry(
        bot_id="weather_app_bot",
        display_name="Weather App Bot",
        description=(
            "Delivers accurate weather forecasts, alerts, and location-based climate information."
        ),
        category=BotCategory.APP,
        module_path="App_bots.weather_app_bot",
        class_name="WeatherAppBot",
        capabilities=["weather", "forecast", "location"],
    ),
    BotEntry(
        bot_id="accommodation_food_bot",
        display_name="Accommodation Food Bot",
        description=(
            "Manages hospitality and food service operations including bookings, menus, and staff scheduling."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.accommodation_food_bot",
        class_name="AccommodationFoodBot",
        capabilities=["hospitality", "food_service", "accommodation"],
    ),
    BotEntry(
        bot_id="administrative_support_industry_bot",
        display_name="Administrative Support Industry Bot",
        description=(
            "Automates administrative support tasks including scheduling, correspondence, and office management."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.administrative_support_industry_bot",
        class_name="AdministrativeSupportIndustryBot",
        capabilities=["admin", "support", "operations"],
    ),
    BotEntry(
        bot_id="agriculture_bot",
        display_name="Agriculture Bot",
        description=(
            "Optimises agricultural operations with crop planning, yield forecasting, and precision farming tools."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.agriculture_bot",
        class_name="AgricultureBot",
        capabilities=["agriculture", "farming", "crops", "yield"],
    ),
    BotEntry(
        bot_id="arts_entertainment_bot",
        display_name="Arts Entertainment Bot",
        description=(
            "Supports arts and entertainment industry workflows including booking, rights management, and promotion."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.arts_entertainment_bot",
        class_name="ArtsEntertainmentBot",
        capabilities=["arts", "entertainment", "media"],
    ),
    BotEntry(
        bot_id="brand_monitor_bot",
        display_name="Brand Monitor Bot",
        description=(
            "Monitors brand mentions across the web and social media, tracks sentiment, and alerts on reputation risks."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.brand_monitor_bot",
        class_name="BrandMonitorBot",
        capabilities=["brand_monitoring", "sentiment", "mentions", "alerts"],
    ),
    BotEntry(
        bot_id="business_plan_bot",
        display_name="Business Plan Bot",
        description=(
            "Generates comprehensive AI-powered business plans with market analysis, financials, and growth strategies."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.business_plan_bot",
        class_name="BusinessPlanBot",
        capabilities=["business_plan", "strategy", "planning", "financials"],
    ),
    BotEntry(
        bot_id="competitor_analyzer_bot",
        display_name="Competitor Analyzer Bot",
        description=(
            "Researches and benchmarks competitors on pricing, features, marketing, and market positioning."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.competitor_analyzer_bot",
        class_name="CompetitorAnalyzerBot",
        capabilities=["competitor_analysis", "market_intel", "benchmarking"],
    ),
    BotEntry(
        bot_id="compliance_checker_bot",
        display_name="Compliance Checker Bot",
        description=(
            "Audits business processes for regulatory compliance across industry standards and legal requirements."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.compliance_checker_bot",
        class_name="ComplianceCheckerBot",
        capabilities=["compliance", "regulatory", "audit", "legal"],
    ),
    BotEntry(
        bot_id="construction_bot",
        display_name="Construction Bot",
        description=(
            "Manages construction project timelines, contractor coordination, materials tracking, and budget oversight."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.construction_bot",
        class_name="ConstructionBot",
        capabilities=["construction", "project_management", "contracts"],
    ),
    BotEntry(
        bot_id="contract_generator_bot",
        display_name="Contract Generator Bot",
        description=(
            "Generates legally-sound contract templates tailored to specific business scenarios and jurisdictions."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.contract_generator_bot",
        class_name="ContractGeneratorBot",
        capabilities=["contracts", "legal", "templates", "automation"],
    ),
    BotEntry(
        bot_id="customer_support_bot",
        display_name="Customer Support Bot",
        description=(
            "Automates customer support with intelligent ticket routing, knowledge base lookup, and escalation workflows."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.customer_support_bot",
        class_name="CustomerSupportBot",
        capabilities=["customer_support", "helpdesk", "tickets", "chat"],
    ),
    BotEntry(
        bot_id="document_manager_bot",
        display_name="Document Manager Bot",
        description=(
            "Organises, indexes, and retrieves business documents with intelligent categorisation and search."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.document_manager_bot",
        class_name="DocumentManagerBot",
        capabilities=["documents", "storage", "organization", "search"],
    ),
    BotEntry(
        bot_id="ecommerce_optimizer_bot",
        display_name="Ecommerce Optimizer Bot",
        description=(
            "Optimises e-commerce store performance through conversion analysis, product page improvements, and UX fixes."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.ecommerce_optimizer_bot",
        class_name="EcommerceOptimizerBot",
        capabilities=["ecommerce", "conversion", "optimization", "sales"],
    ),
    BotEntry(
        bot_id="educational_services_bot",
        display_name="Educational Services Bot",
        description=(
            "Manages educational service delivery including course scheduling, student tracking, and certification."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.educational_services_bot",
        class_name="EducationalServicesBot",
        capabilities=["education", "courses", "certification", "training"],
    ),
    BotEntry(
        bot_id="employee_onboarding_bot",
        display_name="Employee Onboarding Bot",
        description=(
            "Automates employee onboarding with checklists, document collection, training assignment, and HR workflows."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.employee_onboarding_bot",
        class_name="EmployeeOnboardingBot",
        capabilities=["onboarding", "hr", "training", "workflows"],
    ),
    BotEntry(
        bot_id="expense_tracker_bot",
        display_name="Expense Tracker Bot",
        description=(
            "Tracks business expenses, categorises spend, enforces budgets, and generates financial reports."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.expense_tracker_bot",
        class_name="ExpenseTrackerBot",
        capabilities=["expenses", "budgeting", "finance", "reporting"],
    ),
    BotEntry(
        bot_id="finance_insurance_bot",
        display_name="Finance Insurance Bot",
        description=(
            "Handles finance and insurance industry operations including policy management and risk assessment."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.finance_insurance_bot",
        class_name="FinanceInsuranceBot",
        capabilities=["finance", "insurance", "risk", "coverage"],
    ),
    BotEntry(
        bot_id="financial_forecaster_bot",
        display_name="Financial Forecaster Bot",
        description=(
            "Builds financial forecasts with revenue projections, scenario modelling, and cash flow analysis."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.financial_forecaster_bot",
        class_name="FinancialForecasterBot",
        capabilities=["forecasting", "finance", "projections", "modeling"],
    ),
    BotEntry(
        bot_id="franchise_analyzer_bot",
        display_name="Franchise Analyzer Bot",
        description=(
            "Analyses franchise opportunities for ROI potential, market fit, and operational feasibility."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.franchise_analyzer_bot",
        class_name="FranchiseAnalyzerBot",
        capabilities=["franchise", "opportunity_analysis", "roi", "business"],
    ),
    BotEntry(
        bot_id="grant_finder_bot",
        display_name="Grant Finder Bot",
        description=(
            "Discovers and matches business grant opportunities from government and private funding sources."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.grant_finder_bot",
        class_name="GrantFinderBot",
        capabilities=["grants", "funding", "government", "applications"],
    ),
    BotEntry(
        bot_id="health_care_bot",
        display_name="Health Care Bot",
        description=(
            "Manages healthcare business operations including patient scheduling, billing, and compliance workflows."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.health_care_bot",
        class_name="HealthCareBot",
        capabilities=["healthcare", "medical", "patients", "billing"],
    ),
    BotEntry(
        bot_id="information_bot",
        display_name="Information Bot",
        description=(
            "Aggregates and delivers structured business information from internal and external knowledge sources."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.information_bot",
        class_name="InformationBot",
        capabilities=["information", "knowledge_base", "research"],
    ),
    BotEntry(
        bot_id="insurance_advisor_bot",
        display_name="Insurance Advisor Bot",
        description=(
            "Analyses insurance needs, compares policy options, and advises on coverage gaps and risk exposure."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.insurance_advisor_bot",
        class_name="InsuranceAdvisorBot",
        capabilities=["insurance", "coverage", "risk_assessment", "claims"],
    ),
    BotEntry(
        bot_id="inventory_manager_bot",
        display_name="Inventory Manager Bot",
        description=(
            "Tracks inventory levels, automates reorder triggers, and optimises stock across locations."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.inventory_manager_bot",
        class_name="InventoryManagerBot",
        capabilities=["inventory", "stock", "supply_chain", "tracking"],
    ),
    BotEntry(
        bot_id="kpi_tracker_bot",
        display_name="Kpi Tracker Bot",
        description=(
            "Monitors key performance indicators, builds real-time dashboards, and generates executive KPI reports."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.kpi_tracker_bot",
        class_name="KPITrackerBot",
        capabilities=["kpis", "metrics", "dashboards", "reporting"],
    ),
    BotEntry(
        bot_id="llc_formation_bot",
        display_name="Llc Formation Bot",
        description=(
            "Guides business owners through LLC formation with document preparation, filings, and compliance checklists."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.llc_formation_bot",
        class_name="LLCFormationBot",
        capabilities=["llc", "business_formation", "legal", "compliance"],
    ),
    BotEntry(
        bot_id="management_companies_bot",
        display_name="Management Companies Bot",
        description=(
            "Supports management company operations with portfolio oversight, reporting, and operational tools."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.management_companies_bot",
        class_name="ManagementCompaniesBot",
        capabilities=["management", "companies", "portfolio", "oversight"],
    ),
    BotEntry(
        bot_id="manufacturing_bot",
        display_name="Manufacturing Bot",
        description=(
            "Optimises manufacturing operations with production scheduling, quality control, and supply chain management."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.manufacturing_bot",
        class_name="ManufacturingBot",
        capabilities=["manufacturing", "production", "quality_control", "supply_chain"],
    ),
    BotEntry(
        bot_id="market_research_bot",
        display_name="Market Research Bot",
        description=(
            "Conducts comprehensive market research with surveys, competitive analysis, and consumer insights."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.market_research_bot",
        class_name="MarketResearchBot",
        capabilities=["market_research", "surveys", "analysis", "insights"],
    ),
    BotEntry(
        bot_id="meeting_scheduler_bot",
        display_name="Meeting Scheduler Bot",
        description=(
            "Automates meeting scheduling with calendar integration, availability matching, and reminder workflows."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.meeting_scheduler_bot",
        class_name="MeetingSchedulerBot",
        capabilities=["scheduling", "calendar", "meetings", "automation"],
    ),
    BotEntry(
        bot_id="biz_mining_bot",
        display_name="Biz Mining Bot",
        description=(
            "Manages mining and resource extraction operations with production monitoring and compliance tracking."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.mining_bot",
        class_name="MiningBot",
        capabilities=["mining", "extraction", "resources", "operations"],
    ),
    BotEntry(
        bot_id="other_services_bot",
        display_name="Other Services Bot",
        description=(
            "Provides support for miscellaneous service industry operations and business automation tasks."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.other_services_bot",
        class_name="OtherServicesBot",
        capabilities=["services", "general", "consulting"],
    ),
    BotEntry(
        bot_id="partnership_finder_bot",
        display_name="Partnership Finder Bot",
        description=(
            "Identifies and facilitates strategic partnership opportunities with matching and outreach automation."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.partnership_finder_bot",
        class_name="PartnershipFinderBot",
        capabilities=["partnerships", "networking", "business_dev", "outreach"],
    ),
    BotEntry(
        bot_id="payroll_bot",
        display_name="Payroll Bot",
        description=(
            "Processes payroll calculations, tax deductions, direct deposit, and compliance reporting automation."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.payroll_bot",
        class_name="PayrollBot",
        capabilities=["payroll", "hr", "compensation", "tax_filing"],
    ),
    BotEntry(
        bot_id="pitch_deck_bot",
        display_name="Pitch Deck Bot",
        description=(
            "Creates investor-ready pitch decks with AI-generated content, financial models, and visual storytelling."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.pitch_deck_bot",
        class_name="PitchDeckBot",
        capabilities=["pitch_deck", "presentations", "investor_relations", "fundraising"],
    ),
    BotEntry(
        bot_id="pricing_strategy_bot",
        display_name="Pricing Strategy Bot",
        description=(
            "Analyses markets and competition to recommend optimal pricing strategies and dynamic pricing models."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.pricing_strategy_bot",
        class_name="PricingStrategyBot",
        capabilities=["pricing", "strategy", "optimization", "competitive"],
    ),
    BotEntry(
        bot_id="professional_services_bot",
        display_name="Professional Services Bot",
        description=(
            "Automates professional services firm operations including client management, billing, and delivery tracking."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.professional_services_bot",
        class_name="ProfessionalServicesBot",
        capabilities=["professional_services", "consulting", "legal", "finance"],
    ),
    BotEntry(
        bot_id="public_administration_bot",
        display_name="Public Administration Bot",
        description=(
            "Supports public administration workflows including citizen services, compliance, and government reporting."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.public_administration_bot",
        class_name="PublicAdministrationBot",
        capabilities=["public_sector", "government", "administration"],
    ),
    BotEntry(
        bot_id="real_estate_leasing_bot",
        display_name="Real Estate Leasing Bot",
        description=(
            "Manages commercial and residential leasing workflows including listings, applications, and lease generation."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.real_estate_leasing_bot",
        class_name="RealEstateLeasingBot",
        capabilities=["leasing", "real_estate", "contracts", "tenants"],
    ),
    BotEntry(
        bot_id="retail_trade_bot",
        display_name="Retail Trade Bot",
        description=(
            "Optimises retail operations with inventory management, sales analytics, and customer experience tools."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.retail_trade_bot",
        class_name="RetailTradeBot",
        capabilities=["retail", "sales", "inventory", "pos"],
    ),
    BotEntry(
        bot_id="sales_pipeline_bot",
        display_name="Sales Pipeline Bot",
        description=(
            "Manages sales pipeline stages, forecasts revenue, and automates CRM updates and follow-up sequences."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.sales_pipeline_bot",
        class_name="SalesPipelineBot",
        capabilities=["sales_pipeline", "crm", "leads", "forecasting"],
    ),
    BotEntry(
        bot_id="supply_chain_bot",
        display_name="Supply Chain Bot",
        description=(
            "Optimises supply chain operations with vendor management, logistics tracking, and demand forecasting."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.supply_chain_bot",
        class_name="SupplyChainBot",
        capabilities=["supply_chain", "logistics", "procurement", "tracking"],
    ),
    BotEntry(
        bot_id="tax_preparer_bot",
        display_name="Tax Preparer Bot",
        description=(
            "Automates tax preparation with income analysis, deduction identification, and filing deadline management."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.tax_preparer_bot",
        class_name="TaxPreparerBot",
        capabilities=["taxes", "filing", "deductions", "compliance"],
    ),
    BotEntry(
        bot_id="transportation_warehousing_bot",
        display_name="Transportation Warehousing Bot",
        description=(
            "Manages transportation and warehousing operations including fleet tracking and inventory logistics."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.transportation_warehousing_bot",
        class_name="TransportationWarehousingBot",
        capabilities=["transportation", "warehousing", "logistics"],
    ),
    BotEntry(
        bot_id="utilities_bot",
        display_name="Utilities Bot",
        description=(
            "Handles utilities industry operations including service delivery, billing, and infrastructure management."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.utilities_bot",
        class_name="UtilitiesBot",
        capabilities=["utilities", "energy", "billing", "infrastructure"],
    ),
    BotEntry(
        bot_id="vendor_manager_bot",
        display_name="Vendor Manager Bot",
        description=(
            "Manages vendor relationships, procurement workflows, contract compliance, and performance evaluation."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.vendor_manager_bot",
        class_name="VendorManagerBot",
        capabilities=["vendors", "procurement", "contracts", "evaluation"],
    ),
    BotEntry(
        bot_id="wholesale_trade_bot",
        display_name="Wholesale Trade Bot",
        description=(
            "Optimises wholesale trade operations with bulk order management, pricing tiers, and distribution."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.wholesale_trade_bot",
        class_name="WholesaleTradeBot",
        capabilities=["wholesale", "distribution", "bulk_orders", "b2b"],
    ),
    BotEntry(
        bot_id="buyer_persona_bot",
        display_name="Buyer Persona Bot",
        description=(
            "Builds detailed buyer personas for freelance service targeting and proposal personalisation."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.buyer_persona_bot",
        class_name="BuyerPersonaBot",
        capabilities=["buyer_personas", "targeting", "market_research"],
    ),
    BotEntry(
        bot_id="client_finder_bot",
        display_name="Client Finder Bot",
        description=(
            "Discovers and qualifies potential freelance clients through platform and social media prospecting."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.client_finder_bot",
        class_name="ClientFinderBot",
        capabilities=["client_discovery", "lead_gen", "freelance", "prospecting"],
    ),
    BotEntry(
        bot_id="client_retention_bot",
        display_name="Client Retention Bot",
        description=(
            "Implements client retention strategies with follow-up automation and loyalty incentives."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.client_retention_bot",
        class_name="ClientRetentionBot",
        capabilities=["client_retention", "loyalty", "follow_up"],
    ),
    BotEntry(
        bot_id="fiverr_competitor_spy_bot",
        display_name="Fiverr Competitor Spy Bot",
        description=(
            "Monitors competitor gigs and campaigns, analyses pricing and positioning to sharpen competitive advantage."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.competitor_spy_bot",
        class_name="CompetitorSpyBot",
        capabilities=["competitor_analysis", "market_intel", "pricing"],
    ),
    BotEntry(
        bot_id="cross_sell_bot",
        display_name="Cross Sell Bot",
        description=(
            "Identifies and executes cross-selling opportunities to increase order value from existing clients."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.cross_sell_bot",
        class_name="CrossSellBot",
        capabilities=["cross_selling", "upsell", "revenue", "packages"],
    ),
    BotEntry(
        bot_id="deadline_tracker_bot",
        display_name="Deadline Tracker Bot",
        description=(
            "Tracks project deadlines, sends proactive reminders, and escalates at-risk deliveries."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.deadline_tracker_bot",
        class_name="DeadlineTrackerBot",
        capabilities=["deadlines", "project_management", "reminders"],
    ),
    BotEntry(
        bot_id="dispute_resolver_bot",
        display_name="Dispute Resolver Bot",
        description=(
            "Assists with freelance dispute resolution by documenting cases and generating resolution strategies."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.dispute_resolver_bot",
        class_name="DisputeResolverBot",
        capabilities=["disputes", "resolution", "mediation", "support"],
    ),
    BotEntry(
        bot_id="earnings_tracker_bot",
        display_name="Earnings Tracker Bot",
        description=(
            "Tracks freelance earnings, categorises income streams, and projects monthly revenue targets."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.earnings_tracker_bot",
        class_name="EarningsTrackerBot",
        capabilities=["earnings", "income", "analytics", "reporting"],
    ),
    BotEntry(
        bot_id="feedback_analyzer_bot",
        display_name="Feedback Analyzer Bot",
        description=(
            "AI-powered feedback analyzer bot for DreamCo automation and intelligence."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.feedback_analyzer_bot",
        class_name="FeedbackAnalyzerBot",
        capabilities=["feedback_analyzer"],
    ),
    BotEntry(
        bot_id="fiverr_fiverr_bot",
        display_name="Fiverr Fiverr Bot",
        description=(
            "Core Fiverr platform automation bot for gig management, order tracking, and platform optimisation."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.fiverr_bot",
        class_name="FiverrBot",
        capabilities=["fiverr", "gig_management", "freelance", "automation"],
    ),
    BotEntry(
        bot_id="gig_description_optimizer_bot",
        display_name="Gig Description Optimizer Bot",
        description=(
            "Optimises Fiverr gig descriptions with SEO-tuned copy, keywords, and conversion-focused writing."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.gig_description_optimizer_bot",
        class_name="GigDescriptionOptimizerBot",
        capabilities=["gig_optimization", "seo", "copywriting"],
    ),
    BotEntry(
        bot_id="gig_image_optimizer_bot",
        display_name="Gig Image Optimizer Bot",
        description=(
            "Enhances Fiverr gig thumbnails and images for maximum click-through rate and visual appeal."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.gig_image_optimizer_bot",
        class_name="GigImageOptimizerBot",
        capabilities=["image_optimization", "thumbnails", "design"],
    ),
    BotEntry(
        bot_id="gig_ranking_bot",
        display_name="Gig Ranking Bot",
        description=(
            "Analyses and improves Fiverr gig search rankings through SEO, metadata, and engagement optimisation."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.gig_ranking_bot",
        class_name="GigRankingBot",
        capabilities=["gig_ranking", "seo", "visibility", "fiverr"],
    ),
    BotEntry(
        bot_id="inbox_automation_bot",
        display_name="Inbox Automation Bot",
        description=(
            "Automates Fiverr inbox responses with templates, quick replies, and enquiry qualification flows."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.inbox_automation_bot",
        class_name="InboxAutomationBot",
        capabilities=["inbox", "messaging", "automation", "responses"],
    ),
    BotEntry(
        bot_id="level_up_bot",
        display_name="Level Up Bot",
        description=(
            "Provides strategies and action plans to advance through Fiverr seller levels and earn Top Rated status."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.level_up_bot",
        class_name="LevelUpBot",
        capabilities=["leveling", "seller_progression", "fiverr", "skills"],
    ),
    BotEntry(
        bot_id="milestone_tracker_bot",
        display_name="Milestone Tracker Bot",
        description=(
            "Tracks freelance project milestones, monitors deliverables, and notifies stakeholders on completion."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.milestone_tracker_bot",
        class_name="MilestoneTrackerBot",
        capabilities=["milestones", "project_management", "delivery"],
    ),
    BotEntry(
        bot_id="niche_analyzer_bot",
        display_name="Niche Analyzer Bot",
        description=(
            "Analyses freelance market niches for demand, competition, and earning potential."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.niche_analyzer_bot",
        class_name="NicheAnalyzerBot",
        capabilities=["niche_analysis", "market_research", "opportunities"],
    ),
    BotEntry(
        bot_id="order_completion_bot",
        display_name="Order Completion Bot",
        description=(
            "Manages order completion workflows including delivery checklists, client review requests, and archive."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.order_completion_bot",
        class_name="OrderCompletionBot",
        capabilities=["order_completion", "delivery", "quality"],
    ),
    BotEntry(
        bot_id="package_optimizer_bot",
        display_name="Package Optimizer Bot",
        description=(
            "Optimises freelance service packages for maximum perceived value and conversion."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.package_optimizer_bot",
        class_name="PackageOptimizerBot",
        capabilities=["packages", "pricing", "optimization", "services"],
    ),
    BotEntry(
        bot_id="fiverr_portfolio_builder_bot",
        display_name="Fiverr Portfolio Builder Bot",
        description=(
            "Builds and curates a compelling portfolio with case studies, samples, and testimonials."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.portfolio_builder_bot",
        class_name="PortfolioBuilderBot",
        capabilities=["portfolio", "showcase", "branding", "samples"],
    ),
    BotEntry(
        bot_id="pricing_optimizer_bot",
        display_name="Pricing Optimizer Bot",
        description=(
            "Analyses market rates and demand signals to recommend optimal freelance service pricing."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.pricing_optimizer_bot",
        class_name="PricingOptimizerBot",
        capabilities=["pricing", "optimization", "competitive", "revenue"],
    ),
    BotEntry(
        bot_id="proposal_writer_bot",
        display_name="Proposal Writer Bot",
        description=(
            "Writes persuasive, personalised freelance proposals that win high-value client projects."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.proposal_writer_bot",
        class_name="ProposalWriterBot",
        capabilities=["proposals", "copywriting", "pitching", "winning"],
    ),
    BotEntry(
        bot_id="response_time_bot",
        display_name="Response Time Bot",
        description=(
            "Monitors and optimises response time metrics to maintain high platform ratings and conversion."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.response_time_bot",
        class_name="ResponseTimeBot",
        capabilities=["response_time", "automation", "messaging", "alerts"],
    ),
    BotEntry(
        bot_id="revision_manager_bot",
        display_name="Revision Manager Bot",
        description=(
            "Manages client revision requests with structured workflows, scope tracking, and change documentation."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.revision_manager_bot",
        class_name="RevisionManagerBot",
        capabilities=["revisions", "change_management", "client_relations"],
    ),
    BotEntry(
        bot_id="seasonal_pricing_bot",
        display_name="Seasonal Pricing Bot",
        description=(
            "Adjusts freelance pricing dynamically based on seasonal demand, platform trends, and competition."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.seasonal_pricing_bot",
        class_name="SeasonalPricingBot",
        capabilities=["seasonal", "pricing", "demand", "optimization"],
    ),
    BotEntry(
        bot_id="service_expansion_bot",
        display_name="Service Expansion Bot",
        description=(
            "Identifies opportunities to expand freelance service offerings into adjacent high-demand niches."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.service_expansion_bot",
        class_name="ServiceExpansionBot",
        capabilities=["service_expansion", "upsell", "new_offerings"],
    ),
    BotEntry(
        bot_id="skill_tagger_bot",
        display_name="Skill Tagger Bot",
        description=(
            "Optimises skill tags and service categories for maximum discoverability on freelance platforms."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.skill_tagger_bot",
        class_name="SkillTaggerBot",
        capabilities=["skills", "tagging", "seo", "discoverability"],
    ),
    BotEntry(
        bot_id="upsell_bot",
        display_name="Upsell Bot",
        description=(
            "Generates targeted upsell offers and add-on recommendations to increase average order value."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.upsell_bot",
        class_name="UpsellBot",
        capabilities=["upselling", "revenue", "packages", "add_ons"],
    ),
    BotEntry(
        bot_id="mkt_ab_testing_bot",
        display_name="Mkt Ab Testing Bot",
        description=(
            "Manages A/B test experiments for mobile apps, tracks variants, measures conversions, and surfaces winning configurations."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.ab_testing_bot",
        class_name="ABTestingBot",
        capabilities=["ab_testing", "experiment_management", "split_testing", "analytics"],
    ),
    BotEntry(
        bot_id="ad_campaign_bot",
        display_name="Ad Campaign Bot",
        description=(
            "Plans, launches, and optimises paid advertising campaigns across Google, Facebook, and other platforms."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.ad_campaign_bot",
        class_name="AdCampaignBot",
        capabilities=["ad_campaigns", "ppc", "targeting", "optimization"],
    ),
    BotEntry(
        bot_id="affiliate_marketer_bot",
        display_name="Affiliate Marketer Bot",
        description=(
            "Manages affiliate marketing programs with partner recruitment, tracking, and commission automation."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.affiliate_marketer_bot",
        class_name="AffiliateMarketerBot",
        capabilities=["affiliate_marketing", "commissions", "tracking"],
    ),
    BotEntry(
        bot_id="analytics_reporter_bot",
        display_name="Analytics Reporter Bot",
        description=(
            "Aggregates marketing analytics from multiple platforms into unified reports and dashboards."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.analytics_reporter_bot",
        class_name="AnalyticsReporterBot",
        capabilities=["analytics", "reporting", "dashboards", "kpis"],
    ),
    BotEntry(
        bot_id="brand_story_bot",
        display_name="Brand Story Bot",
        description=(
            "Crafts compelling brand narratives, messaging frameworks, and content pillars aligned to target audiences."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.brand_story_bot",
        class_name="BrandStoryBot",
        capabilities=["brand_story", "copywriting", "content", "identity"],
    ),
    BotEntry(
        bot_id="chatbot_builder_bot",
        display_name="Chatbot Builder Bot",
        description=(
            "Builds and deploys AI-powered chatbots for marketing automation, lead capture, and customer service."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.chatbot_builder_bot",
        class_name="ChatbotBuilderBot",
        capabilities=["chatbot", "automation", "customer_service", "ai"],
    ),
    BotEntry(
        bot_id="mkt_competitor_spy_bot",
        display_name="Mkt Competitor Spy Bot",
        description=(
            "Monitors competitor gigs and campaigns, analyses pricing and positioning to sharpen competitive advantage."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.competitor_spy_bot",
        class_name="CompetitorSpyBot",
        capabilities=["competitor_analysis", "market_intel", "pricing"],
    ),
    BotEntry(
        bot_id="conversion_optimizer_bot",
        display_name="Conversion Optimizer Bot",
        description=(
            "Analyses conversion funnels, runs CRO experiments, and implements improvements to lift conversion rates."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.conversion_optimizer_bot",
        class_name="ConversionOptimizerBot",
        capabilities=["conversion", "cro", "a_b_testing", "funnels"],
    ),
    BotEntry(
        bot_id="customer_review_bot",
        display_name="Customer Review Bot",
        description=(
            "Automates review collection, monitors reputation, and responds to customer feedback across platforms."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.customer_review_bot",
        class_name="CustomerReviewBot",
        capabilities=["reviews", "reputation", "testimonials", "nps"],
    ),
    BotEntry(
        bot_id="event_promoter_bot",
        display_name="Event Promoter Bot",
        description=(
            "Plans and executes event marketing campaigns across email, social media, and paid channels."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.event_promoter_bot",
        class_name="EventPromoterBot",
        capabilities=["event_promotion", "marketing", "social_media", "email"],
    ),
    BotEntry(
        bot_id="google_ads_bot",
        display_name="Google Ads Bot",
        description=(
            "Manages Google Ads campaigns with keyword research, bid optimisation, ad copy, and performance reporting."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.google_ads_bot",
        class_name="GoogleAdsBot",
        capabilities=["google_ads", "ppc", "sem", "keywords"],
    ),
    BotEntry(
        bot_id="hashtag_analyzer_bot",
        display_name="Hashtag Analyzer Bot",
        description=(
            "Researches trending hashtags, analyses reach and engagement, and recommends optimal hashtag strategies."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.hashtag_analyzer_bot",
        class_name="HashtagAnalyzerBot",
        capabilities=["hashtags", "social_media", "trending", "reach"],
    ),
    BotEntry(
        bot_id="influencer_finder_bot",
        display_name="Influencer Finder Bot",
        description=(
            "Discovers and evaluates influencers for brand partnerships based on audience fit and engagement."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.influencer_finder_bot",
        class_name="InfluencerFinderBot",
        capabilities=["influencer_marketing", "discovery", "outreach"],
    ),
    BotEntry(
        bot_id="landing_page_bot",
        display_name="Landing Page Bot",
        description=(
            "Designs and optimises landing pages for maximum conversion with A/B testing and CRO best practices."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.landing_page_bot",
        class_name="LandingPageBot",
        capabilities=["landing_pages", "conversion", "cro", "design"],
    ),
    BotEntry(
        bot_id="lead_magnet_bot",
        display_name="Lead Magnet Bot",
        description=(
            "Creates compelling lead magnets to grow email lists and generate qualified leads at scale."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.lead_magnet_bot",
        class_name="LeadMagnetBot",
        capabilities=["lead_magnets", "list_building", "content_marketing"],
    ),
    BotEntry(
        bot_id="loyalty_program_bot",
        display_name="Loyalty Program Bot",
        description=(
            "Designs and manages customer loyalty programs with rewards, tiers, and engagement mechanics."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.loyalty_program_bot",
        class_name="LoyaltyProgramBot",
        capabilities=["loyalty", "rewards", "retention", "gamification"],
    ),
    BotEntry(
        bot_id="newsletter_bot",
        display_name="Newsletter Bot",
        description=(
            "Automates email newsletter creation, list management, segmentation, and performance analytics."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.newsletter_bot",
        class_name="NewsletterBot",
        capabilities=["newsletter", "email_marketing", "subscribers", "automation"],
    ),
    BotEntry(
        bot_id="podcast_promoter_bot",
        display_name="Podcast Promoter Bot",
        description=(
            "Promotes podcasts across platforms, manages episode distribution, and grows audience reach."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.podcast_promoter_bot",
        class_name="PodcastPromoterBot",
        capabilities=["podcasts", "promotion", "distribution", "growth"],
    ),
    BotEntry(
        bot_id="press_release_bot",
        display_name="Press Release Bot",
        description=(
            "Writes and distributes press releases to media outlets and news wires for brand coverage."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.press_release_bot",
        class_name="PressReleaseBot",
        capabilities=["press_releases", "pr", "media", "announcements"],
    ),
    BotEntry(
        bot_id="referral_marketing_bot",
        display_name="Referral Marketing Bot",
        description=(
            "Builds and manages referral marketing campaigns that drive viral customer acquisition."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.referral_marketing_bot",
        class_name="ReferralMarketingBot",
        capabilities=["referrals", "viral_growth", "word_of_mouth"],
    ),
    BotEntry(
        bot_id="retargeting_bot",
        display_name="Retargeting Bot",
        description=(
            "Creates and manages retargeting ad campaigns to re-engage website visitors and cart abandoners."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.retargeting_bot",
        class_name="RetargetingBot",
        capabilities=["retargeting", "ads", "remarketing", "conversion"],
    ),
    BotEntry(
        bot_id="sales_funnel_bot",
        display_name="Sales Funnel Bot",
        description=(
            "Builds and optimises sales funnels with lead capture, nurturing sequences, and conversion touchpoints."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.sales_funnel_bot",
        class_name="SalesFunnelBot",
        capabilities=["sales_funnel", "conversion", "leads", "nurturing"],
    ),
    BotEntry(
        bot_id="seo_optimizer_bot",
        display_name="Seo Optimizer Bot",
        description=(
            "Performs technical and content SEO audits, keyword research, and optimisation to improve organic rankings."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.seo_optimizer_bot",
        class_name="SEOOptimizerBot",
        capabilities=["seo", "keywords", "ranking", "organic_traffic"],
    ),
    BotEntry(
        bot_id="social_proof_bot",
        display_name="Social Proof Bot",
        description=(
            "Collects and displays social proof including testimonials, case studies, and trust signals."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.social_proof_bot",
        class_name="SocialProofBot",
        capabilities=["social_proof", "testimonials", "trust", "conversion"],
    ),
    BotEntry(
        bot_id="video_marketing_bot",
        display_name="Video Marketing Bot",
        description=(
            "Plans, produces, and distributes video marketing content to drive engagement and brand awareness."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.video_marketing_bot",
        class_name="VideoMarketingBot",
        capabilities=["video_marketing", "youtube", "engagement", "content"],
    ),
    BotEntry(
        bot_id="viral_content_bot",
        display_name="Viral Content Bot",
        description=(
            "Creates share-worthy content designed to go viral through emotional triggers and social mechanics."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.viral_content_bot",
        class_name="ViralContentBot",
        capabilities=["viral_content", "engagement", "shares", "growth"],
    ),
    BotEntry(
        bot_id="webinar_bot",
        display_name="Webinar Bot",
        description=(
            "Manages webinar logistics including registration, reminder sequences, follow-up, and attendee nurturing."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.webinar_bot",
        class_name="WebinarBot",
        capabilities=["webinars", "events", "registration", "follow_up"],
    ),
    BotEntry(
        bot_id="administrative_support_bot",
        display_name="Administrative Support Bot",
        description=(
            "Automates clerical and administrative support tasks including scheduling, correspondence, and filing."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.administrative_support_bot",
        class_name="AdministrativeSupportBot",
        capabilities=["admin_support", "clerical", "office_management"],
    ),
    BotEntry(
        bot_id="architecture_engineering_bot",
        display_name="Architecture Engineering Bot",
        description=(
            "Supports architecture and engineering workflows with project management and compliance checks."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.architecture_engineering_bot",
        class_name="ArchitectureEngineeringBot",
        capabilities=["architecture", "engineering", "design", "cad"],
    ),
    BotEntry(
        bot_id="arts_media_bot",
        display_name="Arts Media Bot",
        description=(
            "Assists arts and media professionals with portfolio management, client work, and project tracking."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.arts_media_bot",
        class_name="ArtsMediaBot",
        capabilities=["arts", "media", "creative", "publishing"],
    ),
    BotEntry(
        bot_id="benefits_analyzer_bot",
        display_name="Benefits Analyzer Bot",
        description=(
            "Analyses employee benefits packages, identifies gaps, and recommends improvements for HR teams."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.benefits_analyzer_bot",
        class_name="BenefitsAnalyzerBot",
        capabilities=["benefits", "hr", "compensation", "analysis"],
    ),
    BotEntry(
        bot_id="building_maintenance_bot",
        display_name="Building Maintenance Bot",
        description=(
            "Manages building maintenance schedules, work orders, vendor coordination, and facility compliance."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.building_maintenance_bot",
        class_name="BuildingMaintenanceBot",
        capabilities=["building_maintenance", "facilities", "repairs"],
    ),
    BotEntry(
        bot_id="business_financial_bot",
        display_name="Business Financial Bot",
        description=(
            "Provides business financial analysis including P&L tracking, budgeting, and investment evaluation."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.business_financial_bot",
        class_name="BusinessFinancialBot",
        capabilities=["business_finance", "accounting", "analysis"],
    ),
    BotEntry(
        bot_id="career_path_bot",
        display_name="Career Path Bot",
        description=(
            "Maps personalised career development paths with milestones, skill requirements, and actionable steps."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.career_path_bot",
        class_name="CareerPathBot",
        capabilities=["career_path", "planning", "development", "roadmap"],
    ),
    BotEntry(
        bot_id="certification_advisor_bot",
        display_name="Certification Advisor Bot",
        description=(
            "Recommends professional certifications aligned to career goals and tracks certification progress."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.certification_advisor_bot",
        class_name="CertificationAdvisorBot",
        capabilities=["certifications", "credentials", "learning"],
    ),
    BotEntry(
        bot_id="community_service_bot",
        display_name="Community Service Bot",
        description=(
            "Coordinates community service programs, volunteer management, and social impact tracking."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.community_service_bot",
        class_name="CommunityServiceBot",
        capabilities=["community_service", "volunteering", "social_impact"],
    ),
    BotEntry(
        bot_id="company_culture_bot",
        display_name="Company Culture Bot",
        description=(
            "Assesses and improves company culture through engagement surveys, insights, and action planning."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.company_culture_bot",
        class_name="CompanyCultureBot",
        capabilities=["culture", "engagement", "hr", "values"],
    ),
    BotEntry(
        bot_id="computer_math_bot",
        display_name="Computer Math Bot",
        description=(
            "Assists with computational and mathematical problem-solving for STEM professionals and analysts."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.computer_math_bot",
        class_name="ComputerMathBot",
        capabilities=["computing", "mathematics", "stem", "analysis"],
    ),
    BotEntry(
        bot_id="construction_extraction_bot",
        display_name="Construction Extraction Bot",
        description=(
            "Manages construction and extraction industry operations including safety and compliance."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.construction_extraction_bot",
        class_name="ConstructionExtractionBot",
        capabilities=["construction", "extraction", "mining", "trades"],
    ),
    BotEntry(
        bot_id="contractor_rate_bot",
        display_name="Contractor Rate Bot",
        description=(
            "Provides market-informed contractor rate benchmarks and pricing recommendations by skill and region."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.contractor_rate_bot",
        class_name="ContractorRateBot",
        capabilities=["contractor_rates", "pricing", "freelance", "market"],
    ),
    BotEntry(
        bot_id="cover_letter_bot",
        display_name="Cover Letter Bot",
        description=(
            "Generates tailored, compelling cover letters optimised for specific roles and employers."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.cover_letter_bot",
        class_name="CoverLetterBot",
        capabilities=["cover_letters", "writing", "job_applications", "career"],
    ),
    BotEntry(
        bot_id="diversity_inclusion_bot",
        display_name="Diversity Inclusion Bot",
        description=(
            "Supports DEI initiatives with assessment tools, benchmarking, and actionable inclusion strategies."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.diversity_inclusion_bot",
        class_name="DiversityInclusionBot",
        capabilities=["diversity", "inclusion", "equity", "hr"],
    ),
    BotEntry(
        bot_id="education_library_bot",
        display_name="Education Library Bot",
        description=(
            "Manages educational resource libraries with cataloguing, search, and personalised learning pathways."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.education_library_bot",
        class_name="EducationLibraryBot",
        capabilities=["education", "library", "research", "knowledge"],
    ),
    BotEntry(
        bot_id="farming_fishing_forestry_bot",
        display_name="Farming Fishing Forestry Bot",
        description=(
            "Supports agricultural, fishing, and forestry operations with planning, compliance, and market tools."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.farming_fishing_forestry_bot",
        class_name="FarmingFishingForestryBot",
        capabilities=["farming", "fishing", "forestry", "agriculture"],
    ),
    BotEntry(
        bot_id="food_service_bot",
        display_name="Food Service Bot",
        description=(
            "Manages food service operations including menu planning, staff scheduling, and compliance tracking."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.food_service_bot",
        class_name="FoodServiceBot",
        capabilities=["food_service", "hospitality", "restaurant", "catering"],
    ),
    BotEntry(
        bot_id="freelance_rate_bot",
        display_name="Freelance Rate Bot",
        description=(
            "Benchmarks freelance market rates by skill, experience, and geography to inform competitive pricing."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.freelance_rate_bot",
        class_name="FreelanceRateBot",
        capabilities=["freelance_rates", "pricing", "market_rates", "consulting"],
    ),
    BotEntry(
        bot_id="gig_economy_bot",
        display_name="Gig Economy Bot",
        description=(
            "Helps workers navigate gig economy platforms, optimise profiles, and maximise multi-platform income."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.gig_economy_bot",
        class_name="GigEconomyBot",
        capabilities=["gig_economy", "freelance", "platforms", "income"],
    ),
    BotEntry(
        bot_id="headhunter_bot",
        display_name="Headhunter Bot",
        description=(
            "Assists executive recruiters with candidate sourcing, outreach, and talent pipeline management."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.headhunter_bot",
        class_name="HeadhunterBot",
        capabilities=["headhunting", "recruiting", "talent", "executive_search"],
    ),
    BotEntry(
        bot_id="healthcare_practitioner_bot",
        display_name="Healthcare Practitioner Bot",
        description=(
            "Supports healthcare practitioners with scheduling, patient management, and clinical documentation."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.healthcare_practitioner_bot",
        class_name="HealthcarePractitionerBot",
        capabilities=["healthcare", "practitioners", "medical", "clinical"],
    ),
    BotEntry(
        bot_id="healthcare_support_bot",
        display_name="Healthcare Support Bot",
        description=(
            "Automates healthcare support operations including billing, insurance claims, and appointment management."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.healthcare_support_bot",
        class_name="HealthcareSupportBot",
        capabilities=["healthcare_support", "medical_admin", "billing"],
    ),
    BotEntry(
        bot_id="industry_trend_bot",
        display_name="Industry Trend Bot",
        description=(
            "Tracks and analyses industry trends to surface emerging opportunities and threats for professionals."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.industry_trend_bot",
        class_name="IndustryTrendBot",
        capabilities=["industry_trends", "market_intel", "forecasting"],
    ),
    BotEntry(
        bot_id="installation_maintenance_bot",
        display_name="Installation Maintenance Bot",
        description=(
            "Coordinates installation and maintenance operations with scheduling, parts tracking, and service records."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.installation_maintenance_bot",
        class_name="InstallationMaintenanceBot",
        capabilities=["installation", "maintenance", "repairs", "service"],
    ),
    BotEntry(
        bot_id="job_application_tracker_bot",
        display_name="Job Application Tracker Bot",
        description=(
            "Tracks job applications across platforms, manages follow-up reminders, and monitors pipeline status."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.job_application_tracker_bot",
        class_name="JobApplicationTrackerBot",
        capabilities=["job_applications", "tracking", "career", "pipeline"],
    ),
    BotEntry(
        bot_id="job_board_aggregator_bot",
        display_name="Job Board Aggregator Bot",
        description=(
            "Aggregates job listings from multiple boards and filters opportunities by skills and preferences."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.job_board_aggregator_bot",
        class_name="JobBoardAggregatorBot",
        capabilities=["job_boards", "aggregation", "job_search", "listings"],
    ),
    BotEntry(
        bot_id="legal_bot",
        display_name="Legal Bot",
        description=(
            "Assists legal professionals with research, contract review, compliance monitoring, and case management."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.legal_bot",
        class_name="LegalBot",
        capabilities=["legal", "law", "contracts", "compliance"],
    ),
    BotEntry(
        bot_id="linkedin_optimizer_bot",
        display_name="Linkedin Optimizer Bot",
        description=(
            "Optimises LinkedIn profiles for search visibility, connection growth, and professional branding."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.linkedin_optimizer_bot",
        class_name="LinkedInOptimizerBot",
        capabilities=["linkedin", "profile_optimization", "networking", "job_search"],
    ),
    BotEntry(
        bot_id="management_bot",
        display_name="Management Bot",
        description=(
            "Supports managers with team coordination, performance tracking, goal setting, and reporting automation."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.management_bot",
        class_name="ManagementBot",
        capabilities=["management", "leadership", "operations", "strategy"],
    ),
    BotEntry(
        bot_id="mentor_finder_bot",
        display_name="Mentor Finder Bot",
        description=(
            "Connects professionals with suitable mentors based on industry, goals, and experience level."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.mentor_finder_bot",
        class_name="MentorFinderBot",
        capabilities=["mentors", "mentorship", "networking", "career"],
    ),
    BotEntry(
        bot_id="military_bot",
        display_name="Military Bot",
        description=(
            "Supports military personnel and veterans with career transition, benefits navigation, and skills translation."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.military_bot",
        class_name="MilitaryBot",
        capabilities=["military", "veterans", "defense", "transition"],
    ),
    BotEntry(
        bot_id="networking_bot",
        display_name="Networking Bot",
        description=(
            "Automates professional networking outreach, manages connections, and tracks relationship building progress."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.networking_bot",
        class_name="NetworkingBot",
        capabilities=["networking", "professional_connections", "outreach"],
    ),
    BotEntry(
        bot_id="performance_review_bot",
        display_name="Performance Review Bot",
        description=(
            "Facilitates structured performance reviews with goal tracking, 360 feedback, and development planning."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.performance_review_bot",
        class_name="PerformanceReviewBot",
        capabilities=["performance_reviews", "hr", "feedback", "goals"],
    ),
    BotEntry(
        bot_id="personal_care_bot",
        display_name="Personal Care Bot",
        description=(
            "Manages personal care services including client scheduling, service menus, and loyalty programs."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.personal_care_bot",
        class_name="PersonalCareBot",
        capabilities=["personal_care", "wellness", "grooming", "services"],
    ),
    BotEntry(
        bot_id="occ_portfolio_builder_bot",
        display_name="Occ Portfolio Builder Bot",
        description=(
            "Builds and curates a compelling portfolio with case studies, samples, and testimonials."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.portfolio_builder_bot",
        class_name="PortfolioBuilderBot",
        capabilities=["portfolio", "showcase", "branding", "samples"],
    ),
    BotEntry(
        bot_id="production_bot",
        display_name="Production Bot",
        description=(
            "Optimises production operations with scheduling, quality control, and efficiency tracking tools."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.production_bot",
        class_name="ProductionBot",
        capabilities=["production", "manufacturing", "operations", "efficiency"],
    ),
    BotEntry(
        bot_id="promotion_readiness_bot",
        display_name="Promotion Readiness Bot",
        description=(
            "Assesses promotion readiness with competency gap analysis, achievement tracking, and positioning advice."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.promotion_readiness_bot",
        class_name="PromotionReadinessBot",
        capabilities=["promotion_readiness", "career_growth", "assessment"],
    ),
    BotEntry(
        bot_id="protective_service_bot",
        display_name="Protective Service Bot",
        description=(
            "Supports protective services professionals with incident tracking, compliance, and operational tools."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.protective_service_bot",
        class_name="ProtectiveServiceBot",
        capabilities=["protective_services", "security", "law_enforcement"],
    ),
    BotEntry(
        bot_id="reference_checker_bot",
        display_name="Reference Checker Bot",
        description=(
            "Automates professional reference checks with structured questionnaires and verification workflows."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.reference_checker_bot",
        class_name="ReferenceCheckerBot",
        capabilities=["references", "background_checks", "verification"],
    ),
    BotEntry(
        bot_id="relocation_advisor_bot",
        display_name="Relocation Advisor Bot",
        description=(
            "Assists with job-related relocation including cost analysis, housing search, and transition planning."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.relocation_advisor_bot",
        class_name="RelocationAdvisorBot",
        capabilities=["relocation", "moving", "career", "housing"],
    ),
    BotEntry(
        bot_id="remote_job_finder_bot",
        display_name="Remote Job Finder Bot",
        description=(
            "Discovers and filters remote job opportunities aligned to skills, preferences, and compensation goals."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.remote_job_finder_bot",
        class_name="RemoteJobFinderBot",
        capabilities=["remote_jobs", "work_from_home", "job_search"],
    ),
    BotEntry(
        bot_id="salary_negotiator_bot",
        display_name="Salary Negotiator Bot",
        description=(
            "Provides data-driven salary negotiation strategies with market benchmarks and scripted talking points."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.salary_negotiator_bot",
        class_name="SalaryNegotiatorBot",
        capabilities=["salary_negotiation", "compensation", "career", "offers"],
    ),
    BotEntry(
        bot_id="sales_bot",
        display_name="Sales Bot",
        description=(
            "Manages sales activities including lead management, CRM updates, follow-ups, and revenue forecasting."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.sales_bot",
        class_name="SalesBot",
        capabilities=["sales", "crm", "leads", "revenue"],
    ),
    BotEntry(
        bot_id="science_bot",
        display_name="Science Bot",
        description=(
            "Assists science professionals with research literature, data analysis, and experimental design tools."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.science_bot",
        class_name="ScienceBot",
        capabilities=["science", "research", "stem", "analysis"],
    ),
    BotEntry(
        bot_id="side_hustle_finder_bot",
        display_name="Side Hustle Finder Bot",
        description=(
            "Identifies side hustle opportunities aligned to skills and time availability with income projections."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.side_hustle_finder_bot",
        class_name="SideHustleFinderBot",
        capabilities=["side_hustles", "extra_income", "opportunities"],
    ),
    BotEntry(
        bot_id="skills_gap_bot",
        display_name="Skills Gap Bot",
        description=(
            "Identifies skill gaps relative to target roles and recommends learning paths to close them."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.skills_gap_bot",
        class_name="SkillsGapBot",
        capabilities=["skills_gap", "upskilling", "learning", "career"],
    ),
    BotEntry(
        bot_id="transportation_bot",
        display_name="Transportation Bot",
        description=(
            "Supports transportation industry workers with route planning, fleet management, and logistics tools."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.transportation_bot",
        class_name="TransportationBot",
        capabilities=["transportation", "logistics", "route_planning", "fleet_management"],
    ),
    BotEntry(
        bot_id="upskill_recommender_bot",
        display_name="Upskill Recommender Bot",
        description=(
            "Recommends upskilling resources and courses tailored to career goals and market demand signals."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.upskill_recommender_bot",
        class_name="UpskillRecommenderBot",
        capabilities=["upskilling", "learning", "courses", "career"],
    ),
    BotEntry(
        bot_id="work_life_balance_bot",
        display_name="Work Life Balance Bot",
        description=(
            "Tracks work patterns, suggests boundaries, and provides strategies for sustainable work-life balance."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.work_life_balance_bot",
        class_name="WorkLifeBalanceBot",
        capabilities=["work_life_balance", "wellness", "productivity"],
    ),
    BotEntry(
        bot_id="auction_finder_bot",
        display_name="Auction Finder Bot",
        description=(
            "Discovers real estate auction opportunities, analyses bidding history, and estimates winning bids."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.auction_finder_bot",
        class_name="AuctionFinderBot",
        capabilities=["auctions", "real_estate", "bidding", "deals"],
    ),
    BotEntry(
        bot_id="cash_flow_bot",
        display_name="Cash Flow Bot",
        description=(
            "Calculates rental property cash flow with detailed income, expense, and ROI breakdowns."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.cash_flow_bot",
        class_name="CashFlowBot",
        capabilities=["cash_flow", "rental", "roi", "real_estate"],
    ),
    BotEntry(
        bot_id="commercial_analyzer_bot",
        display_name="Commercial Analyzer Bot",
        description=(
            "Analyses commercial real estate investments including cap rates, NOI, and market comparables."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.commercial_analyzer_bot",
        class_name="CommercialAnalyzerBot",
        capabilities=["commercial_real_estate", "analysis", "investment"],
    ),
    BotEntry(
        bot_id="comparable_sales_bot",
        display_name="Comparable Sales Bot",
        description=(
            "Pulls and analyses comparable sales data to support accurate property valuations."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.comparable_sales_bot",
        class_name="ComparableSalesBot",
        capabilities=["comps", "comparable_sales", "valuation", "market"],
    ),
    BotEntry(
        bot_id="deal_analyzer_bot",
        display_name="Deal Analyzer Bot",
        description=(
            "Evaluates real estate deals with comprehensive ROI, cash flow, and risk analysis."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.deal_analyzer_bot",
        class_name="DealAnalyzerBot",
        capabilities=["deal_analysis", "roi", "real_estate", "investment"],
    ),
    BotEntry(
        bot_id="fix_and_flip_bot",
        display_name="Fix And Flip Bot",
        description=(
            "Analyses fix-and-flip opportunities with renovation cost estimates, ARV calculations, and profit projections."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.fix_and_flip_bot",
        class_name="FixAndFlipBot",
        capabilities=["fix_and_flip", "renovation", "profit", "real_estate"],
    ),
    BotEntry(
        bot_id="flip_profit_calculator_bot",
        display_name="Flip Profit Calculator Bot",
        description=(
            "Calculates expected profit on house flips including purchase, renovation, carrying, and sale costs."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.flip_profit_calculator_bot",
        class_name="FlipProfitCalculatorBot",
        capabilities=["flip_profit", "calculator", "roi", "renovation"],
    ),
    BotEntry(
        bot_id="foreclosure_finder_bot",
        display_name="Foreclosure Finder Bot",
        description=(
            "Discovers pre-foreclosure and bank-owned properties with automated alerts and deal scoring."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.foreclosure_finder_bot",
        class_name="ForeclosureFinderBot",
        capabilities=["foreclosures", "distressed_properties", "deals"],
    ),
    BotEntry(
        bot_id="insurance_estimator_bot",
        display_name="Insurance Estimator Bot",
        description=(
            "Estimates property insurance costs and recommends coverage options for real estate investors."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.insurance_estimator_bot",
        class_name="InsuranceEstimatorBot",
        capabilities=["insurance", "estimates", "property", "coverage"],
    ),
    BotEntry(
        bot_id="investor_matchmaker_bot",
        display_name="Investor Matchmaker Bot",
        description=(
            "Connects real estate investors with deal partners, private lenders, and joint venture opportunities."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.investor_matchmaker_bot",
        class_name="InvestorMatchmakerBot",
        capabilities=["investor_matching", "capital", "deals", "networking"],
    ),
    BotEntry(
        bot_id="land_analyzer_bot",
        display_name="Land Analyzer Bot",
        description=(
            "Analyses raw land parcels for development potential, zoning compliance, and investment value."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.land_analyzer_bot",
        class_name="LandAnalyzerBot",
        capabilities=["land_analysis", "zoning", "development", "real_estate"],
    ),
    BotEntry(
        bot_id="lease_generator_bot",
        display_name="Lease Generator Bot",
        description=(
            "Generates legally-sound residential and commercial lease agreements with customisable terms."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.lease_generator_bot",
        class_name="LeaseGeneratorBot",
        capabilities=["leases", "contracts", "rental", "legal"],
    ),
    BotEntry(
        bot_id="mortgage_calculator_bot",
        display_name="Mortgage Calculator Bot",
        description=(
            "Calculates mortgage payments, amortisation schedules, and financing scenarios for property purchases."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.mortgage_calculator_bot",
        class_name="MortgageCalculatorBot",
        capabilities=["mortgage", "calculations", "financing", "loans"],
    ),
    BotEntry(
        bot_id="multifamily_analyzer_bot",
        display_name="Multifamily Analyzer Bot",
        description=(
            "Evaluates multifamily property investments with unit-level analysis, cap rate, and cash flow modelling."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.multifamily_analyzer_bot",
        class_name="MultifamilyAnalyzerBot",
        capabilities=["multifamily", "apartments", "cap_rate", "cashflow"],
    ),
    BotEntry(
        bot_id="neighborhood_scorer_bot",
        display_name="Neighborhood Scorer Bot",
        description=(
            "Scores neighbourhoods on safety, schools, amenities, and appreciation potential for investment decisions."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.neighborhood_scorer_bot",
        class_name="NeighborhoodScorerBot",
        capabilities=["neighborhood_scoring", "location", "amenities", "safety"],
    ),
    BotEntry(
        bot_id="off_market_finder_bot",
        display_name="Off Market Finder Bot",
        description=(
            "Sources off-market property deals through skip tracing, direct mail, and motivated seller outreach."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.off_market_finder_bot",
        class_name="OffMarketFinderBot",
        capabilities=["off_market", "deals", "sourcing", "leads"],
    ),
    BotEntry(
        bot_id="property_alert_bot",
        display_name="Property Alert Bot",
        description=(
            "Monitors MLS and public records to alert investors when matching properties come to market."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.property_alert_bot",
        class_name="PropertyAlertBot",
        capabilities=["property_alerts", "notifications", "market", "watchlist"],
    ),
    BotEntry(
        bot_id="property_management_bot",
        display_name="Property Management Bot",
        description=(
            "Automates property management tasks including tenant communication, rent collection, and maintenance."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.property_management_bot",
        class_name="PropertyManagementBot",
        capabilities=["property_management", "tenants", "maintenance", "rent"],
    ),
    BotEntry(
        bot_id="property_valuation_bot",
        display_name="Property Valuation Bot",
        description=(
            "Estimates property values using comparable sales, income approach, and automated valuation models."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.property_valuation_bot",
        class_name="PropertyValuationBot",
        capabilities=["property_valuation", "appraisal", "arv", "market"],
    ),
    BotEntry(
        bot_id="renovation_cost_bot",
        display_name="Renovation Cost Bot",
        description=(
            "Estimates renovation costs by scope, material, and region to plan fix-and-flip and BRRRR projects."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.renovation_cost_bot",
        class_name="RenovationCostBot",
        capabilities=["renovation_costs", "estimates", "contractors", "budgeting"],
    ),
    BotEntry(
        bot_id="rental_income_bot",
        display_name="Rental Income Bot",
        description=(
            "Projects rental income potential with market rate analysis, occupancy modelling, and cash flow forecasting."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.rental_income_bot",
        class_name="RentalIncomeBot",
        capabilities=["rental_income", "cash_flow", "roi", "analysis"],
    ),
    BotEntry(
        bot_id="roi_tracker_bot",
        display_name="Roi Tracker Bot",
        description=(
            "Tracks ROI across a real estate portfolio with performance dashboards and investment benchmarks."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.roi_tracker_bot",
        class_name="ROITrackerBot",
        capabilities=["roi_tracking", "investment", "performance", "reporting"],
    ),
    BotEntry(
        bot_id="short_sale_finder_bot",
        display_name="Short Sale Finder Bot",
        description=(
            "Identifies short sale opportunities and guides investors through negotiation and approval processes."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.short_sale_finder_bot",
        class_name="ShortSaleFinderBot",
        capabilities=["short_sales", "distressed", "negotiation", "deals"],
    ),
    BotEntry(
        bot_id="tax_lien_bot",
        display_name="Tax Lien Bot",
        description=(
            "Researches tax lien certificates and deeds for high-yield investment opportunities across jurisdictions."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.tax_lien_bot",
        class_name="TaxLienBot",
        capabilities=["tax_liens", "certificates", "investing", "returns"],
    ),
    BotEntry(
        bot_id="tenant_screening_bot",
        display_name="Tenant Screening Bot",
        description=(
            "Automates tenant screening with background checks, credit analysis, and income verification."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.tenant_screening_bot",
        class_name="TenantScreeningBot",
        capabilities=["tenant_screening", "background_checks", "applications"],
    ),
    BotEntry(
        bot_id="wholesaler_bot",
        display_name="Wholesaler Bot",
        description=(
            "Supports real estate wholesalers with deal sourcing, contract assignment, and buyer list management."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.wholesaler_bot",
        class_name="WholesalerBot",
        capabilities=["wholesale", "real_estate", "deals", "contracts", "assignment"],
    ),
    BotEntry(
        bot_id="zoning_research_bot",
        display_name="Zoning Research Bot",
        description=(
            "Researches zoning regulations, permit requirements, and land use restrictions for real estate projects."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.zoning_research_bot",
        class_name="ZoningResearchBot",
        capabilities=["zoning", "permits", "land_use", "development"],
    ),
]
