"""
Influencer Database — catalog of influencers and celebrities for the DreamCo
Influencer Bot.

Covers 20+ influencers/celebrities across 10 categories:
  FITNESS, ENTERTAINMENT, MUSIC, GAMING, TECH, FASHION, FOOD, TRAVEL,
  EDUCATION, WELLNESS

Each influencer has:
  influencer_id, name, category, audience_size_millions, platform,
  specialty, engagement_rate_pct, partnership_tier (STANDARD/PREMIUM/CELEBRITY)

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dataclasses import dataclass
from typing import List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Partnership tiers
# ---------------------------------------------------------------------------

PARTNERSHIP_STANDARD = "STANDARD"
PARTNERSHIP_PREMIUM = "PREMIUM"
PARTNERSHIP_CELEBRITY = "CELEBRITY"

# ---------------------------------------------------------------------------
# Category constants
# ---------------------------------------------------------------------------

CATEGORY_FITNESS = "FITNESS"
CATEGORY_ENTERTAINMENT = "ENTERTAINMENT"
CATEGORY_MUSIC = "MUSIC"
CATEGORY_GAMING = "GAMING"
CATEGORY_TECH = "TECH"
CATEGORY_FASHION = "FASHION"
CATEGORY_FOOD = "FOOD"
CATEGORY_TRAVEL = "TRAVEL"
CATEGORY_EDUCATION = "EDUCATION"
CATEGORY_WELLNESS = "WELLNESS"


@dataclass
class Influencer:
    """Represents a single influencer or celebrity in the database."""

    influencer_id: str
    name: str
    category: str
    audience_size_millions: float
    platform: str
    specialty: str
    engagement_rate_pct: float
    partnership_tier: str

    def to_dict(self) -> dict:
        return {
            "influencer_id": self.influencer_id,
            "name": self.name,
            "category": self.category,
            "audience_size_millions": self.audience_size_millions,
            "platform": self.platform,
            "specialty": self.specialty,
            "engagement_rate_pct": self.engagement_rate_pct,
            "partnership_tier": self.partnership_tier,
        }


# ---------------------------------------------------------------------------
# Seed data — 22 influencers across all categories
# ---------------------------------------------------------------------------

_INFLUENCERS: List[Influencer] = [
    # FITNESS
    Influencer(
        influencer_id="inf_001",
        name="Alex Fitness",
        category=CATEGORY_FITNESS,
        audience_size_millions=4.2,
        platform="Instagram",
        specialty="HIIT & Strength Training",
        engagement_rate_pct=6.8,
        partnership_tier=PARTNERSHIP_PREMIUM,
    ),
    Influencer(
        influencer_id="inf_002",
        name="Maya Strong",
        category=CATEGORY_FITNESS,
        audience_size_millions=2.1,
        platform="YouTube",
        specialty="Yoga & Mindful Movement",
        engagement_rate_pct=8.3,
        partnership_tier=PARTNERSHIP_STANDARD,
    ),
    # ENTERTAINMENT
    Influencer(
        influencer_id="inf_003",
        name="Jordan Blake",
        category=CATEGORY_ENTERTAINMENT,
        audience_size_millions=18.5,
        platform="TikTok",
        specialty="Comedy Skits & Viral Content",
        engagement_rate_pct=12.1,
        partnership_tier=PARTNERSHIP_CELEBRITY,
    ),
    Influencer(
        influencer_id="inf_004",
        name="Riley Star",
        category=CATEGORY_ENTERTAINMENT,
        audience_size_millions=9.7,
        platform="YouTube",
        specialty="Reaction Videos & Pop Culture",
        engagement_rate_pct=7.4,
        partnership_tier=PARTNERSHIP_PREMIUM,
    ),
    # MUSIC
    Influencer(
        influencer_id="inf_005",
        name="Nova Beats",
        category=CATEGORY_MUSIC,
        audience_size_millions=22.3,
        platform="Instagram",
        specialty="R&B & Soul Production",
        engagement_rate_pct=9.6,
        partnership_tier=PARTNERSHIP_CELEBRITY,
    ),
    Influencer(
        influencer_id="inf_006",
        name="DJ Prism",
        category=CATEGORY_MUSIC,
        audience_size_millions=5.8,
        platform="TikTok",
        specialty="Electronic Dance Music",
        engagement_rate_pct=11.2,
        partnership_tier=PARTNERSHIP_PREMIUM,
    ),
    # GAMING
    Influencer(
        influencer_id="inf_007",
        name="PixelKing",
        category=CATEGORY_GAMING,
        audience_size_millions=7.4,
        platform="YouTube",
        specialty="FPS & Battle Royale",
        engagement_rate_pct=5.9,
        partnership_tier=PARTNERSHIP_PREMIUM,
    ),
    Influencer(
        influencer_id="inf_008",
        name="StreamQueen",
        category=CATEGORY_GAMING,
        audience_size_millions=3.6,
        platform="TikTok",
        specialty="RPG & Storytelling Games",
        engagement_rate_pct=10.4,
        partnership_tier=PARTNERSHIP_STANDARD,
    ),
    # TECH
    Influencer(
        influencer_id="inf_009",
        name="CodeWithKai",
        category=CATEGORY_TECH,
        audience_size_millions=1.9,
        platform="YouTube",
        specialty="AI & Machine Learning Tutorials",
        engagement_rate_pct=7.1,
        partnership_tier=PARTNERSHIP_STANDARD,
    ),
    Influencer(
        influencer_id="inf_010",
        name="TechVision Pro",
        category=CATEGORY_TECH,
        audience_size_millions=3.3,
        platform="Twitter",
        specialty="Gadget Reviews & Tech News",
        engagement_rate_pct=4.8,
        partnership_tier=PARTNERSHIP_PREMIUM,
    ),
    # FASHION
    Influencer(
        influencer_id="inf_011",
        name="Chloe Couture",
        category=CATEGORY_FASHION,
        audience_size_millions=11.2,
        platform="Instagram",
        specialty="Luxury & Sustainable Fashion",
        engagement_rate_pct=8.7,
        partnership_tier=PARTNERSHIP_CELEBRITY,
    ),
    Influencer(
        influencer_id="inf_012",
        name="StreetStyle Sam",
        category=CATEGORY_FASHION,
        audience_size_millions=2.8,
        platform="TikTok",
        specialty="Streetwear & Sneaker Culture",
        engagement_rate_pct=13.5,
        partnership_tier=PARTNERSHIP_STANDARD,
    ),
    # FOOD
    Influencer(
        influencer_id="inf_013",
        name="Chef Mia",
        category=CATEGORY_FOOD,
        audience_size_millions=6.1,
        platform="YouTube",
        specialty="Plant-Based Cooking",
        engagement_rate_pct=9.2,
        partnership_tier=PARTNERSHIP_PREMIUM,
    ),
    Influencer(
        influencer_id="inf_014",
        name="FoodieKing",
        category=CATEGORY_FOOD,
        audience_size_millions=1.7,
        platform="Instagram",
        specialty="Street Food & Restaurant Reviews",
        engagement_rate_pct=6.5,
        partnership_tier=PARTNERSHIP_STANDARD,
    ),
    # TRAVEL
    Influencer(
        influencer_id="inf_015",
        name="Globe Trotter Zoe",
        category=CATEGORY_TRAVEL,
        audience_size_millions=4.9,
        platform="Instagram",
        specialty="Budget Travel & Hidden Gems",
        engagement_rate_pct=7.8,
        partnership_tier=PARTNERSHIP_PREMIUM,
    ),
    Influencer(
        influencer_id="inf_016",
        name="Luxury Nomad",
        category=CATEGORY_TRAVEL,
        audience_size_millions=8.3,
        platform="YouTube",
        specialty="Luxury Travel & Resort Reviews",
        engagement_rate_pct=5.3,
        partnership_tier=PARTNERSHIP_PREMIUM,
    ),
    # EDUCATION
    Influencer(
        influencer_id="inf_017",
        name="Professor Spark",
        category=CATEGORY_EDUCATION,
        audience_size_millions=2.4,
        platform="YouTube",
        specialty="Science & Critical Thinking",
        engagement_rate_pct=8.9,
        partnership_tier=PARTNERSHIP_STANDARD,
    ),
    Influencer(
        influencer_id="inf_018",
        name="StudyWithNia",
        category=CATEGORY_EDUCATION,
        audience_size_millions=1.5,
        platform="TikTok",
        specialty="Study Tips & Exam Prep",
        engagement_rate_pct=14.2,
        partnership_tier=PARTNERSHIP_STANDARD,
    ),
    # WELLNESS
    Influencer(
        influencer_id="inf_019",
        name="Mindful Marco",
        category=CATEGORY_WELLNESS,
        audience_size_millions=3.8,
        platform="Instagram",
        specialty="Meditation & Mental Health",
        engagement_rate_pct=10.1,
        partnership_tier=PARTNERSHIP_PREMIUM,
    ),
    Influencer(
        influencer_id="inf_020",
        name="Dr. Luna Wellness",
        category=CATEGORY_WELLNESS,
        audience_size_millions=5.5,
        platform="YouTube",
        specialty="Holistic Health & Nutrition",
        engagement_rate_pct=9.8,
        partnership_tier=PARTNERSHIP_PREMIUM,
    ),
    Influencer(
        influencer_id="inf_021",
        name="Aria Radiance",
        category=CATEGORY_WELLNESS,
        audience_size_millions=14.7,
        platform="Instagram",
        specialty="Wellness Lifestyle & Skincare",
        engagement_rate_pct=11.6,
        partnership_tier=PARTNERSHIP_CELEBRITY,
    ),
    Influencer(
        influencer_id="inf_022",
        name="The Fitness Celeb",
        category=CATEGORY_FITNESS,
        audience_size_millions=30.1,
        platform="Instagram",
        specialty="Elite Athletic Training",
        engagement_rate_pct=7.0,
        partnership_tier=PARTNERSHIP_CELEBRITY,
    ),
]


class InfluencerDatabase:
    """In-memory catalog of influencers and celebrities."""

    def __init__(self) -> None:
        self._influencers: dict = {inf.influencer_id: inf for inf in _INFLUENCERS}

    def get_influencer(self, influencer_id: str) -> Optional[Influencer]:
        """Return a single influencer by ID, or None if not found."""
        return self._influencers.get(influencer_id)

    def list_influencers(self, category: Optional[str] = None) -> List[Influencer]:
        """Return all influencers, optionally filtered by category."""
        all_inf = list(self._influencers.values())
        if category:
            all_inf = [i for i in all_inf if i.category.upper() == category.upper()]
        return all_inf

    def search_influencers(self, query: str) -> List[Influencer]:
        """Search influencers by name or specialty (case-insensitive)."""
        q = query.lower()
        return [
            i for i in self._influencers.values()
            if q in i.name.lower() or q in i.specialty.lower()
        ]

    def get_by_category(self, category: str) -> List[Influencer]:
        """Return all influencers in the given category."""
        return self.list_influencers(category=category)

    def get_celebrities(self) -> List[Influencer]:
        """Return influencers with CELEBRITY partnership tier."""
        return [i for i in self._influencers.values() if i.partnership_tier == PARTNERSHIP_CELEBRITY]

    def count(self) -> int:
        return len(self._influencers)
