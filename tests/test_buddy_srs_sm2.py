from datetime import date, timedelta
import pytest
from buddy.learning.srs import Card, review, due_cards, catalog_spaced_repetition_check

D0 = date(2026, 9, 28)


def new():
    return Card("c1", "front", "back", due=D0)


def test_first_three_intervals_1_6_then_ease():
    c = new()
    review(c, 5, D0); assert c.interval == 1
    review(c, 5, c.due); assert c.interval == 6
    ease = c.ease
    review(c, 5, c.due); assert c.interval == round(6 * ease)


def test_lapse_resets():
    c = new()
    review(c, 4, D0); review(c, 4, c.due)
    review(c, 1, c.due)
    assert c.repetitions == 0 and c.interval == 1 and c.lapses == 1


def test_ease_floor():
    c = new()
    for _ in range(20):
        review(c, 0, D0)
    assert c.ease == pytest.approx(1.3)


def test_quality_bounds():
    with pytest.raises(ValueError):
        review(new(), 6, D0)


def test_ease_changes_match_sm2():
    c = new(); review(c, 5, D0); assert c.ease == pytest.approx(2.6)
    c = new(); review(c, 4, D0); assert c.ease == pytest.approx(2.5)
    c = new(); review(c, 3, D0); assert c.ease == pytest.approx(2.36)


def test_due_cards_ordering():
    a = Card("a", "", "", due=D0 - timedelta(days=2))
    b = Card("b", "", "", due=D0)
    f = Card("f", "", "", due=D0 + timedelta(days=1))
    assert [c.card_id for c in due_cards([f, b, a], D0)] == ["a", "b"]


def test_retained_after_two_passes():
    c = new(); review(c, 2, D0); review(c, 3, c.due); assert not c.retained
    review(c, 4, c.due); assert c.retained


def test_catalog_check_matches_upstream_rule():
    r = catalog_spaced_repetition_check([True, False, True], D0)
    assert r["retained"] and r["schedule_days"] == [1, 3, 7]
    assert r["review_dates"] == ["2026-09-29", "2026-10-01", "2026-10-05"]
    assert not catalog_spaced_repetition_check([True, False], D0)["retained"]
    assert r["weights_trained"] is False
