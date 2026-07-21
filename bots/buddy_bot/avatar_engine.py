"""
Buddy Bot — Avatar Engine

Renders and manages Buddy's visual presence:
  • 2D avatar with basic expression states (FREE tier)
  • Hyper-realistic 3D avatar with micro-expressions (PRO+)
    — blinking, head tilts, eyebrow raises, subtle smiles
    — lip-syncing tied to voice output
    — dynamic eye contact simulation
  • Augmented Reality (AR) integration — place Buddy in the user's environment
  • Virtual Reality (VR) full-presence companion mode
  • Holographic projection API for physical-room presence (ENTERPRISE)
  • Customisable appearance — face, hairstyle, clothing, accessories
  • Body-language animations during conversation (gestures, posture)
  • Digital Twin mode — optional replication of a user's own appearance
    (requires explicit written consent)

GLOBAL AI SOURCES FLOW: this module participates in GlobalAISourcesFlow
via BuddyBot.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Avatar types
# ---------------------------------------------------------------------------

class AvatarType(Enum):
    AVATAR_2D = "2d"
    AVATAR_3D = "3d"
    DIGITAL_TWIN = "digital_twin"


class AvatarEnvironment(Enum):
    SCREEN = "screen"
    AR = "ar"
    VR = "vr"
    HOLOGRAPHIC = "holographic"


# ---------------------------------------------------------------------------
# Expression catalogue
# ---------------------------------------------------------------------------

class MicroExpression(Enum):
    NEUTRAL = "neutral"
    SOFT_SMILE = "soft_smile"
    WIDE_SMILE = "wide_smile"
    CURIOUS_HEAD_TILT = "curious_head_tilt"
    RAISED_EYEBROW = "raised_eyebrow"
    EMPATHETIC_NOD = "empathetic_nod"
    THOUGHTFUL_PAUSE = "thoughtful_pause"
    SURPRISED_BLINK = "surprised_blink"
    CONCERNED_FURROW = "concerned_furrow"
    PLAYFUL_WINK = "playful_wink"
    ENCOURAGING_SMILE = "encouraging_smile"


class BodyGesture(Enum):
    IDLE = "idle"
    OPEN_HANDS = "open_hands"
    POINTING = "pointing"
    THINKING_POSE = "thinking_pose"
    THUMBS_UP = "thumbs_up"
    WAVE = "wave"
    LEAN_FORWARD = "lean_forward"
    HEAD_NOD = "head_nod"
    ARMS_OPEN = "arms_open"
    HAND_HEART = "hand_heart"


# Emotion → most fitting micro-expression mapping
EMOTION_TO_EXPRESSION: dict[str, MicroExpression] = {
    "joy": MicroExpression.WIDE_SMILE,
    "excitement": MicroExpression.WIDE_SMILE,
    "happiness": MicroExpression.SOFT_SMILE,
    "neutral": MicroExpression.NEUTRAL,
    "sadness": MicroExpression.EMPATHETIC_NOD,
    "empathy": MicroExpression.EMPATHETIC_NOD,
    "concern": MicroExpression.CONCERNED_FURROW,
    "anger": MicroExpression.CONCERNED_FURROW,
    "surprise": MicroExpression.SURPRISED_BLINK,
    "curious": MicroExpression.CURIOUS_HEAD_TILT,
    "humor": MicroExpression.PLAYFUL_WINK,
    "playful": MicroExpression.PLAYFUL_WINK,
    "encouragement": MicroExpression.ENCOURAGING_SMILE,
}


@dataclass
class AvatarAppearance:
    """Customisable visual appearance of Buddy's avatar."""
    face_preset: str = "default"
    skin_tone: str = "medium"
    hair_style: str = "natural_waves"
    hair_color: str = "brown"
    eye_color: str = "brown"
    clothing_style: str = "casual_smart"
    accessories: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "face_preset": self.face_preset,
            "skin_tone": self.skin_tone,
            "hair_style": self.hair_style,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "clothing_style": self.clothing_style,
            "accessories": self.accessories,
        }


@dataclass
class AvatarFrame:
    """A single rendered frame descriptor for Buddy's avatar."""
    expression: MicroExpression
    gesture: BodyGesture
    environment: AvatarEnvironment
    lip_sync_text: str = ""
    eye_contact: bool = True
    blink: bool = False
    head_tilt_degrees: float = 0.0

    def to_dict(self) -> dict:
        return {
            "expression": self.expression.value,
            "gesture": self.gesture.value,
            "environment": self.environment.value,
            "lip_sync_text": self.lip_sync_text,
            "eye_contact": self.eye_contact,
            "blink": self.blink,
            "head_tilt_degrees": self.head_tilt_degrees,
        }


@dataclass
class ConsentRecord:
    """Tracks explicit user consent for identity/image replication features."""
    user_id: str
    feature: str
    granted: bool
    timestamp: float
    consent_text: str

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "feature": self.feature,
            "granted": self.granted,
            "timestamp": self.timestamp,
            "consent_text": self.consent_text[:100],
        }


class AvatarEngineError(Exception):
    """Raised when an avatar operation cannot be completed."""


class AvatarEngine:
    """
    Manages Buddy Bot's visual avatar presence.

    Parameters
    ----------
    avatar_type : AvatarType
        The type of avatar to render.
    environment : AvatarEnvironment
        Where the avatar will be displayed.
    appearance : AvatarAppearance | None
        Custom appearance settings; defaults to standard if None.
    """

    def __init__(
        self,
        avatar_type: AvatarType = AvatarType.AVATAR_2D,
        environment: AvatarEnvironment = AvatarEnvironment.SCREEN,
        appearance: Optional[AvatarAppearance] = None,
    ) -> None:
        self.avatar_type = avatar_type
        self.environment = environment
        self.appearance = appearance or AvatarAppearance()
        self._consent_records: list[ConsentRecord] = []
        self._frame_history: list[AvatarFrame] = []

    # ------------------------------------------------------------------
    # Frame generation
    # ------------------------------------------------------------------

    def render_frame(
        self,
        emotion: str = "neutral",
        speech_text: str = "",
        force_blink: Optional[bool] = None,
    ) -> AvatarFrame:
        """
        Generate an avatar frame descriptor for the given emotional state.

        Parameters
        ----------
        emotion : str
            Detected or requested emotion label.
        speech_text : str
            Text being spoken (for lip sync).
        force_blink : bool | None
            Override the blink state; auto-randomised if None.

        Returns
        -------
        AvatarFrame
        """
        expression = EMOTION_TO_EXPRESSION.get(emotion.lower(), MicroExpression.NEUTRAL)
        gesture = self._emotion_to_gesture(emotion)
        blink = force_blink if force_blink is not None else (random.random() < 0.08)
        tilt = 0.0
        if expression in (MicroExpression.CURIOUS_HEAD_TILT, MicroExpression.EMPATHETIC_NOD):
            tilt = random.uniform(5.0, 12.0)

        frame = AvatarFrame(
            expression=expression,
            gesture=gesture,
            environment=self.environment,
            lip_sync_text=speech_text,
            eye_contact=True,
            blink=blink,
            head_tilt_degrees=tilt,
        )
        self._frame_history.append(frame)
        return frame

    def _emotion_to_gesture(self, emotion: str) -> BodyGesture:
        """Map an emotion string to a body gesture."""
        mapping = {
            "joy": BodyGesture.THUMBS_UP,
            "excitement": BodyGesture.OPEN_HANDS,
            "sadness": BodyGesture.LEAN_FORWARD,
            "empathy": BodyGesture.LEAN_FORWARD,
            "love": BodyGesture.HAND_HEART,
            "encouragement": BodyGesture.THUMBS_UP,
            "greeting": BodyGesture.WAVE,
            "thinking": BodyGesture.THINKING_POSE,
            "neutral": BodyGesture.IDLE,
        }
        return mapping.get(emotion.lower(), BodyGesture.IDLE)

    # ------------------------------------------------------------------
    # Environment switching
    # ------------------------------------------------------------------

    def enter_ar_mode(self) -> dict:
        """Switch avatar to Augmented Reality environment."""
        self.environment = AvatarEnvironment.AR
        return {
            "mode": "ar",
            "status": "Buddy is now projected into your real-world space via AR.",
            "capabilities": ["spatial_awareness", "room_scale_presence", "gesture_response"],
        }

    def enter_vr_mode(self) -> dict:
        """Switch avatar to full Virtual Reality presence."""
        self.environment = AvatarEnvironment.VR
        return {
            "mode": "vr",
            "status": "Buddy is now your fully immersive VR companion.",
            "capabilities": [
                "full_body_presence", "spatial_audio", "interactive_environment",
                "hand_tracking", "gaze_tracking",
            ],
        }

    def enter_holographic_mode(self) -> dict:
        """
        Activate holographic projection API for physical room presence.
        Requires ENTERPRISE tier — enforced by BuddyBot.
        """
        self.environment = AvatarEnvironment.HOLOGRAPHIC
        return {
            "mode": "holographic",
            "status": (
                "Buddy is now available as a holographic projection. "
                "Connect to compatible holographic display hardware."
            ),
            "capabilities": [
                "room_scale_hologram", "360_degree_visibility",
                "physical_gesture_mirroring", "ambient_lighting_integration",
            ],
            "hardware_requirements": [
                "Microsoft HoloLens 2+", "Magic Leap 2",
                "Looking Glass Portrait", "custom_dreamco_holo_unit",
            ],
        }

    # ------------------------------------------------------------------
    # Appearance customisation
    # ------------------------------------------------------------------

    def customise_appearance(self, **kwargs) -> AvatarAppearance:
        """
        Update Buddy's visual appearance.

        Accepted keyword arguments: ``face_preset``, ``skin_tone``,
        ``hair_style``, ``hair_color``, ``eye_color``, ``clothing_style``,
        ``accessories``.
        """
        allowed = {
            "face_preset", "skin_tone", "hair_style", "hair_color",
            "eye_color", "clothing_style", "accessories",
        }
        for key, value in kwargs.items():
            if key not in allowed:
                raise AvatarEngineError(f"Appearance field '{key}' is not customisable.")
            setattr(self.appearance, key, value)
        return self.appearance

    # ------------------------------------------------------------------
    # Consent-gated Digital Twin / GAN Mimicry
    # ------------------------------------------------------------------

    def request_digital_twin_consent(self, user_id: str) -> str:
        """
        Generate the consent request text for Digital Twin mode.
        The user must explicitly call ``grant_consent`` with this text to activate.
        """
        return (
            f"CONSENT REQUIRED — Digital Twin Mode\n"
            f"User ID: {user_id}\n"
            f"You are granting Buddy Bot permission to create a digital replica of your visual "
            f"appearance using GAN-based image synthesis. This replica will ONLY be used within "
            f"your private Buddy Bot session and will NOT be shared with third parties without "
            f"your further explicit consent. You may revoke this permission at any time by "
            f"calling revoke_consent(user_id, 'digital_twin').\n"
            f"To confirm, pass this exact text to grant_consent()."
        )

    def grant_consent(self, user_id: str, feature: str, consent_text: str) -> ConsentRecord:
        """
        Record explicit user consent for a sensitive feature.

        Parameters
        ----------
        user_id : str
            The consenting user.
        feature : str
            Feature being consented to (e.g. ``"digital_twin"``, ``"voice_clone"``).
        consent_text : str
            The full consent text that was presented to and accepted by the user.

        Returns
        -------
        ConsentRecord
        """
        import time as _time
        record = ConsentRecord(
            user_id=user_id,
            feature=feature,
            granted=True,
            timestamp=_time.time(),
            consent_text=consent_text,
        )
        self._consent_records = [
            r for r in self._consent_records
            if not (r.user_id == user_id and r.feature == feature)
        ]
        self._consent_records.append(record)
        return record

    def revoke_consent(self, user_id: str, feature: str) -> None:
        """Revoke previously granted consent for a feature."""
        self._consent_records = [
            r for r in self._consent_records
            if not (r.user_id == user_id and r.feature == feature)
        ]

    def has_consent(self, user_id: str, feature: str) -> bool:
        """Return True if the user has active consent for *feature*."""
        return any(
            r.user_id == user_id and r.feature == feature and r.granted
            for r in self._consent_records
        )

    def create_digital_twin(self, user_id: str, image_data_reference: str) -> dict:
        """
        Create a GAN-powered digital twin avatar.
        Requires prior consent via ``grant_consent(user_id, 'digital_twin', ...)``.

        Parameters
        ----------
        user_id : str
            User whose appearance is being replicated.
        image_data_reference : str
            Reference identifier for the consented image data.

        Returns
        -------
        dict
        """
        if not self.has_consent(user_id, "digital_twin"):
            raise AvatarEngineError(
                "Digital Twin creation requires explicit user consent. "
                "Call request_digital_twin_consent() and grant_consent() first."
            )
        return {
            "status": "digital_twin_created",
            "user_id": user_id,
            "image_data_reference": image_data_reference,
            "model": "StyleGAN3 / DreamCo-GAN",
            "disclaimer": "This digital twin is for private use only. AI-generated.",
            "consent_verified": True,
        }

    # ------------------------------------------------------------------
    # History / status
    # ------------------------------------------------------------------

    def get_frame_history(self) -> list[dict]:
        """Return the list of rendered frames as dicts."""
        return [f.to_dict() for f in self._frame_history]

    def get_consent_records(self) -> list[dict]:
        """Return all consent records as dicts."""
        return [r.to_dict() for r in self._consent_records]

    def to_dict(self) -> dict:
        """Return engine status as a dict."""
        return {
            "avatar_type": self.avatar_type.value,
            "environment": self.environment.value,
            "appearance": self.appearance.to_dict(),
            "frames_rendered": len(self._frame_history),
            "consent_records": len(self._consent_records),
        }
