"""
Tests for bots/localized_bot/

Covers all modules:
  1. Tiers
  2. RegionDatabase (30+ regions)
  3. LocalizationEngine
  4. GlobalLeaderboard
  5. LocalizedBot main class (integration + tier enforcement)
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
from bots.localized_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_BASIC_TRANSLATION,
    FEATURE_FULL_TRANSLATION,
    FEATURE_INDUSTRY_ADAPTION,
    FEATURE_REGIONAL_CHALLENGES,
    FEATURE_GLOBAL_LEADERBOARD_VOTE,
    FEATURE_CUSTOM_LOCALE,
    FEATURE_PRIVATE_REGIONAL_BOTS,
    FEATURE_API_ACCESS,
    FEATURE_ANALYTICS,
    FEATURE_WHITE_LABEL,
)
from bots.localized_bot.region_database import RegionDatabase
from bots.localized_bot.localization_engine import LocalizationEngine
from bots.localized_bot.global_leaderboard import GlobalLeaderboard
from bots.localized_bot.localized_bot import LocalizedBot, LocalizedBotTierError


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

    def test_free_max_regions(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_regions == 3

    def test_pro_max_regions(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.max_regions == 25

    def test_enterprise_unlimited_regions(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited_regions()
        assert cfg.max_regions is None

    def test_free_has_basic_translation(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_BASIC_TRANSLATION)

    def test_pro_has_full_translation(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_FULL_TRANSLATION)

    def test_pro_has_industry_adaption(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_INDUSTRY_ADAPTION)

    def test_enterprise_has_white_label(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_WHITE_LABEL)

    def test_enterprise_has_api_access(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_API_ACCESS)

    def test_enterprise_has_analytics(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_ANALYTICS)

    def test_free_does_not_have_vote(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_GLOBAL_LEADERBOARD_VOTE)

    def test_upgrade_free_to_pro(self):
        next_cfg = get_upgrade_path(Tier.FREE)
        assert next_cfg is not None
        assert next_cfg.tier == Tier.PRO

    def test_upgrade_pro_to_enterprise(self):
        next_cfg = get_upgrade_path(Tier.PRO)
        assert next_cfg is not None
        assert next_cfg.tier == Tier.ENTERPRISE

    def test_no_upgrade_from_enterprise(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_tier_catalogue_keys(self):
        assert set(TIER_CATALOGUE.keys()) == {"free", "pro", "enterprise"}

    def test_tier_config_is_dataclass(self):
        cfg = get_tier_config(Tier.PRO)
        assert isinstance(cfg, TierConfig)


# ===========================================================================
# 2. RegionDatabase
# ===========================================================================

REQUIRED_REGION_IDS = [
    "US", "UK", "Mexico", "Brazil", "France", "Germany", "Japan", "China",
    "India", "Nigeria", "South_Africa", "Australia", "Canada", "Saudi_Arabia",
    "South_Korea", "Russia", "Indonesia", "Argentina", "Spain", "Italy",
    "Egypt", "Turkey", "Thailand", "Vietnam", "Poland", "Netherlands",
    "UAE", "Colombia", "Pakistan", "Bangladesh",
]


class TestRegionDatabase:
    @pytest.fixture
    def db(self):
        return RegionDatabase()

    def test_at_least_30_regions(self, db):
        assert len(db.list_regions()) >= 30

    def test_all_required_regions_present(self, db):
        region_ids = {r["region_id"] for r in db.list_regions()}
        for rid in REQUIRED_REGION_IDS:
            assert rid in region_ids, f"Missing region: {rid}"

    def test_get_us_region(self, db):
        region = db.get_region("US")
        assert region["country_code"] == "US"
        assert region["language_code"] == "en"

    def test_get_japan_region(self, db):
        region = db.get_region("Japan")
        assert region["language_code"] == "ja"
        assert region["currency_code"] == "JPY"

    def test_get_unknown_region_raises(self, db):
        with pytest.raises(KeyError):
            db.get_region("UNKNOWN_XYZ")

    def test_region_has_required_fields(self, db):
        region = db.get_region("Germany")
        for field in ["region_id", "region_name", "country_code", "language_code",
                      "language_name", "industries", "population_millions",
                      "timezone", "currency_code"]:
            assert field in region, f"Missing field: {field}"

    def test_region_industries_list(self, db):
        region = db.get_region("India")
        assert isinstance(region["industries"], list)
        assert 3 <= len(region["industries"]) <= 5

    def test_get_regions_by_language_english(self, db):
        regions = db.get_regions_by_language("en")
        region_ids = {r["region_id"] for r in regions}
        assert "US" in region_ids
        assert "UK" in region_ids
        assert "Nigeria" in region_ids

    def test_get_regions_by_language_spanish(self, db):
        regions = db.get_regions_by_language("es")
        region_ids = {r["region_id"] for r in regions}
        assert "Mexico" in region_ids
        assert "Argentina" in region_ids
        assert "Spain" in region_ids

    def test_get_regions_by_language_arabic(self, db):
        regions = db.get_regions_by_language("ar")
        region_ids = {r["region_id"] for r in regions}
        assert "Saudi_Arabia" in region_ids
        assert "UAE" in region_ids

    def test_get_regions_by_industry_finance(self, db):
        regions = db.get_regions_by_industry("Finance")
        region_ids = {r["region_id"] for r in regions}
        assert "US" in region_ids
        assert "UK" in region_ids

    def test_get_regions_by_industry_case_insensitive(self, db):
        regions_upper = db.get_regions_by_industry("Finance")
        regions_lower = db.get_regions_by_industry("finance")
        assert len(regions_upper) == len(regions_lower)

    def test_search_regions_by_name(self, db):
        results = db.search_regions("Ger")
        names = [r["region_name"] for r in results]
        assert "Germany" in names

    def test_search_regions_by_language(self, db):
        results = db.search_regions("Japanese")
        region_ids = {r["region_id"] for r in results}
        assert "Japan" in region_ids

    def test_search_regions_no_match(self, db):
        results = db.search_regions("ZZZNOMATCH999")
        assert results == []

    def test_list_regions_returns_list(self, db):
        regions = db.list_regions()
        assert isinstance(regions, list)
        assert all(isinstance(r, dict) for r in regions)


# ===========================================================================
# 3. LocalizationEngine
# ===========================================================================

class TestLocalizationEngine:
    @pytest.fixture
    def engine(self):
        return LocalizationEngine()

    def test_adapt_content_returns_dict(self, engine):
        result = engine.adapt_content("Hello!", "US")
        assert isinstance(result, dict)

    def test_adapt_content_keys(self, engine):
        result = engine.adapt_content("Hello!", "Japan")
        for key in ["original", "adapted", "region", "language", "cultural_notes", "industry_notes"]:
            assert key in result

    def test_adapt_content_original_preserved(self, engine):
        result = engine.adapt_content("Test content", "Germany")
        assert result["original"] == "Test content"

    def test_adapt_content_region_name(self, engine):
        result = engine.adapt_content("Hello!", "France")
        assert result["region"] == "France"

    def test_adapt_content_with_industry(self, engine):
        result = engine.adapt_content("Deploy app", "US", industry="Technology")
        assert result["industry_notes"] != ""
        assert "API" in result["industry_notes"] or "innov" in result["industry_notes"].lower()

    def test_adapt_content_no_industry_empty_notes(self, engine):
        result = engine.adapt_content("Hello!", "UK")
        assert result["industry_notes"] == ""

    def test_translate_message_returns_dict(self, engine):
        result = engine.translate_message("Good morning", "ja")
        assert isinstance(result, dict)

    def test_translate_message_keys(self, engine):
        result = engine.translate_message("Hello", "de")
        for key in ["original", "translated", "target_language", "confidence"]:
            assert key in result

    def test_translate_message_original_preserved(self, engine):
        result = engine.translate_message("Good night", "fr")
        assert result["original"] == "Good night"

    def test_translate_message_confidence_range(self, engine):
        result = engine.translate_message("Hello", "es")
        assert 0.0 <= result["confidence"] <= 1.0

    def test_get_cultural_tips_returns_list(self, engine):
        tips = engine.get_cultural_tips("Japan")
        assert isinstance(tips, list)
        assert len(tips) > 0

    def test_get_cultural_tips_default_for_unknown(self, engine):
        tips = engine.get_cultural_tips("Unknown_Region_XYZ")
        assert isinstance(tips, list)
        assert len(tips) > 0

    def test_generate_regional_bot_config_keys(self, engine):
        config = engine.generate_regional_bot_config("US", "sales_bot")
        for key in ["bot_type", "region_id", "region_name", "language_code",
                    "language_name", "timezone", "currency_code", "greeting",
                    "cultural_notes", "industries"]:
            assert key in config

    def test_generate_regional_bot_config_bot_type(self, engine):
        config = engine.generate_regional_bot_config("Japan", "support_bot")
        assert config["bot_type"] == "support_bot"
        assert config["region_id"] == "Japan"


# ===========================================================================
# 4. GlobalLeaderboard
# ===========================================================================

class TestGlobalLeaderboard:
    @pytest.fixture
    def board(self):
        return GlobalLeaderboard()

    def test_register_bot_returns_dict(self, board):
        result = board.register_bot("TestBot", "user1", "US", "A test bot", "sales")
        assert isinstance(result, dict)

    def test_register_bot_fields(self, board):
        result = board.register_bot("MyBot", "user2", "Japan", "Japan bot", "support")
        for key in ["bot_id", "bot_name", "creator_id", "region_id", "description",
                    "category", "registered_at", "vote_count", "total_score", "avg_score"]:
            assert key in result

    def test_register_bot_initial_scores(self, board):
        result = board.register_bot("Bot1", "u1", "UK", "UK Bot", "general")
        assert result["vote_count"] == 0
        assert result["avg_score"] == 0.0

    def test_vote_updates_scores(self, board):
        reg = board.register_bot("VoteBot", "u1", "US", "desc", "cat")
        updated = board.vote_for_bot(reg["bot_id"], "voter1", 5)
        assert updated["vote_count"] == 1
        assert updated["avg_score"] == 5.0

    def test_vote_multiple(self, board):
        reg = board.register_bot("MultiVote", "u1", "US", "desc", "cat")
        board.vote_for_bot(reg["bot_id"], "v1", 4)
        updated = board.vote_for_bot(reg["bot_id"], "v2", 2)
        assert updated["vote_count"] == 2
        assert updated["avg_score"] == 3.0

    def test_vote_invalid_score_low(self, board):
        reg = board.register_bot("B", "u", "US", "d", "c")
        with pytest.raises(ValueError):
            board.vote_for_bot(reg["bot_id"], "v", 0)

    def test_vote_invalid_score_high(self, board):
        reg = board.register_bot("B", "u", "US", "d", "c")
        with pytest.raises(ValueError):
            board.vote_for_bot(reg["bot_id"], "v", 6)

    def test_vote_unknown_bot(self, board):
        with pytest.raises(KeyError):
            board.vote_for_bot("nonexistent-id", "v", 3)

    def test_get_leaderboard_sorted(self, board):
        r1 = board.register_bot("Low", "u1", "US", "d", "cat")
        r2 = board.register_bot("High", "u2", "US", "d", "cat")
        board.vote_for_bot(r1["bot_id"], "v1", 2)
        board.vote_for_bot(r2["bot_id"], "v2", 5)
        lb = board.get_leaderboard()
        assert lb[0]["bot_id"] == r2["bot_id"]

    def test_get_leaderboard_filter_region(self, board):
        board.register_bot("USBot", "u1", "US", "d", "c")
        board.register_bot("JPBot", "u2", "Japan", "d", "c")
        lb = board.get_leaderboard(region_id="Japan")
        assert all(b["region_id"] == "Japan" for b in lb)

    def test_get_leaderboard_filter_category(self, board):
        board.register_bot("SalesBot", "u1", "US", "d", "sales")
        board.register_bot("SupportBot", "u2", "US", "d", "support")
        lb = board.get_leaderboard(category="sales")
        assert all(b["category"] == "sales" for b in lb)

    def test_get_top_bots(self, board):
        for i in range(15):
            r = board.register_bot(f"Bot{i}", "u", "US", "d", "c")
            board.vote_for_bot(r["bot_id"], "v", (i % 5) + 1)
        top = board.get_top_bots(n=5)
        assert len(top) == 5

    def test_get_regional_winner(self, board):
        r1 = board.register_bot("Avg", "u1", "US", "d", "c")
        r2 = board.register_bot("Best", "u2", "US", "d", "c")
        board.vote_for_bot(r1["bot_id"], "v1", 3)
        board.vote_for_bot(r2["bot_id"], "v2", 5)
        winner = board.get_regional_winner("US")
        assert winner is not None
        assert winner["bot_id"] == r2["bot_id"]

    def test_get_regional_winner_no_bots(self, board):
        assert board.get_regional_winner("EMPTY_REGION") is None


# ===========================================================================
# 5. LocalizedBot (integration + tier enforcement)
# ===========================================================================

class TestLocalizedBotFree:
    @pytest.fixture
    def bot(self):
        return LocalizedBot(tier=Tier.FREE)

    def test_list_regions_always_available(self, bot):
        regions = bot.list_regions()
        assert len(regions) >= 30

    def test_get_tier_info(self, bot):
        info = bot.get_tier_info()
        assert info["tier"] == "free"
        assert info["price_usd_monthly"] == 0.0

    def test_upgrade_info_from_free(self, bot):
        upgrade = bot.get_upgrade_info()
        assert upgrade is not None
        assert upgrade["tier"] == "pro"

    def test_adapt_content_allowed_on_free(self, bot):
        result = bot.adapt_content("Hello!", "US")
        assert result["original"] == "Hello!"

    def test_vote_blocked_on_free(self, bot):
        with pytest.raises(LocalizedBotTierError):
            bot.vote_for_bot("some-id", "voter", 5)

    def test_register_regional_bot_blocked_on_free(self, bot):
        with pytest.raises(LocalizedBotTierError):
            bot.register_regional_bot("Bot", "u1", "US", "desc", "cat")

    def test_chat_returns_string(self, bot):
        response = bot.chat("Tell me about regions")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_chat_tier_query(self, bot):
        response = bot.chat("What plan am I on?")
        assert "Free" in response or "free" in response

    def test_industry_adaption_blocked_on_free(self, bot):
        with pytest.raises(LocalizedBotTierError):
            bot.adapt_content("Hello", "US", industry="Technology")


class TestLocalizedBotPro:
    @pytest.fixture
    def bot(self):
        return LocalizedBot(tier=Tier.PRO)

    def test_adapt_content_with_industry(self, bot):
        result = bot.adapt_content("Deploy", "US", industry="Technology")
        assert result["industry_notes"] != ""

    def test_translate_message(self, bot):
        result = bot.translate_message("Good morning", "ja")
        assert "translated" in result

    def test_get_cultural_tips(self, bot):
        tips = bot.get_cultural_tips("Japan")
        assert isinstance(tips, list)

    def test_register_and_vote(self, bot):
        reg = bot.register_regional_bot("ProBot", "u1", "US", "A Pro bot", "sales")
        assert "bot_id" in reg
        updated = bot.vote_for_bot(reg["bot_id"], "voter1", 4)
        assert updated["avg_score"] == 4.0

    def test_get_leaderboard(self, bot):
        lb = bot.get_leaderboard()
        assert isinstance(lb, list)

    def test_upgrade_info_from_pro(self, bot):
        upgrade = bot.get_upgrade_info()
        assert upgrade is not None
        assert upgrade["tier"] == "enterprise"

    def test_chat_translate_hint(self, bot):
        response = bot.chat("How do I translate?")
        assert isinstance(response, str)


class TestLocalizedBotEnterprise:
    @pytest.fixture
    def bot(self):
        return LocalizedBot(tier=Tier.ENTERPRISE)

    def test_all_features_available(self, bot):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feat in [FEATURE_API_ACCESS, FEATURE_WHITE_LABEL, FEATURE_ANALYTICS,
                     FEATURE_CUSTOM_LOCALE, FEATURE_PRIVATE_REGIONAL_BOTS]:
            assert cfg.has_feature(feat)

    def test_no_upgrade_from_enterprise(self, bot):
        assert bot.get_upgrade_info() is None

    def test_register_and_leaderboard(self, bot):
        reg = bot.register_regional_bot("EntBot", "ent_user", "Germany", "Enterprise bot", "finance")
        bot.vote_for_bot(reg["bot_id"], "v1", 5)
        lb = bot.get_leaderboard(region_id="Germany")
        assert len(lb) >= 1
        assert lb[0]["bot_id"] == reg["bot_id"]
