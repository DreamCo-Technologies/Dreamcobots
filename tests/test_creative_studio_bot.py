"""
Tests for the Creative Studio Bot.

Validates:
  1. MusicCreator  — compose_music, generate_lyrics, analyze_music
  2. FilmCreator   — generate_script, create_storyboard, suggest_cinematography
  3. ArtCreator    — generate_artwork, create_3d_model, suggest_color_palette
  4. ContentStrategyEngine — create_content_calendar, generate_viral_post, analyze_engagement
  5. MemeGenerator — generate_meme, analyze_viral_trends, predict_viral_score
  6. CreativeStudioBot — tier gating, daily limits, all public methods, dashboard
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.creative_studio_bot.content_creator import (
    MusicCreator,
    FilmCreator,
    ArtCreator,
    GENRES,
    STYLES,
)
from bots.creative_studio_bot.influencer_engine import (
    ContentStrategyEngine,
    MemeGenerator,
    PLATFORMS,
)
from bots.creative_studio_bot.creative_studio_bot import (
    CreativeStudioBot,
    CreativeStudioBotError,
)
from bots.creative_studio_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    BOT_FEATURES,
    get_bot_tier_info,
    DAILY_CREATION_LIMITS,
)


# ===========================================================================
# Tier tests
# ===========================================================================

class TestTiers:
    def test_tier_enum_values(self):
        assert Tier.FREE.value == "free"
        assert Tier.PRO.value == "pro"
        assert Tier.ENTERPRISE.value == "enterprise"

    def test_tier_catalogue_has_three_tiers(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_free_tier_price(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0

    def test_enterprise_tier_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly > 0.0

    def test_upgrade_path_free_to_pro(self):
        next_tier = get_upgrade_path(Tier.FREE)
        assert next_tier is not None
        assert next_tier.tier == Tier.PRO

    def test_upgrade_path_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_bot_features_free_has_music(self):
        assert "music_creation" in BOT_FEATURES[Tier.FREE.value]

    def test_bot_features_enterprise_has_commercial_rights(self):
        assert "commercial_rights" in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_get_bot_tier_info_returns_dict(self):
        info = get_bot_tier_info(Tier.PRO)
        assert isinstance(info, dict)
        assert "features" in info
        assert "daily_creation_limit" in info

    def test_daily_limit_free(self):
        assert DAILY_CREATION_LIMITS[Tier.FREE.value] == 3

    def test_daily_limit_pro(self):
        assert DAILY_CREATION_LIMITS[Tier.PRO.value] == 50

    def test_daily_limit_enterprise_unlimited(self):
        assert DAILY_CREATION_LIMITS[Tier.ENTERPRISE.value] is None


# ===========================================================================
# MusicCreator tests
# ===========================================================================

class TestMusicCreator:
    def setup_method(self):
        self.creator = MusicCreator()

    def test_compose_music_returns_dict(self):
        result = self.creator.compose_music("jazz", "relaxed")
        assert isinstance(result, dict)

    def test_compose_music_genre_field(self):
        result = self.creator.compose_music("jazz", "relaxed")
        assert result["genre"] == "jazz"

    def test_compose_music_mood_field(self):
        result = self.creator.compose_music("pop", "upbeat")
        assert result["mood"] == "upbeat"

    def test_compose_music_has_tempo(self):
        result = self.creator.compose_music("rock", "energetic")
        assert "tempo" in result
        assert isinstance(result["tempo"], int)

    def test_compose_music_has_instruments(self):
        result = self.creator.compose_music("classical", "calm")
        assert "instruments" in result
        assert isinstance(result["instruments"], list)
        assert len(result["instruments"]) > 0

    def test_compose_music_has_notes(self):
        result = self.creator.compose_music("electronic", "intense")
        assert "notes" in result
        assert isinstance(result["notes"], list)

    def test_compose_music_unknown_genre_falls_back(self):
        result = self.creator.compose_music("unknown_genre", "neutral")
        assert result["genre"] in GENRES

    def test_compose_music_has_structure(self):
        result = self.creator.compose_music("pop", "happy")
        assert "structure" in result
        assert "chorus" in result["structure"]

    def test_generate_lyrics_returns_dict(self):
        result = self.creator.generate_lyrics("love", "rhyming")
        assert isinstance(result, dict)

    def test_generate_lyrics_has_verses(self):
        result = self.creator.generate_lyrics("adventure", "narrative", verses=2)
        assert "verses" in result
        assert len(result["verses"]) == 2

    def test_generate_lyrics_has_chorus(self):
        result = self.creator.generate_lyrics("freedom", "free verse")
        assert "chorus" in result
        assert "lines" in result["chorus"]

    def test_generate_lyrics_has_bridge(self):
        result = self.creator.generate_lyrics("hope", "poetic")
        assert "bridge" in result

    def test_generate_lyrics_clamps_verses(self):
        result = self.creator.generate_lyrics("theme", "style", verses=99)
        assert len(result["verses"]) <= 6

    def test_analyze_music_returns_dict(self):
        result = self.creator.analyze_music({"title": "Test Track", "waveform": []})
        assert isinstance(result, dict)

    def test_analyze_music_has_bpm(self):
        result = self.creator.analyze_music({"title": "Track"})
        assert "bpm" in result
        assert isinstance(result["bpm"], int)

    def test_analyze_music_has_key(self):
        result = self.creator.analyze_music({})
        assert "detected_key" in result

    def test_analyze_music_has_genre_classification(self):
        result = self.creator.analyze_music({})
        assert "genre_classification" in result
        assert result["genre_classification"] in GENRES

    def test_genres_list_not_empty(self):
        assert len(GENRES) >= 8


# ===========================================================================
# FilmCreator tests
# ===========================================================================

class TestFilmCreator:
    def setup_method(self):
        self.creator = FilmCreator()

    def test_generate_script_returns_dict(self):
        result = self.creator.generate_script("thriller", "A detective solves a mystery")
        assert isinstance(result, dict)

    def test_generate_script_has_scenes(self):
        result = self.creator.generate_script("comedy", "Two friends swap lives", num_scenes=3)
        assert "scenes" in result
        assert len(result["scenes"]) == 3

    def test_generate_script_scene_has_heading(self):
        result = self.creator.generate_script("drama", "A family reunion", num_scenes=2)
        assert "heading" in result["scenes"][0]

    def test_generate_script_scene_has_dialogue(self):
        result = self.creator.generate_script("action", "A heist gone wrong", num_scenes=2)
        assert "dialogue" in result["scenes"][0]
        assert len(result["scenes"][0]["dialogue"]) > 0

    def test_generate_script_has_three_act_structure(self):
        result = self.creator.generate_script("sci-fi", "Aliens invade Earth", num_scenes=9)
        assert "three_act_structure" in result
        assert "act_1" in result["three_act_structure"]

    def test_generate_script_clamps_scenes(self):
        result = self.creator.generate_script("horror", "Haunted house", num_scenes=999)
        assert len(result["scenes"]) <= 20

    def test_create_storyboard_returns_dict(self):
        script = self.creator.generate_script("drama", "A romance story", num_scenes=3)
        board = self.creator.create_storyboard(script)
        assert isinstance(board, dict)

    def test_create_storyboard_has_panels(self):
        script = self.creator.generate_script("action", "Car chase", num_scenes=3)
        board = self.creator.create_storyboard(script)
        assert "panels" in board
        assert len(board["panels"]) == 3

    def test_create_storyboard_panel_has_shot_type(self):
        script = self.creator.generate_script("thriller", "Dark alley scene", num_scenes=2)
        board = self.creator.create_storyboard(script)
        assert "shot_type" in board["panels"][0]

    def test_create_storyboard_panel_has_lighting(self):
        script = self.creator.generate_script("romance", "Candlelit dinner", num_scenes=2)
        board = self.creator.create_storyboard(script)
        assert "lighting" in board["panels"][0]

    def test_suggest_cinematography_returns_dict(self):
        result = self.creator.suggest_cinematography("action")
        assert isinstance(result, dict)

    def test_suggest_cinematography_has_camera_angles(self):
        result = self.creator.suggest_cinematography("dialogue")
        assert "camera_angles" in result
        assert len(result["camera_angles"]) > 0

    def test_suggest_cinematography_has_lighting_setups(self):
        result = self.creator.suggest_cinematography("establishing")
        assert "lighting_setups" in result

    def test_suggest_cinematography_has_techniques(self):
        result = self.creator.suggest_cinematography("action")
        assert "techniques" in result

    def test_suggest_cinematography_unknown_falls_back(self):
        result = self.creator.suggest_cinematography("underwater_scene")
        assert "camera_angles" in result


# ===========================================================================
# ArtCreator tests
# ===========================================================================

class TestArtCreator:
    def setup_method(self):
        self.creator = ArtCreator()

    def test_generate_artwork_returns_dict(self):
        result = self.creator.generate_artwork("digital", "mountain landscape")
        assert isinstance(result, dict)

    def test_generate_artwork_has_description(self):
        result = self.creator.generate_artwork("impressionist", "Paris street scene")
        assert "description" in result
        assert len(result["description"]) > 0

    def test_generate_artwork_has_render_parameters(self):
        result = self.creator.generate_artwork("photorealistic", "portrait of a woman")
        assert "render_parameters" in result

    def test_generate_artwork_unknown_style_falls_back(self):
        result = self.creator.generate_artwork("unknown_style", "anything")
        assert result["style"] == "digital"

    def test_generate_artwork_has_resolution(self):
        result = self.creator.generate_artwork("3d_render", "spaceship")
        assert "resolution" in result

    def test_generate_artwork_has_tags(self):
        result = self.creator.generate_artwork("abstract", "emotions")
        assert "tags" in result
        assert isinstance(result["tags"], list)

    def test_create_3d_model_returns_dict(self):
        result = self.creator.create_3d_model("character")
        assert isinstance(result, dict)

    def test_create_3d_model_has_polygon_count(self):
        result = self.creator.create_3d_model("vehicle", complexity="high")
        assert "polygon_count" in result
        assert result["polygon_count"] == 100_000

    def test_create_3d_model_character_is_rigged(self):
        result = self.creator.create_3d_model("character")
        assert result["rigged"] is True

    def test_create_3d_model_vehicle_not_rigged(self):
        result = self.creator.create_3d_model("vehicle")
        assert result["rigged"] is False

    def test_create_3d_model_has_file_formats(self):
        result = self.creator.create_3d_model("environment")
        assert "file_formats" in result
        assert "FBX" in result["file_formats"]

    def test_create_3d_model_low_complexity(self):
        result = self.creator.create_3d_model("prop", complexity="low")
        assert result["polygon_count"] == 2_000

    def test_suggest_color_palette_returns_dict(self):
        result = self.creator.suggest_color_palette("warm")
        assert isinstance(result, dict)

    def test_suggest_color_palette_has_palette(self):
        result = self.creator.suggest_color_palette("cool")
        assert "palette" in result
        assert len(result["palette"]) > 0

    def test_suggest_color_palette_has_hex_codes(self):
        result = self.creator.suggest_color_palette("dramatic")
        for color in result["palette"]:
            assert "hex" in color
            assert color["hex"].startswith("#")

    def test_suggest_color_palette_has_harmony_type(self):
        result = self.creator.suggest_color_palette("warm")
        assert "harmony_type" in result

    def test_styles_list_not_empty(self):
        assert len(STYLES) >= 7


# ===========================================================================
# ContentStrategyEngine tests
# ===========================================================================

class TestContentStrategyEngine:
    def setup_method(self):
        self.engine = ContentStrategyEngine()

    def test_create_content_calendar_returns_dict(self):
        result = self.engine.create_content_calendar("instagram", "fitness")
        assert isinstance(result, dict)

    def test_create_content_calendar_has_calendar(self):
        result = self.engine.create_content_calendar("tiktok", "cooking", weeks=2)
        assert "calendar" in result
        assert len(result["calendar"]) == 2

    def test_create_content_calendar_has_posts(self):
        result = self.engine.create_content_calendar("youtube", "gaming", weeks=1)
        assert result["calendar"][0]["posts"]

    def test_create_content_calendar_post_has_topic(self):
        result = self.engine.create_content_calendar("linkedin", "career", weeks=1)
        post = result["calendar"][0]["posts"][0]
        assert "topic" in post

    def test_create_content_calendar_has_hashtags(self):
        result = self.engine.create_content_calendar("instagram", "travel", weeks=1)
        post = result["calendar"][0]["posts"][0]
        assert "hashtags" in post

    def test_create_content_calendar_total_posts(self):
        result = self.engine.create_content_calendar("instagram", "beauty", weeks=1)
        assert result["total_posts"] > 0

    def test_create_content_calendar_clamps_weeks(self):
        result = self.engine.create_content_calendar("instagram", "niche", weeks=999)
        assert len(result["calendar"]) <= 12

    def test_generate_viral_post_returns_dict(self):
        result = self.engine.generate_viral_post("instagram", "morning routines")
        assert isinstance(result, dict)

    def test_generate_viral_post_has_caption(self):
        result = self.engine.generate_viral_post("tiktok", "productivity", style="educational")
        assert "caption" in result
        assert len(result["caption"]) > 0

    def test_generate_viral_post_has_hashtags(self):
        result = self.engine.generate_viral_post("twitter", "AI tools")
        assert "hashtags" in result

    def test_generate_viral_post_has_cta(self):
        result = self.engine.generate_viral_post("linkedin", "networking", style="inspirational")
        assert "call_to_action" in result

    def test_generate_viral_post_has_predicted_reach(self):
        result = self.engine.generate_viral_post("instagram", "recipes")
        assert "predicted_reach" in result
        assert result["predicted_reach"] > 0

    def test_analyze_engagement_returns_dict(self):
        post_data = {"likes": 500, "comments": 50, "shares": 25, "reach": 10_000}
        result = self.engine.analyze_engagement(post_data)
        assert isinstance(result, dict)

    def test_analyze_engagement_has_rate(self):
        post_data = {"likes": 100, "comments": 10, "shares": 5, "reach": 1_000}
        result = self.engine.analyze_engagement(post_data)
        assert "engagement_rate_pct" in result

    def test_analyze_engagement_has_grade(self):
        post_data = {"likes": 1000, "comments": 200, "shares": 100, "reach": 5_000}
        result = self.engine.analyze_engagement(post_data)
        assert result["performance_grade"] in ("A", "B", "C")

    def test_analyze_engagement_has_recommendations(self):
        post_data = {"likes": 10, "comments": 1, "shares": 0, "reach": 500}
        result = self.engine.analyze_engagement(post_data)
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)

    def test_platforms_list_not_empty(self):
        assert len(PLATFORMS) >= 6


# ===========================================================================
# MemeGenerator tests
# ===========================================================================

class TestMemeGenerator:
    def setup_method(self):
        self.generator = MemeGenerator()

    def test_generate_meme_returns_dict(self):
        result = self.generator.generate_meme("Monday mornings")
        assert isinstance(result, dict)

    def test_generate_meme_has_template(self):
        result = self.generator.generate_meme("deadlines", style="relatable")
        assert "template" in result

    def test_generate_meme_has_top_text(self):
        result = self.generator.generate_meme("coffee", style="wholesome")
        assert "top_text" in result
        assert "coffee" in result["top_text"].lower()

    def test_generate_meme_has_bottom_text(self):
        result = self.generator.generate_meme("AI tools")
        assert "bottom_text" in result

    def test_generate_meme_has_visual_description(self):
        result = self.generator.generate_meme("taxes")
        assert "visual_description" in result

    def test_generate_meme_has_predicted_engagement(self):
        result = self.generator.generate_meme("procrastination", target_audience="millennials")
        assert "predicted_engagement" in result

    def test_analyze_viral_trends_returns_dict(self):
        result = self.generator.analyze_viral_trends("tiktok")
        assert isinstance(result, dict)

    def test_analyze_viral_trends_has_topics(self):
        result = self.generator.analyze_viral_trends("instagram")
        assert "trending_topics" in result
        assert len(result["trending_topics"]) > 0

    def test_analyze_viral_trends_has_formats(self):
        result = self.generator.analyze_viral_trends("youtube")
        assert "trending_formats" in result

    def test_analyze_viral_trends_has_hashtags(self):
        result = self.generator.analyze_viral_trends("twitter")
        assert "top_hashtags" in result

    def test_analyze_viral_trends_unknown_platform_falls_back(self):
        result = self.generator.analyze_viral_trends("unknown_platform")
        assert "trending_topics" in result

    def test_predict_viral_score_returns_dict(self):
        content = {"platform": "instagram", "hook": "Amazing trick!", "visual": True, "hashtags": True}
        result = self.generator.predict_viral_score(content)
        assert isinstance(result, dict)

    def test_predict_viral_score_range(self):
        content = {"platform": "tiktok", "trending_topic": True, "hook": "Watch this"}
        result = self.generator.predict_viral_score(content)
        assert 0 <= result["viral_score"] <= 100

    def test_predict_viral_score_has_label(self):
        content = {"platform": "instagram"}
        result = self.generator.predict_viral_score(content)
        assert result["prediction_label"] in ("viral", "likely_popular", "average")

    def test_predict_viral_score_has_breakdown(self):
        content = {"hook": "Yes!", "visual": True}
        result = self.generator.predict_viral_score(content)
        assert "score_breakdown" in result

    def test_predict_viral_score_has_improvement_tips(self):
        content = {}
        result = self.generator.predict_viral_score(content)
        assert "improvement_tips" in result
        assert len(result["improvement_tips"]) > 0


# ===========================================================================
# CreativeStudioBot integration tests
# ===========================================================================

class TestCreativeStudioBot:
    def test_init_free_tier(self):
        bot = CreativeStudioBot(tier=Tier.FREE)
        assert bot.tier == Tier.FREE

    def test_init_pro_tier(self):
        bot = CreativeStudioBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_init_enterprise_tier(self):
        bot = CreativeStudioBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_create_music_returns_dict(self):
        bot = CreativeStudioBot(tier=Tier.PRO)
        result = bot.create_music("jazz", "relaxed")
        assert isinstance(result, dict)
        assert result["genre"] == "jazz"

    def test_create_film_script_returns_dict(self):
        bot = CreativeStudioBot(tier=Tier.PRO)
        result = bot.create_film_script("thriller", "A spy uncovers a conspiracy")
        assert isinstance(result, dict)
        assert "scenes" in result

    def test_create_artwork_returns_dict(self):
        bot = CreativeStudioBot(tier=Tier.PRO)
        result = bot.create_artwork("digital", "futuristic city")
        assert isinstance(result, dict)
        assert "description" in result

    def test_create_content_strategy_returns_dict(self):
        bot = CreativeStudioBot(tier=Tier.PRO)
        result = bot.create_content_strategy("instagram", "travel")
        assert isinstance(result, dict)
        assert "calendar" in result

    def test_generate_meme_returns_dict(self):
        bot = CreativeStudioBot(tier=Tier.PRO)
        result = bot.generate_meme("coffee addiction")
        assert isinstance(result, dict)
        assert "template" in result

    def test_daily_limit_enforced_free(self):
        bot = CreativeStudioBot(tier=Tier.FREE)
        bot._daily_count = 3
        with pytest.raises(CreativeStudioBotError, match="Daily creation limit"):
            bot.create_music("pop", "upbeat")

    def test_daily_limit_not_enforced_enterprise(self):
        bot = CreativeStudioBot(tier=Tier.ENTERPRISE)
        bot._daily_count = 10_000
        result = bot.create_music("rock", "powerful")
        assert isinstance(result, dict)

    def test_get_creative_dashboard_returns_dict(self):
        bot = CreativeStudioBot(tier=Tier.FREE)
        dashboard = bot.get_creative_dashboard()
        assert isinstance(dashboard, dict)
        assert dashboard["bot_name"] == "Creative Studio Bot"

    def test_dashboard_shows_tier(self):
        bot = CreativeStudioBot(tier=Tier.PRO)
        dashboard = bot.get_creative_dashboard()
        assert dashboard["tier"] == "pro"

    def test_dashboard_creations_remaining_free(self):
        bot = CreativeStudioBot(tier=Tier.FREE)
        bot._daily_count = 1
        dashboard = bot.get_creative_dashboard()
        assert dashboard["creations_remaining"] == 2

    def test_dashboard_creations_remaining_enterprise_unlimited(self):
        bot = CreativeStudioBot(tier=Tier.ENTERPRISE)
        dashboard = bot.get_creative_dashboard()
        assert dashboard["creations_remaining"] == "unlimited"

    def test_dashboard_has_modules(self):
        bot = CreativeStudioBot()
        dashboard = bot.get_creative_dashboard()
        assert "modules" in dashboard
        assert "MusicCreator" in dashboard["modules"]

    def test_describe_tier_returns_string(self):
        bot = CreativeStudioBot(tier=Tier.FREE)
        description = bot.describe_tier()
        assert isinstance(description, str)
        assert "Free" in description

    def test_daily_count_increments(self):
        bot = CreativeStudioBot(tier=Tier.PRO)
        initial = bot._daily_count
        bot.create_music("pop", "happy")
        assert bot._daily_count == initial + 1

    def test_pro_limit_50(self):
        bot = CreativeStudioBot(tier=Tier.PRO)
        bot._daily_count = 50
        with pytest.raises(CreativeStudioBotError):
            bot.create_artwork("abstract", "chaos")

    def test_framework_flow_attribute(self):
        from framework import GlobalAISourcesFlow
        bot = CreativeStudioBot()
        assert hasattr(bot, "flow")
        assert isinstance(bot.flow, GlobalAISourcesFlow)

    def test_framework_validate(self):
        bot = CreativeStudioBot()
        assert bot.flow.validate() is True
