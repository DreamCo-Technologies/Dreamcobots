"""Ad Copy Generator Bot — tier-aware ad copy creation and A/B testing."""
import sys, os
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.ad_copy_generator_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


ALL_PLATFORMS = ["google", "facebook", "instagram", "linkedin", "twitter", "tiktok"]
PLATFORM_LIMITS = {
    Tier.FREE: ["google", "facebook"],
    Tier.PRO: ALL_PLATFORMS,
    Tier.ENTERPRISE: ALL_PLATFORMS,
}

PLATFORM_SPECS = {
    "google": {"headline_chars": 30, "description_chars": 90, "format": "text", "extensions": ["sitelinks", "callouts"]},
    "facebook": {"headline_chars": 40, "body_chars": 125, "format": "image/video", "aspect_ratio": "1.91:1 or 1:1"},
    "instagram": {"caption_chars": 2200, "hashtag_limit": 30, "format": "image/video/carousel", "aspect_ratio": "1:1 or 4:5"},
    "linkedin": {"headline_chars": 70, "body_chars": 600, "format": "image/video/document", "audience": "professional"},
    "twitter": {"tweet_chars": 280, "format": "image/video/text", "hashtag_recommendation": "1-2"},
    "tiktok": {"caption_chars": 150, "format": "vertical video", "duration": "15-60 seconds"},
}


class AdCopyGeneratorBot:
    """Tier-aware ad copy generator bot."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.flow = GlobalAISourcesFlow(bot_name="AdCopyGeneratorBot")

    def generate_ad(self, product: str, platform: str, target_audience: str, goal: str = "conversion") -> dict:
        if platform not in PLATFORM_LIMITS[self.tier]:
            raise PermissionError(f"Platform '{platform}' not available on {self.tier.value} tier")
        headline = f"Transform Your {product} Experience Today"
        body = f"Discover why {target_audience} love {product}. {random.choice(['Limited time offer', 'Join thousands of satisfied customers', 'Start your free trial'])}"
        return {
            "product": product,
            "platform": platform,
            "target_audience": target_audience,
            "goal": goal,
            "headline": headline,
            "body": body,
            "cta": random.choice(["Shop Now", "Learn More", "Get Started", "Sign Up", "Buy Now"]),
            "character_count": {"headline": len(headline), "body": 80},
            "tier_used": self.tier.value,
        }

    def create_ab_variants(self, base_ad: dict, num_variants: int = 3) -> list:
        if self.tier == Tier.FREE:
            raise PermissionError("A/B variants require PRO or ENTERPRISE tier")
        variants = []
        for i in range(num_variants):
            variant = {
                **base_ad,
                "variant_id": f"variant_{i+1}",
                "headline": f"Variant {i+1}: {base_ad.get('headline', '')}",
                "cta": random.choice(["Shop Now", "Learn More", "Get Started", "Try Free"]),
            }
            variants.append(variant)
        return variants

    def estimate_ctr(self, ad_dict: dict) -> dict:
        return {
            "estimated_ctr_percent": round(random.uniform(0.5, 5.0), 2),
            "confidence": random.choice(["high", "medium", "low"]),
            "factors": ["platform engagement rate", "audience targeting precision", "creative quality score"],
            "tier_used": self.tier.value,
        }

    def get_platform_specs(self, platform: str) -> dict:
        return PLATFORM_SPECS.get(platform, {})

    def run(self) -> dict:
        return self.flow.run_pipeline(
            raw_data={"bot": "AdCopyGeneratorBot", "tier": self.tier.value},
            learning_method="supervised",
        )
