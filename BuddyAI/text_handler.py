"""
TextHandler - Text-to-task command parsing for Buddy.

Converts free-form user text into structured intent/parameter pairs
that the TaskEngine can execute.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class ParsedCommand:
    """Structured representation of a parsed user command.

    Attributes:
        intent: Detected intent label (e.g. ``"schedule_task"``).
        params: Key/value parameters extracted from the command.
        raw_text: Original text provided by the user.
        confidence: Confidence score between 0.0 and 1.0.
    """

    intent: str
    params: Dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""
    confidence: float = 1.0


# ---------------------------------------------------------------------------
# Intent patterns
# ---------------------------------------------------------------------------

# Each entry is (intent_name, compiled_regex, param_extractor_fn | None)
# The extractor receives the re.Match object and returns a dict of params.

def _extract_schedule_params(m: re.Match) -> Dict[str, Any]:
    return {
        "task": (m.group("task") or "").strip(),
        "when": (m.group("when") or "").strip(),
    }


def _extract_reminder_params(m: re.Match) -> Dict[str, Any]:
    return {
        "message": (m.group("message") or "").strip(),
        "when": (m.group("when") or "").strip(),
    }


def _extract_search_params(m: re.Match) -> Dict[str, Any]:
    return {"query": (m.group("query") or "").strip()}


def _extract_add_todo_params(m: re.Match) -> Dict[str, Any]:
    return {"item": (m.group("item") or "").strip()}


def _extract_list_todos_params(m: re.Match) -> Dict[str, Any]:
    return {}


def _extract_complete_todo_params(m: re.Match) -> Dict[str, Any]:
    return {"item": (m.group("item") or "").strip()}


def _extract_fetch_api_params(m: re.Match) -> Dict[str, Any]:
    return {"url": (m.group("url") or "").strip()}


def _extract_install_lib_params(m: re.Match) -> Dict[str, Any]:
    return {"package": (m.group("package") or "").strip()}


def _extract_benchmark_params(m: re.Match) -> Dict[str, Any]:
    return {"target": (m.group("target") or "").strip()}


def _extract_help_params(m: re.Match) -> Dict[str, Any]:
    return {}


_INTENT_PATTERNS: List[Tuple[str, re.Pattern, Any]] = [
    (
        "schedule_task",
        re.compile(
            r"(?:schedule|set up|plan)\s+(?P<task>.+?)\s+(?:at|on|for)\s+(?P<when>.+)",
            re.IGNORECASE,
        ),
        _extract_schedule_params,
    ),
    (
        "set_reminder",
        re.compile(
            r"(?:remind me(?: to)?|set a reminder(?: to)?)\s+(?P<message>.+?)"
            r"(?:\s+(?:at|on|by|in)\s+(?P<when>.+))?$",
            re.IGNORECASE,
        ),
        _extract_reminder_params,
    ),
    (
        "add_todo",
        re.compile(
            r"\b(?:add|create|new)\b\s+(?:task|todo|item|note)?\s*(?P<item>.+)",
            re.IGNORECASE,
        ),
        _extract_add_todo_params,
    ),
    (
        "list_todos",
        re.compile(
            r"\b(?:list|show|display)\b\s+(?:my\s+)?(?:tasks|todos|items|notes)",
            re.IGNORECASE,
        ),
        _extract_list_todos_params,
    ),
    (
        "complete_todo",
        re.compile(
            r"\b(?:complete|done|finish|mark(?:\s+done)?)\b\s+(?P<item>.+)",
            re.IGNORECASE,
        ),
        _extract_complete_todo_params,
    ),
    (
        "fetch_api",
        re.compile(
            r"(?:fetch|get|call|retrieve)\s+(?:data\s+)?(?:from\s+)?(?P<url>https?://\S+)",
            re.IGNORECASE,
        ),
        _extract_fetch_api_params,
    ),
    (
        "search",
        re.compile(
            r"(?:search|look up|find|google|lookup)\s+(?:for\s+)?(?P<query>.+)",
            re.IGNORECASE,
        ),
        _extract_search_params,
    ),
    (
        "install_library",
        re.compile(
            r"(?:install|download|add)\s+(?:library|package|module|lib)\s+(?P<package>\S+)",
            re.IGNORECASE,
        ),
        _extract_install_lib_params,
    ),
    (
        "benchmark",
        re.compile(
            r"(?:benchmark|test performance of|profile)\s+(?P<target>.+)",
            re.IGNORECASE,
        ),
        _extract_benchmark_params,
    ),
    (
        "help",
        re.compile(r"(?:help|what can you do|commands|usage)", re.IGNORECASE),
        _extract_help_params,
    ),
]


# ---------------------------------------------------------------------------
# TextHandler class
# ---------------------------------------------------------------------------


class TextHandler:
    """Parse free-form text commands into :class:`ParsedCommand` objects.

    Usage::

        handler = TextHandler()
        cmd = handler.parse("Add todo buy groceries")
        # ParsedCommand(intent='add_todo', params={'item': 'buy groceries'}, ...)
    """

    def parse(self, text: str) -> ParsedCommand:
        """Parse *text* and return the best-matching :class:`ParsedCommand`.

        Falls back to an ``"unknown"`` intent when no pattern matches.

        Args:
            text: Raw user input string.

        Returns:
            A :class:`ParsedCommand` with the detected intent and parameters.
        """
        cleaned = text.strip()
        if not cleaned:
            return ParsedCommand(intent="unknown", raw_text=text, confidence=0.0)

        for intent, pattern, extractor in _INTENT_PATTERNS:
            match = pattern.search(cleaned)
            if match:
                params = extractor(match) if extractor else {}
                logger.debug("Matched intent '%s' from text: %r", intent, cleaned)
                return ParsedCommand(
                    intent=intent,
                    params=params,
                    raw_text=text,
                    confidence=1.0,
                )

        logger.debug("No intent matched for text: %r", cleaned)
        return ParsedCommand(
            intent="unknown",
            params={"raw": cleaned},
            raw_text=text,
            confidence=0.0,
        )

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities (time expressions, URLs, etc.) from *text*.

        Args:
            text: Raw user input string.

        Returns:
            Dictionary with entity keys like ``"time"``, ``"url"``, ``"date"``.
        """
        entities: Dict[str, Any] = {}

        # Time expressions: "3pm", "15:30", "noon", "midnight"
        time_match = re.search(
            r"\b(\d{1,2}(?::\d{2})?\s*(?:am|pm)|noon|midnight)\b",
            text,
            re.IGNORECASE,
        )
        if time_match:
            entities["time"] = time_match.group(0)

        # Dates: "tomorrow", "Monday", "2024-01-15"
        date_match = re.search(
            r"\b(today|tomorrow|yesterday|monday|tuesday|wednesday|thursday|"
            r"friday|saturday|sunday|\d{4}-\d{2}-\d{2})\b",
            text,
            re.IGNORECASE,
        )
        if date_match:
            entities["date"] = date_match.group(0)

        # URLs
        url_match = re.search(r"https?://\S+", text)
        if url_match:
            entities["url"] = url_match.group(0)

        return entities
