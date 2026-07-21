"""
DreamCo Empire OS — Learning Matrix Module

AI-powered hub for self-improvement resources, Big Bro mentorship lessons,
personal growth tracking, and skill progression across empire-relevant domains.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from framework import GlobalAISourcesFlow  # noqa: F401


class LearningDomain(Enum):
    FINANCE = "finance"
    TECH = "tech"
    MARKETING = "marketing"
    LEADERSHIP = "leadership"
    AUTOMATION = "automation"
    SALES = "sales"
    MINDSET = "mindset"
    CRYPTO = "crypto"


class SkillLevel(Enum):
    NOVICE = "novice"
    APPRENTICE = "apprentice"
    JOURNEYMAN = "journeyman"
    EXPERT = "expert"
    MASTER = "master"


@dataclass
class Lesson:
    """A single learning module lesson."""
    lesson_id: str
    title: str
    domain: LearningDomain
    content: str
    xp_reward: int = 10
    completed: bool = False
    completed_at: Optional[str] = None


@dataclass
class LearnerProfile:
    """Tracks a learner's progress across all domains."""
    learner_id: str
    name: str
    xp: int = 0
    level: int = 1
    completed_lessons: list = field(default_factory=list)
    domain_scores: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def add_xp(self, amount: int) -> None:
        self.xp += amount
        self.level = max(1, self.xp // 100 + 1)

    def get_skill_level(self, domain: LearningDomain) -> SkillLevel:
        score = self.domain_scores.get(domain.value, 0)
        if score >= 500:
            return SkillLevel.MASTER
        if score >= 250:
            return SkillLevel.EXPERT
        if score >= 100:
            return SkillLevel.JOURNEYMAN
        if score >= 40:
            return SkillLevel.APPRENTICE
        return SkillLevel.NOVICE


_BUILTIN_LESSONS = [
    ("lesson_001", "Compound Interest Fundamentals", LearningDomain.FINANCE,
     "Money compounds. $1,000 at 10% monthly becomes $3,138 in 12 months. "
     "Start small, reinvest everything, let time do the heavy lifting.", 25),
    ("lesson_002", "Automating Your First Income Stream", LearningDomain.AUTOMATION,
     "Automation is leverage. Build a system once, run it forever. "
     "Pick one repetitive task today and script it.", 30),
    ("lesson_003", "DreamCo Bot Creation 101", LearningDomain.TECH,
     "Every bot starts with a clear job: what problem does it solve? "
     "Define the input, output, and trigger before writing one line of code.", 20),
    ("lesson_004", "Empire Mindset — Think Long-Term", LearningDomain.MINDSET,
     "Losers ask 'how do I make $100 today?' Winners ask 'what system makes $100/day forever?' "
     "Big Bro says: build the machine, not just the product.", 15),
    ("lesson_005", "Lead Generation Basics", LearningDomain.MARKETING,
     "Leads are lifeblood. You need a consistent inbound channel: "
     "SEO, scraping, paid ads, or referrals. Pick one and master it.", 20),
    ("lesson_006", "Crypto Fundamentals for the Empire", LearningDomain.CRYPTO,
     "Understand volatility, liquidity, and on-chain signals. "
     "Never invest more than you can lose. Bots can trade 24/7 while you sleep.", 25),
    ("lesson_007", "Closing Deals with Confidence", LearningDomain.SALES,
     "The close is simple: handle objections, show ROI, then be quiet. "
     "The first person to speak after the ask loses.", 20),
]


class LearningMatrix:
    """
    Learning Matrix — empire-grade self-improvement and mentorship system.

    Tracks learner progress, delivers Big Bro lessons, awards XP,
    and generates personalised learning paths.
    """

    BIG_BRO_TIPS = [
        "Stay sharp. Build smarter than everybody else.",
        "They might laugh today but they'll copy tomorrow.",
        "You're building an empire. Keep going.",
        "Short kings run tech empires too.",
        "Every day you don't learn, you fall behind someone who does.",
        "Knowledge compounds just like money — start stacking.",
    ]

    def __init__(self) -> None:
        self._lessons: dict[str, Lesson] = {}
        self._learners: dict[str, LearnerProfile] = {}
        self._load_builtins()

    def _load_builtins(self) -> None:
        for lid, title, domain, content, xp in _BUILTIN_LESSONS:
            self._lessons[lid] = Lesson(lesson_id=lid, title=title, domain=domain,
                                        content=content, xp_reward=xp)

    # ------------------------------------------------------------------
    # Learner management
    # ------------------------------------------------------------------

    def add_learner(self, learner_id: str, name: str) -> dict:
        """Register a new learner."""
        profile = LearnerProfile(learner_id=learner_id, name=name)
        self._learners[learner_id] = profile
        return _learner_to_dict(profile)

    def get_learner(self, learner_id: str) -> dict:
        return _learner_to_dict(self._get_learner(learner_id))

    # ------------------------------------------------------------------
    # Lessons
    # ------------------------------------------------------------------

    def add_lesson(
        self,
        lesson_id: str,
        title: str,
        domain: LearningDomain,
        content: str,
        xp_reward: int = 10,
    ) -> dict:
        """Add a custom lesson to the matrix."""
        lesson = Lesson(lesson_id=lesson_id, title=title, domain=domain,
                        content=content, xp_reward=xp_reward)
        self._lessons[lesson_id] = lesson
        return _lesson_to_dict(lesson)

    def complete_lesson(self, learner_id: str, lesson_id: str) -> dict:
        """Mark a lesson as completed and award XP to the learner."""
        learner = self._get_learner(learner_id)
        lesson = self._get_lesson(lesson_id)

        if lesson_id in learner.completed_lessons:
            return {"status": "already_completed", "lesson_id": lesson_id}

        lesson.completed = True
        lesson.completed_at = datetime.now(timezone.utc).isoformat()
        learner.completed_lessons.append(lesson_id)
        learner.add_xp(lesson.xp_reward)

        domain_key = lesson.domain.value
        learner.domain_scores[domain_key] = learner.domain_scores.get(domain_key, 0) + lesson.xp_reward

        return {
            "status": "completed",
            "lesson_id": lesson_id,
            "title": lesson.title,
            "xp_earned": lesson.xp_reward,
            "learner_xp": learner.xp,
            "learner_level": learner.level,
            "big_bro_tip": self._tip(),
        }

    def get_learning_path(self, learner_id: str) -> list:
        """Return recommended next lessons based on learner's weakest domains."""
        learner = self._get_learner(learner_id)
        completed = set(learner.completed_lessons)

        remaining = [
            lesson for lid, lesson in self._lessons.items()
            if lid not in completed
        ]
        remaining.sort(key=lambda l: learner.domain_scores.get(l.domain.value, 0))
        return [_lesson_to_dict(l) for l in remaining[:5]]

    def list_lessons(self, domain: Optional[LearningDomain] = None) -> list:
        """Return all lessons, optionally filtered by domain."""
        lessons = list(self._lessons.values())
        if domain:
            lessons = [l for l in lessons if l.domain == domain]
        return [_lesson_to_dict(l) for l in lessons]

    def big_bro_motivate(self) -> str:
        """Return a random Big Bro motivational message."""
        return self._tip()

    def get_stats(self) -> dict:
        return {
            "total_lessons": len(self._lessons),
            "total_learners": len(self._learners),
            "domains": [d.value for d in LearningDomain],
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _tip(self) -> str:
        import random
        return random.choice(self.BIG_BRO_TIPS)

    def _get_learner(self, learner_id: str) -> LearnerProfile:
        if learner_id not in self._learners:
            raise KeyError(f"Learner '{learner_id}' not found.")
        return self._learners[learner_id]

    def _get_lesson(self, lesson_id: str) -> Lesson:
        if lesson_id not in self._lessons:
            raise KeyError(f"Lesson '{lesson_id}' not found.")
        return self._lessons[lesson_id]


def _learner_to_dict(p: LearnerProfile) -> dict:
    return {
        "learner_id": p.learner_id,
        "name": p.name,
        "xp": p.xp,
        "level": p.level,
        "completed_lessons": p.completed_lessons,
        "domain_scores": p.domain_scores,
        "created_at": p.created_at,
    }


def _lesson_to_dict(l: Lesson) -> dict:
    return {
        "lesson_id": l.lesson_id,
        "title": l.title,
        "domain": l.domain.value,
        "content": l.content,
        "xp_reward": l.xp_reward,
        "completed": l.completed,
        "completed_at": l.completed_at,
    }
