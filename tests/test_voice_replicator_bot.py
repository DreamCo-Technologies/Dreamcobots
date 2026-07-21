"""
Tests for the Voice Replicator Bot.

Validates:
  1. Tiers — feature flags, daily limits, tier info
  2. VoiceReplicatorBot — synthesize_speech, clone_voice, translate_and_speak,
     list_supported_languages, get_voice_dashboard
  3. Tier gating — FREE cannot clone voices, ENTERPRISE can
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.voice_replicator_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    BOT_FEATURES,
    DAILY_LIMITS,
    get_bot_tier_info,
    FEATURE_BASIC_TTS,
    FEATURE_VOICE_CLONING,
    FEATURE_REAL_TIME_TRANSLATION,
    FEATURE_LANGUAGE_FULL,
    FEATURE_COMMERCIAL_RIGHTS,
)
from bots.voice_replicator_bot.voice_replicator_bot import (
    VoiceReplicatorBot,
    VoiceReplicatorBotError,
    ALL_LANGUAGES,
    BASIC_LANGUAGES,
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
        assert len(list_tiers()) == 3

    def test_free_tier_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly > 0.0

    def test_enterprise_tier_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly > 0.0

    def test_upgrade_path_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_path_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_free_features_contains_basic_tts(self):
        assert FEATURE_BASIC_TTS in BOT_FEATURES[Tier.FREE.value]

    def test_enterprise_features_contains_voice_cloning(self):
        assert FEATURE_VOICE_CLONING in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_enterprise_features_contains_real_time_translation(self):
        assert FEATURE_REAL_TIME_TRANSLATION in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_enterprise_features_contains_commercial_rights(self):
        assert FEATURE_COMMERCIAL_RIGHTS in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_free_features_do_not_contain_voice_cloning(self):
        assert FEATURE_VOICE_CLONING not in BOT_FEATURES[Tier.FREE.value]

    def test_daily_limit_free(self):
        assert DAILY_LIMITS[Tier.FREE.value] == 10

    def test_daily_limit_pro(self):
        assert DAILY_LIMITS[Tier.PRO.value] == 200

    def test_daily_limit_enterprise_unlimited(self):
        assert DAILY_LIMITS[Tier.ENTERPRISE.value] is None

    def test_get_bot_tier_info_returns_dict(self):
        info = get_bot_tier_info(Tier.PRO)
        assert isinstance(info, dict)
        assert "features" in info
        assert "daily_limit" in info

    def test_get_bot_tier_info_free_no_commercial_rights(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["commercial_rights"] is False

    def test_get_bot_tier_info_enterprise_has_commercial_rights(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert info["commercial_rights"] is True


# ===========================================================================
# Language list tests
# ===========================================================================

class TestLanguageLists:
    def test_all_languages_has_25(self):
        assert len(ALL_LANGUAGES) >= 25

    def test_basic_languages_is_subset(self):
        assert set(BASIC_LANGUAGES).issubset(set(ALL_LANGUAGES))

    def test_english_in_all_languages(self):
        assert "en-US" in ALL_LANGUAGES

    def test_basic_languages_count(self):
        assert len(BASIC_LANGUAGES) == 5


# ===========================================================================
# VoiceReplicatorBot — instantiation
# ===========================================================================

class TestVoiceReplicatorBotInit:
    def test_default_tier_is_free(self):
        bot = VoiceReplicatorBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier_init(self):
        bot = VoiceReplicatorBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier_init(self):
        bot = VoiceReplicatorBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_daily_count_starts_at_zero(self):
        bot = VoiceReplicatorBot()
        assert bot._daily_count == 0


# ===========================================================================
# synthesize_speech
# ===========================================================================

class TestSynthesizeSpeech:
    def setup_method(self):
        self.bot = VoiceReplicatorBot(tier=Tier.PRO)

    def test_returns_dict(self):
        result = self.bot.synthesize_speech("Hello world")
        assert isinstance(result, dict)

    def test_contains_text(self):
        result = self.bot.synthesize_speech("Hello world")
        assert result["text"] == "Hello world"

    def test_contains_language(self):
        result = self.bot.synthesize_speech("Hola", language="es-ES")
        assert result["language"] == "es-ES"

    def test_contains_audio_url(self):
        result = self.bot.synthesize_speech("Test")
        assert "audio_url" in result
        assert result["audio_url"].startswith("https://")

    def test_contains_format(self):
        result = self.bot.synthesize_speech("Test")
        assert result["format"] == "WAV"

    def test_pro_quality_is_hd(self):
        result = self.bot.synthesize_speech("Quality test")
        assert result["quality"] == "HD"

    def test_free_quality_is_standard(self):
        bot = VoiceReplicatorBot(tier=Tier.FREE)
        result = bot.synthesize_speech("Quality test")
        assert result["quality"] == "Standard"

    def test_increments_daily_count(self):
        self.bot.synthesize_speech("Count test")
        assert self.bot._daily_count == 1

    def test_default_language_is_en_us(self):
        result = self.bot.synthesize_speech("Default lang")
        assert result["language"] == "en-US"


# ===========================================================================
# clone_voice — ENTERPRISE only
# ===========================================================================

class TestCloneVoice:
    def test_enterprise_can_clone_voice(self):
        bot = VoiceReplicatorBot(tier=Tier.ENTERPRISE)
        result = bot.clone_voice("https://example.com/audio.wav")
        assert isinstance(result, dict)
        assert "voice_id" in result

    def test_clone_voice_has_quality_score(self):
        bot = VoiceReplicatorBot(tier=Tier.ENTERPRISE)
        result = bot.clone_voice("https://example.com/audio.wav")
        assert "quality_score" in result
        assert 0 < result["quality_score"] <= 1.0

    def test_clone_voice_has_characteristics(self):
        bot = VoiceReplicatorBot(tier=Tier.ENTERPRISE)
        result = bot.clone_voice("https://example.com/audio.wav")
        assert "speaker_characteristics" in result

    def test_free_cannot_clone_voice(self):
        bot = VoiceReplicatorBot(tier=Tier.FREE)
        with pytest.raises(VoiceReplicatorBotError):
            bot.clone_voice("https://example.com/audio.wav")

    def test_pro_cannot_clone_voice(self):
        bot = VoiceReplicatorBot(tier=Tier.PRO)
        with pytest.raises(VoiceReplicatorBotError):
            bot.clone_voice("https://example.com/audio.wav")


# ===========================================================================
# translate_and_speak — ENTERPRISE only
# ===========================================================================

class TestTranslateAndSpeak:
    def test_enterprise_can_translate_and_speak(self):
        bot = VoiceReplicatorBot(tier=Tier.ENTERPRISE)
        result = bot.translate_and_speak("Hello", "en-US", ["es-ES", "fr-FR"])
        assert isinstance(result, dict)
        assert "translations" in result

    def test_translations_count_matches_target_langs(self):
        bot = VoiceReplicatorBot(tier=Tier.ENTERPRISE)
        result = bot.translate_and_speak("Hi", "en-US", ["es-ES", "de-DE", "ja-JP"])
        assert len(result["translations"]) == 3

    def test_translations_have_audio_url(self):
        bot = VoiceReplicatorBot(tier=Tier.ENTERPRISE)
        result = bot.translate_and_speak("Hi", "en-US", ["fr-FR"])
        assert result["translations"][0]["audio_url"].startswith("https://")

    def test_free_cannot_translate_and_speak(self):
        bot = VoiceReplicatorBot(tier=Tier.FREE)
        with pytest.raises(VoiceReplicatorBotError):
            bot.translate_and_speak("Hi", "en-US", ["es-ES"])


# ===========================================================================
# list_supported_languages
# ===========================================================================

class TestListSupportedLanguages:
    def test_free_returns_5_languages(self):
        bot = VoiceReplicatorBot(tier=Tier.FREE)
        langs = bot.list_supported_languages()
        assert len(langs) == 5

    def test_pro_returns_all_languages(self):
        bot = VoiceReplicatorBot(tier=Tier.PRO)
        langs = bot.list_supported_languages()
        assert len(langs) >= 25

    def test_enterprise_returns_all_languages(self):
        bot = VoiceReplicatorBot(tier=Tier.ENTERPRISE)
        langs = bot.list_supported_languages()
        assert len(langs) >= 25


# ===========================================================================
# get_voice_dashboard
# ===========================================================================

class TestGetVoiceDashboard:
    def test_returns_dict(self):
        bot = VoiceReplicatorBot(tier=Tier.PRO)
        dashboard = bot.get_voice_dashboard()
        assert isinstance(dashboard, dict)

    def test_contains_bot_name(self):
        bot = VoiceReplicatorBot(tier=Tier.PRO)
        assert bot.get_voice_dashboard()["bot_name"] == "VoiceReplicatorBot"

    def test_contains_tier(self):
        bot = VoiceReplicatorBot(tier=Tier.FREE)
        assert bot.get_voice_dashboard()["tier"] == "free"

    def test_enterprise_remaining_is_unlimited(self):
        bot = VoiceReplicatorBot(tier=Tier.ENTERPRISE)
        assert bot.get_voice_dashboard()["remaining"] == "unlimited"

    def test_remaining_decrements_with_usage(self):
        bot = VoiceReplicatorBot(tier=Tier.FREE)
        bot.synthesize_speech("hi")
        dash = bot.get_voice_dashboard()
        assert dash["count_today"] == 1

    def test_daily_limit_enforcement(self):
        bot = VoiceReplicatorBot(tier=Tier.FREE)
        bot._daily_count = 10
        with pytest.raises(VoiceReplicatorBotError):
            bot.synthesize_speech("Over limit")
