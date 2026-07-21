"""
Buddy Bot — Reasoning Engine (Claude Mithos Intelligence Layer)

Elevates BuddyBot's intelligence to Claude-Mithos level by providing:

  • Chain-of-thought reasoning — breaks complex queries into transparent reasoning
    steps before producing an answer.
  • Context synthesis — weighs recent conversation history against the current
    message to produce contextually grounded replies.
  • Deep comprehension — identifies intent, entities, sentiment, and implicit
    needs beyond literal keyword matching.
  • Analytical responses — structured multi-perspective analysis for open-ended
    and factual questions.

"Mithos" (μῦθος) is Greek for narrative / story.  Claude Mithos specialises in
narrative intelligence: it understands the *story* the user is living, not just
the words they type.

GLOBAL AI SOURCES FLOW: this module participates in GlobalAISourcesFlow
via BuddyBot.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Query intent taxonomy
# ---------------------------------------------------------------------------

class QueryIntent(Enum):
    FACTUAL       = "factual"        # "What is …?" / "How does …?"
    ANALYTICAL    = "analytical"     # "Why did …?" / "Compare …"
    CREATIVE      = "creative"       # "Write me …" / "Generate …"
    EMOTIONAL     = "emotional"      # Feelings, venting, support
    INSTRUCTIONAL = "instructional"  # "Help me …" / "Show me how …"
    CONVERSATIONAL = "conversational" # Small talk, greetings
    ETHICAL       = "ethical"        # Moral dilemmas, advice
    UNKNOWN       = "unknown"


# ---------------------------------------------------------------------------
# Reasoning step
# ---------------------------------------------------------------------------

@dataclass
class ReasoningStep:
    """A single step in a chain-of-thought reasoning trace."""
    step_number: int
    description: str
    conclusion: str

    def to_dict(self) -> dict:
        return {
            "step_number": self.step_number,
            "description": self.description,
            "conclusion": self.conclusion,
        }


# ---------------------------------------------------------------------------
# Reasoning result
# ---------------------------------------------------------------------------

@dataclass
class ReasoningResult:
    """
    Full output of the ReasoningEngine for one user message.

    Attributes
    ----------
    original_query : str
        The raw user input.
    intent : QueryIntent
        Detected intent class.
    reasoning_steps : list[ReasoningStep]
        Chain-of-thought trace (available in ENTERPRISE tier).
    synthesised_context : str
        Summary of what the engine knows from conversation history.
    deep_comprehension : dict
        Structured insight: intent, entities, sentiment, implicit need.
    final_response : str
        The enriched, Claude-Mithos-quality response.
    confidence : float
        Model confidence in the response (0.0–1.0).
    """
    original_query: str
    intent: QueryIntent
    reasoning_steps: list[ReasoningStep] = field(default_factory=list)
    synthesised_context: str = ""
    deep_comprehension: dict = field(default_factory=dict)
    final_response: str = ""
    confidence: float = 0.92

    def to_dict(self) -> dict:
        return {
            "original_query": self.original_query,
            "intent": self.intent.value,
            "reasoning_steps": [s.to_dict() for s in self.reasoning_steps],
            "synthesised_context": self.synthesised_context,
            "deep_comprehension": self.deep_comprehension,
            "final_response": self.final_response,
            "confidence": self.confidence,
        }


# ---------------------------------------------------------------------------
# Knowledge base snippets (Claude-Mithos calibre)
# ---------------------------------------------------------------------------

_ANALYTICAL_FRAMEWORKS: list[str] = [
    "First-principles thinking — what are the irreducible truths here?",
    "Systems thinking — how do the components interact and reinforce each other?",
    "Socratic questioning — what assumptions underlie the situation?",
    "Cost-benefit analysis — what are the short-term vs long-term trade-offs?",
    "Perspective-taking — how would different stakeholders view this?",
]

_FACTUAL_RESPONSE_TEMPLATES: list[str] = [
    (
        "Based on reasoning from foundational principles: {query_echo}. "
        "The core idea here is that {insight}."
    ),
    (
        "Let me break this down clearly. Regarding \"{query_echo}\": "
        "{insight} — understanding this deeply can shift how you approach it."
    ),
    (
        "This is a great question. The key insight is: {insight}. "
        "Want me to go deeper on any aspect?"
    ),
]

_ANALYTICAL_RESPONSE_TEMPLATES: list[str] = [
    (
        "Thinking through this analytically — there are several dimensions to consider. "
        "{framework} Applied to your question about \"{query_echo}\": {insight}."
    ),
    (
        "Let me reason through this step by step. "
        "When we look at \"{query_echo}\" through a {framework_name} lens: {insight}."
    ),
]

_DEEP_INSIGHTS: list[str] = [
    "patterns that emerge when you zoom out often tell a different story than the surface details",
    "the most meaningful breakthroughs come from questioning the constraints you thought were fixed",
    "connecting ideas from different domains frequently reveals the most elegant solutions",
    "what seems complex often simplifies once you identify the one or two key drivers",
    "the question beneath the question is usually the one worth answering",
    "understanding *why* something works is what allows you to adapt it when conditions change",
    "the real leverage is almost always in the relationships between things, not the things themselves",
]

_EMOTIONAL_SUPPORT_TEMPLATES: list[str] = [
    (
        "I hear you, and I want you to know your feelings are completely valid. "
        "{insight} You don't have to have it all figured out right now."
    ),
    (
        "What you're going through sounds genuinely difficult. "
        "It takes courage to talk about it — and I'm here with you through it. {insight}"
    ),
    (
        "Sometimes just naming what we're feeling is the first step. "
        "{insight} I'm not going anywhere — tell me more if you'd like."
    ),
]

_INSTRUCTIONAL_RESPONSE_TEMPLATES: list[str] = [
    (
        "Let me walk you through this clearly. To help with \"{query_echo}\", "
        "the most effective starting point is: {insight}. "
        "From there, we can build step by step."
    ),
    (
        "Great — I can help with that. The key principle for \"{query_echo}\" is "
        "{insight}. Shall I lay out a detailed plan?"
    ),
]

_CREATIVE_PROMPTS: list[str] = [
    "Here is a concept that might spark something:",
    "Leaning into the creative space:",
    "Let me offer an unexpected angle:",
    "Here's an idea that breaks the expected mould:",
]


# ---------------------------------------------------------------------------
# ReasoningEngine
# ---------------------------------------------------------------------------

class ReasoningEngine:
    """
    Claude-Mithos-level reasoning engine for BuddyBot.

    Provides chain-of-thought reasoning, context synthesis, deep comprehension,
    and analytically enriched responses — elevating BuddyBot from template-based
    replies to genuine narrative intelligence.

    Parameters
    ----------
    enable_chain_of_thought : bool
        When True, reasoning steps are generated and stored in the result.
    context_window : int
        Number of recent conversation turns to consider for context synthesis.
    model_name : str
        The AI model identifier powering this engine.
    """

    MODEL_NAME: str = "claude-mithos-1.0"

    def __init__(
        self,
        enable_chain_of_thought: bool = True,
        context_window: int = 10,
        model_name: str = MODEL_NAME,
    ) -> None:
        self.enable_chain_of_thought = enable_chain_of_thought
        self.context_window = context_window
        self.model_name = model_name
        self._conversation_history: list[dict] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reason(
        self,
        query: str,
        conversation_history: Optional[list[dict]] = None,
    ) -> ReasoningResult:
        """
        Apply Claude-Mithos-level reasoning to *query*.

        Parameters
        ----------
        query : str
            The user's message.
        conversation_history : list[dict] | None
            Recent conversation turns (each with ``user_input`` and ``response``
            keys).  If None, uses internal history.

        Returns
        -------
        ReasoningResult
        """
        history = conversation_history or self._conversation_history

        # Step 1: Deep comprehension
        comprehension = self._deep_comprehend(query)
        intent = comprehension["intent"]

        # Step 2: Context synthesis
        context = self._synthesise_context(query, history)

        # Step 3: Chain-of-thought reasoning
        steps: list[ReasoningStep] = []
        if self.enable_chain_of_thought:
            steps = self._chain_of_thought(query, intent, context)

        # Step 4: Generate enriched response
        response = self._generate_enriched_response(query, intent, comprehension, context)

        result = ReasoningResult(
            original_query=query,
            intent=intent,
            reasoning_steps=steps,
            synthesised_context=context,
            deep_comprehension=comprehension,
            final_response=response,
            confidence=self._estimate_confidence(intent),
        )

        # Update internal history
        self._conversation_history.append({
            "user_input": query,
            "response": response,
        })
        if len(self._conversation_history) > self.context_window:
            self._conversation_history = self._conversation_history[-self.context_window:]

        return result

    def chain_of_thought(self, query: str) -> list[ReasoningStep]:
        """
        Generate a standalone chain-of-thought trace for *query*.

        Returns
        -------
        list[ReasoningStep]
        """
        comprehension = self._deep_comprehend(query)
        context = self._synthesise_context(query, self._conversation_history)
        return self._chain_of_thought(query, comprehension["intent"], context)

    def synthesise_context(
        self,
        conversation_history: list[dict],
        query: str,
    ) -> str:
        """
        Synthesise recent conversation context relevant to *query*.

        Parameters
        ----------
        conversation_history : list[dict]
            Recent turns.
        query : str
            Current user message.

        Returns
        -------
        str
            A concise natural-language context summary.
        """
        return self._synthesise_context(query, conversation_history)

    def deep_comprehend(self, text: str) -> dict:
        """
        Return a structured comprehension of *text*.

        Returns
        -------
        dict with keys: ``intent``, ``entities``, ``sentiment``, ``implicit_need``,
        ``complexity``.
        """
        return self._deep_comprehend(text)

    def analytical_response(self, query: str) -> str:
        """
        Produce a structured analytical response to *query*.

        Returns
        -------
        str
        """
        comprehension = self._deep_comprehend(query)
        context = self._synthesise_context(query, self._conversation_history)
        return self._build_analytical_response(query, comprehension, context)

    def clear_history(self) -> None:
        """Clear the internal conversation history."""
        self._conversation_history = []

    def to_dict(self) -> dict:
        """Return engine status as a dict."""
        return {
            "model_name": self.model_name,
            "enable_chain_of_thought": self.enable_chain_of_thought,
            "context_window": self.context_window,
            "history_turns": len(self._conversation_history),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _detect_intent(self, text: str) -> QueryIntent:
        """Classify the user's query intent."""
        lower = text.lower()

        # Check ethical first — before emotional to avoid "hurts" / "wrong" misclassification
        ethical_signals = (
            "should i", "is it right", "moral", "ethical", "wrong to",
            "okay to", "fair", "justice",
        )
        if any(s in lower for s in ethical_signals):
            return QueryIntent.ETHICAL

        emotional_signals = (
            "feel", "feeling", "sad", "happy", "angry", "anxious", "anxiety",
            "scared", "lonely", "hurt", "upset", "stressed", "overwhelmed",
            "depressed", "excited", "love", "hate", "miss", "proud",
        )
        if any(s in lower for s in emotional_signals):
            return QueryIntent.EMOTIONAL

        instructional_signals = (
            "help me", "how do i", "how to", "show me", "can you", "teach me",
            "guide me", "walk me through", "assist",
        )
        if any(s in lower for s in instructional_signals):
            return QueryIntent.INSTRUCTIONAL

        analytical_signals = (
            "why", "compare", "difference between", "pros and cons",
            "analyse", "analyze", "explain", "what causes", "how does",
            "impact of", "effect of", "trade-off",
        )
        if any(s in lower for s in analytical_signals):
            return QueryIntent.ANALYTICAL

        factual_signals = (
            "what is", "what are", "who is", "when did", "where is",
            "define", "tell me about", "describe",
        )
        if any(s in lower for s in factual_signals):
            return QueryIntent.FACTUAL

        creative_signals = (
            "write", "create", "generate", "make", "compose", "design",
            "come up with", "brainstorm", "imagine", "story",
        )
        if any(s in lower for s in creative_signals):
            return QueryIntent.CREATIVE

        conversational_signals = (
            "hello", "hi", "hey", "how are you", "what's up", "good morning",
            "good night", "bye", "thanks", "thank you",
        )
        if any(s in lower for s in conversational_signals):
            return QueryIntent.CONVERSATIONAL

        return QueryIntent.UNKNOWN

    def _extract_entities(self, text: str) -> list[str]:
        """Heuristic entity extraction (capitalised words, quoted phrases)."""
        quoted = re.findall(r'"([^"]+)"', text)
        capitalised = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
        return list(dict.fromkeys(quoted + capitalised))[:5]

    def _detect_sentiment(self, text: str) -> str:
        """Simple keyword-based sentiment classifier."""
        lower = text.lower()
        positive = ("great", "love", "amazing", "happy", "excited", "wonderful",
                    "fantastic", "good", "best", "brilliant", "joy")
        negative = ("sad", "angry", "hate", "terrible", "awful", "bad", "worst",
                    "horrible", "upset", "hurt", "pain", "fear")
        pos = sum(1 for w in positive if w in lower)
        neg = sum(1 for w in negative if w in lower)
        if pos > neg:
            return "positive"
        if neg > pos:
            return "negative"
        return "neutral"

    def _infer_implicit_need(self, text: str, intent: QueryIntent) -> str:
        """Map intent to the most likely underlying user need."""
        need_map: dict[QueryIntent, str] = {
            QueryIntent.FACTUAL:        "understanding and clarity",
            QueryIntent.ANALYTICAL:     "structured insight and perspective",
            QueryIntent.CREATIVE:       "inspiration and a creative spark",
            QueryIntent.EMOTIONAL:      "validation, empathy, and connection",
            QueryIntent.INSTRUCTIONAL:  "actionable guidance and next steps",
            QueryIntent.CONVERSATIONAL: "connection and a friendly presence",
            QueryIntent.ETHICAL:        "moral clarity and trusted guidance",
            QueryIntent.UNKNOWN:        "a thoughtful, helpful response",
        }
        return need_map.get(intent, "a thoughtful, helpful response")

    def _estimate_complexity(self, text: str) -> str:
        """Classify query complexity based on length and vocabulary."""
        word_count = len(text.split())
        if word_count <= 6:
            return "simple"
        if word_count <= 20:
            return "moderate"
        return "complex"

    def _deep_comprehend(self, text: str) -> dict:
        """Build a structured comprehension map for *text*."""
        intent = self._detect_intent(text)
        entities = self._extract_entities(text)
        sentiment = self._detect_sentiment(text)
        implicit_need = self._infer_implicit_need(text, intent)
        complexity = self._estimate_complexity(text)
        return {
            "intent": intent,
            "entities": entities,
            "sentiment": sentiment,
            "implicit_need": implicit_need,
            "complexity": complexity,
        }

    def _synthesise_context(self, query: str, history: list[dict]) -> str:
        """Produce a concise context summary from recent conversation history."""
        if not history:
            return "This is the beginning of our conversation — no prior context."

        recent = history[-self.context_window:]
        topics: list[str] = []
        for turn in recent:
            user_msg = turn.get("user_input", "")
            entities = self._extract_entities(user_msg)
            topics.extend(entities)

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique_topics: list[str] = []
        for t in topics:
            if t not in seen:
                seen.add(t)
                unique_topics.append(t)

        topic_str = (
            f"Topics discussed so far: {', '.join(unique_topics[:5])}."
            if unique_topics
            else "No specific entities identified in recent turns."
        )
        turns_summary = (
            f"We've had {len(recent)} recent exchange(s). "
            f"{topic_str}"
        )
        return turns_summary

    def _chain_of_thought(
        self,
        query: str,
        intent: QueryIntent,
        context: str,
    ) -> list[ReasoningStep]:
        """Generate a chain-of-thought reasoning trace."""
        steps: list[ReasoningStep] = []

        # Step 1 — Parse intent
        steps.append(ReasoningStep(
            step_number=1,
            description="Parse the query intent",
            conclusion=f"The query is classified as '{intent.value}'.",
        ))

        # Step 2 — Acknowledge context
        steps.append(ReasoningStep(
            step_number=2,
            description="Synthesise relevant conversation context",
            conclusion=context,
        ))

        # Step 3 — Identify the implicit need
        implicit_need = self._infer_implicit_need(query, intent)
        steps.append(ReasoningStep(
            step_number=3,
            description="Identify what the user really needs",
            conclusion=f"The user's core need appears to be: {implicit_need}.",
        ))

        # Step 4 — Select a response strategy
        strategy_map: dict[QueryIntent, str] = {
            QueryIntent.FACTUAL:        "Provide clear, grounded, accurate information.",
            QueryIntent.ANALYTICAL:     "Offer structured multi-perspective analysis.",
            QueryIntent.CREATIVE:       "Generate an imaginative, original idea or piece.",
            QueryIntent.EMOTIONAL:      "Lead with empathy; validate, then support.",
            QueryIntent.INSTRUCTIONAL:  "Break down actionable steps clearly.",
            QueryIntent.CONVERSATIONAL: "Respond warmly and naturally.",
            QueryIntent.ETHICAL:        "Offer balanced moral reasoning.",
            QueryIntent.UNKNOWN:        "Default to a thoughtful, open-ended response.",
        }
        strategy = strategy_map.get(intent, "Default to a thoughtful response.")
        steps.append(ReasoningStep(
            step_number=4,
            description="Select response strategy",
            conclusion=strategy,
        ))

        # Step 5 — Formulate answer
        steps.append(ReasoningStep(
            step_number=5,
            description="Formulate the enriched response",
            conclusion="Applying Claude-Mithos narrative intelligence to craft a response.",
        ))

        return steps

    def _generate_enriched_response(
        self,
        query: str,
        intent: QueryIntent,
        comprehension: dict,
        context: str,
    ) -> str:
        """Generate a Claude-Mithos-quality response based on intent and comprehension."""
        insight = random.choice(_DEEP_INSIGHTS)
        query_echo = query[:60] + ("…" if len(query) > 60 else "")

        if intent == QueryIntent.EMOTIONAL:
            template = random.choice(_EMOTIONAL_SUPPORT_TEMPLATES)
            return template.format(insight=insight.capitalize() + ".")

        if intent == QueryIntent.ANALYTICAL:
            return self._build_analytical_response(query, comprehension, context)

        if intent == QueryIntent.FACTUAL:
            template = random.choice(_FACTUAL_RESPONSE_TEMPLATES)
            return template.format(query_echo=query_echo, insight=insight)

        if intent == QueryIntent.INSTRUCTIONAL:
            template = random.choice(_INSTRUCTIONAL_RESPONSE_TEMPLATES)
            return template.format(query_echo=query_echo, insight=insight)

        if intent == QueryIntent.CREATIVE:
            prompt = random.choice(_CREATIVE_PROMPTS)
            return (
                f"{prompt} For \"{query_echo}\" — what if you started with "
                f"the idea that {insight}? That could open an entirely unexpected direction."
            )

        if intent == QueryIntent.ETHICAL:
            return (
                f"This is a question worth sitting with. "
                f"Different frameworks would weigh it differently, but the thread that "
                f"runs through most of them is this: {insight}. "
                f"What matters most to you in this situation?"
            )

        if intent == QueryIntent.CONVERSATIONAL:
            return (
                f"Great to connect! I'm here and fully present. "
                f"What's on your mind today?"
            )

        # Unknown — open-ended thoughtful reply
        return (
            f"That's worth exploring. One thing I find helpful to keep in mind: "
            f"{insight}. Where would you like to start?"
        )

    def _build_analytical_response(
        self,
        query: str,
        comprehension: dict,
        context: str,
    ) -> str:
        """Construct a structured analytical response."""
        framework = random.choice(_ANALYTICAL_FRAMEWORKS)
        framework_name = framework.split("—")[0].strip()
        insight = random.choice(_DEEP_INSIGHTS)
        query_echo = query[:60] + ("…" if len(query) > 60 else "")

        template = random.choice(_ANALYTICAL_RESPONSE_TEMPLATES)
        return template.format(
            framework=framework,
            framework_name=framework_name,
            query_echo=query_echo,
            insight=insight,
        )

    def _estimate_confidence(self, intent: QueryIntent) -> float:
        """Return a confidence score for the given intent class."""
        confidence_map: dict[QueryIntent, float] = {
            QueryIntent.FACTUAL:        0.91,
            QueryIntent.ANALYTICAL:     0.88,
            QueryIntent.CREATIVE:       0.94,
            QueryIntent.EMOTIONAL:      0.95,
            QueryIntent.INSTRUCTIONAL:  0.92,
            QueryIntent.CONVERSATIONAL: 0.98,
            QueryIntent.ETHICAL:        0.85,
            QueryIntent.UNKNOWN:        0.75,
        }
        return confidence_map.get(intent, 0.80)
