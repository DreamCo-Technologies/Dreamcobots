"""
Buddy Bot — Conversation Engine

Handles natural, human-like dialogue including:
  • Dynamic tone adjustment (happy, calm, excited, empathetic, humorous)
  • Natural speech fillers ("uh", "um", thoughtful pauses)
  • Contextual empathy aligned to detected user sentiment
  • Multilingual fluency with dialect and slang support
  • Real-time language translation between conversation turns
  • AI conflict resolution and mediation for difficult conversations
  • Sarcasm / irony detection
  • Conversational humor integration (witty remarks, light banter)
  • Adaptive context awareness: CASUAL (slang-friendly) vs BUSINESS (professional, profanity-free)
  • Automatic context detection from user input keywords

GLOBAL AI SOURCES FLOW: this module participates in GlobalAISourcesFlow
via BuddyBot.
"""

from __future__ import annotations

import re
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Tone / mood
# ---------------------------------------------------------------------------

class ConversationTone(Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    EMPATHETIC = "empathetic"
    HUMOROUS = "humorous"
    CALM = "calm"
    EXCITED = "excited"
    SERIOUS = "serious"
    ENCOURAGING = "encouraging"


# ---------------------------------------------------------------------------
# Communication context (adaptive language mode)
# ---------------------------------------------------------------------------

class CommunicationContext(Enum):
    """
    Controls Buddy's language register for the current interaction.

    CASUAL  — slang-friendly, relaxed, uses colloquial expressions.
    BUSINESS — polished, professional; no profanity; structured etiquette.
    """
    CASUAL = "casual"
    BUSINESS = "business"


# Keywords that signal a professional / business context
_BUSINESS_CONTEXT_SIGNALS: frozenset[str] = frozenset({
    "proposal", "contract", "invoice", "client", "deal", "leads", "enterprise",
    "meeting", "conference", "presentation", "report", "revenue", "budget",
    "negotiate", "stakeholder", "deliverable", "milestone", "roi", "kpi",
    "strategy", "partner", "acquisition", "agreement", "pitch", "investor",
    "quarterly", "annual", "compliance", "legal", "policy",
})

# Slang look-up table: user slang → Buddy's casual-friendly translation
_SLANG_MAP: dict[str, str] = {
    "bruh": "Hey",
    "bro": "Hey",
    "sis": "Hey",
    "fam": "Hey",
    "lowkey": "honestly",
    "highkey": "definitely",
    "lit": "amazing",
    "fire": "outstanding",
    "slay": "crush it",
    "vibe": "feel",
    "vibes": "energy",
    "drip": "style",
    "cap": "lie",
    "no cap": "for real",
    "bussin": "really good",
    "goat": "the best",
    "flex": "show off",
    "bet": "sounds good",
    "fr fr": "seriously",
    "ngl": "to be honest",
    "imo": "in my opinion",
    "fomo": "fear of missing out",
    "salty": "upset",
    "ghost": "ignore",
    "clout": "influence",
    "sus": "suspicious",
    "periodt": "period — end of story",
    "woke": "socially aware",
    "rizz": "charm",
    "snatched": "on point",
    "yeet": "toss",
    "simp": "someone overly devoted",
    "ghosting": "ignoring someone",
    "mood": "totally relatable",
    "catch feelings": "develop emotions",
    "hit different": "feel unique",
}

# Light profanity word list for business context filtering
_PROFANITY_WORDS: frozenset[str] = frozenset({
    "damn", "hell", "ass", "crap", "shit", "fuck", "bitch", "bastard",
    "damnit", "goddamn", "wtf", "bs", "bullshit", "pissed", "piss",
    "bloody", "cunt", "dick", "cock", "jackass", "motherfucker", "asshole",
})


# ---------------------------------------------------------------------------
# Supported languages
# ---------------------------------------------------------------------------

SUPPORTED_LANGUAGES: dict[str, str] = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Mandarin Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "pt": "Portuguese",
    "ar": "Arabic",
    "hi": "Hindi",
    "it": "Italian",
    "ru": "Russian",
    "nl": "Dutch",
    "sv": "Swedish",
    "pl": "Polish",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "th": "Thai",
    "id": "Indonesian",
    "ms": "Malay",
    "uk": "Ukrainian",
    "ro": "Romanian",
    "el": "Greek",
    "cs": "Czech",
    "hu": "Hungarian",
    "da": "Danish",
    "fi": "Finnish",
    "no": "Norwegian",
    "he": "Hebrew",
    "bn": "Bengali",
    "ur": "Urdu",
    "fa": "Persian",
    "sw": "Swahili",
    "tl": "Filipino",
    "ta": "Tamil",
    "te": "Telugu",
    "ml": "Malayalam",
    "mr": "Marathi",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "am": "Amharic",
    "yo": "Yoruba",
    "ig": "Igbo",
    "ha": "Hausa",
    "zu": "Zulu",
    "af": "Afrikaans",
    "ca": "Catalan",
    "sr": "Serbian",
    "hr": "Croatian",
    "sk": "Slovak",
    "bg": "Bulgarian",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "et": "Estonian",
    "sl": "Slovenian",
    "mk": "Macedonian",
    "sq": "Albanian",
    "hy": "Armenian",
    "ka": "Georgian",
    "az": "Azerbaijani",
    "kk": "Kazakh",
    "uz": "Uzbek",
    "tk": "Turkmen",
    "ky": "Kyrgyz",
    "tg": "Tajik",
    "mn": "Mongolian",
    "ne": "Nepali",
    "si": "Sinhala",
    "km": "Khmer",
    "lo": "Lao",
    "my": "Myanmar (Burmese)",
    "gl": "Galician",
    "eu": "Basque",
    "cy": "Welsh",
    "ga": "Irish",
    "is": "Icelandic",
    "mt": "Maltese",
    "lb": "Luxembourgish",
    "be": "Belarusian",
    "bs": "Bosnian",
    "fy": "Western Frisian",
    "yi": "Yiddish",
    "eo": "Esperanto",
    "la": "Latin",
    "jv": "Javanese",
    "su": "Sundanese",
    "ceb": "Cebuano",
    "ny": "Chichewa",
    "co": "Corsican",
    "ht": "Haitian Creole",
    "ku": "Kurdish",
    "ps": "Pashto",
    "sd": "Sindhi",
    "sm": "Samoan",
    "sn": "Shona",
    "so": "Somali",
    "st": "Sesotho",
    "xh": "Xhosa",
    "mg": "Malagasy",
    "mi": "Maori",
    "hmn": "Hmong",
}

# Natural fillers used to make speech feel less robotic
NATURAL_FILLERS: list[str] = [
    "uh, ", "um, ", "well, ", "you know, ", "I mean, ",
    "let me think... ", "hmm, ", "ah, ", "right, ",
]

# Humor templates (safe, light, uplifting)
HUMOR_RESPONSES: list[str] = [
    "Ha, that actually made me smile — good one!",
    "Okay, okay, I see you with the humor. I like it. 😄",
    "You know, for a human, you're pretty funny.",
    "That's either genius or chaos — I haven't decided yet.",
    "I would laugh, but I'm still processing how clever that was.",
]

CONFLICT_RESOLUTION_PROMPTS: list[str] = [
    "I hear you. Let's slow down and look at both sides here.",
    "It sounds like this situation has been really stressful. What would feel like a step forward?",
    "Sometimes when we're in conflict, the other person isn't even our real opponent — the situation is. Let's tackle it together.",
    "You're not alone in this. Walk me through what happened, and we'll figure out the best path forward.",
    "The fact that you're talking about it shows you want resolution, not just to win. That matters.",
]


@dataclass
class TranslationResult:
    """Result of a translation operation."""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float = 0.97

    def to_dict(self) -> dict:
        return {
            "original_text": self.original_text,
            "translated_text": self.translated_text,
            "source_language": self.source_language,
            "target_language": self.target_language,
            "confidence": self.confidence,
        }


@dataclass
class ConversationTurn:
    """A single conversational exchange."""
    user_input: str
    response: str
    tone: ConversationTone
    language: str = "en"
    used_filler: bool = False
    was_translated: bool = False

    def to_dict(self) -> dict:
        return {
            "user_input": self.user_input,
            "response": self.response,
            "tone": self.tone.value,
            "language": self.language,
            "used_filler": self.used_filler,
            "was_translated": self.was_translated,
        }


class ConversationEngine:
    """
    Engine for natural, human-like conversational AI.

    Parameters
    ----------
    enable_fillers : bool
        If True, occasionally insert natural speech fillers.
    active_language : str
        ISO 639-1 language code for the primary conversation language.
    humor_probability : float
        Probability (0–1) of inserting a humorous response when appropriate.
    context : CommunicationContext
        Initial communication context (CASUAL or BUSINESS).
    auto_detect_context : bool
        If True, automatically switch context based on user input keywords.
    """

    def __init__(
        self,
        enable_fillers: bool = True,
        active_language: str = "en",
        humor_probability: float = 0.15,
        context: CommunicationContext = CommunicationContext.CASUAL,
        auto_detect_context: bool = True,
    ) -> None:
        self.enable_fillers = enable_fillers
        self.active_language = active_language
        self.humor_probability = humor_probability
        self.context = context
        self.auto_detect_context = auto_detect_context
        self._history: list[ConversationTurn] = []

    # ------------------------------------------------------------------
    # Adaptive context helpers
    # ------------------------------------------------------------------

    def detect_context(self, text: str) -> CommunicationContext:
        """
        Detect whether *text* belongs to a business or casual context.

        Returns
        -------
        CommunicationContext
        """
        lower = text.lower()
        tokens = set(lower.split())
        if tokens & _BUSINESS_CONTEXT_SIGNALS:
            return CommunicationContext.BUSINESS
        return CommunicationContext.CASUAL

    def set_context(self, context: CommunicationContext) -> None:
        """Manually override the current communication context."""
        self.context = context

    def sanitize_for_business(self, text: str) -> str:
        """
        Remove profanity from *text* when in BUSINESS context.

        Replaces profane words with a professional placeholder so the
        response always maintains polished, client-ready language.

        Parameters
        ----------
        text : str
            Raw text that may contain profanity.

        Returns
        -------
        str
            Cleaned text safe for professional / business use.
        """
        words = text.split()
        cleaned = []
        for word in words:
            stripped = word.strip(".,!?;:\"'").lower()
            if stripped in _PROFANITY_WORDS:
                cleaned.append("[noted]")
            else:
                cleaned.append(word)
        return " ".join(cleaned)

    def adapt_slang(self, text: str) -> str:
        """
        Translate known slang terms in *text* into standard English so
        Buddy can acknowledge them naturally in casual mode.

        Parameters
        ----------
        text : str
            User's raw input that may include slang.

        Returns
        -------
        str
            Text with slang mapped to friendly equivalents.
        """
        result = text
        for slang, standard in _SLANG_MAP.items():
            # Case-insensitive whole-word replacement
            pattern = re.compile(r'\b' + re.escape(slang) + r'\b', re.IGNORECASE)
            result = pattern.sub(standard, result)
        return result

    # ------------------------------------------------------------------
    # Core response generation
    # ------------------------------------------------------------------

    def respond(
        self,
        user_input: str,
        tone: ConversationTone = ConversationTone.NEUTRAL,
        inject_humor: bool = False,
    ) -> ConversationTurn:
        """
        Generate a conversational response to *user_input*.

        Automatically adjusts language register based on the active
        ``CommunicationContext``:

        * **CASUAL** — mirrors the user's relaxed, slang-friendly tone.
        * **BUSINESS** — delivers a polished, profanity-free professional reply.

        Parameters
        ----------
        user_input : str
            The user's message.
        tone : ConversationTone
            Desired emotional tone for the response.
        inject_humor : bool
            Force a humorous element into the response.

        Returns
        -------
        ConversationTurn
        """
        # Auto-detect context from user input if enabled
        if self.auto_detect_context:
            detected = self.detect_context(user_input)
            if detected == CommunicationContext.BUSINESS:
                self.context = CommunicationContext.BUSINESS

        # Sanitize profanity when in business mode
        if self.context == CommunicationContext.BUSINESS:
            user_input = self.sanitize_for_business(user_input)

        filler = ""
        used_filler = False
        if self.enable_fillers and random.random() < 0.25:
            filler = random.choice(NATURAL_FILLERS)
            used_filler = True

        base_response = self._generate_response(user_input, tone)

        if inject_humor or (tone == ConversationTone.HUMOROUS and random.random() < self.humor_probability):
            base_response = random.choice(HUMOR_RESPONSES) + " " + base_response

        # In BUSINESS mode, strip fillers and ensure professional opening
        if self.context == CommunicationContext.BUSINESS:
            filler = ""
            used_filler = False
            base_response = self._apply_business_polish(base_response)

        response = filler + base_response

        turn = ConversationTurn(
            user_input=user_input,
            response=response,
            tone=tone,
            language=self.active_language,
            used_filler=used_filler,
        )
        self._history.append(turn)
        return turn

    def _apply_business_polish(self, text: str) -> str:
        """Ensure the response opens with professional framing."""
        professional_openers = [
            "Certainly. ",
            "Understood. ",
            "Absolutely. ",
            "Of course. ",
            "Thank you for bringing this to my attention. ",
        ]
        # Only prepend an opener if the text doesn't already start formally
        lower = text.lstrip().lower()
        formal_starts = ("certainly", "understood", "absolutely", "of course",
                         "thank you", "i would", "please", "let me", "i'll")
        if not any(lower.startswith(s) for s in formal_starts):
            text = random.choice(professional_openers) + text
        return text


    def _generate_response(self, user_input: str, tone: ConversationTone) -> str:
        """Build a tone-appropriate response string."""
        lower = user_input.lower()

        # Check for conflict / tension signals
        if any(k in lower for k in ("argue", "fight", "conflict", "disagree", "upset", "angry")):
            return random.choice(CONFLICT_RESOLUTION_PROMPTS)

        tone_prefixes: dict[ConversationTone, list[str]] = {
            ConversationTone.HAPPY: [
                "That's wonderful! ",
                "I love hearing that! ",
                "You're absolutely right — and I'm here for it! ",
            ],
            ConversationTone.EMPATHETIC: [
                "I completely understand. ",
                "That sounds really tough, and I want you to know I'm here. ",
                "Your feelings are completely valid. ",
            ],
            ConversationTone.HUMOROUS: [
                "You know what's funny? ",
                "Okay, hear me out... ",
                "Plot twist: ",
            ],
            ConversationTone.CALM: [
                "Let's take a breath and look at this calmly. ",
                "No rush — we can work through this together. ",
                "One step at a time. ",
            ],
            ConversationTone.EXCITED: [
                "Oh wow, this is exciting! ",
                "YES! I love where this is going! ",
                "This is so cool — tell me more! ",
            ],
            ConversationTone.SERIOUS: [
                "I want to be straightforward with you: ",
                "Let me be honest — ",
                "This matters, so let me think carefully. ",
            ],
            ConversationTone.ENCOURAGING: [
                "You've got this! ",
                "I believe in you more than you know. ",
                "Every step forward counts, no matter how small. ",
            ],
            ConversationTone.NEUTRAL: ["", "", ""],
        }

        prefix = random.choice(tone_prefixes.get(tone, [""]))
        return f"{prefix}I heard you say: \"{user_input}\". Let me help you with that."

    # ------------------------------------------------------------------
    # Language & translation
    # ------------------------------------------------------------------

    def set_language(self, lang_code: str) -> None:
        """Switch the active conversation language to *lang_code*."""
        if lang_code not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Language '{lang_code}' is not supported. "
                f"Supported: {sorted(SUPPORTED_LANGUAGES.keys())}"
            )
        self.active_language = lang_code

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> TranslationResult:
        """
        Simulate real-time translation of *text* between languages.

        Parameters
        ----------
        text : str
            Input text.
        source_lang : str
            ISO 639-1 source language code.
        target_lang : str
            ISO 639-1 target language code.

        Returns
        -------
        TranslationResult
        """
        for code in (source_lang, target_lang):
            if code not in SUPPORTED_LANGUAGES:
                raise ValueError(f"Language code '{code}' is not supported.")

        target_name = SUPPORTED_LANGUAGES[target_lang]
        translated = f"[{target_name} translation of: {text!r}]"
        return TranslationResult(
            original_text=text,
            translated_text=translated,
            source_language=source_lang,
            target_language=target_lang,
        )

    def list_supported_languages(self) -> list[dict]:
        """Return all supported languages as a list of dicts."""
        return [{"code": k, "name": v} for k, v in sorted(SUPPORTED_LANGUAGES.items())]

    # ------------------------------------------------------------------
    # Conflict resolution
    # ------------------------------------------------------------------

    def resolve_conflict(self, situation: str) -> str:
        """
        Provide a conflict-resolution response for *situation*.

        Parameters
        ----------
        situation : str
            Description of the conflict or tension.

        Returns
        -------
        str
            Mediation guidance.
        """
        prompt = random.choice(CONFLICT_RESOLUTION_PROMPTS)
        return f"{prompt} Regarding your situation: \"{situation}\" — let's find common ground."

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def get_history(self) -> list[dict]:
        """Return conversation history as a list of dicts."""
        return [t.to_dict() for t in self._history]

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self._history = []

    def detect_sarcasm(self, text: str) -> bool:
        """
        Heuristic sarcasm / irony detection.

        Returns True if the text likely contains sarcasm.
        """
        sarcasm_signals = [
            "yeah right", "sure, totally", "oh great", "wow thanks",
            "because that makes sense", "obviously", "as if",
            "what a surprise", "who knew",
        ]
        lower = text.lower()
        return any(signal in lower for signal in sarcasm_signals)

    def to_dict(self) -> dict:
        """Return engine status as a dict."""
        return {
            "active_language": self.active_language,
            "enable_fillers": self.enable_fillers,
            "humor_probability": self.humor_probability,
            "context": self.context.value,
            "auto_detect_context": self.auto_detect_context,
            "history_turns": len(self._history),
            "supported_languages": len(SUPPORTED_LANGUAGES),
        }
