"""
Feature 3: App Feature Update Bot
Functionality: Notifies users of new features and updates in the app via
  in-app announcements, email digests, and changelog entries.
Use Cases: Ensuring users are aware of improvements and new capabilities.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 example product update records
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": 1,  "version": "v3.5.0", "title": "AI Deal Scoring Engine",           "type": "major_feature", "tier_required": "PRO",        "date": "2025-05-01", "description": "New AI model scores every deal on a 0-100 scale using 15 market signals.", "views": 8420, "action_rate": 34.2},
    {"id": 2,  "version": "v3.5.0", "title": "Real-Time Lead Alerts",            "type": "feature",       "tier_required": "FREE",       "date": "2025-05-01", "description": "Get instant push notifications when high-value leads are detected.", "views": 6234, "action_rate": 28.7},
    {"id": 3,  "version": "v3.5.0", "title": "Bulk Bot Runner (50 bots at once)","type": "major_feature", "tier_required": "ENTERPRISE", "date": "2025-05-01", "description": "Run up to 50 bots simultaneously for maximum automation throughput.", "views": 3120, "action_rate": 52.1},
    {"id": 4,  "version": "v3.4.2", "title": "Stripe Connect Integration",       "type": "integration",   "tier_required": "PRO",        "date": "2025-04-20", "description": "Receive payments directly to your Stripe account from bot-generated leads.", "views": 9800, "action_rate": 41.3},
    {"id": 5,  "version": "v3.4.2", "title": "Bug Fix: Dashboard Load Speed",    "type": "bug_fix",       "tier_required": "FREE",       "date": "2025-04-20", "description": "Fixed a bug causing slow load times for users with 100+ bots.", "views": 4560, "action_rate": 12.1},
    {"id": 6,  "version": "v3.4.1", "title": "CSV Export for All Reports",       "type": "feature",       "tier_required": "PRO",        "date": "2025-04-15", "description": "Download any analytics report as a CSV with one click.", "views": 5670, "action_rate": 25.8},
    {"id": 7,  "version": "v3.4.1", "title": "Dark Mode",                        "type": "ui",            "tier_required": "FREE",       "date": "2025-04-15", "description": "Toggle dark mode in Settings → Appearance for easier late-night work.", "views": 12300, "action_rate": 67.4},
    {"id": 8,  "version": "v3.4.0", "title": "White-Label Bot Dashboard",        "type": "major_feature", "tier_required": "ENTERPRISE", "date": "2025-04-10", "description": "Rebrand the entire bot dashboard with your company's logo, colors, and domain.", "views": 2890, "action_rate": 43.2},
    {"id": 9,  "version": "v3.4.0", "title": "Zapier Integration (5000+ apps)",  "type": "integration",   "tier_required": "PRO",        "date": "2025-04-10", "description": "Connect DreamCo to Zapier and automate workflows across 5,000+ tools.", "views": 11200, "action_rate": 38.5},
    {"id": 10, "version": "v3.3.5", "title": "Google Sheets Bot Sync",           "type": "integration",   "tier_required": "FREE",       "date": "2025-04-05", "description": "Sync bot output data directly to a Google Sheet in real time.", "views": 7840, "action_rate": 29.6},
    {"id": 11, "version": "v3.3.5", "title": "Multi-Language Support (12 langs)","type": "feature",       "tier_required": "FREE",       "date": "2025-04-05", "description": "DreamCo now supports 12 languages including Spanish, French, German, and Japanese.", "views": 4320, "action_rate": 18.3},
    {"id": 12, "version": "v3.3.4", "title": "Improved Performance (2x faster)", "type": "performance",   "tier_required": "FREE",       "date": "2025-04-01", "description": "Core bot engine rewritten for 2x faster execution and 40% lower token usage.", "views": 9120, "action_rate": 22.7},
    {"id": 13, "version": "v3.3.4", "title": "Bot Version History",              "type": "feature",       "tier_required": "PRO",        "date": "2025-04-01", "description": "View and restore previous versions of any bot configuration.", "views": 3450, "action_rate": 16.8},
    {"id": 14, "version": "v3.3.3", "title": "Team Permissions Management",      "type": "feature",       "tier_required": "PRO",        "date": "2025-03-25", "description": "Set granular permissions: Admin, Editor, Viewer for every team member.", "views": 5670, "action_rate": 31.2},
    {"id": 15, "version": "v3.3.3", "title": "Bug Fix: Payment Webhook Retry",   "type": "bug_fix",       "tier_required": "FREE",       "date": "2025-03-25", "description": "Fixed a race condition causing duplicate payment webhook deliveries.", "views": 2100, "action_rate": 8.4},
    {"id": 16, "version": "v3.3.2", "title": "AI Content Generator Bot",         "type": "major_feature", "tier_required": "PRO",        "date": "2025-03-20", "description": "Generate blog posts, social media content, and ad copy using GPT-4.", "views": 15600, "action_rate": 56.8},
    {"id": 17, "version": "v3.3.2", "title": "Predictive Revenue Analytics",     "type": "analytics",     "tier_required": "ENTERPRISE", "date": "2025-03-20", "description": "ML model predicts 30-day revenue based on current bot performance trends.", "views": 4200, "action_rate": 47.3},
    {"id": 18, "version": "v3.3.1", "title": "HubSpot CRM Integration",          "type": "integration",   "tier_required": "PRO",        "date": "2025-03-15", "description": "Auto-sync leads and deals from bots directly into HubSpot CRM.", "views": 8900, "action_rate": 35.6},
    {"id": 19, "version": "v3.3.1", "title": "Custom Webhook Builder",           "type": "developer",     "tier_required": "PRO",        "date": "2025-03-15", "description": "Build and test webhooks visually without writing code.", "views": 3780, "action_rate": 22.1},
    {"id": 20, "version": "v3.3.0", "title": "Bot Marketplace Launch",           "type": "major_feature", "tier_required": "FREE",       "date": "2025-03-10", "description": "Browse and install 200+ community-built bot templates from the marketplace.", "views": 22100, "action_rate": 48.9},
    {"id": 21, "version": "v3.2.5", "title": "Improved Mobile App",              "type": "mobile",        "tier_required": "FREE",       "date": "2025-03-05", "description": "v2.0 of the mobile app with redesigned navigation and offline mode.", "views": 11400, "action_rate": 42.3},
    {"id": 22, "version": "v3.2.5", "title": "Email Digest Reports",             "type": "analytics",     "tier_required": "PRO",        "date": "2025-03-05", "description": "Receive a daily or weekly email summary of bot performance and revenue.", "views": 5600, "action_rate": 19.7},
    {"id": 23, "version": "v3.2.4", "title": "Security: SOC 2 Type II Certified","type": "security",     "tier_required": "FREE",       "date": "2025-03-01", "description": "DreamCo is now SOC 2 Type II certified. Full audit report available.", "views": 3200, "action_rate": 15.4},
    {"id": 24, "version": "v3.2.4", "title": "Affiliate Dashboard",              "type": "feature",       "tier_required": "PRO",        "date": "2025-03-01", "description": "Track referrals, commissions, and payouts in a dedicated affiliate dashboard.", "views": 8900, "action_rate": 38.2},
    {"id": 25, "version": "v3.2.3", "title": "One-Click Bot Templates",          "type": "feature",       "tier_required": "FREE",       "date": "2025-02-25", "description": "Deploy pre-built bot templates for Real Estate, Fiverr, Marketing in one click.", "views": 16700, "action_rate": 61.5},
    {"id": 26, "version": "v3.2.2", "title": "Competitor Price Monitor Bot",     "type": "major_feature", "tier_required": "PRO",        "date": "2025-02-20", "description": "Monitor competitor pricing across platforms and receive real-time alerts.", "views": 7400, "action_rate": 33.8},
    {"id": 27, "version": "v3.2.1", "title": "A/B Bot Testing Framework",        "type": "developer",     "tier_required": "ENTERPRISE", "date": "2025-02-15", "description": "Run statistically significant A/B tests across two bot configurations.", "views": 2900, "action_rate": 28.6},
    {"id": 28, "version": "v3.2.0", "title": "Revenue Milestone Badges",         "type": "gamification",  "tier_required": "FREE",       "date": "2025-02-10", "description": "Earn badges when bots hit $100, $1K, $10K milestones. Share on LinkedIn!", "views": 14300, "action_rate": 55.3},
    {"id": 29, "version": "v3.1.9", "title": "Salesforce CRM Integration",       "type": "integration",   "tier_required": "ENTERPRISE", "date": "2025-02-05", "description": "Two-way sync between DreamCo bots and Salesforce contacts, leads, and opportunities.", "views": 6700, "action_rate": 44.1},
    {"id": 30, "version": "v3.1.8", "title": "Initial ENTERPRISE Plan Launch",   "type": "major_feature", "tier_required": "ENTERPRISE", "date": "2025-02-01", "description": "Introducing the ENTERPRISE plan with unlimited bots, white-label, and dedicated support.", "views": 19800, "action_rate": 72.3},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "max_updates": 10,  "targeted_notify": False, "changelog_access": True},
    "PRO":        {"price_usd": 29,  "max_updates": None,"targeted_notify": True,  "changelog_access": True},
    "ENTERPRISE": {"price_usd": 99,  "max_updates": None,"targeted_notify": True,  "changelog_access": True},
}


class FeatureUpdateBot:
    """Notifies users about new features, improvements, and bug fixes.

    Competes with Beamer and Headway by providing tier-targeted announcements,
    engagement analytics, and automated email digests.
    Monetization: $29/month PRO or $99/month ENTERPRISE subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="FeatureUpdateBot")

    def _available_updates(self) -> list[dict]:
        limit = self._config["max_updates"]
        return EXAMPLES[:limit] if limit else EXAMPLES

    def get_latest_updates(self, count: int = 5) -> list[dict]:
        """Return the N most recent product updates."""
        return sorted(
            self._available_updates(), key=lambda u: u["date"], reverse=True
        )[:count]

    def get_updates_by_type(self, update_type: str) -> list[dict]:
        """Return updates filtered by type."""
        return [u for u in self._available_updates() if u["type"] == update_type]

    def get_updates_for_tier(self, tier: str) -> list[dict]:
        """Return updates relevant to a specific tier."""
        tier_order = {"FREE": 0, "PRO": 1, "ENTERPRISE": 2}
        user_level = tier_order.get(tier, 0)
        return [
            u for u in self._available_updates()
            if tier_order.get(u["tier_required"], 0) <= user_level
        ]

    def get_high_engagement_updates(self, min_action_rate: float = 40.0) -> list[dict]:
        """Return updates with high user engagement (action rate)."""
        return [u for u in self._available_updates() if u["action_rate"] >= min_action_rate]

    def send_notification(self, update_id: int, user_email: str) -> dict:
        """Send an update notification to a user (PRO/ENTERPRISE)."""
        if not self._config["targeted_notify"]:
            raise PermissionError(
                "Targeted notifications require PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        update = next((u for u in EXAMPLES if u["id"] == update_id), None)
        if update is None:
            raise ValueError(f"Update ID {update_id} not found.")
        return {
            "sent": True,
            "user_email": user_email,
            "update_title": update["title"],
            "message": f"🆕 {update['version']}: {update['title']} — {update['description'][:80]}...",
        }

    def get_changelog(self, version: str | None = None) -> list[dict]:
        """Return the full changelog, optionally filtered by version."""
        updates = self._available_updates()
        if version:
            updates = [u for u in updates if u["version"] == version]
        return sorted(updates, key=lambda u: u["date"], reverse=True)

    def get_update_analytics(self) -> dict:
        """Return engagement analytics across all updates."""
        updates = self._available_updates()
        avg_views = round(sum(u["views"] for u in updates) / len(updates), 0) if updates else 0
        avg_action = round(sum(u["action_rate"] for u in updates) / len(updates), 2) if updates else 0
        by_type: dict[str, int] = {}
        for u in updates:
            by_type[u["type"]] = by_type.get(u["type"], 0) + 1
        return {
            "total_updates": len(updates),
            "avg_views_per_update": avg_views,
            "avg_action_rate_pct": avg_action,
            "updates_by_type": by_type,
            "highest_engagement": max(updates, key=lambda u: u["action_rate"])["title"] if updates else None,
            "tier": self.tier,
        }

    def describe_tier(self) -> str:
        cfg = self._config
        limit = cfg["max_updates"] if cfg["max_updates"] else "all"
        lines = [
            f"=== FeatureUpdateBot — {self.tier} Tier ===",
            f"  Monthly price        : ${cfg['price_usd']}/month",
            f"  Updates accessible   : {limit}",
            f"  Targeted notify      : {'enabled' if cfg['targeted_notify'] else 'disabled'}",
            f"  Changelog access     : {'enabled' if cfg['changelog_access'] else 'disabled'}",
        ]
        return "\n".join(lines)

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "feature_updates", "updates_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {"pipeline_complete": result.get("pipeline_complete"), "analytics": self.get_update_analytics()}


if __name__ == "__main__":
    bot = FeatureUpdateBot(tier="PRO")
    latest = bot.get_latest_updates(3)
    print("Latest 3 updates:")
    for u in latest:
        print(f"  🆕 {u['version']} — {u['title']} ({u['action_rate']}% action rate)")
    high_eng = bot.get_high_engagement_updates(50.0)
    print(f"\nHigh-engagement updates (>50%): {len(high_eng)}")
    analytics = bot.get_update_analytics()
    print(f"Avg action rate: {analytics['avg_action_rate_pct']}%")
    print(bot.describe_tier())

NotificationBot = FeatureUpdateBot


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


class FeatureUpdateBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


_orig_featureupdate_bot_init = FeatureUpdateBot.__init__


def _featureupdate_bot_new_init(self, tier=Tier.FREE):
    if not isinstance(tier, Tier):
        tier_str = str(tier).lower()
        if tier_str not in ("free", "pro", "enterprise"):
            raise ValueError(f"Invalid tier '{tier}'. Choose from ['FREE', 'PRO', 'ENTERPRISE']")
        tier = Tier(tier_str)
    _orig_featureupdate_bot_init(self, tier.value.upper())
    self.tier = tier


FeatureUpdateBot.__init__ = _featureupdate_bot_new_init
FeatureUpdateBot.RESULT_LIMITS = {"free": 5, "pro": 25, "enterprise": 100}


def _featureupdate_bot_monthly_price(self):
    return _TIER_MONTHLY_PRICE[self.tier.value]


def _featureupdate_bot_get_tier_info(self):
    return {
        "tier": self.tier.value,
        "monthly_price_usd": self.monthly_price(),
        "result_limit": self.RESULT_LIMITS[self.tier.value],
    }


def _featureupdate_bot_enforce_tier(self, required_value):
    order = ["free", "pro", "enterprise"]
    if order.index(self.tier.value) < order.index(required_value):
        raise FeatureUpdateBotTierError(
            f"{required_value.upper()} tier required. Current: {self.tier.value}"
        )


def _featureupdate_bot_list_items(self, limit=None):
    cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
    return _random_tier.sample(EXAMPLES, min(cap, len(EXAMPLES)))


def _featureupdate_bot_analyze(self):
    self._enforce_tier("pro")
    return {"bot": "FeatureUpdateBot", "tier": self.tier.value, "count": len(EXAMPLES)}


def _featureupdate_bot_export_report(self):
    self._enforce_tier("enterprise")
    return {"bot": "FeatureUpdateBot", "tier": self.tier.value, "total_items": len(EXAMPLES), "items": EXAMPLES}


FeatureUpdateBot.monthly_price = _featureupdate_bot_monthly_price
FeatureUpdateBot.get_tier_info = _featureupdate_bot_get_tier_info
FeatureUpdateBot._enforce_tier = _featureupdate_bot_enforce_tier
FeatureUpdateBot.list_items = _featureupdate_bot_list_items
FeatureUpdateBot.analyze = _featureupdate_bot_analyze
FeatureUpdateBot.export_report = _featureupdate_bot_export_report
