"""
Dreamcobots Education Bot — tier-aware course management and learning platform.

Usage
-----
    from education_bot import EducationBot
    from tiers import Tier

    bot = EducationBot(tier=Tier.FREE)
    course = bot.create_course("Intro to Python", ["Variables", "Loops", "Functions"])
    print(course)
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path

import importlib.util as _ilu
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_spec = _ilu.spec_from_file_location("_education_tiers", os.path.join(_THIS_DIR, "tiers.py"))
_education_tiers = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_education_tiers)
EDUCATION_FEATURES = _education_tiers.EDUCATION_FEATURES
COURSE_LIMITS = _education_tiers.COURSE_LIMITS
get_education_tier_info = _education_tiers.get_education_tier_info


class EducationBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class EducationBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class EducationBot:
    """
    Tier-aware education and course management bot.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling course limits and feature availability.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._courses: dict[str, dict] = {}
        self._progress: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def create_course(self, title: str, content: list[str]) -> dict:
        """
        Create a new course.

        Parameters
        ----------
        title : str
            Course title.
        content : list[str]
            List of lesson topics/modules.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        course_limit = COURSE_LIMITS[self.tier.value]
        if course_limit is not None and len(self._courses) >= course_limit:
            raise EducationBotTierError(
                f"Course limit of {course_limit} reached on the {self.config.name} tier. "
                "Upgrade to create more courses."
            )
        course_id = f"COURSE-{len(self._courses) + 1:04d}"
        self._request_count += 1
        course = {
            "course_id": course_id,
            "title": title,
            "content": content,
            "lessons": len(content),
            "status": "active",
        }
        self._courses[course_id] = course
        self._progress[course_id] = {"completed_lessons": 0, "total_lessons": len(content)}
        return {
            "course": course,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def generate_quiz(self, course_id: str, num_questions: int = 5) -> dict:
        """
        Generate quiz questions for a course.

        Parameters
        ----------
        course_id : str
            ID of the course to quiz on.
        num_questions : int
            Number of questions to generate.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        if course_id not in self._courses:
            raise EducationBotTierError(f"Course '{course_id}' not found.")
        self._request_count += 1
        questions = [
            {
                "question_id": f"Q-{i + 1:03d}",
                "question": f"Mock question {i + 1} about {self._courses[course_id]['title']}",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
            }
            for i in range(num_questions)
        ]
        return {
            "course_id": course_id,
            "questions": questions,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def submit_answer(self, course_id: str, question_id: str, answer: str) -> dict:
        """
        Submit an answer for a quiz question.

        Parameters
        ----------
        course_id : str
            Course ID the question belongs to.
        question_id : str
            ID of the question being answered.
        answer : str
            The submitted answer.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        if course_id not in self._courses:
            raise EducationBotTierError(f"Course '{course_id}' not found.")
        self._request_count += 1
        correct = answer == "Option A"
        return {
            "course_id": course_id,
            "question_id": question_id,
            "submitted_answer": answer,
            "correct": correct,
            "feedback": "Correct!" if correct else "Incorrect. The correct answer is Option A.",
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def get_progress(self, course_id: str) -> dict:
        """
        Get progress metrics for a course.

        Parameters
        ----------
        course_id : str
            ID of the course.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        if course_id not in self._courses:
            raise EducationBotTierError(f"Course '{course_id}' not found.")
        self._request_count += 1
        prog = self._progress[course_id]
        total = prog["total_lessons"]
        completed = prog["completed_lessons"]
        pct = round((completed / total) * 100, 1) if total > 0 else 0.0
        return {
            "course_id": course_id,
            "course_title": self._courses[course_id]["title"],
            "completed_lessons": completed,
            "total_lessons": total,
            "completion_pct": pct,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    # ------------------------------------------------------------------
    # Tier information
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Print and return a description of the current tier."""
        info = get_education_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        course_limit = (
            "Unlimited"
            if info["course_limit"] is None
            else str(info["course_limit"])
        )
        lines = [
            f"=== {info['name']} Education Bot Tier ===",
            f"Price        : ${info['price_usd_monthly']:.2f}/month",
            f"Requests     : {limit}/month",
            f"Course limit : {course_limit}",
            f"Support      : {info['support_level']}",
            "",
            "Features:",
        ]
        for feat in info["education_features"]:
            lines.append(f"  ✓ {feat}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Print details about the next available tier upgrade."""
        next_cfg = get_upgrade_path(self.tier)
        if next_cfg is None:
            msg = f"You are already on the top-tier plan ({self.config.name})."
            print(msg)
            return msg
        current_feats = set(EDUCATION_FEATURES[self.tier.value])
        new_feats = [f for f in EDUCATION_FEATURES[next_cfg.tier.value] if f not in current_feats]
        lines = [
            f"=== Upgrade: {self.config.name} → {next_cfg.name} ===",
            f"New price: ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New features:",
        ]
        for feat in new_feats:
            lines.append(f"  + {feat}")
        lines.append(
            f"\nTo upgrade, set tier=Tier.{next_cfg.tier.name} when "
            "constructing EducationBot or contact support."
        )
        output = "\n".join(lines)
        print(output)
        return output

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise EducationBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))


if __name__ == "__main__":
    bot = EducationBot(tier=Tier.FREE)
    bot.describe_tier()
    course = bot.create_course("Intro to Python", ["Variables", "Loops", "Functions"])
    print(course)
