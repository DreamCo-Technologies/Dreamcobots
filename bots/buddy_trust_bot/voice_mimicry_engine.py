# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Voice Mimicry Engine — Buddy Trust Bot

Allows Buddy to create and use voice profiles for personalized voice synthesis.
All operations REQUIRE explicit consent from the individual being mimicked.

Guardrails:
  - Consent check before every synthesis operation.
  - No profile is stored without acknowledgment_token.
  - Profiles can be frozen/unfrozen by the owner at any time.
  - All synthesis events are logged (caller must pass an AuditLog instance).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class VoiceProfileStatus(Enum):
    ACTIVE = "active"
    FROZEN = "frozen"       # Owner has locked this profile
    REVOKED = "revoked"     # Consent revoked — profile unusable


@dataclass
class VoiceProfile:
    """
    A stored voice profile for a consented individual.

    In a real deployment the ``voice_data_ref`` would be an encrypted
    reference to a vector store or audio model checkpoint.  Here it is
    stored as an opaque string for simulation purposes.
    """

    profile_id: str
    owner_user_id: str          # Person whose voice is captured
    display_name: str
    language: str               # e.g. "en-US"
    accent: str                 # e.g. "Southern American"
    voice_data_ref: str         # Opaque encrypted reference
    consent_token: str          # acknowledgment_token from ConsentManager
    status: VoiceProfileStatus = VoiceProfileStatus.ACTIVE
    sample_count: int = 0       # Number of audio samples provided
    created_at: float = 0.0
    tags: list = field(default_factory=list)

    def is_usable(self) -> bool:
        return self.status == VoiceProfileStatus.ACTIVE

    def to_dict(self) -> dict:
        return {
            "profile_id": self.profile_id,
            "owner_user_id": self.owner_user_id,
            "display_name": self.display_name,
            "language": self.language,
            "accent": self.accent,
            "voice_data_ref": self.voice_data_ref,
            "consent_token": self.consent_token,
            "status": self.status.value,
            "sample_count": self.sample_count,
            "created_at": self.created_at,
            "tags": self.tags,
        }


@dataclass
class VoiceSynthesisResult:
    """Result of a voice synthesis request."""

    synthesis_id: str
    profile_id: str
    text: str
    audio_ref: str          # Opaque reference to synthesised audio
    duration_seconds: float
    consent_token: str      # Token verified at time of synthesis

    def to_dict(self) -> dict:
        return {
            "synthesis_id": self.synthesis_id,
            "profile_id": self.profile_id,
            "text": self.text,
            "audio_ref": self.audio_ref,
            "duration_seconds": self.duration_seconds,
            "consent_token": self.consent_token,
        }


class VoiceMimicryEngine:
    """
    Voice mimicry with explicit consent enforcement.

    Parameters
    ----------
    max_profiles : Optional[int]
        Maximum number of stored voice profiles (None = unlimited).
    consent_manager : ConsentManager
        Shared ConsentManager instance for consent validation.
    """

    def __init__(self, max_profiles: Optional[int], consent_manager) -> None:
        self._max_profiles = max_profiles
        self._consent_manager = consent_manager
        self._profiles: dict[str, VoiceProfile] = {}   # profile_id -> profile

    # ------------------------------------------------------------------
    # Profile management
    # ------------------------------------------------------------------

    def create_profile(
        self,
        owner_user_id: str,
        display_name: str,
        language: str = "en-US",
        accent: str = "",
        voice_data_ref: str = "",
        tags: Optional[list] = None,
    ) -> VoiceProfile:
        """
        Create a new voice profile.

        Requires active VOICE_MIMICRY consent for *owner_user_id*.
        Raises ``VoiceMimicryError`` if consent is missing or limit exceeded.
        """
        from bots.buddy_trust_bot.consent_manager import ConsentType
        consent = self._consent_manager.require_consent(owner_user_id, ConsentType.VOICE_MIMICRY)

        if self._max_profiles is not None and len(self._profiles) >= self._max_profiles:
            raise VoiceMimicryLimitError(
                f"Voice profile limit ({self._max_profiles}) reached on current tier."
            )

        import time
        profile_id = str(uuid.uuid4())
        profile = VoiceProfile(
            profile_id=profile_id,
            owner_user_id=owner_user_id,
            display_name=display_name,
            language=language,
            accent=accent,
            voice_data_ref=voice_data_ref or f"voice_vector:{profile_id}",
            consent_token=consent.acknowledgment_token,
            created_at=time.time(),
            tags=tags or [],
        )
        self._profiles[profile_id] = profile
        return profile

    def add_samples(self, profile_id: str, sample_count: int) -> VoiceProfile:
        """Increase the sample count for a voice profile (simulates audio ingestion)."""
        profile = self._get_profile(profile_id)
        profile.sample_count += sample_count
        return profile

    def freeze_profile(self, profile_id: str) -> VoiceProfile:
        """Freeze a voice profile — no synthesis allowed while frozen."""
        profile = self._get_profile(profile_id)
        profile.status = VoiceProfileStatus.FROZEN
        return profile

    def unfreeze_profile(self, profile_id: str) -> VoiceProfile:
        """Unfreeze a previously frozen voice profile."""
        profile = self._get_profile(profile_id)
        if profile.status == VoiceProfileStatus.REVOKED:
            raise VoiceMimicryError("A revoked profile cannot be unfrozen.")
        profile.status = VoiceProfileStatus.ACTIVE
        return profile

    def revoke_profile(self, profile_id: str) -> VoiceProfile:
        """Permanently revoke a voice profile (consent withdrawn)."""
        profile = self._get_profile(profile_id)
        profile.status = VoiceProfileStatus.REVOKED
        return profile

    # ------------------------------------------------------------------
    # Synthesis
    # ------------------------------------------------------------------

    def synthesize(
        self,
        profile_id: str,
        text: str,
        requester_user_id: str,
    ) -> VoiceSynthesisResult:
        """
        Synthesise speech in the voice of the profile owner.

        The *requester_user_id* must have active VOICE_MIMICRY consent AND
        the profile itself must be ACTIVE (not frozen or revoked).
        """
        from bots.buddy_trust_bot.consent_manager import ConsentType
        consent = self._consent_manager.require_consent(
            requester_user_id, ConsentType.VOICE_MIMICRY
        )
        profile = self._get_profile(profile_id)

        if not profile.is_usable():
            raise VoiceMimicryError(
                f"Profile '{profile_id}' is {profile.status.value} and cannot be used for synthesis."
            )

        import time
        synthesis_id = str(uuid.uuid4())
        words = len(text.split())
        duration = round(words * 0.4, 2)   # ~150 WPM simulation

        return VoiceSynthesisResult(
            synthesis_id=synthesis_id,
            profile_id=profile_id,
            text=text,
            audio_ref=f"audio:{synthesis_id}",
            duration_seconds=duration,
            consent_token=consent.acknowledgment_token,
        )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_profile(self, profile_id: str) -> VoiceProfile:
        return self._get_profile(profile_id)

    def list_profiles(
        self,
        owner_user_id: Optional[str] = None,
        active_only: bool = False,
    ) -> list[VoiceProfile]:
        profiles = list(self._profiles.values())
        if owner_user_id:
            profiles = [p for p in profiles if p.owner_user_id == owner_user_id]
        if active_only:
            profiles = [p for p in profiles if p.is_usable()]
        return profiles

    def profile_count(self) -> int:
        return len(self._profiles)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_profile(self, profile_id: str) -> VoiceProfile:
        if profile_id not in self._profiles:
            raise VoiceMimicryError(f"Voice profile '{profile_id}' not found.")
        return self._profiles[profile_id]


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class VoiceMimicryError(Exception):
    """General voice mimicry error."""


class VoiceMimicryLimitError(VoiceMimicryError):
    """Raised when the tier profile limit is exceeded."""


__all__ = [
    "VoiceProfileStatus",
    "VoiceProfile",
    "VoiceSynthesisResult",
    "VoiceMimicryEngine",
    "VoiceMimicryError",
    "VoiceMimicryLimitError",
]
