"""
Temporary session database for the 211 Resource and Eligibility Checker Bot.

Sessions are stored in memory only and are purged after SESSION_TTL_SECONDS.
No personally-identifiable information is persisted to disk, in compliance
with HIPAA best-practice guidelines.

For production use, replace the in-memory store with an encrypted Redis
instance or Firebase Firestore with TTL policies configured.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import time
import uuid
from typing import Any, Optional

from config import SESSION_TTL_SECONDS


class SessionDatabase:
    """Lightweight in-memory session store with automatic TTL expiry."""

    def __init__(self, ttl: int = SESSION_TTL_SECONDS):
        self._store: dict[str, dict] = {}
        self._ttl = ttl

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_session(self) -> str:
        """Create a new session and return its unique ID."""
        session_id = str(uuid.uuid4())
        self._store[session_id] = {
            "_created_at": time.time(),
            "_last_active": time.time(),
        }
        return session_id

    def get(self, session_id: str, key: str, default: Any = None) -> Any:
        """Retrieve a value from a session."""
        self._evict_expired()
        session = self._store.get(session_id)
        if session is None:
            return default
        return session.get(key, default)

    def set(self, session_id: str, key: str, value: Any) -> None:
        """Set a value in a session, refreshing its TTL."""
        self._evict_expired()
        if session_id not in self._store:
            raise KeyError(f"Session '{session_id}' does not exist or has expired.")
        self._store[session_id][key] = value
        self._store[session_id]["_last_active"] = time.time()

    def get_session(self, session_id: str) -> Optional[dict]:
        """Return a shallow copy of the session data (without internal keys)."""
        self._evict_expired()
        session = self._store.get(session_id)
        if session is None:
            return None
        return {k: v for k, v in session.items() if not k.startswith("_")}

    def delete_session(self, session_id: str) -> None:
        """Explicitly delete a session (e.g., after the conversation ends)."""
        self._store.pop(session_id, None)

    def session_exists(self, session_id: str) -> bool:
        """Check whether a session is active."""
        self._evict_expired()
        return session_id in self._store

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _evict_expired(self) -> None:
        """Remove sessions that have exceeded their TTL."""
        now = time.time()
        expired = [
            sid
            for sid, data in self._store.items()
            if now - data.get("_last_active", 0) > self._ttl
        ]
        for sid in expired:
            del self._store[sid]
