# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY
# Regenerate with: python3 tools/compile_bot_registry.py
#
# Bot Library — DreamCo Global Bot Communication Network.
#
# Catalogs and registers all DreamCo bots so they can be discovered,
# configured, and operated through the GBN.  Each entry derives from a
# namespace + source path, which eliminates duplicate IDs, naming drift,
# and manual sync errors between directories and the registry.
#
# Namespace map:
#   core     → bots/          (trusted core bots — no prefix)
#   app      → App_bots/
#   biz      → Business_bots/
#   fvr      → Fiverr_bots/
#   mkt      → Marketing_bots/
#   occ      → Occupational_bots/
#   re       → Real_Estate_bots/

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
    # Registry compiler fields — set automatically; do not write by hand
    namespace: str = ""       # e.g. "core", "app", "biz", "fvr", "mkt", "occ", "re"
    source_path: str = ""     # e.g. "Real_Estate_bots/foreclosure_finder_bot.py"

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
            "namespace": self.namespace,
            "source_path": self.source_path,
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
            "Unified gateway for Big Tech & AI services (Google Cloud AI, Enterprise AI, "
            "Microsoft Azure AI, Nvidia AI, AWS), Big Data/Analytics (Databricks, "
            "Palantir, Snowflake, Tableau), Communication & Collaboration (Slack, "
            "Teams, Zoom), subscription resales, and proprietary Dream AI Models."
        ),
        category=BotCategory.AI,
        module_path="bots.enterprise_integrations_bot.enterprise_integrations_bot",
        class_name="EnterpriseIntegrationsBot",
        capabilities=[
            "google_cloud_ai", "enterprise_ai", "azure_ai", "nvidia_ai", "aws_ai",
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


    # <<< BEGIN GENERATED CATALOGUE >>>
# Generated at 2026-05-21T17:32:05Z by tools/compile_bot_registry.py
# Total bots: 230

    BotEntry(
        bot_id="pr_learning_bot",
        display_name="Pr Learning Bot",
        description=(
            "Pr Learning Bot — core DreamCo automation system."
        ),
        category=BotCategory.SYSTEM,
        module_path="bots.pr_learning_bot",
        class_name="PullRequestLearningBot",
        version="1.0.0",
        capabilities=[],
        namespace="core",
        source_path="bots/pr_learning_bot.py",
    ),
    BotEntry(
        bot_id="app_ab_testing_bot",
        display_name="Ab Testing Bot",
        description=(
            "Ab Testing Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.ab_testing_bot",
        class_name="ABTestingBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/ab_testing_bot.py",
    ),
    BotEntry(
        bot_id="app_accessibility_bot",
        display_name="Accessibility Bot",
        description=(
            "Accessibility Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.accessibility_bot",
        class_name="AccessibilityBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/accessibility_bot.py",
    ),
    BotEntry(
        bot_id="app_analytics_bot",
        display_name="Analytics Bot",
        description=(
            "Analytics Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.analytics_bot",
        class_name="AnalyticsBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/analytics_bot.py",
    ),
    BotEntry(
        bot_id="app_api_rate_limiter_bot",
        display_name="Api Rate Limiter Bot",
        description=(
            "Api Rate Limiter Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.api_rate_limiter_bot",
        class_name="APIRateLimiterBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/api_rate_limiter_bot.py",
    ),
    BotEntry(
        bot_id="app_app_store_optimizer_bot",
        display_name="App Store Optimizer Bot",
        description=(
            "App Store Optimizer Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.app_store_optimizer_bot",
        class_name="AppStoreOptimizerBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/app_store_optimizer_bot.py",
    ),
    BotEntry(
        bot_id="app_beta_tester_bot",
        display_name="Beta Tester Bot",
        description=(
            "Beta Tester Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.beta_tester_bot",
        class_name="BetaTesterBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/beta_tester_bot.py",
    ),
    BotEntry(
        bot_id="app_books_app_bot",
        display_name="Books App Bot",
        description=(
            "Books App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.books_app_bot",
        class_name="BooksAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/books_app_bot.py",
    ),
    BotEntry(
        bot_id="app_business_app_bot",
        display_name="Business App Bot",
        description=(
            "Business App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.business_app_bot",
        class_name="BusinessAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/business_app_bot.py",
    ),
    BotEntry(
        bot_id="app_churn_predictor_bot",
        display_name="Churn Predictor Bot",
        description=(
            "Churn Predictor Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.churn_predictor_bot",
        class_name="ChurnPredictorBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/churn_predictor_bot.py",
    ),
    BotEntry(
        bot_id="app_crash_reporter_bot",
        display_name="Crash Reporter Bot",
        description=(
            "Crash Reporter Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.crash_reporter_bot",
        class_name="CrashReporterBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/crash_reporter_bot.py",
    ),
    BotEntry(
        bot_id="app_deep_link_bot",
        display_name="Deep Link Bot",
        description=(
            "Deep Link Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.deep_link_bot",
        class_name="DeepLinkBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/deep_link_bot.py",
    ),
    BotEntry(
        bot_id="app_education_app_bot",
        display_name="Education App Bot",
        description=(
            "Education App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.education_app_bot",
        class_name="EducationAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/education_app_bot.py",
    ),
    BotEntry(
        bot_id="app_entertainment_app_bot",
        display_name="Entertainment App Bot",
        description=(
            "Entertainment App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.entertainment_app_bot",
        class_name="EntertainmentAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/entertainment_app_bot.py",
    ),
    BotEntry(
        bot_id="app_feature_flag_bot",
        display_name="Feature Flag Bot",
        description=(
            "Feature Flag Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.feature_flag_bot",
        class_name="FeatureFlagBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/feature_flag_bot.py",
    ),
    BotEntry(
        bot_id="app_finance_app_bot",
        display_name="Finance App Bot",
        description=(
            "Finance App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.finance_app_bot",
        class_name="FinanceAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/finance_app_bot.py",
    ),
    BotEntry(
        bot_id="app_food_drink_app_bot",
        display_name="Food Drink App Bot",
        description=(
            "Food Drink App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.food_drink_app_bot",
        class_name="FoodDrinkAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/food_drink_app_bot.py",
    ),
    BotEntry(
        bot_id="app_games_app_bot",
        display_name="Games App Bot",
        description=(
            "Games App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.games_app_bot",
        class_name="GamesAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/games_app_bot.py",
    ),
    BotEntry(
        bot_id="app_gamification_bot",
        display_name="Gamification Bot",
        description=(
            "Gamification Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.gamification_bot",
        class_name="GamificationBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/gamification_bot.py",
    ),
    BotEntry(
        bot_id="app_health_fitness_app_bot",
        display_name="Health Fitness App Bot",
        description=(
            "Health Fitness App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.health_fitness_app_bot",
        class_name="HealthFitnessAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/health_fitness_app_bot.py",
    ),
    BotEntry(
        bot_id="app_in_app_purchase_bot",
        display_name="In App Purchase Bot",
        description=(
            "In App Purchase Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.in_app_purchase_bot",
        class_name="InAppPurchaseBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/in_app_purchase_bot.py",
    ),
    BotEntry(
        bot_id="app_kids_family_app_bot",
        display_name="Kids Family App Bot",
        description=(
            "Kids Family App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.kids_family_app_bot",
        class_name="KidsFamilyAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/kids_family_app_bot.py",
    ),
    BotEntry(
        bot_id="app_lifestyle_app_bot",
        display_name="Lifestyle App Bot",
        description=(
            "Lifestyle App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.lifestyle_app_bot",
        class_name="LifestyleAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/lifestyle_app_bot.py",
    ),
    BotEntry(
        bot_id="app_localization_bot",
        display_name="Localization Bot",
        description=(
            "Localization Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.localization_bot",
        class_name="LocalizationBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/localization_bot.py",
    ),
    BotEntry(
        bot_id="app_medical_app_bot",
        display_name="Medical App Bot",
        description=(
            "Medical App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.medical_app_bot",
        class_name="MedicalAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/medical_app_bot.py",
    ),
    BotEntry(
        bot_id="app_monetization_bot",
        display_name="Monetization Bot",
        description=(
            "Monetization Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.monetization_bot",
        class_name="MonetizationBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/monetization_bot.py",
    ),
    BotEntry(
        bot_id="app_music_app_bot",
        display_name="Music App Bot",
        description=(
            "Music App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.music_app_bot",
        class_name="MusicAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/music_app_bot.py",
    ),
    BotEntry(
        bot_id="app_navigation_app_bot",
        display_name="Navigation App Bot",
        description=(
            "Navigation App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.navigation_app_bot",
        class_name="NavigationAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/navigation_app_bot.py",
    ),
    BotEntry(
        bot_id="app_news_app_bot",
        display_name="News App Bot",
        description=(
            "News App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.news_app_bot",
        class_name="NewsAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/news_app_bot.py",
    ),
    BotEntry(
        bot_id="app_onboarding_funnel_bot",
        display_name="Onboarding Funnel Bot",
        description=(
            "Onboarding Funnel Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.onboarding_funnel_bot",
        class_name="OnboardingFunnelBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/onboarding_funnel_bot.py",
    ),
    BotEntry(
        bot_id="app_payment_gateway_bot",
        display_name="Payment Gateway Bot",
        description=(
            "Payment Gateway Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.payment_gateway_bot",
        class_name="PaymentGatewayBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/payment_gateway_bot.py",
    ),
    BotEntry(
        bot_id="app_performance_monitor_bot",
        display_name="Performance Monitor Bot",
        description=(
            "Performance Monitor Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.performance_monitor_bot",
        class_name="PerformanceMonitorBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/performance_monitor_bot.py",
    ),
    BotEntry(
        bot_id="app_personalization_bot",
        display_name="Personalization Bot",
        description=(
            "Personalization Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.personalization_bot",
        class_name="PersonalizationBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/personalization_bot.py",
    ),
    BotEntry(
        bot_id="app_photo_video_app_bot",
        display_name="Photo Video App Bot",
        description=(
            "Photo Video App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.photo_video_app_bot",
        class_name="PhotoVideoAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/photo_video_app_bot.py",
    ),
    BotEntry(
        bot_id="app_productivity_app_bot",
        display_name="Productivity App Bot",
        description=(
            "Productivity App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.productivity_app_bot",
        class_name="ProductivityAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/productivity_app_bot.py",
    ),
    BotEntry(
        bot_id="app_push_notification_bot",
        display_name="Push Notification Bot",
        description=(
            "Push Notification Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.push_notification_bot",
        class_name="PushNotificationBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/push_notification_bot.py",
    ),
    BotEntry(
        bot_id="app_reference_app_bot",
        display_name="Reference App Bot",
        description=(
            "Reference App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.reference_app_bot",
        class_name="ReferenceAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/reference_app_bot.py",
    ),
    BotEntry(
        bot_id="app_referral_program_bot",
        display_name="Referral Program Bot",
        description=(
            "Referral Program Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.referral_program_bot",
        class_name="ReferralProgramBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/referral_program_bot.py",
    ),
    BotEntry(
        bot_id="app_review_collector_bot",
        display_name="Review Collector Bot",
        description=(
            "Review Collector Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.review_collector_bot",
        class_name="ReviewCollectorBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/review_collector_bot.py",
    ),
    BotEntry(
        bot_id="app_session_tracker_bot",
        display_name="Session Tracker Bot",
        description=(
            "Session Tracker Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.session_tracker_bot",
        class_name="SessionTrackerBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/session_tracker_bot.py",
    ),
    BotEntry(
        bot_id="app_shopping_app_bot",
        display_name="Shopping App Bot",
        description=(
            "Shopping App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.shopping_app_bot",
        class_name="ShoppingAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/shopping_app_bot.py",
    ),
    BotEntry(
        bot_id="app_social_networking_app_bot",
        display_name="Social Networking App Bot",
        description=(
            "Social Networking App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.social_networking_app_bot",
        class_name="SocialNetworkingAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/social_networking_app_bot.py",
    ),
    BotEntry(
        bot_id="app_social_sharing_bot",
        display_name="Social Sharing Bot",
        description=(
            "Social Sharing Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.social_sharing_bot",
        class_name="SocialSharingBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/social_sharing_bot.py",
    ),
    BotEntry(
        bot_id="app_sports_app_bot",
        display_name="Sports App Bot",
        description=(
            "Sports App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.sports_app_bot",
        class_name="SportsAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/sports_app_bot.py",
    ),
    BotEntry(
        bot_id="app_subscription_manager_bot",
        display_name="Subscription Manager Bot",
        description=(
            "Subscription Manager Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.subscription_manager_bot",
        class_name="SubscriptionManagerBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/subscription_manager_bot.py",
    ),
    BotEntry(
        bot_id="app_travel_app_bot",
        display_name="Travel App Bot",
        description=(
            "Travel App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.travel_app_bot",
        class_name="TravelAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/travel_app_bot.py",
    ),
    BotEntry(
        bot_id="app_user_feedback_bot",
        display_name="User Feedback Bot",
        description=(
            "User Feedback Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.user_feedback_bot",
        class_name="UserFeedbackBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/user_feedback_bot.py",
    ),
    BotEntry(
        bot_id="app_user_retention_bot",
        display_name="User Retention Bot",
        description=(
            "User Retention Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.user_retention_bot",
        class_name="UserRetentionBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/user_retention_bot.py",
    ),
    BotEntry(
        bot_id="app_user_segmentation_bot",
        display_name="User Segmentation Bot",
        description=(
            "User Segmentation Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.user_segmentation_bot",
        class_name="UserSegmentationBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/user_segmentation_bot.py",
    ),
    BotEntry(
        bot_id="app_utilities_app_bot",
        display_name="Utilities App Bot",
        description=(
            "Utilities App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.utilities_app_bot",
        class_name="UtilitiesAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/utilities_app_bot.py",
    ),
    BotEntry(
        bot_id="app_weather_app_bot",
        display_name="Weather App Bot",
        description=(
            "Weather App Bot — mobile app automation bot."
        ),
        category=BotCategory.APP,
        module_path="App_bots.weather_app_bot",
        class_name="WeatherAppBot",
        version="1.0.0",
        capabilities=[],
        namespace="app",
        source_path="App_bots/weather_app_bot.py",
    ),
    BotEntry(
        bot_id="biz_accommodation_food_bot",
        display_name="Accommodation Food Bot",
        description=(
            "Accommodation Food Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.accommodation_food_bot",
        class_name="AccommodationFoodBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/accommodation_food_bot.py",
    ),
    BotEntry(
        bot_id="biz_administrative_support_industry_bot",
        display_name="Administrative Support Industry Bot",
        description=(
            "Administrative Support Industry Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.administrative_support_industry_bot",
        class_name="AdministrativeSupportIndustryBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/administrative_support_industry_bot.py",
    ),
    BotEntry(
        bot_id="biz_agriculture_bot",
        display_name="Agriculture Bot",
        description=(
            "Agriculture Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.agriculture_bot",
        class_name="AgricultureBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/agriculture_bot.py",
    ),
    BotEntry(
        bot_id="biz_arts_entertainment_bot",
        display_name="Arts Entertainment Bot",
        description=(
            "Arts Entertainment Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.arts_entertainment_bot",
        class_name="ArtsEntertainmentBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/arts_entertainment_bot.py",
    ),
    BotEntry(
        bot_id="biz_brand_monitor_bot",
        display_name="Brand Monitor Bot",
        description=(
            "Brand Monitor Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.brand_monitor_bot",
        class_name="BrandMonitorBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/brand_monitor_bot.py",
    ),
    BotEntry(
        bot_id="biz_business_plan_bot",
        display_name="Business Plan Bot",
        description=(
            "Business Plan Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.business_plan_bot",
        class_name="BusinessPlanBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/business_plan_bot.py",
    ),
    BotEntry(
        bot_id="biz_competitor_analyzer_bot",
        display_name="Competitor Analyzer Bot",
        description=(
            "Competitor Analyzer Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.competitor_analyzer_bot",
        class_name="CompetitorAnalyzerBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/competitor_analyzer_bot.py",
    ),
    BotEntry(
        bot_id="biz_compliance_checker_bot",
        display_name="Compliance Checker Bot",
        description=(
            "Compliance Checker Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.compliance_checker_bot",
        class_name="ComplianceCheckerBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/compliance_checker_bot.py",
    ),
    BotEntry(
        bot_id="biz_construction_bot",
        display_name="Construction Bot",
        description=(
            "Construction Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.construction_bot",
        class_name="ConstructionBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/construction_bot.py",
    ),
    BotEntry(
        bot_id="biz_contract_generator_bot",
        display_name="Contract Generator Bot",
        description=(
            "Contract Generator Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.contract_generator_bot",
        class_name="ContractGeneratorBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/contract_generator_bot.py",
    ),
    BotEntry(
        bot_id="biz_customer_support_bot",
        display_name="Customer Support Bot",
        description=(
            "Customer Support Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.customer_support_bot",
        class_name="CustomerSupportBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/customer_support_bot.py",
    ),
    BotEntry(
        bot_id="biz_document_manager_bot",
        display_name="Document Manager Bot",
        description=(
            "Document Manager Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.document_manager_bot",
        class_name="DocumentManagerBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/document_manager_bot.py",
    ),
    BotEntry(
        bot_id="biz_ecommerce_optimizer_bot",
        display_name="Ecommerce Optimizer Bot",
        description=(
            "Ecommerce Optimizer Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.ecommerce_optimizer_bot",
        class_name="EcommerceOptimizerBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/ecommerce_optimizer_bot.py",
    ),
    BotEntry(
        bot_id="biz_educational_services_bot",
        display_name="Educational Services Bot",
        description=(
            "Educational Services Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.educational_services_bot",
        class_name="EducationalServicesBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/educational_services_bot.py",
    ),
    BotEntry(
        bot_id="biz_employee_onboarding_bot",
        display_name="Employee Onboarding Bot",
        description=(
            "Employee Onboarding Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.employee_onboarding_bot",
        class_name="EmployeeOnboardingBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/employee_onboarding_bot.py",
    ),
    BotEntry(
        bot_id="biz_expense_tracker_bot",
        display_name="Expense Tracker Bot",
        description=(
            "Expense Tracker Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.expense_tracker_bot",
        class_name="ExpenseTrackerBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/expense_tracker_bot.py",
    ),
    BotEntry(
        bot_id="biz_finance_insurance_bot",
        display_name="Finance Insurance Bot",
        description=(
            "Finance Insurance Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.finance_insurance_bot",
        class_name="FinanceInsuranceBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/finance_insurance_bot.py",
    ),
    BotEntry(
        bot_id="biz_financial_forecaster_bot",
        display_name="Financial Forecaster Bot",
        description=(
            "Financial Forecaster Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.financial_forecaster_bot",
        class_name="FinancialForecasterBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/financial_forecaster_bot.py",
    ),
    BotEntry(
        bot_id="biz_franchise_analyzer_bot",
        display_name="Franchise Analyzer Bot",
        description=(
            "Franchise Analyzer Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.franchise_analyzer_bot",
        class_name="FranchiseAnalyzerBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/franchise_analyzer_bot.py",
    ),
    BotEntry(
        bot_id="biz_grant_finder_bot",
        display_name="Grant Finder Bot",
        description=(
            "Grant Finder Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.grant_finder_bot",
        class_name="GrantFinderBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/grant_finder_bot.py",
    ),
    BotEntry(
        bot_id="biz_health_care_bot",
        display_name="Health Care Bot",
        description=(
            "Health Care Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.health_care_bot",
        class_name="HealthCareBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/health_care_bot.py",
    ),
    BotEntry(
        bot_id="biz_information_bot",
        display_name="Information Bot",
        description=(
            "Information Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.information_bot",
        class_name="InformationBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/information_bot.py",
    ),
    BotEntry(
        bot_id="biz_insurance_advisor_bot",
        display_name="Insurance Advisor Bot",
        description=(
            "Insurance Advisor Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.insurance_advisor_bot",
        class_name="InsuranceAdvisorBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/insurance_advisor_bot.py",
    ),
    BotEntry(
        bot_id="biz_inventory_manager_bot",
        display_name="Inventory Manager Bot",
        description=(
            "Inventory Manager Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.inventory_manager_bot",
        class_name="InventoryManagerBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/inventory_manager_bot.py",
    ),
    BotEntry(
        bot_id="biz_kpi_tracker_bot",
        display_name="Kpi Tracker Bot",
        description=(
            "Kpi Tracker Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.kpi_tracker_bot",
        class_name="KPITrackerBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/kpi_tracker_bot.py",
    ),
    BotEntry(
        bot_id="biz_llc_formation_bot",
        display_name="Llc Formation Bot",
        description=(
            "Llc Formation Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.llc_formation_bot",
        class_name="LLCFormationBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/llc_formation_bot.py",
    ),
    BotEntry(
        bot_id="biz_management_companies_bot",
        display_name="Management Companies Bot",
        description=(
            "Management Companies Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.management_companies_bot",
        class_name="ManagementCompaniesBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/management_companies_bot.py",
    ),
    BotEntry(
        bot_id="biz_manufacturing_bot",
        display_name="Manufacturing Bot",
        description=(
            "Manufacturing Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.manufacturing_bot",
        class_name="ManufacturingBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/manufacturing_bot.py",
    ),
    BotEntry(
        bot_id="biz_market_research_bot",
        display_name="Market Research Bot",
        description=(
            "Market Research Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.market_research_bot",
        class_name="MarketResearchBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/market_research_bot.py",
    ),
    BotEntry(
        bot_id="biz_meeting_scheduler_bot",
        display_name="Meeting Scheduler Bot",
        description=(
            "Meeting Scheduler Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.meeting_scheduler_bot",
        class_name="MeetingSchedulerBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/meeting_scheduler_bot.py",
    ),
    BotEntry(
        bot_id="biz_mining_bot",
        display_name="Mining Bot",
        description=(
            "Mining Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.mining_bot",
        class_name="MiningBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/mining_bot.py",
    ),
    BotEntry(
        bot_id="biz_other_services_bot",
        display_name="Other Services Bot",
        description=(
            "Other Services Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.other_services_bot",
        class_name="OtherServicesBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/other_services_bot.py",
    ),
    BotEntry(
        bot_id="biz_partnership_finder_bot",
        display_name="Partnership Finder Bot",
        description=(
            "Partnership Finder Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.partnership_finder_bot",
        class_name="PartnershipFinderBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/partnership_finder_bot.py",
    ),
    BotEntry(
        bot_id="biz_payroll_bot",
        display_name="Payroll Bot",
        description=(
            "Payroll Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.payroll_bot",
        class_name="PayrollBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/payroll_bot.py",
    ),
    BotEntry(
        bot_id="biz_pitch_deck_bot",
        display_name="Pitch Deck Bot",
        description=(
            "Pitch Deck Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.pitch_deck_bot",
        class_name="PitchDeckBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/pitch_deck_bot.py",
    ),
    BotEntry(
        bot_id="biz_pricing_strategy_bot",
        display_name="Pricing Strategy Bot",
        description=(
            "Pricing Strategy Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.pricing_strategy_bot",
        class_name="PricingStrategyBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/pricing_strategy_bot.py",
    ),
    BotEntry(
        bot_id="biz_professional_services_bot",
        display_name="Professional Services Bot",
        description=(
            "Professional Services Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.professional_services_bot",
        class_name="ProfessionalServicesBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/professional_services_bot.py",
    ),
    BotEntry(
        bot_id="biz_public_administration_bot",
        display_name="Public Administration Bot",
        description=(
            "Public Administration Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.public_administration_bot",
        class_name="PublicAdministrationBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/public_administration_bot.py",
    ),
    BotEntry(
        bot_id="biz_real_estate_leasing_bot",
        display_name="Real Estate Leasing Bot",
        description=(
            "Real Estate Leasing Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.real_estate_leasing_bot",
        class_name="RealEstateLeasingBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/real_estate_leasing_bot.py",
    ),
    BotEntry(
        bot_id="biz_retail_trade_bot",
        display_name="Retail Trade Bot",
        description=(
            "Retail Trade Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.retail_trade_bot",
        class_name="RetailTradeBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/retail_trade_bot.py",
    ),
    BotEntry(
        bot_id="biz_sales_pipeline_bot",
        display_name="Sales Pipeline Bot",
        description=(
            "Sales Pipeline Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.sales_pipeline_bot",
        class_name="SalesPipelineBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/sales_pipeline_bot.py",
    ),
    BotEntry(
        bot_id="biz_supply_chain_bot",
        display_name="Supply Chain Bot",
        description=(
            "Supply Chain Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.supply_chain_bot",
        class_name="SupplyChainBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/supply_chain_bot.py",
    ),
    BotEntry(
        bot_id="biz_tax_preparer_bot",
        display_name="Tax Preparer Bot",
        description=(
            "Tax Preparer Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.tax_preparer_bot",
        class_name="TaxPreparerBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/tax_preparer_bot.py",
    ),
    BotEntry(
        bot_id="biz_transportation_warehousing_bot",
        display_name="Transportation Warehousing Bot",
        description=(
            "Transportation Warehousing Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.transportation_warehousing_bot",
        class_name="TransportationWarehousingBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/transportation_warehousing_bot.py",
    ),
    BotEntry(
        bot_id="biz_utilities_bot",
        display_name="Utilities Bot",
        description=(
            "Utilities Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.utilities_bot",
        class_name="UtilitiesBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/utilities_bot.py",
    ),
    BotEntry(
        bot_id="biz_vendor_manager_bot",
        display_name="Vendor Manager Bot",
        description=(
            "Vendor Manager Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.vendor_manager_bot",
        class_name="VendorManagerBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/vendor_manager_bot.py",
    ),
    BotEntry(
        bot_id="biz_wholesale_trade_bot",
        display_name="Wholesale Trade Bot",
        description=(
            "Wholesale Trade Bot — business operations automation bot."
        ),
        category=BotCategory.BUSINESS,
        module_path="Business_bots.wholesale_trade_bot",
        class_name="WholesaleTradeBot",
        version="1.0.0",
        capabilities=[],
        namespace="biz",
        source_path="Business_bots/wholesale_trade_bot.py",
    ),
    BotEntry(
        bot_id="fvr_buyer_persona_bot",
        display_name="Buyer Persona Bot",
        description=(
            "Buyer Persona Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.buyer_persona_bot",
        class_name="BuyerPersonaBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/buyer_persona_bot.py",
    ),
    BotEntry(
        bot_id="fvr_client_finder_bot",
        display_name="Client Finder Bot",
        description=(
            "Client Finder Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.client_finder_bot",
        class_name="ClientFinderBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/client_finder_bot.py",
    ),
    BotEntry(
        bot_id="fvr_client_retention_bot",
        display_name="Client Retention Bot",
        description=(
            "Client Retention Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.client_retention_bot",
        class_name="ClientRetentionBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/client_retention_bot.py",
    ),
    BotEntry(
        bot_id="fvr_competitor_spy_bot",
        display_name="Competitor Spy Bot",
        description=(
            "Competitor Spy Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.competitor_spy_bot",
        class_name="CompetitorSpyBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/competitor_spy_bot.py",
    ),
    BotEntry(
        bot_id="fvr_cross_sell_bot",
        display_name="Cross Sell Bot",
        description=(
            "Cross Sell Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.cross_sell_bot",
        class_name="CrossSellBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/cross_sell_bot.py",
    ),
    BotEntry(
        bot_id="fvr_deadline_tracker_bot",
        display_name="Deadline Tracker Bot",
        description=(
            "Deadline Tracker Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.deadline_tracker_bot",
        class_name="DeadlineTrackerBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/deadline_tracker_bot.py",
    ),
    BotEntry(
        bot_id="fvr_dispute_resolver_bot",
        display_name="Dispute Resolver Bot",
        description=(
            "Dispute Resolver Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.dispute_resolver_bot",
        class_name="DisputeResolverBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/dispute_resolver_bot.py",
    ),
    BotEntry(
        bot_id="fvr_earnings_tracker_bot",
        display_name="Earnings Tracker Bot",
        description=(
            "Earnings Tracker Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.earnings_tracker_bot",
        class_name="EarningsTrackerBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/earnings_tracker_bot.py",
    ),
    BotEntry(
        bot_id="fvr_feedback_analyzer_bot",
        display_name="Feedback Analyzer Bot",
        description=(
            "Feedback Analyzer Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.feedback_analyzer_bot",
        class_name="FeedbackAnalyzerBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/feedback_analyzer_bot.py",
    ),
    BotEntry(
        bot_id="fvr_fiverr_bot",
        display_name="Fiverr Bot",
        description=(
            "Fiverr Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.fiverr_bot",
        class_name="FiverrBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/fiverr_bot.py",
    ),
    BotEntry(
        bot_id="fvr_gig_description_optimizer_bot",
        display_name="Gig Description Optimizer Bot",
        description=(
            "Gig Description Optimizer Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.gig_description_optimizer_bot",
        class_name="GigDescriptionOptimizerBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/gig_description_optimizer_bot.py",
    ),
    BotEntry(
        bot_id="fvr_gig_image_optimizer_bot",
        display_name="Gig Image Optimizer Bot",
        description=(
            "Gig Image Optimizer Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.gig_image_optimizer_bot",
        class_name="GigImageOptimizerBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/gig_image_optimizer_bot.py",
    ),
    BotEntry(
        bot_id="fvr_gig_ranking_bot",
        display_name="Gig Ranking Bot",
        description=(
            "Gig Ranking Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.gig_ranking_bot",
        class_name="GigRankingBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/gig_ranking_bot.py",
    ),
    BotEntry(
        bot_id="fvr_inbox_automation_bot",
        display_name="Inbox Automation Bot",
        description=(
            "Inbox Automation Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.inbox_automation_bot",
        class_name="InboxAutomationBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/inbox_automation_bot.py",
    ),
    BotEntry(
        bot_id="fvr_level_up_bot",
        display_name="Level Up Bot",
        description=(
            "Level Up Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.level_up_bot",
        class_name="LevelUpBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/level_up_bot.py",
    ),
    BotEntry(
        bot_id="fvr_milestone_tracker_bot",
        display_name="Milestone Tracker Bot",
        description=(
            "Milestone Tracker Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.milestone_tracker_bot",
        class_name="MilestoneTrackerBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/milestone_tracker_bot.py",
    ),
    BotEntry(
        bot_id="fvr_niche_analyzer_bot",
        display_name="Niche Analyzer Bot",
        description=(
            "Niche Analyzer Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.niche_analyzer_bot",
        class_name="NicheAnalyzerBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/niche_analyzer_bot.py",
    ),
    BotEntry(
        bot_id="fvr_order_completion_bot",
        display_name="Order Completion Bot",
        description=(
            "Order Completion Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.order_completion_bot",
        class_name="OrderCompletionBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/order_completion_bot.py",
    ),
    BotEntry(
        bot_id="fvr_package_optimizer_bot",
        display_name="Package Optimizer Bot",
        description=(
            "Package Optimizer Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.package_optimizer_bot",
        class_name="PackageOptimizerBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/package_optimizer_bot.py",
    ),
    BotEntry(
        bot_id="fvr_portfolio_builder_bot",
        display_name="Portfolio Builder Bot",
        description=(
            "Portfolio Builder Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.portfolio_builder_bot",
        class_name="PortfolioBuilderBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/portfolio_builder_bot.py",
    ),
    BotEntry(
        bot_id="fvr_pricing_optimizer_bot",
        display_name="Pricing Optimizer Bot",
        description=(
            "Pricing Optimizer Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.pricing_optimizer_bot",
        class_name="PricingOptimizerBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/pricing_optimizer_bot.py",
    ),
    BotEntry(
        bot_id="fvr_proposal_writer_bot",
        display_name="Proposal Writer Bot",
        description=(
            "Proposal Writer Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.proposal_writer_bot",
        class_name="ProposalWriterBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/proposal_writer_bot.py",
    ),
    BotEntry(
        bot_id="fvr_response_time_bot",
        display_name="Response Time Bot",
        description=(
            "Response Time Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.response_time_bot",
        class_name="ResponseTimeBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/response_time_bot.py",
    ),
    BotEntry(
        bot_id="fvr_revision_manager_bot",
        display_name="Revision Manager Bot",
        description=(
            "Revision Manager Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.revision_manager_bot",
        class_name="RevisionManagerBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/revision_manager_bot.py",
    ),
    BotEntry(
        bot_id="fvr_seasonal_pricing_bot",
        display_name="Seasonal Pricing Bot",
        description=(
            "Seasonal Pricing Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.seasonal_pricing_bot",
        class_name="SeasonalPricingBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/seasonal_pricing_bot.py",
    ),
    BotEntry(
        bot_id="fvr_service_expansion_bot",
        display_name="Service Expansion Bot",
        description=(
            "Service Expansion Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.service_expansion_bot",
        class_name="ServiceExpansionBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/service_expansion_bot.py",
    ),
    BotEntry(
        bot_id="fvr_skill_tagger_bot",
        display_name="Skill Tagger Bot",
        description=(
            "Skill Tagger Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.skill_tagger_bot",
        class_name="SkillTaggerBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/skill_tagger_bot.py",
    ),
    BotEntry(
        bot_id="fvr_upsell_bot",
        display_name="Upsell Bot",
        description=(
            "Upsell Bot — Fiverr platform automation bot."
        ),
        category=BotCategory.FREELANCE,
        module_path="Fiverr_bots.upsell_bot",
        class_name="UpsellBot",
        version="1.0.0",
        capabilities=[],
        namespace="fvr",
        source_path="Fiverr_bots/upsell_bot.py",
    ),
    BotEntry(
        bot_id="mkt_ab_testing_bot",
        display_name="Ab Testing Bot",
        description=(
            "Ab Testing Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.ab_testing_bot",
        class_name="ABTestingBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/ab_testing_bot.py",
    ),
    BotEntry(
        bot_id="mkt_ad_campaign_bot",
        display_name="Ad Campaign Bot",
        description=(
            "Ad Campaign Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.ad_campaign_bot",
        class_name="AdCampaignBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/ad_campaign_bot.py",
    ),
    BotEntry(
        bot_id="mkt_affiliate_marketer_bot",
        display_name="Affiliate Marketer Bot",
        description=(
            "Affiliate Marketer Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.affiliate_marketer_bot",
        class_name="AffiliateMarketerBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/affiliate_marketer_bot.py",
    ),
    BotEntry(
        bot_id="mkt_analytics_reporter_bot",
        display_name="Analytics Reporter Bot",
        description=(
            "Analytics Reporter Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.analytics_reporter_bot",
        class_name="AnalyticsReporterBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/analytics_reporter_bot.py",
    ),
    BotEntry(
        bot_id="mkt_brand_story_bot",
        display_name="Brand Story Bot",
        description=(
            "Brand Story Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.brand_story_bot",
        class_name="BrandStoryBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/brand_story_bot.py",
    ),
    BotEntry(
        bot_id="mkt_chatbot_builder_bot",
        display_name="Chatbot Builder Bot",
        description=(
            "Chatbot Builder Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.chatbot_builder_bot",
        class_name="ChatbotBuilderBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/chatbot_builder_bot.py",
    ),
    BotEntry(
        bot_id="mkt_competitor_spy_bot",
        display_name="Competitor Spy Bot",
        description=(
            "Competitor Spy Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.competitor_spy_bot",
        class_name="CompetitorSpyBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/competitor_spy_bot.py",
    ),
    BotEntry(
        bot_id="mkt_conversion_optimizer_bot",
        display_name="Conversion Optimizer Bot",
        description=(
            "Conversion Optimizer Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.conversion_optimizer_bot",
        class_name="ConversionOptimizerBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/conversion_optimizer_bot.py",
    ),
    BotEntry(
        bot_id="mkt_customer_review_bot",
        display_name="Customer Review Bot",
        description=(
            "Customer Review Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.customer_review_bot",
        class_name="CustomerReviewBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/customer_review_bot.py",
    ),
    BotEntry(
        bot_id="mkt_event_promoter_bot",
        display_name="Event Promoter Bot",
        description=(
            "Event Promoter Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.event_promoter_bot",
        class_name="EventPromoterBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/event_promoter_bot.py",
    ),
    BotEntry(
        bot_id="mkt_google_ads_bot",
        display_name="Google Ads Bot",
        description=(
            "Google Ads Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.google_ads_bot",
        class_name="GoogleAdsBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/google_ads_bot.py",
    ),
    BotEntry(
        bot_id="mkt_hashtag_analyzer_bot",
        display_name="Hashtag Analyzer Bot",
        description=(
            "Hashtag Analyzer Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.hashtag_analyzer_bot",
        class_name="HashtagAnalyzerBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/hashtag_analyzer_bot.py",
    ),
    BotEntry(
        bot_id="mkt_influencer_finder_bot",
        display_name="Influencer Finder Bot",
        description=(
            "Influencer Finder Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.influencer_finder_bot",
        class_name="InfluencerFinderBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/influencer_finder_bot.py",
    ),
    BotEntry(
        bot_id="mkt_landing_page_bot",
        display_name="Landing Page Bot",
        description=(
            "Landing Page Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.landing_page_bot",
        class_name="LandingPageBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/landing_page_bot.py",
    ),
    BotEntry(
        bot_id="mkt_lead_magnet_bot",
        display_name="Lead Magnet Bot",
        description=(
            "Lead Magnet Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.lead_magnet_bot",
        class_name="LeadMagnetBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/lead_magnet_bot.py",
    ),
    BotEntry(
        bot_id="mkt_loyalty_program_bot",
        display_name="Loyalty Program Bot",
        description=(
            "Loyalty Program Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.loyalty_program_bot",
        class_name="LoyaltyProgramBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/loyalty_program_bot.py",
    ),
    BotEntry(
        bot_id="mkt_newsletter_bot",
        display_name="Newsletter Bot",
        description=(
            "Newsletter Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.newsletter_bot",
        class_name="NewsletterBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/newsletter_bot.py",
    ),
    BotEntry(
        bot_id="mkt_podcast_promoter_bot",
        display_name="Podcast Promoter Bot",
        description=(
            "Podcast Promoter Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.podcast_promoter_bot",
        class_name="PodcastPromoterBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/podcast_promoter_bot.py",
    ),
    BotEntry(
        bot_id="mkt_press_release_bot",
        display_name="Press Release Bot",
        description=(
            "Press Release Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.press_release_bot",
        class_name="PressReleaseBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/press_release_bot.py",
    ),
    BotEntry(
        bot_id="mkt_referral_marketing_bot",
        display_name="Referral Marketing Bot",
        description=(
            "Referral Marketing Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.referral_marketing_bot",
        class_name="ReferralMarketingBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/referral_marketing_bot.py",
    ),
    BotEntry(
        bot_id="mkt_retargeting_bot",
        display_name="Retargeting Bot",
        description=(
            "Retargeting Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.retargeting_bot",
        class_name="RetargetingBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/retargeting_bot.py",
    ),
    BotEntry(
        bot_id="mkt_sales_funnel_bot",
        display_name="Sales Funnel Bot",
        description=(
            "Sales Funnel Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.sales_funnel_bot",
        class_name="SalesFunnelBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/sales_funnel_bot.py",
    ),
    BotEntry(
        bot_id="mkt_seo_optimizer_bot",
        display_name="Seo Optimizer Bot",
        description=(
            "Seo Optimizer Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.seo_optimizer_bot",
        class_name="SEOOptimizerBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/seo_optimizer_bot.py",
    ),
    BotEntry(
        bot_id="mkt_social_proof_bot",
        display_name="Social Proof Bot",
        description=(
            "Social Proof Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.social_proof_bot",
        class_name="SocialProofBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/social_proof_bot.py",
    ),
    BotEntry(
        bot_id="mkt_video_marketing_bot",
        display_name="Video Marketing Bot",
        description=(
            "Video Marketing Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.video_marketing_bot",
        class_name="VideoMarketingBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/video_marketing_bot.py",
    ),
    BotEntry(
        bot_id="mkt_viral_content_bot",
        display_name="Viral Content Bot",
        description=(
            "Viral Content Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.viral_content_bot",
        class_name="ViralContentBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/viral_content_bot.py",
    ),
    BotEntry(
        bot_id="mkt_webinar_bot",
        display_name="Webinar Bot",
        description=(
            "Webinar Bot — marketing automation bot."
        ),
        category=BotCategory.MARKETING,
        module_path="Marketing_bots.webinar_bot",
        class_name="WebinarBot",
        version="1.0.0",
        capabilities=[],
        namespace="mkt",
        source_path="Marketing_bots/webinar_bot.py",
    ),
    BotEntry(
        bot_id="occ_administrative_support_bot",
        display_name="Administrative Support Bot",
        description=(
            "Administrative Support Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.administrative_support_bot",
        class_name="AdministrativeSupportBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/administrative_support_bot.py",
    ),
    BotEntry(
        bot_id="occ_architecture_engineering_bot",
        display_name="Architecture Engineering Bot",
        description=(
            "Architecture Engineering Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.architecture_engineering_bot",
        class_name="ArchitectureEngineeringBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/architecture_engineering_bot.py",
    ),
    BotEntry(
        bot_id="occ_arts_media_bot",
        display_name="Arts Media Bot",
        description=(
            "Arts Media Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.arts_media_bot",
        class_name="ArtsMediaBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/arts_media_bot.py",
    ),
    BotEntry(
        bot_id="occ_benefits_analyzer_bot",
        display_name="Benefits Analyzer Bot",
        description=(
            "Benefits Analyzer Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.benefits_analyzer_bot",
        class_name="BenefitsAnalyzerBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/benefits_analyzer_bot.py",
    ),
    BotEntry(
        bot_id="occ_building_maintenance_bot",
        display_name="Building Maintenance Bot",
        description=(
            "Building Maintenance Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.building_maintenance_bot",
        class_name="BuildingMaintenanceBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/building_maintenance_bot.py",
    ),
    BotEntry(
        bot_id="occ_business_financial_bot",
        display_name="Business Financial Bot",
        description=(
            "Business Financial Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.business_financial_bot",
        class_name="BusinessFinancialBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/business_financial_bot.py",
    ),
    BotEntry(
        bot_id="occ_career_path_bot",
        display_name="Career Path Bot",
        description=(
            "Career Path Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.career_path_bot",
        class_name="CareerPathBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/career_path_bot.py",
    ),
    BotEntry(
        bot_id="occ_certification_advisor_bot",
        display_name="Certification Advisor Bot",
        description=(
            "Certification Advisor Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.certification_advisor_bot",
        class_name="CertificationAdvisorBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/certification_advisor_bot.py",
    ),
    BotEntry(
        bot_id="occ_community_service_bot",
        display_name="Community Service Bot",
        description=(
            "Community Service Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.community_service_bot",
        class_name="CommunityServiceBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/community_service_bot.py",
    ),
    BotEntry(
        bot_id="occ_company_culture_bot",
        display_name="Company Culture Bot",
        description=(
            "Company Culture Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.company_culture_bot",
        class_name="CompanyCultureBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/company_culture_bot.py",
    ),
    BotEntry(
        bot_id="occ_computer_math_bot",
        display_name="Computer Math Bot",
        description=(
            "Computer Math Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.computer_math_bot",
        class_name="ComputerMathBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/computer_math_bot.py",
    ),
    BotEntry(
        bot_id="occ_construction_extraction_bot",
        display_name="Construction Extraction Bot",
        description=(
            "Construction Extraction Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.construction_extraction_bot",
        class_name="ConstructionExtractionBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/construction_extraction_bot.py",
    ),
    BotEntry(
        bot_id="occ_contractor_rate_bot",
        display_name="Contractor Rate Bot",
        description=(
            "Contractor Rate Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.contractor_rate_bot",
        class_name="ContractorRateBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/contractor_rate_bot.py",
    ),
    BotEntry(
        bot_id="occ_cover_letter_bot",
        display_name="Cover Letter Bot",
        description=(
            "Cover Letter Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.cover_letter_bot",
        class_name="CoverLetterBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/cover_letter_bot.py",
    ),
    BotEntry(
        bot_id="occ_diversity_inclusion_bot",
        display_name="Diversity Inclusion Bot",
        description=(
            "Diversity Inclusion Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.diversity_inclusion_bot",
        class_name="DiversityInclusionBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/diversity_inclusion_bot.py",
    ),
    BotEntry(
        bot_id="occ_education_library_bot",
        display_name="Education Library Bot",
        description=(
            "Education Library Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.education_library_bot",
        class_name="EducationLibraryBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/education_library_bot.py",
    ),
    BotEntry(
        bot_id="occ_farming_fishing_forestry_bot",
        display_name="Farming Fishing Forestry Bot",
        description=(
            "Farming Fishing Forestry Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.farming_fishing_forestry_bot",
        class_name="FarmingFishingForestryBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/farming_fishing_forestry_bot.py",
    ),
    BotEntry(
        bot_id="occ_food_service_bot",
        display_name="Food Service Bot",
        description=(
            "Food Service Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.food_service_bot",
        class_name="FoodServiceBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/food_service_bot.py",
    ),
    BotEntry(
        bot_id="occ_freelance_rate_bot",
        display_name="Freelance Rate Bot",
        description=(
            "Freelance Rate Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.freelance_rate_bot",
        class_name="FreelanceRateBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/freelance_rate_bot.py",
    ),
    BotEntry(
        bot_id="occ_gig_economy_bot",
        display_name="Gig Economy Bot",
        description=(
            "Gig Economy Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.gig_economy_bot",
        class_name="GigEconomyBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/gig_economy_bot.py",
    ),
    BotEntry(
        bot_id="occ_headhunter_bot",
        display_name="Headhunter Bot",
        description=(
            "Headhunter Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.headhunter_bot",
        class_name="HeadhunterBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/headhunter_bot.py",
    ),
    BotEntry(
        bot_id="occ_healthcare_practitioner_bot",
        display_name="Healthcare Practitioner Bot",
        description=(
            "Healthcare Practitioner Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.healthcare_practitioner_bot",
        class_name="HealthcarePractitionerBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/healthcare_practitioner_bot.py",
    ),
    BotEntry(
        bot_id="occ_healthcare_support_bot",
        display_name="Healthcare Support Bot",
        description=(
            "Healthcare Support Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.healthcare_support_bot",
        class_name="HealthcareSupportBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/healthcare_support_bot.py",
    ),
    BotEntry(
        bot_id="occ_industry_trend_bot",
        display_name="Industry Trend Bot",
        description=(
            "Industry Trend Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.industry_trend_bot",
        class_name="IndustryTrendBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/industry_trend_bot.py",
    ),
    BotEntry(
        bot_id="occ_installation_maintenance_bot",
        display_name="Installation Maintenance Bot",
        description=(
            "Installation Maintenance Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.installation_maintenance_bot",
        class_name="InstallationMaintenanceBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/installation_maintenance_bot.py",
    ),
    BotEntry(
        bot_id="occ_job_application_tracker_bot",
        display_name="Job Application Tracker Bot",
        description=(
            "Job Application Tracker Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.job_application_tracker_bot",
        class_name="JobApplicationTrackerBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/job_application_tracker_bot.py",
    ),
    BotEntry(
        bot_id="occ_job_board_aggregator_bot",
        display_name="Job Board Aggregator Bot",
        description=(
            "Job Board Aggregator Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.job_board_aggregator_bot",
        class_name="JobBoardAggregatorBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/job_board_aggregator_bot.py",
    ),
    BotEntry(
        bot_id="occ_legal_bot",
        display_name="Legal Bot",
        description=(
            "Legal Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.legal_bot",
        class_name="LegalBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/legal_bot.py",
    ),
    BotEntry(
        bot_id="occ_linkedin_optimizer_bot",
        display_name="Linkedin Optimizer Bot",
        description=(
            "Linkedin Optimizer Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.linkedin_optimizer_bot",
        class_name="LinkedInOptimizerBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/linkedin_optimizer_bot.py",
    ),
    BotEntry(
        bot_id="occ_management_bot",
        display_name="Management Bot",
        description=(
            "Management Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.management_bot",
        class_name="ManagementBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/management_bot.py",
    ),
    BotEntry(
        bot_id="occ_mentor_finder_bot",
        display_name="Mentor Finder Bot",
        description=(
            "Mentor Finder Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.mentor_finder_bot",
        class_name="MentorFinderBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/mentor_finder_bot.py",
    ),
    BotEntry(
        bot_id="occ_military_bot",
        display_name="Military Bot",
        description=(
            "Military Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.military_bot",
        class_name="MilitaryBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/military_bot.py",
    ),
    BotEntry(
        bot_id="occ_networking_bot",
        display_name="Networking Bot",
        description=(
            "Networking Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.networking_bot",
        class_name="NetworkingBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/networking_bot.py",
    ),
    BotEntry(
        bot_id="occ_performance_review_bot",
        display_name="Performance Review Bot",
        description=(
            "Performance Review Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.performance_review_bot",
        class_name="PerformanceReviewBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/performance_review_bot.py",
    ),
    BotEntry(
        bot_id="occ_personal_care_bot",
        display_name="Personal Care Bot",
        description=(
            "Personal Care Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.personal_care_bot",
        class_name="PersonalCareBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/personal_care_bot.py",
    ),
    BotEntry(
        bot_id="occ_portfolio_builder_bot",
        display_name="Portfolio Builder Bot",
        description=(
            "Portfolio Builder Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.portfolio_builder_bot",
        class_name="PortfolioBuilderBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/portfolio_builder_bot.py",
    ),
    BotEntry(
        bot_id="occ_production_bot",
        display_name="Production Bot",
        description=(
            "Production Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.production_bot",
        class_name="ProductionBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/production_bot.py",
    ),
    BotEntry(
        bot_id="occ_promotion_readiness_bot",
        display_name="Promotion Readiness Bot",
        description=(
            "Promotion Readiness Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.promotion_readiness_bot",
        class_name="PromotionReadinessBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/promotion_readiness_bot.py",
    ),
    BotEntry(
        bot_id="occ_protective_service_bot",
        display_name="Protective Service Bot",
        description=(
            "Protective Service Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.protective_service_bot",
        class_name="ProtectiveServiceBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/protective_service_bot.py",
    ),
    BotEntry(
        bot_id="occ_reference_checker_bot",
        display_name="Reference Checker Bot",
        description=(
            "Reference Checker Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.reference_checker_bot",
        class_name="ReferenceCheckerBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/reference_checker_bot.py",
    ),
    BotEntry(
        bot_id="occ_relocation_advisor_bot",
        display_name="Relocation Advisor Bot",
        description=(
            "Relocation Advisor Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.relocation_advisor_bot",
        class_name="RelocationAdvisorBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/relocation_advisor_bot.py",
    ),
    BotEntry(
        bot_id="occ_remote_job_finder_bot",
        display_name="Remote Job Finder Bot",
        description=(
            "Remote Job Finder Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.remote_job_finder_bot",
        class_name="RemoteJobFinderBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/remote_job_finder_bot.py",
    ),
    BotEntry(
        bot_id="occ_salary_negotiator_bot",
        display_name="Salary Negotiator Bot",
        description=(
            "Salary Negotiator Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.salary_negotiator_bot",
        class_name="SalaryNegotiatorBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/salary_negotiator_bot.py",
    ),
    BotEntry(
        bot_id="occ_sales_bot",
        display_name="Sales Bot",
        description=(
            "Sales Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.sales_bot",
        class_name="SalesBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/sales_bot.py",
    ),
    BotEntry(
        bot_id="occ_science_bot",
        display_name="Science Bot",
        description=(
            "Science Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.science_bot",
        class_name="ScienceBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/science_bot.py",
    ),
    BotEntry(
        bot_id="occ_side_hustle_finder_bot",
        display_name="Side Hustle Finder Bot",
        description=(
            "Side Hustle Finder Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.side_hustle_finder_bot",
        class_name="SideHustleFinderBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/side_hustle_finder_bot.py",
    ),
    BotEntry(
        bot_id="occ_skills_gap_bot",
        display_name="Skills Gap Bot",
        description=(
            "Skills Gap Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.skills_gap_bot",
        class_name="SkillsGapBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/skills_gap_bot.py",
    ),
    BotEntry(
        bot_id="occ_transportation_bot",
        display_name="Transportation Bot",
        description=(
            "Transportation Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.transportation_bot",
        class_name="TransportationBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/transportation_bot.py",
    ),
    BotEntry(
        bot_id="occ_upskill_recommender_bot",
        display_name="Upskill Recommender Bot",
        description=(
            "Upskill Recommender Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.upskill_recommender_bot",
        class_name="UpskillRecommenderBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/upskill_recommender_bot.py",
    ),
    BotEntry(
        bot_id="occ_work_life_balance_bot",
        display_name="Work Life Balance Bot",
        description=(
            "Work Life Balance Bot — occupational intelligence bot."
        ),
        category=BotCategory.OCCUPATIONAL,
        module_path="Occupational_bots.work_life_balance_bot",
        class_name="WorkLifeBalanceBot",
        version="1.0.0",
        capabilities=[],
        namespace="occ",
        source_path="Occupational_bots/work_life_balance_bot.py",
    ),
    BotEntry(
        bot_id="re_auction_finder_bot",
        display_name="Auction Finder Bot",
        description=(
            "Auction Finder Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.auction_finder_bot",
        class_name="AuctionFinderBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/auction_finder_bot.py",
    ),
    BotEntry(
        bot_id="re_cash_flow_bot",
        display_name="Cash Flow Bot",
        description=(
            "Cash Flow Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.cash_flow_bot",
        class_name="CashFlowBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/cash_flow_bot.py",
    ),
    BotEntry(
        bot_id="re_commercial_analyzer_bot",
        display_name="Commercial Analyzer Bot",
        description=(
            "Commercial Analyzer Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.commercial_analyzer_bot",
        class_name="CommercialAnalyzerBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/commercial_analyzer_bot.py",
    ),
    BotEntry(
        bot_id="re_comparable_sales_bot",
        display_name="Comparable Sales Bot",
        description=(
            "Comparable Sales Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.comparable_sales_bot",
        class_name="ComparableSalesBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/comparable_sales_bot.py",
    ),
    BotEntry(
        bot_id="re_deal_analyzer_bot",
        display_name="Deal Analyzer Bot",
        description=(
            "Deal Analyzer Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.deal_analyzer_bot",
        class_name="DealAnalyzerBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/deal_analyzer_bot.py",
    ),
    BotEntry(
        bot_id="re_fix_and_flip_bot",
        display_name="Fix And Flip Bot",
        description=(
            "Fix And Flip Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.fix_and_flip_bot",
        class_name="FixAndFlipBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/fix_and_flip_bot.py",
    ),
    BotEntry(
        bot_id="re_flip_profit_calculator_bot",
        display_name="Flip Profit Calculator Bot",
        description=(
            "Flip Profit Calculator Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.flip_profit_calculator_bot",
        class_name="FlipProfitCalculatorBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/flip_profit_calculator_bot.py",
    ),
    BotEntry(
        bot_id="re_foreclosure_finder_bot",
        display_name="Foreclosure Finder Bot",
        description=(
            "Foreclosure Finder Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.foreclosure_finder_bot",
        class_name="ForeclosureFinderBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/foreclosure_finder_bot.py",
    ),
    BotEntry(
        bot_id="re_insurance_estimator_bot",
        display_name="Insurance Estimator Bot",
        description=(
            "Insurance Estimator Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.insurance_estimator_bot",
        class_name="InsuranceEstimatorBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/insurance_estimator_bot.py",
    ),
    BotEntry(
        bot_id="re_investor_matchmaker_bot",
        display_name="Investor Matchmaker Bot",
        description=(
            "Investor Matchmaker Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.investor_matchmaker_bot",
        class_name="InvestorMatchmakerBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/investor_matchmaker_bot.py",
    ),
    BotEntry(
        bot_id="re_land_analyzer_bot",
        display_name="Land Analyzer Bot",
        description=(
            "Land Analyzer Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.land_analyzer_bot",
        class_name="LandAnalyzerBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/land_analyzer_bot.py",
    ),
    BotEntry(
        bot_id="re_lease_generator_bot",
        display_name="Lease Generator Bot",
        description=(
            "Lease Generator Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.lease_generator_bot",
        class_name="LeaseGeneratorBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/lease_generator_bot.py",
    ),
    BotEntry(
        bot_id="re_mortgage_calculator_bot",
        display_name="Mortgage Calculator Bot",
        description=(
            "Mortgage Calculator Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.mortgage_calculator_bot",
        class_name="MortgageCalculatorBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/mortgage_calculator_bot.py",
    ),
    BotEntry(
        bot_id="re_multifamily_analyzer_bot",
        display_name="Multifamily Analyzer Bot",
        description=(
            "Multifamily Analyzer Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.multifamily_analyzer_bot",
        class_name="MultifamilyAnalyzerBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/multifamily_analyzer_bot.py",
    ),
    BotEntry(
        bot_id="re_neighborhood_scorer_bot",
        display_name="Neighborhood Scorer Bot",
        description=(
            "Neighborhood Scorer Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.neighborhood_scorer_bot",
        class_name="NeighborhoodScorerBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/neighborhood_scorer_bot.py",
    ),
    BotEntry(
        bot_id="re_off_market_finder_bot",
        display_name="Off Market Finder Bot",
        description=(
            "Off Market Finder Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.off_market_finder_bot",
        class_name="OffMarketFinderBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/off_market_finder_bot.py",
    ),
    BotEntry(
        bot_id="re_property_alert_bot",
        display_name="Property Alert Bot",
        description=(
            "Property Alert Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.property_alert_bot",
        class_name="PropertyAlertBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/property_alert_bot.py",
    ),
    BotEntry(
        bot_id="re_property_management_bot",
        display_name="Property Management Bot",
        description=(
            "Property Management Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.property_management_bot",
        class_name="PropertyManagementBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/property_management_bot.py",
    ),
    BotEntry(
        bot_id="re_property_valuation_bot",
        display_name="Property Valuation Bot",
        description=(
            "Property Valuation Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.property_valuation_bot",
        class_name="PropertyValuationBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/property_valuation_bot.py",
    ),
    BotEntry(
        bot_id="re_renovation_cost_bot",
        display_name="Renovation Cost Bot",
        description=(
            "Renovation Cost Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.renovation_cost_bot",
        class_name="RenovationCostBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/renovation_cost_bot.py",
    ),
    BotEntry(
        bot_id="re_rental_income_bot",
        display_name="Rental Income Bot",
        description=(
            "Rental Income Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.rental_income_bot",
        class_name="RentalIncomeBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/rental_income_bot.py",
    ),
    BotEntry(
        bot_id="re_roi_tracker_bot",
        display_name="Roi Tracker Bot",
        description=(
            "Roi Tracker Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.roi_tracker_bot",
        class_name="ROITrackerBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/roi_tracker_bot.py",
    ),
    BotEntry(
        bot_id="re_short_sale_finder_bot",
        display_name="Short Sale Finder Bot",
        description=(
            "Short Sale Finder Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.short_sale_finder_bot",
        class_name="ShortSaleFinderBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/short_sale_finder_bot.py",
    ),
    BotEntry(
        bot_id="re_tax_lien_bot",
        display_name="Tax Lien Bot",
        description=(
            "Tax Lien Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.tax_lien_bot",
        class_name="TaxLienBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/tax_lien_bot.py",
    ),
    BotEntry(
        bot_id="re_tenant_screening_bot",
        display_name="Tenant Screening Bot",
        description=(
            "Tenant Screening Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.tenant_screening_bot",
        class_name="TenantScreeningBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/tenant_screening_bot.py",
    ),
    BotEntry(
        bot_id="re_wholesaler_bot",
        display_name="Wholesaler Bot",
        description=(
            "Wholesaler Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.wholesaler_bot",
        class_name="WholesalerBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/wholesaler_bot.py",
    ),
    BotEntry(
        bot_id="re_zoning_research_bot",
        display_name="Zoning Research Bot",
        description=(
            "Zoning Research Bot — real estate analysis bot."
        ),
        category=BotCategory.REAL_ESTATE,
        module_path="Real_Estate_bots.zoning_research_bot",
        class_name="ZoningResearchBot",
        version="1.0.0",
        capabilities=[],
        namespace="re",
        source_path="Real_Estate_bots/zoning_research_bot.py",
    ),
# <<< END GENERATED CATALOGUE >>>
]
