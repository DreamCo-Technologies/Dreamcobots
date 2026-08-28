import pytest

from buddy_os.intelligence.verification_selector import VerificationOption, VerificationSelector


def test_selector_prefers_information_gain_per_cost_and_risk():
    selector = VerificationSelector()
    options = [
        VerificationOption("cheap", .6, cost=1, risk=.1),
        VerificationOption("expensive", .95, cost=4, risk=.1),
    ]
    assert selector.choose(options).option_id == "cheap"


def test_selector_ignores_unavailable_options_and_handles_empty_input():
    selector = VerificationSelector()
    assert selector.choose([]) is None
    assert selector.choose([VerificationOption("x", .9, available=False)]) is None


def test_verification_option_validates_values():
    with pytest.raises(ValueError):
        VerificationOption("x", 1.1)
    with pytest.raises(ValueError):
        VerificationOption("x", .5, cost=0)
