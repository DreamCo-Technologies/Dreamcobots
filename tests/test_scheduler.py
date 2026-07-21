"""Tests for Scheduler."""

import time
import pytest
from BuddyAI.scheduler import Scheduler


@pytest.fixture
def scheduler():
    s = Scheduler()
    s.start()
    yield s
    s.stop()


def test_schedule_and_fire(scheduler):
    results = []
    scheduler.schedule_task("test", lambda: results.append(1), delay=0.05)
    time.sleep(0.3)
    assert results == [1]


def test_cancel_task(scheduler):
    results = []
    task_id = scheduler.schedule_task("test", lambda: results.append(1), delay=0.5)
    cancelled = scheduler.cancel_task(task_id)
    assert cancelled is True
    time.sleep(0.7)
    assert results == []


def test_get_upcoming(scheduler):
    scheduler.schedule_task("task1", lambda: None, delay=10)
    scheduler.schedule_task("task2", lambda: None, delay=20)
    upcoming = scheduler.get_upcoming()
    names = [t["name"] for t in upcoming]
    assert "task1" in names
    assert "task2" in names


def test_cancel_nonexistent_task(scheduler):
    result = scheduler.cancel_task("nonexistent-id")
    assert result is False


def test_recurring_task(scheduler):
    results = []
    scheduler.schedule_task(
        "recurring",
        lambda: results.append(1),
        delay=0.05,
        recurring=True,
        interval=0.1,
    )
    time.sleep(0.5)
    # Should have fired multiple times
    assert len(results) >= 2


def test_get_upcoming_empty(scheduler):
    assert scheduler.get_upcoming() == []
