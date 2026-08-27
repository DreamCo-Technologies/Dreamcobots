from buddy_os.intelligence.plan_verifier import PlanVerifier


def test_verifier_requires_simulation_and_known_assets():
    verifier = PlanVerifier()
    blocked = verifier.verify("p1", ["asset-a"], [], simulated=False)
    assert not blocked.approved_for_authorization
    assert {issue.code for issue in blocked.issues} == {"missing_asset", "not_simulated"}


def test_verifier_passes_simulated_complete_plan():
    verifier = PlanVerifier()
    check = verifier.verify("p2", ["asset-a"], ["asset-a"], simulated=True)
    assert check.approved_for_authorization
