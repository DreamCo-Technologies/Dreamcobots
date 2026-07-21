"""
Tests for the Professional Video Editing Bot.

Validates:
  1. Tiers — feature flags, monthly limits, tier info
  2. ProfessionalVideoEditingBot — load_project, add_clip, apply_transition,
     apply_color_grade, apply_motion_tracking, optimize_render, export_project,
     get_studio_dashboard
  3. Tier gating — FREE basic/1080p, PRO AI transitions/color, ENTERPRISE NLE+render
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.professional_video_editing_bot.tiers import (
    Tier,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    BOT_FEATURES,
    MONTHLY_LIMITS,
    DAILY_LIMITS,
    get_bot_tier_info,
    FEATURE_BASIC_EDITING,
    FEATURE_MP4_1080P_EXPORT,
    FEATURE_AI_TRANSITIONS,
    FEATURE_COLOR_GRADING,
    FEATURE_MOTION_TRACKING,
    FEATURE_EXPORT_4K,
    FEATURE_RENDER_OPTIMIZATION,
    FEATURE_NLE_COMPATIBILITY,
    FEATURE_REAL_TIME_COLLABORATION,
    FEATURE_COMMERCIAL_RIGHTS,
)
from bots.professional_video_editing_bot.professional_video_editing_bot import (
    ProfessionalVideoEditingBot,
    ProfessionalVideoEditingBotError,
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

    def test_free_has_1080p_export(self):
        assert FEATURE_MP4_1080P_EXPORT in BOT_FEATURES[Tier.FREE.value]

    def test_pro_has_ai_transitions(self):
        assert FEATURE_AI_TRANSITIONS in BOT_FEATURES[Tier.PRO.value]

    def test_pro_has_color_grading(self):
        assert FEATURE_COLOR_GRADING in BOT_FEATURES[Tier.PRO.value]

    def test_pro_has_motion_tracking(self):
        assert FEATURE_MOTION_TRACKING in BOT_FEATURES[Tier.PRO.value]

    def test_enterprise_has_render_optimization(self):
        assert FEATURE_RENDER_OPTIMIZATION in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_enterprise_has_nle_compatibility(self):
        assert FEATURE_NLE_COMPATIBILITY in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_enterprise_has_commercial_rights(self):
        assert FEATURE_COMMERCIAL_RIGHTS in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_free_lacks_nle_compatibility(self):
        assert FEATURE_NLE_COMPATIBILITY not in BOT_FEATURES[Tier.FREE.value]

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
        bot = ProfessionalVideoEditingBot()
        assert bot.tier == Tier.FREE

    def test_monthly_count_starts_zero(self):
        bot = ProfessionalVideoEditingBot()
        assert bot._monthly_count == 0


# ===========================================================================
# load_project
# ===========================================================================

class TestLoadProject:
    def test_free_can_load_project(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.FREE)
        result = bot.load_project()
        assert isinstance(result, dict)
        assert "project_id" in result

    def test_has_clips(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.FREE)
        result = bot.load_project()
        assert "clips" in result

    def test_has_fps(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.FREE)
        result = bot.load_project()
        assert "fps" in result


# ===========================================================================
# add_clip
# ===========================================================================

class TestAddClip:
    def test_free_can_add_clip(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.FREE)
        result = bot.add_clip("footage.mp4")
        assert isinstance(result, dict)
        assert "clip_id" in result

    def test_clip_source_echoed(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.PRO)
        result = bot.add_clip("scene1.mp4", 0.0)
        assert result["clip_source"] == "scene1.mp4"

    def test_has_duration(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.FREE)
        result = bot.add_clip("clip.mp4")
        assert "duration_sec" in result

    def test_position_echoed(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.FREE)
        result = bot.add_clip("clip.mp4", 5.5)
        assert result["position_sec"] == 5.5


# ===========================================================================
# apply_transition
# ===========================================================================

class TestApplyTransition:
    def test_pro_can_apply_transition(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.PRO)
        result = bot.apply_transition("clip_001", "clip_002", "dissolve")
        assert isinstance(result, dict)
        assert "status" in result

    def test_transition_echoed(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.PRO)
        result = bot.apply_transition("a", "b", "wipe")
        assert result["transition"] == "wipe"

    def test_has_ai_optimized(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.PRO)
        result = bot.apply_transition("a", "b", "crossfade")
        assert "ai_optimized" in result

    def test_free_cannot_apply_ai_transition(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.FREE)
        with pytest.raises(ProfessionalVideoEditingBotError):
            bot.apply_transition("a", "b", "dissolve")


# ===========================================================================
# apply_color_grade
# ===========================================================================

class TestApplyColorGrade:
    def test_pro_can_color_grade(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.PRO)
        result = bot.apply_color_grade("clip_001", "cinematic")
        assert isinstance(result, dict)
        assert "lut_applied" in result

    def test_preset_echoed(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.PRO)
        result = bot.apply_color_grade("clip_001", "vintage")
        assert result["preset"] == "vintage"

    def test_free_cannot_color_grade(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.FREE)
        with pytest.raises(ProfessionalVideoEditingBotError):
            bot.apply_color_grade("clip_001", "warm")


# ===========================================================================
# apply_motion_tracking
# ===========================================================================

class TestApplyMotionTracking:
    def test_pro_can_motion_track(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.PRO)
        result = bot.apply_motion_tracking("clip_001", "person")
        assert isinstance(result, dict)

    def test_free_cannot_motion_track(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.FREE)
        with pytest.raises(ProfessionalVideoEditingBotError):
            bot.apply_motion_tracking("clip_001", "car")


# ===========================================================================
# optimize_render
# ===========================================================================

class TestOptimizeRender:
    def test_enterprise_can_optimize(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.ENTERPRISE)
        proj = bot.load_project()
        result = bot.optimize_render(proj["project_id"])
        assert isinstance(result, dict)

    def test_free_cannot_optimize(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.FREE)
        with pytest.raises(ProfessionalVideoEditingBotError):
            bot.optimize_render("proj_001")


# ===========================================================================
# export_project
# ===========================================================================

class TestExportProject:
    def test_free_can_export(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.FREE)
        proj = bot.load_project()
        result = bot.export_project(proj["project_id"])
        assert isinstance(result, dict)
        assert "file_url" in result

    def test_enterprise_export_with_nle(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.ENTERPRISE)
        proj = bot.load_project()
        result = bot.export_project(proj["project_id"], nle_compatible="Adobe Premiere")
        assert result["nle_compatible"] == "Adobe Premiere"

    def test_has_file_url(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.PRO)
        proj = bot.load_project()
        result = bot.export_project(proj["project_id"], export_format="MP4")
        assert result["file_url"].startswith("https://")


# ===========================================================================
# get_studio_dashboard
# ===========================================================================

class TestGetStudioDashboard:
    def test_returns_dict(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.PRO)
        assert isinstance(bot.get_studio_dashboard(), dict)

    def test_contains_bot_name(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.PRO)
        assert bot.get_studio_dashboard()["bot_name"] == "ProfessionalVideoEditingBot"

    def test_enterprise_remaining_unlimited(self):
        bot = ProfessionalVideoEditingBot(tier=Tier.ENTERPRISE)
        assert bot.get_studio_dashboard()["remaining"] == "unlimited"
