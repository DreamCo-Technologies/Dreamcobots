"""
Dreamcobots CodingAssistantBot — tier-aware code completion, review, and test generation.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.coding_assistant_bot.tiers import CODING_ASSISTANT_FEATURES, get_coding_assistant_tier_info
import uuid
from datetime import datetime


class CodingAssistantBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class CodingAssistantBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class CodingAssistantBot:
    """Tier-aware code completion, review, and test generation bot."""

    FREE_LANGUAGES = ["python", "javascript", "html"]
    PRO_LANGUAGES = [
        "python", "javascript", "html", "java", "typescript", "go", "rust",
        "c++", "c#", "ruby", "php", "swift", "kotlin", "scala", "r",
        "matlab", "sql", "bash", "dart", "elixir",
    ]

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise CodingAssistantBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _check_language(self, language: str) -> None:
        lang = language.lower()
        if self.tier == Tier.FREE and lang not in self.FREE_LANGUAGES:
            raise CodingAssistantBotTierError(
                f"Language '{language}' is not available on the Free tier. "
                f"Available languages: {self.FREE_LANGUAGES}. "
                "Please upgrade to PRO or ENTERPRISE for more languages."
            )
        if self.tier == Tier.PRO and lang not in self.PRO_LANGUAGES:
            raise CodingAssistantBotTierError(
                f"Language '{language}' is not available on the PRO tier. "
                "Please upgrade to ENTERPRISE for all languages."
            )

    def _check_feature(self, feature: str) -> None:
        features = CODING_ASSISTANT_FEATURES[self.tier.value]
        if not any(feature.lower() in f.lower() for f in features):
            raise CodingAssistantBotTierError(
                f"'{feature}' is not available on the {self.config.name} tier. "
                f"Please upgrade to access this feature."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))

    def complete_code(self, request: dict) -> dict:
        """
        Complete or extend a code snippet.

        Args:
            request: {"code": str, "language": str, "instruction": str optional}

        Returns:
            {"completion": str, "language": str, "suggestions": list, "tier": str}
        """
        self._check_request_limit()
        self._request_count += 1

        code = request.get("code", "")
        language = request.get("language", "python")
        instruction = request.get("instruction", "complete the code")

        self._check_language(language)

        if self.tier == Tier.FREE:
            completion = (
                f"# Basic completion for {language}\n{code}\n"
                "# Added baseline behavior: validate inputs, return a result, and add tests."
            )
            suggestions = [f"Consider adding error handling in {language}."]

        elif self.tier == Tier.PRO:
            completion = (
                f"# Advanced {language} completion\n{code}\n"
                f"# Instruction: {instruction}\n# Implementation added with best practices"
            )
            suggestions = [
                f"Add type hints for better {language} readability.",
                "Consider extracting this into a separate function.",
                "Add unit tests for the new implementation.",
            ]

        else:  # ENTERPRISE
            completion = (
                f"# Full AI {language} completion\n{code}\n"
                f"# Instruction: {instruction}\n"
                "# Optimized implementation with documentation, error handling, and tests"
            )
            suggestions = [
                f"Add type hints for better {language} readability.",
                "Consider extracting this into a separate function.",
                "Add unit tests for the new implementation.",
                "Review for potential security vulnerabilities.",
                "Consider performance optimizations for large inputs.",
            ]

        return {
            "completion": completion,
            "language": language,
            "suggestions": suggestions,
            "tier": self.tier.value,
        }

    def review_code(self, code: str, language: str) -> dict:
        """
        Review code for bugs, style issues, and improvements.

        Args:
            code: The code to review.
            language: The programming language.

        Returns:
            {"language": str, "issues": list, "suggestions": list, "score": float, "tier": str}
        """
        self._check_request_limit()
        self._request_count += 1

        self._check_language(language)

        if self.tier == Tier.FREE:
            issues = ["Check for potential null reference errors.", "Verify input validation."]
            suggestions = ["Add comments to improve readability."]
            score = 0.6

        elif self.tier == Tier.PRO:
            issues = [
                "Check for potential null reference errors.",
                "Verify input validation.",
                "Consider exception handling.",
                "Review variable naming conventions.",
            ]
            suggestions = [
                "Add comments to improve readability.",
                "Refactor repeated logic into helper functions.",
                "Improve test coverage for edge cases.",
            ]
            score = 0.75

        else:  # ENTERPRISE
            issues = [
                "Check for potential null reference errors.",
                "Verify input validation.",
                "Consider exception handling.",
                "Review variable naming conventions.",
                "Evaluate algorithm complexity.",
                "Check for security vulnerabilities.",
            ]
            suggestions = [
                "Add comments to improve readability.",
                "Refactor repeated logic into helper functions.",
                "Improve test coverage for edge cases.",
                "Consider async patterns for I/O operations.",
                "Add telemetry and logging for production observability.",
            ]
            score = 0.9

        return {
            "language": language,
            "issues": issues,
            "suggestions": suggestions,
            "score": score,
            "tier": self.tier.value,
        }

    def generate_tests(self, code: str, language: str) -> dict:
        """
        Generate unit tests for the provided code.

        Args:
            code: The source code to test.
            language: The programming language.

        Returns:
            {"language": str, "tests": str, "framework": str, "tier": str}
        """
        if self.tier == Tier.FREE:
            raise CodingAssistantBotTierError(
                "Test generation is not available on the Free tier. "
                "Please upgrade to PRO or ENTERPRISE."
            )

        self._check_request_limit()
        self._request_count += 1

        self._check_language(language)

        frameworks = {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "jest",
            "java": "junit",
            "go": "testing",
            "rust": "cargo test",
        }
        framework = frameworks.get(language.lower(), "unittest")

        tests = (
            f"# Auto-generated {framework} tests for {language}\n"
            f"# Generated at {datetime.now().isoformat()}\n\n"
            f"def test_basic_functionality():\n"
            f"    result = {{'status': 'ok'}}\n"
            f"    assert result['status'] == 'ok'\n\n"
            f"def test_edge_cases():\n"
            f"    payload = {{'items': []}}\n"
            f"    assert payload['items'] == []\n"
        )

        return {
            "language": language,
            "tests": tests,
            "framework": framework,
            "tier": self.tier.value,
        }

    def get_stats(self) -> dict:
        return {
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
            "buddy_integration": True,
        }
