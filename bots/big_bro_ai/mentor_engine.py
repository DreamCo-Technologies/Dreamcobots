"""
Big Bro AI — Mentor Engine

Multi-domain mentoring flows covering money, tech, relationships,
confidence, and life situations.  Big Bro adjusts advice based on
the user's growth trajectory — he stops repeating lessons people
already learned and pushes harder when someone is ready.

GLOBAL AI SOURCES FLOW: participates via big_bro_ai.py pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Mentoring domains
# ---------------------------------------------------------------------------

class MentorDomain(Enum):
    MONEY = "money"
    TECH = "tech"
    RELATIONSHIPS = "relationships"
    CONFIDENCE = "confidence"
    LIFE = "life"
    DISCIPLINE = "discipline"
    COMMUNITY = "community"


# ---------------------------------------------------------------------------
# Growth stage — determines how hard Big Bro pushes
# ---------------------------------------------------------------------------

class GrowthStage(Enum):
    SEED = "seed"           # Needs encouragement and basics
    GROWING = "growing"     # Needs direction and accountability
    BUILDING = "building"   # Needs discipline and strategy
    SCALING = "scaling"     # Needs optimization and advanced tools


# ---------------------------------------------------------------------------
# Lesson library
# ---------------------------------------------------------------------------

MONEY_LESSONS: dict[str, str] = {
    "subscriptions_vs_onetime": (
        "Why subscriptions beat one-time sales: "
        "A one-time sale ends. A subscription compounds. "
        "100 people paying $10/month is $1,000/month, then $1,000 next month too."
    ),
    "automation_beats_grinding": (
        "Automation beats grinding: your time is finite, "
        "but a system runs 24/7. Build the system once, collect repeatedly."
    ),
    "small_payments_scale": (
        "Small payments scale: $10 from 1,000 people is $10,000. "
        "Stop chasing whales. Build distribution."
    ),
    "ownership_vs_labor": (
        "Ownership > labor: laborers trade time for money. "
        "Owners build assets that generate money without their time."
    ),
    "traffic_conversion": (
        "Traffic × Conversion = Revenue. "
        "Get people to your system, then make sure the system converts them."
    ),
    "compound_logic": (
        "Compound interest works on money AND skills. "
        "Every day you build is worth more than the last because skills compound."
    ),
    "income_lanes": (
        "Multiple income lanes: AI chatbots, automation services, "
        "subscriptions, digital products, templates, SaaS tools, consulting."
    ),
    "fast_vs_scale": (
        "What pays fast: services (consulting, done-for-you automation). "
        "What scales long-term: products, subscriptions, platforms."
    ),
}

TECH_LESSONS: dict[str, str] = {
    "ai_fundamentals": (
        "AI fundamentals: models learn patterns from data. "
        "The more relevant data, the smarter the model."
    ),
    "automation_logic": (
        "Automation logic: identify repetitive tasks, write the rule once, "
        "let the system run it forever."
    ),
    "apis": (
        "APIs are bridges between systems. "
        "Master APIs and you can connect any two tools in existence."
    ),
    "saas_thinking": (
        "SaaS thinking: instead of solving a problem once, "
        "build a system that solves it for thousands."
    ),
    "platform_economics": (
        "Platforms make money by connecting supply and demand. "
        "You don't need to be the supply OR the demand — just the platform."
    ),
    "tech_beats_popularity": (
        "Tech beats popularity: a viral post lasts a week. "
        "A working system lasts forever and pays you while you sleep."
    ),
}

RELATIONSHIP_LESSONS: dict[str, str] = {
    "dont_chase": (
        "Don't chase attention. Build yourself so attention has no choice "
        "but to find you."
    ),
    "rejection": (
        "Rejection is redirection. Every no removes someone who wasn't aligned "
        "and makes room for someone who is."
    ),
    "boundaries": (
        "Boundaries aren't walls — they're the rules that protect your energy. "
        "Enforce them calmly, not emotionally."
    ),
    "emotional_control": (
        "Emotional control is power. The person who stays calm in conflict "
        "always has the upper hand."
    ),
    "not_simping": (
        "Investing in someone who doesn't invest back isn't loyalty — it's a "
        "transaction with no return. Value yourself."
    ),
    "respect_without_weakness": (
        "Respect is non-negotiable, but it's not weakness. "
        "You can be kind and still have standards."
    ),
}

CONFIDENCE_LESSONS: dict[str, str] = {
    "competence_to_confidence": (
        "Confidence comes from competence. "
        "Stop waiting to feel confident — build the skill, confidence follows."
    ),
    "power_is_leverage": (
        "Power isn't physical. It's leverage. "
        "The person who controls the system controls the outcome."
    ),
    "young_is_advantage": (
        "Being young is an advantage. "
        "You have time to fail, learn, and build before most people even start."
    ),
    "technical_is_weapon": (
        "Being technical is a superpower. "
        "You can build what others can only imagine."
    ),
    "no_approval_needed": (
        "You don't need approval. You need execution. "
        "The results speak louder than any opinion."
    ),
}

DISCIPLINE_LESSONS: dict[str, str] = {
    "consistency_over_intensity": (
        "Consistency beats intensity every time. "
        "Showing up daily for a year outperforms a week of all-nighters."
    ),
    "one_task_ship": (
        "Today we ship one improvement. "
        "Progress is built in units — one unit at a time."
    ),
    "stoic_mindset": (
        "Control what you can control. Release what you can't. "
        "Waste zero energy on things outside your domain."
    ),
    "daily_upgrade": (
        "Every day you don't improve, someone else is. "
        "1% better daily is 37x better in a year."
    ),
}


# ---------------------------------------------------------------------------
# Mentor Engine
# ---------------------------------------------------------------------------

class MentorEngineError(Exception):
    """Raised when a mentoring operation fails."""


@dataclass
class MentorEngine:
    """
    Multi-domain mentoring engine for Big Bro AI.

    Tracks what lessons each user has already received and advances them
    to the next level when they are ready.

    Parameters
    ----------
    enabled_domains : list[MentorDomain]
        Domains available on the current tier.
    """

    enabled_domains: list[MentorDomain] = field(
        default_factory=lambda: list(MentorDomain)
    )
    _user_progress: dict[str, dict[str, list[str]]] = field(
        default_factory=dict, init=False, repr=False
    )

    # ------------------------------------------------------------------
    # Domain check
    # ------------------------------------------------------------------

    def _require_domain(self, domain: MentorDomain) -> None:
        if domain not in self.enabled_domains:
            raise MentorEngineError(
                f"Domain '{domain.value}' is not available on your current tier."
            )

    # ------------------------------------------------------------------
    # Lesson delivery
    # ------------------------------------------------------------------

    def teach(self, user_id: str, domain: MentorDomain, topic: Optional[str] = None) -> dict:
        """
        Deliver a lesson to *user_id* in *domain*.

        If *topic* is not specified, the next unlearned lesson is returned.

        Returns
        -------
        dict
            ``{"domain", "topic", "lesson", "already_learned": bool}``
        """
        self._require_domain(domain)
        lesson_map = self._get_lesson_map(domain)
        if not lesson_map:
            return {
                "domain": domain.value,
                "topic": "general",
                "lesson": "Keep studying — more lessons coming soon.",
                "already_learned": False,
            }

        learned = self._get_learned(user_id, domain)

        if topic is not None:
            already = topic in learned
            lesson_text = lesson_map.get(
                topic, "That topic isn't in my lesson library yet."
            )
            if not already:
                self._mark_learned(user_id, domain, topic)
            return {
                "domain": domain.value,
                "topic": topic,
                "lesson": lesson_text,
                "already_learned": already,
            }

        # Auto-pick next unlearned lesson
        for t, lesson_text in lesson_map.items():
            if t not in learned:
                self._mark_learned(user_id, domain, t)
                return {
                    "domain": domain.value,
                    "topic": t,
                    "lesson": lesson_text,
                    "already_learned": False,
                }

        # All lessons learned — push to next stage
        return {
            "domain": domain.value,
            "topic": "advanced",
            "lesson": (
                f"You've mastered the basics of {domain.value}. "
                "Time to apply. What are you building?"
            ),
            "already_learned": True,
        }

    # ------------------------------------------------------------------
    # Growth stage
    # ------------------------------------------------------------------

    def assess_growth_stage(self, user_id: str) -> GrowthStage:
        """
        Infer the user's growth stage from lessons completed.

        Returns
        -------
        GrowthStage
        """
        total_learned = sum(
            len(lessons)
            for lessons in self._user_progress.get(user_id, {}).values()
        )
        if total_learned < 3:
            return GrowthStage.SEED
        if total_learned < 8:
            return GrowthStage.GROWING
        if total_learned < 15:
            return GrowthStage.BUILDING
        return GrowthStage.SCALING

    def daily_task(self, user_id: str) -> str:
        """Return a daily task appropriate for the user's growth stage."""
        stage = self.assess_growth_stage(user_id)
        tasks = {
            GrowthStage.SEED: "Write down one thing you want to build and why.",
            GrowthStage.GROWING: "Complete one automation tutorial and document what you learned.",
            GrowthStage.BUILDING: "Ship one small improvement to your current project today.",
            GrowthStage.SCALING: "Identify one bottleneck in your system and eliminate it.",
        }
        return tasks[stage]

    def growth_message(self, user_id: str) -> str:
        """Return a growth-appropriate motivational message."""
        stage = self.assess_growth_stage(user_id)
        messages = {
            GrowthStage.SEED: (
                "Last year you needed encouragement. Now you need a plan. Let's build one."
            ),
            GrowthStage.GROWING: (
                "You've got momentum. Don't lose it — show up tomorrow too."
            ),
            GrowthStage.BUILDING: (
                "You're past the beginner phase. Time for discipline, not motivation."
            ),
            GrowthStage.SCALING: (
                "Last year you needed encouragement. Now you need discipline. "
                "Welcome to the next level."
            ),
        }
        return messages[stage]

    # ------------------------------------------------------------------
    # Progress report
    # ------------------------------------------------------------------

    def progress_report(self, user_id: str) -> dict:
        """Return a full progress report for *user_id*."""
        stage = self.assess_growth_stage(user_id)
        domain_progress = {}
        for domain in MentorDomain:
            learned = self._get_learned(user_id, domain)
            total = len(self._get_lesson_map(domain))
            domain_progress[domain.value] = {
                "learned": len(learned),
                "total": total,
                "topics": learned,
            }
        return {
            "user_id": user_id,
            "growth_stage": stage.value,
            "daily_task": self.daily_task(user_id),
            "domains": domain_progress,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_lesson_map(self, domain: MentorDomain) -> dict[str, str]:
        maps = {
            MentorDomain.MONEY: MONEY_LESSONS,
            MentorDomain.TECH: TECH_LESSONS,
            MentorDomain.RELATIONSHIPS: RELATIONSHIP_LESSONS,
            MentorDomain.CONFIDENCE: CONFIDENCE_LESSONS,
            MentorDomain.DISCIPLINE: DISCIPLINE_LESSONS,
            MentorDomain.LIFE: {**CONFIDENCE_LESSONS, **DISCIPLINE_LESSONS},
            MentorDomain.COMMUNITY: {
                "leader_energy": (
                    "Community leaders don't demand respect — they earn it "
                    "by adding value consistently."
                ),
                "teach_to_lead": (
                    "Teaching what you know elevates your status. "
                    "The person who helps others learn is always valued."
                ),
            },
        }
        return maps.get(domain, {})

    def _get_learned(self, user_id: str, domain: MentorDomain) -> list[str]:
        return self._user_progress.get(user_id, {}).get(domain.value, [])

    def _mark_learned(self, user_id: str, domain: MentorDomain, topic: str) -> None:
        if user_id not in self._user_progress:
            self._user_progress[user_id] = {}
        if domain.value not in self._user_progress[user_id]:
            self._user_progress[user_id][domain.value] = []
        if topic not in self._user_progress[user_id][domain.value]:
            self._user_progress[user_id][domain.value].append(topic)
