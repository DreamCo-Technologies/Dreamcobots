from decimal import Decimal

from DreamPayments.benchmark import TOP_CAPABILITIES, buddy_target_matrix, coverage
from DreamPayments.fee_auditor import audit_statement
from DreamPayments.gateway import PaymentRequest, SandboxProcessor
from DreamPayments.pricing import core_plan
from DreamPayments.router import PaymentRouter, RoutingCandidate, RoutingPolicy


def test_sandbox_payment_and_refund():
    gateway = SandboxProcessor()
    result = gateway.authorize_and_capture(
        PaymentRequest(
            merchant_id="merchant_demo",
            amount=Decimal("47.50"),
            payment_method_token="tok_sandbox_only",
        )
    )
    assert result.status == "succeeded"
    refunded = gateway.refund(result.payment_id)
    assert refunded.status == "refunded"


def test_fee_auditor_effective_rate():
    audit = audit_statement(Decimal("30000"), Decimal("1050"))
    assert audit.effective_rate_percent == Decimal("3.50")


def test_router_respects_reliability_and_cost():
    selected = PaymentRouter().choose(
        [
            RoutingCandidate("processor-a", Decimal("1.25"), Decimal("0.999"), 180),
            RoutingCandidate("processor-b", Decimal("1.05"), Decimal("0.998"), 140),
        ],
        RoutingPolicy(strategy="lowest_cost"),
    )
    assert selected.processor == "processor-b"


def test_core_software_plan_is_free_but_rails_are_not_claimed_free():
    plan = core_plan()
    assert plan.monthly_software_fee == Decimal("0.00")
    assert plan.payment_rail_costs_included is False


def test_benchmark_tracks_30_payment_capabilities_as_targets():
    assert len(TOP_CAPABILITIES) == 30
    scores = buddy_target_matrix()
    assert coverage(scores, "Buddy") == 100.0
    assert all("target" in item.evidence.lower() for item in scores)
