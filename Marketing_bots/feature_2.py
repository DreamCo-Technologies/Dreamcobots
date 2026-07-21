"""
Feature 2: Email Campaign Bot
Functionality: Designs and sends out email marketing campaigns. Includes
  template library, subscriber management, A/B testing, and open-rate analytics.
Use Cases: Companies promoting products to their customer base.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 example email campaign templates
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": 1,  "name": "Welcome Series - Day 1",           "subject": "Welcome to DreamCo! Here's what to expect 🎉",                    "type": "welcome",       "open_rate": 52.3, "click_rate": 18.4, "subscribers": 5000,  "status": "active"},
    {"id": 2,  "name": "Welcome Series - Day 3",           "subject": "3 ways to get started with DreamCo today",                          "type": "welcome",       "open_rate": 44.1, "click_rate": 14.2, "subscribers": 5000,  "status": "active"},
    {"id": 3,  "name": "Welcome Series - Day 7",           "subject": "How are you getting on? Let us help 🤝",                             "type": "welcome",       "open_rate": 35.8, "click_rate": 10.6, "subscribers": 5000,  "status": "active"},
    {"id": 4,  "name": "Product Launch Blast",             "subject": "🚀 Introducing [Feature] — available NOW",                           "type": "announcement",  "open_rate": 41.2, "click_rate": 15.8, "subscribers": 25000, "status": "active"},
    {"id": 5,  "name": "Monthly Newsletter - May",         "subject": "May digest: Top stories, tips & updates 📰",                         "type": "newsletter",    "open_rate": 28.5, "click_rate": 8.2,  "subscribers": 20000, "status": "active"},
    {"id": 6,  "name": "Flash Sale Announcement",          "subject": "⚡ 48-HOUR SALE: 40% off everything. Code: DREAM40",                 "type": "promotional",   "open_rate": 38.7, "click_rate": 22.1, "subscribers": 30000, "status": "sent"},
    {"id": 7,  "name": "Abandoned Cart Recovery",          "subject": "You left something behind! 🛒 Complete your order",                  "type": "transactional", "open_rate": 45.6, "click_rate": 19.3, "subscribers": 1500,  "status": "active"},
    {"id": 8,  "name": "Re-engagement Campaign",           "subject": "We miss you! Here's 20% off to come back 💙",                        "type": "re_engagement", "open_rate": 22.4, "click_rate": 8.9,  "subscribers": 8000,  "status": "active"},
    {"id": 9,  "name": "Customer Win-Back",                "subject": "Is this goodbye? One last thing before you go…",                     "type": "win_back",      "open_rate": 18.3, "click_rate": 6.4,  "subscribers": 3000,  "status": "sent"},
    {"id": 10, "name": "Birthday Email",                   "subject": "🎂 Happy Birthday! A special gift inside",                           "type": "lifecycle",     "open_rate": 58.2, "click_rate": 24.6, "subscribers": 500,   "status": "active"},
    {"id": 11, "name": "Weekly Tips - Automation",         "subject": "This week: 3 automation hacks for 2025 ⚙️",                          "type": "educational",   "open_rate": 33.1, "click_rate": 11.4, "subscribers": 15000, "status": "active"},
    {"id": 12, "name": "Case Study Spotlight",             "subject": "How [Customer] 10x'd their revenue in 90 days 📈",                   "type": "social_proof",  "open_rate": 36.4, "click_rate": 13.7, "subscribers": 20000, "status": "sent"},
    {"id": 13, "name": "Free Webinar Invite",              "subject": "Free webinar: Master AI marketing in 60 min 🎓 [Register]",           "type": "event",         "open_rate": 30.2, "click_rate": 14.8, "subscribers": 25000, "status": "active"},
    {"id": 14, "name": "Review Request",                   "subject": "Got a minute? Share your experience 🙏",                             "type": "feedback",      "open_rate": 26.8, "click_rate": 9.2,  "subscribers": 5000,  "status": "active"},
    {"id": 15, "name": "Upsell Campaign - PRO",            "subject": "Upgrade to PRO and unlock 10x more power ⚡",                        "type": "upsell",        "open_rate": 24.5, "click_rate": 7.8,  "subscribers": 10000, "status": "active"},
    {"id": 16, "name": "Year in Review",                   "subject": "Your 2024 DreamCo recap — you did amazing! 🌟",                      "type": "lifecycle",     "open_rate": 47.3, "click_rate": 16.2, "subscribers": 20000, "status": "sent"},
    {"id": 17, "name": "Cold Outreach - SaaS Founders",   "subject": "How top founders automate 80% of their marketing",                   "type": "cold_outreach", "open_rate": 19.8, "click_rate": 5.6,  "subscribers": 1000,  "status": "active"},
    {"id": 18, "name": "Free Trial Expiry Reminder",       "subject": "Your free trial expires in 3 days ⏰ Upgrade now",                  "type": "transactional", "open_rate": 55.4, "click_rate": 28.3, "subscribers": 2000,  "status": "active"},
    {"id": 19, "name": "New Blog Post Notification",       "subject": "New post: 7 ways AI is transforming marketing in 2025 📖",           "type": "content",       "open_rate": 27.6, "click_rate": 10.1, "subscribers": 18000, "status": "active"},
    {"id": 20, "name": "Referral Program Launch",          "subject": "Earn $50 for every friend you refer 💸",                             "type": "referral",      "open_rate": 34.2, "click_rate": 16.9, "subscribers": 15000, "status": "active"},
    {"id": 21, "name": "Feature Announcement - API",       "subject": "NEW: Connect DreamCo to any tool with our API 🔌",                   "type": "announcement",  "open_rate": 32.8, "click_rate": 12.4, "subscribers": 10000, "status": "sent"},
    {"id": 22, "name": "End of Year Sale",                 "subject": "🎄 Our biggest sale of the year — 60% off for 24 hours only!",        "type": "promotional",   "open_rate": 46.7, "click_rate": 25.3, "subscribers": 40000, "status": "sent"},
    {"id": 23, "name": "VIP Customer Thank You",           "subject": "You're one of our top customers — here's a surprise 🎁",             "type": "loyalty",       "open_rate": 61.5, "click_rate": 30.1, "subscribers": 500,   "status": "active"},
    {"id": 24, "name": "Survey Campaign",                  "subject": "Quick question: What's your biggest marketing challenge? (30 sec)",  "type": "feedback",      "open_rate": 29.4, "click_rate": 12.8, "subscribers": 12000, "status": "active"},
    {"id": 25, "name": "Seasonal Campaign - Summer",       "subject": "☀️ Supercharge your summer marketing with DreamCo",                  "type": "seasonal",      "open_rate": 28.1, "click_rate": 9.5,  "subscribers": 20000, "status": "active"},
    {"id": 26, "name": "Competitor Comparison",            "subject": "DreamCo vs [Competitor]: See why 10K+ chose us 🏆",                   "type": "comparison",    "open_rate": 31.6, "click_rate": 13.2, "subscribers": 15000, "status": "sent"},
    {"id": 27, "name": "Milestone Celebration",            "subject": "🎉 We just hit 100,000 users — celebrate with us!",                   "type": "announcement",  "open_rate": 43.8, "click_rate": 17.6, "subscribers": 30000, "status": "sent"},
    {"id": 28, "name": "Drip Campaign - Lead Nurture 1",   "subject": "Before you buy, here's what you should know about DreamCo",          "type": "nurture",       "open_rate": 35.2, "click_rate": 11.8, "subscribers": 8000,  "status": "active"},
    {"id": 29, "name": "Drip Campaign - Lead Nurture 2",   "subject": "Still thinking? Here's a real ROI example from a customer like you", "type": "nurture",       "open_rate": 29.8, "click_rate": 10.4, "subscribers": 6500,  "status": "active"},
    {"id": 30, "name": "Drip Campaign - Lead Nurture 3",   "subject": "Last chance: Try DreamCo free for 14 days — no credit card needed", "type": "nurture",       "open_rate": 38.4, "click_rate": 19.7, "subscribers": 5200,  "status": "active"},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "max_campaigns": 3,    "subscribers": 500,    "ab_testing": False, "analytics": False},
    "PRO":        {"price_usd": 49,  "max_campaigns": 50,   "subscribers": 25000,  "ab_testing": True,  "analytics": True},
    "ENTERPRISE": {"price_usd": 199, "max_campaigns": None, "subscribers": None,   "ab_testing": True,  "analytics": True},
}


class EmailCampaignBot:
    """Designs and manages email marketing campaigns with A/B testing and analytics.

    Competes with Mailchimp and Klaviyo by providing AI-powered subject line
    optimization, smart segmentation, and real-time analytics.
    Monetization: $49/month PRO or $199/month ENTERPRISE subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="EmailCampaignBot")
        self._active_campaigns: list[dict] = []

    def get_campaign_templates(self, campaign_type: str | None = None) -> list[dict]:
        """Return all campaign templates, optionally filtered by type."""
        results = list(EXAMPLES)
        if campaign_type:
            results = [c for c in results if c["type"] == campaign_type]
        return results

    def activate_campaign(self, campaign_id: int) -> dict:
        """Activate a campaign template."""
        max_c = self._config["max_campaigns"]
        if max_c is not None and len(self._active_campaigns) >= max_c:
            raise PermissionError(
                f"Campaign limit of {max_c} reached on {self.tier} tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        campaign = next((c for c in EXAMPLES if c["id"] == campaign_id), None)
        if campaign is None:
            raise ValueError(f"Campaign ID {campaign_id} not found.")
        max_subs = self._config["subscribers"]
        if max_subs is not None and campaign["subscribers"] > max_subs:
            raise PermissionError(
                f"Subscriber limit of {max_subs} exceeded on {self.tier} tier."
            )
        result = dict(campaign)
        result["status"] = "active"
        self._active_campaigns.append(result)
        return result

    def get_top_performing_campaigns(self, metric: str = "open_rate", count: int = 5) -> list[dict]:
        """Return top campaigns by open rate or click rate."""
        if metric not in {"open_rate", "click_rate"}:
            raise ValueError("metric must be 'open_rate' or 'click_rate'")
        return sorted(EXAMPLES, key=lambda c: c[metric], reverse=True)[:count]

    def get_ab_test_recommendation(self, campaign_id: int) -> dict:
        """Get A/B test subject line suggestions (PRO/ENTERPRISE)."""
        if not self._config["ab_testing"]:
            raise PermissionError(
                "A/B testing requires PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        campaign = next((c for c in EXAMPLES if c["id"] == campaign_id), None)
        if campaign is None:
            raise ValueError(f"Campaign ID {campaign_id} not found.")
        return {
            "original_subject": campaign["subject"],
            "variant_a": campaign["subject"],
            "variant_b": f"RE: {campaign['subject']}",
            "variant_c": campaign["subject"].replace("🎉", "").strip() + " [Limited Time]",
            "recommendation": "Test variant B for 20% higher open rates in B2B segments.",
        }

    def get_analytics_report(self) -> dict:
        """Return campaign analytics report (PRO/ENTERPRISE)."""
        if not self._config["analytics"]:
            raise PermissionError(
                "Analytics require PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        avg_open = round(sum(c["open_rate"] for c in EXAMPLES) / len(EXAMPLES), 2)
        avg_click = round(sum(c["click_rate"] for c in EXAMPLES) / len(EXAMPLES), 2)
        top = self.get_top_performing_campaigns("open_rate", 3)
        by_type: dict[str, list[float]] = {}
        for c in EXAMPLES:
            by_type.setdefault(c["type"], []).append(c["open_rate"])
        type_avg = {t: round(sum(v) / len(v), 2) for t, v in by_type.items()}
        return {
            "total_campaigns": len(EXAMPLES),
            "avg_open_rate_pct": avg_open,
            "avg_click_rate_pct": avg_click,
            "top_campaigns": [{"name": c["name"], "open_rate": c["open_rate"]} for c in top],
            "open_rate_by_type": type_avg,
            "tier": self.tier,
        }

    def get_campaigns_by_type(self, campaign_type: str) -> list[dict]:
        """Return all campaigns of a specific type."""
        return self.get_campaign_templates(campaign_type)

    def describe_tier(self) -> str:
        cfg = self._config
        camp_limit = cfg["max_campaigns"] if cfg["max_campaigns"] else "unlimited"
        sub_limit = cfg["subscribers"] if cfg["subscribers"] else "unlimited"
        lines = [
            f"=== EmailCampaignBot — {self.tier} Tier ===",
            f"  Monthly price   : ${cfg['price_usd']}/month",
            f"  Max campaigns   : {camp_limit}",
            f"  Max subscribers : {sub_limit}",
            f"  A/B Testing     : {'enabled' if cfg['ab_testing'] else 'disabled'}",
            f"  Analytics       : {'enabled' if cfg['analytics'] else 'disabled'}",
        ]
        return "\n".join(lines)

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "email_campaigns", "templates_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {"pipeline_complete": result.get("pipeline_complete"), "templates": len(EXAMPLES)}


if __name__ == "__main__":
    bot = EmailCampaignBot(tier="PRO")
    top = bot.get_top_performing_campaigns("open_rate", 3)
    print("Top 3 email campaigns by open rate:")
    for c in top:
        print(f"  📧 {c['name']} — Open: {c['open_rate']}% | Click: {c['click_rate']}%")
    report = bot.get_analytics_report()
    print(f"\nAvg open rate: {report['avg_open_rate_pct']}%")
    print(bot.describe_tier())


EmailMarketingBot = EmailCampaignBot


# ---------------------------------------------------------------------------
# Tier system additions for test compatibility
# ---------------------------------------------------------------------------
import random as _random_tier
from enum import Enum as _TierEnum


class Tier(_TierEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


_TIER_MONTHLY_PRICE = {"free": 0, "pro": 29, "enterprise": 99}


class EmailCampaignBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


_orig_emailcampaign_bot_init = EmailCampaignBot.__init__


def _emailcampaign_bot_new_init(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_emailcampaign_bot_init(self, tier_val.upper())
    self.tier = tier if isinstance(tier, Tier) else Tier(tier_val)


EmailCampaignBot.__init__ = _emailcampaign_bot_new_init
EmailCampaignBot.RESULT_LIMITS = {"free": 5, "pro": 25, "enterprise": 100}


def _emailcampaign_bot_monthly_price(self):
    return _TIER_MONTHLY_PRICE[self.tier.value]


def _emailcampaign_bot_get_tier_info(self):
    return {
        "tier": self.tier.value,
        "monthly_price_usd": self.monthly_price(),
        "result_limit": self.RESULT_LIMITS[self.tier.value],
    }


def _emailcampaign_bot_enforce_tier(self, required_value):
    order = ["free", "pro", "enterprise"]
    if order.index(self.tier.value) < order.index(required_value):
        raise EmailCampaignBotTierError(
            f"{required_value.upper()} tier required. Current: {self.tier.value}"
        )


def _emailcampaign_bot_list_items(self, limit=None):
    cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
    return _random_tier.sample(EXAMPLES, min(cap, len(EXAMPLES)))


def _emailcampaign_bot_analyze(self):
    self._enforce_tier("pro")
    return {"bot": "EmailCampaignBot", "tier": self.tier.value, "count": len(EXAMPLES)}


def _emailcampaign_bot_export_report(self):
    self._enforce_tier("enterprise")
    return {"bot": "EmailCampaignBot", "tier": self.tier.value, "total_items": len(EXAMPLES), "items": EXAMPLES}


EmailCampaignBot.monthly_price = _emailcampaign_bot_monthly_price
EmailCampaignBot.get_tier_info = _emailcampaign_bot_get_tier_info
EmailCampaignBot._enforce_tier = _emailcampaign_bot_enforce_tier
EmailCampaignBot.list_items = _emailcampaign_bot_list_items
EmailCampaignBot.analyze = _emailcampaign_bot_analyze
EmailCampaignBot.export_report = _emailcampaign_bot_export_report
