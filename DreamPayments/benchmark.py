from dataclasses import dataclass

TOP_CAPABILITIES = (
    "online_card_payments", "in_person_pos", "tap_to_pay", "payment_links", "invoices",
    "recurring_billing", "subscriptions", "marketplace_split_payments", "developer_api",
    "webhooks", "refunds", "disputes_chargebacks", "fraud_detection", "inventory",
    "customer_crm", "employee_management", "multi_location", "digital_wallets",
    "fast_deposits", "business_banking", "card_issuing", "international_payments",
    "processor_routing", "statement_fee_auditing", "ai_dispute_assistance",
    "ai_revenue_recovery", "ai_payment_assistant", "reconciliation", "analytics",
    "sandbox_testing",
)


@dataclass(frozen=True)
class CapabilityScore:
    provider: str
    capability: str
    score: int  # 0 missing, 1 partial, 2 strong
    evidence: str = ""


def buddy_target_matrix() -> list[CapabilityScore]:
    """Target-state matrix; targets are not production claims."""
    return [
        CapabilityScore("Buddy", capability, 2, "DreamPayments target; verify in CI before production-ready")
        for capability in TOP_CAPABILITIES
    ]


def coverage(scores: list[CapabilityScore], provider: str) -> float:
    values = [s.score for s in scores if s.provider == provider]
    return 0.0 if not values else sum(values) / (2 * len(values)) * 100
