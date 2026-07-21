"""Tests for bots/logo_generator_bot/tiers.py and bots/logo_generator_bot/logo_generator_bot.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.logo_generator_bot.logo_generator_bot import LogoGeneratorBot
from bots.logo_generator_bot.tiers import BOT_FEATURES, get_bot_tier_info


class TestLogoGeneratorBotInstantiation:
    def test_default_tier_is_free(self):
        bot = LogoGeneratorBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = LogoGeneratorBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = LogoGeneratorBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE


class TestLogoGeneratorBotStyles:
    def test_list_styles_returns_list(self):
        bot = LogoGeneratorBot()
        assert isinstance(bot.list_styles(), list)

    def test_free_gets_5_styles(self):
        bot = LogoGeneratorBot()
        assert len(bot.list_styles()) == 5

    def test_pro_gets_all_styles(self):
        bot = LogoGeneratorBot(tier=Tier.PRO)
        assert len(bot.list_styles()) == 10

    def test_free_tier_style_limit(self):
        bot = LogoGeneratorBot()
        with pytest.raises(PermissionError):
            bot.generate_logo("Acme", "tech", style="futuristic")


class TestLogoGeneratorBotTemplates:
    def test_list_templates_returns_dict(self):
        bot = LogoGeneratorBot()
        assert isinstance(bot.list_templates(), dict)

    def test_list_templates_industry(self):
        bot = LogoGeneratorBot()
        result = bot.list_templates(industry="tech")
        assert isinstance(result, list)
        assert len(result) > 0


class TestLogoGeneratorBotGenerate:
    def test_generate_logo_returns_required_keys(self):
        bot = LogoGeneratorBot()
        result = bot.generate_logo("Acme", "tech", "modern")
        for key in ["business_name", "industry", "style", "concept_id", "svg_description", "color_palette", "typography", "tagline_suggestion", "tier_used"]:
            assert key in result

    def test_generate_logo_modern_style(self):
        bot = LogoGeneratorBot()
        result = bot.generate_logo("Acme", "tech", "modern")
        assert result["style"] == "modern"

    def test_generate_logo_vintage_style(self):
        bot = LogoGeneratorBot(tier=Tier.PRO)
        result = bot.generate_logo("Acme", "food", "vintage")
        assert result["style"] == "vintage"

    def test_generate_logo_minimal_style(self):
        bot = LogoGeneratorBot(tier=Tier.PRO)
        result = bot.generate_logo("Acme", "finance", "minimal")
        assert result["style"] == "minimal"

    def test_color_palette_is_list(self):
        bot = LogoGeneratorBot()
        result = bot.generate_logo("Acme", "tech", "modern")
        assert isinstance(result["color_palette"], list)

    def test_concept_id_increments(self):
        bot = LogoGeneratorBot()
        r1 = bot.generate_logo("Acme", "tech", "modern")
        r2 = bot.generate_logo("Beta", "food", "bold")
        assert r1["concept_id"] == "concept_1"
        assert r2["concept_id"] == "concept_2"


class TestLogoGeneratorBotBrandGuide:
    def test_get_brand_guide_raises_on_free(self):
        bot = LogoGeneratorBot()
        with pytest.raises(PermissionError):
            bot.get_brand_guide("Acme")

    def test_get_brand_guide_works_on_pro(self):
        bot = LogoGeneratorBot(tier=Tier.PRO)
        result = bot.get_brand_guide("Acme")
        assert isinstance(result, dict)
        assert "primary_color" in result

    def test_get_brand_guide_works_on_enterprise(self):
        bot = LogoGeneratorBot(tier=Tier.ENTERPRISE)
        result = bot.get_brand_guide("Acme")
        assert isinstance(result, dict)


class TestLogoGeneratorBotTiers:
    def test_bot_features_has_all_tiers(self):
        assert Tier.FREE.value in BOT_FEATURES
        assert Tier.PRO.value in BOT_FEATURES
        assert Tier.ENTERPRISE.value in BOT_FEATURES

    def test_get_bot_tier_info_free(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["tier"] == "free"

    def test_pro_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_tier_config_price(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_run_returns_pipeline_complete(self):
        bot = LogoGeneratorBot()
        result = bot.run()
        assert result.get("pipeline_complete") is True
