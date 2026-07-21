"""Social Media Manager Bot — tier-aware social media post creation and scheduling."""
import sys, os
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.social_media_manager_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


ALL_PLATFORMS = ["instagram", "twitter", "linkedin", "facebook", "tiktok", "youtube"]
PLATFORM_LIMITS = {
    Tier.FREE: ["instagram"],
    Tier.PRO: ["instagram", "twitter", "linkedin", "facebook", "tiktok"],
    Tier.ENTERPRISE: ALL_PLATFORMS,
}


class SocialMediaManagerBot:
    """Tier-aware social media management bot."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.flow = GlobalAISourcesFlow(bot_name="SocialMediaManagerBot")

    def create_post(self, platform: str, topic: str, tone: str = "professional", include_hashtags: bool = True) -> dict:
        if platform not in PLATFORM_LIMITS[self.tier]:
            raise PermissionError(f"Platform '{platform}' not available on {self.tier.value} tier")
        caption = f"Exciting update about {topic}! {random.choice(['Stay tuned', 'Learn more', 'Check it out', 'Join us'])}"
        hashtags = [f"#{topic.replace(' ', '')}", "#business", "#growth"] if include_hashtags else []
        return {
            "platform": platform,
            "topic": topic,
            "tone": tone,
            "caption": caption,
            "hashtags": hashtags,
            "estimated_reach": random.randint(100, 10000),
            "best_time_to_post": random.choice(["9:00 AM", "12:00 PM", "6:00 PM", "8:00 PM"]),
            "media_suggestion": random.choice(["high-quality photo", "infographic", "short video", "carousel"]),
            "tier_used": self.tier.value,
        }

    def schedule_content(self, platform: str, posts_per_week: int = 3) -> dict:
        if platform not in PLATFORM_LIMITS[self.tier]:
            raise PermissionError(f"Platform '{platform}' not available on {self.tier.value} tier")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        calendar = [
            {
                "day": days[i % 7],
                "time": random.choice(["9:00 AM", "12:00 PM", "6:00 PM"]),
                "topic_suggestion": random.choice(["Product highlight", "Customer story", "Industry tip", "Behind the scenes"]),
                "content_type": random.choice(["image", "video", "carousel", "story"]),
            }
            for i in range(posts_per_week)
        ]
        return {
            "platform": platform,
            "posts_per_week": posts_per_week,
            "calendar": calendar,
            "tier_used": self.tier.value,
        }

    def get_hashtag_suggestions(self, topic: str, platform: str) -> list:
        if self.tier == Tier.FREE:
            raise PermissionError("Hashtag suggestions require PRO or ENTERPRISE tier")
        base = topic.replace(" ", "")
        return [
            f"#{base}", "#trending", "#viral", "#business", "#growth",
            "#marketing", "#digital", "#brand", f"#{base}tips", "#community",
        ]

    def analyze_engagement(self, platform: str, post_id: str) -> dict:
        return {
            "post_id": post_id,
            "platform": platform,
            "likes": random.randint(10, 5000),
            "comments": random.randint(1, 200),
            "shares": random.randint(0, 500),
            "reach": random.randint(500, 50000),
            "impressions": random.randint(1000, 100000),
            "engagement_rate": round(random.uniform(1.0, 8.0), 2),
            "tier_used": self.tier.value,
        }

    def run(self) -> dict:
        return self.flow.run_pipeline(
            raw_data={"bot": "SocialMediaManagerBot", "tier": self.tier.value},
            learning_method="supervised",
        )
