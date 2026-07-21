"""
Tests for bots/influencer_bot/

Covers all modules:
  1. Tiers
  2. Influencer Database
  3. Brand Partnership
  4. Virality Engine
  5. InfluencerBot main class (integration)
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from bots.influencer_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_INFLUENCER_CATALOG,
    FEATURE_COBRAND_TEMPLATE,
    FEATURE_BASIC_ANALYTICS,
    FEATURE_FULL_DATABASE,
    FEATURE_VIRALITY_ENGINE,
    FEATURE_CAMPAIGN_MANAGER,
    FEATURE_AUDIENCE_ANALYTICS,
    FEATURE_CELEBRITY_PARTNERSHIPS,
    FEATURE_CUSTOM_COBRAND,
    FEATURE_WHITE_LABEL,
    FEATURE_REVENUE_SHARING,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
)
from bots.influencer_bot.influencer_database import (
    InfluencerDatabase,
    Influencer,
    PARTNERSHIP_STANDARD,
    PARTNERSHIP_PREMIUM,
    PARTNERSHIP_CELEBRITY,
    CATEGORY_FITNESS,
    CATEGORY_MUSIC,
    CATEGORY_GAMING,
    CATEGORY_TECH,
    CATEGORY_WELLNESS,
)
from bots.influencer_bot.brand_partnership import BrandPartnership
from bots.influencer_bot.virality_engine import (
    ViralityEngine,
    CAMPAIGN_TYPES,
    CAMPAIGN_CHALLENGE,
    CAMPAIGN_PRODUCT_LAUNCH,
    CAMPAIGN_EDUCATION_SERIES,
    CAMPAIGN_GIVEAWAY,
    CAMPAIGN_COLLAB_SERIES,
    CONTENT_POST,
    CONTENT_STORY,
    CONTENT_VIDEO_SCRIPT,
    CONTENT_BOT_SHOWCASE,
)
from bots.influencer_bot.influencer_bot import InfluencerBot, InfluencerBotTierError


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        assert len(list_tiers()) == 3

    def test_free_price(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0

    def test_pro_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0

    def test_enterprise_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0

    def test_enterprise_unlimited_bots(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited_bots()

    def test_free_limited_bots(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_cobranded_bots == 1

    def test_pro_limited_bots(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.max_cobranded_bots == 10

    def test_free_has_catalog_feature(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_INFLUENCER_CATALOG)

    def test_free_lacks_full_database(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_FULL_DATABASE)

    def test_pro_has_virality_engine(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_VIRALITY_ENGINE)

    def test_enterprise_has_celebrity_partnerships(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_CELEBRITY_PARTNERSHIPS)

    def test_enterprise_has_white_label(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_WHITE_LABEL)

    def test_enterprise_has_api_access(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_API_ACCESS)

    def test_enterprise_has_dedicated_support(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_DEDICATED_SUPPORT)

    def test_upgrade_from_free(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_from_pro(self):
        upgrade = get_upgrade_path(Tier.PRO)
        assert upgrade is not None
        assert upgrade.tier == Tier.ENTERPRISE

    def test_no_upgrade_from_enterprise(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_all_feature_flags_defined(self):
        all_flags = [
            FEATURE_INFLUENCER_CATALOG, FEATURE_COBRAND_TEMPLATE, FEATURE_BASIC_ANALYTICS,
            FEATURE_FULL_DATABASE, FEATURE_VIRALITY_ENGINE, FEATURE_CAMPAIGN_MANAGER,
            FEATURE_AUDIENCE_ANALYTICS, FEATURE_CELEBRITY_PARTNERSHIPS, FEATURE_CUSTOM_COBRAND,
            FEATURE_WHITE_LABEL, FEATURE_REVENUE_SHARING, FEATURE_API_ACCESS,
            FEATURE_DEDICATED_SUPPORT,
        ]
        assert len(all_flags) == 13


# ===========================================================================
# 2. Influencer Database
# ===========================================================================

class TestInfluencerDatabase:
    def setup_method(self):
        self.db = InfluencerDatabase()

    def test_minimum_twenty_influencers(self):
        assert self.db.count() >= 20

    def test_get_influencer_by_id(self):
        inf = self.db.get_influencer("inf_001")
        assert inf is not None
        assert inf.influencer_id == "inf_001"

    def test_get_influencer_unknown_returns_none(self):
        assert self.db.get_influencer("not_real") is None

    def test_list_all_influencers(self):
        all_inf = self.db.list_influencers()
        assert len(all_inf) >= 20

    def test_list_influencers_by_category(self):
        fitness = self.db.list_influencers(category=CATEGORY_FITNESS)
        assert len(fitness) >= 1
        assert all(i.category == CATEGORY_FITNESS for i in fitness)

    def test_get_by_category(self):
        music = self.db.get_by_category(CATEGORY_MUSIC)
        assert len(music) >= 1
        assert all(i.category == CATEGORY_MUSIC for i in music)

    def test_search_by_name(self):
        results = self.db.search_influencers("Alex")
        assert len(results) >= 1
        assert any("Alex" in r.name for r in results)

    def test_search_by_specialty(self):
        results = self.db.search_influencers("yoga")
        assert len(results) >= 1

    def test_get_celebrities(self):
        celebs = self.db.get_celebrities()
        assert len(celebs) >= 3
        assert all(c.partnership_tier == PARTNERSHIP_CELEBRITY for c in celebs)

    def test_influencer_to_dict(self):
        inf = self.db.get_influencer("inf_001")
        d = inf.to_dict()
        required_keys = [
            "influencer_id", "name", "category", "audience_size_millions",
            "platform", "specialty", "engagement_rate_pct", "partnership_tier",
        ]
        for key in required_keys:
            assert key in d

    def test_category_case_insensitive(self):
        lower = self.db.list_influencers(category="fitness")
        upper = self.db.list_influencers(category="FITNESS")
        assert len(lower) == len(upper)


# ===========================================================================
# 3. Brand Partnership
# ===========================================================================

class TestBrandPartnership:
    def setup_method(self):
        self.bp = BrandPartnership()

    def _make_partnership(self, influencer_id="inf_007", rev_share=0.15):
        return self.bp.create_partnership(
            influencer_id=influencer_id,
            brand_name="TestBrand",
            bot_name="TestBot",
            bot_description="A great test bot",
            category=CATEGORY_GAMING,
            revenue_share_pct=rev_share,
        )

    def test_create_partnership_returns_dict(self):
        p = self._make_partnership()
        assert isinstance(p, dict)
        assert "partnership_id" in p

    def test_partnership_status_active(self):
        p = self._make_partnership()
        assert p["status"] == "ACTIVE"

    def test_get_partnership(self):
        p = self._make_partnership()
        fetched = self.bp.get_partnership(p["partnership_id"])
        assert fetched["partnership_id"] == p["partnership_id"]

    def test_get_unknown_partnership_returns_none(self):
        assert self.bp.get_partnership("prt_nope") is None

    def test_list_partnerships_empty(self):
        assert self.bp.list_partnerships() == []

    def test_list_partnerships(self):
        self._make_partnership()
        self._make_partnership()
        assert len(self.bp.list_partnerships()) == 2

    def test_list_partnerships_filtered_by_influencer(self):
        self._make_partnership(influencer_id="inf_001")
        self._make_partnership(influencer_id="inf_002")
        result = self.bp.list_partnerships(influencer_id="inf_001")
        assert len(result) == 1
        assert result[0]["influencer_id"] == "inf_001"

    def test_create_cobranded_bot_returns_dict(self):
        p = self._make_partnership()
        bot = self.bp.create_cobranded_bot(
            partnership_id=p["partnership_id"],
            target_audience="Gamers 18-35",
            bot_capabilities=["chat", "recommendations"],
        )
        assert "bot_id" in bot
        assert bot["status"] == "READY"

    def test_create_cobranded_bot_updates_partnership(self):
        p = self._make_partnership()
        bot = self.bp.create_cobranded_bot(
            partnership_id=p["partnership_id"],
            target_audience="Gamers",
            bot_capabilities=["chat"],
        )
        updated = self.bp.get_partnership(p["partnership_id"])
        assert bot["bot_id"] in updated["cobranded_bots"]

    def test_create_cobranded_bot_unknown_partnership(self):
        with pytest.raises(ValueError):
            self.bp.create_cobranded_bot("bad_id", "audience", [])

    def test_calculate_projected_revenue(self):
        p = self._make_partnership()
        rev = self.bp.calculate_projected_revenue(p["partnership_id"], monthly_users=1000)
        assert rev["gross_revenue_usd"] > 0
        assert rev["net_revenue_usd"] < rev["gross_revenue_usd"]
        assert "subscription_revenue_usd" in rev
        assert "ad_revenue_usd" in rev

    def test_revenue_influencer_share(self):
        p = self._make_partnership(rev_share=0.20)
        rev = self.bp.calculate_projected_revenue(p["partnership_id"], monthly_users=1000)
        expected_share = round(rev["gross_revenue_usd"] * 0.20, 2)
        assert rev["influencer_share_usd"] == expected_share

    def test_revenue_unknown_partnership_raises(self):
        with pytest.raises(ValueError):
            self.bp.calculate_projected_revenue("bad_id", 100)


# ===========================================================================
# 4. Virality Engine
# ===========================================================================

class TestViralityEngine:
    def setup_method(self):
        self.ve = ViralityEngine()

    def _make_campaign(self, campaign_type=CAMPAIGN_CHALLENGE):
        return self.ve.create_campaign(
            partnership_id="prt_test",
            campaign_type=campaign_type,
            title="Test Challenge",
            description="A test viral challenge",
            duration_days=7,
        )

    def test_campaign_types_count(self):
        assert len(CAMPAIGN_TYPES) == 5

    def test_create_campaign_returns_dict(self):
        c = self._make_campaign()
        assert "campaign_id" in c
        assert c["status"] == "DRAFT"

    def test_create_campaign_invalid_type(self):
        with pytest.raises(ValueError):
            self.ve.create_campaign("prt_x", "BAD_TYPE", "T", "D", 3)

    def test_launch_campaign(self):
        c = self._make_campaign()
        launched = self.ve.launch_campaign(c["campaign_id"])
        assert launched["status"] == "ACTIVE"

    def test_launch_unknown_campaign_raises(self):
        with pytest.raises(ValueError):
            self.ve.launch_campaign("cmp_nope")

    def test_track_draft_campaign(self):
        c = self._make_campaign()
        metrics = self.ve.track_campaign(c["campaign_id"])
        assert metrics["views"] == 0
        assert metrics["viral_score"] == 0.0

    def test_track_active_campaign(self):
        c = self._make_campaign(CAMPAIGN_GIVEAWAY)
        self.ve.launch_campaign(c["campaign_id"])
        metrics = self.ve.track_campaign(c["campaign_id"])
        assert metrics["views"] > 0
        assert metrics["shares"] > 0
        assert metrics["conversions"] > 0

    def test_track_unknown_campaign_raises(self):
        with pytest.raises(ValueError):
            self.ve.track_campaign("cmp_nope")

    def test_generate_viral_content_post(self):
        content = self.ve.generate_viral_content("prt_test", CONTENT_POST)
        assert content["content_type"] == CONTENT_POST
        assert "hook" in content
        assert "call_to_action" in content

    def test_generate_viral_content_story(self):
        content = self.ve.generate_viral_content("prt_test", CONTENT_STORY)
        assert content["content_type"] == CONTENT_STORY

    def test_generate_viral_content_video_script(self):
        content = self.ve.generate_viral_content("prt_test", CONTENT_VIDEO_SCRIPT)
        assert content["content_type"] == CONTENT_VIDEO_SCRIPT
        assert "estimated_duration_seconds" in content

    def test_generate_viral_content_bot_showcase(self):
        content = self.ve.generate_viral_content("prt_test", CONTENT_BOT_SHOWCASE)
        assert content["content_type"] == CONTENT_BOT_SHOWCASE
        assert "demo_features" in content

    def test_generate_invalid_content_type(self):
        with pytest.raises(ValueError):
            self.ve.generate_viral_content("prt_test", "INVALID")

    def test_viral_score_zero_views(self):
        assert self.ve.calculate_viral_score(0, 0, 0) == 0.0

    def test_viral_score_in_range(self):
        score = self.ve.calculate_viral_score(1_000_000, 50_000, 20_000)
        assert 0.0 <= score <= 100.0

    def test_viral_score_high_share_rate(self):
        score = self.ve.calculate_viral_score(1000, 500, 200)
        assert score > 0.0


# ===========================================================================
# 5. InfluencerBot — Integration
# ===========================================================================

class TestInfluencerBotFree:
    def setup_method(self):
        self.bot = InfluencerBot(tier=Tier.FREE)

    def test_browse_influencers_excludes_celebrities(self):
        influencers = self.bot.browse_influencers()
        assert all(i["partnership_tier"] != PARTNERSHIP_CELEBRITY for i in influencers)

    def test_get_influencer_valid(self):
        inf = self.bot.get_influencer("inf_001")
        assert inf["influencer_id"] == "inf_001"

    def test_get_influencer_invalid(self):
        result = self.bot.get_influencer("bad_id")
        assert "error" in result

    def test_free_cannot_launch_campaign(self):
        with pytest.raises(InfluencerBotTierError):
            self.bot.launch_campaign("prt_x", CAMPAIGN_CHALLENGE, "T", "D", 7)

    def test_free_cannot_generate_viral_content(self):
        with pytest.raises(InfluencerBotTierError):
            self.bot.generate_viral_content("prt_x", CONTENT_POST)

    def test_get_tier_info(self):
        info = self.bot.get_tier_info()
        assert info["tier"] == "free"
        assert info["price_usd_monthly"] == 0.0

    def test_get_upgrade_info(self):
        info = self.bot.get_upgrade_info()
        assert info["upgrade_available"] is True
        assert info["upgrade_to"] == "Pro"

    def test_chat_about_influencers(self):
        response = self.bot.chat("show me the influencer catalog")
        assert "influencer" in response.lower()

    def test_chat_about_tier(self):
        response = self.bot.chat("what tier am I on?")
        assert "free" in response.lower() or "pro" in response.lower()

    def test_chat_default_response(self):
        response = self.bot.chat("hello there")
        assert "Influencer Bot" in response


class TestInfluencerBotPro:
    def setup_method(self):
        self.bot = InfluencerBot(tier=Tier.PRO)

    def test_browse_includes_premium(self):
        influencers = self.bot.browse_influencers()
        tiers = {i["partnership_tier"] for i in influencers}
        assert PARTNERSHIP_PREMIUM in tiers

    def test_create_partnership_standard_influencer(self):
        p = self.bot.create_partnership(
            influencer_id="inf_009",
            brand_name="TechCo",
            bot_name="TechBot",
            bot_description="AI tutorial bot",
            category=CATEGORY_TECH,
        )
        assert "partnership_id" in p

    def test_pro_cannot_partner_celebrity(self):
        with pytest.raises(InfluencerBotTierError):
            self.bot.create_partnership(
                influencer_id="inf_003",
                brand_name="BigBrand",
                bot_name="CelebBot",
                bot_description="Celebrity bot",
                category="ENTERTAINMENT",
            )

    def test_create_cobranded_bot(self):
        p = self.bot.create_partnership(
            influencer_id="inf_007",
            brand_name="GameCo",
            bot_name="GamingBot",
            bot_description="Gaming tips bot",
            category=CATEGORY_GAMING,
        )
        bot_def = self.bot.create_cobranded_bot(
            partnership_id=p["partnership_id"],
            target_audience="Gamers 18-30",
            bot_capabilities=["chat", "game_tips"],
        )
        assert bot_def["status"] == "READY"
        assert "bot_id" in bot_def

    def test_launch_and_track_campaign(self):
        p = self.bot.create_partnership(
            influencer_id="inf_007",
            brand_name="GameCo",
            bot_name="GamingBot",
            bot_description="Gaming tips bot",
            category=CATEGORY_GAMING,
        )
        campaign = self.bot.launch_campaign(
            partnership_id=p["partnership_id"],
            campaign_type=CAMPAIGN_CHALLENGE,
            title="7-Day Gaming Challenge",
            description="Play a new game every day",
            duration_days=7,
        )
        assert campaign["status"] == "ACTIVE"
        metrics = self.bot.track_campaign(campaign["campaign_id"])
        assert metrics["views"] > 0

    def test_generate_viral_content(self):
        content = self.bot.generate_viral_content("prt_test", CONTENT_VIDEO_SCRIPT)
        assert content["content_type"] == CONTENT_VIDEO_SCRIPT

    def test_pro_upgrade_info_points_to_enterprise(self):
        info = self.bot.get_upgrade_info()
        assert info["upgrade_to"] == "Enterprise"

    def test_pro_revenue_share_capped(self):
        p = self.bot.create_partnership(
            influencer_id="inf_009",
            brand_name="TechCo",
            bot_name="TechBot",
            bot_description="AI tutorial bot",
            category=CATEGORY_TECH,
            revenue_share_pct=0.30,
        )
        assert p["revenue_share_pct"] == 0.10


class TestInfluencerBotEnterprise:
    def setup_method(self):
        self.bot = InfluencerBot(tier=Tier.ENTERPRISE)

    def test_celebrity_partnership_allowed(self):
        p = self.bot.create_partnership(
            influencer_id="inf_003",
            brand_name="MegaBrand",
            bot_name="StarBot",
            bot_description="Celebrity co-branded bot",
            category="ENTERTAINMENT",
        )
        assert "partnership_id" in p

    def test_unlimited_bots(self):
        info = self.bot.get_tier_info()
        assert info["max_cobranded_bots"] is None

    def test_no_upgrade_available(self):
        info = self.bot.get_upgrade_info()
        assert info["upgrade_available"] is False

    def test_chat_about_celebrity(self):
        response = self.bot.chat("tell me about celebrity partners")
        assert "celebrity" in response.lower() or "Celebrity" in response
