"""
Lawsuit Finder Bot — tier-aware legal case research and lawsuit discovery assistant.

Usage
-----
    from bots.lawsuit_finder_bot.lawsuit_finder_bot import LawsuitFinderBot
    from bots.ai_chatbot.tiers import Tier

    bot = LawsuitFinderBot(tier=Tier.PRO)
    response = bot.chat("Find class action lawsuits against pharmaceutical companies")
    print(response["message"])
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.lawsuit_finder_bot.tiers import (
    LF_EXTRA_FEATURES,
    LF_TOOLS,
    get_lf_tier_info,
)


class LawsuitFinderTierError(Exception):
    """Raised when a legal tool is not available on the current tier."""


class LawsuitFinderRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class LawsuitFinderBot:
    """
    Tier-aware legal case research and lawsuit discovery assistant.

    Supported tools (by tier):
      FREE       -- public case search, statute lookup, jurisdiction info
      PRO        -- class action finder, settlement tracker, attorney matcher
      ENTERPRISE -- deep case analytics, litigation trend reports, API integrations

    Disclaimer
    ----------
    This bot provides informational assistance only and does not constitute
    legal advice.  Always consult a qualified attorney for legal matters.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling tool access.
    """

    DISCLAIMER = (
        "DISCLAIMER: This bot provides informational assistance only and does "
        "not constitute legal advice. Always consult a qualified attorney."
    )

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._history: list[dict] = []

    # ------------------------------------------------------------------
    # Core chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str, tool: str | None = None) -> dict:
        """
        Process a legal research query and return a structured response.

        Parameters
        ----------
        message : str
            User's natural-language legal question.
        tool : str | None
            Optional tool to invoke directly.

        Returns
        -------
        dict with keys: ``message``, ``tool``, ``tier``, ``disclaimer``,
        ``requests_used``, ``requests_remaining``.
        """
        self._check_request_limit()
        active_tool = tool or self._default_tool(message)
        self._check_tool_access(active_tool)

        self._request_count += 1
        response_text = (
            f"[LawsuitFinderBot/{active_tool}] Processed: {message!r}"
        )
        self._history.append({"role": "user", "content": message})
        self._history.append({"role": "assistant", "content": response_text})

        return {
            "message": response_text,
            "tool": active_tool,
            "tier": self.tier.value,
            "disclaimer": self.DISCLAIMER,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def search_cases(self, query: str, jurisdiction: str | None = None) -> dict:
        """
        Search for relevant legal cases.

        Parameters
        ----------
        query : str
            Keywords or case description.
        jurisdiction : str | None
            Optional jurisdiction filter (e.g. ``"federal"``, ``"CA"``).

        Returns
        -------
        dict with keys: ``status``, ``cases``, ``tier``, ``disclaimer``.
        """
        self._check_request_limit()
        self._check_tool_access("case_search")
        self._request_count += 1

        return {
            "status": "success",
            "cases": (
                f"[Mock] Cases matching '{query}' in "
                f"jurisdiction '{jurisdiction or 'all'}'"
            ),
            "tier": self.tier.value,
            "disclaimer": self.DISCLAIMER,
        }

    def find_class_actions(self, industry: str) -> dict:
        """
        Find active or settled class action lawsuits in a given industry.

        Parameters
        ----------
        industry : str
            Industry sector (e.g. ``"pharmaceutical"``, ``"tech"``).

        Returns
        -------
        dict with keys: ``industry``, ``results``, ``tier``, ``disclaimer``.
        """
        self._check_request_limit()
        self._check_tool_access("class_action_finder")
        self._request_count += 1

        return {
            "industry": industry,
            "results": f"[Mock] Class actions in '{industry}' industry",
            "tier": self.tier.value,
            "disclaimer": self.DISCLAIMER,
        }

    def list_tools(self) -> list[str]:
        """Return the legal tools available on the current tier."""
        return list(LF_TOOLS.get(self.tier.value, []))

    def get_history(self) -> list[dict]:
        """Return a copy of the conversation history."""
        return list(self._history)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self._history = []

    # ------------------------------------------------------------------
    # Tier information
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Print and return a description of the current legal bot tier."""
        info = get_lf_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        lines = [
            f"=== {info['name']} Lawsuit Finder Bot Tier ===",
            f"Price   : ${info['price_usd_monthly']:.2f}/month",
            f"Requests: {limit}/month",
            f"Support : {info['support_level']}",
            "",
            "Legal research features:",
        ]
        for feat in info["lf_features"]:
            lines.append(f"  ✓ {feat}")
        lines.append("")
        lines.append("Available tools:")
        for t in info["tools"]:
            lines.append(f"  • {t}")
        lines.append("")
        lines.append(f"⚠  {self.DISCLAIMER}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Print details about the next available tier upgrade."""
        next_tier = get_upgrade_path(self.tier)
        if next_tier is None:
            msg = f"You are already on the highest tier ({self.config.name})."
        else:
            msg = (
                f"Upgrade to {next_tier.name} for "
                f"${next_tier.price_usd_monthly:.2f}/month to unlock "
                f"class action discovery and attorney matching."
            )
        print(msg)
        return msg

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _default_tool(self, message: str) -> str:
        available = LF_TOOLS.get(self.tier.value, ["case_search"])
        lower = message.lower()
        if "class action" in lower or "class-action" in lower:
            return "class_action_finder"
        if "settlement" in lower:
            return "settlement_tracker"
        if "attorney" in lower or "lawyer" in lower:
            return "attorney_matcher"
        if "statute" in lower or "law" in lower:
            return "statute_lookup"
        return available[0] if available else "case_search"

    def _check_tool_access(self, tool: str) -> None:
        allowed = LF_TOOLS.get(self.tier.value, [])
        if tool not in allowed:
            raise LawsuitFinderTierError(
                f"Tool '{tool}' is not available on the "
                f"{self.config.name} tier. Upgrade to access it."
            )

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise LawsuitFinderRequestLimitError(
                f"Monthly request limit of {limit} reached on the "
                f"{self.config.name} tier."
            )

    def _requests_remaining(self) -> int | None:
        limit = self.config.requests_per_month
        if limit is None:
            return None
        return max(0, limit - self._request_count)
