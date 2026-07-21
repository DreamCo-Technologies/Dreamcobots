"""
Feature 1: Social Media Posting Bot
Functionality: Automates posting updates to social media channels including
  Twitter, Instagram, LinkedIn, and Facebook. Includes scheduling, hashtag
  optimization, and engagement analytics.
Use Cases: Businesses maintaining an active online presence.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 example social media post templates
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": 1,  "platform": "twitter",   "content": "🚀 Excited to announce our new product launch! Check it out at our website. #ProductLaunch #Startup",     "type": "announcement", "hashtags": ["#ProductLaunch", "#Startup"],    "scheduled": "2025-05-01 09:00", "status": "pending"},
    {"id": 2,  "platform": "instagram", "content": "Behind the scenes at our office! 📸 Our team is working hard to bring you amazing results. #BehindTheScenes", "type": "culture",       "hashtags": ["#BehindTheScenes", "#Team"],    "scheduled": "2025-05-01 11:00", "status": "pending"},
    {"id": 3,  "platform": "linkedin",  "content": "We're hiring! 🌟 Join our growing team as a Senior Software Engineer. Apply now: [link] #Hiring #TechJobs",  "type": "recruitment",  "hashtags": ["#Hiring", "#TechJobs"],          "scheduled": "2025-05-01 14:00", "status": "posted"},
    {"id": 4,  "platform": "facebook",  "content": "Customer spotlight 🙌 Read how @ClientName grew their revenue 200% using our platform! [link]",              "type": "testimonial",  "hashtags": [],                                "scheduled": "2025-05-02 10:00", "status": "pending"},
    {"id": 5,  "platform": "twitter",   "content": "Quick tip: Always A/B test your landing pages! 📊 Small changes = big results. #MarketingTips #GrowthHack", "type": "tip",           "hashtags": ["#MarketingTips", "#GrowthHack"], "scheduled": "2025-05-02 12:00", "status": "posted"},
    {"id": 6,  "platform": "instagram", "content": "New blog post: 10 ways to boost your conversion rate 📈 Link in bio! #Marketing #ConversionRate",            "type": "content",      "hashtags": ["#Marketing", "#ConversionRate"], "scheduled": "2025-05-02 15:00", "status": "pending"},
    {"id": 7,  "platform": "linkedin",  "content": "Proud to share that we've just hit $1M ARR! 🎉 Thank you to our amazing customers and team. #Milestone",      "type": "milestone",    "hashtags": ["#Milestone", "#SaaS"],           "scheduled": "2025-05-03 09:00", "status": "pending"},
    {"id": 8,  "platform": "facebook",  "content": "Flash sale! 🔥 50% off all plans today only. Use code DREAM50. Offer expires midnight! [link]",               "type": "promotion",    "hashtags": ["#Sale", "#Deal"],                "scheduled": "2025-05-03 10:00", "status": "pending"},
    {"id": 9,  "platform": "twitter",   "content": "🧵 Thread: 7 automation tools that saved us 10+ hours per week… (1/7) #Automation #Productivity",             "type": "thread",       "hashtags": ["#Automation", "#Productivity"],  "scheduled": "2025-05-03 11:00", "status": "posted"},
    {"id": 10, "platform": "instagram", "content": "Swipe left to see our before & after case study! 📊 #CaseStudy #Results #Marketing",                          "type": "case_study",   "hashtags": ["#CaseStudy", "#Results"],        "scheduled": "2025-05-04 09:00", "status": "pending"},
    {"id": 11, "platform": "linkedin",  "content": "Just published: The Ultimate Guide to B2B Lead Generation in 2025. Read it here: [link] #B2B #LeadGen",        "type": "content",      "hashtags": ["#B2B", "#LeadGen"],              "scheduled": "2025-05-04 10:00", "status": "pending"},
    {"id": 12, "platform": "facebook",  "content": "Happy Friday! 🎊 End the week strong. What's your biggest win this week? Comment below!",                      "type": "engagement",   "hashtags": [],                                "scheduled": "2025-05-04 17:00", "status": "posted"},
    {"id": 13, "platform": "twitter",   "content": "Joining us at #WebSummit2025? Let's connect! DM to schedule a meeting. 🤝 #Networking #TechConference",       "type": "event",        "hashtags": ["#WebSummit2025", "#Networking"], "scheduled": "2025-05-05 09:00", "status": "pending"},
    {"id": 14, "platform": "instagram", "content": "Quote of the day 💡 'The best marketing doesn't feel like marketing.' — Tom Fishburne #MarketingQuote",        "type": "quote",        "hashtags": ["#MarketingQuote", "#Inspire"],   "scheduled": "2025-05-05 12:00", "status": "pending"},
    {"id": 15, "platform": "linkedin",  "content": "We partnered with @Company to bring you an even better product experience. Read more: [link] #Partnership",    "type": "announcement", "hashtags": ["#Partnership", "#B2B"],          "scheduled": "2025-05-06 09:00", "status": "pending"},
    {"id": 16, "platform": "facebook",  "content": "📹 New video: How to triple your email open rates in 30 days. Watch now: [link] #EmailMarketing",             "type": "video",        "hashtags": ["#EmailMarketing", "#Video"],     "scheduled": "2025-05-06 14:00", "status": "pending"},
    {"id": 17, "platform": "twitter",   "content": "Hot take: Most startups fail not because of product but because of distribution. Agree? 🔥 #StartupTips",      "type": "opinion",      "hashtags": ["#StartupTips", "#Growth"],       "scheduled": "2025-05-07 10:00", "status": "pending"},
    {"id": 18, "platform": "instagram", "content": "Monday motivation 💪 Start the week with your goals clear and your mindset strong. #MondayMotivation",         "type": "motivation",   "hashtags": ["#MondayMotivation", "#Goals"],   "scheduled": "2025-05-07 08:00", "status": "pending"},
    {"id": 19, "platform": "linkedin",  "content": "Congrats to our Customer Success team for achieving a 98% satisfaction rate! 🏆 #CustomerSuccess #Proud",      "type": "culture",      "hashtags": ["#CustomerSuccess", "#Team"],     "scheduled": "2025-05-07 11:00", "status": "pending"},
    {"id": 20, "platform": "facebook",  "content": "Webinar alert! 🎓 Join us live on May 15 to learn about AI-powered marketing. Register free: [link]",          "type": "event",        "hashtags": ["#Webinar", "#AI", "#Marketing"], "scheduled": "2025-05-07 15:00", "status": "pending"},
    {"id": 21, "platform": "twitter",   "content": "Reminder: Consistency > Perfection in content marketing 🎯 Post daily, improve weekly. #ContentMarketing",     "type": "tip",          "hashtags": ["#ContentMarketing", "#Social"],  "scheduled": "2025-05-08 09:00", "status": "pending"},
    {"id": 22, "platform": "instagram", "content": "Throwback to our first office 🏠 vs now 🏢 Look how far we've come! #TBT #CompanyGrowth",                       "type": "milestone",    "hashtags": ["#TBT", "#CompanyGrowth"],        "scheduled": "2025-05-08 12:00", "status": "pending"},
    {"id": 23, "platform": "linkedin",  "content": "Open question for founders: What's the one marketing channel you'd never stop using? 🤔 Drop your answer below.", "type": "engagement",  "hashtags": ["#Founders", "#Marketing"],       "scheduled": "2025-05-08 14:00", "status": "pending"},
    {"id": 24, "platform": "facebook",  "content": "We just crossed 10,000 customers! 🎉 A huge thank you to every single one of you. Share your story with us!",  "type": "milestone",    "hashtags": [],                                "scheduled": "2025-05-09 10:00", "status": "pending"},
    {"id": 25, "platform": "twitter",   "content": "Here's how we reduced churn by 40%: [Thread] 🧵 #SaaS #CustomerRetention #ChurnReduction",                     "type": "thread",       "hashtags": ["#SaaS", "#CustomerRetention"],   "scheduled": "2025-05-09 11:00", "status": "pending"},
    {"id": 26, "platform": "instagram", "content": "New product feature drop! 🆕 Now you can automate your entire workflow in 3 clicks. Try it free! #ProductUpdate","type": "product",      "hashtags": ["#ProductUpdate", "#Automation"], "scheduled": "2025-05-09 15:00", "status": "pending"},
    {"id": 27, "platform": "linkedin",  "content": "Sharing 5 lessons from scaling from $0 to $1M ARR: [article link] #SaaS #Startup #Lessons",                    "type": "content",      "hashtags": ["#SaaS", "#Startup"],             "scheduled": "2025-05-10 09:00", "status": "pending"},
    {"id": 28, "platform": "facebook",  "content": "Answer this: Morning coffee ☕ or afternoon energy drink ⚡? We're a morning coffee team! How about you?",       "type": "engagement",   "hashtags": [],                                "scheduled": "2025-05-10 11:00", "status": "pending"},
    {"id": 29, "platform": "twitter",   "content": "DreamCo just launched a new bot that automates your social media. Try it free → [link] #Automation #AI",        "type": "promotion",    "hashtags": ["#Automation", "#AI", "#Marketing"],"scheduled": "2025-05-11 10:00","status": "pending"},
    {"id": 30, "platform": "instagram", "content": "Thank you for 50K followers! 🙏 You make this community amazing. Something special is coming soon… 👀",          "type": "milestone",    "hashtags": ["#ThankYou", "#Community"],       "scheduled": "2025-05-11 14:00", "status": "pending"},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "monthly_posts": 10,  "platforms": ["twitter"],                            "analytics": False, "scheduling": False},
    "PRO":        {"price_usd": 49,  "monthly_posts": 200, "platforms": ["twitter", "instagram", "linkedin"],   "analytics": True,  "scheduling": True},
    "ENTERPRISE": {"price_usd": 199, "monthly_posts": None,"platforms": ["twitter", "instagram", "linkedin", "facebook"], "analytics": True, "scheduling": True},
}


class SocialMediaPostingBot:
    """Automates social media posting across Twitter, Instagram, LinkedIn, Facebook.

    Competes with Buffer and Hootsuite by providing AI-powered content templates,
    hashtag optimization, and real-time engagement analytics.
    Monetization: $49/month PRO or $199/month ENTERPRISE subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="SocialMediaPostingBot")
        self._posted: list[dict] = []

    def _check_platform(self, platform: str) -> None:
        if platform not in self._config["platforms"]:
            raise PermissionError(
                f"Platform '{platform}' requires a higher tier. "
                f"Available on {self.tier}: {self._config['platforms']}. "
                "Upgrade at dreamcobots.com/pricing"
            )

    def schedule_post(self, post_id: int) -> dict:
        """Schedule a post from the template library."""
        if not self._config["scheduling"]:
            raise PermissionError(
                "Post scheduling requires PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        monthly_limit = self._config["monthly_posts"]
        if monthly_limit is not None and len(self._posted) >= monthly_limit:
            raise PermissionError(
                f"Monthly post limit of {monthly_limit} reached on {self.tier} tier."
            )
        post = next((p for p in EXAMPLES if p["id"] == post_id), None)
        if post is None:
            raise ValueError(f"Post template ID {post_id} not found.")
        self._check_platform(post["platform"])
        scheduled = dict(post)
        scheduled["status"] = "scheduled"
        self._posted.append(scheduled)
        return scheduled

    def post_now(self, post_id: int) -> dict:
        """Immediately post from a template."""
        monthly_limit = self._config["monthly_posts"]
        if monthly_limit is not None and len(self._posted) >= monthly_limit:
            raise PermissionError(
                f"Monthly post limit of {monthly_limit} reached on {self.tier} tier."
            )
        post = next((p for p in EXAMPLES if p["id"] == post_id), None)
        if post is None:
            raise ValueError(f"Post template ID {post_id} not found.")
        self._check_platform(post["platform"])
        result = dict(post)
        result["status"] = "posted"
        self._posted.append(result)
        return result

    def get_posts_by_platform(self, platform: str) -> list[dict]:
        """Return all post templates for a specific platform."""
        return [p for p in EXAMPLES if p["platform"] == platform]

    def get_posts_by_type(self, post_type: str) -> list[dict]:
        """Return posts of a specific type (announcement, tip, promotion, etc.)."""
        return [p for p in EXAMPLES if p["type"] == post_type]

    def get_pending_posts(self) -> list[dict]:
        """Return all pending (unscheduled) posts from the template library."""
        return [p for p in EXAMPLES if p["status"] == "pending"]

    def get_analytics(self) -> dict:
        """Return posting analytics (PRO/ENTERPRISE only)."""
        if not self._config["analytics"]:
            raise PermissionError(
                "Analytics require PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        by_platform: dict[str, int] = {}
        by_type: dict[str, int] = {}
        for p in EXAMPLES:
            by_platform[p["platform"]] = by_platform.get(p["platform"], 0) + 1
            by_type[p["type"]] = by_type.get(p["type"], 0) + 1
        return {
            "total_templates": len(EXAMPLES),
            "by_platform": by_platform,
            "by_type": by_type,
            "posts_this_month": len(self._posted),
            "tier": self.tier,
        }

    def get_available_platforms(self) -> list[str]:
        """Return the platforms available on the current tier."""
        return list(self._config["platforms"])

    def describe_tier(self) -> str:
        cfg = self._config
        limit = cfg["monthly_posts"] if cfg["monthly_posts"] else "unlimited"
        lines = [
            f"=== SocialMediaPostingBot — {self.tier} Tier ===",
            f"  Monthly price   : ${cfg['price_usd']}/month",
            f"  Monthly posts   : {limit}",
            f"  Platforms       : {', '.join(cfg['platforms'])}",
            f"  Scheduling      : {'enabled' if cfg['scheduling'] else 'disabled'}",
            f"  Analytics       : {'enabled' if cfg['analytics'] else 'disabled'}",
        ]
        return "\n".join(lines)

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "social_media_posting", "templates_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {
            "pipeline_complete": result.get("pipeline_complete"),
            "templates_available": len(EXAMPLES),
        }


if __name__ == "__main__":
    bot = SocialMediaPostingBot(tier="PRO")
    twitter_posts = bot.get_posts_by_platform("twitter")
    print(f"Twitter posts available: {len(twitter_posts)}")
    tips = bot.get_posts_by_type("tip")
    print(f"Marketing tip posts: {len(tips)}")
    analytics = bot.get_analytics()
    print(f"Posts by platform: {analytics['by_platform']}")
    print(bot.describe_tier())


SocialMediaBot = SocialMediaPostingBot


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


class SocialMediaPostingBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


_orig_socialmediaposting_bot_init = SocialMediaPostingBot.__init__


def _socialmediaposting_bot_new_init(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_socialmediaposting_bot_init(self, tier_val.upper())
    self.tier = tier if isinstance(tier, Tier) else Tier(tier_val)


SocialMediaPostingBot.__init__ = _socialmediaposting_bot_new_init
SocialMediaPostingBot.RESULT_LIMITS = {"free": 5, "pro": 25, "enterprise": 100}


def _socialmediaposting_bot_monthly_price(self):
    return _TIER_MONTHLY_PRICE[self.tier.value]


def _socialmediaposting_bot_get_tier_info(self):
    return {
        "tier": self.tier.value,
        "monthly_price_usd": self.monthly_price(),
        "result_limit": self.RESULT_LIMITS[self.tier.value],
    }


def _socialmediaposting_bot_enforce_tier(self, required_value):
    order = ["free", "pro", "enterprise"]
    if order.index(self.tier.value) < order.index(required_value):
        raise SocialMediaPostingBotTierError(
            f"{required_value.upper()} tier required. Current: {self.tier.value}"
        )


def _socialmediaposting_bot_list_items(self, limit=None):
    cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
    return _random_tier.sample(EXAMPLES, min(cap, len(EXAMPLES)))


def _socialmediaposting_bot_analyze(self):
    self._enforce_tier("pro")
    return {"bot": "SocialMediaPostingBot", "tier": self.tier.value, "count": len(EXAMPLES)}


def _socialmediaposting_bot_export_report(self):
    self._enforce_tier("enterprise")
    return {"bot": "SocialMediaPostingBot", "tier": self.tier.value, "total_items": len(EXAMPLES), "items": EXAMPLES}


SocialMediaPostingBot.monthly_price = _socialmediaposting_bot_monthly_price
SocialMediaPostingBot.get_tier_info = _socialmediaposting_bot_get_tier_info
SocialMediaPostingBot._enforce_tier = _socialmediaposting_bot_enforce_tier
SocialMediaPostingBot.list_items = _socialmediaposting_bot_list_items
SocialMediaPostingBot.analyze = _socialmediaposting_bot_analyze
SocialMediaPostingBot.export_report = _socialmediaposting_bot_export_report


# ---------------------------------------------------------------------------
# BuddyAI integration: bot_id, name, category, chat, end_session for SocialMediaPostingBot
# ---------------------------------------------------------------------------
import uuid as _uuid_mkt1


def _socialmediabot_new_init_full(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_socialmediaposting_bot_init(self, tier_val.upper())
    self.tier = tier if isinstance(tier, Tier) else Tier(tier_val)
    if not hasattr(self, "bot_id"):
        self.bot_id = str(_uuid_mkt1.uuid4())
    self.name = "Social Media Bot"
    self.category = "marketing"
    self.domain = "social_media"


SocialMediaPostingBot.__init__ = _socialmediabot_new_init_full


def _socialmediabot_chat(self, user_input: str, user_id: str = "anonymous") -> str:
    q = user_input.lower()
    if any(w in q for w in ("social", "marketing", "post", "campaign", "brand")):
        return "I can help with social media marketing! Let's boost your online presence."
    return "I'm your Social Media Marketing Bot. Ask me about campaigns, posts, or brand strategy."


def _socialmediabot_end_session(self, user_id: str) -> None:
    pass


SocialMediaPostingBot.chat = _socialmediabot_chat
SocialMediaPostingBot.end_session = _socialmediabot_end_session
SocialMediaBot = SocialMediaPostingBot

def _socialmediabot_status(self) -> dict:
    return {
        "name": self.name,
        "category": self.category,
        "domain": self.domain,
        "revenue": {"total_revenue_usd": 0.0},
        "datasets": {"datasets_available": 0, "total_sales": 0},
        "top_intents": ["social_media", "marketing"],
    }


SocialMediaPostingBot.status = _socialmediabot_status
SocialMediaBot = SocialMediaPostingBot
