"""
Big Bro AI — Courses-as-Systems Module

Treats every course as a deployable system with lessons, milestones,
automations, and revenue hooks.  Big Bro delivers education in a
structured, progressive format — no "school vibes", just real application.

GLOBAL AI SOURCES FLOW: participates via big_bro_ai.py pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Course categories
# ---------------------------------------------------------------------------

class CourseCategory(Enum):
    AI_FUNDAMENTALS = "ai_fundamentals"
    AUTOMATION = "automation"
    MONEY_SYSTEMS = "money_systems"
    SALES = "sales"
    RELATIONSHIPS = "relationships"
    TECH = "tech"
    BUSINESS = "business"
    MINDSET = "mindset"
    CODING = "coding"
    FRANCHISE = "franchise"


# ---------------------------------------------------------------------------
# Lesson
# ---------------------------------------------------------------------------

@dataclass
class Lesson:
    """
    A single lesson within a course.

    Attributes
    ----------
    lesson_id : str
        Unique identifier within the course.
    title : str
        Short title.
    content : str
        The lesson text / teaching.
    takeaway : str
        One-line actionable takeaway.
    automation_hook : str
        How this lesson connects to a buildable system.
    order : int
        Position in the course.
    """

    lesson_id: str
    title: str
    content: str
    takeaway: str
    automation_hook: str = ""
    order: int = 0

    def to_dict(self) -> dict:
        return {
            "lesson_id": self.lesson_id,
            "title": self.title,
            "content": self.content,
            "takeaway": self.takeaway,
            "automation_hook": self.automation_hook,
            "order": self.order,
        }


# ---------------------------------------------------------------------------
# Milestone
# ---------------------------------------------------------------------------

@dataclass
class Milestone:
    """A measurable checkpoint within a course."""
    milestone_id: str
    title: str
    description: str
    completed: bool = False

    def to_dict(self) -> dict:
        return {
            "milestone_id": self.milestone_id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
        }


# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------

@dataclass
class Course:
    """
    A course-as-system: a complete teachable unit with lessons,
    milestones, and revenue hooks.

    Attributes
    ----------
    course_id : str
        Unique identifier.
    title : str
        Course title.
    category : CourseCategory
        Domain category.
    description : str
        What students will learn.
    price_usd : float
        Price to enrol (0 = free).
    lessons : list[Lesson]
        Ordered lesson list.
    milestones : list[Milestone]
        Checkpoints within the course.
    revenue_hook : str
        How completing this course generates or unlocks income.
    """

    course_id: str
    title: str
    category: CourseCategory
    description: str
    price_usd: float = 0.0
    lessons: list[Lesson] = field(default_factory=list)
    milestones: list[Milestone] = field(default_factory=list)
    revenue_hook: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def lesson_count(self) -> int:
        return len(self.lessons)

    def milestone_count(self) -> int:
        return len(self.milestones)

    def to_dict(self) -> dict:
        return {
            "course_id": self.course_id,
            "title": self.title,
            "category": self.category.value,
            "description": self.description,
            "price_usd": self.price_usd,
            "lesson_count": self.lesson_count(),
            "milestone_count": self.milestone_count(),
            "revenue_hook": self.revenue_hook,
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# Student enrollment record
# ---------------------------------------------------------------------------

@dataclass
class Enrollment:
    """Tracks a user's progress through a course."""
    user_id: str
    course_id: str
    completed_lessons: list[str] = field(default_factory=list)
    completed_milestones: list[str] = field(default_factory=list)
    enrolled_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def progress_pct(self, total_lessons: int) -> float:
        if total_lessons == 0:
            return 100.0
        return round(len(self.completed_lessons) / total_lessons * 100, 1)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "course_id": self.course_id,
            "completed_lessons": self.completed_lessons,
            "completed_milestones": self.completed_milestones,
            "enrolled_at": self.enrolled_at,
        }


# ---------------------------------------------------------------------------
# Courses-as-Systems Engine
# ---------------------------------------------------------------------------

class CoursesSystemError(Exception):
    """Raised when a courses-system operation fails."""


class CoursesSystem:
    """
    Creates and manages courses-as-systems for Big Bro AI.

    Each course is both a learning experience AND a deployable system
    that generates or teaches income.
    """

    def __init__(self) -> None:
        self._courses: dict[str, Course] = {}
        self._enrollments: dict[tuple[str, str], Enrollment] = {}
        self._course_counter: int = 0
        self._seed_courses()

    # ------------------------------------------------------------------
    # Seed built-in courses
    # ------------------------------------------------------------------

    def _seed_courses(self) -> None:
        """Pre-populate with the core Big Bro curriculum."""
        seed_data = [
            {
                "title": "DreamCo Money Systems 101",
                "category": CourseCategory.MONEY_SYSTEMS,
                "description": (
                    "How to build systems that pay you while you sleep. "
                    "Covers the 4 pillars: build, automate, charge, scale."
                ),
                "price_usd": 29.0,
                "revenue_hook": "Graduates can charge $500+ to build money systems for clients.",
            },
            {
                "title": "AI Automation Bootcamp",
                "category": CourseCategory.AUTOMATION,
                "description": (
                    "Practical AI automation from zero: APIs, bots, workflows, "
                    "and income-generating automation pipelines."
                ),
                "price_usd": 49.0,
                "revenue_hook": "Sell automation services at $1,000–$5,000 per project.",
            },
            {
                "title": "Relationship & Confidence Mastery",
                "category": CourseCategory.RELATIONSHIPS,
                "description": (
                    "Big Bro's framework for dating, boundaries, emotional control, "
                    "and building real confidence from competence."
                ),
                "price_usd": 19.0,
                "revenue_hook": "Build a paid community around this content.",
            },
            {
                "title": "Bot Factory Blueprint",
                "category": CourseCategory.AI_FUNDAMENTALS,
                "description": (
                    "How to design, build, and deploy income-generating bots "
                    "using the Bot Factory system."
                ),
                "price_usd": 79.0,
                "revenue_hook": "Launch a bot-as-a-service business.",
            },
            {
                "title": "Franchise & Catalog Business Model",
                "category": CourseCategory.FRANCHISE,
                "description": (
                    "How to build a franchise-ready catalog business where customers "
                    "order through your network."
                ),
                "price_usd": 99.0,
                "revenue_hook": "Recurring franchise fees + catalog commissions.",
            },
        ]
        for data in seed_data:
            self._course_counter += 1
            course_id = f"crs_{self._course_counter:04d}"
            course = Course(
                course_id=course_id,
                title=data["title"],
                category=data["category"],
                description=data["description"],
                price_usd=data["price_usd"],
                revenue_hook=data["revenue_hook"],
            )
            self._courses[course_id] = course

    # ------------------------------------------------------------------
    # Course CRUD
    # ------------------------------------------------------------------

    def create_course(
        self,
        title: str,
        category: CourseCategory,
        description: str,
        price_usd: float = 0.0,
        revenue_hook: str = "",
    ) -> Course:
        """Create a new course."""
        self._course_counter += 1
        course_id = f"crs_{self._course_counter:04d}"
        course = Course(
            course_id=course_id,
            title=title,
            category=category,
            description=description,
            price_usd=price_usd,
            revenue_hook=revenue_hook,
        )
        self._courses[course_id] = course
        return course

    def get_course(self, course_id: str) -> Optional[Course]:
        """Return a course by ID, or None."""
        return self._courses.get(course_id)

    def list_courses(
        self, category: Optional[CourseCategory] = None
    ) -> list[Course]:
        """Return all courses, optionally filtered by category."""
        courses = list(self._courses.values())
        if category is not None:
            courses = [c for c in courses if c.category == category]
        return sorted(courses, key=lambda c: c.created_at)

    def course_count(self) -> int:
        return len(self._courses)

    # ------------------------------------------------------------------
    # Lesson management
    # ------------------------------------------------------------------

    def add_lesson(
        self,
        course_id: str,
        title: str,
        content: str,
        takeaway: str,
        automation_hook: str = "",
    ) -> Lesson:
        """Add a lesson to an existing course."""
        course = self._require_course(course_id)
        order = len(course.lessons) + 1
        lesson_id = f"les_{course_id}_{order:03d}"
        lesson = Lesson(
            lesson_id=lesson_id,
            title=title,
            content=content,
            takeaway=takeaway,
            automation_hook=automation_hook,
            order=order,
        )
        course.lessons.append(lesson)
        return lesson

    # ------------------------------------------------------------------
    # Enrollment & progress
    # ------------------------------------------------------------------

    def enroll(self, user_id: str, course_id: str) -> Enrollment:
        """Enroll *user_id* in *course_id*."""
        self._require_course(course_id)
        key = (user_id, course_id)
        if key not in self._enrollments:
            self._enrollments[key] = Enrollment(
                user_id=user_id, course_id=course_id
            )
        return self._enrollments[key]

    def complete_lesson(
        self, user_id: str, course_id: str, lesson_id: str
    ) -> dict:
        """Mark a lesson as completed for *user_id*."""
        key = (user_id, course_id)
        if key not in self._enrollments:
            raise CoursesSystemError(
                f"User '{user_id}' is not enrolled in course '{course_id}'."
            )
        enrollment = self._enrollments[key]
        if lesson_id not in enrollment.completed_lessons:
            enrollment.completed_lessons.append(lesson_id)
        course = self._require_course(course_id)
        return {
            "user_id": user_id,
            "course_id": course_id,
            "lesson_id": lesson_id,
            "progress_pct": enrollment.progress_pct(course.lesson_count()),
        }

    def get_enrollment(self, user_id: str, course_id: str) -> Optional[Enrollment]:
        """Return the enrollment record, or None."""
        return self._enrollments.get((user_id, course_id))

    # ------------------------------------------------------------------
    # Revenue report
    # ------------------------------------------------------------------

    def revenue_summary(self) -> dict:
        """Summarise course catalog revenue potential."""
        courses = list(self._courses.values())
        total_catalog_value = sum(c.price_usd for c in courses)
        enrollments = len(self._enrollments)
        return {
            "total_courses": len(courses),
            "total_catalog_value_usd": round(total_catalog_value, 2),
            "total_enrollments": enrollments,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _require_course(self, course_id: str) -> Course:
        course = self._courses.get(course_id)
        if course is None:
            raise CoursesSystemError(f"No course found with id '{course_id}'.")
        return course
