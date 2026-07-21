"""
Feature 3: Fiverr Review Generator Bot
Functionality: Requests client feedback after service completion, analyzes
  review sentiment, and generates AI-powered response templates.
Use Cases: Freelancers wanting to build their reputation and increase ratings.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 example client reviews with sentiment data
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": 1,  "buyer": "techstartup_co",  "gig": "Logo Design",           "rating": 5, "review": "Absolutely stunning logo! Fast delivery and easy to work with.",         "sentiment": "positive", "response_sent": False},
    {"id": 2,  "buyer": "bloggerpro22",    "gig": "SEO Blog Post",          "rating": 5, "review": "High quality content that ranked on page 1 within 2 weeks!",             "sentiment": "positive", "response_sent": True},
    {"id": 3,  "buyer": "coffee_brand",    "gig": "Social Media Pack",      "rating": 4, "review": "Great work overall. Could have included more variety but solid quality.", "sentiment": "positive", "response_sent": False},
    {"id": 4,  "buyer": "researcher_bob",  "gig": "Data Entry Task",        "rating": 5, "review": "Fast, accurate, and professional. Will order again!",                    "sentiment": "positive", "response_sent": False},
    {"id": 5,  "buyer": "intl_docs_inc",   "gig": "Spanish Translation",    "rating": 5, "review": "Perfect translation. Native-level Spanish with no errors.",              "sentiment": "positive", "response_sent": True},
    {"id": 6,  "buyer": "realtor_mike",    "gig": "Business Card Design",   "rating": 4, "review": "Nice design but needed a few revisions. Good communication.",            "sentiment": "positive", "response_sent": False},
    {"id": 7,  "buyer": "ad_agency_x",     "gig": "Google Ads Setup",       "rating": 5, "review": "ROAS doubled after the campaign setup. Incredible work!",                "sentiment": "positive", "response_sent": False},
    {"id": 8,  "buyer": "podcast_host",    "gig": "Voice Over",             "rating": 5, "review": "Clear, professional voice. Got it on the first try!",                    "sentiment": "positive", "response_sent": True},
    {"id": 9,  "buyer": "influencer_99",   "gig": "Instagram Content",      "rating": 4, "review": "Good content but some captions felt generic. Would order again.",        "sentiment": "neutral",  "response_sent": False},
    {"id": 10, "buyer": "retailer_mark",   "gig": "Mailchimp Setup",        "rating": 5, "review": "Open rates went up 40% after the new template. Amazing results!",        "sentiment": "positive", "response_sent": False},
    {"id": 11, "buyer": "finance_co",      "gig": "PowerPoint Deck",        "rating": 5, "review": "The deck was professional and polished. Loved the design.",              "sentiment": "positive", "response_sent": True},
    {"id": 12, "buyer": "brand_kit_buyer", "gig": "Social Media Kit",       "rating": 4, "review": "Kit was good. Needed some tweaks but seller was responsive.",            "sentiment": "positive", "response_sent": False},
    {"id": 13, "buyer": "dev_team_xyz",    "gig": "Bug Fix Service",        "rating": 5, "review": "Found and fixed 3 bugs in under an hour. Super fast!",                   "sentiment": "positive", "response_sent": False},
    {"id": 14, "buyer": "coach_emma",      "gig": "Ebook Creation",         "rating": 5, "review": "Beautiful ebook with great layout. My clients love it!",                 "sentiment": "positive", "response_sent": True},
    {"id": 15, "buyer": "seo_agency_v",    "gig": "Keyword Research",       "rating": 3, "review": "The research was okay but I expected more in-depth analysis.",            "sentiment": "neutral",  "response_sent": False},
    {"id": 16, "buyer": "new_brand_co",    "gig": "About Us Page",          "rating": 5, "review": "Captures our brand voice perfectly! Better than expected.",               "sentiment": "positive", "response_sent": False},
    {"id": 17, "buyer": "home_decor_shop", "gig": "Pinterest Management",   "rating": 4, "review": "Follower count grew by 500 in 2 weeks. Decent results.",                 "sentiment": "positive", "response_sent": False},
    {"id": 18, "buyer": "ecom_store_amy",  "gig": "Product Descriptions",   "rating": 5, "review": "Conversion rate improved after updating product pages. Great job!",      "sentiment": "positive", "response_sent": True},
    {"id": 19, "buyer": "small_biz_jane",  "gig": "WordPress Site",         "rating": 5, "review": "Stunning website! Delivered ahead of schedule. 5 stars!",                "sentiment": "positive", "response_sent": False},
    {"id": 20, "buyer": "saas_founder",    "gig": "Explainer Video",        "rating": 4, "review": "Good video. Took one revision but the final result was excellent.",      "sentiment": "positive", "response_sent": False},
    {"id": 21, "buyer": "fashion_brand",   "gig": "Shopify Store",          "rating": 5, "review": "The store looks amazing and is easy to manage. Highly recommend!",       "sentiment": "positive", "response_sent": True},
    {"id": 22, "buyer": "job_seeker_2025", "gig": "Resume Writing",         "rating": 5, "review": "Got 3 interview calls within a week of using this resume!",              "sentiment": "positive", "response_sent": False},
    {"id": 23, "buyer": "gamer_youtuber",  "gig": "YouTube Intro",          "rating": 4, "review": "Looks great! Would have liked more color options initially.",             "sentiment": "positive", "response_sent": False},
    {"id": 24, "buyer": "bizops_lead",     "gig": "Python Automation",      "rating": 5, "review": "Saved us 20 hours per week with this automation. Worth every penny!",    "sentiment": "positive", "response_sent": True},
    {"id": 25, "buyer": "startup_cto",     "gig": "FastAPI Backend",        "rating": 5, "review": "Excellent code quality with full documentation. Highly recommend!",      "sentiment": "positive", "response_sent": False},
    {"id": 26, "buyer": "app_startup_x",   "gig": "React Native App",       "rating": 5, "review": "Delivered a fully functional app with clean code and on time!",          "sentiment": "positive", "response_sent": False},
    {"id": 27, "buyer": "author_lisa",     "gig": "Manuscript Editing",     "rating": 4, "review": "Good editing work. Caught most errors but missed a few minor ones.",     "sentiment": "positive", "response_sent": False},
    {"id": 28, "buyer": "ecom_cmo",        "gig": "Chatbot Dev",            "rating": 5, "review": "Chatbot increased customer engagement by 30%. Fantastic work!",          "sentiment": "positive", "response_sent": True},
    {"id": 29, "buyer": "seo_blogger",     "gig": "Guest Blog Posts",       "rating": 4, "review": "Well-written posts. One needed a rewrite but overall great quality.",    "sentiment": "positive", "response_sent": False},
    {"id": 30, "buyer": "exec_coach_tom",  "gig": "LinkedIn Profile",       "rating": 5, "review": "Profile looks world-class. Connections and opportunities have increased.", "sentiment": "positive", "response_sent": True},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "max_reviews": 10,   "auto_request": False, "ai_responses": False},
    "PRO":        {"price_usd": 29,  "max_reviews": 100,  "auto_request": True,  "ai_responses": False},
    "ENTERPRISE": {"price_usd": 99,  "max_reviews": None, "auto_request": True,  "ai_responses": True},
}


class FiverrReviewGeneratorBot:
    """Manages review requests, sentiment analysis, and AI-generated responses.

    Competes with RepuGen and BirdEye by providing Fiverr-specific review
    management with AI response generation.
    Monetization: $29/month PRO or $99/month ENTERPRISE subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="FiverrReviewGeneratorBot")

    def _get_reviews(self) -> list[dict]:
        limit = self._config["max_reviews"]
        return EXAMPLES[:limit] if limit else EXAMPLES

    def get_all_reviews(self) -> list[dict]:
        """Return all reviews within tier limit."""
        return self._get_reviews()

    def get_reviews_by_rating(self, rating: int) -> list[dict]:
        """Return reviews filtered by star rating (1-5)."""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5.")
        return [r for r in self._get_reviews() if r["rating"] == rating]

    def get_reviews_by_sentiment(self, sentiment: str) -> list[dict]:
        """Return reviews filtered by sentiment: positive, neutral, negative."""
        valid = {"positive", "neutral", "negative"}
        if sentiment not in valid:
            raise ValueError(f"Invalid sentiment. Choose from {valid}")
        return [r for r in self._get_reviews() if r["sentiment"] == sentiment]

    def get_average_rating(self) -> float:
        """Return the average star rating across all available reviews."""
        reviews = self._get_reviews()
        if not reviews:
            return 0.0
        return round(sum(r["rating"] for r in reviews) / len(reviews), 2)

    def get_rating_distribution(self) -> dict[int, int]:
        """Return count of reviews per star rating."""
        distribution: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in self._get_reviews():
            distribution[r["rating"]] += 1
        return distribution

    def get_pending_responses(self) -> list[dict]:
        """Return reviews that have not yet received a response."""
        return [r for r in self._get_reviews() if not r["response_sent"]]

    def send_review_request(self, buyer: str, gig: str) -> dict:
        """Send an automated review request to a buyer (PRO/ENTERPRISE)."""
        if not self._config["auto_request"]:
            raise PermissionError(
                "Auto review requests require PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        message = (
            f"Hi {buyer}, thank you for ordering '{gig}'! "
            "I hope you're happy with the results. "
            "A quick review would mean a lot and help other buyers. 🙏"
        )
        return {"sent": True, "buyer": buyer, "gig": gig, "message": message}

    def generate_response(self, review_id: int) -> str:
        """Generate an AI-powered response to a review (ENTERPRISE only)."""
        if not self._config["ai_responses"]:
            raise PermissionError(
                "AI response generation requires ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        review = next((r for r in EXAMPLES if r["id"] == review_id), None)
        if review is None:
            raise ValueError(f"Review ID {review_id} not found.")
        if review["sentiment"] == "positive":
            return (
                f"Thank you so much for the wonderful review, {review['buyer']}! "
                f"It was a pleasure working on your {review['gig']} project. "
                "Looking forward to our next collaboration! 😊"
            )
        if review["sentiment"] == "neutral":
            return (
                f"Thank you for your honest feedback, {review['buyer']}. "
                "I appreciate your input and will use it to improve my services. "
                "Please reach out if you'd like any revisions!"
            )
        return (
            f"I'm sorry to hear you weren't fully satisfied, {review['buyer']}. "
            "Please message me directly and I'll do my best to make it right."
        )

    def get_review_summary(self) -> dict:
        """Return a comprehensive review summary."""
        reviews = self._get_reviews()
        return {
            "total_reviews": len(reviews),
            "average_rating": self.get_average_rating(),
            "rating_distribution": self.get_rating_distribution(),
            "sentiment_breakdown": {
                "positive": len(self.get_reviews_by_sentiment("positive")),
                "neutral": len(self.get_reviews_by_sentiment("neutral")),
                "negative": len(self.get_reviews_by_sentiment("negative")),
            },
            "pending_responses": len(self.get_pending_responses()),
            "tier": self.tier,
        }

    def describe_tier(self) -> str:
        cfg = self._config
        limit = cfg["max_reviews"] if cfg["max_reviews"] else "unlimited"
        lines = [
            f"=== FiverrReviewGeneratorBot — {self.tier} Tier ===",
            f"  Monthly price   : ${cfg['price_usd']}/month",
            f"  Max reviews     : {limit}",
            f"  Auto requests   : {'enabled' if cfg['auto_request'] else 'disabled'}",
            f"  AI responses    : {'enabled' if cfg['ai_responses'] else 'disabled (ENTERPRISE)'}",
        ]
        return "\n".join(lines)

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "fiverr_review_management", "reviews_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {"pipeline_complete": result.get("pipeline_complete"), "summary": self.get_review_summary()}


if __name__ == "__main__":
    bot = FiverrReviewGeneratorBot(tier="PRO")
    summary = bot.get_review_summary()
    print(f"Average rating: {summary['average_rating']} ⭐")
    print(f"Pending responses: {summary['pending_responses']}")
    print(f"5-star reviews: {summary['rating_distribution'][5]}")
    print(bot.describe_tier())

ReviewCollectorBot = FiverrReviewGeneratorBot


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


class FiverrReviewGeneratorBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


_orig_fiverrreviewgenerator_bot_init = FiverrReviewGeneratorBot.__init__


def _fiverrreviewgenerator_bot_new_init(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_fiverrreviewgenerator_bot_init(self, tier_val.upper())
    self.tier = Tier(tier_val)


FiverrReviewGeneratorBot.__init__ = _fiverrreviewgenerator_bot_new_init
FiverrReviewGeneratorBot.RESULT_LIMITS = {"free": 5, "pro": 25, "enterprise": 100}


def _fiverrreviewgenerator_bot_monthly_price(self):
    return _TIER_MONTHLY_PRICE[self.tier.value]


def _fiverrreviewgenerator_bot_get_tier_info(self):
    return {
        "tier": self.tier.value,
        "monthly_price_usd": self.monthly_price(),
        "result_limit": self.RESULT_LIMITS[self.tier.value],
    }


def _fiverrreviewgenerator_bot_enforce_tier(self, required_value):
    order = ["free", "pro", "enterprise"]
    if order.index(self.tier.value) < order.index(required_value):
        raise FiverrReviewGeneratorBotTierError(
            f"{required_value.upper()} tier required. Current: {self.tier.value}"
        )


def _fiverrreviewgenerator_bot_list_items(self, limit=None):
    cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
    return _random_tier.sample(EXAMPLES, min(cap, len(EXAMPLES)))


def _fiverrreviewgenerator_bot_analyze(self):
    self._enforce_tier("pro")
    return {"bot": "FiverrReviewGeneratorBot", "tier": self.tier.value, "count": len(EXAMPLES)}


def _fiverrreviewgenerator_bot_export_report(self):
    self._enforce_tier("enterprise")
    return {"bot": "FiverrReviewGeneratorBot", "tier": self.tier.value, "total_items": len(EXAMPLES), "items": EXAMPLES}


FiverrReviewGeneratorBot.monthly_price = _fiverrreviewgenerator_bot_monthly_price
FiverrReviewGeneratorBot.get_tier_info = _fiverrreviewgenerator_bot_get_tier_info
FiverrReviewGeneratorBot._enforce_tier = _fiverrreviewgenerator_bot_enforce_tier
FiverrReviewGeneratorBot.list_items = _fiverrreviewgenerator_bot_list_items
FiverrReviewGeneratorBot.analyze = _fiverrreviewgenerator_bot_analyze
FiverrReviewGeneratorBot.export_report = _fiverrreviewgenerator_bot_export_report
