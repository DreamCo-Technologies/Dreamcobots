"""
Tests for the Buddy Media Transformation Bot.

Validates:
  1. Tiers — feature flags, daily limits, tier info
  2. BuddyMediaTransformationBot — text_to_music, create_video, create_personalized_song,
     create_avatar_video, customize_visual_style, get_media_dashboard
  3. Tier gating — FREE watermark, ENTERPRISE voice cloning and avatar
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.buddy_media_transformation_bot.tiers import (
    Tier,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    BOT_FEATURES,
    DAILY_LIMITS,
    get_bot_tier_info,
    FEATURE_TEXT_TO_MUSIC_BASIC,
    FEATURE_TEXT_TO_MUSIC_ADVANCED,
    FEATURE_VOICE_INTEGRATION,
    FEATURE_VIDEO_CREATION,
    FEATURE_USER_VOICE_CLONING,
    FEATURE_AVATAR_CREATION,
    FEATURE_CUSTOM_VISUAL_STYLES,
    FEATURE_COMMERCIAL_RIGHTS,
    FEATURE_WATERMARK,
)
from bots.buddy_media_transformation_bot.buddy_media_transformation_bot import (
    BuddyMediaTransformationBot,
    BuddyMediaTransformationBotError,
)


# ===========================================================================
# Tier tests
# ===========================================================================

class TestTiers:
    def test_tier_enum_values(self):
        assert Tier.FREE.value == "free"
        assert Tier.PRO.value == "pro"
        assert Tier.ENTERPRISE.value == "enterprise"

    def test_three_tiers(self):
        assert len(list_tiers()) == 3

    def test_free_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_upgrade_free_to_pro(self):
        assert get_upgrade_path(Tier.FREE).tier == Tier.PRO

    def test_upgrade_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_free_has_text_to_music_basic(self):
        assert FEATURE_TEXT_TO_MUSIC_BASIC in BOT_FEATURES[Tier.FREE.value]

    def test_free_has_watermark(self):
        assert FEATURE_WATERMARK in BOT_FEATURES[Tier.FREE.value]

    def test_pro_has_voice_integration(self):
        assert FEATURE_VOICE_INTEGRATION in BOT_FEATURES[Tier.PRO.value]

    def test_pro_has_video_creation(self):
        assert FEATURE_VIDEO_CREATION in BOT_FEATURES[Tier.PRO.value]

    def test_enterprise_has_voice_cloning(self):
        assert FEATURE_USER_VOICE_CLONING in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_enterprise_has_avatar_creation(self):
        assert FEATURE_AVATAR_CREATION in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_enterprise_has_commercial_rights(self):
        assert FEATURE_COMMERCIAL_RIGHTS in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_daily_limit_free(self):
        assert DAILY_LIMITS[Tier.FREE.value] == 3

    def test_daily_limit_pro(self):
        assert DAILY_LIMITS[Tier.PRO.value] == 20

    def test_daily_limit_enterprise_unlimited(self):
        assert DAILY_LIMITS[Tier.ENTERPRISE.value] is None

    def test_tier_info_returns_dict(self):
        info = get_bot_tier_info(Tier.PRO)
        assert isinstance(info, dict)
        assert "features" in info


# ===========================================================================
# Instantiation
# ===========================================================================

class TestInit:
    def test_default_tier_is_free(self):
        bot = BuddyMediaTransformationBot()
        assert bot.tier == Tier.FREE

    def test_daily_count_starts_zero(self):
        bot = BuddyMediaTransformationBot()
        assert bot._daily_count == 0


# ===========================================================================
# text_to_music
# ===========================================================================

class TestTextToMusic:
    def test_free_can_create_basic_music(self):
        bot = BuddyMediaTransformationBot(tier=Tier.FREE)
        result = bot.text_to_music("I love the rain")
        assert isinstance(result, dict)
        assert "audio_url" in result

    def test_returns_audio_url(self):
        bot = BuddyMediaTransformationBot(tier=Tier.PRO)
        result = bot.text_to_music("Walking on sunshine", "pop")
        assert result["audio_url"].startswith("https://")

    def test_has_bpm(self):
        bot = BuddyMediaTransformationBot(tier=Tier.PRO)
        result = bot.text_to_music("Night vibes", "jazz")
        assert "bpm" in result
        assert isinstance(result["bpm"], int)

    def test_free_watermark_applied(self):
        bot = BuddyMediaTransformationBot(tier=Tier.FREE)
        result = bot.text_to_music("Hello world")
        assert result["watermarked"] is True

    def test_enterprise_no_watermark(self):
        bot = BuddyMediaTransformationBot(tier=Tier.ENTERPRISE)
        result = bot.text_to_music("Hello world")
        assert result["watermarked"] is False

    def test_increments_daily_count(self):
        bot = BuddyMediaTransformationBot(tier=Tier.PRO)
        bot.text_to_music("test")
        assert bot._daily_count == 1


# ===========================================================================
# create_video
# ===========================================================================

class TestCreateVideo:
    def test_pro_can_create_video(self):
        bot = BuddyMediaTransformationBot(tier=Tier.PRO)
        result = bot.create_video("My story script")
        assert isinstance(result, dict)
        assert "video_url" in result

    def test_has_duration(self):
        bot = BuddyMediaTransformationBot(tier=Tier.PRO)
        result = bot.create_video("Short story")
        assert "duration_secs" in result

    def test_has_resolution(self):
        bot = BuddyMediaTransformationBot(tier=Tier.PRO)
        result = bot.create_video("Test script")
        assert "resolution" in result

    def test_free_cannot_create_video(self):
        bot = BuddyMediaTransformationBot(tier=Tier.FREE)
        with pytest.raises(BuddyMediaTransformationBotError):
            bot.create_video("Script")


# ===========================================================================
# create_personalized_song
# ===========================================================================

class TestCreatePersonalizedSong:
    def test_enterprise_can_create_personalized_song(self):
        bot = BuddyMediaTransformationBot(tier=Tier.ENTERPRISE)
        result = bot.create_personalized_song("Love song lyrics", "voice_001", "pop")
        assert isinstance(result, dict)
        assert "audio_url" in result

    def test_has_genre(self):
        bot = BuddyMediaTransformationBot(tier=Tier.ENTERPRISE)
        result = bot.create_personalized_song("lyrics", "voice_001", "jazz")
        assert result["genre"] == "jazz"

    def test_free_cannot_create_personalized_song(self):
        bot = BuddyMediaTransformationBot(tier=Tier.FREE)
        with pytest.raises(BuddyMediaTransformationBotError):
            bot.create_personalized_song("lyrics", "voice_001", "pop")


# ===========================================================================
# create_avatar_video
# ===========================================================================

class TestCreateAvatarVideo:
    def test_enterprise_can_create_avatar_video(self):
        bot = BuddyMediaTransformationBot(tier=Tier.ENTERPRISE)
        result = bot.create_avatar_video("Hello, I am here!", "user_face.jpg")
        assert isinstance(result, dict)
        assert "avatar_video_url" in result or "video_url" in result

    def test_has_lip_sync(self):
        bot = BuddyMediaTransformationBot(tier=Tier.ENTERPRISE)
        result = bot.create_avatar_video("Test script", "face.png")
        assert "lip_sync_quality" in result or "lip_sync_accuracy" in result

    def test_pro_cannot_create_avatar_video(self):
        bot = BuddyMediaTransformationBot(tier=Tier.PRO)
        with pytest.raises(BuddyMediaTransformationBotError):
            bot.create_avatar_video("script", "face.jpg")


# ===========================================================================
# get_media_dashboard
# ===========================================================================

class TestGetMediaDashboard:
    def test_returns_dict(self):
        bot = BuddyMediaTransformationBot(tier=Tier.PRO)
        assert isinstance(bot.get_media_dashboard(), dict)

    def test_contains_bot_name(self):
        bot = BuddyMediaTransformationBot(tier=Tier.PRO)
        assert bot.get_media_dashboard()["bot_name"] == "BuddyMediaTransformationBot"

    def test_enterprise_remaining_is_unlimited(self):
        bot = BuddyMediaTransformationBot(tier=Tier.ENTERPRISE)
        assert bot.get_media_dashboard()["remaining"] == "unlimited"

    def test_daily_limit_enforced(self):
        bot = BuddyMediaTransformationBot(tier=Tier.FREE)
        bot._daily_count = 3
        with pytest.raises(BuddyMediaTransformationBotError):
            bot.text_to_music("Over limit")
