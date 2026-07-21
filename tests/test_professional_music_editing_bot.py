"""
Tests for the Professional Music Editing Bot.

Validates:
  1. Tiers — feature flags, monthly limits, tier info
  2. ProfessionalMusicEditingBot — load_project, add_track, apply_effect,
     compose_with_ai, reduce_noise, master_track, export_project, get_studio_dashboard
  3. Tier gating — FREE basic editing/mp3 only, ENTERPRISE mastering and DAW compatibility
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.professional_music_editing_bot.tiers import (
    Tier,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    BOT_FEATURES,
    MONTHLY_LIMITS,
    DAILY_LIMITS,
    get_bot_tier_info,
    FEATURE_BASIC_EDITING,
    FEATURE_MP3_EXPORT,
    FEATURE_MULTI_TRACK_EDITING,
    FEATURE_AI_COMPOSITION,
    FEATURE_NOISE_REDUCTION,
    FEATURE_WAV_AIFF_EXPORT,
    FEATURE_UNLIMITED_TRACKS,
    FEATURE_AI_MASTERING,
    FEATURE_DAW_COMPATIBILITY,
    FEATURE_REAL_TIME_COLLABORATION,
    FEATURE_COMMERCIAL_RIGHTS,
)
from bots.professional_music_editing_bot.professional_music_editing_bot import (
    ProfessionalMusicEditingBot,
    ProfessionalMusicEditingBotError,
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

    def test_free_has_basic_editing(self):
        assert FEATURE_BASIC_EDITING in BOT_FEATURES[Tier.FREE.value]

    def test_free_has_mp3_export(self):
        assert FEATURE_MP3_EXPORT in BOT_FEATURES[Tier.FREE.value]

    def test_pro_has_multi_track(self):
        assert FEATURE_MULTI_TRACK_EDITING in BOT_FEATURES[Tier.PRO.value]

    def test_pro_has_ai_composition(self):
        assert FEATURE_AI_COMPOSITION in BOT_FEATURES[Tier.PRO.value]

    def test_pro_has_noise_reduction(self):
        assert FEATURE_NOISE_REDUCTION in BOT_FEATURES[Tier.PRO.value]

    def test_enterprise_has_ai_mastering(self):
        assert FEATURE_AI_MASTERING in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_enterprise_has_daw_compatibility(self):
        assert FEATURE_DAW_COMPATIBILITY in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_enterprise_has_commercial_rights(self):
        assert FEATURE_COMMERCIAL_RIGHTS in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_free_lacks_ai_mastering(self):
        assert FEATURE_AI_MASTERING not in BOT_FEATURES[Tier.FREE.value]

    def test_monthly_limit_free(self):
        assert MONTHLY_LIMITS[Tier.FREE.value] == 3

    def test_monthly_limit_pro(self):
        assert MONTHLY_LIMITS[Tier.PRO.value] == 30

    def test_monthly_limit_enterprise_unlimited(self):
        assert MONTHLY_LIMITS[Tier.ENTERPRISE.value] is None

    def test_tier_info_returns_dict(self):
        info = get_bot_tier_info(Tier.PRO)
        assert isinstance(info, dict)
        assert "features" in info


# ===========================================================================
# Instantiation
# ===========================================================================

class TestInit:
    def test_default_tier_is_free(self):
        bot = ProfessionalMusicEditingBot()
        assert bot.tier == Tier.FREE

    def test_monthly_count_starts_zero(self):
        bot = ProfessionalMusicEditingBot()
        assert bot._monthly_count == 0


# ===========================================================================
# load_project
# ===========================================================================

class TestLoadProject:
    def test_free_can_load_project(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.FREE)
        result = bot.load_project()
        assert isinstance(result, dict)
        assert "project_id" in result

    def test_has_sample_rate(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.FREE)
        result = bot.load_project()
        assert "sample_rate" in result

    def test_has_tracks(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.FREE)
        result = bot.load_project()
        assert "tracks" in result


# ===========================================================================
# add_track
# ===========================================================================

class TestAddTrack:
    def test_free_can_add_track(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.FREE)
        result = bot.add_track("drums")
        assert isinstance(result, dict)
        assert "track_id" in result

    def test_has_volume(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.FREE)
        result = bot.add_track("bass")
        assert "volume_db" in result

    def test_has_pan(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.FREE)
        result = bot.add_track("guitar")
        assert "pan" in result

    def test_track_type_echoed(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.PRO)
        result = bot.add_track("vocals")
        assert result["track_type"] == "vocals"


# ===========================================================================
# apply_effect
# ===========================================================================

class TestApplyEffect:
    def test_free_can_apply_effect(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.FREE)
        result = bot.apply_effect("track_001", "reverb")
        assert isinstance(result, dict)
        assert "status" in result

    def test_effect_echoed(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.PRO)
        result = bot.apply_effect("track_001", "eq", {"low_cut": 80})
        assert result["effect"] == "eq"


# ===========================================================================
# compose_with_ai
# ===========================================================================

class TestComposeWithAI:
    def test_pro_can_compose(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.PRO)
        result = bot.compose_with_ai("jazz", "relaxed")
        assert isinstance(result, dict)
        assert "tempo" in result

    def test_has_key(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.PRO)
        result = bot.compose_with_ai("pop", "upbeat")
        assert "key" in result

    def test_has_tracks(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.PRO)
        result = bot.compose_with_ai("electronic", "dark", duration_sec=30)
        assert "tracks" in result

    def test_free_cannot_compose_with_ai(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.FREE)
        with pytest.raises(ProfessionalMusicEditingBotError):
            bot.compose_with_ai("rock", "energetic")


# ===========================================================================
# reduce_noise
# ===========================================================================

class TestReduceNoise:
    def test_pro_can_reduce_noise(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.PRO)
        result = bot.reduce_noise("track_001")
        assert isinstance(result, dict)
        assert "reduction_db" in result

    def test_has_algorithm(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.PRO)
        result = bot.reduce_noise("track_001")
        assert "algorithm" in result

    def test_free_cannot_reduce_noise(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.FREE)
        with pytest.raises(ProfessionalMusicEditingBotError):
            bot.reduce_noise("track_001")


# ===========================================================================
# master_track
# ===========================================================================

class TestMasterTrack:
    def test_enterprise_can_master(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.ENTERPRISE)
        proj = bot.load_project()
        result = bot.master_track(proj["project_id"])
        assert isinstance(result, dict)

    def test_free_cannot_master(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.FREE)
        with pytest.raises(ProfessionalMusicEditingBotError):
            bot.master_track("proj_001")


# ===========================================================================
# export_project
# ===========================================================================

class TestExportProject:
    def test_free_can_export_mp3(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.FREE)
        proj = bot.load_project()
        result = bot.export_project(proj["project_id"], export_format="MP3")
        assert isinstance(result, dict)
        assert "file_url" in result

    def test_enterprise_export_with_daw(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.ENTERPRISE)
        proj = bot.load_project()
        result = bot.export_project(proj["project_id"], export_format="WAV", daw_compatible="FL Studio")
        assert result["daw_compatible"] == "FL Studio"

    def test_has_file_url(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.PRO)
        proj = bot.load_project()
        result = bot.export_project(proj["project_id"], export_format="WAV")
        assert result["file_url"].startswith("https://")


# ===========================================================================
# get_studio_dashboard
# ===========================================================================

class TestGetStudioDashboard:
    def test_returns_dict(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.PRO)
        assert isinstance(bot.get_studio_dashboard(), dict)

    def test_contains_bot_name(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.PRO)
        assert bot.get_studio_dashboard()["bot_name"] == "ProfessionalMusicEditingBot"

    def test_enterprise_remaining_unlimited(self):
        bot = ProfessionalMusicEditingBot(tier=Tier.ENTERPRISE)
        assert bot.get_studio_dashboard()["remaining"] == "unlimited"
