from datetime import datetime, timedelta, timezone

import pytest

from buddy.learning.srs.fsrs import FSRSAdapter, FSRSConfig, stable_fsrs_card_id

T0 = datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc)


def test_fsrs_uses_pinned_fsrs6_adapter_and_configurable_retention():
    adapter = FSRSAdapter(FSRSConfig(desired_retention=0.88, enable_fuzzing=False))
    result = adapter.review(
        learner_id="learner-1", deck_id="bootcamp", item_id="python-functions",
        rating="Good", reviewed_at=T0,
    )
    assert result.scheduler == "fsrs"
    assert result.scheduler_version == "FSRS-6/py-fsrs-6.3.3"
    assert result.desired_retention == 0.88
    assert result.actual_recall is True
    assert result.mastery_awarded is False
    assert result.resulting_state["card_id"] == stable_fsrs_card_id("learner-1", "bootcamp", "python-functions")


@pytest.mark.parametrize(("rating", "expected"), [(1, False), (2, True), (3, True), (4, True)])
def test_all_fsrs_ratings_preserve_recall_and_mastery_separation(rating, expected):
    result = FSRSAdapter().review(
        learner_id="learner-1", deck_id="d", item_id="i", rating=rating, reviewed_at=T0,
    )
    assert result.actual_recall is expected
    assert result.mastery_awarded is False


def test_fsrs_serialized_state_round_trips_and_replay_is_deterministic():
    adapter = FSRSAdapter()
    first = adapter.review(
        learner_id="l", deck_id="d", item_id="i", rating="Good", reviewed_at=T0,
    )
    second = adapter.review(
        learner_id="l", deck_id="d", item_id="i", rating="Easy",
        reviewed_at=T0 + timedelta(days=1),
        state_json=__import__("json").dumps(first.resulting_state),
    )
    replay_first = adapter.review(
        learner_id="l", deck_id="d", item_id="i", rating="Good", reviewed_at=T0,
    )
    replay_second = adapter.review(
        learner_id="l", deck_id="d", item_id="i", rating="Easy",
        reviewed_at=T0 + timedelta(days=1),
        state_json=__import__("json").dumps(replay_first.resulting_state),
    )
    assert second.resulting_state == replay_second.resulting_state
    assert second.due_at_utc == replay_second.due_at_utc


def test_fsrs_rejects_naive_time_invalid_rating_and_wrong_card_state():
    adapter = FSRSAdapter()
    with pytest.raises(ValueError, match="timezone-aware"):
        adapter.review(learner_id="l", deck_id="d", item_id="i", rating=3, reviewed_at=datetime(2026, 11, 25))
    with pytest.raises(ValueError, match="1..4"):
        adapter.review(learner_id="l", deck_id="d", item_id="i", rating=5, reviewed_at=T0)
    other = adapter.review(learner_id="other", deck_id="d", item_id="i", rating=3, reviewed_at=T0)
    with pytest.raises(ValueError, match="does not belong"):
        adapter.review(learner_id="l", deck_id="d", item_id="i", rating=3, reviewed_at=T0, state_json=__import__("json").dumps(other.resulting_state))


def test_fsrs_config_rejects_invalid_retention_and_steps():
    with pytest.raises(ValueError, match="desired_retention"):
        FSRSConfig(desired_retention=1.0)
    with pytest.raises(ValueError, match="strictly increasing"):
        FSRSConfig(learning_steps_seconds=(60, 60))


def test_fsrs_rejects_boolean_rating_values():
    with pytest.raises(ValueError, match="1..4"):
        FSRSAdapter().review(
            learner_id="l", deck_id="d", item_id="i", rating=True, reviewed_at=T0,
        )
