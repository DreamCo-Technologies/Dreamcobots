from datetime import date, timedelta

import pytest

from buddy.learning.srs.leitner import (
    DEFAULT_INTERVALS,
    LeitnerCard,
    due_leitner_cards,
    review_leitner,
)

D0 = date(2026, 11, 25)


def test_correct_answer_advances_box_and_uses_interval():
    card = LeitnerCard("a", "front", "back", due=D0)
    review_leitner(card, True, D0)
    assert card.box == 2
    assert card.due == D0 + timedelta(days=2)
    assert card.reviews == 1


def test_incorrect_answer_resets_to_first_box():
    card = LeitnerCard("a", "front", "back", box=4, due=D0)
    review_leitner(card, False, D0)
    assert card.box == 1
    assert card.due == D0 + timedelta(days=1)
    assert card.lapses == 1


def test_box_is_capped_at_last_interval():
    card = LeitnerCard("a", "front", "back", box=len(DEFAULT_INTERVALS), due=D0)
    review_leitner(card, True, D0)
    assert card.box == len(DEFAULT_INTERVALS)
    assert card.due == D0 + timedelta(days=DEFAULT_INTERVALS[-1])


def test_due_cards_are_stably_ordered():
    later = LeitnerCard("z", "", "", box=2, due=D0)
    earlier = LeitnerCard("a", "", "", box=1, due=D0 - timedelta(days=1))
    future = LeitnerCard("f", "", "", due=D0 + timedelta(days=1))
    assert [c.card_id for c in due_leitner_cards([later, future, earlier], D0)] == ["a", "z"]


def test_invalid_intervals_and_box_are_rejected():
    card = LeitnerCard("a", "", "", due=D0)
    with pytest.raises(ValueError):
        review_leitner(card, True, D0, intervals=(1, 1, 4))
    card.box = 0
    with pytest.raises(ValueError):
        review_leitner(card, True, D0)
