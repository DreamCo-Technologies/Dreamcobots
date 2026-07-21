import sys, os
REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, REPO_ROOT)

TOOL_DIR = os.path.join(REPO_ROOT, 'automation-tools', 'color_palette_generator')
sys.path.insert(0, TOOL_DIR)

import pytest
from color_palette_generator import ColorPaletteGenerator


class TestColorPaletteGeneratorInstantiation:
    def test_default_tier_is_free(self):
        gen = ColorPaletteGenerator()
        assert gen.tier == "free"

    def test_pro_tier(self):
        gen = ColorPaletteGenerator(tier="pro")
        assert gen.tier == "pro"


class TestHexHslConversion:
    def test_hex_to_hsl_white(self):
        gen = ColorPaletteGenerator()
        h, s, l = gen.hex_to_hsl("#ffffff")
        assert l == 100.0

    def test_hex_to_hsl_black(self):
        gen = ColorPaletteGenerator()
        h, s, l = gen.hex_to_hsl("#000000")
        assert l == 0.0

    def test_roundtrip(self):
        gen = ColorPaletteGenerator()
        original = "#1a73e8"
        h, s, l = gen.hex_to_hsl(original)
        result = gen.hsl_to_hex(h, s, l)
        assert result.startswith("#")
        assert len(result) == 7


class TestGeneratePalette:
    def test_returns_correct_size(self):
        gen = ColorPaletteGenerator(tier="pro")
        result = gen.generate_palette("#1a73e8", scheme="complementary", size=5)
        assert len(result["palette"]) == 5

    def test_base_color_in_palette(self):
        gen = ColorPaletteGenerator(tier="pro")
        result = gen.generate_palette("#1a73e8", size=5)
        assert "#1a73e8" in result["palette"]

    def test_scheme_types(self):
        gen = ColorPaletteGenerator(tier="pro")
        for scheme in ColorPaletteGenerator.SCHEME_TYPES:
            result = gen.generate_palette("#ff0000", scheme=scheme, size=3)
            assert result["scheme"] == scheme

    def test_invalid_scheme_falls_back(self):
        gen = ColorPaletteGenerator(tier="pro")
        result = gen.generate_palette("#1a73e8", scheme="invalid", size=3)
        assert result["scheme"] == "complementary"

    def test_free_tier_monthly_limit(self):
        gen = ColorPaletteGenerator(tier="free")
        for _ in range(5):
            gen.generate_palette("#1a73e8", size=3)
        with pytest.raises(PermissionError):
            gen.generate_palette("#1a73e8", size=3)


class TestSuggestBrandColors:
    def test_known_industry(self):
        gen = ColorPaletteGenerator()
        result = gen.suggest_brand_colors("tech")
        assert result["recommended_base"] == "#1a73e8"

    def test_unknown_industry_has_fallback(self):
        gen = ColorPaletteGenerator()
        result = gen.suggest_brand_colors("aerospace")
        assert result["recommended_base"].startswith("#")
