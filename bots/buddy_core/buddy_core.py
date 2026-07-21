"""
Buddy Core System — Main Entry Point.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Buddy Core is the central intelligence layer of the DreamCobots ecosystem:

  • Intent Parser    — natural language → structured intent
  • Tool Injection   — auto-select best-fit APIs & libraries
  • Bot Generator    — Bot-on-Demand with DNA blueprinting
  • Feedback Loop    — performance tracking, revenue, auto-optimisation
  • Privacy Engine   — permission vaults, activity logs, safety guardrails
  • Lead Engine      — scrape → score → monetise lead campaigns

Usage
-----
    from bots.buddy_core import BuddyCore, Tier

    buddy = BuddyCore(tier=Tier.PRO, operator_name="MyApp")

    # Create a bot
    result = buddy.create_bot("PropertyScout", purpose="Find real-estate leads")

    # Run a lead campaign
    result = buddy.run_lead_campaign(industry="real_estate", count=50)

    # Chat interface
    reply = buddy.chat("Create a marketing bot called CampaignMaster")
    print(reply["message"])
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401

from bots.buddy_core.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_INTENT_PARSER,
    FEATURE_TOOL_INJECTION,
    FEATURE_BOT_GENERATOR,
    FEATURE_FEEDBACK_LOOP,
    FEATURE_PRIVACY_VAULT,
    FEATURE_LEAD_ENGINE,
    FEATURE_ADVANCED_AI,
    FEATURE_WHITE_LABEL,
    FEATURE_CUSTOM_ENCRYPTION,
    FEATURE_ENTERPRISE_LOGS,
    FEATURE_TOOL_SCRAPER,
    FEATURE_TOOL_REPLICATION,
)
from bots.buddy_core.intent_parser import IntentParser, IntentType, Industry, ParsedIntent
from bots.buddy_core.tool_db import ToolDB, Tool
from bots.buddy_core.bot_generator import BotGenerator, GeneratedBot, BotStatus
from bots.buddy_core.feedback_loop import FeedbackLoop, MetricType
from bots.buddy_core.privacy_engine import (
    PrivacyEngine,
    PermissionLevel,
    ActionCategory,
)
from bots.buddy_core.lead_engine import LeadEngine, LeadSource
from bots.buddy_core.tool_scraper import ToolScraper, ToolProfile
from bots.buddy_core.tool_replication import ToolReplicationEngine, ReplicatedTool


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class BuddyCoreError(Exception):
    """General Buddy Core error."""


class BuddyCoreTierError(BuddyCoreError):
    """Raised when the current tier does not have access to a feature."""


# ---------------------------------------------------------------------------
# BuddyCore
# ---------------------------------------------------------------------------

class BuddyCore:
    """
    Central intelligence layer wiring all Buddy Core modules together.

    Adheres to the GLOBAL AI SOURCES FLOW framework.
    """

    def __init__(self, tier: Tier, operator_name: str = "Buddy") -> None:
        self._tier = tier
        self._tier_config: TierConfig = get_tier_config(tier)
        self._operator_name = operator_name

        # Modules
        self._intent_parser = IntentParser()
        self._tool_db = ToolDB()
        self._bot_generator = BotGenerator()
        self._feedback_loop = FeedbackLoop()
        self._privacy_engine = PrivacyEngine()
        self._lead_engine = LeadEngine()
        self._tool_scraper = ToolScraper()
        self._replication_engine = ToolReplicationEngine()

    # ------------------------------------------------------------------
    # Tier / Feature guards
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        """Raise BuddyCoreTierError if *feature* is not available on this tier."""
        if not self._tier_config.has_feature(feature):
            upgrade = get_upgrade_path(self._tier)
            hint = (
                f"Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo) to unlock."
                if upgrade
                else "Already at the highest tier."
            )
            raise BuddyCoreTierError(
                f"Feature '{feature}' is not available on the {self._tier_config.name} tier. "
                + hint
            )

    def can_access(self, feature: str) -> bool:
        """Return True if the current tier includes *feature*."""
        return self._tier_config.has_feature(feature)

    def get_tier_info(self) -> dict:
        """Return a summary of the current tier configuration."""
        cfg = self._tier_config
        upgrade = get_upgrade_path(self._tier)
        return {
            "tier": cfg.tier.value,
            "name": cfg.name,
            "price_usd_monthly": cfg.price_usd_monthly,
            "max_bots_per_day": cfg.max_bots_per_day,
            "max_leads_per_day": cfg.max_leads_per_day,
            "features": cfg.features,
            "support_level": cfg.support_level,
            "upgrade_available": upgrade is not None,
            "upgrade_to": upgrade.name if upgrade else None,
            "upgrade_price": upgrade.price_usd_monthly if upgrade else None,
        }

    # ------------------------------------------------------------------
    # Bot-on-Demand
    # ------------------------------------------------------------------

    def create_bot(
        self,
        name: str,
        purpose: str = "",
        industry: str = "",
    ) -> dict:
        """Create a new bot using the BotGenerator."""
        self._require(FEATURE_BOT_GENERATOR)
        bot = self._bot_generator.create_bot(name=name, purpose=purpose, industry=industry)
        return {
            "status": "created",
            "bot_id": bot.bot_id,
            "name": bot.name,
            "industry": bot.dna.industry,
            "tools": bot.tools,
            "bot_status": bot.status.value,
        }

    # ------------------------------------------------------------------
    # Tool Injection
    # ------------------------------------------------------------------

    def inject_tools(self, bot_name: str, industry: str) -> dict:
        """Auto-inject the best tools for a bot."""
        self._require(FEATURE_TOOL_INJECTION)
        tools = self._tool_db.inject_tools(bot_name, industry)
        return {
            "bot_name": bot_name,
            "industry": industry,
            "tools_injected": len(tools),
            "tools": [
                {
                    "tool_id": t.tool_id,
                    "name": t.name,
                    "category": t.category.value,
                    "is_free": t.is_free,
                }
                for t in tools
            ],
        }

    # ------------------------------------------------------------------
    # Lead Engine
    # ------------------------------------------------------------------

    def run_lead_campaign(
        self,
        industry: str,
        count: int = 20,
        source: str = "linkedin",
    ) -> dict:
        """Run a lead scraping and scoring campaign."""
        self._require(FEATURE_LEAD_ENGINE)
        try:
            lead_source = LeadSource(source.lower())
        except ValueError:
            lead_source = LeadSource.LINKEDIN
        return self._lead_engine.run_campaign(industry=industry, source=lead_source, count=count)

    # ------------------------------------------------------------------
    # Feedback Loop
    # ------------------------------------------------------------------

    def run_feedback_cycle(self, bot_id: str) -> dict:
        """Run a full feedback and optimisation cycle for *bot_id*."""
        self._require(FEATURE_FEEDBACK_LOOP)
        return self._feedback_loop.run_cycle(bot_id)

    # ------------------------------------------------------------------
    # Privacy & Permissions
    # ------------------------------------------------------------------

    def set_permissions(self, user_id: str, level: str) -> dict:
        """Set permission level for a user."""
        self._require(FEATURE_PRIVACY_VAULT)
        try:
            perm_level = PermissionLevel(level.lower())
        except ValueError:
            raise BuddyCoreError(f"Unknown permission level: '{level}'")
        perm = self._privacy_engine.permissions.set_permission(user_id, perm_level)
        return {
            "user_id": user_id,
            "level": perm.level.value,
            "allowed_categories": [c.value for c in perm.allowed_categories],
        }

    def log_activity(
        self, user_id: str, action: str, category: str, status: str = "success"
    ) -> dict:
        """Log a user activity."""
        try:
            cat = ActionCategory(category.lower())
        except ValueError:
            raise BuddyCoreError(f"Unknown action category: '{category}'")
        entry = self._privacy_engine.logger.log(user_id, action, cat, status=status)
        return {
            "log_id": entry.log_id,
            "user_id": entry.user_id,
            "action": entry.action,
            "category": entry.category.value,
            "status": entry.status,
        }

    def check_action_safety(
        self, action: str, category: str, user_id: str
    ) -> dict:
        """Check whether an action passes safety guardrails."""
        try:
            cat = ActionCategory(category.lower())
        except ValueError:
            raise BuddyCoreError(f"Unknown action category: '{category}'")
        return self._privacy_engine.guardrail.check_action(action, cat, user_id)

    def store_secure(self, key: str, value: str, user_id: str) -> dict:
        """Store a sensitive value in the encrypted vault."""
        self._require(FEATURE_PRIVACY_VAULT)
        token = self._privacy_engine.vault.store(key, value, user_id)
        return {"status": "stored", "token": token, "user_id": user_id}

    # ------------------------------------------------------------------
    # Tool Scraper & Replication
    # ------------------------------------------------------------------

    def scrape_tool(
        self,
        tool_name: str,
        description: str,
        base_url: str | None = None,
        extra_keywords: list[str] | None = None,
        is_open_source: bool = False,
        has_free_tier: bool = True,
    ) -> dict:
        """
        Analyze an external tool and return its capability profile.

        Requires the ``tool_scraper`` feature (PRO tier and above).

        Parameters
        ----------
        tool_name : str
            Human-readable name of the tool (e.g. ``"Zapier"``).
        description : str
            One or two sentence description of what the tool does.
        base_url : str, optional
            Base API endpoint URL.
        extra_keywords : list[str], optional
            Additional keywords for capability detection.
        is_open_source : bool
        has_free_tier : bool

        Returns
        -------
        dict
            Serialised :class:`~bots.buddy_core.tool_scraper.ToolProfile`.
        """
        self._require(FEATURE_TOOL_SCRAPER)
        profile = self._tool_scraper.analyze(
            tool_name=tool_name,
            description=description,
            base_url=base_url,
            extra_keywords=extra_keywords,
            is_open_source=is_open_source,
            has_free_tier=has_free_tier,
        )
        return profile.to_dict()

    def scrape_known_tool(self, platform_name: str) -> dict:
        """
        Analyze a pre-catalogued platform by name.

        Requires the ``tool_scraper`` feature (PRO tier and above).

        Parameters
        ----------
        platform_name : str
            Case-insensitive name of the known platform (e.g. ``"zapier"``).

        Returns
        -------
        dict
            Serialised :class:`~bots.buddy_core.tool_scraper.ToolProfile`,
            or ``{"error": ...}`` if the platform is not in the catalogue.
        """
        self._require(FEATURE_TOOL_SCRAPER)
        profile = self._tool_scraper.analyze_known_platform(platform_name)
        if profile is None:
            known = self._tool_scraper.list_known_platforms()
            return {
                "error": f"Unknown platform '{platform_name}'.",
                "known_platforms": known,
            }
        return profile.to_dict()

    def replicate_tool(
        self,
        tool_name: str,
        description: str,
        base_url: str | None = None,
        extra_keywords: list[str] | None = None,
        is_open_source: bool = False,
        has_free_tier: bool = True,
    ) -> dict:
        """
        Analyze an external tool and generate a Buddy-native equivalent.

        Requires the ``tool_replication`` feature (ENTERPRISE tier).

        Returns
        -------
        dict
            Serialised :class:`~bots.buddy_core.tool_replication.ReplicatedTool`
            including ``source_code``.
        """
        self._require(FEATURE_TOOL_REPLICATION)
        profile = self._tool_scraper.analyze(
            tool_name=tool_name,
            description=description,
            base_url=base_url,
            extra_keywords=extra_keywords,
            is_open_source=is_open_source,
            has_free_tier=has_free_tier,
        )
        replica = self._replication_engine.replicate(profile)
        result = replica.to_dict()
        result["source_code"] = replica.source_code
        return result

    def replicate_known_tool(self, platform_name: str) -> dict:
        """
        Replicate a pre-catalogued platform by name.

        Requires the ``tool_replication`` feature (ENTERPRISE tier).

        Parameters
        ----------
        platform_name : str
            Case-insensitive name of the known platform (e.g. ``"zapier"``).

        Returns
        -------
        dict
            Serialised :class:`~bots.buddy_core.tool_replication.ReplicatedTool`
            including ``source_code``, or ``{"error": ...}`` if unknown.
        """
        self._require(FEATURE_TOOL_REPLICATION)
        profile = self._tool_scraper.analyze_known_platform(platform_name)
        if profile is None:
            known = self._tool_scraper.list_known_platforms()
            return {
                "error": f"Unknown platform '{platform_name}'.",
                "known_platforms": known,
            }
        replica = self._replication_engine.replicate(profile)
        result = replica.to_dict()
        result["source_code"] = replica.source_code
        return result

    def list_replicable_platforms(self) -> list[str]:
        """Return the list of pre-catalogued platforms available for replication."""
        return self._tool_scraper.list_known_platforms()

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def dashboard(self) -> dict:
        """Return a full system overview."""
        return {
            "operator": self._operator_name,
            "tier": self.get_tier_info(),
            "bots": self._bot_generator.get_stats(),
            "leads": self._lead_engine.get_stats(),
            "feedback": self._feedback_loop.get_summary(),
            "privacy": {
                "activity_logs": self._privacy_engine.logger.get_stats(),
                "pending_actions": len(
                    self._privacy_engine.guardrail.get_pending_actions()
                ),
            },
        }

    # ------------------------------------------------------------------
    # Natural language chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """
        Accept a natural-language message and dispatch to the appropriate
        module.  Returns a structured response dict.
        """
        parsed: ParsedIntent = self._intent_parser.parse(message)
        intent = parsed.intent_type
        industry = parsed.industry.value

        if intent == IntentType.CREATE_BOT:
            name = parsed.bot_name or "MyBot"
            if self.can_access(FEATURE_BOT_GENERATOR):
                result = self.create_bot(name=name, industry=industry)
                return {
                    "intent": intent.value,
                    "message": f"Bot '{name}' created for {industry} industry.",
                    "data": result,
                }
            return {
                "intent": intent.value,
                "message": "Upgrade required to create bots.",
                "data": {},
            }

        if intent == IntentType.FIND_LEADS:
            if self.can_access(FEATURE_LEAD_ENGINE):
                result = self.run_lead_campaign(industry=industry)
                return {
                    "intent": intent.value,
                    "message": f"Lead campaign for {industry} complete. {result['total_leads']} leads found.",
                    "data": result,
                }
            return {
                "intent": intent.value,
                "message": "Upgrade required to run lead campaigns.",
                "data": {},
            }

        if intent == IntentType.ANALYZE_DATA:
            return {
                "intent": intent.value,
                "message": "Here is your dashboard overview.",
                "data": self.dashboard(),
            }

        if intent == IntentType.GET_STATUS:
            return {
                "intent": intent.value,
                "message": f"System is running. Tier: {self._tier_config.name}.",
                "data": self.get_tier_info(),
            }

        if intent == IntentType.MANAGE_TOOLS:
            tools = self._tool_db.get_tools_for_industry(industry)
            return {
                "intent": intent.value,
                "message": f"Found {len(tools)} tools for {industry}.",
                "data": {"tools": [t.name for t in tools]},
            }

        # UNKNOWN / RUN_WORKFLOW / fallback
        return {
            "intent": intent.value,
            "message": (
                f"Hi! I'm {self._operator_name}. I can create bots, find leads, "
                "inject tools, run feedback cycles, and manage privacy. "
                "How can I help?"
            ),
            "data": {"confidence": parsed.confidence},
        }

    # ------------------------------------------------------------------
    # GLOBAL AI SOURCES FLOW framework entry point
    # ------------------------------------------------------------------

    def process(self, payload: dict) -> dict:
        """
        GLOBAL AI SOURCES FLOW framework entry point.

        Accepts a payload dict with at least a 'command' key and optional
        parameters, routes to the appropriate method, and returns a
        structured result.

        Recognised commands:
          - chat: natural-language dispatch (requires 'message')
          - create_bot: create a bot (requires 'name'; optional 'purpose', 'industry')
          - run_lead_campaign: lead campaign (requires 'industry'; optional 'count')
          - run_feedback_cycle: feedback cycle (requires 'bot_id')
          - inject_tools: inject tools (requires 'bot_name', 'industry')
          - dashboard: full system overview
          - get_tier_info: tier details
        """
        command = payload.get("command", "chat")

        if command == "chat":
            return self.chat(payload.get("message", ""))

        if command == "create_bot":
            return self.create_bot(
                name=payload.get("name", "MyBot"),
                purpose=payload.get("purpose", ""),
                industry=payload.get("industry", ""),
            )

        if command == "run_lead_campaign":
            return self.run_lead_campaign(
                industry=payload.get("industry", "general"),
                count=payload.get("count", 20),
                source=payload.get("source", "linkedin"),
            )

        if command == "run_feedback_cycle":
            return self.run_feedback_cycle(payload.get("bot_id", ""))

        if command == "inject_tools":
            return self.inject_tools(
                bot_name=payload.get("bot_name", ""),
                industry=payload.get("industry", "general"),
            )

        if command == "dashboard":
            return self.dashboard()

        if command == "get_tier_info":
            return self.get_tier_info()

        raise BuddyCoreError(f"Unknown command: '{command}'")
