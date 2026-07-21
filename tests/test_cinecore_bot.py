"""Tests for bots/cinecore_bot — DreamCo CineCore AI Commercial System."""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.cinecore_bot.cinecore_bot import (
    CineCoreBot,
    CineCoreBotTierError,
    CineCoreBotError,
    CommercialScript,
    VideoAsset,
    LeadRecord,
    AnalyticsRecord,
    ScriptEngine,
    VideoEngine,
    VoiceEngine,
    PlatformOptimizer,
    LeadEngine,
    BusinessScorer,
    ClosingAgent,
    BillingEngine,
    AnalyticsEngine,
    BulkGenerator,
    SelfHeal,
    CRM,
    SUPPORTED_PLATFORMS,
    SUPPORTED_VOICE_TONES,
    SUPPORTED_GENRES,
)
from bots.cinecore_bot.tiers import BOT_FEATURES, get_bot_tier_info


# ===========================================================================
# Tier definitions
# ===========================================================================

class TestTierDefinitions:
    def test_all_tiers_have_features(self):
        for tier in Tier:
            assert len(BOT_FEATURES[tier.value]) > 0

    def test_enterprise_has_more_features_than_pro(self):
        assert len(BOT_FEATURES[Tier.ENTERPRISE.value]) > len(BOT_FEATURES[Tier.PRO.value])

    def test_pro_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_enterprise_has_white_label(self):
        enterprise_features = " ".join(BOT_FEATURES[Tier.ENTERPRISE.value])
        assert "white-label" in enterprise_features

    def test_get_bot_tier_info_free(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["tier"] == "free"
        assert info["price_usd_monthly"] == 0.0
        assert "features" in info

    def test_get_bot_tier_info_pro(self):
        info = get_bot_tier_info(Tier.PRO)
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] > 0

    def test_get_bot_tier_info_enterprise(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert info["tier"] == "enterprise"
        assert info["price_usd_monthly"] > get_bot_tier_info(Tier.PRO)["price_usd_monthly"]

    def test_tier_info_has_support_level(self):
        for tier in Tier:
            info = get_bot_tier_info(tier)
            assert "support_level" in info
            assert info["support_level"]


# ===========================================================================
# CineCoreBot instantiation
# ===========================================================================

class TestCineCoreBotInstantiation:
    def test_default_tier_is_free(self):
        bot = CineCoreBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = CineCoreBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = CineCoreBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = CineCoreBot()
        assert bot.config is not None

    def test_all_engines_initialized(self):
        bot = CineCoreBot(tier=Tier.PRO)
        assert bot._script_engine is not None
        assert bot._video_engine is not None
        assert bot._voice_engine is not None
        assert bot._platform_optimizer is not None
        assert bot._lead_engine is not None
        assert bot._business_scorer is not None
        assert bot._closing_agent is not None
        assert bot._billing_engine is not None
        assert bot._analytics_engine is not None
        assert bot._bulk_generator is not None
        assert bot._self_heal is not None
        assert bot._crm is not None


# ===========================================================================
# ScriptEngine
# ===========================================================================

class TestScriptEngine:
    def test_generate_basic_script_free(self):
        engine = ScriptEngine(Tier.FREE)
        result = engine.generate("Test Cafe", "coffee", "young adults")
        assert isinstance(result, CommercialScript)
        assert result.business_name == "Test Cafe"
        assert result.product == "coffee"
        assert result.target_audience == "young adults"

    def test_script_has_hook_body_cta(self):
        engine = ScriptEngine(Tier.PRO)
        result = engine.generate("Test Biz", "product", "audience")
        assert result.hook
        assert result.body
        assert result.cta
        assert result.script

    def test_free_tier_platform_is_tiktok_only(self):
        engine = ScriptEngine(Tier.FREE)
        result = engine.generate("Biz", "prod", "audience")
        assert result.platforms == ["tiktok"]

    def test_pro_tier_has_all_platforms(self):
        engine = ScriptEngine(Tier.PRO)
        result = engine.generate("Biz", "prod", "audience")
        for platform in SUPPORTED_PLATFORMS:
            assert platform in result.platforms

    def test_enterprise_tier_has_all_platforms(self):
        engine = ScriptEngine(Tier.ENTERPRISE)
        result = engine.generate("Biz", "prod", "audience")
        for platform in SUPPORTED_PLATFORMS:
            assert platform in result.platforms

    def test_genre_ad(self):
        engine = ScriptEngine(Tier.PRO)
        result = engine.generate("Biz", "prod", "audience", genre="ad")
        assert result.genre == "ad"

    def test_genre_biography(self):
        engine = ScriptEngine(Tier.PRO)
        result = engine.generate("Biz", "prod", "audience", genre="biography")
        assert result.genre == "biography"

    def test_genre_documentary(self):
        engine = ScriptEngine(Tier.PRO)
        result = engine.generate("Biz", "prod", "audience", genre="documentary")
        assert result.genre == "documentary"

    def test_genre_viral(self):
        engine = ScriptEngine(Tier.PRO)
        result = engine.generate("Biz", "prod", "audience", genre="viral")
        assert result.genre == "viral"

    def test_genre_product_promo(self):
        engine = ScriptEngine(Tier.PRO)
        result = engine.generate("Biz", "prod", "audience", genre="product_promo")
        assert result.genre == "product_promo"

    def test_invalid_genre_raises_error(self):
        engine = ScriptEngine(Tier.PRO)
        with pytest.raises(CineCoreBotError):
            engine.generate("Biz", "prod", "audience", genre="invalid_genre")

    def test_free_daily_limit(self):
        engine = ScriptEngine(Tier.FREE)
        for _ in range(5):
            engine.generate("Biz", "prod", "audience")
        with pytest.raises(CineCoreBotTierError):
            engine.generate("Biz", "prod", "audience")

    def test_reset_daily_counter(self):
        engine = ScriptEngine(Tier.FREE)
        for _ in range(5):
            engine.generate("Biz", "prod", "audience")
        engine.reset_daily_counter()
        # Should work again after reset
        result = engine.generate("Biz", "prod", "audience")
        assert result is not None

    def test_pro_higher_daily_limit(self):
        engine = ScriptEngine(Tier.PRO)
        assert engine.daily_limit == 50

    def test_enterprise_unlimited(self):
        engine = ScriptEngine(Tier.ENTERPRISE)
        assert engine.daily_limit > 1000

    def test_script_to_dict(self):
        engine = ScriptEngine(Tier.FREE)
        result = engine.generate("Biz", "prod", "audience")
        d = result.to_dict()
        assert "script_id" in d
        assert "hook" in d
        assert "body" in d
        assert "cta" in d
        assert "script" in d
        assert "platforms" in d

    def test_script_id_unique(self):
        engine = ScriptEngine(Tier.PRO)
        s1 = engine.generate("Biz1", "prod", "audience")
        s2 = engine.generate("Biz2", "prod", "audience")
        assert s1.script_id != s2.script_id


# ===========================================================================
# VideoEngine
# ===========================================================================

class TestVideoEngine:
    def test_free_tier_no_providers(self):
        engine = VideoEngine(Tier.FREE)
        assert engine.available_providers == []

    def test_pro_has_runway_and_pika(self):
        engine = VideoEngine(Tier.PRO)
        assert "runway" in engine.available_providers
        assert "pika" in engine.available_providers

    def test_enterprise_has_custom_provider(self):
        engine = VideoEngine(Tier.ENTERPRISE)
        assert "custom" in engine.available_providers

    def test_free_max_duration_zero(self):
        engine = VideoEngine(Tier.FREE)
        assert engine.max_duration == 0

    def test_pro_max_duration_15(self):
        engine = VideoEngine(Tier.PRO)
        assert engine.max_duration == 15

    def test_enterprise_max_duration_60(self):
        engine = VideoEngine(Tier.ENTERPRISE)
        assert engine.max_duration == 60

    def test_free_tier_raises_tier_error(self):
        engine = VideoEngine(Tier.FREE)
        with pytest.raises(CineCoreBotTierError):
            engine.generate("some script")

    def test_pro_generate_runway(self):
        engine = VideoEngine(Tier.PRO)
        asset = engine.generate("Commercial script here", provider="runway", duration=15)
        assert isinstance(asset, VideoAsset)
        assert asset.provider == "runway"
        assert asset.status == "ready"

    def test_pro_generate_pika(self):
        engine = VideoEngine(Tier.PRO)
        asset = engine.generate("Commercial script here", provider="pika", duration=10)
        assert asset.provider == "pika"

    def test_pro_duration_exceeds_limit(self):
        engine = VideoEngine(Tier.PRO)
        with pytest.raises(CineCoreBotTierError):
            engine.generate("script", duration=30)

    def test_invalid_provider_raises_error(self):
        engine = VideoEngine(Tier.PRO)
        with pytest.raises(CineCoreBotError):
            engine.generate("script", provider="unknown_api")

    def test_video_has_platform_urls(self):
        engine = VideoEngine(Tier.PRO)
        asset = engine.generate("script", provider="runway", duration=15)
        assert "tiktok" in asset.platforms
        assert "youtube" in asset.platforms
        assert "instagram" in asset.platforms

    def test_video_to_dict(self):
        engine = VideoEngine(Tier.PRO)
        asset = engine.generate("script", provider="runway")
        d = asset.to_dict()
        assert "video_id" in d
        assert "video_url" in d
        assert "provider" in d
        assert "status" in d

    def test_format_for_platforms(self):
        engine = VideoEngine(Tier.PRO)
        asset = engine.generate("script")
        platforms = engine.format_for_platforms(asset)
        assert "tiktok" in platforms
        assert "youtube" in platforms


# ===========================================================================
# VoiceEngine
# ===========================================================================

class TestVoiceEngine:
    def test_free_neutral_tone_only(self):
        engine = VoiceEngine(Tier.FREE)
        assert engine.available_tones == ["neutral"]

    def test_pro_all_tones(self):
        engine = VoiceEngine(Tier.PRO)
        for tone in SUPPORTED_VOICE_TONES:
            assert tone in engine.available_tones

    def test_enterprise_all_tones(self):
        engine = VoiceEngine(Tier.ENTERPRISE)
        for tone in SUPPORTED_VOICE_TONES:
            assert tone in engine.available_tones

    def test_free_voice_is_ai_neutral(self):
        engine = VoiceEngine(Tier.FREE)
        assert "ai_neutral" in engine.available_voices

    def test_pro_has_male_female_voices(self):
        engine = VoiceEngine(Tier.PRO)
        assert "male" in engine.available_voices
        assert "female" in engine.available_voices

    def test_generate_voiceover_free(self):
        engine = VoiceEngine(Tier.FREE)
        result = engine.generate("Test script", voice="ai_neutral", tone="neutral")
        assert "audio_url" in result
        assert result["status"] == "ready"

    def test_generate_voiceover_pro_excited_tone(self):
        engine = VoiceEngine(Tier.PRO)
        result = engine.generate("Test script", voice="ai_neutral", tone="excited")
        assert result["tone"] == "excited"

    def test_free_excited_tone_raises_error(self):
        engine = VoiceEngine(Tier.FREE)
        with pytest.raises(CineCoreBotTierError):
            engine.generate("script", tone="excited")

    def test_clone_voice_enterprise_only(self):
        engine = VoiceEngine(Tier.ENTERPRISE)
        result = engine.clone_voice("https://example.com/sample.mp3", "Test script")
        assert "audio_url" in result
        assert result["status"] == "ready"

    def test_clone_voice_raises_error_on_free(self):
        engine = VoiceEngine(Tier.FREE)
        with pytest.raises(CineCoreBotTierError):
            engine.clone_voice("https://example.com/sample.mp3", "script")

    def test_clone_voice_raises_error_on_pro(self):
        engine = VoiceEngine(Tier.PRO)
        with pytest.raises(CineCoreBotTierError):
            engine.clone_voice("https://example.com/sample.mp3", "script")

    def test_duration_estimate_scales_with_script(self):
        engine = VoiceEngine(Tier.PRO)
        short = engine.generate("Short script", tone="neutral")
        long = engine.generate("A much longer script with many words that should take more time to speak aloud", tone="neutral")
        assert long["duration_estimate_seconds"] >= short["duration_estimate_seconds"]


# ===========================================================================
# PlatformOptimizer
# ===========================================================================

class TestPlatformOptimizer:
    def _make_asset(self):
        return VideoAsset(
            script_id="test123",
            video_url="https://cdn.example.com/video.mp4",
            provider="runway",
            duration_seconds=15,
        )

    def test_free_only_tiktok(self):
        optimizer = PlatformOptimizer(Tier.FREE)
        assert optimizer.available_platforms == ["tiktok"]

    def test_pro_all_platforms(self):
        optimizer = PlatformOptimizer(Tier.PRO)
        for p in SUPPORTED_PLATFORMS:
            assert p in optimizer.available_platforms

    def test_optimize_returns_dict(self):
        optimizer = PlatformOptimizer(Tier.PRO)
        asset = self._make_asset()
        result = optimizer.optimize(asset)
        assert isinstance(result, dict)
        assert "tiktok" in result
        assert "youtube" in result

    def test_optimize_free_only_tiktok(self):
        optimizer = PlatformOptimizer(Tier.FREE)
        asset = self._make_asset()
        result = optimizer.optimize(asset)
        assert list(result.keys()) == ["tiktok"]

    def test_optimize_has_specs(self):
        optimizer = PlatformOptimizer(Tier.PRO)
        asset = self._make_asset()
        result = optimizer.optimize(asset)
        tiktok = result["tiktok"]
        assert "aspect_ratio" in tiktok
        assert "format" in tiktok

    def test_auto_post_free_raises_error(self):
        optimizer = PlatformOptimizer(Tier.FREE)
        asset = self._make_asset()
        with pytest.raises(CineCoreBotTierError):
            optimizer.auto_post(asset)

    def test_auto_post_pro(self):
        optimizer = PlatformOptimizer(Tier.PRO)
        asset = self._make_asset()
        result = optimizer.auto_post(asset, caption="Check us out!")
        assert "tiktok" in result
        assert result["tiktok"]["status"] == "posted"

    def test_auto_post_enterprise(self):
        optimizer = PlatformOptimizer(Tier.ENTERPRISE)
        asset = self._make_asset()
        result = optimizer.auto_post(asset)
        for platform in SUPPORTED_PLATFORMS:
            assert platform in result


# ===========================================================================
# LeadEngine
# ===========================================================================

class TestLeadEngine:
    def test_search_returns_leads(self):
        engine = LeadEngine(Tier.PRO)
        leads = engine.search("business near me")
        assert isinstance(leads, list)
        assert len(leads) > 0

    def test_each_lead_is_lead_record(self):
        engine = LeadEngine(Tier.PRO)
        leads = engine.search("restaurant")
        for lead in leads:
            assert isinstance(lead, LeadRecord)
            assert lead.name
            assert lead.business_type

    def test_filter_weak_marketing(self):
        engine = LeadEngine(Tier.PRO)
        leads = engine.search("business near me")
        weak = engine.filter_weak_marketing(leads)
        for lead in weak:
            assert lead.rating < 4.0

    def test_free_daily_limit(self):
        engine = LeadEngine(Tier.FREE)
        for _ in range(3):
            engine.search("business near me")
        with pytest.raises(CineCoreBotTierError):
            engine.search("business near me")

    def test_reset_daily_counter(self):
        engine = LeadEngine(Tier.FREE)
        for _ in range(3):
            engine.search("business near me")
        engine.reset_daily_counter()
        leads = engine.search("business near me")
        assert leads is not None

    def test_pro_higher_daily_limit(self):
        engine = LeadEngine(Tier.PRO)
        assert engine.daily_limit == 50

    def test_enterprise_unlimited(self):
        engine = LeadEngine(Tier.ENTERPRISE)
        assert engine.daily_limit > 1000

    def test_lead_has_id(self):
        engine = LeadEngine(Tier.PRO)
        leads = engine.search("business near me")
        for lead in leads:
            assert lead.lead_id

    def test_lead_to_dict(self):
        engine = LeadEngine(Tier.PRO)
        leads = engine.search("business near me")
        d = leads[0].to_dict()
        assert "lead_id" in d
        assert "name" in d
        assert "business_type" in d
        assert "location" in d
        assert "rating" in d


# ===========================================================================
# BusinessScorer
# ===========================================================================

class TestBusinessScorer:
    def test_low_rating_high_score(self):
        scorer = BusinessScorer()
        lead = LeadRecord(name="Biz", business_type="restaurant", location="downtown", rating=2.5)
        score = scorer.score(lead)
        assert score > 150

    def test_high_rating_lower_score(self):
        scorer = BusinessScorer()
        low = LeadRecord(name="Biz1", business_type="tech", location="city", rating=2.5)
        high = LeadRecord(name="Biz2", business_type="tech", location="city", rating=4.9)
        assert scorer.score(low) > scorer.score(high)

    def test_high_value_type_bonus(self):
        scorer = BusinessScorer()
        high = LeadRecord(name="Biz1", business_type="restaurant", location="city", rating=3.5)
        low = LeadRecord(name="Biz2", business_type="tech", location="city", rating=3.5)
        assert scorer.score(high) > scorer.score(low)

    def test_rank_orders_by_score(self):
        scorer = BusinessScorer()
        leads = [
            LeadRecord(name="Biz1", business_type="tech", location="city", rating=4.5),
            LeadRecord(name="Biz2", business_type="restaurant", location="city", rating=2.5),
            LeadRecord(name="Biz3", business_type="plumbing", location="city", rating=3.0),
        ]
        ranked = scorer.rank(leads)
        for i in range(len(ranked) - 1):
            assert ranked[i].opportunity_score >= ranked[i + 1].opportunity_score

    def test_score_cap_at_200(self):
        scorer = BusinessScorer()
        lead = LeadRecord(name="Biz", business_type="restaurant", location="city", rating=1.0)
        score = scorer.score(lead)
        assert score <= 200

    def test_rank_sets_opportunity_score(self):
        scorer = BusinessScorer()
        leads = [
            LeadRecord(name="Biz", business_type="restaurant", location="city", rating=3.0)
        ]
        ranked = scorer.rank(leads)
        assert ranked[0].opportunity_score > 0


# ===========================================================================
# ClosingAgent
# ===========================================================================

class TestClosingAgent:
    def _make_lead(self):
        return LeadRecord(
            name="Joe's Diner",
            business_type="restaurant",
            location="downtown",
            rating=3.1,
        )

    def test_generate_outreach_initial(self):
        agent = ClosingAgent(Tier.PRO)
        lead = self._make_lead()
        result = agent.generate_outreach(lead, "initial")
        assert result["requires_approval"] is True
        assert result["status"] == "draft"
        assert "Joe's Diner" in result["message"]

    def test_generate_outreach_follow_up(self):
        agent = ClosingAgent(Tier.PRO)
        lead = self._make_lead()
        result = agent.generate_outreach(lead, "follow_up")
        assert result["template"] == "follow_up"

    def test_generate_outreach_close(self):
        agent = ClosingAgent(Tier.PRO)
        lead = self._make_lead()
        result = agent.generate_outreach(lead, "close")
        assert result["template"] == "close"

    def test_handle_reply_price_objection(self):
        agent = ClosingAgent(Tier.PRO)
        response = agent.handle_reply("What's the price?")
        assert response
        assert len(response) > 20

    def test_handle_reply_interested(self):
        agent = ClosingAgent(Tier.PRO)
        response = agent.handle_reply("Yes I'm interested")
        assert response
        assert len(response) > 20

    def test_handle_reply_time_objection(self):
        agent = ClosingAgent(Tier.PRO)
        response = agent.handle_reply("I don't have time for this")
        assert response
        assert len(response) > 20

    def test_handle_reply_default(self):
        agent = ClosingAgent(Tier.FREE)
        response = agent.handle_reply("random message")
        assert response

    def test_generate_upsell_free_raises_error(self):
        agent = ClosingAgent(Tier.FREE)
        with pytest.raises(CineCoreBotTierError):
            agent.generate_upsell(100.0)

    def test_generate_upsell_pro(self):
        agent = ClosingAgent(Tier.PRO)
        result = agent.generate_upsell(200.0)
        assert isinstance(result, str)
        assert len(result) > 10

    def test_generate_upsell_scales_with_spend(self):
        agent = ClosingAgent(Tier.ENTERPRISE)
        low_spend = agent.generate_upsell(100.0)
        high_spend = agent.generate_upsell(5000.0)
        assert low_spend != high_spend

    def test_invalid_template_falls_back_to_initial(self):
        agent = ClosingAgent(Tier.PRO)
        lead = self._make_lead()
        result = agent.generate_outreach(lead, "nonexistent_template")
        assert result["template"] == "initial"


# ===========================================================================
# BillingEngine
# ===========================================================================

class TestBillingEngine:
    def test_list_plans_always_available(self):
        engine = BillingEngine(Tier.FREE)
        plans = engine.list_plans()
        assert isinstance(plans, list)
        assert len(plans) >= 3

    def test_plan_has_required_fields(self):
        engine = BillingEngine(Tier.PRO)
        plans = engine.list_plans()
        for plan in plans:
            assert "plan_id" in plan
            assert "price_usd" in plan
            assert "interval" in plan

    def test_create_customer_free_raises_error(self):
        engine = BillingEngine(Tier.FREE)
        with pytest.raises(CineCoreBotTierError):
            engine.create_customer("test@example.com")

    def test_create_customer_pro(self):
        engine = BillingEngine(Tier.PRO)
        customer = engine.create_customer("test@example.com")
        assert "customer_id" in customer
        assert customer["email"] == "test@example.com"

    def test_create_subscription_free_raises_error(self):
        engine = BillingEngine(Tier.FREE)
        with pytest.raises(CineCoreBotTierError):
            engine.create_subscription("test@example.com")

    def test_create_subscription_pro(self):
        engine = BillingEngine(Tier.PRO)
        sub = engine.create_subscription("test@example.com", plan="pro")
        assert "subscription_id" in sub
        assert sub["status"] == "active"
        assert sub["email"] == "test@example.com"

    def test_create_subscription_invalid_plan(self):
        engine = BillingEngine(Tier.PRO)
        with pytest.raises(CineCoreBotError):
            engine.create_subscription("test@example.com", plan="nonexistent")

    def test_create_subscription_enterprise_plan(self):
        engine = BillingEngine(Tier.ENTERPRISE)
        sub = engine.create_subscription("test@example.com", plan="enterprise")
        assert sub["plan"] == "enterprise"

    def test_cancel_subscription_enterprise_only(self):
        engine = BillingEngine(Tier.ENTERPRISE)
        result = engine.cancel_subscription("sub_abc123")
        assert result["status"] == "cancelled"

    def test_cancel_subscription_pro_raises_error(self):
        engine = BillingEngine(Tier.PRO)
        with pytest.raises(CineCoreBotTierError):
            engine.cancel_subscription("sub_abc123")

    def test_subscription_id_unique(self):
        engine = BillingEngine(Tier.PRO)
        s1 = engine.create_subscription("a@example.com")
        s2 = engine.create_subscription("b@example.com")
        assert s1["subscription_id"] != s2["subscription_id"]


# ===========================================================================
# AnalyticsEngine
# ===========================================================================

class TestAnalyticsEngine:
    def test_track_returns_analytics_record(self):
        engine = AnalyticsEngine(Tier.PRO)
        record = engine.track("video_001")
        assert isinstance(record, AnalyticsRecord)

    def test_free_tier_no_clicks_revenue(self):
        engine = AnalyticsEngine(Tier.FREE)
        record = engine.track("video_001")
        assert record.clicks == 0
        assert record.revenue_usd == 0.0

    def test_pro_has_clicks_and_conversions(self):
        engine = AnalyticsEngine(Tier.PRO)
        record = engine.track("video_002")
        assert record.views > 0
        # clicks can be 0 or more (random), but field exists
        assert hasattr(record, "clicks")

    def test_analytics_to_dict(self):
        engine = AnalyticsEngine(Tier.PRO)
        record = engine.track("video_003")
        d = record.to_dict()
        assert "video_id" in d
        assert "views" in d
        assert "clicks" in d
        assert "conversions" in d
        assert "revenue_usd" in d
        assert "ctr" in d
        assert "cvr" in d

    def test_revenue_summary(self):
        engine = AnalyticsEngine(Tier.PRO)
        engine.track("v1")
        engine.track("v2")
        summary = engine.revenue_summary()
        assert summary["total_videos_tracked"] == 2
        assert "total_revenue_usd" in summary
        assert "avg_revenue_per_video" in summary

    def test_empty_revenue_summary(self):
        engine = AnalyticsEngine(Tier.PRO)
        summary = engine.revenue_summary()
        assert summary["total_videos_tracked"] == 0
        assert summary["avg_revenue_per_video"] == 0.0

    def test_records_method(self):
        engine = AnalyticsEngine(Tier.PRO)
        engine.track("v1")
        engine.track("v2")
        records = engine.records()
        assert len(records) == 2
        assert all(isinstance(r, dict) for r in records)

    def test_deterministic_with_same_id(self):
        engine1 = AnalyticsEngine(Tier.PRO)
        engine2 = AnalyticsEngine(Tier.PRO)
        r1 = engine1.track("same_id_test")
        r2 = engine2.track("same_id_test")
        assert r1.views == r2.views


# ===========================================================================
# BulkGenerator
# ===========================================================================

class TestBulkGenerator:
    def _make_bulk_generator(self, tier: Tier) -> BulkGenerator:
        se = ScriptEngine(tier)
        ve = VideoEngine(tier)
        return BulkGenerator(tier, se, ve)

    def test_free_limit_is_one(self):
        gen = self._make_bulk_generator(Tier.FREE)
        assert gen.bulk_limit == 1

    def test_pro_limit_is_twenty(self):
        gen = self._make_bulk_generator(Tier.PRO)
        assert gen.bulk_limit == 20

    def test_enterprise_limit_is_large(self):
        gen = self._make_bulk_generator(Tier.ENTERPRISE)
        assert gen.bulk_limit > 1000

    def test_bulk_run_single(self):
        gen = self._make_bulk_generator(Tier.PRO)
        businesses = [{"name": "Cafe", "product": "coffee", "target_audience": "adults"}]
        results = gen.run(businesses)
        assert len(results) == 1
        assert "script" in results[0]

    def test_bulk_run_multiple(self):
        gen = self._make_bulk_generator(Tier.PRO)
        businesses = [
            {"name": f"Biz{i}", "product": "prod", "target_audience": "audience"}
            for i in range(5)
        ]
        results = gen.run(businesses)
        assert len(results) == 5

    def test_bulk_exceeds_limit_raises_error(self):
        gen = self._make_bulk_generator(Tier.FREE)
        businesses = [
            {"name": "Biz1", "product": "prod", "target_audience": "audience"},
            {"name": "Biz2", "product": "prod", "target_audience": "audience"},
        ]
        with pytest.raises(CineCoreBotTierError):
            gen.run(businesses)

    def test_bulk_with_video_pro(self):
        gen = self._make_bulk_generator(Tier.PRO)
        businesses = [{"name": "Biz", "product": "prod", "target_audience": "audience"}]
        results = gen.run(businesses, include_video=True)
        assert "video" in results[0]

    def test_bulk_without_video(self):
        gen = self._make_bulk_generator(Tier.PRO)
        businesses = [{"name": "Biz", "product": "prod", "target_audience": "audience"}]
        results = gen.run(businesses, include_video=False)
        assert "video" not in results[0]


# ===========================================================================
# SelfHeal
# ===========================================================================

class TestSelfHeal:
    def test_monitor_healthy(self):
        sh = SelfHeal()
        result = sh.monitor("video_engine", "ok")
        assert result["health"] == "ok"

    def test_monitor_error_triggers_fix(self):
        sh = SelfHeal()
        result = sh.monitor("script_engine", "error")
        assert result["health"] == "degraded"
        assert "fix" in result
        assert result["fix"]["status"] == "resolved"

    def test_fixes_counter_increments(self):
        sh = SelfHeal()
        sh.monitor("engine1", "error")
        sh.monitor("engine2", "error")
        health = sh.system_health()
        assert health["fixes_applied"] == 2

    def test_system_health_returns_dict(self):
        sh = SelfHeal()
        health = sh.system_health()
        assert "status" in health
        assert "total_issues_detected" in health
        assert "fixes_applied" in health
        assert "open_issues" in health

    def test_healthy_system_status(self):
        sh = SelfHeal()
        health = sh.system_health()
        assert health["status"] == "healthy"

    def test_reset_clears_issues(self):
        sh = SelfHeal()
        sh.monitor("engine", "error")
        sh.reset()
        health = sh.system_health()
        assert health["total_issues_detected"] == 0
        assert health["fixes_applied"] == 0


# ===========================================================================
# CRM
# ===========================================================================

class TestCRM:
    def _make_lead(self, name="Biz"):
        return LeadRecord(name=name, business_type="restaurant", location="downtown", rating=3.0)

    def test_add_lead(self):
        crm = CRM()
        lead = self._make_lead()
        result = crm.add_lead(lead)
        assert result["stage"] == "new_lead"
        assert result["name"] == "Biz"

    def test_leads_list(self):
        crm = CRM()
        crm.add_lead(self._make_lead("A"))
        crm.add_lead(self._make_lead("B"))
        assert len(crm.leads) == 2

    def test_update_stage(self):
        crm = CRM()
        lead = self._make_lead()
        added = crm.add_lead(lead)
        result = crm.update_stage(added["lead_id"], "demo_sent")
        assert result["stage"] == "demo_sent"

    def test_update_stage_invalid(self):
        crm = CRM()
        lead = self._make_lead()
        added = crm.add_lead(lead)
        with pytest.raises(CineCoreBotError):
            crm.update_stage(added["lead_id"], "invalid_stage")

    def test_update_stage_not_found(self):
        crm = CRM()
        with pytest.raises(CineCoreBotError):
            crm.update_stage("nonexistent_id", "demo_sent")

    def test_close_won_adds_to_clients(self):
        crm = CRM()
        lead = self._make_lead()
        added = crm.add_lead(lead)
        crm.update_stage(added["lead_id"], "closed_won")
        assert len(crm.clients) == 1

    def test_convert_to_client(self):
        crm = CRM()
        lead = self._make_lead()
        result = crm.convert_to_client(lead)
        assert result["stage"] == "closed_won"
        assert len(crm.clients) == 1

    def test_pipeline_summary(self):
        crm = CRM()
        crm.add_lead(self._make_lead("A"))
        crm.add_lead(self._make_lead("B"))
        summary = crm.pipeline_summary()
        assert summary["total_leads"] == 2
        assert "new_lead" in summary

    def test_pipeline_stages_are_valid(self):
        for stage in CRM.PIPELINE_STAGES:
            assert isinstance(stage, str)
            assert len(stage) > 0


# ===========================================================================
# CineCoreBot (full integration)
# ===========================================================================

class TestCineCoreBotIntegration:
    def test_generate_script(self):
        bot = CineCoreBot(tier=Tier.PRO)
        script = bot.generate_script("Cafe", "coffee", "adults")
        assert "hook" in script
        assert "cta" in script
        assert "script" in script

    def test_generate_video_pro(self):
        bot = CineCoreBot(tier=Tier.PRO)
        script = bot.generate_script("Cafe", "coffee", "adults")
        video = bot.generate_video(script["script"])
        assert "video_url" in video
        assert "video_id" in video

    def test_generate_video_free_raises_error(self):
        bot = CineCoreBot(tier=Tier.FREE)
        with pytest.raises(CineCoreBotTierError):
            bot.generate_video("some script")

    def test_generate_voiceover(self):
        bot = CineCoreBot(tier=Tier.PRO)
        result = bot.generate_voiceover("Test script", tone="excited")
        assert "audio_url" in result

    def test_find_leads(self):
        bot = CineCoreBot(tier=Tier.PRO)
        leads = bot.find_leads("restaurant near me")
        assert isinstance(leads, list)
        assert len(leads) > 0

    def test_score_leads(self):
        bot = CineCoreBot(tier=Tier.PRO)
        leads = bot.find_leads("business near me")
        scored = bot.score_leads(leads)
        assert len(scored) == len(leads)
        # Should be sorted by score descending
        for i in range(len(scored) - 1):
            assert scored[i]["opportunity_score"] >= scored[i + 1]["opportunity_score"]

    def test_generate_outreach(self):
        bot = CineCoreBot(tier=Tier.PRO)
        leads = bot.find_leads("restaurant near me")
        outreach = bot.generate_outreach(leads[0])
        assert outreach["requires_approval"] is True
        assert "message" in outreach

    def test_handle_client_reply(self):
        bot = CineCoreBot(tier=Tier.PRO)
        response = bot.handle_client_reply("What is the price?")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_list_plans(self):
        bot = CineCoreBot(tier=Tier.FREE)
        plans = bot.list_plans()
        assert len(plans) >= 3

    def test_create_subscription_pro(self):
        bot = CineCoreBot(tier=Tier.PRO)
        sub = bot.create_subscription("client@example.com")
        assert "subscription_id" in sub

    def test_get_analytics(self):
        bot = CineCoreBot(tier=Tier.PRO)
        analytics = bot.get_analytics("video_test_001")
        assert "views" in analytics
        assert "clicks" in analytics

    def test_revenue_summary(self):
        bot = CineCoreBot(tier=Tier.PRO)
        bot.get_analytics("v1")
        bot.get_analytics("v2")
        summary = bot.revenue_summary()
        assert summary["total_videos_tracked"] == 2

    def test_bulk_generate(self):
        bot = CineCoreBot(tier=Tier.PRO)
        businesses = [
            {"name": "Biz1", "product": "prod", "target_audience": "audience"},
            {"name": "Biz2", "product": "prod", "target_audience": "audience"},
        ]
        results = bot.bulk_generate(businesses)
        assert len(results) == 2

    def test_system_health(self):
        bot = CineCoreBot(tier=Tier.PRO)
        health = bot.system_health()
        assert health["status"] == "healthy"

    def test_monitor_component_ok(self):
        bot = CineCoreBot(tier=Tier.PRO)
        result = bot.monitor_component("video_engine", "ok")
        assert result["health"] == "ok"

    def test_monitor_component_error(self):
        bot = CineCoreBot(tier=Tier.PRO)
        result = bot.monitor_component("script_engine", "error")
        assert result["health"] == "degraded"

    def test_add_lead_to_crm(self):
        bot = CineCoreBot(tier=Tier.PRO)
        leads = bot.find_leads("restaurant near me")
        result = bot.add_lead_to_crm(leads[0])
        assert result["stage"] == "new_lead"

    def test_update_lead_stage(self):
        bot = CineCoreBot(tier=Tier.PRO)
        leads = bot.find_leads("restaurant near me")
        added = bot.add_lead_to_crm(leads[0])
        updated = bot.update_lead_stage(added["lead_id"], "demo_sent")
        assert updated["stage"] == "demo_sent"

    def test_crm_summary(self):
        bot = CineCoreBot(tier=Tier.PRO)
        leads = bot.find_leads("business near me")
        for lead in leads[:3]:
            bot.add_lead_to_crm(lead)
        summary = bot.crm_summary()
        assert summary["total_leads"] == 3

    def test_describe_tier_free(self):
        bot = CineCoreBot(tier=Tier.FREE)
        description = bot.describe_tier()
        assert "CineCore" in description
        assert "free" in description.lower()

    def test_describe_tier_pro(self):
        bot = CineCoreBot(tier=Tier.PRO)
        description = bot.describe_tier()
        assert "CineCore" in description

    def test_run_full_campaign_free(self):
        bot = CineCoreBot(tier=Tier.FREE)
        report = bot.run_full_campaign("Cafe", "coffee", "adults")
        assert "script_generation" in report["steps_completed"]
        assert "voiceover_generation" in report["steps_completed"]
        # Video not expected on FREE tier
        assert "video_generation" not in report["steps_completed"]

    def test_run_full_campaign_pro(self):
        bot = CineCoreBot(tier=Tier.PRO)
        report = bot.run_full_campaign("Cafe", "coffee", "adults")
        assert "script_generation" in report["steps_completed"]
        assert "video_generation" in report["steps_completed"]
        assert "platform_optimization" in report["steps_completed"]
        assert "analytics_tracking" in report["steps_completed"]
        assert "voiceover_generation" in report["steps_completed"]

    def test_optimize_for_platforms(self):
        bot = CineCoreBot(tier=Tier.PRO)
        script = bot.generate_script("Cafe", "coffee", "adults")
        video = bot.generate_video(script["script"])
        optimized = bot.optimize_for_platforms(video)
        assert "tiktok" in optimized
        assert "youtube" in optimized

    def test_auto_post_pro(self):
        bot = CineCoreBot(tier=Tier.PRO)
        script = bot.generate_script("Cafe", "coffee", "adults")
        video = bot.generate_video(script["script"])
        result = bot.auto_post(video, caption="Try our coffee!")
        assert "tiktok" in result
        assert result["tiktok"]["status"] == "posted"

    def test_clone_voice_enterprise(self):
        bot = CineCoreBot(tier=Tier.ENTERPRISE)
        result = bot.clone_voice("https://example.com/sample.mp3", "Test script")
        assert "audio_url" in result

    def test_generate_upsell_pro(self):
        bot = CineCoreBot(tier=Tier.PRO)
        result = bot.generate_upsell(200.0)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_create_customer_enterprise(self):
        bot = CineCoreBot(tier=Tier.ENTERPRISE)
        customer = bot.create_customer("vip@example.com")
        assert "customer_id" in customer
