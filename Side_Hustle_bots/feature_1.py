# Side Hustle Bot – Feature 1: Content Creator Assistant
# Functionality: Helps content creators plan, produce, and monetise digital content.
# Use Cases: YouTubers, podcasters, bloggers scaling their side income.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel


class ContentCreatorBot(BaseBot):
    """
    Side-hustle bot that supports content creators with ideation,
    scheduling, monetisation strategy, and audience growth.

    Sells content performance datasets to creator-economy platforms.
    """

    _CONTENT_IDEAS = {
        "youtube":  ["Tutorial series", "Day-in-the-life vlog", "Product review", "Interview"],
        "podcast":  ["Expert interview", "Solo deep-dive", "Q&A episode", "Case study"],
        "blog":     ["How-to guide", "Top-10 list", "Opinion piece", "Case study"],
        "tiktok":   ["Behind-the-scenes", "Quick tip", "Trending audio skit", "Challenge"],
    }

    def __init__(self):
        super().__init__(
            name="Content Creator Bot",
            domain="creator_economy",
            category="side_hustle",
        )

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Creator Economy Performance Dataset",
            description="Engagement and revenue data from 100K content creators across 4 platforms.",
            domain="creator_economy",
            size_mb=210.0,
            price_usd=249.00,
            license="CC-BY-4.0",
            tags=["content", "creator", "YouTube", "monetisation", "engagement"],
            ethical_review_passed=True,
        )

    def _setup_plans(self):
        super()._setup_plans()
        self.monetization.add_plan(PricingPlan(
            plan_id="creator_pro",
            name="Creator Pro",
            model=PricingModel.SUBSCRIPTION,
            price_usd=19.99,
            description="Unlimited content ideas, scheduling, and analytics.",
            features=["Unlimited ideas", "Content calendar", "Monetisation tips", "Dataset access"],
        ))

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        tokens = set(nlp_result.get("tokens", []))
        prefix = self._emotion_prefix()

        platform_ideas = None
        for platform, ideas in self._CONTENT_IDEAS.items():
            if platform in tokens:
                platform_ideas = (platform, ideas)
                break

        if intent == "greeting":
            response = (
                f"{prefix}Hey creator! 🎬 I'm {self.name}. "
                "I'll help you grow your audience and monetise your content. "
                "Which platform are you focusing on?"
            )
        elif intent == "help":
            platforms = ", ".join(self._CONTENT_IDEAS.keys())
            response = (
                f"I can help with: 💡 Content ideas  |  📅 Content calendar  |  "
                f"💰 Monetisation strategy  |  Platforms: {platforms}."
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer creator economy performance datasets."
                + self._dataset_offer()
            )
        elif platform_ideas:
            platform, ideas = platform_ideas
            idea_list = "  •  ".join(ideas)
            response = (
                f"{prefix}Great {platform.title()} content ideas: {idea_list}. "
                "Which angle resonates with your audience?"
            )
        else:
            response = (
                f"{prefix}Let's grow your content business! "
                "Share your niche and audience size and I'll suggest a content strategy."
            )
        return response


if __name__ == "__main__":
    bot = ContentCreatorBot()
    print(bot.chat("Hi! I run a YouTube channel about personal finance."))
    print(bot.chat("I need content ideas for YouTube this week."))
    print(bot.status())
