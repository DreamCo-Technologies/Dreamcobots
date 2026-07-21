"""
Buddy Teach Bot — Skill Trainer

Teaches humans practical skills through structured lessons with
step-by-step guidance, quizzes, and progress tracking.

Supported skill domains (expandable):
  - Automotive: car repair, oil changes, tire rotation, diagnostics
  - Home Improvement: plumbing, electrical basics, drywall repair
  - Technology: coding basics, smartphone setup, smart home wiring
  - Culinary: cooking techniques, nutrition, food safety
  - Healthcare: first aid, CPR, wound care
  - Finance: budgeting, investing, tax filing
  - Creative: photography, music production, painting
  - Collectibles: coin grading, card authentication, antique appraisal

All scoring and progression logic is deterministic (no external ML deps).
"""

from __future__ import annotations

import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  — GLOBAL AI SOURCES FLOW


class SkillDomain(Enum):
    AUTOMOTIVE = "automotive"
    HOME_IMPROVEMENT = "home_improvement"
    TECHNOLOGY = "technology"
    CULINARY = "culinary"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    CREATIVE = "creative"
    COLLECTIBLES = "collectibles"


class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LessonStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class LessonStep:
    """A single instructional step within a lesson."""

    step_number: int
    title: str
    instruction: str
    safety_notes: list[str] = field(default_factory=list)
    tools_required: list[str] = field(default_factory=list)
    estimated_minutes: int = 5
    ar_overlay_hint: str = ""   # Hint for AR/VR overlay display

    def to_dict(self) -> dict:
        return {
            "step_number": self.step_number,
            "title": self.title,
            "instruction": self.instruction,
            "safety_notes": self.safety_notes,
            "tools_required": self.tools_required,
            "estimated_minutes": self.estimated_minutes,
            "ar_overlay_hint": self.ar_overlay_hint,
        }


@dataclass
class Lesson:
    """A structured instructional lesson."""

    lesson_id: str
    title: str
    domain: SkillDomain
    difficulty: DifficultyLevel
    description: str
    steps: list[LessonStep]
    prerequisites: list[str] = field(default_factory=list)
    estimated_total_minutes: int = 30
    passing_score: float = 0.7     # 70 % correct to pass
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "lesson_id": self.lesson_id,
            "title": self.title,
            "domain": self.domain.value,
            "difficulty": self.difficulty.value,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "prerequisites": self.prerequisites,
            "estimated_total_minutes": self.estimated_total_minutes,
            "passing_score": self.passing_score,
            "tags": self.tags,
        }


@dataclass
class LessonProgress:
    """Tracks a learner's progress through a lesson."""

    progress_id: str
    learner_id: str
    lesson_id: str
    status: LessonStatus = LessonStatus.NOT_STARTED
    current_step: int = 0
    score: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    feedback: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "progress_id": self.progress_id,
            "learner_id": self.learner_id,
            "lesson_id": self.lesson_id,
            "status": self.status.value,
            "current_step": self.current_step,
            "score": self.score,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "feedback": self.feedback,
        }


# ---------------------------------------------------------------------------
# Built-in lesson library
# ---------------------------------------------------------------------------

def _build_car_repair_basics() -> Lesson:
    return Lesson(
        lesson_id="auto-001",
        title="Car Repair Basics: Oil Change",
        domain=SkillDomain.AUTOMOTIVE,
        difficulty=DifficultyLevel.BEGINNER,
        description=(
            "Learn how to safely change your car's engine oil step by step. "
            "Buddy will guide you through the entire process with live AR overlays."
        ),
        steps=[
            LessonStep(
                step_number=1,
                title="Gather Your Supplies",
                instruction=(
                    "You will need: new engine oil (check owner's manual for grade), "
                    "a new oil filter, an oil drain pan, a socket wrench set, "
                    "and protective gloves."
                ),
                tools_required=["Socket wrench", "Oil drain pan", "Funnel", "Gloves"],
                estimated_minutes=5,
                ar_overlay_hint="Highlight supply list on screen with checkboxes",
            ),
            LessonStep(
                step_number=2,
                title="Warm Up the Engine",
                instruction=(
                    "Start your car and let it run for 2–3 minutes. Warm oil drains "
                    "faster. Then turn it off and wait 10 minutes so it is not "
                    "dangerously hot."
                ),
                safety_notes=[
                    "Never drain oil immediately after a long drive — it will be scalding hot.",
                    "Work in a well-ventilated area.",
                ],
                estimated_minutes=12,
                ar_overlay_hint="Display countdown timer overlay",
            ),
            LessonStep(
                step_number=3,
                title="Locate & Remove the Drain Plug",
                instruction=(
                    "Slide under the car and locate the oil pan drain plug. Place your "
                    "drain pan underneath. Use the correct socket to loosen the plug "
                    "counter-clockwise, then remove it by hand. Allow oil to drain fully."
                ),
                tools_required=["Socket wrench", "Oil drain pan"],
                safety_notes=["Wear gloves — oil may still be warm."],
                estimated_minutes=10,
                ar_overlay_hint="AR arrow pointing to drain plug location",
            ),
            LessonStep(
                step_number=4,
                title="Replace the Oil Filter",
                instruction=(
                    "Unscrew the old oil filter. Apply a thin film of new oil to the "
                    "rubber gasket of the new filter. Hand-tighten the new filter — "
                    "do NOT use a wrench."
                ),
                tools_required=["Oil filter wrench (removal only)", "New oil filter"],
                estimated_minutes=8,
                ar_overlay_hint="Zoom-in AR view of filter location",
            ),
            LessonStep(
                step_number=5,
                title="Reinstall the Drain Plug & Add New Oil",
                instruction=(
                    "Thread the drain plug back in clockwise and tighten with the "
                    "socket wrench — snug but not over-torqued. Open the hood, remove "
                    "the oil filler cap, insert the funnel, and pour in the new oil."
                ),
                tools_required=["Socket wrench", "Funnel", "New engine oil"],
                estimated_minutes=7,
                ar_overlay_hint="Torque indicator overlay on drain plug",
            ),
            LessonStep(
                step_number=6,
                title="Check Oil Level & Test",
                instruction=(
                    "Replace the oil filler cap. Start the engine and let it run for "
                    "60 seconds. Check under the car for leaks. Turn off the engine, "
                    "wait 2 minutes, then pull the dipstick to verify oil level is "
                    "between MIN and MAX."
                ),
                safety_notes=["Dispose of old oil responsibly at a recycling centre."],
                estimated_minutes=5,
                ar_overlay_hint="Dipstick MIN/MAX indicator overlay",
            ),
        ],
        estimated_total_minutes=47,
        tags=["car", "oil change", "automotive", "maintenance"],
    )


def _build_tire_rotation() -> Lesson:
    return Lesson(
        lesson_id="auto-002",
        title="Tire Rotation",
        domain=SkillDomain.AUTOMOTIVE,
        difficulty=DifficultyLevel.BEGINNER,
        description="Rotate your vehicle's tires to even out wear and extend tire life.",
        steps=[
            LessonStep(1, "Check Your Manual", "Consult your owner's manual for the recommended rotation pattern.", estimated_minutes=3),
            LessonStep(2, "Loosen Lug Nuts", "Before lifting the car, loosen each lug nut slightly with the lug wrench.", tools_required=["Lug wrench"], estimated_minutes=5, safety_notes=["Do NOT remove them yet."]),
            LessonStep(3, "Jack Up the Car", "Place the jack under the designated jack points and raise the vehicle. Secure with jack stands.", tools_required=["Car jack", "Jack stands"], safety_notes=["Never work under a car supported only by a hydraulic jack."], estimated_minutes=10),
            LessonStep(4, "Rotate Tires", "Follow the rotation pattern: front-to-rear, cross, or X-pattern based on tire type.", estimated_minutes=15),
            LessonStep(5, "Torque Lug Nuts", "Tighten lug nuts in a star pattern to the manufacturer's spec.", tools_required=["Torque wrench"], estimated_minutes=5),
            LessonStep(6, "Lower & Verify", "Lower the vehicle, remove jack stands, and double-check lug nut torque.", estimated_minutes=5),
        ],
        estimated_total_minutes=43,
        tags=["car", "tire", "rotation", "maintenance"],
    )


def _build_first_aid_cpr() -> Lesson:
    return Lesson(
        lesson_id="health-001",
        title="CPR Basics",
        domain=SkillDomain.HEALTHCARE,
        difficulty=DifficultyLevel.BEGINNER,
        description="Learn adult CPR technique: chest compressions and rescue breaths.",
        steps=[
            LessonStep(1, "Check for Safety", "Ensure the scene is safe before approaching.", safety_notes=["Never put yourself in danger."], estimated_minutes=1),
            LessonStep(2, "Check Responsiveness", "Tap shoulders firmly and shout 'Are you OK?'", estimated_minutes=1),
            LessonStep(3, "Call for Help", "Call emergency services (911) or have someone else call while you begin CPR.", estimated_minutes=1),
            LessonStep(4, "Chest Compressions", "Place heel of hand on centre of chest. Compress 2 inches deep at 100–120 BPM. Do 30 compressions.", ar_overlay_hint="Metronome beat overlay at 110 BPM", estimated_minutes=3),
            LessonStep(5, "Rescue Breaths", "Tilt head back, lift chin. Pinch nose, give 2 rescue breaths watching for chest rise.", estimated_minutes=2),
            LessonStep(6, "Continue Cycles", "Repeat 30 compressions + 2 breaths until help arrives or the person recovers.", estimated_minutes=5),
        ],
        estimated_total_minutes=13,
        tags=["healthcare", "cpr", "first aid", "emergency"],
    )


def _build_basic_investing() -> Lesson:
    return Lesson(
        lesson_id="finance-001",
        title="Investing 101: Stock Market Basics",
        domain=SkillDomain.FINANCE,
        difficulty=DifficultyLevel.BEGINNER,
        description="Understand how the stock market works and how to start investing.",
        steps=[
            LessonStep(1, "What is a Stock?", "A stock represents partial ownership in a company. When the company grows, your share value increases.", estimated_minutes=5),
            LessonStep(2, "Key Terms", "Learn: ticker symbol, market cap, dividend, P/E ratio, portfolio diversification.", estimated_minutes=8),
            LessonStep(3, "Opening a Brokerage Account", "Choose a regulated broker, verify identity, and fund the account.", estimated_minutes=10),
            LessonStep(4, "Placing Your First Trade", "Search for a ticker, review the stock's 52-week range, and place a limit order.", estimated_minutes=7),
            LessonStep(5, "Risk Management", "Never invest more than you can afford to lose. Diversify across sectors.", safety_notes=["This is educational only — consult a financial advisor for personal advice."], estimated_minutes=8),
        ],
        estimated_total_minutes=38,
        tags=["finance", "investing", "stocks", "beginners"],
    )


LESSON_LIBRARY: dict[str, Lesson] = {
    lesson.lesson_id: lesson
    for lesson in [
        _build_car_repair_basics(),
        _build_tire_rotation(),
        _build_first_aid_cpr(),
        _build_basic_investing(),
    ]
}


class SkillTrainerError(Exception):
    """Raised when a skill-training operation fails."""


class SkillTrainer:
    """
    Human skill trainer.

    Manages the lesson library, tracks learner progress, and awards
    completion certificates upon passing.
    """

    def __init__(self, max_skill_tracks: Optional[int] = 3) -> None:
        self.max_skill_tracks = max_skill_tracks
        self._library: dict[str, Lesson] = dict(LESSON_LIBRARY)
        self._progress: dict[str, LessonProgress] = {}   # progress_id -> LessonProgress
        self._certificates: list[dict] = []

    # ------------------------------------------------------------------
    # Library management
    # ------------------------------------------------------------------

    def add_lesson(self, lesson: Lesson) -> None:
        """Add a custom lesson to the library."""
        active_domains = {
            self._library[lid].domain
            for lid in self._library
        }
        if (
            self.max_skill_tracks is not None
            and lesson.domain not in active_domains
            and len(active_domains) >= self.max_skill_tracks
        ):
            raise SkillTrainerError(
                f"Max skill tracks ({self.max_skill_tracks}) reached. "
                "Upgrade to add more domains."
            )
        self._library[lesson.lesson_id] = lesson

    def list_lessons(
        self,
        domain: Optional[SkillDomain] = None,
        difficulty: Optional[DifficultyLevel] = None,
    ) -> list[Lesson]:
        lessons = list(self._library.values())
        if domain:
            lessons = [l for l in lessons if l.domain == domain]
        if difficulty:
            lessons = [l for l in lessons if l.difficulty == difficulty]
        return lessons

    def get_lesson(self, lesson_id: str) -> Lesson:
        if lesson_id not in self._library:
            raise SkillTrainerError(f"Lesson '{lesson_id}' not found.")
        return self._library[lesson_id]

    # ------------------------------------------------------------------
    # Progress tracking
    # ------------------------------------------------------------------

    def start_lesson(self, learner_id: str, lesson_id: str) -> LessonProgress:
        """Begin tracking a learner's progress through a lesson."""
        if lesson_id not in self._library:
            raise SkillTrainerError(f"Lesson '{lesson_id}' not found.")
        progress = LessonProgress(
            progress_id=str(uuid.uuid4()),
            learner_id=learner_id,
            lesson_id=lesson_id,
            status=LessonStatus.IN_PROGRESS,
            current_step=1,
            started_at=time.time(),
        )
        self._progress[progress.progress_id] = progress
        return progress

    def advance_step(self, progress_id: str) -> LessonProgress:
        """Advance the learner to the next step."""
        progress = self._get_progress(progress_id)
        lesson = self.get_lesson(progress.lesson_id)
        if progress.status != LessonStatus.IN_PROGRESS:
            raise SkillTrainerError(
                f"Progress '{progress_id}' is not in-progress "
                f"(status: {progress.status.value})."
            )
        if progress.current_step < len(lesson.steps):
            progress.current_step += 1
        return progress

    def complete_lesson(
        self, progress_id: str, quiz_score: float
    ) -> LessonProgress:
        """
        Mark a lesson as complete and record the quiz score.

        quiz_score: 0.0–1.0 representing fraction of questions correct.
        """
        progress = self._get_progress(progress_id)
        lesson = self.get_lesson(progress.lesson_id)
        progress.score = max(0.0, min(1.0, quiz_score))
        progress.completed_at = time.time()
        if progress.score >= lesson.passing_score:
            progress.status = LessonStatus.COMPLETED
            self._issue_certificate(progress, lesson)
            progress.feedback.append(
                f"Congratulations! You passed '{lesson.title}' "
                f"with a score of {progress.score * 100:.0f}%."
            )
        else:
            progress.status = LessonStatus.FAILED
            progress.feedback.append(
                f"You scored {progress.score * 100:.0f}% — "
                f"you need {lesson.passing_score * 100:.0f}% to pass. "
                "Keep practising and try again!"
            )
        return progress

    def get_progress(self, progress_id: str) -> LessonProgress:
        return self._get_progress(progress_id)

    def list_learner_progress(self, learner_id: str) -> list[LessonProgress]:
        return [p for p in self._progress.values() if p.learner_id == learner_id]

    def learner_certificates(self, learner_id: str) -> list[dict]:
        return [c for c in self._certificates if c["learner_id"] == learner_id]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_progress(self, progress_id: str) -> LessonProgress:
        if progress_id not in self._progress:
            raise SkillTrainerError(f"Progress record '{progress_id}' not found.")
        return self._progress[progress_id]

    def _issue_certificate(self, progress: LessonProgress, lesson: Lesson) -> None:
        cert = {
            "certificate_id": str(uuid.uuid4()),
            "learner_id": progress.learner_id,
            "lesson_id": lesson.lesson_id,
            "lesson_title": lesson.title,
            "domain": lesson.domain.value,
            "score": progress.score,
            "issued_at": progress.completed_at,
        }
        self._certificates.append(cert)

    def domain_summary(self) -> dict:
        """Return a count of lessons per domain."""
        summary: dict[str, int] = {}
        for lesson in self._library.values():
            key = lesson.domain.value
            summary[key] = summary.get(key, 0) + 1
        return summary
