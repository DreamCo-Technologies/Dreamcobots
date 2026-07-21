"""
Dreamcobots Automation Bot — tier-aware task scheduling and workflow automation.

Usage
-----
    from automation_bot import AutomationBot
    from tiers import Tier

    bot = AutomationBot(tier=Tier.FREE)
    task = bot.create_task("daily_report", "daily@08:00", {"action": "send_email"})
    print(task)
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path

import importlib.util as _ilu
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_spec = _ilu.spec_from_file_location("_automation_tiers", os.path.join(_THIS_DIR, "tiers.py"))
_automation_tiers = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_automation_tiers)
AUTOMATION_FEATURES = _automation_tiers.AUTOMATION_FEATURES
TASK_LIMITS = _automation_tiers.TASK_LIMITS
get_automation_tier_info = _automation_tiers.get_automation_tier_info


class AutomationBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class AutomationBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class AutomationBot:
    """
    Tier-aware task scheduling and workflow automation bot.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling task limits and feature availability.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._tasks: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def create_task(self, name: str, trigger: str, action: dict) -> dict:
        """
        Create a scheduled task.

        Parameters
        ----------
        name : str
            Unique task name.
        trigger : str
            Trigger specification (e.g., "daily@08:00", "webhook://my-hook").
        action : dict
            Action configuration (e.g., {"type": "send_email", "to": "..."}).

        Returns
        -------
        dict
        """
        self._check_request_limit()
        task_limit = TASK_LIMITS[self.tier.value]
        if task_limit is not None and len(self._tasks) >= task_limit:
            raise AutomationBotTierError(
                f"Task limit of {task_limit} reached on the {self.config.name} tier. "
                "Upgrade to create more tasks."
            )
        if name in self._tasks:
            raise AutomationBotTierError(f"A task named '{name}' already exists.")
        if "webhook" in trigger and self.tier == Tier.FREE:
            raise AutomationBotTierError(
                "Webhook triggers require PRO or ENTERPRISE tier."
            )
        self._request_count += 1
        task = {
            "name": name,
            "trigger": trigger,
            "action": action,
            "status": "active",
            "runs": 0,
        }
        self._tasks[name] = task
        return {
            "task": task,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def run_task(self, task_name: str) -> dict:
        """
        Execute a task immediately.

        Parameters
        ----------
        task_name : str
            Name of the task to run.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        if task_name not in self._tasks:
            raise AutomationBotTierError(f"No task named '{task_name}' found.")
        self._request_count += 1
        self._tasks[task_name]["runs"] += 1
        return {
            "task_name": task_name,
            "result": f"[Mock] Task '{task_name}' executed successfully.",
            "run_number": self._tasks[task_name]["runs"],
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def list_tasks(self) -> list[dict]:
        """Return a list of all registered tasks."""
        return list(self._tasks.values())

    def delete_task(self, task_name: str) -> None:
        """Delete a task by name."""
        if task_name not in self._tasks:
            raise AutomationBotTierError(f"No task named '{task_name}' found.")
        del self._tasks[task_name]

    # ------------------------------------------------------------------
    # Tier information
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Print and return a description of the current tier."""
        info = get_automation_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        task_limit = (
            "Unlimited"
            if info["task_limit"] is None
            else str(info["task_limit"])
        )
        lines = [
            f"=== {info['name']} Automation Bot Tier ===",
            f"Price      : ${info['price_usd_monthly']:.2f}/month",
            f"Requests   : {limit}/month",
            f"Task limit : {task_limit}",
            f"Support    : {info['support_level']}",
            "",
            "Features:",
        ]
        for feat in info["automation_features"]:
            lines.append(f"  ✓ {feat}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Print details about the next available tier upgrade."""
        next_cfg = get_upgrade_path(self.tier)
        if next_cfg is None:
            msg = f"You are already on the top-tier plan ({self.config.name})."
            print(msg)
            return msg
        current_feats = set(AUTOMATION_FEATURES[self.tier.value])
        new_feats = [f for f in AUTOMATION_FEATURES[next_cfg.tier.value] if f not in current_feats]
        lines = [
            f"=== Upgrade: {self.config.name} → {next_cfg.name} ===",
            f"New price: ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New features:",
        ]
        for feat in new_feats:
            lines.append(f"  + {feat}")
        lines.append(
            f"\nTo upgrade, set tier=Tier.{next_cfg.tier.name} when "
            "constructing AutomationBot or contact support."
        )
        output = "\n".join(lines)
        print(output)
        return output

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise AutomationBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))


if __name__ == "__main__":
    bot = AutomationBot(tier=Tier.FREE)
    bot.describe_tier()
