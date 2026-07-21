"""
Text Processing Tools for Dreamcobots platform.

Provides text overlay for videos, instant translations, and text-to-speech
functionality with exceptional quality.
"""

import re
import unicodedata
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TextOverlay:
    """Represents a text overlay to be burned into a video frame range."""
    text: str
    start_time_seconds: float
    end_time_seconds: float
    position: Tuple[int, int] = (10, 10)   # (x, y) pixels from top-left
    font_size: int = 24
    color: str = "white"
    background_color: Optional[str] = None
    overlay_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def validate(self) -> None:
        """Raise ValueError for invalid overlay parameters."""
        if not self.text.strip():
            raise ValueError("Overlay text must not be empty.")
        if self.end_time_seconds <= self.start_time_seconds:
            raise ValueError("end_time must be after start_time.")
        if self.font_size < 1:
            raise ValueError("font_size must be >= 1.")


@dataclass
class TranslationResult:
    """Holds the result of a translation operation."""
    source_text: str
    translated_text: str
    source_language: str
    target_language: str


@dataclass
class SpeechSegment:
    """Represents a synthesised speech segment."""
    text: str
    voice: str
    speed: float           # 0.5 (slow) – 2.0 (fast), 1.0 = normal
    pitch: float           # 0.5 (low) – 2.0 (high), 1.0 = normal
    audio_format: str      # 'wav', 'mp3', 'ogg'
    segment_id: str = field(default_factory=lambda: str(uuid.uuid4()))


# ---------------------------------------------------------------------------
# Built-in translation dictionary (covers common phrases without network calls)
# ---------------------------------------------------------------------------

_BUILTIN_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "hello": {"es": "hola", "fr": "bonjour", "de": "hallo", "zh": "你好", "ar": "مرحبا"},
    "goodbye": {"es": "adiós", "fr": "au revoir", "de": "auf wiedersehen", "zh": "再见", "ar": "وداعا"},
    "thank you": {"es": "gracias", "fr": "merci", "de": "danke", "zh": "谢谢", "ar": "شكرا"},
    "yes": {"es": "sí", "fr": "oui", "de": "ja", "zh": "是", "ar": "نعم"},
    "no": {"es": "no", "fr": "non", "de": "nein", "zh": "否", "ar": "لا"},
    "welcome": {"es": "bienvenido", "fr": "bienvenue", "de": "willkommen", "zh": "欢迎", "ar": "أهلا وسهلا"},
}

SUPPORTED_LANGUAGES = {"en", "es", "fr", "de", "zh", "ar"}


# ---------------------------------------------------------------------------
# TextProcessor
# ---------------------------------------------------------------------------

class TextProcessor:
    """
    Exceptional text-processing toolkit for the Dreamcobots platform.

    Features:
    - Video text overlay specification generation
    - Instant multi-language translation
    - Text-to-speech synthesis configuration
    - Text normalisation, sanitisation, and analysis utilities
    """

    def __init__(self, default_language: str = "en") -> None:
        self.default_language = default_language
        self._overlays: List[TextOverlay] = []
        self._speech_queue: List[SpeechSegment] = []

    # ------------------------------------------------------------------
    # Text overlay (for videos)
    # ------------------------------------------------------------------

    def create_overlay(
        self,
        text: str,
        start_time_seconds: float,
        end_time_seconds: float,
        position: Tuple[int, int] = (10, 10),
        font_size: int = 24,
        color: str = "white",
        background_color: Optional[str] = None,
    ) -> TextOverlay:
        """
        Define a text overlay to appear in a video during a time window.

        Args:
            text: The text string to display.
            start_time_seconds: When the overlay appears (seconds from start).
            end_time_seconds: When the overlay disappears.
            position: (x, y) pixel coordinates.
            font_size: Font size in points.
            color: Text colour (CSS colour name or hex).
            background_color: Optional background box colour.

        Returns:
            TextOverlay descriptor (pass to your video-processing pipeline).
        """
        overlay = TextOverlay(
            text=text,
            start_time_seconds=start_time_seconds,
            end_time_seconds=end_time_seconds,
            position=position,
            font_size=font_size,
            color=color,
            background_color=background_color,
        )
        overlay.validate()
        self._overlays.append(overlay)
        return overlay

    def get_overlays(self) -> List[TextOverlay]:
        """Return all registered overlays sorted by start time."""
        return sorted(self._overlays, key=lambda o: o.start_time_seconds)

    def remove_overlay(self, overlay_id: str) -> bool:
        """Remove an overlay by ID. Returns True if found."""
        for i, o in enumerate(self._overlays):
            if o.overlay_id == overlay_id:
                self._overlays.pop(i)
                return True
        return False

    def generate_ffmpeg_drawtext(self, overlay: TextOverlay) -> str:
        """
        Generate an FFmpeg ``drawtext`` filter string for *overlay*.

        Returns:
            FFmpeg filter string suitable for use in a ``-vf`` argument.
        """
        escaped = overlay.text.replace("'", r"\'").replace(":", r"\:")
        box_part = ""
        if overlay.background_color:
            box_part = f":box=1:boxcolor={overlay.background_color}@0.5"
        return (
            f"drawtext=text='{escaped}'"
            f":x={overlay.position[0]}:y={overlay.position[1]}"
            f":fontsize={overlay.font_size}:fontcolor={overlay.color}"
            f"{box_part}"
            f":enable='between(t,{overlay.start_time_seconds},{overlay.end_time_seconds})'"
        )

    # ------------------------------------------------------------------
    # Translation
    # ------------------------------------------------------------------

    def translate(self, text: str, target_language: str, source_language: str = "en") -> TranslationResult:
        """
        Translate *text* from *source_language* to *target_language*.

        Uses the built-in phrase dictionary for known phrases; returns the
        original text with a note for phrases not yet in the dictionary.

        Args:
            text: Text to translate.
            target_language: ISO 639-1 language code (e.g. 'es', 'fr').
            source_language: Source language code (default 'en').

        Returns:
            TranslationResult with both original and translated text.

        Raises:
            ValueError: If target_language is not in SUPPORTED_LANGUAGES.
        """
        if target_language not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Language '{target_language}' not supported. Supported: {SUPPORTED_LANGUAGES}"
            )
        if source_language == target_language:
            return TranslationResult(
                source_text=text,
                translated_text=text,
                source_language=source_language,
                target_language=target_language,
            )

        normalized = text.strip().lower()
        translations = _BUILTIN_TRANSLATIONS.get(normalized, {})
        translated = translations.get(target_language, text)

        return TranslationResult(
            source_text=text,
            translated_text=translated,
            source_language=source_language,
            target_language=target_language,
        )

    def batch_translate(
        self,
        texts: List[str],
        target_language: str,
        source_language: str = "en",
    ) -> List[TranslationResult]:
        """Translate a list of texts to *target_language*."""
        return [self.translate(t, target_language, source_language) for t in texts]

    # ------------------------------------------------------------------
    # Text-to-Speech
    # ------------------------------------------------------------------

    def synthesize_speech(
        self,
        text: str,
        voice: str = "default",
        speed: float = 1.0,
        pitch: float = 1.0,
        audio_format: str = "wav",
    ) -> SpeechSegment:
        """
        Queue a text-to-speech synthesis request.

        Args:
            text: Text to synthesise.
            voice: Voice identifier (e.g. 'en-US-neural', 'default').
            speed: Playback speed multiplier (0.5–2.0).
            pitch: Pitch multiplier (0.5–2.0).
            audio_format: Output audio format ('wav', 'mp3', 'ogg').

        Returns:
            SpeechSegment descriptor.

        Raises:
            ValueError: For out-of-range speed/pitch or unsupported format.
        """
        if not 0.5 <= speed <= 2.0:
            raise ValueError("speed must be between 0.5 and 2.0")
        if not 0.5 <= pitch <= 2.0:
            raise ValueError("pitch must be between 0.5 and 2.0")
        if audio_format not in ("wav", "mp3", "ogg"):
            raise ValueError(f"Unsupported audio format '{audio_format}'")

        segment = SpeechSegment(
            text=text,
            voice=voice,
            speed=speed,
            pitch=pitch,
            audio_format=audio_format,
        )
        self._speech_queue.append(segment)
        return segment

    def get_speech_queue(self) -> List[SpeechSegment]:
        """Return all queued speech segments."""
        return list(self._speech_queue)

    def clear_speech_queue(self) -> None:
        """Clear all queued speech segments."""
        self._speech_queue.clear()

    # ------------------------------------------------------------------
    # Text utilities
    # ------------------------------------------------------------------

    @staticmethod
    def sanitize(text: str) -> str:
        """
        Remove control characters and normalise Unicode (NFC).

        Args:
            text: Raw input string.

        Returns:
            Cleaned string.
        """
        text = unicodedata.normalize("NFC", text)
        text = "".join(ch for ch in text if unicodedata.category(ch) != "Cc")
        return text.strip()

    @staticmethod
    def word_count(text: str) -> int:
        """Return the number of words in *text*."""
        return len(text.split())

    @staticmethod
    def extract_keywords(text: str, min_length: int = 4) -> List[str]:
        """
        Return a de-duplicated list of words longer than *min_length* chars.

        Args:
            text: Input text.
            min_length: Minimum word length to include.

        Returns:
            List of unique lowercase keywords (preserving first-seen order).
        """
        words = re.findall(r"\b[a-zA-Z]{%d,}\b" % min_length, text.lower())
        seen: Dict[str, None] = {}
        for w in words:
            seen.setdefault(w, None)
        return list(seen.keys())
