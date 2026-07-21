# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""Brand Identity module for Business Launch Pad."""

import uuid
from dataclasses import dataclass, field


@dataclass
class ColorPalette:
    primary: str
    secondary: str
    accent: str
    neutral: str


@dataclass
class BrandKit:
    brand_id: str
    business_name: str
    industry: str
    logo_concepts: list[str]
    color_palette: ColorPalette
    brand_voice: str
    tagline: str
    style_guide: dict


_INDUSTRY_COLORS: dict[str, ColorPalette] = {
    "technology": ColorPalette(primary="#0057FF", secondary="#00C2FF", accent="#FF6B00", neutral="#F4F6F8"),
    "healthcare": ColorPalette(primary="#00897B", secondary="#4DB6AC", accent="#FF7043", neutral="#FAFAFA"),
    "finance": ColorPalette(primary="#1A237E", secondary="#283593", accent="#FFC107", neutral="#ECEFF1"),
    "retail": ColorPalette(primary="#D32F2F", secondary="#F44336", accent="#FFC107", neutral="#F5F5F5"),
    "education": ColorPalette(primary="#1565C0", secondary="#42A5F5", accent="#FF6F00", neutral="#E8F4FD"),
    "food & beverage": ColorPalette(primary="#E65100", secondary="#FF8F00", accent="#2E7D32", neutral="#FFF8E1"),
    "real estate": ColorPalette(primary="#37474F", secondary="#546E7A", accent="#C6A84B", neutral="#ECEFF1"),
    "consulting": ColorPalette(primary="#004D40", secondary="#00796B", accent="#FF6D00", neutral="#F1F8E9"),
    "e-commerce": ColorPalette(primary="#6A1B9A", secondary="#AB47BC", accent="#FFD600", neutral="#F3E5F5"),
    "entertainment": ColorPalette(primary="#212121", secondary="#424242", accent="#E91E63", neutral="#F5F5F5"),
}

_DEFAULT_COLORS = ColorPalette(primary="#2C3E50", secondary="#3498DB", accent="#E74C3C", neutral="#ECF0F1")

_BRAND_VOICES: dict[str, str] = {
    "technology": "Innovative, clear, and forward-thinking — we speak with technical authority while remaining approachable.",
    "healthcare": "Compassionate, trustworthy, and evidence-based — we communicate with warmth and clinical precision.",
    "finance": "Professional, confident, and transparent — we speak with authority while building trust through clarity.",
    "retail": "Energetic, friendly, and customer-first — we communicate with enthusiasm and a personal touch.",
    "education": "Encouraging, clear, and inspiring — we empower learners with accessible and motivating language.",
    "food & beverage": "Warm, inviting, and sensory-rich — we evoke taste and community in every message.",
    "real estate": "Authoritative, aspirational, and detail-oriented — we speak to both dreams and practical decisions.",
    "consulting": "Strategic, insightful, and direct — we communicate expertise with confidence and brevity.",
    "e-commerce": "Convenient, exciting, and personalized — we celebrate deals while building loyalty.",
    "entertainment": "Bold, immersive, and culturally aware — we create excitement and invite participation.",
}

_DEFAULT_BRAND_VOICE = "Professional, approachable, and results-driven — we communicate value with clarity and confidence."


class BrandIdentity:
    """Creates brand kits including logo concepts, color palettes, voice, and style guides."""

    def __init__(self) -> None:
        self._brands: list[BrandKit] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_brand(self, business_name: str, industry: str) -> BrandKit:
        """Generate a complete brand kit."""
        logo_concepts = self.generate_logo_concepts(business_name, industry)
        color_palette = self.recommend_colors(industry)
        brand_voice = self.define_brand_voice(industry)
        tagline = self.create_tagline(business_name, industry)
        kit = BrandKit(
            brand_id=str(uuid.uuid4()),
            business_name=business_name,
            industry=industry,
            logo_concepts=logo_concepts,
            color_palette=color_palette,
            brand_voice=brand_voice,
            tagline=tagline,
            style_guide={},
        )
        kit.style_guide = self.generate_style_guide(kit)
        self._brands.append(kit)
        return kit

    def generate_logo_concepts(self, business_name: str, industry: str) -> list[str]:
        """Return 5 logo concept descriptions."""
        initial = business_name[0].upper() if business_name else "B"
        return [
            f"Minimalist wordmark: '{business_name}' in clean sans-serif typography with a bold {industry}-inspired icon",
            f"Geometric monogram: stylized '{initial}' letterform with interconnected lines suggesting innovation",
            f"Abstract symbol: fluid shapes representing growth and connectivity in the {industry} sector",
            f"Badge/crest design: professional emblem with '{business_name}' name integrated into a shield or circle",
            f"Combination mark: custom icon paired with '{business_name}' logotype in a balanced horizontal layout",
        ]

    def recommend_colors(self, industry: str) -> ColorPalette:
        """Return a recommended color palette for the given industry."""
        return _INDUSTRY_COLORS.get(industry.lower(), _DEFAULT_COLORS)

    def define_brand_voice(self, industry: str) -> str:
        """Return a brand voice description for the industry."""
        return _BRAND_VOICES.get(industry.lower(), _DEFAULT_BRAND_VOICE)

    def create_tagline(self, business_name: str, industry: str) -> str:
        """Generate a tagline for the business."""
        taglines = [
            f"Redefining {industry} for the modern world.",
            f"Where {industry} meets innovation.",
            f"Your success in {industry} starts here.",
            f"Empowering your {industry} journey.",
            f"The future of {industry} is {business_name}.",
        ]
        idx = len(business_name) % len(taglines)
        return taglines[idx]

    def generate_style_guide(self, brand_kit: BrandKit) -> dict:
        """Generate a style guide from a BrandKit."""
        cp = brand_kit.color_palette
        return {
            "colors": {
                "primary": cp.primary,
                "secondary": cp.secondary,
                "accent": cp.accent,
                "neutral": cp.neutral,
            },
            "typography": {
                "heading_font": "Inter Bold",
                "body_font": "Inter Regular",
                "heading_sizes": ["48px", "36px", "28px", "22px"],
                "body_sizes": ["16px", "14px"],
            },
            "logo_usage": {
                "minimum_size": "32px",
                "clear_space": "16px on all sides",
                "approved_backgrounds": ["white", "light neutral", "primary color"],
            },
            "tone": brand_kit.brand_voice,
            "imagery": f"Use real, authentic photography that reflects the {brand_kit.industry} industry. Avoid stock-photo clichés.",
            "spacing": "8px base unit grid system",
        }

    def list_brands(self) -> list[BrandKit]:
        """Return all created brand kits."""
        return list(self._brands)

    def get_brand(self, brand_id: str) -> BrandKit:
        """Retrieve a brand kit by ID; raises KeyError if not found."""
        for brand in self._brands:
            if brand.brand_id == brand_id:
                return brand
        raise KeyError(f"Brand '{brand_id}' not found")
