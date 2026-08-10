from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass(frozen=True)
class FeeAudit:
    card_sales: Decimal
    total_processing_fees: Decimal
    effective_rate_percent: Decimal
    fixed_monthly_fees: Decimal = Decimal("0")
    equipment_fees: Decimal = Decimal("0")
    other_fees: Decimal = Decimal("0")


def audit_statement(card_sales: Decimal, total_processing_fees: Decimal, *, fixed_monthly_fees: Decimal = Decimal("0"), equipment_fees: Decimal = Decimal("0"), other_fees: Decimal = Decimal("0")) -> FeeAudit:
    if card_sales <= 0:
        raise ValueError("card_sales must be greater than zero")
    if min(total_processing_fees, fixed_monthly_fees, equipment_fees, other_fees) < 0:
        raise ValueError("fee values cannot be negative")
    rate = (total_processing_fees / card_sales * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return FeeAudit(card_sales, total_processing_fees, rate, fixed_monthly_fees, equipment_fees, other_fees)
