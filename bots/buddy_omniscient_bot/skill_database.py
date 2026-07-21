"""
Skill Database — Community-Built Skill Database and Expert Collaboration
for Buddy Omniscient Bot.

Features:
  • Crowdsourcing hub where users upload unique skills for Buddy to teach.
  • Expert collaboration: Buddy is trained by world-class experts
    (NASA engineers, artists, business magnates, scientists, etc.)
  • Skill discovery, search, and rating system.
  • Highlight showcase of unique community talents.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict
import uuid

from framework import GlobalAISourcesFlow  # noqa: F401


class SkillCategory(Enum):
    AUTOMOTIVE = "automotive"
    COOKING = "cooking"
    MUSIC = "music"
    TECHNOLOGY = "technology"
    SCIENCE = "science"
    BUSINESS = "business"
    ARTS = "arts"
    FITNESS = "fitness"
    ENGINEERING = "engineering"
    MEDICINE = "medicine"
    EDUCATION = "education"
    LEGAL = "legal"
    FINANCE = "finance"
    SUSTAINABILITY = "sustainability"
    SPACE = "space"
    CUSTOM = "custom"


class SkillDifficulty(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ExpertField(Enum):
    SPACE_ENGINEERING = "space_engineering"
    MEDICINE = "medicine"
    BUSINESS = "business"
    ARTS = "arts"
    SCIENCE = "science"
    TECHNOLOGY = "technology"
    MUSIC = "music"
    SPORTS = "sports"
    EDUCATION = "education"
    SUSTAINABILITY = "sustainability"
    CULINARY = "culinary"
    LAW = "law"
    FINANCE = "finance"


@dataclass
class CommunitySkill:
    """Represents a skill uploaded by a community member."""

    skill_id: str
    title: str
    category: SkillCategory
    difficulty: SkillDifficulty
    uploaded_by: str
    description: str
    steps: List[str]
    tags: List[str]
    rating: float = 0.0
    rating_count: int = 0
    verified: bool = False
    featured: bool = False
    views: int = 0

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "title": self.title,
            "category": self.category.value,
            "difficulty": self.difficulty.value,
            "uploaded_by": self.uploaded_by,
            "description": self.description,
            "steps": self.steps,
            "tags": self.tags,
            "rating": round(self.rating, 2),
            "rating_count": self.rating_count,
            "verified": self.verified,
            "featured": self.featured,
            "views": self.views,
        }


@dataclass
class ExpertProfile:
    """Represents a world-class expert who has trained Buddy."""

    expert_id: str
    name: str
    field: ExpertField
    organization: str
    specializations: List[str]
    skills_contributed: List[str]
    bio: str
    verified: bool = True

    def to_dict(self) -> dict:
        return {
            "expert_id": self.expert_id,
            "name": self.name,
            "field": self.field.value,
            "organization": self.organization,
            "specializations": self.specializations,
            "skills_contributed": self.skills_contributed,
            "bio": self.bio,
            "verified": self.verified,
        }


# ---------------------------------------------------------------------------
# Seed data — expert profiles
# ---------------------------------------------------------------------------

_EXPERT_PROFILES: List[ExpertProfile] = [
    ExpertProfile(
        expert_id="EXP-001",
        name="Dr. Astra Novak",
        field=ExpertField.SPACE_ENGINEERING,
        organization="DreamCo Space Division / NASA Partner",
        specializations=[
            "Rocket propulsion", "Orbital mechanics", "Spacecraft systems",
            "Satellite deployment", "Space robotics",
        ],
        skills_contributed=[
            "Understanding rocket fuel types",
            "How to read telemetry data",
            "Introduction to orbital mechanics",
            "Spacecraft systems overview",
        ],
        bio=(
            "Dr. Novak has 20+ years of experience in aerospace engineering. "
            "She has trained Buddy in space science so anyone can understand "
            "the cosmos — from school students to future astronauts."
        ),
    ),
    ExpertProfile(
        expert_id="EXP-002",
        name="Marcus DeLeon",
        field=ExpertField.BUSINESS,
        organization="Fortune 500 Business Strategist",
        specializations=[
            "Startup scaling", "Go-to-market strategy", "Revenue modeling",
            "Brand building", "Investor relations",
        ],
        skills_contributed=[
            "Business plan creation in hours",
            "Brand identity from scratch",
            "Customer acquisition strategies",
            "Pitch deck fundamentals",
        ],
        bio=(
            "Marcus has founded and scaled 7 companies across 4 continents. "
            "He trained Buddy with real-world business strategies so "
            "anyone can launch and grow a business."
        ),
    ),
    ExpertProfile(
        expert_id="EXP-003",
        name="Yuki Tanaka",
        field=ExpertField.ARTS,
        organization="International Digital Arts Academy",
        specializations=[
            "Digital illustration", "3D modeling", "Motion graphics",
            "Character design", "Generative AI art",
        ],
        skills_contributed=[
            "Digital drawing for beginners",
            "3D art creation techniques",
            "Color theory essentials",
            "Creating viral art content",
        ],
        bio=(
            "Yuki is a world-renowned digital artist whose work has appeared "
            "in global galleries. She trained Buddy in artistic techniques "
            "to make creativity accessible to everyone."
        ),
    ),
    ExpertProfile(
        expert_id="EXP-004",
        name="Dr. Samuel Okonkwo",
        field=ExpertField.MEDICINE,
        organization="Global Health Innovation Institute",
        specializations=[
            "Preventive medicine", "Health diagnostics", "Mental wellness",
            "Nutrition science", "Wearable health tech",
        ],
        skills_contributed=[
            "Reading basic health metrics",
            "Nutrition planning fundamentals",
            "Mental health awareness",
            "Understanding medical diagnostics",
        ],
        bio=(
            "Dr. Okonkwo is a leading physician and health innovator. "
            "He trained Buddy in health literacy so Buddy can provide "
            "evidence-based wellness guidance to users worldwide."
        ),
    ),
    ExpertProfile(
        expert_id="EXP-005",
        name="Elena Vasquez",
        field=ExpertField.SUSTAINABILITY,
        organization="EcoFutures Global",
        specializations=[
            "Renewable energy", "Carbon footprint reduction", "Circular economy",
            "Sustainable architecture", "Climate action",
        ],
        skills_contributed=[
            "Calculating your carbon footprint",
            "Home energy optimization",
            "Sustainable business practices",
            "Renewable energy basics",
        ],
        bio=(
            "Elena leads global sustainability initiatives. She trained Buddy "
            "to empower individuals and businesses to make environmentally "
            "positive decisions every day."
        ),
    ),
    ExpertProfile(
        expert_id="EXP-006",
        name="James 'JRock' Rivera",
        field=ExpertField.MUSIC,
        organization="Grammy Award-Winning Producer",
        specializations=[
            "Guitar mastery", "Music production", "Beat making",
            "Songwriting", "Music theory",
        ],
        skills_contributed=[
            "Guitar solo techniques",
            "Music production fundamentals",
            "Songwriting structure",
            "Music theory basics",
        ],
        bio=(
            "JRock has produced chart-topping hits across multiple genres. "
            "He trained Buddy in music so anyone can learn to play, produce, "
            "and perform at a professional level."
        ),
    ),
]

_SEED_COMMUNITY_SKILLS: List[CommunitySkill] = [
    CommunitySkill(
        skill_id="SKILL-001",
        title="How to Change Your Own Oil",
        category=SkillCategory.AUTOMOTIVE,
        difficulty=SkillDifficulty.BEGINNER,
        uploaded_by="CarEnthusiast_Dave",
        description="A step-by-step guide to changing your car's oil safely at home.",
        steps=[
            "Gather supplies: oil, filter, drain pan, wrench.",
            "Warm up the engine for 2 minutes, then turn off.",
            "Drain the old oil from the drain plug.",
            "Replace the oil filter.",
            "Add new oil and check the dipstick.",
        ],
        tags=["car", "oil change", "DIY", "maintenance"],
        rating=4.8,
        rating_count=214,
        verified=True,
        featured=True,
        views=8920,
    ),
    CommunitySkill(
        skill_id="SKILL-002",
        title="Guitar Solo: Sweet Child O' Mine Intro",
        category=SkillCategory.MUSIC,
        difficulty=SkillDifficulty.INTERMEDIATE,
        uploaded_by="GuitarHero_Max",
        description="Learn the iconic opening riff of Sweet Child O' Mine with finger-placement guides.",
        steps=[
            "Tune your guitar to standard E tuning.",
            "Practice the D string pattern: 12-10-12-10.",
            "Add the G string: 9-10.",
            "Practice slowly with a metronome at 60 BPM.",
            "Gradually increase speed to 120 BPM.",
        ],
        tags=["guitar", "music", "rock", "riff", "beginner-friendly"],
        rating=4.9,
        rating_count=512,
        verified=True,
        featured=True,
        views=24100,
    ),
    CommunitySkill(
        skill_id="SKILL-003",
        title="Advanced Pokémon Card Appraisal",
        category=SkillCategory.ARTS,
        difficulty=SkillDifficulty.ADVANCED,
        uploaded_by="PokeCollector_J",
        description="How to accurately value rare Pokémon cards using condition, print run, and market data.",
        steps=[
            "Examine card condition under bright light for scratches.",
            "Identify the print run from card identifier codes.",
            "Cross-reference recent auction results on major platforms.",
            "Assess holographic pattern authenticity.",
            "Calculate a fair market value range.",
        ],
        tags=["pokemon", "cards", "valuation", "collectibles", "investment"],
        rating=4.7,
        rating_count=180,
        verified=True,
        featured=False,
        views=5600,
    ),
]


class SkillDatabase:
    """
    Community-Built Skill Database for Buddy Omniscient Bot.

    Manages community skill uploads, expert profiles, ratings,
    search, and featured skill highlights.
    """

    def __init__(self, max_uploads: Optional[int] = 0) -> None:
        self._max_uploads = max_uploads
        self._skills: Dict[str, CommunitySkill] = {
            s.skill_id: s for s in _SEED_COMMUNITY_SKILLS
        }
        self._experts: Dict[str, ExpertProfile] = {
            e.expert_id: e for e in _EXPERT_PROFILES
        }
        self._user_upload_count: int = 0

    # ------------------------------------------------------------------
    # Skill management
    # ------------------------------------------------------------------

    def upload_skill(
        self,
        title: str,
        category: SkillCategory,
        difficulty: SkillDifficulty,
        uploaded_by: str,
        description: str,
        steps: List[str],
        tags: Optional[List[str]] = None,
    ) -> CommunitySkill:
        """Upload a new community skill."""
        if self._max_uploads is not None and self._max_uploads == 0:
            raise PermissionError(
                "Skill uploads are not available on the Free tier. "
                "Upgrade to Pro to share your skills with the community."
            )
        if self._max_uploads is not None and self._user_upload_count >= self._max_uploads:
            raise PermissionError(
                f"Upload limit of {self._max_uploads} skills reached. "
                "Upgrade to Enterprise for unlimited uploads."
            )
        skill_id = f"SKILL-{uuid.uuid4().hex[:6].upper()}"
        skill = CommunitySkill(
            skill_id=skill_id,
            title=title,
            category=category,
            difficulty=difficulty,
            uploaded_by=uploaded_by,
            description=description,
            steps=steps,
            tags=tags or [],
        )
        self._skills[skill_id] = skill
        self._user_upload_count += 1
        return skill

    def get_skill(self, skill_id: str) -> Optional[CommunitySkill]:
        skill = self._skills.get(skill_id)
        if skill:
            skill.views += 1
        return skill

    def search_skills(
        self,
        query: str = "",
        category: Optional[SkillCategory] = None,
        difficulty: Optional[SkillDifficulty] = None,
        featured_only: bool = False,
    ) -> List[CommunitySkill]:
        skills = list(self._skills.values())
        if query:
            q = query.lower()
            skills = [
                s for s in skills
                if q in s.title.lower()
                or q in s.description.lower()
                or any(q in t.lower() for t in s.tags)
            ]
        if category:
            skills = [s for s in skills if s.category == category]
        if difficulty:
            skills = [s for s in skills if s.difficulty == difficulty]
        if featured_only:
            skills = [s for s in skills if s.featured]
        return sorted(skills, key=lambda s: s.rating, reverse=True)

    def rate_skill(self, skill_id: str, rating: float) -> dict:
        if not (1.0 <= rating <= 5.0):
            return {"error": "Rating must be between 1.0 and 5.0."}
        skill = self._skills.get(skill_id)
        if not skill:
            return {"error": f"Skill '{skill_id}' not found."}
        total = skill.rating * skill.rating_count + rating
        skill.rating_count += 1
        skill.rating = total / skill.rating_count
        return {
            "skill_id": skill_id,
            "new_rating": round(skill.rating, 2),
            "rating_count": skill.rating_count,
            "message": "Thank you for rating this skill!",
        }

    def count_skills(self) -> int:
        return len(self._skills)

    def list_featured_skills(self) -> List[CommunitySkill]:
        return [s for s in self._skills.values() if s.featured]

    # ------------------------------------------------------------------
    # Expert collaboration
    # ------------------------------------------------------------------

    def get_expert(self, expert_id: str) -> Optional[ExpertProfile]:
        return self._experts.get(expert_id)

    def list_experts(self, field: Optional[ExpertField] = None) -> List[ExpertProfile]:
        experts = list(self._experts.values())
        if field:
            experts = [e for e in experts if e.field == field]
        return experts

    def count_experts(self) -> int:
        return len(self._experts)

    def get_expert_skill_summary(self) -> dict:
        """Return a summary of all skills contributed by experts."""
        summary = {}
        for expert in self._experts.values():
            summary[expert.name] = {
                "field": expert.field.value,
                "organization": expert.organization,
                "skills_count": len(expert.skills_contributed),
                "skills": expert.skills_contributed,
            }
        return summary
