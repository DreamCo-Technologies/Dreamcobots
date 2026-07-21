"""
Business Automation Bot — tier-aware workflow and task-automation assistant.

Usage
-----
    from bots.business_automation.business_automation_bot import BusinessAutomationBot
    from bots.ai_chatbot.tiers import Tier       # re-uses the shared Tier enum

    bot = BusinessAutomationBot(tier=Tier.FREE)
    response = bot.chat("Schedule a meeting for Monday 10 AM")
    print(response["message"])
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.business_automation.tiers import (
    BA_EXTRA_FEATURES,
    BA_WORKFLOWS,
    get_ba_tier_info,
)


class BusinessAutomationTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class BusinessAutomationRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class BusinessAutomationBot:
    """
    Tier-aware business automation assistant.

    Supported automation areas (by tier):
      FREE       -- meeting scheduling, task reminders, email drafts
      PRO        -- CRM integration, invoice generation, report automation
      ENTERPRISE -- full workflow orchestration, ERP integration, white-label

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature availability.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._history: list[dict] = []

    # ------------------------------------------------------------------
    # Core chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str, workflow: str | None = None) -> dict:
        """
        Process an automation request and return a structured response.

        Parameters
        ----------
        message : str
            The user's natural-language request.
        workflow : str | None
            Optional workflow ID to invoke directly.

        Returns
        -------
        dict with keys: ``message``, ``workflow``, ``tier``,
        ``requests_used``, ``requests_remaining``.
        """
        self._check_request_limit()
        active_workflow = workflow or self._default_workflow(message)
        self._check_workflow_access(active_workflow)

        self._request_count += 1
        response_text = (
            f"[BusinessAutomation/{active_workflow}] Processed: {message!r}"
        )
        self._history.append({"role": "user", "content": message})
        self._history.append({"role": "assistant", "content": response_text})

        return {
            "message": response_text,
            "workflow": active_workflow,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def run_workflow(self, workflow_id: str, params: dict | None = None) -> dict:
        """
        Run a named automation workflow.

        Parameters
        ----------
        workflow_id : str
            Workflow identifier (must be available on current tier).
        params : dict | None
            Optional parameters for the workflow.

        Returns
        -------
        dict with keys: ``workflow``, ``status``, ``result``, ``tier``.
        """
        self._check_request_limit()
        self._check_workflow_access(workflow_id)
        self._request_count += 1

        return {
            "workflow": workflow_id,
            "status": "completed",
            "result": f"[Mock] Workflow '{workflow_id}' executed with params: {params}",
            "tier": self.tier.value,
        }

    def list_workflows(self) -> list[str]:
        """Return the workflows available on the current tier."""
        return list(BA_WORKFLOWS.get(self.tier.value, []))

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
        """Print and return a description of the current tier."""
        info = get_ba_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        lines = [
            f"=== {info['name']} Business Automation Tier ===",
            f"Price   : ${info['price_usd_monthly']:.2f}/month",
            f"Requests: {limit}/month",
            f"Support : {info['support_level']}",
            "",
            "Automation features:",
        ]
        for feat in info["ba_features"]:
            lines.append(f"  ✓ {feat}")
        lines.append("")
        lines.append("Available workflows:")
        for wf in info["workflows"]:
            lines.append(f"  • {wf}")
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
                f"${next_tier.price_usd_monthly:.2f}/month and unlock "
                f"{len(BA_WORKFLOWS.get(next_tier.tier.value, []))} workflows."
            )
        print(msg)
        return msg

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _default_workflow(self, message: str) -> str:
        available = BA_WORKFLOWS.get(self.tier.value, ["meeting_scheduler"])
        lower = message.lower()
        if "meeting" in lower or "schedule" in lower:
            return "meeting_scheduler"
        if "invoice" in lower or "billing" in lower:
            return "invoice_generator"
        if "report" in lower:
            return "report_automation"
        if "email" in lower:
            return "email_drafter"
        return available[0] if available else "meeting_scheduler"

    def _check_workflow_access(self, workflow_id: str) -> None:
        allowed = BA_WORKFLOWS.get(self.tier.value, [])
        if workflow_id not in allowed:
            raise BusinessAutomationTierError(
                f"Workflow '{workflow_id}' is not available on the "
                f"{self.config.name} tier. Upgrade to access it."
            )

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise BusinessAutomationRequestLimitError(
                f"Monthly request limit of {limit} reached on the "
                f"{self.config.name} tier."
            )

    def _requests_remaining(self) -> int | None:
        limit = self.config.requests_per_month
        if limit is None:
            return None
        return max(0, limit - self._request_count)
