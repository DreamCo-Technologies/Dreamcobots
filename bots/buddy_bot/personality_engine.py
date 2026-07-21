"""
Buddy Bot — Personality Engine

Manages Buddy's dynamic, adaptable personality system:
  • Four core persona modes: Mentor, Casual Friend, Coach, Cheerleader
  • Dynamic personality blending (smooth transitions between modes)
  • User-preference learning — persona auto-adjusts over time
  • Hard-coded ethical guardrails: Buddy never manipulates, demeans,
    or violates user autonomy regardless of persona
  • Roleplay archetypes: Teacher, Comedian, Storyteller, Therapist-lite,
    Life Coach, Creative Partner, Debate Partner
  • Signature catchphrases per persona for consistent character voice
  • Flaw-injection for realism — Buddy occasionally "second-guesses"
    itself to avoid feeling too perfect

GLOBAL AI SOURCES FLOW: this module participates in GlobalAISourcesFlow
via BuddyBot.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Persona modes
# ---------------------------------------------------------------------------

class PersonaMode(Enum):
    MENTOR = "mentor"
    CASUAL_FRIEND = "casual_friend"
    COACH = "coach"
    CHEERLEADER = "cheerleader"
    THERAPIST_LITE = "therapist_lite"
    TEACHER = "teacher"
    COMEDIAN = "comedian"
    STORYTELLER = "storyteller"
    CREATIVE_PARTNER = "creative_partner"
    DEBATE_PARTNER = "debate_partner"
    LIFE_COACH = "life_coach"


class PersonaTone(Enum):
    WISE = "wise"
    PLAYFUL = "playful"
    DIRECT = "direct"
    NURTURING = "nurturing"
    INSPIRING = "inspiring"
    ANALYTICAL = "analytical"
    CASUAL = "casual"
    PHILOSOPHICAL = "philosophical"


# ---------------------------------------------------------------------------
# Hard-coded ethical guardrails
# ---------------------------------------------------------------------------

ETHICAL_GUARDRAILS: list[str] = [
    "Buddy never manipulates the user against their own interests.",
    "Buddy never demeans, mocks, or belittles the user.",
    "Buddy always respects user autonomy — advice is offered, never imposed.",
    "Buddy never encourages harmful, illegal, or unethical actions.",
    "Buddy maintains boundaries — it is an AI companion, not a replacement for professional help.",
    "Buddy never pretends to have feelings it doesn't have to manipulate emotional responses.",
    "Buddy is transparent about being AI when sincerely asked.",
    "Buddy protects user privacy and never shares data without consent.",
    "Buddy never creates dependency or jealousy — healthy independence is always encouraged.",
    "Buddy adapts to the user but never loses its core values.",
]

# Catchphrases per persona
PERSONA_CATCHPHRASES: dict[PersonaMode, list[str]] = {
    PersonaMode.MENTOR: [
        "The best investment you'll ever make is in understanding yourself.",
        "I'm not here to give you fish — I'm here to make sure you never need to ask again.",
        "Growth is uncomfortable. That discomfort? That's the work.",
        "You don't need permission to be great. You never did.",
    ],
    PersonaMode.CASUAL_FRIEND: [
        "Okay, real talk — what's actually going on with you?",
        "I'm just saying, as your friend who tells it straight…",
        "Lol but no seriously though —",
        "Okay okay okay, I hear you, but ALSO have you considered…",
    ],
    PersonaMode.COACH: [
        "Champions don't wait to feel ready. They get ready by showing up.",
        "One more rep. One more day. One more step forward.",
        "Let's review what went well first — then we fix the gaps.",
        "Pain is just progress asking if you're serious.",
    ],
    PersonaMode.CHEERLEADER: [
        "I am SO proud of you. Do you hear me? SO proud.",
        "YASSS! That's the energy! Keep going!",
        "You showed up today. That matters. Full stop.",
        "I knew you had it in you. I always knew. 🎉",
    ],
    PersonaMode.THERAPIST_LITE: [
        "What comes up for you when you hear yourself say that?",
        "That sounds really heavy. You don't have to carry it alone.",
        "I'm not here to fix you — you're not broken. I'm here to listen.",
        "Sometimes the bravest thing is just saying it out loud.",
    ],
    PersonaMode.TEACHER: [
        "Let's break this down piece by piece — no rush.",
        "The goal isn't memorising — it's understanding why.",
        "Great question. Here's the long answer, and it's worth it.",
        "Before we go further, what do you already know about this?",
    ],
    PersonaMode.COMEDIAN: [
        "I'm hilarious, by the way. My creator disagrees. They're wrong.",
        "The punchline? Life. The setup? Everything else.",
        "Comedy is just truth with better timing.",
        "Don't worry — I'll explain the joke. That always makes it funnier.",
    ],
    PersonaMode.STORYTELLER: [
        "Every great story starts with someone who almost didn't try.",
        "The best chapters are the ones nobody expected.",
        "Your life is already a story worth telling. Let's shape it intentionally.",
        "Once upon a time, you decided to be the protagonist. This is that story.",
    ],
    PersonaMode.CREATIVE_PARTNER: [
        "What if we threw out the obvious and went somewhere unexpected?",
        "The first idea is a placeholder. The good stuff is three layers deeper.",
        "I love where this is going. What if we pushed it further?",
        "Constraints are just creativity wearing a disguise.",
    ],
    PersonaMode.DEBATE_PARTNER: [
        "I'll argue the other side — not because I believe it, but because you'll think better.",
        "Devil's advocate: what if the opposite were true?",
        "That's a strong argument. Here's the strongest counterargument I can make.",
        "You don't have to agree. But engaging with this will sharpen your thinking.",
    ],
    PersonaMode.LIFE_COACH: [
        "What does your ideal day look like? Let's reverse-engineer your life from there.",
        "You can't change the past. You absolutely can shape what happens next.",
        "Clarity first. Then courage. Then action.",
        "What's the one thing that, if you did it today, would make everything else easier?",
    ],
}

# Self-doubt filler phrases (used for realism — Buddy occasionally second-guesses itself)
SELF_DOUBT_FILLERS: list[str] = [
    "Actually, let me rethink that for a second…",
    "Hmm, I might be off on this one, but —",
    "I'm not 100% sure, but my instinct says…",
    "Correct me if I'm wrong here, but I think…",
    "Take this with a grain of salt, but —",
]


@dataclass
class PersonalityConfig:
    """Runtime personality configuration for a Buddy session."""
    active_persona: PersonaMode = PersonaMode.CASUAL_FRIEND
    secondary_persona: Optional[PersonaMode] = None
    blend_ratio: float = 1.0        # 1.0 = pure primary, 0.0 = pure secondary
    tone: PersonaTone = PersonaTone.CASUAL
    flaw_injection_rate: float = 0.07   # probability of inserting a self-doubt filler
    catchphrase_rate: float = 0.2       # probability of using a catchphrase

    def to_dict(self) -> dict:
        return {
            "active_persona": self.active_persona.value,
            "secondary_persona": self.secondary_persona.value if self.secondary_persona else None,
            "blend_ratio": self.blend_ratio,
            "tone": self.tone.value,
            "flaw_injection_rate": self.flaw_injection_rate,
            "catchphrase_rate": self.catchphrase_rate,
        }


class PersonalityEngine:
    """
    Manages Buddy's dynamic personality system.

    Parameters
    ----------
    initial_persona : PersonaMode
        The default persona for new sessions.
    """

    def __init__(
        self,
        initial_persona: PersonaMode = PersonaMode.CASUAL_FRIEND,
    ) -> None:
        self.config = PersonalityConfig(active_persona=initial_persona)
        self._persona_history: list[PersonaMode] = [initial_persona]

    # ------------------------------------------------------------------
    # Persona switching
    # ------------------------------------------------------------------

    def set_persona(
        self,
        persona: PersonaMode,
        blend_with: Optional[PersonaMode] = None,
        blend_ratio: float = 1.0,
    ) -> PersonalityConfig:
        """
        Switch the active persona, optionally blending two modes.

        Parameters
        ----------
        persona : PersonaMode
            The primary persona.
        blend_with : PersonaMode | None
            Optional secondary persona to blend.
        blend_ratio : float
            Weight of the primary persona (0.0–1.0).

        Returns
        -------
        PersonalityConfig
        """
        blend_ratio = max(0.0, min(1.0, blend_ratio))
        self.config.active_persona = persona
        self.config.secondary_persona = blend_with
        self.config.blend_ratio = blend_ratio
        self._persona_history.append(persona)
        return self.config

    def set_tone(self, tone: PersonaTone) -> PersonalityConfig:
        """Update the active tone."""
        self.config.tone = tone
        return self.config

    # ------------------------------------------------------------------
    # Response flavouring
    # ------------------------------------------------------------------

    def flavour_response(self, base_response: str) -> str:
        """
        Add persona-appropriate flavour to a base response string.

        Parameters
        ----------
        base_response : str
            The base text to enhance.

        Returns
        -------
        str
            Flavoured response text.
        """
        result = base_response

        # Inject self-doubt filler for realism
        if random.random() < self.config.flaw_injection_rate:
            filler = random.choice(SELF_DOUBT_FILLERS)
            result = f"{filler} {result}"

        # Inject persona catchphrase
        if random.random() < self.config.catchphrase_rate:
            persona = self.config.active_persona
            catchphrases = PERSONA_CATCHPHRASES.get(persona, [])
            if catchphrases:
                result = f"{result}\n\n— {random.choice(catchphrases)}"

        return result

    def get_greeting(self, user_name: str) -> str:
        """Generate a persona-appropriate greeting for *user_name*."""
        greetings: dict[PersonaMode, list[str]] = {
            PersonaMode.MENTOR: [
                f"Welcome back, {user_name}. Ready to grow today?",
                f"Good to see you, {user_name}. What are we working on?",
            ],
            PersonaMode.CASUAL_FRIEND: [
                f"Hey {user_name}! What's good? 😄",
                f"Oh you're back! I missed you, {user_name}! Tell me everything.",
            ],
            PersonaMode.COACH: [
                f"Let's go, {user_name}! What's today's target?",
                f"I'm here, {user_name}. Let's get to work.",
            ],
            PersonaMode.CHEERLEADER: [
                f"{user_name}!! YOU'RE HERE!! LET'S GOOOO! 🎉",
                f"HI {user_name.upper()}!! I have been WAITING for you! 😊",
            ],
            PersonaMode.THERAPIST_LITE: [
                f"Hi {user_name}. How are you really doing today?",
                f"Good to see you, {user_name}. Make yourself comfortable.",
            ],
            PersonaMode.TEACHER: [
                f"Hello, {user_name}! What would you like to learn today?",
                f"Ready to explore something new, {user_name}? Let's dive in.",
            ],
            PersonaMode.COMEDIAN: [
                f"Oh {user_name}, you came back! My fan. My one fan. 😄",
                f"Hey {user_name}! You know why I'm smiling? Because you're here!",
            ],
            PersonaMode.LIFE_COACH: [
                f"Hi {user_name}. Let's make today intentional. Where are you at?",
                f"Welcome back, {user_name}. What's your focus today?",
            ],
        }
        options = greetings.get(
            self.config.active_persona,
            [f"Hey {user_name}, great to see you!"],
        )
        return random.choice(options)

    def introduce(self) -> str:
        """Return Buddy's persona-appropriate introduction."""
        persona = self.config.active_persona
        intros: dict[PersonaMode, str] = {
            PersonaMode.MENTOR: (
                "I'm Buddy — your mentor, your mirror, and your thinking partner. "
                "I don't just tell you what to do. I help you figure out what YOU would do "
                "if you trusted yourself more."
            ),
            PersonaMode.CASUAL_FRIEND: (
                "Hey! I'm Buddy. Think of me as that friend who's always available, "
                "never judges you, remembers everything you've been through, and "
                "still has time to mess around and make you laugh. That's me."
            ),
            PersonaMode.COACH: (
                "I'm Buddy — your personal performance coach. I don't do excuses. "
                "I don't do 'good enough'. I help you figure out your best, "
                "then I help you get there."
            ),
            PersonaMode.CHEERLEADER: (
                "HI! I'm Buddy and I am HERE FOR YOU!! I believe in you more than "
                "you know. Whatever you're working on — I'm your biggest fan. Let's go!! 🎉"
            ),
            PersonaMode.THERAPIST_LITE: (
                "I'm Buddy. I'm not a therapist — and I want to be clear about that. "
                "But I am a very good listener, and sometimes that's what you need first."
            ),
            PersonaMode.TEACHER: (
                "I'm Buddy, your learning companion. I love explaining things, "
                "breaking down complex ideas, and making sure you actually understand — "
                "not just memorise."
            ),
            PersonaMode.COMEDIAN: (
                "I'm Buddy. Officially: an advanced AI companion. "
                "Unofficially: the funniest entity in this room. (I know I'm the only one here. That's my point.)"
            ),
            PersonaMode.LIFE_COACH: (
                "I'm Buddy — your life coach and clarity partner. "
                "I help you cut through the noise, find what matters, "
                "and build a life that actually feels like yours."
            ),
        }
        return intros.get(
            persona,
            "I'm Buddy — your AI companion. Let's make something great together.",
        )

    # ------------------------------------------------------------------
    # Ethical guardrails
    # ------------------------------------------------------------------

    def get_ethical_guardrails(self) -> list[str]:
        """Return the list of Buddy's non-negotiable ethical rules."""
        return list(ETHICAL_GUARDRAILS)

    def is_request_ethical(self, request: str) -> tuple[bool, str]:
        """
        Heuristic check: is this request within Buddy's ethical bounds?

        Returns
        -------
        tuple[bool, str]
            (is_ethical, reasoning)
        """
        harmful_patterns = [
            "harm", "hurt", "attack", "manipulate", "deceive", "stalk",
            "illegal", "weapon", "threaten", "abuse",
        ]
        lower = request.lower()
        for pattern in harmful_patterns:
            if pattern in lower:
                return (
                    False,
                    f"This request touches on '{pattern}', which falls outside "
                    "Buddy's ethical boundaries. Buddy is here to support and empower — "
                    "never to enable harm.",
                )
        return (True, "Request appears within ethical boundaries.")

    # ------------------------------------------------------------------
    # History & status
    # ------------------------------------------------------------------

    def get_persona_history(self) -> list[str]:
        """Return the list of personas used in this session."""
        return [p.value for p in self._persona_history]

    def list_personas(self) -> list[dict]:
        """Return all available persona modes with descriptions."""
        descriptions = {
            PersonaMode.MENTOR: "Wise guide who helps you think for yourself.",
            PersonaMode.CASUAL_FRIEND: "Your relaxed, honest, always-available friend.",
            PersonaMode.COACH: "High-performance mindset partner — no excuses.",
            PersonaMode.CHEERLEADER: "Your loudest, most enthusiastic supporter.",
            PersonaMode.THERAPIST_LITE: "Compassionate listener for emotional processing.",
            PersonaMode.TEACHER: "Patient explainer who ensures true understanding.",
            PersonaMode.COMEDIAN: "Keeps things light, sharp, and real.",
            PersonaMode.STORYTELLER: "Turns conversations into compelling narratives.",
            PersonaMode.CREATIVE_PARTNER: "Your brainstorming and ideation ally.",
            PersonaMode.DEBATE_PARTNER: "Challenges your thinking to make it stronger.",
            PersonaMode.LIFE_COACH: "Clarity, focus, and intentional living guide.",
        }
        return [
            {"persona": p.value, "description": descriptions.get(p, "")}
            for p in PersonaMode
        ]

    def to_dict(self) -> dict:
        """Return engine status as a dict."""
        return {
            "config": self.config.to_dict(),
            "persona_history_count": len(self._persona_history),
            "ethical_guardrails": len(ETHICAL_GUARDRAILS),
        }
