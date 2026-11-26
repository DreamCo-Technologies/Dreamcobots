from datetime import datetime, timedelta, timezone

import pytest

from buddy.learning.srs.store import IdempotencyConflictError, SRSStore

T0 = datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc)


def event(event_id="evt-1", reviewed_at=T0, due_at=T0 + timedelta(days=1)):
    return {
        "event_id": event_id, "learner_id": "learner-1", "deck_id": "bootcamp",
        "item_id": "python-functions", "division_ids": ["DreamEducation", "CommandCore"],
        "scheduler_name": "fsrs", "scheduler_version": "FSRS-6/py-fsrs-6.3.3",
        "rating": 3, "reviewed_at_utc": reviewed_at.isoformat(), "due_at_utc": due_at.isoformat(),
        "prior_state": {"state": 1}, "resulting_state": {"state": 2},
        "predicted_retrievability": 0.82, "actual_recall": True,
        "desired_retention": 0.9, "parameter_set_id": "params-v1", "provenance": {"source": "offline"},
    }


def test_review_history_is_append_only_and_sync_is_idempotent(tmp_path):
    store = SRSStore(tmp_path / "srs.db")
    first = event()
    assert store.record_review(first).status == "inserted"
    assert store.record_review(first).status == "duplicate"
    assert len(store.list_review_events("learner-1", "bootcamp", "python-functions")) == 1
    with pytest.raises(IdempotencyConflictError):
        store.record_review({**first, "rating": 1})
    import sqlite3
    with sqlite3.connect(tmp_path / "srs.db") as conn:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            conn.execute("UPDATE srs_review_events SET rating=1 WHERE event_id='evt-1'")


def test_offline_out_of_order_event_requests_replay_without_rewinding_state(tmp_path):
    store = SRSStore(tmp_path / "srs.db")
    later = event("evt-later", T0 + timedelta(days=2), T0 + timedelta(days=5))
    earlier = event("evt-earlier", T0 + timedelta(days=1), T0 + timedelta(days=3))
    assert store.record_review(later).state_updated is True
    result = store.record_review(earlier)
    assert result.replay_required is True
    state = store.get_card_state("learner-1", "bootcamp", "python-functions")
    assert state["latest_event_id"] == "evt-later"
    assert state["replay_required"] is True
    assert len(store.list_review_events("learner-1", "bootcamp", "python-functions")) == 2


def test_due_items_are_shared_across_division_memberships(tmp_path):
    store = SRSStore(tmp_path / "srs.db")
    store.record_review(event())
    assert len(store.due_items("learner-1", T0.isoformat(), "DreamEducation")) == 0
    due = store.due_items("learner-1", (T0 + timedelta(days=2)).isoformat(), "DreamEducation")
    assert len(due) == 1
    assert "CommandCore" in due[0]["division_ids"]


def test_mastery_evidence_is_separate_from_recall_events(tmp_path):
    store = SRSStore(tmp_path / "srs.db")
    store.record_review(event())
    evidence = {
        "evidence_id": "bench-evt-1", "learner_id": "learner-1", "deck_id": "bootcamp",
        "item_id": "python-functions", "division_ids": ["DreamEducation"],
        "benchmark_id": "python-functions-transfer-v1", "passed": True,
        "score": 0.95, "verified_at_utc": (T0 + timedelta(days=1)).isoformat(),
        "evidence": {"attempts": 2, "reviewer": "automated-benchmark"},
    }
    assert store.record_mastery_evidence(evidence) == "inserted"
    assert store.record_mastery_evidence(evidence) == "duplicate"
    assert len(store.list_review_events("learner-1", "bootcamp", "python-functions")) == 1
    assert len(store.list_mastery_evidence("learner-1", "bootcamp", "python-functions")) == 1


def test_same_timestamp_offline_events_use_event_id_tie_break(tmp_path):
    store = SRSStore(tmp_path / "srs.db")
    later_id = event("z-event", T0, T0 + timedelta(days=2))
    earlier_id = event("a-event", T0, T0 + timedelta(days=1))
    assert store.record_review(later_id).state_updated is True
    result = store.record_review(earlier_id)
    assert result.replay_required is True
    state = store.get_card_state("learner-1", "bootcamp", "python-functions")
    assert state["latest_event_id"] == "z-event"


def test_replay_required_is_exposed_as_a_real_boolean(tmp_path):
    store = SRSStore(tmp_path / "srs.db")
    store.record_review(event("later", T0 + timedelta(days=2), T0 + timedelta(days=5)))
    store.record_review(event("earlier", T0 + timedelta(days=1), T0 + timedelta(days=3)))
    state = store.get_card_state("learner-1", "bootcamp", "python-functions")
    assert state["replay_required"] is True
    due = store.due_items("learner-1", (T0 + timedelta(days=10)).isoformat())
    assert due == []
