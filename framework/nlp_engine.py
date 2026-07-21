"""
nlp_engine.py – Lightweight NLP engine for the DreamCObots framework.

Provides tokenization, sentiment analysis, intent detection, and contextual
understanding using only Python standard-library primitives so that bots run
without mandatory third-party dependencies.  Production deployments can swap
the underlying implementation for a transformer-based model without changing
the public API.
"""

import re
import math
from collections import Counter
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Sentiment lexicons (compact, extensible)
# ---------------------------------------------------------------------------
_POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "wonderful", "fantastic",
    "happy", "love", "like", "best", "awesome", "perfect", "brilliant",
    "positive", "helpful", "outstanding", "superb", "impressive", "glad",
    "excited", "pleased", "enjoy", "nice", "well", "better", "thanks",
    "thank", "appreciate", "splendid", "cheerful", "joyful",
}

_NEGATIVE_WORDS = {
    "bad", "terrible", "awful", "horrible", "hate", "dislike", "worst",
    "poor", "boring", "negative", "useless", "frustrating", "difficult",
    "problem", "issue", "fail", "failed", "error", "wrong", "sad",
    "angry", "disappointed", "confused", "unhappy", "annoyed", "upset",
    "slow", "broken", "worse", "never", "not", "no",
}

# ---------------------------------------------------------------------------
# Intent patterns  {intent_name: [keyword_list]}
# ---------------------------------------------------------------------------
_INTENT_PATTERNS: Dict[str, List[str]] = {
    "job_search":       ["job", "career", "position", "hire", "employment", "work", "vacancy"],
    "resume_help":      ["resume", "cv", "curriculum", "portfolio", "bio"],
    "interview_prep":   ["interview", "prepare", "question", "practice", "mock"],
    "dataset_purchase": ["buy", "purchase", "dataset", "data", "acquire", "get", "download"],
    "dataset_sell":     ["sell", "upload", "distribute", "publish", "monetize"],
    "pricing_inquiry":  ["price", "cost", "fee", "payment", "charge", "rate", "plan"],
    "help":             ["help", "support", "assist", "guide", "how", "what", "explain"],
    "greeting":         ["hello", "hi", "hey", "greetings", "howdy", "good morning", "good afternoon"],
    "farewell":         ["bye", "goodbye", "see you", "later", "exit", "quit"],
    "feedback":         ["feedback", "review", "rating", "opinion", "suggest", "improve"],
    "schedule":         ["schedule", "meeting", "appointment", "calendar", "book", "plan"],
    "invoice":          ["invoice", "bill", "receipt", "payment", "charge", "statement"],
}


class NLPEngine:
    """
    Core NLP component shared by all bots.

    Responsibilities
    ----------------
    * Tokenize and normalise raw text.
    * Detect dominant sentiment (positive / negative / neutral) with score.
    * Identify the most likely user intent from a predefined taxonomy.
    * Maintain a rolling context window for multi-turn understanding.
    """

    def __init__(self, context_window: int = 5):
        self._context: List[str] = []
        self._context_window = context_window
        self._tf_cache: Dict[str, Counter] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(self, text: str) -> Dict:
        """
        Full NLP pipeline.

        Returns a dict with keys:
            tokens, sentiment, sentiment_score, intent, entities, context_summary
        """
        tokens = self._tokenize(text)
        sentiment, score = self._sentiment(tokens)
        intent = self._detect_intent(tokens, text.lower())
        entities = self._extract_entities(text)
        self._update_context(text)

        return {
            "tokens": tokens,
            "sentiment": sentiment,
            "sentiment_score": score,
            "intent": intent,
            "entities": entities,
            "context_summary": self._context_summary(),
        }

    def detect_intent(self, text: str) -> str:
        tokens = self._tokenize(text)
        return self._detect_intent(tokens, text.lower())

    def sentiment(self, text: str) -> Tuple[str, float]:
        return self._sentiment(self._tokenize(text))

    def get_context(self) -> List[str]:
        return list(self._context)

    def clear_context(self) -> None:
        self._context.clear()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        text = text.lower()
        text = re.sub(r"[^\w\s'-]", " ", text)
        return [t for t in text.split() if t]

    def _sentiment(self, tokens: List[str]) -> Tuple[str, float]:
        pos = sum(1 for t in tokens if t in _POSITIVE_WORDS)
        neg = sum(1 for t in tokens if t in _NEGATIVE_WORDS)
        total = max(pos + neg, 1)
        score = (pos - neg) / total          # range [-1, 1]
        if score > 0.1:
            label = "positive"
        elif score < -0.1:
            label = "negative"
        else:
            label = "neutral"
        return label, round(score, 3)

    @staticmethod
    def _detect_intent(tokens: List[str], raw: str) -> str:
        token_set = set(tokens)
        scores: Dict[str, int] = {}
        for intent, keywords in _INTENT_PATTERNS.items():
            hit = sum(
                1 for kw in keywords
                if kw in token_set
                or re.search(r"\b" + re.escape(kw) + r"\b", raw) is not None
            )
            if hit:
                scores[intent] = hit
        if not scores:
            return "general"
        return max(scores, key=lambda k: scores[k])

    @staticmethod
    def _extract_entities(text: str) -> Dict[str, List[str]]:
        """Simple rule-based named-entity extraction."""
        entities: Dict[str, List[str]] = {"emails": [], "urls": [], "numbers": [], "capitalized": []}
        entities["emails"] = re.findall(r"[\w.+-]+@[\w-]+\.\w+", text)
        entities["urls"] = re.findall(r"https?://\S+", text)
        entities["numbers"] = re.findall(r"\b\d+(?:\.\d+)?\b", text)
        entities["capitalized"] = re.findall(r"\b[A-Z][a-z]{2,}\b", text)
        return entities

    def _update_context(self, text: str) -> None:
        self._context.append(text)
        if len(self._context) > self._context_window:
            self._context.pop(0)

    def _context_summary(self) -> str:
        if not self._context:
            return ""
        all_tokens = []
        for t in self._context:
            all_tokens.extend(self._tokenize(t))
        freq = Counter(all_tokens)
        top = [w for w, _ in freq.most_common(5)]
        return "Topics: " + ", ".join(top) if top else ""
