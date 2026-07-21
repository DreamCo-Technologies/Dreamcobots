"""
Finance Bot — tier-aware personal and business finance assistant.

Usage
-----
    from bots.finance_bot.finance_bot import FinanceBot
    from bots.ai_chatbot.tiers import Tier

    bot = FinanceBot(tier=Tier.PRO)
    response = bot.chat("Analyze my Q3 cash flow")
    print(response["message"])
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.finance_bot.tiers import (
    FINANCE_EXTRA_FEATURES,
    FINANCE_TOOLS,
    get_finance_tier_info,
)


class FinanceTierError(Exception):
    """Raised when a finance tool is not available on the current tier."""


class FinanceRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class FinanceBot:
    """
    Tier-aware finance assistant for personal and business use.

    Supported tools (by tier):
      FREE       -- budget tracker, expense categorization, savings tips
      PRO        -- investment portfolio analysis, tax estimator, cash flow reports
      ENTERPRISE -- multi-entity accounting, compliance reporting, ERP sync

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling tool access.
    """

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
        Process a finance query and return a structured response.

        Parameters
        ----------
        message : str
            User's natural-language finance question or instruction.
        tool : str | None
            Optional tool to invoke directly.

        Returns
        -------
        dict with keys: ``message``, ``tool``, ``tier``,
        ``requests_used``, ``requests_remaining``.
        """
        self._check_request_limit()
        active_tool = tool or self._default_tool(message)
        self._check_tool_access(active_tool)

        self._request_count += 1
        response_text = (
            f"[FinanceBot/{active_tool}] Processed: {message!r}"
        )
        self._history.append({"role": "user", "content": message})
        self._history.append({"role": "assistant", "content": response_text})

        return {
            "message": response_text,
            "tool": active_tool,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def analyze(self, tool: str, data: dict | None = None) -> dict:
        """
        Run a specific finance analysis tool with structured data.

        Parameters
        ----------
        tool : str
            Tool identifier (must be available on current tier).
        data : dict | None
            Optional input data for the analysis.

        Returns
        -------
        dict with keys: ``tool``, ``status``, ``result``, ``tier``.
        """
        self._check_request_limit()
        self._check_tool_access(tool)
        self._request_count += 1

        return {
            "tool": tool,
            "status": "completed",
            "result": f"[Mock] Finance tool '{tool}' ran with data: {data}",
            "tier": self.tier.value,
        }

    def list_tools(self) -> list[str]:
        """Return the finance tools available on the current tier."""
        return list(FINANCE_TOOLS.get(self.tier.value, []))

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
        """Print and return a description of the current finance tier."""
        info = get_finance_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        lines = [
            f"=== {info['name']} Finance Bot Tier ===",
            f"Price   : ${info['price_usd_monthly']:.2f}/month",
            f"Requests: {limit}/month",
            f"Support : {info['support_level']}",
            "",
            "Finance features:",
        ]
        for feat in info["finance_features"]:
            lines.append(f"  ✓ {feat}")
        lines.append("")
        lines.append("Available tools:")
        for t in info["tools"]:
            lines.append(f"  • {t}")
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
                f"${next_tier.price_usd_monthly:.2f}/month to unlock advanced "
                f"finance analytics."
            )
        print(msg)
        return msg

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _default_tool(self, message: str) -> str:
        available = FINANCE_TOOLS.get(self.tier.value, ["budget_tracker"])
        lower = message.lower()
        if "budget" in lower or "expense" in lower:
            return "budget_tracker"
        if "invest" in lower or "portfolio" in lower:
            return "portfolio_analyzer"
        if "tax" in lower:
            return "tax_estimator"
        if "cash" in lower or "flow" in lower:
            return "cash_flow_report"
        if "savings" in lower:
            return "savings_planner"
        return available[0] if available else "budget_tracker"

    def _check_tool_access(self, tool: str) -> None:
        allowed = FINANCE_TOOLS.get(self.tier.value, [])
        if tool not in allowed:
            raise FinanceTierError(
                f"Finance tool '{tool}' is not available on the "
                f"{self.config.name} tier. Upgrade to access it."
            )

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise FinanceRequestLimitError(
                f"Monthly request limit of {limit} reached on the "
                f"{self.config.name} tier."
            )

    def _requests_remaining(self) -> int | None:
        limit = self.config.requests_per_month
        if limit is None:
            return None
        return max(0, limit - self._request_count)
