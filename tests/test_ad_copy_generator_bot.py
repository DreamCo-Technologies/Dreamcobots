"""Tests for bots/ad_copy_generator_bot"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.ad_copy_generator_bot.ad_copy_generator_bot import AdCopyGeneratorBot
from bots.ad_copy_generator_bot.tiers import BOT_FEATURES, get_bot_tier_info


class TestAdCopyGeneratorBotInstantiation:
    def test_default_tier_is_free(self):
        bot = AdCopyGeneratorBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = AdCopyGeneratorBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = AdCopyGeneratorBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE


class TestGenerateAd:
    def test_free_can_use_google(self):
        bot = AdCopyGeneratorBot()
        result = bot.generate_ad("Widget", "google", "entrepreneurs")
        assert result["platform"] == "google"

    def test_free_can_use_facebook(self):
        bot = AdCopyGeneratorBot()
        result = bot.generate_ad("Widget", "facebook", "marketers")
        assert result["platform"] == "facebook"

    def test_free_cannot_use_instagram(self):
        bot = AdCopyGeneratorBot()
        with pytest.raises(PermissionError):
            bot.generate_ad("Widget", "instagram", "users")

    def test_free_cannot_use_linkedin(self):
        bot = AdCopyGeneratorBot()
        with pytest.raises(PermissionError):
            bot.generate_ad("Widget", "linkedin", "professionals")

    def test_pro_can_use_all_platforms(self):
        bot = AdCopyGeneratorBot(tier=Tier.PRO)
        for platform in ["google", "facebook", "instagram", "linkedin", "twitter", "tiktok"]:
            result = bot.generate_ad("Widget", platform, "users")
            assert result["platform"] == platform

    def test_generate_ad_has_required_keys(self):
        bot = AdCopyGeneratorBot()
        result = bot.generate_ad("Widget", "google", "users")
        for key in ["product", "platform", "headline", "body", "cta", "tier_used"]:
            assert key in result

    def test_ad_headline_contains_product(self):
        bot = AdCopyGeneratorBot()
        result = bot.generate_ad("CloudSync", "google", "teams")
        assert "CloudSync" in result["headline"]


class TestAbVariants:
    def test_ab_variants_raises_on_free(self):
        bot = AdCopyGeneratorBot()
        ad = bot.generate_ad("Widget", "google", "users")
        with pytest.raises(PermissionError):
            bot.create_ab_variants(ad)

    def test_ab_variants_works_on_pro(self):
        bot = AdCopyGeneratorBot(tier=Tier.PRO)
        ad = bot.generate_ad("Widget", "google", "users")
        variants = bot.create_ab_variants(ad, num_variants=3)
        assert len(variants) == 3

    def test_ab_variants_have_variant_id(self):
        bot = AdCopyGeneratorBot(tier=Tier.PRO)
        ad = bot.generate_ad("Widget", "facebook", "users")
        variants = bot.create_ab_variants(ad, num_variants=2)
        assert variants[0]["variant_id"] == "variant_1"
        assert variants[1]["variant_id"] == "variant_2"


class TestCtrEstimation:
    def test_estimate_ctr_returns_dict(self):
        bot = AdCopyGeneratorBot()
        ad = bot.generate_ad("Widget", "google", "users")
        result = bot.estimate_ctr(ad)
        assert "estimated_ctr_percent" in result
        assert "confidence" in result

    def test_ctr_is_in_valid_range(self):
        bot = AdCopyGeneratorBot()
        ad = bot.generate_ad("Widget", "google", "users")
        result = bot.estimate_ctr(ad)
        assert 0.0 <= result["estimated_ctr_percent"] <= 10.0


class TestPlatformSpecs:
    def test_get_platform_specs_google(self):
        bot = AdCopyGeneratorBot()
        specs = bot.get_platform_specs("google")
        assert "headline_chars" in specs

    def test_get_platform_specs_unknown(self):
        bot = AdCopyGeneratorBot()
        specs = bot.get_platform_specs("unknown_platform")
        assert specs == {}


class TestAdCopyBotTiers:
    def test_bot_features_has_all_tiers(self):
        assert Tier.FREE.value in BOT_FEATURES
        assert Tier.PRO.value in BOT_FEATURES
        assert Tier.ENTERPRISE.value in BOT_FEATURES

    def test_pro_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_run_returns_pipeline_complete(self):
        bot = AdCopyGeneratorBot()
        result = bot.run()
        assert result.get("pipeline_complete") is True
