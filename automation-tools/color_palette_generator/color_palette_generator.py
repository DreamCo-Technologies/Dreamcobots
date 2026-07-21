# GLOBAL AI SOURCES FLOW
"""Color Palette Generator - brand and design color palette automation."""
import sys
import os
import importlib.util
_TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_TOOL_DIR, '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from framework import GlobalAISourcesFlow  # noqa: F401
# Load local tiers.py by path to avoid sys.modules conflicts with other tiers modules
import colorsys

_tiers_spec = importlib.util.spec_from_file_location('_local_tiers', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS


class ColorPaletteGenerator:
    """Generate color palettes for branding and design workflows."""

    SCHEME_TYPES = ["monochromatic", "complementary", "triadic", "analogous", "split-complementary"]

    def __init__(self, tier: str = "free"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["free"])
        self._palette_count = 0
        self._monthly_limit = 5 if tier == "free" else None

    def _check_limit(self):
        if self._monthly_limit and self._palette_count >= self._monthly_limit:
            raise PermissionError(f"Monthly palette limit ({self._monthly_limit}) reached. Upgrade to Pro.")

    @staticmethod
    def hex_to_hsl(hex_color: str) -> tuple:
        """Convert hex color to HSL tuple."""
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return round(h * 360, 1), round(s * 100, 1), round(l * 100, 1)

    @staticmethod
    def hsl_to_hex(h: float, s: float, l: float) -> str:
        """Convert HSL to hex color string."""
        r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

    def generate_palette(self, base_color: str, scheme: str = "complementary", size: int = 5) -> dict:
        """Generate a color palette from a base hex color."""
        self._check_limit()
        if scheme not in self.SCHEME_TYPES:
            scheme = "complementary"
        h, s, l = self.hex_to_hsl(base_color)
        colors = [base_color]
        if scheme == "monochromatic":
            step = 15
            for i in range(1, size):
                new_l = max(10, min(90, l + (i * step) - (size // 2 * step)))
                colors.append(self.hsl_to_hex(h, s, new_l))
        elif scheme == "complementary":
            colors.append(self.hsl_to_hex((h + 180) % 360, s, l))
            for i in range(2, size):
                colors.append(self.hsl_to_hex(h, s, max(10, min(90, l + i * 10 - 20))))
        elif scheme == "triadic":
            colors.append(self.hsl_to_hex((h + 120) % 360, s, l))
            colors.append(self.hsl_to_hex((h + 240) % 360, s, l))
            for i in range(3, size):
                colors.append(self.hsl_to_hex(h, s, max(10, min(90, l + i * 10))))
        elif scheme == "analogous":
            for i in range(1, size):
                colors.append(self.hsl_to_hex((h + i * 30) % 360, s, l))
        elif scheme == "split-complementary":
            colors.append(self.hsl_to_hex((h + 150) % 360, s, l))
            colors.append(self.hsl_to_hex((h + 210) % 360, s, l))
            for i in range(3, size):
                colors.append(self.hsl_to_hex(h, s, max(10, min(90, l + i * 10))))

        self._palette_count += 1
        return {
            "base_color": base_color,
            "scheme": scheme,
            "palette": colors[:size],
            "tier": self.tier,
        }

    def suggest_brand_colors(self, industry: str) -> dict:
        """Return recommended base colors for a given industry."""
        suggestions = {
            "tech": "#1a73e8",
            "health": "#34a853",
            "finance": "#1e3a5f",
            "retail": "#e53935",
            "food": "#fb8c00",
            "education": "#7c4dff",
        }
        base = suggestions.get(industry.lower(), "#5c6bc0")
        return {"industry": industry, "recommended_base": base}
