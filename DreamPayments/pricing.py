from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class DreamPaymentsPlan:
    name: str
    monthly_software_fee: Decimal
    payment_rail_costs_included: bool
    description: str


def core_plan() -> DreamPaymentsPlan:
    return DreamPaymentsPlan(
        name="Buddy Pay Core",
        monthly_software_fee=Decimal("0.00"),
        payment_rail_costs_included=False,
        description=(
            "$0/month DreamCo software layer. Processor, interchange, network, banking, "
            "chargeback, payout, and regulated third-party costs remain transparent and separate."
        ),
    )
