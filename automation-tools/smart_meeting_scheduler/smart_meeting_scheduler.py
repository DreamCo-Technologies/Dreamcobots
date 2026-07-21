# GLOBAL AI SOURCES FLOW
"""Smart Meeting Scheduler - intelligent meeting scheduling and conflict detection."""
import sys
import os
import importlib.util
_TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_TOOL_DIR, '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from framework import GlobalAISourcesFlow  # noqa: F401
# Load local tiers.py by path to avoid sys.modules conflicts with other tiers modules
from datetime import datetime, timedelta

_tiers_spec = importlib.util.spec_from_file_location('_local_tiers', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS


class SmartMeetingScheduler:
    """Intelligent meeting scheduler with conflict detection and timezone support."""

    SLOT_DURATION_MINUTES = 30

    def __init__(self, tier: str = "free"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["free"])
        self._meetings: list[dict] = []
        self._meeting_count = 0
        self._monthly_limit = 5 if tier == "free" else None

    def _check_limit(self):
        if self._monthly_limit and self._meeting_count >= self._monthly_limit:
            raise PermissionError(f"Monthly meeting limit ({self._monthly_limit}) reached. Upgrade to Pro.")

    def _has_conflict(self, start: datetime, end: datetime) -> bool:
        for meeting in self._meetings:
            m_start = meeting["start"]
            m_end = meeting["end"]
            if not (end <= m_start or start >= m_end):
                return True
        return False

    def schedule_meeting(self, title: str, start_iso: str, duration_minutes: int, attendees: list) -> dict:
        """Schedule a meeting, checking for conflicts."""
        self._check_limit()
        start = datetime.fromisoformat(start_iso)
        end = start + timedelta(minutes=duration_minutes)
        if self._has_conflict(start, end):
            return {
                "status": "conflict",
                "message": f"Time slot {start_iso} conflicts with an existing meeting.",
                "title": title,
            }
        meeting = {
            "id": f"mtg_{len(self._meetings) + 1:04d}",
            "title": title,
            "start": start,
            "end": end,
            "duration_minutes": duration_minutes,
            "attendees": attendees,
            "tier": self.tier,
        }
        self._meetings.append(meeting)
        self._meeting_count += 1
        return {
            "status": "scheduled",
            "id": meeting["id"],
            "title": title,
            "start": start_iso,
            "end": end.isoformat(),
            "attendees": attendees,
        }

    def find_next_available(self, after_iso: str, duration_minutes: int = 30) -> str:
        """Find the next available slot after a given datetime."""
        candidate = datetime.fromisoformat(after_iso)
        for _ in range(100):
            end = candidate + timedelta(minutes=duration_minutes)
            if not self._has_conflict(candidate, end):
                return candidate.isoformat()
            candidate += timedelta(minutes=self.SLOT_DURATION_MINUTES)
        return (datetime.fromisoformat(after_iso) + timedelta(days=1)).isoformat()

    def list_meetings(self) -> list:
        """Return all scheduled meetings."""
        return [
            {
                "id": m["id"],
                "title": m["title"],
                "start": m["start"].isoformat(),
                "end": m["end"].isoformat(),
                "attendees": m["attendees"],
            }
            for m in self._meetings
        ]
