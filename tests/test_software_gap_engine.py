from dreamco_platform.software_gap_engine import CapabilityEvidence, category_coverage, rank_gaps


def test_missing_high_value_gap_ranks_above_partial_low_value_gap():
    gaps = rank_gaps([
        CapabilityEvidence("crm_sales", "forecast sales", "PARTIAL", user_value=2, frequency=2, dependency_value=2, revenue_value=2, risk=2),
        CapabilityEvidence("manufacturing", "control machines", "MISSING", user_value=5, frequency=4, dependency_value=5, revenue_value=5, risk=5),
    ])
    assert gaps[0].category_id == "manufacturing"


def test_disconnected_prefers_reconnection_over_duplicate_build():
    result = rank_gaps([CapabilityEvidence("payments_banking", "accept payments", "DISCONNECTED")])[0]
    assert "connect" in result.action.lower() or "repair" in result.action.lower()


def test_category_coverage_is_evidence_weighted():
    items = [
        CapabilityEvidence("office_suites", "write", "VERIFIED"),
        CapabilityEvidence("office_suites", "calculate", "PARTIAL"),
        CapabilityEvidence("office_suites", "present", "MISSING"),
    ]
    assert category_coverage(items, "office_suites") == 50.0
