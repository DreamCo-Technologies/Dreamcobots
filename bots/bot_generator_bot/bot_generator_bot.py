"""
Bot Generator Bot — Main Entry Point

The DreamCo Bot Generator Bot is the core multiplier of the Dreamcobots
ecosystem.  Given a natural-language description of a desired bot (e.g.
"Make a Dentist Lead Bot"), it:

  1. Parses the request into a structured BotIntent (parser.py)
  2. Injects appropriate scraping/processing tools (tool_injector.py)
  3. Dynamically builds the bot source code (template_engine.py)
  4. Deploys the generated bot to the filesystem (deployer.py)

Tier-aware monetization controls how many bots a user can generate per month.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from bots.bot_generator_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_BASIC_GENERATION,
    FEATURE_TOOL_INJECTION,
    FEATURE_ADVANCED_TEMPLATES,
    FEATURE_AUTO_DEPLOY,
    FEATURE_CUSTOM_DNA,
    FEATURE_WHITE_LABEL,
)
from bots.bot_generator_bot.parser import BotParser, BotIntent
from bots.bot_generator_bot.tool_injector import ToolInjector
from bots.bot_generator_bot.template_engine import TemplateEngine
from bots.bot_generator_bot.deployer import BotDeployer


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class BotGeneratorError(Exception):
    """Base exception for Bot Generator errors."""


class BotGeneratorTierError(BotGeneratorError):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class BotGeneratorBot:
    """
    DreamCo Bot Generator Bot — empire-grade autonomous bot factory.

    Creates new, fully-functional bots on demand by parsing user intent,
    injecting tools, building templates, and deploying to disk.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling how many bots can be generated and
        which features (advanced templates, auto-deploy, white-label) are
        available.
    bots_root : str, optional
        Filesystem path where generated bots will be deployed.  Defaults to
        the repository ``bots/`` directory.
    """

    def __init__(self, tier: Tier = Tier.FREE, bots_root: str | None = None) -> None:
        self.tier = tier
        self._config: TierConfig = get_tier_config(tier)
        self._parser = BotParser()
        self._injector = ToolInjector()
        self._engine = TemplateEngine()
        self._deployer = BotDeployer(bots_root=bots_root)
        self._bots_generated: int = 0
        self._generation_log: list = []

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
            raise BotGeneratorTierError(
                f"Feature '{feature}' is not available on the {self._config.name} tier.{hint}"
            )

    def _check_monthly_limit(self) -> None:
        limit = self._config.max_bots_per_month
        if limit is not None and self._bots_generated >= limit:
            upgrade = get_upgrade_path(self.tier)
            hint = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo) for more bots."
                if upgrade
                else ""
            )
            raise BotGeneratorTierError(
                f"Monthly bot generation limit ({limit}) reached for the "
                f"{self._config.name} tier.{hint}"
            )

    # ------------------------------------------------------------------
    # Core generation pipeline
    # ------------------------------------------------------------------

    def generate(
        self,
        user_input: str,
        deploy: bool = False,
        dry_run: bool = False,
        custom_dna: dict | None = None,
    ) -> dict:
        """
        Run the full bot generation pipeline.

        Parameters
        ----------
        user_input : str
            Natural-language description, e.g. "Make a Dentist Lead Bot".
        deploy : bool
            When ``True``, write generated files to disk (PRO+ required).
        dry_run : bool
            Perform a deploy dry-run (plan without writing files).
        custom_dna : dict, optional
            Override the parsed DNA entirely (ENTERPRISE only).

        Returns
        -------
        dict
            Full generation result including source code, DNA, and optional
            deploy result.
        """
        self._require(FEATURE_BASIC_GENERATION)
        self._check_monthly_limit()

        # Step 1: Parse intent
        intent: BotIntent = self._parser.parse(user_input)

        # Step 2: Build DNA (custom override for ENTERPRISE)
        if custom_dna is not None:
            self._require(FEATURE_CUSTOM_DNA)
            dna = custom_dna
        else:
            dna = intent.to_dna()

        # Step 3: Inject tools (PRO+)
        if self._config.has_feature(FEATURE_TOOL_INJECTION):
            dna = self._injector.inject(dna)
        else:
            dna["resolved_tools"] = []
            dna["missing_tools"] = dna.get("tools", [])

        # Step 4: Build template
        build_result = self._engine.build(dna)

        # Step 5: Deploy (PRO+)
        deploy_result = None
        if deploy or dry_run:
            self._require(FEATURE_AUTO_DEPLOY)
            deploy_result = self._deployer.deploy(build_result, dry_run=dry_run)

        self._bots_generated += 1

        log_entry = {
            "user_input": user_input,
            "intent": {
                "industry": intent.industry,
                "goal": intent.goal,
                "confidence": intent.confidence,
            },
            "dna": dna,
            "build_result": {
                "bot_name": build_result["bot_name"],
                "class_name": build_result["class_name"],
                "filename": build_result["filename"],
                "generated_at": build_result["generated_at"],
            },
            "deploy_result": deploy_result,
            "tier": self.tier.value,
        }
        self._generation_log.append(log_entry)

        return {
            **log_entry,
            "source": build_result["source"],
        }

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def list_available_tools(self) -> list:
        """Return all tools available for injection."""
        return self._injector.list_available_tools()

    def get_generation_log(self) -> list:
        """Return the full generation history for this session."""
        return list(self._generation_log)

    def get_summary(self) -> dict:
        """Return a performance summary for this session."""
        return {
            "tier": self.tier.value,
            "bots_generated_this_session": self._bots_generated,
            "monthly_limit": self._config.max_bots_per_month,
            "remaining_this_month": (
                self._config.max_bots_per_month - self._bots_generated
                if self._config.max_bots_per_month is not None
                else "unlimited"
            ),
            "deployed_bots": self._deployer.list_deployed_bots(),
            "features": self._config.features,
        }

    # ------------------------------------------------------------------
    # BuddyAI chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """Natural-language interface for BuddyAI routing."""
        msg = message.lower()
        if any(kw in msg for kw in ("make", "build", "create", "generate")):
            result = self.generate(message)
            return {
                "message": (
                    f"Bot generated: {result['build_result']['bot_name']}. "
                    f"Industry: {result['intent']['industry']}, "
                    f"Goal: {result['intent']['goal']}."
                ),
                "data": result,
            }
        if "tools" in msg or "available" in msg:
            tools = self.list_available_tools()
            return {"message": f"{len(tools)} tools available.", "data": tools}
        if "summary" in msg or "stats" in msg:
            return {"message": "Bot Generator summary.", "data": self.get_summary()}
        return {
            "message": (
                "DreamCo Bot Generator online. "
                f"Tier: {self.tier.value}. "
                "Say 'Make a [industry] Bot' to generate a new bot."
            )
        }

    def process(self, payload: dict) -> dict:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        return self.chat(payload.get("command", ""))


def _botgenerator_test_bot(self, bot_name: str) -> str:
    """Test a bot by name. Returns a result string."""
    try:
        import importlib
        module_path = f"bots.{bot_name}.{bot_name}"
        try:
            mod = importlib.import_module(module_path)
        except ModuleNotFoundError:
            try:
                mod = importlib.import_module(f"bots.{bot_name}")
            except ModuleNotFoundError:
                return f"Failed: Module '{bot_name}' not found."
        import inspect
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if hasattr(obj, "run"):
                try:
                    import unittest.mock as _mock
                    with _mock.patch("os.system", return_value=0):
                        instance = obj()
                        result = instance.run()
                    return str(result) if result else f"Bot {name} tested successfully."
                except Exception as e:
                    return f"Failed: {type(e).__name__}: {e}"
        return f"Tested {bot_name}: no runnable bot class found."
    except Exception as e:
        return f"Failed: {type(e).__name__}: {e}"


def _botgenerator_create_bot(self, description: str) -> dict:
    """Create a bot from a description. Delegates to generate()."""
    return self.generate(description)


BotGeneratorBot.test_bot = _botgenerator_test_bot
BotGeneratorBot.create_bot = _botgenerator_create_bot
