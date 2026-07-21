# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Image Synthesis Engine — Buddy Trust Bot

Allows Buddy to generate image and video avatars from user-approved data.
All operations REQUIRE explicit IMAGE_SYNTHESIS consent.

Use cases:
  - Professional presentation avatars
  - Creative video content with a personalised face/voice overlay
  - Digital twin representation for remote meetings

Guardrails:
  - Consent required before any avatar is created.
  - Avatars can be frozen or revoked by the owner.
  - Synthesis history is fully traceable via consent tokens.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AvatarType(Enum):
    PHOTO = "photo"             # Static image
    ANIMATED_GIF = "animated_gif"
    VIDEO_AVATAR = "video_avatar"
    HOLOGRAPHIC = "holographic" # AR/VR overlay


class AvatarStatus(Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    REVOKED = "revoked"


@dataclass
class ImageAvatar:
    """
    A generated image/video avatar.

    ``image_data_ref`` is an opaque reference (e.g. S3 key or encrypted blob ID).
    """

    avatar_id: str
    owner_user_id: str
    display_name: str
    avatar_type: AvatarType
    image_data_ref: str     # Encrypted reference to stored image/video
    consent_token: str
    status: AvatarStatus = AvatarStatus.ACTIVE
    resolution: str = "1920x1080"
    duration_seconds: float = 0.0    # For video/animated types
    created_at: float = 0.0
    tags: list = field(default_factory=list)

    def is_usable(self) -> bool:
        return self.status == AvatarStatus.ACTIVE

    def to_dict(self) -> dict:
        return {
            "avatar_id": self.avatar_id,
            "owner_user_id": self.owner_user_id,
            "display_name": self.display_name,
            "avatar_type": self.avatar_type.value,
            "image_data_ref": self.image_data_ref,
            "consent_token": self.consent_token,
            "status": self.status.value,
            "resolution": self.resolution,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at,
            "tags": self.tags,
        }


@dataclass
class SynthesisJob:
    """Represents a queued or completed synthesis job."""

    job_id: str
    avatar_id: str
    prompt: str             # Creative/professional description for synthesis
    output_ref: str         # Reference to generated output
    consent_token: str
    completed: bool = False
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "avatar_id": self.avatar_id,
            "prompt": self.prompt,
            "output_ref": self.output_ref,
            "consent_token": self.consent_token,
            "completed": self.completed,
            "error": self.error,
        }


class ImageSynthesisEngine:
    """
    Image and video avatar synthesis with consent enforcement.

    Parameters
    ----------
    max_avatars : Optional[int]
        Maximum number of stored avatars (None = unlimited).
    consent_manager :
        Shared ConsentManager instance for consent validation.
    """

    def __init__(self, max_avatars: Optional[int], consent_manager) -> None:
        self._max_avatars = max_avatars
        self._consent_manager = consent_manager
        self._avatars: dict[str, ImageAvatar] = {}
        self._jobs: dict[str, SynthesisJob] = {}

    # ------------------------------------------------------------------
    # Avatar management
    # ------------------------------------------------------------------

    def create_avatar(
        self,
        owner_user_id: str,
        display_name: str,
        avatar_type: AvatarType = AvatarType.PHOTO,
        resolution: str = "1920x1080",
        duration_seconds: float = 0.0,
        tags: Optional[list] = None,
    ) -> ImageAvatar:
        """
        Create a new image avatar.

        Requires active IMAGE_SYNTHESIS consent for *owner_user_id*.
        """
        from bots.buddy_trust_bot.consent_manager import ConsentType
        consent = self._consent_manager.require_consent(
            owner_user_id, ConsentType.IMAGE_SYNTHESIS
        )

        if self._max_avatars is not None and len(self._avatars) >= self._max_avatars:
            raise ImageSynthesisLimitError(
                f"Avatar limit ({self._max_avatars}) reached on current tier."
            )

        import time
        avatar_id = str(uuid.uuid4())
        avatar = ImageAvatar(
            avatar_id=avatar_id,
            owner_user_id=owner_user_id,
            display_name=display_name,
            avatar_type=avatar_type,
            image_data_ref=f"img_blob:{avatar_id}",
            consent_token=consent.acknowledgment_token,
            resolution=resolution,
            duration_seconds=duration_seconds,
            created_at=time.time(),
            tags=tags or [],
        )
        self._avatars[avatar_id] = avatar
        return avatar

    def freeze_avatar(self, avatar_id: str) -> ImageAvatar:
        """Freeze an avatar — no synthesis while frozen."""
        avatar = self._get_avatar(avatar_id)
        avatar.status = AvatarStatus.FROZEN
        return avatar

    def unfreeze_avatar(self, avatar_id: str) -> ImageAvatar:
        """Unfreeze a previously frozen avatar."""
        avatar = self._get_avatar(avatar_id)
        if avatar.status == AvatarStatus.REVOKED:
            raise ImageSynthesisError("A revoked avatar cannot be unfrozen.")
        avatar.status = AvatarStatus.ACTIVE
        return avatar

    def revoke_avatar(self, avatar_id: str) -> ImageAvatar:
        """Permanently revoke an avatar (consent withdrawn)."""
        avatar = self._get_avatar(avatar_id)
        avatar.status = AvatarStatus.REVOKED
        return avatar

    # ------------------------------------------------------------------
    # Synthesis jobs
    # ------------------------------------------------------------------

    def submit_synthesis_job(
        self,
        avatar_id: str,
        prompt: str,
        requester_user_id: str,
    ) -> SynthesisJob:
        """
        Submit a synthesis job to generate creative content using an avatar.

        Requires active IMAGE_SYNTHESIS consent for *requester_user_id*.
        """
        from bots.buddy_trust_bot.consent_manager import ConsentType
        consent = self._consent_manager.require_consent(
            requester_user_id, ConsentType.IMAGE_SYNTHESIS
        )
        avatar = self._get_avatar(avatar_id)
        if not avatar.is_usable():
            raise ImageSynthesisError(
                f"Avatar '{avatar_id}' is {avatar.status.value} and cannot be used."
            )

        job_id = str(uuid.uuid4())
        job = SynthesisJob(
            job_id=job_id,
            avatar_id=avatar_id,
            prompt=prompt,
            output_ref=f"output:{job_id}",
            consent_token=consent.acknowledgment_token,
            completed=True,   # Simulated immediate completion
        )
        self._jobs[job_id] = job
        return job

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_avatar(self, avatar_id: str) -> ImageAvatar:
        return self._get_avatar(avatar_id)

    def list_avatars(
        self,
        owner_user_id: Optional[str] = None,
        active_only: bool = False,
    ) -> list[ImageAvatar]:
        avatars = list(self._avatars.values())
        if owner_user_id:
            avatars = [a for a in avatars if a.owner_user_id == owner_user_id]
        if active_only:
            avatars = [a for a in avatars if a.is_usable()]
        return avatars

    def list_jobs(self, avatar_id: Optional[str] = None) -> list[SynthesisJob]:
        jobs = list(self._jobs.values())
        if avatar_id:
            jobs = [j for j in jobs if j.avatar_id == avatar_id]
        return jobs

    def avatar_count(self) -> int:
        return len(self._avatars)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_avatar(self, avatar_id: str) -> ImageAvatar:
        if avatar_id not in self._avatars:
            raise ImageSynthesisError(f"Avatar '{avatar_id}' not found.")
        return self._avatars[avatar_id]


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ImageSynthesisError(Exception):
    """General image synthesis error."""


class ImageSynthesisLimitError(ImageSynthesisError):
    """Raised when the tier avatar limit is exceeded."""


__all__ = [
    "AvatarType",
    "AvatarStatus",
    "ImageAvatar",
    "SynthesisJob",
    "ImageSynthesisEngine",
    "ImageSynthesisError",
    "ImageSynthesisLimitError",
]
