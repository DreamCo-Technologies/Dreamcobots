from datetime import datetime, timedelta, timezone

import pytest

from buddy.learning.srs.anki_classic import AnkiClassicCard, AnkiClassicConfig, AnkiClassicScheduler

T0 = datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc)


def test_learning_steps_and_graduation():
    scheduler = AnkiClassicScheduler()
    card = AnkiClassicCard("card-1")
    first = scheduler.review(card, "Good", T0)
    assert first.resulting_state["state"] == "learning"
    assert first.due_at_utc == (T0 + timedelta(seconds=600)).isoformat()
    second = scheduler.review(
        AnkiClassicCard(**first.resulting_state), "Good", T0 + timedelta(minutes=10)
    )
    assert second.resulting_state["state"] == "review"
    assert second.interval_seconds == 86400


def test_easy_graduates_to_easy_interval():
    result = AnkiClassicScheduler().review(AnkiClassicCard("x"), "Easy", T0)
    assert result.resulting_state["state"] == "review"
    assert result.interval_seconds == 4 * 86400


def test_lapse_uses_relearning_steps_and_ease_penalty():
    scheduler = AnkiClassicScheduler()
    card = AnkiClassicCard("reviewed", state="review", interval_days=20, ease_factor=2.5)
    result = scheduler.review(card, "Again", T0)
    assert result.resulting_state["state"] == "relearning"
    assert result.resulting_state["lapses"] == 1
    assert result.resulting_state["ease_factor"] == 2.3
    assert result.interval_seconds == 600


def test_review_interval_adjustments_and_caps():
    scheduler = AnkiClassicScheduler(AnkiClassicConfig(maximum_interval_days=30))
    card = AnkiClassicCard("reviewed", state="review", interval_days=25, ease_factor=2.5)
    result = scheduler.review(card, "Easy", T0)
    assert result.resulting_state["interval_days"] == 30
    assert result.interval_seconds == 30 * 86400


def test_original_card_is_immutable_and_invalid_inputs_fail():
    scheduler = AnkiClassicScheduler()
    original = AnkiClassicCard("new")
    scheduler.review(original, "Good", T0)
    assert original.state == "new"
    with pytest.raises(ValueError, match="timezone-aware"):
        scheduler.review(original, "Good", datetime(2026, 11, 25))
    with pytest.raises(ValueError, match="1..4"):
        scheduler.review(original, 5, T0)
    with pytest.raises(ValueError, match="minimum ease"):
        AnkiClassicConfig(starting_ease=1.0)
