"""
AR/VR Engine — Personalized Reality Integration for Buddy Omniscient Bot.

Provides:
  • Real-time AR overlays projected on any smart device for personalized
    recommendations (furnishing, car repair, augmented education, etc.)
  • Holographic bot projection for "life-sized AI assistants" using AR/VR
    headsets, smartphones, tablets, smart TVs, and game consoles.
  • Multi-platform broadcast of AR sessions (TV, phone, tablet, computer,
    smart TV, gaming console).

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import uuid

from framework import GlobalAISourcesFlow  # noqa: F401


class AROverlayType(Enum):
    REPAIR_GUIDE = "repair_guide"
    FURNITURE_PLACEMENT = "furniture_placement"
    EDUCATION = "education"
    NAVIGATION = "navigation"
    HEALTH_METRICS = "health_metrics"
    COOKING_GUIDE = "cooking_guide"
    BUSINESS_PLANNING = "business_planning"
    GAMING = "gaming"
    CREATIVE_DESIGN = "creative_design"
    CUSTOM = "custom"


class ProjectionDevice(Enum):
    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    SMART_TV = "smart_tv"
    COMPUTER = "computer"
    GAME_CONSOLE = "game_console"
    AR_GLASSES = "ar_glasses"
    VR_HEADSET = "vr_headset"
    HOLOGRAPHIC_DISPLAY = "holographic_display"


class HolographicMode(Enum):
    LIFE_SIZED = "life_sized"
    TABLE_TOP = "table_top"
    WALL_PROJECTION = "wall_projection"
    SPATIAL_AR = "spatial_ar"


@dataclass
class AROverlaySession:
    """Represents an active AR overlay session."""

    session_id: str
    overlay_type: AROverlayType
    device: ProjectionDevice
    context: str
    instructions: List[str]
    active: bool = True
    voice_guidance: bool = False
    hands_free_mode: bool = False

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "overlay_type": self.overlay_type.value,
            "device": self.device.value,
            "context": self.context,
            "instructions": self.instructions,
            "active": self.active,
            "voice_guidance": self.voice_guidance,
            "hands_free_mode": self.hands_free_mode,
        }


@dataclass
class HolographicSession:
    """Represents a holographic Buddy projection."""

    session_id: str
    mode: HolographicMode
    device: ProjectionDevice
    buddy_persona: str
    context: str
    active: bool = True

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "mode": self.mode.value,
            "device": self.device.value,
            "buddy_persona": self.buddy_persona,
            "context": self.context,
            "active": self.active,
        }


# ---------------------------------------------------------------------------
# AR instruction templates for common tasks
# ---------------------------------------------------------------------------

_AR_INSTRUCTION_TEMPLATES: dict = {
    AROverlayType.REPAIR_GUIDE: [
        "Step 1: Buddy scans the item and identifies components needing attention.",
        "Step 2: AR labels highlight each part with tool requirements.",
        "Step 3: Animated overlays show the correct repair sequence.",
        "Step 4: Real-time progress tracking confirms each step completion.",
        "Step 5: Buddy verifies the repair and suggests preventive maintenance.",
    ],
    AROverlayType.FURNITURE_PLACEMENT: [
        "Step 1: Buddy scans the room dimensions using your device camera.",
        "Step 2: AR furniture models are projected to scale in your space.",
        "Step 3: Adjust placement, color, and style with voice or touch.",
        "Step 4: Buddy evaluates traffic flow and ergonomics.",
        "Step 5: Share your design or order items directly through Buddy.",
    ],
    AROverlayType.EDUCATION: [
        "Step 1: Buddy identifies the subject from your environment or input.",
        "Step 2: AR overlays annotate real-world objects with learning data.",
        "Step 3: Interactive 3D models illustrate complex concepts.",
        "Step 4: Buddy quizzes you in real-time using your surroundings.",
        "Step 5: Progress is saved to your personalized learning path.",
    ],
    AROverlayType.COOKING_GUIDE: [
        "Step 1: Buddy identifies ingredients using your camera.",
        "Step 2: AR overlays display measurements and prep instructions.",
        "Step 3: Timer overlays sync with each cooking stage.",
        "Step 4: Buddy provides plating suggestions with visual guides.",
        "Step 5: Save and share your dish to the DreamCo community.",
    ],
    AROverlayType.BUSINESS_PLANNING: [
        "Step 1: Buddy projects a virtual business dashboard in your space.",
        "Step 2: AR charts display market data and opportunity analysis.",
        "Step 3: Interactive overlays let you model revenue scenarios.",
        "Step 4: Buddy guides you through setup checklist items.",
        "Step 5: Export your business plan to any device instantly.",
    ],
}


class ARVREngine:
    """
    AR/VR Engine for Buddy Omniscient Bot.

    Manages AR overlay sessions and holographic projections across all
    supported devices — smartphones, tablets, smart TVs, computers,
    game consoles, AR glasses, and VR headsets.
    """

    def __init__(self, max_sessions: Optional[int] = 5) -> None:
        self._max_sessions = max_sessions
        self._ar_sessions: dict[str, AROverlaySession] = {}
        self._holographic_sessions: dict[str, HolographicSession] = {}

    # ------------------------------------------------------------------
    # AR Overlay methods
    # ------------------------------------------------------------------

    def start_ar_overlay(
        self,
        overlay_type: AROverlayType,
        device: ProjectionDevice,
        context: str = "",
        voice_guidance: bool = False,
        hands_free_mode: bool = False,
    ) -> AROverlaySession:
        """Start a new AR overlay session on the specified device."""
        active_count = sum(1 for s in self._ar_sessions.values() if s.active)
        if self._max_sessions is not None and active_count >= self._max_sessions:
            raise RuntimeError(
                f"Maximum of {self._max_sessions} concurrent AR sessions reached. "
                "Upgrade your tier for more sessions."
            )
        session_id = f"AR-{uuid.uuid4().hex[:8].upper()}"
        instructions = _AR_INSTRUCTION_TEMPLATES.get(
            overlay_type,
            ["Buddy is generating custom AR instructions for your task."],
        )
        session = AROverlaySession(
            session_id=session_id,
            overlay_type=overlay_type,
            device=device,
            context=context or f"{overlay_type.value} guidance",
            instructions=instructions,
            voice_guidance=voice_guidance,
            hands_free_mode=hands_free_mode,
        )
        self._ar_sessions[session_id] = session
        return session

    def stop_ar_overlay(self, session_id: str) -> bool:
        """Stop an active AR overlay session."""
        session = self._ar_sessions.get(session_id)
        if session and session.active:
            session.active = False
            return True
        return False

    def list_ar_sessions(self, active_only: bool = False) -> List[AROverlaySession]:
        sessions = list(self._ar_sessions.values())
        if active_only:
            sessions = [s for s in sessions if s.active]
        return sessions

    # ------------------------------------------------------------------
    # Holographic Projection methods
    # ------------------------------------------------------------------

    def project_holographic_buddy(
        self,
        device: ProjectionDevice,
        mode: HolographicMode = HolographicMode.LIFE_SIZED,
        buddy_persona: str = "Buddy",
        context: str = "",
    ) -> HolographicSession:
        """Project a holographic Buddy assistant on the specified device."""
        session_id = f"HOLO-{uuid.uuid4().hex[:8].upper()}"
        session = HolographicSession(
            session_id=session_id,
            mode=mode,
            device=device,
            buddy_persona=buddy_persona,
            context=context or "Holographic Buddy assistant ready.",
            active=True,
        )
        self._holographic_sessions[session_id] = session
        return session

    def stop_holographic_session(self, session_id: str) -> bool:
        """Stop a holographic session."""
        session = self._holographic_sessions.get(session_id)
        if session and session.active:
            session.active = False
            return True
        return False

    def list_holographic_sessions(self, active_only: bool = False) -> List[HolographicSession]:
        sessions = list(self._holographic_sessions.values())
        if active_only:
            sessions = [s for s in sessions if s.active]
        return sessions

    # ------------------------------------------------------------------
    # Broadcast methods
    # ------------------------------------------------------------------

    def broadcast_to_devices(
        self,
        session_id: str,
        target_devices: List[ProjectionDevice],
    ) -> dict:
        """Broadcast an active AR session to multiple devices simultaneously."""
        session = self._ar_sessions.get(session_id)
        if not session:
            return {"error": f"Session '{session_id}' not found."}
        if not session.active:
            return {"error": f"Session '{session_id}' is not active."}
        return {
            "session_id": session_id,
            "broadcast_to": [d.value for d in target_devices],
            "status": "broadcasting",
            "message": (
                f"AR session '{session_id}' is now broadcasting to "
                f"{len(target_devices)} device(s)."
            ),
        }

    def get_supported_devices(self) -> List[str]:
        """Return a list of all supported projection devices."""
        return [d.value for d in ProjectionDevice]

    def count_active_ar_sessions(self) -> int:
        return sum(1 for s in self._ar_sessions.values() if s.active)

    def count_active_holographic_sessions(self) -> int:
        return sum(1 for s in self._holographic_sessions.values() if s.active)
