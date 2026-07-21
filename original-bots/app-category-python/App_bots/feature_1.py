"""
Feature 1: App User Onboarding Bot
Functionality: Guides new users through the app setup process with personalized
  checklists, progress tracking, and contextual tips.
Use Cases: Improving user retention rates and reducing time-to-value.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 example onboarding step records
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": 1,  "step": "Create Account",               "category": "setup",       "user_type": "all",        "completion_rate": 98.5, "avg_time_sec": 45,  "tip": "Use a business email for team features.", "required": True},
    {"id": 2,  "step": "Verify Email",                  "category": "setup",       "user_type": "all",        "completion_rate": 87.3, "avg_time_sec": 60,  "tip": "Check spam folder if email doesn't arrive.", "required": True},
    {"id": 3,  "step": "Set Up Profile",                "category": "profile",     "user_type": "all",        "completion_rate": 78.2, "avg_time_sec": 120, "tip": "Add a photo to increase trust by 40%.", "required": False},
    {"id": 4,  "step": "Connect Integration",           "category": "integrations","user_type": "business",   "completion_rate": 62.4, "avg_time_sec": 180, "tip": "Connect Slack for real-time bot alerts.", "required": False},
    {"id": 5,  "step": "Create First Bot",              "category": "core",        "user_type": "all",        "completion_rate": 71.8, "avg_time_sec": 300, "tip": "Start with the Real Estate Bot template.", "required": True},
    {"id": 6,  "step": "Run Your First Automation",     "category": "core",        "user_type": "all",        "completion_rate": 58.6, "avg_time_sec": 240, "tip": "Test with a small dataset first.", "required": True},
    {"id": 7,  "step": "Set Up Billing",                "category": "billing",     "user_type": "paid",       "completion_rate": 92.1, "avg_time_sec": 90,  "tip": "Annual plans save 20% vs monthly.", "required": False},
    {"id": 8,  "step": "Invite Team Members",           "category": "collaboration","user_type": "business",  "completion_rate": 45.3, "avg_time_sec": 120, "tip": "Teams with 3+ members see 2x results.", "required": False},
    {"id": 9,  "step": "Configure Notifications",       "category": "settings",    "user_type": "all",        "completion_rate": 55.7, "avg_time_sec": 60,  "tip": "Enable Slack/email alerts for bot completions.", "required": False},
    {"id": 10, "step": "Watch Getting Started Video",   "category": "education",   "user_type": "all",        "completion_rate": 42.1, "avg_time_sec": 300, "tip": "Our tutorial reduces setup time by 60%.", "required": False},
    {"id": 11, "step": "Complete AI Profile Survey",    "category": "personalization","user_type": "all",     "completion_rate": 38.9, "avg_time_sec": 120, "tip": "This helps us recommend the right bots.", "required": False},
    {"id": 12, "step": "Connect CRM (Salesforce/HubSpot)","category": "integrations","user_type": "enterprise","completion_rate": 78.4,"avg_time_sec": 240,"tip": "CRM sync unlocks lead scoring features.", "required": False},
    {"id": 13, "step": "Set Revenue Goals",             "category": "strategy",    "user_type": "all",        "completion_rate": 52.3, "avg_time_sec": 90,  "tip": "Users who set goals earn 3x more on average.", "required": False},
    {"id": 14, "step": "Enable API Access",             "category": "developer",   "user_type": "enterprise", "completion_rate": 85.2, "avg_time_sec": 60,  "tip": "Generate your API key in Settings > Developer.", "required": False},
    {"id": 15, "step": "Configure Webhook Endpoints",   "category": "developer",   "user_type": "enterprise", "completion_rate": 72.8, "avg_time_sec": 180, "tip": "Webhooks enable real-time event processing.", "required": False},
    {"id": 16, "step": "Set Up Payment Methods",        "category": "billing",     "user_type": "all",        "completion_rate": 80.6, "avg_time_sec": 90,  "tip": "Stripe and PayPal accepted.", "required": False},
    {"id": 17, "step": "Explore Bot Marketplace",       "category": "discovery",   "user_type": "all",        "completion_rate": 65.4, "avg_time_sec": 120, "tip": "Browse 100+ bot templates for your industry.", "required": False},
    {"id": 18, "step": "Run Lead Generator Bot",        "category": "core",        "user_type": "business",   "completion_rate": 48.7, "avg_time_sec": 360, "tip": "Configure your niche for best results.", "required": False},
    {"id": 19, "step": "Schedule First Report",         "category": "analytics",   "user_type": "pro",        "completion_rate": 39.2, "avg_time_sec": 60,  "tip": "Weekly reports keep you on track.", "required": False},
    {"id": 20, "step": "Enable Two-Factor Authentication","category": "security",  "user_type": "all",        "completion_rate": 34.5, "avg_time_sec": 90,  "tip": "2FA protects your revenue data.", "required": False},
    {"id": 21, "step": "Complete Compliance Questionnaire","category": "compliance","user_type": "enterprise", "completion_rate": 91.3, "avg_time_sec": 180, "tip": "Required for GDPR and CCPA features.", "required": True},
    {"id": 22, "step": "Upload Brand Assets",           "category": "customization","user_type": "enterprise","completion_rate": 70.2, "avg_time_sec": 120, "tip": "White-label your bots with your brand.", "required": False},
    {"id": 23, "step": "Configure Stripe Connect",      "category": "billing",     "user_type": "paid",       "completion_rate": 88.7, "avg_time_sec": 150, "tip": "Receive payments directly to your account.", "required": False},
    {"id": 24, "step": "Set Up Affiliate Program",      "category": "growth",      "user_type": "pro",        "completion_rate": 28.4, "avg_time_sec": 90,  "tip": "Earn $50 for every referral who upgrades.", "required": False},
    {"id": 25, "step": "Join Community Slack",          "category": "community",   "user_type": "all",        "completion_rate": 22.8, "avg_time_sec": 30,  "tip": "2,000+ members share strategies daily.", "required": False},
    {"id": 26, "step": "Book Onboarding Call",          "category": "support",     "user_type": "enterprise", "completion_rate": 95.6, "avg_time_sec": 300, "tip": "1-on-1 with your dedicated success manager.", "required": False},
    {"id": 27, "step": "Set Up Zapier/Make Triggers",   "category": "integrations","user_type": "pro",        "completion_rate": 41.3, "avg_time_sec": 240, "tip": "Zapier connects DreamCo to 5,000+ apps.", "required": False},
    {"id": 28, "step": "Enable Auto-Revenue Mode",      "category": "core",        "user_type": "all",        "completion_rate": 31.9, "avg_time_sec": 180, "tip": "Bots run 24/7 to generate revenue while you sleep.", "required": False},
    {"id": 29, "step": "Review Pricing Strategy",       "category": "strategy",    "user_type": "all",        "completion_rate": 44.6, "avg_time_sec": 90,  "tip": "Free tier works great for validation phase.", "required": False},
    {"id": 30, "step": "Achieve First Revenue Milestone","category": "achievement","user_type": "all",        "completion_rate": 18.3, "avg_time_sec": 0,   "tip": "Users who hit $100 in the first week retain at 90%+.", "required": False},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "max_steps": 10,  "ai_personalization": False, "progress_tracking": True},
    "PRO":        {"price_usd": 29,  "max_steps": 20,  "ai_personalization": True,  "progress_tracking": True},
    "ENTERPRISE": {"price_usd": 99,  "max_steps": None,"ai_personalization": True,  "progress_tracking": True},
}


class UserOnboardingBot:
    """Guides new users through app setup with personalized checklists and tips.

    Competes with Appcues and Intercom by providing role-based onboarding flows,
    completion tracking, and AI-powered personalization.
    Monetization: $29/month PRO or $99/month ENTERPRISE subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="UserOnboardingBot")
        self._completed_steps: list[int] = []

    def _available_steps(self) -> list[dict]:
        limit = self._config["max_steps"]
        return EXAMPLES[:limit] if limit else EXAMPLES

    def get_onboarding_checklist(self, user_type: str = "all") -> list[dict]:
        """Return the onboarding checklist for a user type."""
        steps = self._available_steps()
        if user_type != "all":
            steps = [s for s in steps if s["user_type"] in (user_type, "all")]
        return steps

    def get_required_steps(self) -> list[dict]:
        """Return only the required (mandatory) onboarding steps."""
        return [s for s in self._available_steps() if s["required"]]

    def complete_step(self, step_id: int) -> dict:
        """Mark a step as completed."""
        step = next((s for s in EXAMPLES if s["id"] == step_id), None)
        if step is None:
            raise ValueError(f"Step ID {step_id} not found.")
        if step_id not in self._completed_steps:
            self._completed_steps.append(step_id)
        progress = self.get_progress()
        return {
            "completed": True,
            "step": step["step"],
            "progress_pct": progress["progress_pct"],
            "next_tip": progress.get("next_step", {}).get("tip") if progress.get("next_step") else None,
        }

    def get_progress(self) -> dict:
        """Return current onboarding progress."""
        available = self._available_steps()
        total = len(available)
        completed = len([s for s in available if s["id"] in self._completed_steps])
        progress_pct = round(completed / total * 100, 1) if total else 0
        next_step = next((s for s in available if s["id"] not in self._completed_steps), None)
        return {
            "total_steps": total,
            "completed_steps": completed,
            "progress_pct": progress_pct,
            "next_step": next_step,
            "is_complete": completed == total,
        }

    def get_steps_by_category(self, category: str) -> list[dict]:
        """Return steps filtered by category."""
        return [s for s in self._available_steps() if s["category"] == category]

    def get_low_completion_steps(self, threshold_pct: float = 50.0) -> list[dict]:
        """Return steps with completion rates below the threshold."""
        return [s for s in self._available_steps() if s["completion_rate"] < threshold_pct]

    def get_personalized_path(self, user_type: str, goals: list[str]) -> list[dict]:
        """Get an AI-personalized onboarding path (PRO/ENTERPRISE)."""
        if not self._config["ai_personalization"]:
            raise PermissionError(
                "AI personalization requires PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        base_steps = self.get_onboarding_checklist(user_type)
        goal_categories = {
            "revenue": ["core", "billing", "strategy", "achievement"],
            "automation": ["core", "integrations", "developer"],
            "team": ["collaboration", "setup", "security"],
            "analytics": ["analytics", "core", "settings"],
        }
        priority_cats: list[str] = []
        for goal in goals:
            priority_cats.extend(goal_categories.get(goal, []))
        priority_steps = [s for s in base_steps if s["category"] in priority_cats]
        other_steps = [s for s in base_steps if s["category"] not in priority_cats]
        return (priority_steps + other_steps)[:10]

    def get_onboarding_analytics(self) -> dict:
        """Return aggregate analytics across all onboarding steps."""
        steps = self._available_steps()
        avg_completion = round(sum(s["completion_rate"] for s in steps) / len(steps), 2) if steps else 0
        avg_time = round(sum(s["avg_time_sec"] for s in steps) / len(steps), 2) if steps else 0
        by_category: dict[str, float] = {}
        counts: dict[str, int] = {}
        for s in steps:
            cat = s["category"]
            by_category[cat] = by_category.get(cat, 0) + s["completion_rate"]
            counts[cat] = counts.get(cat, 0) + 1
        cat_avg = {k: round(v / counts[k], 2) for k, v in by_category.items()}
        return {
            "total_steps": len(steps),
            "avg_completion_rate_pct": avg_completion,
            "avg_time_per_step_sec": avg_time,
            "completion_by_category": cat_avg,
            "tier": self.tier,
        }

    def describe_tier(self) -> str:
        cfg = self._config
        limit = cfg["max_steps"] if cfg["max_steps"] else "all"
        lines = [
            f"=== UserOnboardingBot — {self.tier} Tier ===",
            f"  Monthly price      : ${cfg['price_usd']}/month",
            f"  Onboarding steps   : {limit}",
            f"  Progress tracking  : {'enabled' if cfg['progress_tracking'] else 'disabled'}",
            f"  AI personalization : {'enabled' if cfg['ai_personalization'] else 'disabled'}",
        ]
        return "\n".join(lines)

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "user_onboarding", "steps_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {"pipeline_complete": result.get("pipeline_complete"), "analytics": self.get_onboarding_analytics()}


if __name__ == "__main__":
    bot = UserOnboardingBot(tier="PRO")
    checklist = bot.get_onboarding_checklist("all")
    print(f"Total onboarding steps: {len(checklist)}")
    required = bot.get_required_steps()
    print(f"Required steps: {[s['step'] for s in required]}")
    bot.complete_step(1)
    bot.complete_step(2)
    progress = bot.get_progress()
    print(f"Progress: {progress['progress_pct']}% — Next: {progress['next_step']['step']}")
    print(bot.describe_tier())


OnboardingBot = UserOnboardingBot


# ---------------------------------------------------------------------------
# Tier system additions for test compatibility
# ---------------------------------------------------------------------------
import random as _random_tier
from enum import Enum as _TierEnum


class Tier(_TierEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other.upper()
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()


_TIER_MONTHLY_PRICE = {"free": 0, "pro": 29, "enterprise": 99}


class UserOnboardingBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


_orig_useronboarding_bot_init = UserOnboardingBot.__init__


def _useronboarding_bot_new_init(self, tier=Tier.FREE):
    if not isinstance(tier, Tier):
        tier_str = str(tier).lower()
        if tier_str not in ("free", "pro", "enterprise"):
            raise ValueError(f"Invalid tier '{tier}'. Choose from ['FREE', 'PRO', 'ENTERPRISE']")
        tier = Tier(tier_str)
    _orig_useronboarding_bot_init(self, tier.value.upper())
    self.tier = tier


UserOnboardingBot.__init__ = _useronboarding_bot_new_init
UserOnboardingBot.RESULT_LIMITS = {"free": 5, "pro": 25, "enterprise": 100}


def _useronboarding_bot_monthly_price(self):
    return _TIER_MONTHLY_PRICE[self.tier.value]


def _useronboarding_bot_get_tier_info(self):
    return {
        "tier": self.tier.value,
        "monthly_price_usd": self.monthly_price(),
        "result_limit": self.RESULT_LIMITS[self.tier.value],
    }


def _useronboarding_bot_enforce_tier(self, required_value):
    order = ["free", "pro", "enterprise"]
    if order.index(self.tier.value) < order.index(required_value):
        raise UserOnboardingBotTierError(
            f"{required_value.upper()} tier required. Current: {self.tier.value}"
        )


def _useronboarding_bot_list_items(self, limit=None):
    cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
    return _random_tier.sample(EXAMPLES, min(cap, len(EXAMPLES)))


def _useronboarding_bot_analyze(self):
    self._enforce_tier("pro")
    return {"bot": "UserOnboardingBot", "tier": self.tier.value, "count": len(EXAMPLES)}


def _useronboarding_bot_export_report(self):
    self._enforce_tier("enterprise")
    return {"bot": "UserOnboardingBot", "tier": self.tier.value, "total_items": len(EXAMPLES), "items": EXAMPLES}


UserOnboardingBot.monthly_price = _useronboarding_bot_monthly_price
UserOnboardingBot.get_tier_info = _useronboarding_bot_get_tier_info
UserOnboardingBot._enforce_tier = _useronboarding_bot_enforce_tier
UserOnboardingBot.list_items = _useronboarding_bot_list_items
UserOnboardingBot.analyze = _useronboarding_bot_analyze
UserOnboardingBot.export_report = _useronboarding_bot_export_report
