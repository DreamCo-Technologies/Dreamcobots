"""
Virality Engine — campaign management and viral content generation for the
DreamCo Influencer Bot.

Handles creating and tracking viral campaigns, generating content ideas,
and computing viral scores.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import uuid
from typing import List

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Campaign type constants
# ---------------------------------------------------------------------------

CAMPAIGN_CHALLENGE = "CHALLENGE"
CAMPAIGN_PRODUCT_LAUNCH = "PRODUCT_LAUNCH"
CAMPAIGN_EDUCATION_SERIES = "EDUCATION_SERIES"
CAMPAIGN_GIVEAWAY = "GIVEAWAY"
CAMPAIGN_COLLAB_SERIES = "COLLAB_SERIES"

CAMPAIGN_TYPES: List[str] = [
    CAMPAIGN_CHALLENGE,
    CAMPAIGN_PRODUCT_LAUNCH,
    CAMPAIGN_EDUCATION_SERIES,
    CAMPAIGN_GIVEAWAY,
    CAMPAIGN_COLLAB_SERIES,
]

# ---------------------------------------------------------------------------
# Content type constants
# ---------------------------------------------------------------------------

CONTENT_POST = "POST"
CONTENT_STORY = "STORY"
CONTENT_VIDEO_SCRIPT = "VIDEO_SCRIPT"
CONTENT_BOT_SHOWCASE = "BOT_SHOWCASE"


class ViralityEngine:
    """Manages viral campaigns and content generation for influencer bots."""

    def __init__(self) -> None:
        self._campaigns: dict = {}

    # ------------------------------------------------------------------
    # Campaign lifecycle
    # ------------------------------------------------------------------

    def create_campaign(
        self,
        partnership_id: str,
        campaign_type: str,
        title: str,
        description: str,
        duration_days: int,
    ) -> dict:
        """Create a new viral campaign.

        Parameters
        ----------
        partnership_id : str
            ID of the brand partnership driving this campaign.
        campaign_type : str
            One of the CAMPAIGN_TYPES constants.
        title : str
            Campaign title.
        description : str
            Campaign description.
        duration_days : int
            Planned duration of the campaign in days.

        Returns
        -------
        dict
            Campaign record with generated campaign_id and DRAFT status.

        Raises
        ------
        ValueError
            If campaign_type is not a valid CAMPAIGN_TYPES value.
        """
        if campaign_type not in CAMPAIGN_TYPES:
            raise ValueError(
                f"Invalid campaign_type '{campaign_type}'. "
                f"Must be one of: {CAMPAIGN_TYPES}"
            )
        campaign_id = f"cmp_{uuid.uuid4().hex[:10]}"
        record = {
            "campaign_id": campaign_id,
            "partnership_id": partnership_id,
            "campaign_type": campaign_type,
            "title": title,
            "description": description,
            "duration_days": duration_days,
            "status": "DRAFT",
            "metrics": {
                "views": 0,
                "shares": 0,
                "conversions": 0,
                "viral_score": 0.0,
            },
        }
        self._campaigns[campaign_id] = record
        return record

    def launch_campaign(self, campaign_id: str) -> dict:
        """Set campaign status to ACTIVE.

        Parameters
        ----------
        campaign_id : str
            ID of an existing campaign.

        Returns
        -------
        dict
            Updated campaign record.

        Raises
        ------
        ValueError
            If the campaign_id does not exist.
        """
        campaign = self._campaigns.get(campaign_id)
        if campaign is None:
            raise ValueError(f"Campaign '{campaign_id}' not found.")
        campaign["status"] = "ACTIVE"
        return campaign

    def track_campaign(self, campaign_id: str) -> dict:
        """Return current metrics for a campaign.

        Simulates realistic metrics based on campaign type and status.

        Parameters
        ----------
        campaign_id : str
            ID of an existing campaign.

        Returns
        -------
        dict
            Metrics dict with views, shares, conversions, and viral_score.

        Raises
        ------
        ValueError
            If the campaign_id does not exist.
        """
        campaign = self._campaigns.get(campaign_id)
        if campaign is None:
            raise ValueError(f"Campaign '{campaign_id}' not found.")

        metrics = campaign["metrics"]

        # Simulate metric growth when campaign is ACTIVE
        if campaign["status"] == "ACTIVE":
            base_views = {
                CAMPAIGN_CHALLENGE: 150_000,
                CAMPAIGN_PRODUCT_LAUNCH: 80_000,
                CAMPAIGN_EDUCATION_SERIES: 40_000,
                CAMPAIGN_GIVEAWAY: 200_000,
                CAMPAIGN_COLLAB_SERIES: 120_000,
            }.get(campaign["campaign_type"], 50_000)

            views = base_views * campaign["duration_days"]
            shares = int(views * 0.05)
            conversions = int(views * 0.02)
            viral_score = self.calculate_viral_score(views, shares, conversions)

            metrics["views"] = views
            metrics["shares"] = shares
            metrics["conversions"] = conversions
            metrics["viral_score"] = viral_score

        return {
            "campaign_id": campaign_id,
            "title": campaign["title"],
            "status": campaign["status"],
            "views": metrics["views"],
            "shares": metrics["shares"],
            "conversions": metrics["conversions"],
            "viral_score": metrics["viral_score"],
        }

    # ------------------------------------------------------------------
    # Content generation
    # ------------------------------------------------------------------

    def generate_viral_content(self, partnership_id: str, content_type: str) -> dict:
        """Generate a viral content idea for an influencer partnership.

        Parameters
        ----------
        partnership_id : str
            ID of the brand partnership.
        content_type : str
            One of POST, STORY, VIDEO_SCRIPT, BOT_SHOWCASE.

        Returns
        -------
        dict
            Content definition including hook, body, call_to_action.

        Raises
        ------
        ValueError
            If content_type is not recognised.
        """
        valid_types = [CONTENT_POST, CONTENT_STORY, CONTENT_VIDEO_SCRIPT, CONTENT_BOT_SHOWCASE]
        if content_type not in valid_types:
            raise ValueError(
                f"Invalid content_type '{content_type}'. Must be one of: {valid_types}"
            )

        templates = {
            CONTENT_POST: {
                "content_type": CONTENT_POST,
                "partnership_id": partnership_id,
                "hook": "🚀 Big news — my new AI-powered bot is live!",
                "body": (
                    "I've teamed up with DreamCo to create a personalised bot just for "
                    "my community. It answers your questions, shares exclusive content, "
                    "and gives you the inside track on everything I love."
                ),
                "call_to_action": "Tap the link in bio to try it FREE today! 👇",
                "suggested_hashtags": ["#AIBot", "#InfluencerBot", "#DreamCo", "#CoLab"],
            },
            CONTENT_STORY: {
                "content_type": CONTENT_STORY,
                "partnership_id": partnership_id,
                "hook": "Swipe up ⬆️ to meet my new AI bot!",
                "body": "24/7 access to personalised tips, content & deals. It's like having me in your pocket.",
                "call_to_action": "Link in bio — try it for free!",
                "sticker_suggestion": "Poll: Would you use my AI bot? YES / ALREADY AM 🔥",
            },
            CONTENT_VIDEO_SCRIPT: {
                "content_type": CONTENT_VIDEO_SCRIPT,
                "partnership_id": partnership_id,
                "hook": "What if I could reply to EVERY single one of you?",
                "body": (
                    "[Show phone screen] I built an AI version of myself — powered by DreamCo. "
                    "It knows my training programmes, my favourite recipes, my travel hacks. "
                    "Ask it anything. It replies instantly, 24/7."
                ),
                "call_to_action": "Link below — first 1000 sign-ups get PRO free for a month. GO!",
                "estimated_duration_seconds": 45,
            },
            CONTENT_BOT_SHOWCASE: {
                "content_type": CONTENT_BOT_SHOWCASE,
                "partnership_id": partnership_id,
                "hook": "Here's what my AI bot can actually do 👀",
                "body": (
                    "Demo reel: ask the bot for a workout plan → instant response. "
                    "Ask for a recipe → personalised to your goals. "
                    "Ask for a product recommendation → curated just for you."
                ),
                "call_to_action": "Try it yourself — free link in bio!",
                "demo_features": [
                    "Personalised recommendations",
                    "24/7 Q&A with influencer knowledge base",
                    "Exclusive community content",
                    "Campaign access & giveaway entry",
                ],
            },
        }
        return templates[content_type]

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def calculate_viral_score(self, views: int, shares: int, conversions: int) -> float:
        """Compute a viral score between 0 and 100.

        Formula weights shares heavily (primary virality signal), then
        conversions (intent signal), then raw views (reach signal).

        Parameters
        ----------
        views : int
        shares : int
        conversions : int

        Returns
        -------
        float
            Score in the range [0, 100].
        """
        if views <= 0:
            return 0.0

        share_rate = shares / views
        conversion_rate = conversions / views

        # Weighted sum — normalised to 0-100
        raw = (share_rate * 60) + (conversion_rate * 30) + min(views / 1_000_000, 1.0) * 10
        return round(min(raw * 100, 100.0), 2)
