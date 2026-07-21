"""
DreamCo AI Level-Up Bot — Main Entry Point.

Composes all AI Level-Up sub-systems into a single platform:

  • AI Companies Database  — 100+ companies with tools, pricing, region, API info
  • AI Course Engine       — 10-level AI University (DreamCo Professional Certificate)
  • Token Marketplace      — usage-based billing with 25% DreamCo markup
  • AI Skill Tree          — gamified learning progression with badges and rewards
  • AI Agents Generator    — custom bot builder for automation workflows

Architecture:
    DreamCoBots
    │
    ├── buddybot
    │
    ├── ai_level_up_bot
    │     ├── ai_companies_database
    │     ├── ai_course_engine
    │     ├── token_marketplace
    │     ├── ai_skill_tree
    │     └── ai_agents_generator
    │
    ├── trade_titan_bot
    └── hustle_bots

Usage
-----
    from bots.ai_level_up_bot import AILevelUpBot, Tier

    bot = AILevelUpBot(tier=Tier.PRO)
    company = bot.teach_ai_tool("ChatGPT")
    print(company)
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.ai_level_up_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_AI_COMPANIES_DATABASE,
    FEATURE_AI_COURSE_ENGINE,
    FEATURE_TOKEN_MARKETPLACE,
    FEATURE_AI_SKILL_TREE,
    FEATURE_AI_AGENTS_GENERATOR,
    FEATURE_FULL_DATABASE,
)
from bots.ai_level_up_bot.ai_companies_database import AICompanyDatabase, AICompany
from bots.ai_level_up_bot.ai_course_engine import AICourseEngine
from bots.ai_level_up_bot.token_marketplace import TokenMarketplace
from bots.ai_level_up_bot.ai_skill_tree import AISkillTree
from bots.ai_level_up_bot.ai_agents_generator import AIAgentsGenerator

from framework import GlobalAISourcesFlow  # noqa: F401


class AILevelUpBotError(Exception):
    """Base exception for AI Level-Up Bot errors."""


class AILevelUpTierError(AILevelUpBotError):
    """Raised when accessing a feature unavailable on the current tier."""


class AILevelUpBot:
    """DreamCo AI Level-Up Bot orchestrator.

    Combines the AI Companies Database, Course Engine, Token Marketplace,
    Skill Tree, and Agents Generator into a unified platform.

    Parameters
    ----------
    tier : Tier
        Subscription tier (STARTER / PRO / ENTERPRISE).
    user_id : str
        Identifier for the current user session.
    """

    def __init__(self, tier: Tier = Tier.STARTER, user_id: str = "user") -> None:
        self.bot_name = "AI Level-Up Bot"
        self.version = "1.0"
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self.user_id = user_id

        # Initialise sub-systems
        self.database = AICompanyDatabase()
        self.course_engine = AICourseEngine(
            max_level=self.config.max_course_levels,
        )
        self.token_marketplace = TokenMarketplace(
            max_daily_tokens=self.config.max_tokens_per_day,
        )
        self.skill_tree = AISkillTree(
            max_level=self.config.max_course_levels,
        )
        max_agents = None if tier == Tier.ENTERPRISE else (10 if tier == Tier.PRO else 3)
        self.agents_generator = AIAgentsGenerator(
            max_agents=max_agents,
            created_by=user_id,
        )

    # ------------------------------------------------------------------
    # Core public API (mirrors problem-statement class outline)
    # ------------------------------------------------------------------

    def run(self) -> str:
        """Return a status message confirming the bot is online."""
        return f"{self.bot_name} v{self.version} Online [{self.tier.value.upper()} tier]"

    def teach_ai_tool(self, tool_name: str) -> dict:
        """Return capabilities and pricing info for a named AI tool.

        Parameters
        ----------
        tool_name : str
            Name of the tool (e.g. "ChatGPT", "DALL-E").

        Returns
        -------
        dict
            Tool name, capabilities, pricing, and company context,
            or an error dict if not found.
        """
        self._require_feature(FEATURE_AI_COMPANIES_DATABASE)
        company = self.database.get_tool(tool_name)
        if company is None:
            return {"error": f"Tool '{tool_name}' not found in the database."}
        return {
            "tool": tool_name,
            "company": company.company_name,
            "category": company.category,
            "capabilities": company.tools,
            "pricing": company.pricing,
            "region": company.region,
            "api_available": company.api_available,
        }

    def search_companies(self, category: str) -> list:
        """Return companies in the given category.

        Respects tier-level database access limits.
        """
        self._require_feature(FEATURE_AI_COMPANIES_DATABASE)
        companies = self.database.get_by_category(category)
        if not self.config.has_feature(FEATURE_FULL_DATABASE):
            companies = companies[: self.config.max_companies_accessible or 25]
        return [c.to_dict() for c in companies]

    def get_course_level(self, level: int) -> dict:
        """Return course details for a given level."""
        self._require_feature(FEATURE_AI_COURSE_ENGINE)
        course = self.course_engine.get_level(level)
        if course is None:
            return {"error": f"Level {level} is not accessible on the {self.tier.value} tier."}
        return course.to_dict()

    def purchase_tokens(self, service_type: str, units: float) -> dict:
        """Purchase tokens for a service."""
        self._require_feature(FEATURE_TOKEN_MARKETPLACE)
        return self.token_marketplace.purchase_tokens(service_type, units)

    def advance_skill_tree(self, node_id: str) -> dict:
        """Complete a skill tree node and earn rewards."""
        self._require_feature(FEATURE_AI_SKILL_TREE)
        return self.skill_tree.complete_node(node_id)

    def create_agent(
        self,
        name: str,
        purpose: str,
        tools: list,
        automation_hooks: list = None,
        description: str = "",
    ) -> dict:
        """Create a custom AI agent specification."""
        self._require_feature(FEATURE_AI_AGENTS_GENERATOR)
        return self.agents_generator.create_agent(
            name=name,
            purpose=purpose,
            tools=tools,
            automation_hooks=automation_hooks,
            description=description,
        )

    def create_agent_from_template(self, template_key: str) -> dict:
        """Create an agent from a pre-built template."""
        self._require_feature(FEATURE_AI_AGENTS_GENERATOR)
        return self.agents_generator.create_from_template(template_key)

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def dashboard(self) -> dict:
        """Return a unified dashboard of bot status and key metrics."""
        progress = self.skill_tree.get_progress_summary()
        token_summary = self.token_marketplace.get_usage_summary()
        return {
            "bot": self.bot_name,
            "version": self.version,
            "tier": self.tier.value,
            "user_id": self.user_id,
            "database_size": self.database.count(),
            "accessible_course_levels": self.config.max_course_levels,
            "skill_progress": progress,
            "token_usage": token_summary,
            "agents_created": self.agents_generator.count_agents(),
        }

    def describe_tier(self) -> dict:
        """Return details about the current subscription tier."""
        cfg = self.config
        upgrade = get_upgrade_path(self.tier)
        return {
            "tier": cfg.tier.value,
            "name": cfg.name,
            "price_usd_monthly": cfg.price_usd_monthly,
            "max_tokens_per_day": cfg.max_tokens_per_day,
            "max_course_levels": cfg.max_course_levels,
            "features": cfg.features,
            "support_level": cfg.support_level,
            "upgrade_available": upgrade is not None,
            "upgrade_to": upgrade.name if upgrade else None,
            "upgrade_price": upgrade.price_usd_monthly if upgrade else None,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            raise AILevelUpTierError(
                f"Feature '{feature}' is not available on the {self.tier.value} tier. "
                f"Please upgrade your subscription."
            )
