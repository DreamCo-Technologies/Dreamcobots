import pytest

from buddy_os.intelligence.reasoning_uncertainty import Uncertainty, independent_support, uncertainty_budget, weakest_link


def test_uncertainty_is_bounded():
    with pytest.raises(ValueError):
        Uncertainty(1.1)


def test_independent_support_and_weakest_link_are_conservative_primitives():
    a, b = Uncertainty(0.8), Uncertainty(0.9)
    assert independent_support(a, b).confidence == pytest.approx(0.98)
    assert weakest_link(a, b).confidence == pytest.approx(0.8)
    assert uncertainty_budget((a, b)) == pytest.approx(0.3)
