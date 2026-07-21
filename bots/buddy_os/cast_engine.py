"""
Buddy OS — Cast Engine

Enables sending and casting content to external screens via:
  - Google Cast (Chromecast, Android TV, Google TV)
  - Apple AirPlay (Apple TV, AirPlay 2 receivers)
  - Miracast (Windows, Android wireless display)
  - HDMI / DisplayPort (wired, via HDMI-CEC commands)

Each protocol is represented as a CastProtocol.  The engine discovers
receivers, establishes a cast session, and controls playback.

GLOBAL AI SOURCES FLOW: participates via buddy_os.py pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class CastProtocol(Enum):
    GOOGLE_CAST = "google_cast"
    AIRPLAY = "airplay"
    MIRACAST = "miracast"
    HDMI = "hdmi"
    DLNA = "dlna"


class CastState(Enum):
    IDLE = "idle"
    CONNECTING = "connecting"
    CASTING = "casting"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class ContentType(Enum):
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    SCREEN_MIRROR = "screen_mirror"
    PRESENTATION = "presentation"
    DASHBOARD = "dashboard"


@dataclass
class CastReceiver:
    """Represents a discovered cast-capable screen or device."""

    receiver_id: str
    name: str
    protocol: CastProtocol
    ip_address: str = ""
    port: int = 0
    state: CastState = CastState.IDLE
    volume: float = 0.5
    metadata: dict = field(default_factory=dict)

    def is_active(self) -> bool:
        return self.state in (CastState.CASTING, CastState.PAUSED)

    def to_dict(self) -> dict:
        return {
            "receiver_id": self.receiver_id,
            "name": self.name,
            "protocol": self.protocol.value,
            "ip_address": self.ip_address,
            "port": self.port,
            "state": self.state.value,
            "volume": self.volume,
        }


@dataclass
class CastSession:
    """An active or completed cast session."""

    session_id: str
    receiver_id: str
    content_type: ContentType
    content_url: str
    state: CastState = CastState.CASTING
    position_seconds: float = 0.0
    duration_seconds: float = 0.0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "receiver_id": self.receiver_id,
            "content_type": self.content_type.value,
            "content_url": self.content_url,
            "state": self.state.value,
            "position_seconds": self.position_seconds,
            "duration_seconds": self.duration_seconds,
        }


class CastEngine:
    """
    Buddy OS Cast subsystem.

    Discovers cast receivers, establishes sessions, and controls playback
    across Google Cast, Apple AirPlay, Miracast, and HDMI targets.
    """

    def __init__(self, max_targets: Optional[int] = None) -> None:
        self._receivers: dict[str, CastReceiver] = {}
        self._sessions: dict[str, CastSession] = {}
        self._receiver_counter: int = 0
        self._session_counter: int = 0
        self._max_targets = max_targets

    # ------------------------------------------------------------------
    # Receiver discovery
    # ------------------------------------------------------------------

    def add_receiver(
        self,
        name: str,
        protocol: CastProtocol,
        ip_address: str = "",
        port: int = 0,
        metadata: Optional[dict] = None,
    ) -> CastReceiver:
        """Register a cast receiver (discovered on the local network or wired)."""
        if self._max_targets is not None and len(self._receivers) >= self._max_targets:
            raise RuntimeError(
                f"Cast target limit of {self._max_targets} reached. Upgrade your tier."
            )
        self._receiver_counter += 1
        receiver_id = f"recv_{self._receiver_counter:04d}"
        receiver = CastReceiver(
            receiver_id=receiver_id,
            name=name,
            protocol=protocol,
            ip_address=ip_address,
            port=port,
            metadata=dict(metadata or {}),
        )
        self._receivers[receiver_id] = receiver
        return receiver

    def remove_receiver(self, receiver_id: str) -> None:
        """Remove a cast receiver."""
        self._receivers.pop(receiver_id, None)

    def list_receivers(
        self, protocol: Optional[CastProtocol] = None
    ) -> list[CastReceiver]:
        """Return all known receivers, optionally filtered by protocol."""
        receivers = list(self._receivers.values())
        if protocol is not None:
            receivers = [r for r in receivers if r.protocol == protocol]
        return receivers

    # ------------------------------------------------------------------
    # Cast sessions
    # ------------------------------------------------------------------

    def start_cast(
        self,
        receiver_id: str,
        content_type: ContentType,
        content_url: str,
        duration_seconds: float = 0.0,
        metadata: Optional[dict] = None,
    ) -> CastSession:
        """Begin casting content to a receiver."""
        receiver = self._get_receiver(receiver_id)
        receiver.state = CastState.CASTING
        self._session_counter += 1
        session_id = f"sess_{self._session_counter:04d}"
        session = CastSession(
            session_id=session_id,
            receiver_id=receiver_id,
            content_type=content_type,
            content_url=content_url,
            state=CastState.CASTING,
            duration_seconds=duration_seconds,
            metadata=dict(metadata or {}),
        )
        self._sessions[session_id] = session
        return session

    def pause_cast(self, session_id: str) -> CastSession:
        """Pause an active cast session."""
        session = self._get_session(session_id)
        session.state = CastState.PAUSED
        self._receivers[session.receiver_id].state = CastState.PAUSED
        return session

    def resume_cast(self, session_id: str) -> CastSession:
        """Resume a paused cast session."""
        session = self._get_session(session_id)
        session.state = CastState.CASTING
        self._receivers[session.receiver_id].state = CastState.CASTING
        return session

    def stop_cast(self, session_id: str) -> CastSession:
        """Stop a cast session."""
        session = self._get_session(session_id)
        session.state = CastState.STOPPED
        self._receivers[session.receiver_id].state = CastState.IDLE
        return session

    def seek(self, session_id: str, position_seconds: float) -> CastSession:
        """Seek to a position in the current content."""
        session = self._get_session(session_id)
        if session.duration_seconds > 0:
            position_seconds = max(0.0, min(position_seconds, session.duration_seconds))
        session.position_seconds = position_seconds
        return session

    def set_volume(self, receiver_id: str, volume: float) -> CastReceiver:
        """Set the volume on a receiver (0.0 – 1.0)."""
        receiver = self._get_receiver(receiver_id)
        receiver.volume = max(0.0, min(1.0, volume))
        return receiver

    def get_session(self, session_id: str) -> CastSession:
        return self._get_session(session_id)

    def list_sessions(self, active_only: bool = False) -> list[CastSession]:
        """Return sessions, optionally limited to active ones."""
        sessions = list(self._sessions.values())
        if active_only:
            sessions = [s for s in sessions if s.state == CastState.CASTING]
        return sessions

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_receiver(self, receiver_id: str) -> CastReceiver:
        if receiver_id not in self._receivers:
            raise KeyError(f"Receiver '{receiver_id}' not found.")
        return self._receivers[receiver_id]

    def _get_session(self, session_id: str) -> CastSession:
        if session_id not in self._sessions:
            raise KeyError(f"Session '{session_id}' not found.")
        return self._sessions[session_id]
