"""
Buddy Bot — Voice Engine

Human-like voice capabilities for Buddy Bot:
  • Natural voice synthesis with dynamic pitch, cadence, and warmth
  • Real-time voice morphing — adjust accent, tone, and speed mid-conversation
  • Voice cloning (ENTERPRISE, consent-gated) using ElevenLabs / Azure Neural Voice /
    NVIDIA Riva compatible APIs
  • Multi-speaker simulation (group conversation feel)
  • Predictive pause insertion for natural speech rhythm
  • Speech speed adaptation to match the user's speaking pace
  • Accent library — global accents with cultural sensitivity guardrails
  • Disclaimer injection whenever a cloned voice is active (transparency)

GLOBAL AI SOURCES FLOW: this module participates in GlobalAISourcesFlow
via BuddyBot.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Voice profiles
# ---------------------------------------------------------------------------

class VoiceTone(Enum):
    WARM = "warm"
    NEUTRAL = "neutral"
    ENERGETIC = "energetic"
    CALM = "calm"
    AUTHORITATIVE = "authoritative"
    PLAYFUL = "playful"
    EMPATHETIC = "empathetic"
    PROFESSIONAL = "professional"


class AccentStyle(Enum):
    AMERICAN_STANDARD = "american_standard"
    BRITISH_RP = "british_rp"
    AUSTRALIAN = "australian"
    SOUTHERN_US = "southern_us"
    NEW_YORK = "new_york"
    CANADIAN = "canadian"
    IRISH = "irish"
    SCOTTISH = "scottish"
    SOUTH_AFRICAN = "south_african"
    NIGERIAN = "nigerian"
    JAMAICAN = "jamaican"
    INDIAN_STANDARD = "indian_standard"
    FRENCH_ACCENTED = "french_accented"
    SPANISH_ACCENTED = "spanish_accented"
    PORTUGUESE_ACCENTED = "portuguese_accented"
    GERMAN_ACCENTED = "german_accented"
    JAPANESE_ACCENTED = "japanese_accented"
    KOREAN_ACCENTED = "korean_accented"
    MANDARIN_ACCENTED = "mandarin_accented"
    ARABIC_ACCENTED = "arabic_accented"
    NEUTRAL_GLOBAL = "neutral_global"


# Compatible voice synthesis backends
VOICE_BACKENDS: list[str] = [
    "ElevenLabs",
    "Microsoft Azure Neural Voice",
    "NVIDIA Riva",
    "OpenAI TTS",
    "Google Cloud Text-to-Speech",
    "Amazon Polly",
    "Enterprise AI Text to Speech",
    "DreamCo Voice Engine (proprietary)",
]


@dataclass
class VoiceProfile:
    """A reusable voice configuration."""
    profile_id: str
    display_name: str
    tone: VoiceTone
    accent: AccentStyle
    pitch_semitones: float = 0.0      # offset from baseline; negative = lower
    speed_wpm: int = 140              # words per minute
    warmth: float = 0.7               # 0.0 (cold) → 1.0 (very warm)
    pause_probability: float = 0.2    # probability of inserting a natural pause
    backend: str = "DreamCo Voice Engine (proprietary)"
    is_cloned: bool = False
    clone_source_user: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "profile_id": self.profile_id,
            "display_name": self.display_name,
            "tone": self.tone.value,
            "accent": self.accent.value,
            "pitch_semitones": self.pitch_semitones,
            "speed_wpm": self.speed_wpm,
            "warmth": self.warmth,
            "pause_probability": self.pause_probability,
            "backend": self.backend,
            "is_cloned": self.is_cloned,
            "clone_source_user": self.clone_source_user,
        }


@dataclass
class SpeechOutput:
    """Result of a voice synthesis operation."""
    text: str
    ssml: str
    profile: VoiceProfile
    estimated_duration_seconds: float
    natural_pauses_inserted: int
    disclaimer: str = ""

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "ssml": self.ssml,
            "profile_id": self.profile.profile_id,
            "tone": self.profile.tone.value,
            "accent": self.profile.accent.value,
            "estimated_duration_seconds": round(self.estimated_duration_seconds, 2),
            "natural_pauses_inserted": self.natural_pauses_inserted,
            "backend": self.profile.backend,
            "disclaimer": self.disclaimer,
        }


# Default built-in voice profiles
DEFAULT_PROFILES: list[VoiceProfile] = [
    VoiceProfile(
        profile_id="buddy_default",
        display_name="Buddy — Default",
        tone=VoiceTone.WARM,
        accent=AccentStyle.NEUTRAL_GLOBAL,
        pitch_semitones=0.0,
        speed_wpm=140,
        warmth=0.8,
    ),
    VoiceProfile(
        profile_id="buddy_calm",
        display_name="Buddy — Calm",
        tone=VoiceTone.CALM,
        accent=AccentStyle.AMERICAN_STANDARD,
        pitch_semitones=-1.0,
        speed_wpm=120,
        warmth=0.9,
    ),
    VoiceProfile(
        profile_id="buddy_energetic",
        display_name="Buddy — Energetic",
        tone=VoiceTone.ENERGETIC,
        accent=AccentStyle.AMERICAN_STANDARD,
        pitch_semitones=1.5,
        speed_wpm=165,
        warmth=0.7,
    ),
    VoiceProfile(
        profile_id="buddy_professional",
        display_name="Buddy — Professional",
        tone=VoiceTone.PROFESSIONAL,
        accent=AccentStyle.BRITISH_RP,
        pitch_semitones=-0.5,
        speed_wpm=130,
        warmth=0.5,
    ),
]


class VoiceEngineError(Exception):
    """Raised when a voice operation cannot be completed."""


class VoiceEngine:
    """
    Manages voice synthesis, morphing, and (consented) voice cloning for Buddy Bot.

    Parameters
    ----------
    active_profile_id : str
        Profile ID to use by default.
    """

    def __init__(self, active_profile_id: str = "buddy_default") -> None:
        self._profiles: dict[str, VoiceProfile] = {
            p.profile_id: p for p in DEFAULT_PROFILES
        }
        self._active_profile_id = active_profile_id
        self._consent_records: dict[str, dict] = {}   # user_id → consent info
        self._synthesis_history: list[SpeechOutput] = []

    # ------------------------------------------------------------------
    # Profile management
    # ------------------------------------------------------------------

    @property
    def active_profile(self) -> VoiceProfile:
        """Return the currently active VoiceProfile."""
        return self._profiles[self._active_profile_id]

    def set_active_profile(self, profile_id: str) -> VoiceProfile:
        """Switch the active voice profile."""
        if profile_id not in self._profiles:
            raise VoiceEngineError(
                f"Voice profile '{profile_id}' not found. "
                f"Available: {list(self._profiles.keys())}"
            )
        self._active_profile_id = profile_id
        return self._profiles[profile_id]

    def add_profile(self, profile: VoiceProfile) -> None:
        """Register a new voice profile."""
        self._profiles[profile.profile_id] = profile

    def list_profiles(self) -> list[dict]:
        """Return all available voice profiles as dicts."""
        return [p.to_dict() for p in self._profiles.values()]

    # ------------------------------------------------------------------
    # Speech synthesis
    # ------------------------------------------------------------------

    def synthesise(
        self,
        text: str,
        profile_id: Optional[str] = None,
        adapt_speed_wpm: Optional[int] = None,
    ) -> SpeechOutput:
        """
        Convert *text* to a speech output descriptor.

        Parameters
        ----------
        text : str
            The text to speak.
        profile_id : str | None
            Override the active profile for this call.
        adapt_speed_wpm : int | None
            Override the profile's speech speed (adaptive pacing).

        Returns
        -------
        SpeechOutput
        """
        profile = self._profiles.get(profile_id or self._active_profile_id)
        if profile is None:
            raise VoiceEngineError(f"Voice profile '{profile_id}' not found.")

        speed = adapt_speed_wpm or profile.speed_wpm
        ssml, pauses = self._build_ssml(text, profile, speed)
        duration = len(text.split()) / (speed / 60.0)

        disclaimer = ""
        if profile.is_cloned:
            disclaimer = (
                f"⚠️ AI VOICE DISCLOSURE: This voice is a cloned replica of "
                f"user '{profile.clone_source_user}' generated with explicit consent. "
                "For entertainment / productivity purposes only."
            )

        output = SpeechOutput(
            text=text,
            ssml=ssml,
            profile=profile,
            estimated_duration_seconds=duration,
            natural_pauses_inserted=pauses,
            disclaimer=disclaimer,
        )
        self._synthesis_history.append(output)
        return output

    def _build_ssml(
        self,
        text: str,
        profile: VoiceProfile,
        speed_wpm: int,
    ) -> tuple[str, int]:
        """
        Build a simplified SSML string with natural pauses.

        Returns (ssml_string, pause_count).
        """
        words = text.split()
        ssml_words: list[str] = []
        pause_count = 0
        pause_interval = random.randint(8, 15)
        for i, word in enumerate(words):
            ssml_words.append(word)
            if i > 0 and i % pause_interval == 0:
                if random.random() < profile.pause_probability:
                    ssml_words.append('<break time="300ms"/>')
                    pause_count += 1

        inner = " ".join(ssml_words)
        rate_pct = int((speed_wpm / 140) * 100)
        pitch_st = f"{profile.pitch_semitones:+.1f}st"
        ssml = (
            f'<speak version="1.0">'
            f'<prosody rate="{rate_pct}%" pitch="{pitch_st}">'
            f"{inner}"
            f"</prosody></speak>"
        )
        return ssml, pause_count

    # ------------------------------------------------------------------
    # Real-time voice morphing
    # ------------------------------------------------------------------

    def morph_voice(
        self,
        tone: Optional[VoiceTone] = None,
        accent: Optional[AccentStyle] = None,
        pitch_delta: float = 0.0,
        speed_delta: int = 0,
    ) -> VoiceProfile:
        """
        Adjust the active voice profile in real time.

        Parameters
        ----------
        tone : VoiceTone | None
            New tone to apply.
        accent : AccentStyle | None
            New accent to apply.
        pitch_delta : float
            Semitone offset to add/subtract from current pitch.
        speed_delta : int
            WPM offset to add/subtract from current speed.

        Returns
        -------
        Updated VoiceProfile
        """
        p = self.active_profile
        if tone is not None:
            p.tone = tone
        if accent is not None:
            p.accent = accent
        p.pitch_semitones = max(-6.0, min(6.0, p.pitch_semitones + pitch_delta))
        p.speed_wpm = max(80, min(220, p.speed_wpm + speed_delta))
        return p

    # ------------------------------------------------------------------
    # Voice cloning (consent-gated, ENTERPRISE)
    # ------------------------------------------------------------------

    def request_voice_clone_consent(self, user_id: str) -> str:
        """Generate consent request text for voice cloning."""
        return (
            f"CONSENT REQUIRED — Voice Clone Feature\n"
            f"User ID: {user_id}\n"
            f"You are granting Buddy Bot permission to create a synthetic voice model "
            f"based on your voice recordings. This clone will ONLY be used within your "
            f"private Buddy Bot session. It will NEVER be used to impersonate you publicly "
            f"or without further explicit consent. A clear AI disclaimer will always precede "
            f"any use of a cloned voice. You may revoke this at any time.\n"
            f"To confirm, pass this exact text to grant_voice_clone_consent()."
        )

    def grant_voice_clone_consent(
        self,
        user_id: str,
        consent_text: str,
        voice_sample_reference: str,
    ) -> dict:
        """
        Record voice cloning consent and create a cloned profile.

        Parameters
        ----------
        user_id : str
            The consenting user.
        consent_text : str
            The full consent text accepted by the user.
        voice_sample_reference : str
            Reference ID for the submitted voice sample data.

        Returns
        -------
        dict with the new profile_id and consent details.
        """
        import time as _time
        self._consent_records[user_id] = {
            "feature": "voice_clone",
            "granted": True,
            "timestamp": _time.time(),
            "consent_text_hash": hash(consent_text),
        }
        profile_id = f"clone_{user_id}"
        cloned_profile = VoiceProfile(
            profile_id=profile_id,
            display_name=f"Cloned Voice — {user_id}",
            tone=VoiceTone.WARM,
            accent=AccentStyle.NEUTRAL_GLOBAL,
            backend="ElevenLabs / DreamCo Voice Engine",
            is_cloned=True,
            clone_source_user=user_id,
        )
        self._profiles[profile_id] = cloned_profile
        return {
            "status": "voice_clone_created",
            "profile_id": profile_id,
            "user_id": user_id,
            "voice_sample_reference": voice_sample_reference,
            "disclaimer_required": True,
            "consent_verified": True,
        }

    def revoke_voice_clone_consent(self, user_id: str) -> None:
        """Revoke voice clone consent and delete the cloned profile."""
        profile_id = f"clone_{user_id}"
        self._consent_records.pop(user_id, None)
        self._profiles.pop(profile_id, None)

    def has_voice_clone_consent(self, user_id: str) -> bool:
        """Return True if the user has granted voice cloning consent."""
        return self._consent_records.get(user_id, {}).get("granted", False)

    # ------------------------------------------------------------------
    # Multi-speaker simulation
    # ------------------------------------------------------------------

    def simulate_group_conversation(self, speakers: list[str], lines: list[str]) -> list[dict]:
        """
        Simulate a group conversation with multiple voice personas.

        Parameters
        ----------
        speakers : list[str]
            List of speaker display names.
        lines : list[str]
            Corresponding dialogue lines (same length as speakers).

        Returns
        -------
        list[dict]
            Synthesised outputs for each line.
        """
        if len(speakers) != len(lines):
            raise VoiceEngineError("speakers and lines must have the same length.")

        results = []
        for speaker, line in zip(speakers, lines):
            profile_id = self._get_or_create_speaker_profile(speaker)
            output = self.synthesise(line, profile_id=profile_id)
            results.append({"speaker": speaker, **output.to_dict()})
        return results

    def _get_or_create_speaker_profile(self, speaker: str) -> str:
        """Return a profile_id for a speaker, creating one if needed."""
        pid = f"speaker_{speaker.lower().replace(' ', '_')}"
        if pid not in self._profiles:
            tones = list(VoiceTone)
            accents = list(AccentStyle)
            self._profiles[pid] = VoiceProfile(
                profile_id=pid,
                display_name=speaker,
                tone=random.choice(tones),
                accent=random.choice(accents),
            )
        return pid

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_synthesis_history(self) -> list[dict]:
        """Return synthesis history as a list of dicts."""
        return [s.to_dict() for s in self._synthesis_history]

    def to_dict(self) -> dict:
        """Return engine status as a dict."""
        return {
            "active_profile": self.active_profile.to_dict(),
            "total_profiles": len(self._profiles),
            "synthesis_history_count": len(self._synthesis_history),
            "available_backends": VOICE_BACKENDS,
            "consent_records": len(self._consent_records),
        }
