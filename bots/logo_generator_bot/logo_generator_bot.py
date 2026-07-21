"""Logo Generator Bot — tier-aware logo creation and brand guide generation."""
import sys, os
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.logo_generator_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class LogoGeneratorBot:
    """Tier-aware logo generator and brand guide bot."""

    LOGO_TEMPLATES = {
        "tech": ["circuit board", "binary code", "microchip", "network nodes"],
        "food": ["fork and knife", "chef hat", "leaf", "flame"],
        "finance": ["bar chart", "coins", "shield", "arrow"],
        "health": ["cross", "heart", "leaf", "caduceus"],
        "retail": ["shopping bag", "price tag", "storefront", "hanger"],
        "education": ["book", "graduation cap", "pencil", "owl"],
        "legal": ["scales of justice", "gavel", "shield", "column"],
        "fitness": ["dumbbell", "lightning bolt", "running figure", "circle"],
        "travel": ["plane", "compass", "globe", "mountain"],
        "beauty": ["flower", "mirror", "lipstick", "sparkle"],
        "music": ["musical note", "guitar", "waveform", "microphone"],
        "sports": ["trophy", "ball", "laurel wreath", "star"],
        "real_estate": ["house", "key", "skyline", "arch"],
        "photography": ["camera", "aperture", "lens", "film strip"],
        "automotive": ["car silhouette", "wheel", "road", "speedometer"],
        "gaming": ["controller", "joystick", "pixel", "shield"],
        "nonprofit": ["hands", "heart", "dove", "globe"],
        "hospitality": ["bed", "bell", "key", "star"],
        "fashion": ["hanger", "needle", "crown", "diamond"],
        "consulting": ["lightbulb", "chart", "handshake", "gear"],
    }

    ALL_STYLES = ["modern", "vintage", "minimal", "bold", "elegant", "geometric", "handcrafted", "futuristic", "playful", "classic"]
    FREE_STYLES = ALL_STYLES[:5]

    CONCEPT_LIMITS = {Tier.FREE: 3, Tier.PRO: 25, Tier.ENTERPRISE: None}

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.flow = GlobalAISourcesFlow(bot_name="LogoGeneratorBot")
        self._concept_count = 0

    def list_styles(self) -> list:
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            return self.ALL_STYLES
        return self.FREE_STYLES

    def list_templates(self, industry=None):
        if industry:
            return self.LOGO_TEMPLATES.get(industry, [])
        return dict(self.LOGO_TEMPLATES)

    def generate_logo(self, business_name: str, industry: str, style: str = "modern", colors=None) -> dict:
        limit = self.CONCEPT_LIMITS[self.tier]
        if self.tier == Tier.FREE and self._concept_count >= 3:
            raise PermissionError("Concept limit reached for FREE tier")
        if self.tier == Tier.PRO and self._concept_count >= 25:
            raise PermissionError("Concept limit reached for PRO tier")
        if self.tier == Tier.FREE and style not in self.FREE_STYLES:
            raise PermissionError("Style not available on FREE tier")
        self._concept_count += 1
        templates = self.LOGO_TEMPLATES.get(industry, ["abstract shapes"])
        return {
            "business_name": business_name,
            "industry": industry,
            "style": style,
            "concept_id": f"concept_{self._concept_count}",
            "svg_description": f"A {style} logo for {business_name} featuring {random.choice(templates)} design elements",
            "color_palette": colors or [random.choice(["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8"]), "#FFFFFF", "#333333"],
            "typography": random.choice(["Sans-serif Bold", "Serif Classic", "Modern Rounded", "Geometric"]),
            "tagline_suggestion": f"Your {industry} brand, reimagined",
            "tier_used": self.tier.value,
        }

    def get_brand_guide(self, business_name: str) -> dict:
        if self.tier == Tier.FREE:
            raise PermissionError("Brand guide requires PRO or ENTERPRISE tier")
        return {
            "business_name": business_name,
            "primary_color": "#4ECDC4",
            "secondary_color": "#FF6B6B",
            "typography": {"heading": "Montserrat Bold", "body": "Open Sans Regular"},
            "usage_guidelines": ["Use on white backgrounds", "Maintain minimum size of 32px", "Don't stretch or distort"],
            "tier_used": self.tier.value,
        }

    def run(self) -> dict:
        return self.flow.run_pipeline(
            raw_data={"bot": "LogoGeneratorBot", "tier": self.tier.value, "concepts_generated": self._concept_count},
            learning_method="supervised",
        )
