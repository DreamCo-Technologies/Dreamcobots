"""Tests for bots/commercial_bot/tiers.py and bots/commercial_bot/commercial_bot.py"""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.commercial_bot.commercial_bot import (
    CommercialBot,
    CommercialBotTierError,
    CommercialScript,
    Lead,
    Deal,
    AdPerformance,
    ScriptEngine,
    VideoEngine,
    VoiceEngine,
    PlatformOptimizer,
    ClientFinder,
    ClosingAgent,
    BillingEngine,
    AnalyticsEngine,
    BulkGenerator,
    SelfHeal,
    PLATFORMS,
    PRICING_TIERS,
    SCRIPT_DURATIONS,
    BULK_LIMITS,
)
from bots.commercial_bot.tiers import BOT_FEATURES, get_bot_tier_info


# ---------------------------------------------------------------------------
# Tier definitions
# ---------------------------------------------------------------------------

class TestTierDefinitions:
    def test_all_tiers_have_features(self):
        for tier in Tier:
            assert len(BOT_FEATURES[tier.value]) > 0

    def test_enterprise_has_more_features_than_pro(self):
        assert len(BOT_FEATURES[Tier.ENTERPRISE.value]) > len(BOT_FEATURES[Tier.PRO.value])

    def test_pro_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_enterprise_has_api_access(self):
        assert any("API" in f for f in BOT_FEATURES[Tier.ENTERPRISE.value])

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

    def test_free_tier_has_script_generator(self):
        features = BOT_FEATURES[Tier.FREE.value]
        assert any("script" in f.lower() for f in features)

    def test_enterprise_has_video_generation(self):
        features = BOT_FEATURES[Tier.ENTERPRISE.value]
        assert any("video" in f.lower() for f in features)


# ---------------------------------------------------------------------------
# ScriptEngine
# ---------------------------------------------------------------------------

class TestScriptEngine:
    def setup_method(self):
        self.engine = ScriptEngine()

    def test_generate_returns_commercial_script(self):
        result = self.engine.generate("Joe's Pizza", "wood-fired pizza", "families")
        assert isinstance(result, CommercialScript)

    def test_script_contains_business_name(self):
        result = self.engine.generate("Joe's Pizza", "wood-fired pizza", "families")
        assert "Joe's Pizza" in result.script

    def test_script_has_hook(self):
        result = self.engine.generate("Joe's Pizza", "wood-fired pizza", "families")
        assert result.hook and len(result.hook) > 0

    def test_script_has_cta(self):
        result = self.engine.generate("Joe's Pizza", "wood-fired pizza", "families")
        assert result.cta and len(result.cta) > 0

    def test_15_second_script_shorter_than_60(self):
        short = self.engine.generate("Biz", "product", "audience", duration_seconds=15)
        long = self.engine.generate("Biz", "product", "audience", duration_seconds=60)
        assert len(short.script) <= len(long.script)

    def test_duration_snapped_to_allowed(self):
        result = self.engine.generate(
            "Biz", "product", "audience", duration_seconds=45, tier=Tier.FREE
        )
        allowed = SCRIPT_DURATIONS[Tier.FREE]
        assert result.duration_seconds in allowed

    def test_free_tier_single_platform(self):
        result = self.engine.generate(
            "Biz", "product", "audience", tier=Tier.FREE
        )
        assert result.platforms == ["TikTok"]

    def test_pro_tier_multi_platform(self):
        result = self.engine.generate(
            "Biz", "product", "audience", tier=Tier.PRO
        )
        assert len(result.platforms) > 1

    def test_created_at_set(self):
        result = self.engine.generate("Biz", "product", "audience")
        assert result.created_at is not None

    def test_different_businesses_produce_different_scripts(self):
        a = self.engine.generate("Alpha Corp", "software", "developers")
        b = self.engine.generate("Beta LLC", "hardware", "engineers")
        assert a.script != b.script


# ---------------------------------------------------------------------------
# VideoEngine
# ---------------------------------------------------------------------------

class TestVideoEngine:
    def setup_method(self):
        self.engine = VideoEngine()

    def test_build_scenes_returns_list(self):
        scenes = self.engine.build_scenes("Hook\n\nBody\n\nCTA")
        assert isinstance(scenes, list)
        assert len(scenes) > 0

    def test_scenes_have_required_fields(self):
        scenes = self.engine.build_scenes("Hook\n\nBody")
        for scene in scenes:
            assert hasattr(scene, "index")
            assert hasattr(scene, "label")
            assert hasattr(scene, "description")
            assert hasattr(scene, "camera_angle")
            assert hasattr(scene, "b_roll")

    def test_generate_video_free_tier(self):
        result = self.engine.generate_video("Test script", tier=Tier.FREE)
        assert result["status"] == "concept_ready"
        assert "scenes" in result

    def test_generate_video_enterprise_has_url(self):
        result = self.engine.generate_video("Test script", tier=Tier.ENTERPRISE)
        assert result["status"] == "rendered"
        assert "video_url" in result

    def test_format_for_platforms_returns_all_platforms(self):
        result = self.engine.format_for_platforms("http://example.com/video.mp4")
        for p in PLATFORMS:
            assert p in result

    def test_scenes_have_alternating_camera_angles(self):
        scenes = self.engine.build_scenes("A\n\nB\n\nC\n\nD\n\nE")
        angles = [s.camera_angle for s in scenes]
        assert len(set(angles)) > 1


# ---------------------------------------------------------------------------
# VoiceEngine
# ---------------------------------------------------------------------------

class TestVoiceEngine:
    def setup_method(self):
        self.engine = VoiceEngine()

    def test_generate_voiceover_returns_dict(self):
        result = self.engine.generate_voiceover("Buy now!", tone="excited", platform="TikTok")
        assert isinstance(result, dict)

    def test_voiceover_contains_script(self):
        script = "Buy now before it's gone!"
        result = self.engine.generate_voiceover(script)
        assert result["voiceover_script"] == script

    def test_unknown_tone_defaults_to_neutral(self):
        result = self.engine.generate_voiceover("script", tone="alien")
        assert result["tone"] == "neutral"

    def test_valid_tones_preserved(self):
        for tone in VoiceEngine.TONES:
            result = self.engine.generate_voiceover("script", tone=tone)
            assert result["tone"] == tone

    def test_platform_guidance_present(self):
        result = self.engine.generate_voiceover("script", platform="YouTube")
        assert result["format_guidance"]

    def test_estimated_duration_positive(self):
        result = self.engine.generate_voiceover("Hello world this is a test script")
        assert result["estimated_duration_seconds"] >= 15


# ---------------------------------------------------------------------------
# PlatformOptimizer
# ---------------------------------------------------------------------------

class TestPlatformOptimizer:
    def setup_method(self):
        self.optimizer = PlatformOptimizer()

    def test_optimize_returns_all_platforms_by_default(self):
        result = self.optimizer.optimize("Short script for all platforms")
        for p in PLATFORMS:
            assert p in result

    def test_optimize_specific_platforms(self):
        result = self.optimizer.optimize("Script", platforms=["TikTok", "YouTube"])
        assert "TikTok" in result
        assert "YouTube" in result
        assert "Instagram" not in result

    def test_adapted_script_present(self):
        result = self.optimizer.optimize("Buy now! Great product for everyone.")
        for platform_data in result.values():
            assert "adapted_script" in platform_data

    def test_aspect_ratio_present(self):
        result = self.optimizer.optimize("Script")
        assert result["TikTok"]["aspect_ratio"] == "9:16"
        assert result["YouTube"]["aspect_ratio"] == "16:9"

    def test_long_script_truncated(self):
        long_script = " ".join(["word"] * 200)
        result = self.optimizer.optimize(long_script, platforms=["TikTok"])
        assert "..." in result["TikTok"]["adapted_script"]


# ---------------------------------------------------------------------------
# ClientFinder
# ---------------------------------------------------------------------------

class TestClientFinder:
    def setup_method(self):
        self.finder = ClientFinder()

    def test_find_returns_leads(self):
        leads = self.finder.find("restaurant", limit=3)
        assert len(leads) <= 3
        assert all(isinstance(l, Lead) for l in leads)

    def test_lead_has_required_fields(self):
        leads = self.finder.find("restaurant", limit=1)
        lead = leads[0]
        assert lead.name
        assert lead.niche == "restaurant"
        assert lead.contact
        assert lead.source

    def test_unknown_niche_generates_leads(self):
        leads = self.finder.find("custom_niche", limit=2)
        assert len(leads) > 0

    def test_score_lead_returns_int(self):
        leads = self.finder.find("restaurant", limit=1)
        score = self.finder.score_lead(leads[0])
        assert isinstance(score, int)
        assert 0 <= score <= 100

    def test_high_value_niches_get_bonus_score(self):
        finder = ClientFinder()
        real_estate_lead = Lead(
            name="Top Realty", niche="real_estate", contact="x@y.com",
            source="google_maps", score=70
        )
        restaurant_lead = Lead(
            name="Joe's Diner", niche="restaurant", contact="a@b.com",
            source="google_maps", score=70
        )
        assert finder.score_lead(real_estate_lead) > finder.score_lead(restaurant_lead)

    def test_limit_respected(self):
        leads = self.finder.find("restaurant", limit=2)
        assert len(leads) <= 2


# ---------------------------------------------------------------------------
# ClosingAgent
# ---------------------------------------------------------------------------

class TestClosingAgent:
    def setup_method(self):
        self.agent = ClosingAgent()

    def test_send_outreach_step_0(self):
        msg = self.agent.send_outreach("Joe", step=0)
        assert "Joe" in msg

    def test_send_outreach_step_1(self):
        msg = self.agent.send_outreach("Joe", step=1)
        assert len(msg) > 0

    def test_send_outreach_step_2(self):
        msg = self.agent.send_outreach("Joe", step=2)
        assert len(msg) > 0

    def test_send_outreach_step_out_of_range_clamped(self):
        msg = self.agent.send_outreach("Joe", step=99)
        assert len(msg) > 0

    def test_respond_price_objection(self):
        reply = self.agent.respond("What is the price for this?")
        assert "$" in reply or "package" in reply.lower()

    def test_respond_interested(self):
        reply = self.agent.respond("I am interested")
        assert "today" in reply.lower() or "set" in reply.lower()

    def test_respond_unknown_returns_default(self):
        reply = self.agent.respond("blah blah xyz")
        assert len(reply) > 0

    def test_create_deal_returns_deal(self):
        deal = self.agent.create_deal("ABC Corp", "pro_commercial")
        assert isinstance(deal, Deal)
        assert deal.client == "ABC Corp"
        assert deal.monthly_value > 0

    def test_create_deal_monthly_value_in_range(self):
        deal = self.agent.create_deal("Test", "basic")
        low, high = PRICING_TIERS["basic"]
        assert deal.monthly_value >= low

    def test_create_deal_default_package(self):
        deal = self.agent.create_deal("Biz")
        assert deal.package == "pro_commercial"


# ---------------------------------------------------------------------------
# BillingEngine
# ---------------------------------------------------------------------------

class TestBillingEngine:
    def setup_method(self):
        self.billing = BillingEngine()

    def test_create_subscription_returns_dict(self):
        sub = self.billing.create_subscription("client@example.com")
        assert isinstance(sub, dict)
        assert sub["status"] == "active"

    def test_subscription_has_email(self):
        sub = self.billing.create_subscription("test@test.com")
        assert sub["customer_email"] == "test@test.com"

    def test_list_subscriptions(self):
        self.billing.create_subscription("a@a.com")
        self.billing.create_subscription("b@b.com")
        subs = self.billing.list_subscriptions()
        assert len(subs) == 2

    def test_cancel_subscription(self):
        self.billing.create_subscription("cancel@test.com")
        result = self.billing.cancel_subscription("cancel@test.com")
        assert result is True

    def test_cancel_nonexistent_returns_false(self):
        result = self.billing.cancel_subscription("ghost@test.com")
        assert result is False

    def test_total_mrr_sums_active(self):
        self.billing.create_subscription("x@x.com", "pro_commercial")
        mrr = self.billing.total_mrr()
        assert mrr > 0

    def test_mrr_excludes_cancelled(self):
        self.billing.create_subscription("c@c.com", "basic")
        before = self.billing.total_mrr()
        self.billing.cancel_subscription("c@c.com")
        after = self.billing.total_mrr()
        assert after < before

    def test_subscription_amount_matches_package(self):
        sub = self.billing.create_subscription("d@d.com", "monthly_package")
        low, high = PRICING_TIERS["monthly_package"]
        assert sub["amount_usd"] >= low


# ---------------------------------------------------------------------------
# AnalyticsEngine
# ---------------------------------------------------------------------------

class TestAnalyticsEngine:
    def setup_method(self):
        self.analytics = AnalyticsEngine()

    def test_record_creates_entry(self):
        perf = self.analytics.record("vid_001", views=1000, clicks=50, conversions=5, revenue=250.0)
        assert isinstance(perf, AdPerformance)
        assert perf.video_id == "vid_001"

    def test_track_returns_dict(self):
        self.analytics.record("vid_002", views=500)
        result = self.analytics.track("vid_002")
        assert isinstance(result, dict)
        assert result["video_id"] == "vid_002"

    def test_track_nonexistent_returns_zeros(self):
        result = self.analytics.track("nonexistent")
        assert result["views"] == 0
        assert result["clicks"] == 0

    def test_ctr_calculated(self):
        self.analytics.record("vid_003", views=1000, clicks=100)
        result = self.analytics.track("vid_003")
        assert result["ctr_pct"] == 10.0

    def test_cvr_calculated(self):
        self.analytics.record("vid_004", views=1000, clicks=100, conversions=10)
        result = self.analytics.track("vid_004")
        assert result["cvr_pct"] == 10.0

    def test_metrics_accumulate(self):
        self.analytics.record("vid_005", views=500)
        self.analytics.record("vid_005", views=500)
        result = self.analytics.track("vid_005")
        assert result["views"] == 1000

    def test_top_performers_returns_list(self):
        self.analytics.record("a", views=100, revenue=500)
        self.analytics.record("b", views=200, revenue=1000)
        top = self.analytics.top_performers(n=2)
        assert len(top) <= 2
        assert top[0]["revenue"] >= top[-1]["revenue"]

    def test_top_performers_default_n(self):
        for i in range(7):
            self.analytics.record(f"vid_{i}", revenue=float(i * 100))
        top = self.analytics.top_performers()
        assert len(top) <= 5


# ---------------------------------------------------------------------------
# BulkGenerator
# ---------------------------------------------------------------------------

class TestBulkGenerator:
    def setup_method(self):
        self.script_engine = ScriptEngine()
        self.video_engine = VideoEngine()
        self.bulk = BulkGenerator(self.script_engine, self.video_engine)

    def test_run_pro_tier(self):
        businesses = ["Biz A", "Biz B", "Biz C"]
        results = self.bulk.run(businesses, niche="restaurant", tier=Tier.PRO)
        assert len(results) == 3

    def test_result_has_required_fields(self):
        results = self.bulk.run(["Biz X"], tier=Tier.PRO)
        assert "business" in results[0]
        assert "script" in results[0]
        assert "video" in results[0]
        assert "hook" in results[0]
        assert "cta" in results[0]

    def test_free_tier_raises(self):
        with pytest.raises(CommercialBotTierError):
            self.bulk.run(["Biz A"], tier=Tier.FREE)

    def test_respects_bulk_limit(self):
        businesses = [f"Biz {i}" for i in range(200)]
        results = self.bulk.run(businesses, tier=Tier.PRO)
        assert len(results) <= BULK_LIMITS[Tier.PRO]

    def test_enterprise_runs_large_batch(self):
        businesses = [f"Store {i}" for i in range(100)]
        results = self.bulk.run(businesses, tier=Tier.ENTERPRISE)
        assert len(results) == 100


# ---------------------------------------------------------------------------
# SelfHeal
# ---------------------------------------------------------------------------

class TestSelfHeal:
    def setup_method(self):
        self.heal = SelfHeal()

    def test_check_system_returns_dict(self):
        result = self.heal.check_system()
        assert isinstance(result, dict)

    def test_check_system_healthy(self):
        result = self.heal.check_system()
        assert result["status"] == "healthy"

    def test_check_system_lists_engines(self):
        result = self.heal.check_system()
        assert "engines" in result
        assert len(result["engines"]) > 0

    def test_checked_at_present(self):
        result = self.heal.check_system()
        assert "checked_at" in result

    def test_detect_errors_returns_list(self):
        errors = self.heal.detect_errors()
        assert isinstance(errors, list)

    def test_fix_no_errors(self):
        msg = self.heal.fix([])
        assert "No errors" in msg

    def test_fix_with_errors(self):
        msg = self.heal.fix(["error_1", "error_2"])
        assert "2" in msg


# ---------------------------------------------------------------------------
# CommercialBot FREE tier
# ---------------------------------------------------------------------------

class TestCommercialBotFree:
    def setup_method(self):
        self.bot = CommercialBot(tier=Tier.FREE)

    def test_generate_script_returns_dict(self):
        result = self.bot.generate_script("Joe's Pizza", "pizza", "families")
        assert isinstance(result, dict)
        assert "script" in result

    def test_generate_script_contains_business(self):
        result = self.bot.generate_script("Joe's Pizza", "pizza", "families")
        assert "Joe's Pizza" in result["script"]

    def test_create_ad_plan_returns_dict(self):
        script = self.bot.generate_script("Biz", "product", "audience")["script"]
        plan = self.bot.create_ad_plan(script)
        assert "hook" in plan
        assert "scenes" in plan
        assert "platforms" in plan

    def test_free_tier_single_platform_in_plan(self):
        script = self.bot.generate_script("Biz", "product", "audience")["script"]
        plan = self.bot.create_ad_plan(script)
        assert "TikTok" in plan["platforms"]

    def test_generate_video_raises_tier_error(self):
        with pytest.raises(CommercialBotTierError):
            self.bot.generate_video("test script")

    def test_find_clients_raises_tier_error(self):
        with pytest.raises(CommercialBotTierError):
            self.bot.find_clients()

    def test_close_client_raises_tier_error(self):
        with pytest.raises(CommercialBotTierError):
            self.bot.close_client("Joe")

    def test_bulk_generate_raises_tier_error(self):
        with pytest.raises(CommercialBotTierError):
            self.bot.bulk_generate(["Biz A"])

    def test_revenue_summary_returns_dict(self):
        summary = self.bot.revenue_summary()
        assert isinstance(summary, dict)
        assert summary["tier"] == "free"

    def test_tier_info_returns_free(self):
        info = self.bot.tier_info()
        assert info["tier"] == "free"
        assert info["price_usd_monthly"] == 0.0


# ---------------------------------------------------------------------------
# CommercialBot PRO tier
# ---------------------------------------------------------------------------

class TestCommercialBotPro:
    def setup_method(self):
        self.bot = CommercialBot(tier=Tier.PRO)

    def test_generate_script_60_seconds(self):
        result = self.bot.generate_script("AutoDealer", "cars", "buyers", 60)
        assert result["duration_seconds"] == 60

    def test_generate_video_returns_concept(self):
        result = self.bot.generate_video("Buy now! Great cars here.")
        assert "scenes" in result

    def test_generate_voiceover_returns_dict(self):
        result = self.bot.generate_voiceover("Script here", tone="professional")
        assert result["tone"] == "professional"

    def test_find_clients_restaurant(self):
        leads = self.bot.find_clients(niche="restaurant", limit=3)
        assert len(leads) <= 3
        assert all(l["niche"] == "restaurant" for l in leads)

    def test_find_clients_have_score(self):
        leads = self.bot.find_clients(niche="restaurant", limit=2)
        for lead in leads:
            assert "score" in lead
            assert 0 <= lead["score"] <= 100

    def test_close_client_outreach(self):
        msg = self.bot.close_client("Joe's Diner")
        assert "Joe's Diner" in msg

    def test_close_client_price_objection(self):
        reply = self.bot.close_client("Joe", message="What is the price?")
        assert "package" in reply.lower() or "$" in reply

    def test_send_outreach_step_1(self):
        msg = self.bot.send_outreach("Prime Realty", step=1)
        assert len(msg) > 0

    def test_create_deal_returns_deal_dict(self):
        deal = self.bot.create_deal("City Motors", "pro_commercial")
        assert deal["client"] == "City Motors"
        assert deal["monthly_value"] > 0

    def test_create_deal_updates_revenue(self):
        before = self.bot.revenue_summary()["pipeline_revenue_usd"]
        self.bot.create_deal("New Client", "monthly_package")
        after = self.bot.revenue_summary()["pipeline_revenue_usd"]
        assert after > before

    def test_bulk_generate_3_businesses(self):
        results = self.bot.bulk_generate(
            ["Pizza Palace", "Auto World", "Top Realtor"], niche="restaurant"
        )
        assert len(results) == 3

    def test_bulk_results_have_script(self):
        results = self.bot.bulk_generate(["Biz A", "Biz B"])
        for r in results:
            assert "script" in r
            assert len(r["script"]) > 0

    def test_create_subscription(self):
        sub = self.bot.create_subscription("client@agency.com", "pro_commercial")
        assert sub["status"] == "active"

    def test_mrr_increases_after_subscription(self):
        before = self.bot.revenue_summary()["mrr_usd"]
        self.bot.create_subscription("new@client.com")
        after = self.bot.revenue_summary()["mrr_usd"]
        assert after > before

    def test_analytics_track(self):
        self.bot.analytics.record("vid_pro_001", views=2000, clicks=200, revenue=1000.0)
        result = self.bot.analytics.track("vid_pro_001")
        assert result["views"] == 2000
        assert result["ctr_pct"] == 10.0

    def test_self_heal_check(self):
        result = self.bot.self_heal.check_system()
        assert result["status"] == "healthy"

    def test_revenue_summary_pro_tier(self):
        summary = self.bot.revenue_summary()
        assert summary["tier"] == "pro"
        assert "features" in summary

    def test_multi_platform_ad_plan(self):
        script = self.bot.generate_script("Brand", "product", "users")["script"]
        plan = self.bot.create_ad_plan(script)
        assert len(plan["platforms"]) > 1


# ---------------------------------------------------------------------------
# CommercialBot ENTERPRISE tier
# ---------------------------------------------------------------------------

class TestCommercialBotEnterprise:
    def setup_method(self):
        self.bot = CommercialBot(tier=Tier.ENTERPRISE)

    def test_generate_video_enterprise_renders(self):
        result = self.bot.generate_video("Cinematic ad script here")
        assert result["status"] == "rendered"
        assert "video_url" in result

    def test_bulk_generate_large_batch(self):
        businesses = [f"Enterprise Client {i}" for i in range(60)]
        results = self.bot.bulk_generate(businesses)
        assert len(results) == 60

    def test_find_clients_all_niches(self):
        for niche in ["real_estate", "car_dealership", "ecommerce"]:
            leads = self.bot.find_clients(niche=niche, limit=2)
            assert len(leads) > 0

    def test_enterprise_tier_info(self):
        info = self.bot.tier_info()
        assert info["tier"] == "enterprise"
        assert info["price_usd_monthly"] > 0

    def test_enterprise_revenue_summary(self):
        summary = self.bot.revenue_summary()
        assert summary["tier"] == "enterprise"
        assert len(summary["features"]) > len(
            CommercialBot(tier=Tier.PRO).revenue_summary()["features"]
        )

    def test_multiple_subscriptions_mrr(self):
        for i in range(5):
            self.bot.create_subscription(f"client{i}@test.com", "monthly_package")
        mrr = self.bot.revenue_summary()["mrr_usd"]
        _, high = PRICING_TIERS["monthly_package"]
        assert mrr >= 5 * high


# ---------------------------------------------------------------------------
# Constants / Pricing
# ---------------------------------------------------------------------------

class TestConstants:
    def test_platforms_list(self):
        assert "TikTok" in PLATFORMS
        assert "YouTube" in PLATFORMS
        assert "Instagram" in PLATFORMS
        assert "Facebook" in PLATFORMS

    def test_pricing_tiers_defined(self):
        assert "basic" in PRICING_TIERS
        assert "pro_commercial" in PRICING_TIERS
        assert "monthly_package" in PRICING_TIERS

    def test_pricing_ranges_valid(self):
        for package, (low, high) in PRICING_TIERS.items():
            if high is not None:
                assert high >= low

    def test_bulk_limits_increase_with_tier(self):
        assert BULK_LIMITS[Tier.FREE] < BULK_LIMITS[Tier.PRO]
        assert BULK_LIMITS[Tier.PRO] < BULK_LIMITS[Tier.ENTERPRISE]

    def test_script_durations_increase_with_tier(self):
        free_max = max(SCRIPT_DURATIONS[Tier.FREE])
        pro_max = max(SCRIPT_DURATIONS[Tier.PRO])
        enterprise_max = max(SCRIPT_DURATIONS[Tier.ENTERPRISE])
        assert free_max <= pro_max <= enterprise_max


# ---------------------------------------------------------------------------
# Integration: Full workflow
# ---------------------------------------------------------------------------

class TestFullWorkflow:
    def test_full_commercial_creation_workflow(self):
        bot = CommercialBot(tier=Tier.PRO)

        # Step 1: Find leads
        leads = bot.find_clients(niche="restaurant", limit=3)
        assert len(leads) > 0

        # Step 2: Generate script
        result = bot.generate_script(
            leads[0]["name"], "dining experience", "local families", 30
        )
        assert result["script"]

        # Step 3: Create ad plan
        plan = bot.create_ad_plan(result["script"])
        assert "scenes" in plan

        # Step 4: Outreach
        msg = bot.close_client(leads[0]["name"])
        assert leads[0]["name"] in msg

        # Step 5: Close deal
        deal = bot.create_deal(leads[0]["name"])
        assert deal["monthly_value"] > 0

        # Step 6: Subscribe
        sub = bot.create_subscription(leads[0]["contact"])
        assert sub["status"] == "active"

        # Step 7: Track analytics
        bot.analytics.record("vid_wf_001", views=1000, clicks=100, conversions=10, revenue=500.0)
        stats = bot.analytics.track("vid_wf_001")
        assert stats["ctr_pct"] == 10.0

        # Step 8: Revenue summary
        summary = bot.revenue_summary()
        assert summary["total_clients"] >= 1
        assert summary["pipeline_revenue_usd"] > 0

    def test_bulk_outreach_workflow(self):
        bot = CommercialBot(tier=Tier.ENTERPRISE)
        businesses = [f"Local Biz {i}" for i in range(10)]
        results = bot.bulk_generate(businesses, niche="roofing", duration_seconds=30)
        assert len(results) == 10
        for r in results:
            assert "hook" in r
            assert "cta" in r
            assert "video" in r

    def test_self_healing_workflow(self):
        bot = CommercialBot(tier=Tier.PRO)
        health = bot.self_heal.check_system()
        assert health["status"] == "healthy"
        errors = bot.self_heal.detect_errors()
        fix_msg = bot.self_heal.fix(errors)
        assert "No errors" in fix_msg