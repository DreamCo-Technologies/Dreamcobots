from buddy.learning.mastery_decision import MasteryEvidence, eligible_for_mastery, should_keep_external_fallback


def evidence(**overrides):
    values = dict(native_passes=3, holdout_passed=True, regression_passed=True, repeated_signature_stable=True, external_assistance_used=True)
    values.update(overrides)
    return MasteryEvidence(**values)


def test_mastery_requires_all_gates():
    assert eligible_for_mastery(evidence())
    assert not eligible_for_mastery(evidence(native_passes=2))
    assert not eligible_for_mastery(evidence(holdout_passed=False))
    assert not eligible_for_mastery(evidence(regression_passed=False))
    assert not eligible_for_mastery(evidence(repeated_signature_stable=False))


def test_external_fallback_remains_until_mastery():
    assert not should_keep_external_fallback(evidence())
    assert should_keep_external_fallback(evidence(native_passes=2))
