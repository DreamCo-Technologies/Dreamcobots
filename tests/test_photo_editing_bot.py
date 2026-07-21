"""
Tests for the Photo Editing Bot.

Validates:
  1. Tiers — feature flags, daily limits, tier info
  2. PhotoEditingBot — edit_photo, remove_noise, remove_background, apply_filter,
     batch_edit, cartoonify, create_caricature, generate_animation,
     generate_cartoon_frame, get_editing_dashboard
  3. Tier gating — FREE basic only, PRO cartoon/caricature, ENTERPRISE animation
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.photo_editing_bot.tiers import (
    Tier,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    BOT_FEATURES,
    DAILY_LIMITS,
    get_bot_tier_info,
    FEATURE_BASIC_EDITING,
    FEATURE_BACKGROUND_REMOVAL,
    FEATURE_FILTERS,
    FEATURE_JPG_PNG_EXPORT,
    FEATURE_NOISE_REMOVAL,
    FEATURE_BATCH_EDITING,
    FEATURE_CARTOON_CONVERSION,
    FEATURE_CARICATURE,
    FEATURE_HD_EXPORT,
    FEATURE_ANIMATION_GENERATION,
    FEATURE_CARTOON_FRAME_GENERATION,
    FEATURE_FRAME_BY_FRAME_AI,
    FEATURE_COMMERCIAL_RIGHTS,
    FEATURE_WHITE_LABEL,
)
from bots.photo_editing_bot.photo_editing_bot import (
    PhotoEditingBot,
    PhotoEditingBotError,
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

    def test_free_has_background_removal(self):
        assert FEATURE_BACKGROUND_REMOVAL in BOT_FEATURES[Tier.FREE.value]

    def test_free_has_filters(self):
        assert FEATURE_FILTERS in BOT_FEATURES[Tier.FREE.value]

    def test_pro_has_noise_removal(self):
        assert FEATURE_NOISE_REMOVAL in BOT_FEATURES[Tier.PRO.value]

    def test_pro_has_cartoon_conversion(self):
        assert FEATURE_CARTOON_CONVERSION in BOT_FEATURES[Tier.PRO.value]

    def test_pro_has_caricature(self):
        assert FEATURE_CARICATURE in BOT_FEATURES[Tier.PRO.value]

    def test_enterprise_has_animation_generation(self):
        assert FEATURE_ANIMATION_GENERATION in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_enterprise_has_cartoon_frame_generation(self):
        assert FEATURE_CARTOON_FRAME_GENERATION in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_enterprise_has_commercial_rights(self):
        assert FEATURE_COMMERCIAL_RIGHTS in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_free_lacks_animation(self):
        assert FEATURE_ANIMATION_GENERATION not in BOT_FEATURES[Tier.FREE.value]

    def test_daily_limit_free(self):
        assert DAILY_LIMITS[Tier.FREE.value] == 10

    def test_daily_limit_pro(self):
        assert DAILY_LIMITS[Tier.PRO.value] == 100

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
        bot = PhotoEditingBot()
        assert bot.tier == Tier.FREE

    def test_daily_count_starts_zero(self):
        bot = PhotoEditingBot()
        assert bot._daily_count == 0


# ===========================================================================
# edit_photo
# ===========================================================================

class TestEditPhoto:
    def test_free_can_edit(self):
        bot = PhotoEditingBot(tier=Tier.FREE)
        result = bot.edit_photo("photo.jpg")
        assert isinstance(result, dict)
        assert "output_url" in result

    def test_has_resolution(self):
        bot = PhotoEditingBot(tier=Tier.FREE)
        result = bot.edit_photo("photo.jpg")
        assert "resolution" in result

    def test_adjustments_applied(self):
        bot = PhotoEditingBot(tier=Tier.PRO)
        result = bot.edit_photo("photo.jpg", {"brightness": 1.2, "contrast": 1.1})
        assert "adjustments_applied" in result

    def test_increments_daily_count(self):
        bot = PhotoEditingBot(tier=Tier.FREE)
        bot.edit_photo("photo.jpg")
        assert bot._daily_count == 1


# ===========================================================================
# remove_noise
# ===========================================================================

class TestRemoveNoise:
    def test_pro_can_remove_noise(self):
        bot = PhotoEditingBot(tier=Tier.PRO)
        result = bot.remove_noise("noisy.jpg")
        assert isinstance(result, dict)
        assert "output_url" in result

    def test_has_psnr_improvement(self):
        bot = PhotoEditingBot(tier=Tier.PRO)
        result = bot.remove_noise("noisy.jpg")
        assert "psnr_improvement_db" in result

    def test_free_cannot_remove_noise(self):
        bot = PhotoEditingBot(tier=Tier.FREE)
        with pytest.raises(PhotoEditingBotError):
            bot.remove_noise("noisy.jpg")


# ===========================================================================
# remove_background
# ===========================================================================

class TestRemoveBackground:
    def test_free_can_remove_background(self):
        bot = PhotoEditingBot(tier=Tier.FREE)
        result = bot.remove_background("photo.jpg")
        assert isinstance(result, dict)
        assert "output_url" in result


# ===========================================================================
# apply_filter
# ===========================================================================

class TestApplyFilter:
    def test_free_can_apply_filter(self):
        bot = PhotoEditingBot(tier=Tier.FREE)
        result = bot.apply_filter("photo.jpg", "sepia")
        assert isinstance(result, dict)
        assert "output_url" in result

    def test_filter_echoed(self):
        bot = PhotoEditingBot(tier=Tier.PRO)
        result = bot.apply_filter("photo.jpg", "vintage")
        assert result["filter_name"] == "vintage"


# ===========================================================================
# batch_edit
# ===========================================================================

class TestBatchEdit:
    def test_pro_can_batch_edit(self):
        bot = PhotoEditingBot(tier=Tier.PRO)
        result = bot.batch_edit(["p1.jpg", "p2.jpg", "p3.jpg"], {"brightness": 1.1})
        assert isinstance(result, dict)
        assert "processed" in result

    def test_processed_count(self):
        bot = PhotoEditingBot(tier=Tier.PRO)
        result = bot.batch_edit(["a.jpg", "b.jpg"], {"contrast": 1.2})
        assert result["processed"] == 2

    def test_free_cannot_batch_edit(self):
        bot = PhotoEditingBot(tier=Tier.FREE)
        with pytest.raises(PhotoEditingBotError):
            bot.batch_edit(["a.jpg", "b.jpg"], {})


# ===========================================================================
# cartoonify
# ===========================================================================

class TestCartoonify:
    def test_pro_can_cartoonify(self):
        bot = PhotoEditingBot(tier=Tier.PRO)
        result = bot.cartoonify("photo.jpg")
        assert isinstance(result, dict)
        assert "output_url" in result

    def test_style_echoed(self):
        bot = PhotoEditingBot(tier=Tier.PRO)
        result = bot.cartoonify("photo.jpg", "anime")
        assert result["style"] == "anime"

    def test_has_model(self):
        bot = PhotoEditingBot(tier=Tier.PRO)
        result = bot.cartoonify("photo.jpg", "comic")
        assert "processing_model" in result

    def test_free_cannot_cartoonify(self):
        bot = PhotoEditingBot(tier=Tier.FREE)
        with pytest.raises(PhotoEditingBotError):
            bot.cartoonify("photo.jpg")


# ===========================================================================
# create_caricature
# ===========================================================================

class TestCreateCaricature:
    def test_pro_can_create_caricature(self):
        bot = PhotoEditingBot(tier=Tier.PRO)
        result = bot.create_caricature("face.jpg")
        assert isinstance(result, dict)
        assert "output_url" in result

    def test_has_face_detected(self):
        bot = PhotoEditingBot(tier=Tier.PRO)
        result = bot.create_caricature("face.jpg")
        assert "face_detected" in result

    def test_free_cannot_create_caricature(self):
        bot = PhotoEditingBot(tier=Tier.FREE)
        with pytest.raises(PhotoEditingBotError):
            bot.create_caricature("face.jpg")


# ===========================================================================
# generate_animation
# ===========================================================================

class TestGenerateAnimation:
    def test_enterprise_can_generate_animation(self):
        bot = PhotoEditingBot(tier=Tier.ENTERPRISE)
        result = bot.generate_animation(["f1.jpg", "f2.jpg", "f3.jpg"])
        assert isinstance(result, dict)
        assert "output_url" in result

    def test_has_frame_count(self):
        bot = PhotoEditingBot(tier=Tier.ENTERPRISE)
        result = bot.generate_animation(["f1.jpg", "f2.jpg"])
        assert "frame_count" in result
        assert result["frame_count"] == 2

    def test_style_echoed(self):
        bot = PhotoEditingBot(tier=Tier.ENTERPRISE)
        result = bot.generate_animation(["f1.jpg"], style="disney")
        assert result["style"] == "disney"

    def test_pro_cannot_generate_animation(self):
        bot = PhotoEditingBot(tier=Tier.PRO)
        with pytest.raises(PhotoEditingBotError):
            bot.generate_animation(["f1.jpg"])


# ===========================================================================
# generate_cartoon_frame
# ===========================================================================

class TestGenerateCartoonFrame:
    def test_enterprise_can_generate_frame(self):
        bot = PhotoEditingBot(tier=Tier.ENTERPRISE)
        result = bot.generate_cartoon_frame("a dog in the park")
        assert isinstance(result, dict)
        assert "output_url" in result

    def test_description_echoed(self):
        bot = PhotoEditingBot(tier=Tier.ENTERPRISE)
        result = bot.generate_cartoon_frame("a blue sky")
        assert result["description"] == "a blue sky"

    def test_has_seed(self):
        bot = PhotoEditingBot(tier=Tier.ENTERPRISE)
        result = bot.generate_cartoon_frame("sunset scene", "anime")
        assert "seed" in result

    def test_free_cannot_generate_frame(self):
        bot = PhotoEditingBot(tier=Tier.FREE)
        with pytest.raises(PhotoEditingBotError):
            bot.generate_cartoon_frame("a cat")


# ===========================================================================
# get_editing_dashboard
# ===========================================================================

class TestGetEditingDashboard:
    def test_returns_dict(self):
        bot = PhotoEditingBot(tier=Tier.PRO)
        assert isinstance(bot.get_editing_dashboard(), dict)

    def test_contains_bot_name(self):
        bot = PhotoEditingBot(tier=Tier.PRO)
        assert bot.get_editing_dashboard()["bot_name"] == "PhotoEditingBot"

    def test_enterprise_remaining_unlimited(self):
        bot = PhotoEditingBot(tier=Tier.ENTERPRISE)
        assert bot.get_editing_dashboard()["remaining"] == "unlimited"

    def test_daily_limit_enforced(self):
        bot = PhotoEditingBot(tier=Tier.FREE)
        bot._daily_count = 10
        with pytest.raises(PhotoEditingBotError):
            bot.edit_photo("over_limit.jpg")
