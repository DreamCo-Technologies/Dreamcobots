"""
Dreamcobots SocialMediaBot — tier-aware social media scheduling and analytics.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.social_media_bot.tiers import SOCIAL_MEDIA_FEATURES, get_social_media_tier_info
import uuid
from datetime import datetime


class SocialMediaBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class SocialMediaBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class SocialMediaBot:
    """Tier-aware social media scheduling and analytics bot."""

    POST_LIMITS = {
        "free": 10,
        "pro": 200,
        "enterprise": None,
    }

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._accounts: list[str] = []
        self._posts: list[dict] = []
        self._posts_this_month: int = 0

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise SocialMediaBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _check_post_limit(self) -> None:
        limit = self.POST_LIMITS[self.tier.value]
        if limit is not None and self._posts_this_month >= limit:
            raise SocialMediaBotRequestLimitError(
                f"Monthly post limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _check_feature(self, feature: str) -> None:
        features = SOCIAL_MEDIA_FEATURES[self.tier.value]
        if not any(feature.lower() in f.lower() for f in features):
            raise SocialMediaBotTierError(
                f"'{feature}' is not available on the {self.config.name} tier. "
                f"Please upgrade to access this feature."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))

    def schedule_post(self, post: dict) -> dict:
        """
        Schedule a social media post.

        Args:
            post: {"content": str, "platform": str, "scheduled_time": str optional}

        Returns:
            {"post_id": str, "platform": str, "scheduled_time": str, "status": str, "tier": str}
        """
        self._check_request_limit()
        self._check_post_limit()
        self._request_count += 1

        content = post.get("content", "")
        platform = post.get("platform", "twitter")
        scheduled_time = post.get("scheduled_time", datetime.now().isoformat())

        if self.tier == Tier.FREE:
            # FREE tier: only 1 platform (raise an error if a list is passed)
            if isinstance(platform, list) and len(platform) > 1:
                raise SocialMediaBotTierError(
                    "Multi-platform posting is not available on the Free tier. "
                    "Please upgrade to PRO or ENTERPRISE."
                )

        post_id = str(uuid.uuid4())
        record = {
            "post_id": post_id,
            "platform": platform,
            "scheduled_time": scheduled_time,
            "status": "scheduled",
            "tier": self.tier.value,
        }
        self._posts.append(record)
        self._posts_this_month += 1

        return record

    def analyze_engagement(self, account_id: str) -> dict:
        """
        Analyze engagement metrics for an account.

        Args:
            account_id: The social media account identifier.

        Returns:
            {"account_id": str, "followers": int, "engagement_rate": float,
             "top_posts": list, "tier": str}
        """
        if self.tier == Tier.FREE:
            followers = 100
            engagement_rate = 0.02
            top_posts = [{"post_id": "sample_1", "likes": 5, "shares": 1}]

        elif self.tier == Tier.PRO:
            followers = 1500
            engagement_rate = 0.045
            top_posts = [
                {"post_id": "sample_1", "likes": 120, "shares": 30, "comments": 15},
                {"post_id": "sample_2", "likes": 95, "shares": 20, "comments": 8},
                {"post_id": "sample_3", "likes": 80, "shares": 15, "comments": 12},
            ]

        else:  # ENTERPRISE
            followers = 25000
            engagement_rate = 0.072
            top_posts = [
                {"post_id": "sample_1", "likes": 2100, "shares": 450, "comments": 180, "reach": 45000},
                {"post_id": "sample_2", "likes": 1800, "shares": 380, "comments": 140, "reach": 38000},
                {"post_id": "sample_3", "likes": 1500, "shares": 310, "comments": 120, "reach": 32000},
            ]

        return {
            "account_id": account_id,
            "followers": followers,
            "engagement_rate": engagement_rate,
            "top_posts": top_posts,
            "tier": self.tier.value,
        }

    def generate_hashtags(self, topic: str) -> list:
        """
        Generate relevant hashtags for a topic.

        Args:
            topic: The topic to generate hashtags for.

        Returns:
            List of hashtag strings.
        """
        base_tags = [f"#{topic.replace(' ', '')}", f"#{topic.replace(' ', '')}Tips", f"#DreamcobotsAI"]

        if self.tier == Tier.FREE:
            return base_tags

        elif self.tier == Tier.PRO:
            optimized_tags = base_tags + [
                f"#{topic.replace(' ', '')}Strategy",
                f"#{topic.replace(' ', '')}Growth",
                "#Marketing",
                "#BusinessTips",
                "#DigitalMarketing",
                "#ContentStrategy",
                "#SocialMediaMarketing",
            ]
            return optimized_tags[:10]

        else:  # ENTERPRISE
            ai_tags = base_tags + [
                f"#{topic.replace(' ', '')}Strategy",
                f"#{topic.replace(' ', '')}Growth",
                f"#{topic.replace(' ', '')}Expert",
                f"#{topic.replace(' ', '')}Community",
                "#Marketing",
                "#BusinessTips",
                "#DigitalMarketing",
                "#ContentStrategy",
                "#SocialMediaMarketing",
                "#AIMarketing",
                "#GrowthHacking",
                "#BrandStrategy",
                "#InfluencerMarketing",
                "#ContentCreation",
                "#SocialMediaStrategy",
                "#OnlineMarketing",
                "#DigitalStrategy",
            ]
            return ai_tags[:20]

    def get_stats(self) -> dict:
        return {
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
            "posts_scheduled": len(self._posts),
            "posts_this_month": self._posts_this_month,
            "buddy_integration": True,
        }
