"""DreamPayments: processor-neutral payment orchestration for Buddy."""

from .gateway import PaymentGateway, PaymentRequest, PaymentResult, SandboxProcessor
from .router import PaymentRouter, RoutingCandidate, RoutingPolicy
from .fee_auditor import FeeAudit, audit_statement
from .pricing import DreamPaymentsPlan, core_plan

__all__ = [
    "PaymentGateway", "PaymentRequest", "PaymentResult", "SandboxProcessor",
    "PaymentRouter", "RoutingCandidate", "RoutingPolicy",
    "FeeAudit", "audit_statement", "DreamPaymentsPlan", "core_plan",
]
