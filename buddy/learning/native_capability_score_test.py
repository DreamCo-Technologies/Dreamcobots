from native_capability_score import CapabilitySample, external_assistance_rate, native_solve_rate


def test_native_rate_ignores_unverified_samples():
    samples = [CapabilitySample(True, False, True), CapabilitySample(True, True, True), CapabilitySample(True, False, False)]
    assert native_solve_rate(samples) == 0.5
    assert external_assistance_rate(samples) == 0.5
