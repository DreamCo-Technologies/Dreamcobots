"""
Buddy Teach Bot — Broadcast Engine

Delivers teaching content to any smart device or screen:
  - Smart TV (Samsung Tizen, LG webOS, Android TV, Roku)
  - Game Consoles (PlayStation, Xbox, Nintendo Switch)
  - Phones & Tablets (iOS, Android)
  - Computers (Windows, macOS, Linux, Chromebook)
  - Smart Home Displays (Echo Show, Google Nest Hub)
  - AR/VR Headsets (Meta Quest, Apple Vision Pro, HoloLens)

Each target is represented as a BroadcastTarget.  The engine queues
lessons, manages live sessions, and tracks engagement per device.
All logic is deterministic so there are no external dependencies at runtime.
"""

from __future__ import annotations

import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  — GLOBAL AI SOURCES FLOW


class DeviceCategory(Enum):
    SMART_TV = "smart_tv"
    GAME_CONSOLE = "game_console"
    PHONE = "phone"
    TABLET = "tablet"
    COMPUTER = "computer"
    SMART_DISPLAY = "smart_display"
    AR_VR_HEADSET = "ar_vr_headset"
    STREAMING_STICK = "streaming_stick"


class BroadcastState(Enum):
    IDLE = "idle"
    CONNECTING = "connecting"
    LIVE = "live"
    PAUSED = "paused"
    ENDED = "ended"
    ERROR = "error"


class ContentFormat(Enum):
    VIDEO_TUTORIAL = "video_tutorial"
    INTERACTIVE_LESSON = "interactive_lesson"
    AR_OVERLAY = "ar_overlay"
    LIVE_DEMO = "live_demo"
    QUIZ = "quiz"
    STEP_BY_STEP = "step_by_step"


@dataclass
class BroadcastTarget:
    """Represents a connected device that can receive broadcast content."""

    target_id: str
    name: str
    category: DeviceCategory
    platform: str = ""          # e.g. "Android TV", "PlayStation 5"
    ip_address: str = ""
    state: BroadcastState = BroadcastState.IDLE
    volume: float = 0.8
    ar_capable: bool = False
    metadata: dict = field(default_factory=dict)

    def is_active(self) -> bool:
        return self.state in (BroadcastState.LIVE, BroadcastState.PAUSED)

    def to_dict(self) -> dict:
        return {
            "target_id": self.target_id,
            "name": self.name,
            "category": self.category.value,
            "platform": self.platform,
            "ip_address": self.ip_address,
            "state": self.state.value,
            "volume": self.volume,
            "ar_capable": self.ar_capable,
        }


@dataclass
class BroadcastSession:
    """An active or completed broadcast session."""

    session_id: str
    target_ids: list[str]
    lesson_title: str
    content_format: ContentFormat
    content_url: str = ""
    state: BroadcastState = BroadcastState.LIVE
    started_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None
    viewer_count: int = 0
    engagement_score: float = 0.0
    metadata: dict = field(default_factory=dict)

    def duration_seconds(self) -> float:
        end = self.ended_at or time.time()
        return end - self.started_at

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "target_ids": self.target_ids,
            "lesson_title": self.lesson_title,
            "content_format": self.content_format.value,
            "content_url": self.content_url,
            "state": self.state.value,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "viewer_count": self.viewer_count,
            "engagement_score": self.engagement_score,
        }


class BroadcastEngineError(Exception):
    """Raised when a broadcast operation fails."""


class BroadcastEngine:
    """
    Multi-platform broadcast engine.

    Manages device registration, session creation, and content delivery
    to any combination of smart devices.
    """

    def __init__(self, max_targets: Optional[int] = 1) -> None:
        self.max_targets = max_targets
        self._targets: dict[str, BroadcastTarget] = {}
        self._sessions: dict[str, BroadcastSession] = {}
        self._session_history: list[BroadcastSession] = []

    # ------------------------------------------------------------------
    # Device management
    # ------------------------------------------------------------------

    def register_target(
        self,
        name: str,
        category: DeviceCategory,
        platform: str = "",
        ip_address: str = "",
        ar_capable: bool = False,
        metadata: Optional[dict] = None,
    ) -> BroadcastTarget:
        """Register a new broadcast target device."""
        if self.max_targets is not None and len(self._targets) >= self.max_targets:
            raise BroadcastEngineError(
                f"Maximum broadcast targets ({self.max_targets}) reached. "
                "Upgrade your tier to add more devices."
            )
        target_id = str(uuid.uuid4())
        target = BroadcastTarget(
            target_id=target_id,
            name=name,
            category=category,
            platform=platform,
            ip_address=ip_address,
            ar_capable=ar_capable,
            metadata=metadata or {},
        )
        self._targets[target_id] = target
        return target

    def remove_target(self, target_id: str) -> None:
        """Remove a registered broadcast target."""
        if target_id not in self._targets:
            raise BroadcastEngineError(f"Target '{target_id}' not found.")
        del self._targets[target_id]

    def list_targets(self) -> list[BroadcastTarget]:
        return list(self._targets.values())

    def get_target(self, target_id: str) -> BroadcastTarget:
        if target_id not in self._targets:
            raise BroadcastEngineError(f"Target '{target_id}' not found.")
        return self._targets[target_id]

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def start_broadcast(
        self,
        lesson_title: str,
        content_format: ContentFormat,
        target_ids: list[str],
        content_url: str = "",
        metadata: Optional[dict] = None,
    ) -> BroadcastSession:
        """Start a broadcast session to one or more targets."""
        for tid in target_ids:
            if tid not in self._targets:
                raise BroadcastEngineError(f"Target '{tid}' not registered.")

        session_id = str(uuid.uuid4())
        session = BroadcastSession(
            session_id=session_id,
            target_ids=list(target_ids),
            lesson_title=lesson_title,
            content_format=content_format,
            content_url=content_url,
            state=BroadcastState.LIVE,
            viewer_count=len(target_ids),
            metadata=metadata or {},
        )
        self._sessions[session_id] = session

        # Update device states
        for tid in target_ids:
            self._targets[tid].state = BroadcastState.LIVE

        return session

    def pause_broadcast(self, session_id: str) -> BroadcastSession:
        session = self._get_session(session_id)
        if session.state != BroadcastState.LIVE:
            raise BroadcastEngineError(
                f"Session '{session_id}' is not live (state: {session.state.value})."
            )
        session.state = BroadcastState.PAUSED
        for tid in session.target_ids:
            if tid in self._targets:
                self._targets[tid].state = BroadcastState.PAUSED
        return session

    def resume_broadcast(self, session_id: str) -> BroadcastSession:
        session = self._get_session(session_id)
        if session.state != BroadcastState.PAUSED:
            raise BroadcastEngineError(
                f"Session '{session_id}' is not paused (state: {session.state.value})."
            )
        session.state = BroadcastState.LIVE
        for tid in session.target_ids:
            if tid in self._targets:
                self._targets[tid].state = BroadcastState.LIVE
        return session

    def end_broadcast(self, session_id: str) -> BroadcastSession:
        session = self._get_session(session_id)
        session.state = BroadcastState.ENDED
        session.ended_at = time.time()
        for tid in session.target_ids:
            if tid in self._targets:
                self._targets[tid].state = BroadcastState.IDLE
        self._session_history.append(session)
        del self._sessions[session_id]
        return session

    def update_engagement(self, session_id: str, score: float) -> None:
        """Update the engagement score for an active session (0.0–1.0)."""
        session = self._get_session(session_id)
        session.engagement_score = max(0.0, min(1.0, score))

    def active_sessions(self) -> list[BroadcastSession]:
        return list(self._sessions.values())

    def session_history(self) -> list[BroadcastSession]:
        return list(self._session_history)

    def _get_session(self, session_id: str) -> BroadcastSession:
        if session_id not in self._sessions:
            raise BroadcastEngineError(f"Session '{session_id}' not found.")
        return self._sessions[session_id]

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def broadcast_to_all(
        self,
        lesson_title: str,
        content_format: ContentFormat,
        content_url: str = "",
    ) -> BroadcastSession:
        """Start a broadcast to every registered target."""
        if not self._targets:
            raise BroadcastEngineError("No broadcast targets registered.")
        return self.start_broadcast(
            lesson_title=lesson_title,
            content_format=content_format,
            target_ids=list(self._targets.keys()),
            content_url=content_url,
        )

    def get_device_summary(self) -> dict:
        """Return a count of devices grouped by category."""
        summary: dict[str, int] = {}
        for target in self._targets.values():
            key = target.category.value
            summary[key] = summary.get(key, 0) + 1
        return summary
