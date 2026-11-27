from datetime import datetime, timedelta, timezone

from buddy.learning.srs.fsrs import FSRSAdapter
from buddy.learning.srs.service import BuddySRSService
from buddy.learning.srs.store import SRSStore

T0 = datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc)


def test_shared_service_routes_one_schedule_across_divisions_and_retries(tmp_path):
    service = BuddySRSService(SRSStore(tmp_path / "srs.db"))
    first = service.review_fsrs(
        event_id="event-1", learner_id="learner", deck_id="foundation",
        item_id="python-functions", division_ids=["DreamEducation", "CommandCore"],
        rating="Good", reviewed_at=T0,
    )
    assert first["status"] == "inserted"
    retry = service.review_fsrs(
        event_id="event-1", learner_id="learner", deck_id="foundation",
        item_id="python-functions", division_ids=["DreamEducation", "CommandCore"],
        rating="Good", reviewed_at=T0,
    )
    assert retry["status"] == "duplicate"
    due = service.due_items("learner", (T0 + timedelta(days=3)).isoformat(), "CommandCore")
    assert len(due) == 1
    assert "DreamEducation" in due[0]["division_ids"]


def test_out_of_order_offline_events_replay_to_a_consistent_state(tmp_path):
    store = SRSStore(tmp_path / "srs.db")
    service = BuddySRSService(store)
    later = service.review_fsrs(
        event_id="later", learner_id="learner", deck_id="d", item_id="i",
        division_ids=["DreamEducation"], rating="Good", reviewed_at=T0 + timedelta(days=2),
    )
    assert later["status"] == "inserted"
    adapter = FSRSAdapter()
    older = adapter.review(
        learner_id="learner", deck_id="d", item_id="i",
        rating="Again", reviewed_at=T0 + timedelta(days=1),
    )
    offline_event = {
        "event_id": "older", "learner_id": "learner", "deck_id": "d", "item_id": "i",
        "division_ids": ["DreamEducation"], "scheduler_name": older.scheduler,
        "scheduler_version": older.scheduler_version, "rating": older.rating,
        "reviewed_at_utc": older.reviewed_at_utc, "due_at_utc": older.due_at_utc,
        "prior_state": older.prior_state, "resulting_state": older.resulting_state,
        "predicted_retrievability": older.predicted_retrievability,
        "actual_recall": older.actual_recall, "desired_retention": older.desired_retention,
        "parameter_set_id": older.parameter_set_id, "scheduler_config": older.scheduler_config,
        "provenance": {"offline": True},
    }
    sync = service.sync_offline_event(offline_event)
    assert sync["replay_required"] is True
    rebuilt = service.rebuild_card_state("learner", "d", "i")
    assert rebuilt["replay_required"] is False
    assert rebuilt["latest_event_id"] == "later"
    assert len(store.list_review_events("learner", "d", "i")) == 2


def test_mastery_is_never_awarded_by_a_review(tmp_path):
    service = BuddySRSService(SRSStore(tmp_path / "srs.db"))
    review = service.review_fsrs(
        event_id="recall", learner_id="learner", deck_id="d", item_id="i",
        division_ids=["DreamEducation"], rating="Easy", reviewed_at=T0,
    )
    assert review["review"]["mastery_awarded"] is False
    evidence = {
        "evidence_id": "benchmark-1", "learner_id": "learner", "deck_id": "d",
        "item_id": "i", "division_ids": ["DreamEducation"], "benchmark_id": "transfer-v1",
        "passed": True, "score": 0.94, "verified_at_utc": (T0 + timedelta(days=1)).isoformat(),
        "evidence": {"attempt": 1},
    }
    assert service.record_mastery_evidence(evidence) == "inserted"
