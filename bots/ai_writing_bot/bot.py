"""
Dreamcobots AIWritingBot — tier-aware AI content generation and SEO optimization.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.ai_writing_bot.tiers import AI_WRITING_FEATURES, get_ai_writing_tier_info
import uuid
from datetime import datetime


class AIWritingBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class AIWritingBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class AIWritingBot:
    """Tier-aware AI content generation and SEO optimization bot."""

    WORD_LIMITS = {
        "free": 1000,
        "pro": 50000,
        "enterprise": None,
    }

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._words_used: int = 0
        self._templates: list[dict] = []

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise AIWritingBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _check_word_limit(self, additional_words: int) -> None:
        limit = self.WORD_LIMITS[self.tier.value]
        if limit is not None and self._words_used + additional_words > limit:
            raise AIWritingBotTierError(
                f"Monthly word limit of {limit:,} would be exceeded on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _check_feature(self, feature: str) -> None:
        features = AI_WRITING_FEATURES[self.tier.value]
        if not any(feature.lower() in f.lower() for f in features):
            raise AIWritingBotTierError(
                f"'{feature}' is not available on the {self.config.name} tier. "
                f"Please upgrade to access this feature."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))

    def generate_content(self, request: dict) -> dict:
        """
        Generate content based on the request.

        Args:
            request: {"topic": str, "type": str, "tone": str optional}

        Returns:
            {"content": str, "word_count": int, "seo_score": float, "tier": str}
        """
        self._check_request_limit()
        self._request_count += 1

        topic = request.get("topic", "")
        content_type = request.get("type", "article")
        tone = request.get("tone", "neutral")

        if self.tier == Tier.FREE:
            content = f"Mock content about {topic} in {content_type} format."
            seo_score = 0.5
        elif self.tier == Tier.PRO:
            content = f"Mock content about {topic} in {content_type} format with {tone} tone. This content includes advanced SEO optimization and tone-aware writing."
            seo_score = 0.75
        else:  # ENTERPRISE
            content = (
                f"Mock content about {topic} in {content_type} format with {tone} tone. "
                f"This content is crafted with brand voice training, multi-language support, "
                f"and full SEO optimization. Generated at {datetime.now().isoformat()}."
            )
            seo_score = 0.9

        word_count = len(content.split())
        self._check_word_limit(word_count)
        self._words_used += word_count

        return {
            "content": content,
            "word_count": word_count,
            "seo_score": seo_score,
            "tier": self.tier.value,
        }

    def optimize_seo(self, content: str) -> dict:
        """
        Provide SEO optimization suggestions for content.

        Args:
            content: The content string to optimize.

        Returns:
            {"original_length": int, "suggestions": list, "score": float, "tier": str}
        """
        original_length = len(content)

        if self.tier == Tier.FREE:
            suggestions = ["Add more keywords", "Improve title"]
            score = 0.5
        elif self.tier == Tier.PRO:
            suggestions = [
                "Add more keywords",
                "Improve title",
                "Optimize meta description",
                "Increase internal linking",
                "Improve readability score",
            ]
            score = 0.75
        else:  # ENTERPRISE
            suggestions = [
                "Add more keywords",
                "Improve title",
                "Optimize meta description",
                "Increase internal linking",
                "Improve readability score",
                "Add structured data markup",
                "Optimize for featured snippets",
                "Improve Core Web Vitals signals",
                "Add semantic keyword variations",
                "Optimize for voice search",
            ]
            score = 0.9

        return {
            "original_length": original_length,
            "suggestions": suggestions,
            "score": score,
            "tier": self.tier.value,
        }

    def get_templates(self) -> list:
        """
        Return available content templates for the current tier.

        Returns:
            List of template dicts with "name" and "type" fields.
        """
        if self.tier == Tier.FREE:
            count = 5
        elif self.tier == Tier.PRO:
            count = 50
        else:  # ENTERPRISE
            count = 100

        template_types = ["blog post", "product description", "email", "social media", "landing page",
                          "press release", "case study", "whitepaper", "newsletter", "ad copy"]

        templates = []
        for i in range(count):
            template_type = template_types[i % len(template_types)]
            templates.append({
                "name": f"Template {i + 1}: {template_type.title()}",
                "type": template_type,
            })
        return templates

    def get_stats(self) -> dict:
        return {
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
            "words_used": self._words_used,
            "buddy_integration": True,
        }
