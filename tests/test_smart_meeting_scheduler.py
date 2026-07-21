import sys, os
REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, REPO_ROOT)

TOOL_DIR = os.path.join(REPO_ROOT, 'automation-tools', 'smart_meeting_scheduler')
sys.path.insert(0, TOOL_DIR)

import pytest
from smart_meeting_scheduler import SmartMeetingScheduler


class TestSmartMeetingSchedulerInstantiation:
    def test_default_tier_is_free(self):
        s = SmartMeetingScheduler()
        assert s.tier == "free"

    def test_pro_tier(self):
        s = SmartMeetingScheduler(tier="pro")
        assert s.tier == "pro"


class TestScheduleMeeting:
    def test_schedule_success(self):
        s = SmartMeetingScheduler(tier="pro")
        result = s.schedule_meeting("Standup", "2025-06-01T09:00:00", 30, ["a@b.com"])
        assert result["status"] == "scheduled"
        assert result["id"].startswith("mtg_")

    def test_conflict_detected(self):
        s = SmartMeetingScheduler(tier="pro")
        s.schedule_meeting("First", "2025-06-01T09:00:00", 60, ["a@b.com"])
        result = s.schedule_meeting("Second", "2025-06-01T09:30:00", 30, ["b@c.com"])
        assert result["status"] == "conflict"

    def test_free_tier_monthly_limit(self):
        s = SmartMeetingScheduler(tier="free")
        for i in range(5):
            s.schedule_meeting(f"M{i}", f"2025-06-0{i+1}T09:00:00", 30, [])
        with pytest.raises(PermissionError):
            s.schedule_meeting("Extra", "2025-06-10T09:00:00", 30, [])

    def test_no_conflict_different_times(self):
        s = SmartMeetingScheduler(tier="pro")
        s.schedule_meeting("AM", "2025-06-01T09:00:00", 30, [])
        result = s.schedule_meeting("PM", "2025-06-01T14:00:00", 30, [])
        assert result["status"] == "scheduled"


class TestFindNextAvailable:
    def test_returns_iso_string(self):
        s = SmartMeetingScheduler(tier="pro")
        slot = s.find_next_available("2025-06-01T09:00:00", 30)
        assert "T" in slot

    def test_avoids_conflict(self):
        s = SmartMeetingScheduler(tier="pro")
        s.schedule_meeting("Block", "2025-06-01T09:00:00", 60, [])
        slot = s.find_next_available("2025-06-01T09:00:00", 30)
        assert slot != "2025-06-01T09:00:00"


class TestListMeetings:
    def test_empty_initially(self):
        s = SmartMeetingScheduler(tier="pro")
        assert s.list_meetings() == []

    def test_returns_scheduled_meetings(self):
        s = SmartMeetingScheduler(tier="pro")
        s.schedule_meeting("A", "2025-06-01T10:00:00", 30, [])
        meetings = s.list_meetings()
        assert len(meetings) == 1
        assert meetings[0]["title"] == "A"
