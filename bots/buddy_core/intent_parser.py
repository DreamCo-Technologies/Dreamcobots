"""
Intent Parser for the Buddy Core System.

Detects user intent and industry from natural-language text using
keyword-based matching.  No external NLP dependencies required.

Part of the Buddy Core System — adheres to the GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class IntentParserError(Exception):
    """Raised when intent parsing fails."""


class IntentType(Enum):
    CREATE_BOT = "create_bot"
    FIND_LEADS = "find_leads"
    RUN_WORKFLOW = "run_workflow"
    ANALYZE_DATA = "analyze_data"
    MANAGE_TOOLS = "manage_tools"
    GET_STATUS = "get_status"
    UNKNOWN = "unknown"


class Industry(Enum):
    REAL_ESTATE = "real_estate"
    FINANCE = "finance"
    FREELANCE = "freelance"
    MARKETING = "marketing"
    HEALTH = "health"
    LOGISTICS = "logistics"
    GENERAL = "general"


@dataclass
class ParsedIntent:
    """Result of parsing a user message."""

    intent_type: IntentType
    industry: Industry
    bot_name: str
    raw_text: str
    confidence: float
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Keyword maps
# ---------------------------------------------------------------------------

_INTENT_KEYWORDS: dict[IntentType, list[str]] = {
    IntentType.CREATE_BOT: [
        "create bot", "build bot", "make bot", "generate bot",
        "new bot", "create a bot", "build a bot", "make a bot",
        "create agent", "build agent", "launch bot", "spin up",
    ],
    IntentType.FIND_LEADS: [
        "find leads", "get leads", "scrape leads", "lead generation",
        "prospects", "find prospects", "gather leads", "collect leads",
        "lead campaign", "run campaign", "fetch leads",
    ],
    IntentType.RUN_WORKFLOW: [
        "run workflow", "execute workflow", "start workflow",
        "trigger workflow", "automate", "automation", "run process",
        "execute task", "schedule task",
    ],
    IntentType.ANALYZE_DATA: [
        "analyze data", "analyse data", "data analysis", "show stats",
        "performance stats", "metrics", "report", "insights",
        "dashboard", "summarize",
    ],
    IntentType.MANAGE_TOOLS: [
        "manage tools", "list tools", "inject tools", "add tool",
        "remove tool", "tool db", "available tools", "show tools",
        "configure tool",
    ],
    IntentType.GET_STATUS: [
        "status", "health check", "system status", "how is",
        "what is running", "active bots", "running bots", "check status",
        "get status", "overview",
    ],
}

_INDUSTRY_KEYWORDS: dict[Industry, list[str]] = {
    Industry.REAL_ESTATE: [
        "real estate", "property", "house", "home", "zillow",
        "trulia", "mortgage", "realty", "listing", "mls",
    ],
    Industry.FINANCE: [
        "finance", "financial", "stock", "crypto", "investment",
        "banking", "trading", "portfolio", "plaid", "payment",
    ],
    Industry.FREELANCE: [
        "freelance", "fiverr", "upwork", "gig", "contractor",
        "consultant", "freelancer", "project", "client work",
    ],
    Industry.MARKETING: [
        "marketing", "campaign", "ad", "email marketing", "mailchimp",
        "seo", "social media", "content", "brand", "influencer",
    ],
    Industry.HEALTH: [
        "health", "medical", "healthcare", "hospital", "clinic",
        "doctor", "patient", "wellness", "pharmacy", "telemedicine",
    ],
    Industry.LOGISTICS: [
        "logistics", "shipping", "delivery", "supply chain",
        "warehouse", "transport", "freight", "cargo", "tracking",
    ],
}


class IntentParser:
    """Keyword-based intent and industry detector."""

    def parse(self, text: str) -> ParsedIntent:
        """Parse *text* and return a ParsedIntent."""
        if not text or not isinstance(text, str):
            raise IntentParserError("text must be a non-empty string")

        lower = text.lower()
        intent = self._detect_intent(lower)
        industry = self.get_industry(lower)
        confidence = self.get_confidence(lower, intent)
        bot_name = self._extract_bot_name(lower)

        return ParsedIntent(
            intent_type=intent,
            industry=industry,
            bot_name=bot_name,
            raw_text=text,
            confidence=confidence,
            metadata={"lower": lower},
        )

    def _detect_intent(self, lower: str) -> IntentType:
        scores: dict[IntentType, int] = {i: 0 for i in IntentType}
        for intent, keywords in _INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in lower:
                    scores[intent] += len(kw.split())
        best = max(scores, key=lambda i: scores[i])
        if scores[best] == 0:
            return IntentType.UNKNOWN
        return best

    def get_industry(self, text: str) -> Industry:
        """Detect industry from text."""
        lower = text.lower()
        scores: dict[Industry, int] = {i: 0 for i in Industry}
        for industry, keywords in _INDUSTRY_KEYWORDS.items():
            for kw in keywords:
                if kw in lower:
                    scores[industry] += 1
        best = max(scores, key=lambda i: scores[i])
        if scores[best] == 0:
            return Industry.GENERAL
        return best

    def get_confidence(self, text: str, intent: IntentType) -> float:
        """Return a 0.0–1.0 confidence score for the detected intent."""
        if intent == IntentType.UNKNOWN:
            return 0.0
        lower = text.lower()
        keywords = _INTENT_KEYWORDS.get(intent, [])
        matches = sum(1 for kw in keywords if kw in lower)
        total_words = max(len(lower.split()), 1)
        raw = matches / max(len(keywords), 1)
        # Penalise very short or very long inputs slightly
        length_factor = min(total_words / 5, 1.0)
        score = 0.5 * raw + 0.5 * min(matches / 2, 1.0)
        score = score * (0.7 + 0.3 * length_factor)
        return round(min(score, 1.0), 4)

    def _extract_bot_name(self, lower: str) -> str:
        """Attempt to extract a bot name from common patterns like 'create a <name> bot'."""
        import re
        patterns = [
            r"(?:create|build|make|generate|launch)\s+(?:a\s+)?(\w+)\s+bot",
            r"bot\s+(?:called|named)\s+(\w+)",
            r"new\s+(\w+)\s+bot",
        ]
        for pattern in patterns:
            m = re.search(pattern, lower)
            if m:
                candidate = m.group(1)
                if candidate not in {"a", "an", "the", "my", "new"}:
                    return candidate.capitalize() + "Bot"
        return ""
