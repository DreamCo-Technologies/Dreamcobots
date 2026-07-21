"""
Feature 3: Customer Feedback Bot
Functionality: Collects and analyzes customer feedback on products and services.
  Includes NPS surveys, sentiment analysis, and actionable insights.
Use Cases: Businesses looking to improve customer satisfaction and retention.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 example customer feedback records
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": 1,  "customer": "Alice M.",     "product": "DreamCo PRO",    "nps_score": 10, "rating": 5, "feedback": "Best automation tool I've used. Cut my workload in half!",               "sentiment": "positive", "category": "ease_of_use",    "resolved": True},
    {"id": 2,  "customer": "Bob T.",        "product": "DreamCo PRO",    "nps_score": 9,  "rating": 5, "feedback": "Excellent customer support — very responsive and helpful.",               "sentiment": "positive", "category": "support",         "resolved": True},
    {"id": 3,  "customer": "Carol S.",      "product": "DreamCo FREE",   "nps_score": 7,  "rating": 4, "feedback": "Good product but I wish the free tier had more features.",                "sentiment": "neutral",  "category": "pricing",         "resolved": False},
    {"id": 4,  "customer": "David W.",      "product": "DreamCo ENTERPRISE","nps_score": 10,"rating": 5,"feedback": "Enterprise plan is worth every penny. ROI is phenomenal.",               "sentiment": "positive", "category": "value",           "resolved": True},
    {"id": 5,  "customer": "Emma R.",       "product": "DreamCo PRO",    "nps_score": 6,  "rating": 3, "feedback": "The app is good but the mobile experience needs improvement.",            "sentiment": "neutral",  "category": "product",         "resolved": False},
    {"id": 6,  "customer": "Frank L.",      "product": "DreamCo PRO",    "nps_score": 9,  "rating": 5, "feedback": "Onboarding was seamless. Was up and running in 10 minutes.",              "sentiment": "positive", "category": "onboarding",      "resolved": True},
    {"id": 7,  "customer": "Grace K.",      "product": "DreamCo ENTERPRISE","nps_score": 10,"rating": 5,"feedback": "The AI features in ENTERPRISE are incredibly powerful and accurate.",     "sentiment": "positive", "category": "product",         "resolved": True},
    {"id": 8,  "customer": "Henry P.",      "product": "DreamCo PRO",    "nps_score": 8,  "rating": 4, "feedback": "Very good tool. Would love better API documentation.",                    "sentiment": "positive", "category": "documentation",   "resolved": False},
    {"id": 9,  "customer": "Isabella N.",   "product": "DreamCo FREE",   "nps_score": 5,  "rating": 3, "feedback": "Too many limitations on the free plan. Considering upgrading.",           "sentiment": "neutral",  "category": "pricing",         "resolved": False},
    {"id": 10, "customer": "Jack D.",        "product": "DreamCo PRO",    "nps_score": 10, "rating": 5, "feedback": "This product is a game-changer for our marketing team!",                 "sentiment": "positive", "category": "value",           "resolved": True},
    {"id": 11, "customer": "Karen H.",      "product": "DreamCo ENTERPRISE","nps_score": 9, "rating": 5,"feedback": "Integration with Salesforce worked perfectly. Highly recommend.",         "sentiment": "positive", "category": "integrations",    "resolved": True},
    {"id": 12, "customer": "Leo A.",         "product": "DreamCo PRO",    "nps_score": 4,  "rating": 2, "feedback": "The dashboard is confusing and not intuitive at all.",                    "sentiment": "negative", "category": "ux",              "resolved": False},
    {"id": 13, "customer": "Mary B.",        "product": "DreamCo PRO",    "nps_score": 9,  "rating": 5, "feedback": "Automating lead generation with DreamCo doubled our pipeline.",           "sentiment": "positive", "category": "results",         "resolved": True},
    {"id": 14, "customer": "Nick C.",        "product": "DreamCo FREE",   "nps_score": 8,  "rating": 4, "feedback": "Great free option. I'll upgrade once I validate my business.",            "sentiment": "positive", "category": "value",           "resolved": True},
    {"id": 15, "customer": "Olivia E.",      "product": "DreamCo ENTERPRISE","nps_score": 10,"rating": 5,"feedback": "The dedicated account manager is incredible. Feels like a true partner.", "sentiment": "positive", "category": "support",         "resolved": True},
    {"id": 16, "customer": "Paul F.",        "product": "DreamCo PRO",    "nps_score": 3,  "rating": 2, "feedback": "I had a billing issue that took 3 days to resolve. Frustrating.",         "sentiment": "negative", "category": "billing",         "resolved": True},
    {"id": 17, "customer": "Quinn G.",       "product": "DreamCo PRO",    "nps_score": 10, "rating": 5, "feedback": "The automation features alone make this tool worth the price!",           "sentiment": "positive", "category": "product",         "resolved": True},
    {"id": 18, "customer": "Rachel J.",      "product": "DreamCo FREE",   "nps_score": 7,  "rating": 4, "feedback": "Works well but I'd like more analytics on the free tier.",               "sentiment": "neutral",  "category": "analytics",       "resolved": False},
    {"id": 19, "customer": "Sam M.",          "product": "DreamCo PRO",    "nps_score": 9,  "rating": 5, "feedback": "Love the new features added every month. Always improving!",              "sentiment": "positive", "category": "product",         "resolved": True},
    {"id": 20, "customer": "Tina O.",         "product": "DreamCo ENTERPRISE","nps_score": 10,"rating": 5,"feedback": "White-label option lets us resell this to our own clients. Amazing!",   "sentiment": "positive", "category": "value",           "resolved": True},
    {"id": 21, "customer": "Uma P.",          "product": "DreamCo PRO",    "nps_score": 8,  "rating": 4, "feedback": "Fast and reliable. Only minor issue is occasional slow load times.",     "sentiment": "positive", "category": "performance",     "resolved": False},
    {"id": 22, "customer": "Victor Q.",       "product": "DreamCo FREE",   "nps_score": 6,  "rating": 3, "feedback": "Decent free plan. Support response time could be faster.",               "sentiment": "neutral",  "category": "support",         "resolved": False},
    {"id": 23, "customer": "Wendy R.",        "product": "DreamCo PRO",    "nps_score": 10, "rating": 5, "feedback": "Best business decision I've made this year. 10 out of 10!",              "sentiment": "positive", "category": "value",           "resolved": True},
    {"id": 24, "customer": "Xander S.",       "product": "DreamCo ENTERPRISE","nps_score": 9, "rating": 5,"feedback": "Custom workflows are incredibly powerful and flexible.",                "sentiment": "positive", "category": "product",         "resolved": True},
    {"id": 25, "customer": "Yara T.",         "product": "DreamCo PRO",    "nps_score": 5,  "rating": 3, "feedback": "Sometimes the bot runs but doesn't produce expected output.",            "sentiment": "neutral",  "category": "reliability",     "resolved": False},
    {"id": 26, "customer": "Zach U.",         "product": "DreamCo PRO",    "nps_score": 9,  "rating": 5, "feedback": "Revenue grew 60% after deploying DreamCo to our sales workflow.",       "sentiment": "positive", "category": "results",         "resolved": True},
    {"id": 27, "customer": "Amy V.",          "product": "DreamCo FREE",   "nps_score": 8,  "rating": 4, "feedback": "Really impressed with the free tier. Will upgrade soon.",                "sentiment": "positive", "category": "value",           "resolved": True},
    {"id": 28, "customer": "Brian W.",        "product": "DreamCo ENTERPRISE","nps_score": 2, "rating": 1,"feedback": "Onboarding was poor and the promised features weren't ready on launch.", "sentiment": "negative", "category": "onboarding",      "resolved": True},
    {"id": 29, "customer": "Cindy X.",        "product": "DreamCo PRO",    "nps_score": 9,  "rating": 5, "feedback": "Helps my team stay focused on high-value work. Amazing product!",        "sentiment": "positive", "category": "productivity",    "resolved": True},
    {"id": 30, "customer": "Derek Y.",        "product": "DreamCo ENTERPRISE","nps_score": 10,"rating": 5,"feedback": "The ROI speaks for itself. We 3x'd our leads in 2 months.",            "sentiment": "positive", "category": "results",         "resolved": True},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "max_responses": 50,   "sentiment_analysis": False, "insights": False},
    "PRO":        {"price_usd": 29,  "max_responses": 1000, "sentiment_analysis": True,  "insights": False},
    "ENTERPRISE": {"price_usd": 99,  "max_responses": None, "sentiment_analysis": True,  "insights": True},
}


class CustomerFeedbackBot:
    """Collects, analyzes, and acts on customer feedback using NPS + sentiment AI.

    Competes with Qualtrics and SurveyMonkey by providing real-time NPS scoring,
    sentiment tagging, and AI-generated actionable insights.
    Monetization: $29/month PRO or $99/month ENTERPRISE subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="CustomerFeedbackBot")

    def _get_feedback(self) -> list[dict]:
        limit = self._config["max_responses"]
        return EXAMPLES[:limit] if limit else EXAMPLES

    def get_all_feedback(self) -> list[dict]:
        """Return all feedback within tier limit."""
        return self._get_feedback()

    def get_nps_score(self) -> dict:
        """Calculate Net Promoter Score (NPS)."""
        feedback = self._get_feedback()
        promoters = sum(1 for f in feedback if f["nps_score"] >= 9)
        passives = sum(1 for f in feedback if 7 <= f["nps_score"] <= 8)
        detractors = sum(1 for f in feedback if f["nps_score"] <= 6)
        total = len(feedback)
        nps = round(((promoters - detractors) / total) * 100, 1) if total else 0
        return {
            "nps": nps,
            "promoters": promoters,
            "passives": passives,
            "detractors": detractors,
            "total_responses": total,
            "grade": "Excellent" if nps >= 70 else "Good" if nps >= 50 else "Needs Work",
        }

    def get_sentiment_breakdown(self) -> dict:
        """Return sentiment distribution (PRO/ENTERPRISE)."""
        if not self._config["sentiment_analysis"]:
            raise PermissionError(
                "Sentiment analysis requires PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        feedback = self._get_feedback()
        counts: dict[str, int] = {}
        for f in feedback:
            counts[f["sentiment"]] = counts.get(f["sentiment"], 0) + 1
        return counts

    def get_feedback_by_category(self, category: str) -> list[dict]:
        """Return feedback tagged with a specific category."""
        return [f for f in self._get_feedback() if f["category"] == category]

    def get_negative_feedback(self) -> list[dict]:
        """Return all negative feedback records that need attention."""
        return [f for f in self._get_feedback() if f["sentiment"] == "negative"]

    def get_unresolved_issues(self) -> list[dict]:
        """Return feedback where the issue is not yet resolved."""
        return [f for f in self._get_feedback() if not f["resolved"]]

    def get_average_rating(self) -> float:
        """Return average product rating across all feedback."""
        fb = self._get_feedback()
        if not fb:
            return 0.0
        return round(sum(f["rating"] for f in fb) / len(fb), 2)

    def get_ai_insights(self) -> dict:
        """Generate AI-powered insights from feedback data (ENTERPRISE only)."""
        if not self._config["insights"]:
            raise PermissionError(
                "AI insights require ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        neg = self.get_negative_feedback()
        top_issues = {}
        for f in neg:
            top_issues[f["category"]] = top_issues.get(f["category"], 0) + 1
        nps = self.get_nps_score()
        return {
            "nps_summary": nps,
            "top_complaint_categories": top_issues,
            "unresolved_count": len(self.get_unresolved_issues()),
            "avg_rating": self.get_average_rating(),
            "recommendations": [
                "Improve UX dashboard — multiple customers flagged confusion.",
                "Streamline billing processes — billing complaints need faster resolution.",
                "Enhance free tier features to convert more FREE users to PRO.",
            ],
        }

    def describe_tier(self) -> str:
        cfg = self._config
        limit = cfg["max_responses"] if cfg["max_responses"] else "unlimited"
        lines = [
            f"=== CustomerFeedbackBot — {self.tier} Tier ===",
            f"  Monthly price      : ${cfg['price_usd']}/month",
            f"  Max responses      : {limit}",
            f"  Sentiment analysis : {'enabled' if cfg['sentiment_analysis'] else 'disabled'}",
            f"  AI insights        : {'enabled' if cfg['insights'] else 'disabled (ENTERPRISE)'}",
        ]
        return "\n".join(lines)

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "customer_feedback_analysis", "responses_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {"pipeline_complete": result.get("pipeline_complete"), "nps": self.get_nps_score()}


if __name__ == "__main__":
    bot = CustomerFeedbackBot(tier="PRO")
    nps = bot.get_nps_score()
    print(f"NPS Score: {nps['nps']} ({nps['grade']})")
    print(f"Promoters: {nps['promoters']} | Passives: {nps['passives']} | Detractors: {nps['detractors']}")
    sentiment = bot.get_sentiment_breakdown()
    print(f"Sentiment: {sentiment}")
    print(f"Average rating: {bot.get_average_rating()} ⭐")
    print(bot.describe_tier())

ContentCreationBot = CustomerFeedbackBot


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


class CustomerFeedbackBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


_orig_customerfeedback_bot_init = CustomerFeedbackBot.__init__


def _customerfeedback_bot_new_init(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_customerfeedback_bot_init(self, tier_val.upper())
    self.tier = tier if isinstance(tier, Tier) else Tier(tier_val)


CustomerFeedbackBot.__init__ = _customerfeedback_bot_new_init
CustomerFeedbackBot.RESULT_LIMITS = {"free": 5, "pro": 25, "enterprise": 100}


def _customerfeedback_bot_monthly_price(self):
    return _TIER_MONTHLY_PRICE[self.tier.value]


def _customerfeedback_bot_get_tier_info(self):
    return {
        "tier": self.tier.value,
        "monthly_price_usd": self.monthly_price(),
        "result_limit": self.RESULT_LIMITS[self.tier.value],
    }


def _customerfeedback_bot_enforce_tier(self, required_value):
    order = ["free", "pro", "enterprise"]
    if order.index(self.tier.value) < order.index(required_value):
        raise CustomerFeedbackBotTierError(
            f"{required_value.upper()} tier required. Current: {self.tier.value}"
        )


def _customerfeedback_bot_list_items(self, limit=None):
    cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
    return _random_tier.sample(EXAMPLES, min(cap, len(EXAMPLES)))


def _customerfeedback_bot_analyze(self):
    self._enforce_tier("pro")
    return {"bot": "CustomerFeedbackBot", "tier": self.tier.value, "count": len(EXAMPLES)}


def _customerfeedback_bot_export_report(self):
    self._enforce_tier("enterprise")
    return {"bot": "CustomerFeedbackBot", "tier": self.tier.value, "total_items": len(EXAMPLES), "items": EXAMPLES}


CustomerFeedbackBot.monthly_price = _customerfeedback_bot_monthly_price
CustomerFeedbackBot.get_tier_info = _customerfeedback_bot_get_tier_info
CustomerFeedbackBot._enforce_tier = _customerfeedback_bot_enforce_tier
CustomerFeedbackBot.list_items = _customerfeedback_bot_list_items
CustomerFeedbackBot.analyze = _customerfeedback_bot_analyze
CustomerFeedbackBot.export_report = _customerfeedback_bot_export_report

# ---------------------------------------------------------------------------
# CustomerFeedbackBot extended interface: chat with sentiment detection
# ---------------------------------------------------------------------------
import uuid as _uuid_cfb


def _customerfeedbackbot_full_init(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_customerfeedback_bot_init(self, tier_val.upper())
    self.tier = tier if isinstance(tier, Tier) else Tier(tier_val)
    if not hasattr(self, "bot_id"):
        self.bot_id = str(_uuid_cfb.uuid4())
    self.name = "Customer Feedback Bot"
    self.category = "marketing"
    self.domain = "customer_feedback"
    self._feedback_counts = {"positive": 0, "negative": 0, "neutral": 0}


def _customerfeedbackbot_chat(self, user_input: str, user_id: str = "anonymous") -> str:
    q = user_input.lower()
    positive_words = {"amazing", "great", "love", "excellent", "fantastic", "wonderful", "good", "happy"}
    negative_words = {"terrible", "awful", "broken", "bad", "horrible", "worst", "hate", "poor"}
    words = set(q.split())
    if words & positive_words:
        self._feedback_counts["positive"] += 1
        return "Thank you for the positive feedback! We're glad you're happy."
    elif words & negative_words:
        self._feedback_counts["negative"] += 1
        return "We're sorry to hear about your negative experience. We'll improve."
    else:
        self._feedback_counts["neutral"] += 1
        return "Thank you for your neutral feedback. We value all input."


CustomerFeedbackBot.__init__ = _customerfeedbackbot_full_init
CustomerFeedbackBot.chat = _customerfeedbackbot_chat
CustomerFeedbackBot.end_session = lambda self, user_id: None
