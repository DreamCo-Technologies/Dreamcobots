from buddy.learning.dependency_reduction_score import Cohort, is_improving, reduction_score


def test_native_gain_and_external_drop_are_positive_progress():
    previous = Cohort(native_pass_rate=0.40, external_assistance_rate=0.60)
    current = Cohort(native_pass_rate=0.55, external_assistance_rate=0.45)
    assert reduction_score(previous, current) == 0.30
    assert is_improving(previous, current)


def test_external_reduction_without_quality_gain_is_not_learning():
    previous = Cohort(native_pass_rate=0.40, external_assistance_rate=0.60)
    current = Cohort(native_pass_rate=0.40, external_assistance_rate=0.45)
    assert not is_improving(previous, current)
