"""
monetization.py – Plug-and-play monetization mechanisms for DreamCObots.

Supports multiple revenue models:
* ``subscription`` – recurring monthly/annual plans.
* ``pay_per_use``  – charge per API call or interaction.
* ``one_time``     – single purchase (e.g. a dataset or report).
* ``freemium``     – free tier with paid upgrade.

Revenue is tracked per bot and can be queried at any time.
"""

import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class PricingModel(str, Enum):
    SUBSCRIPTION  = "subscription"
    PAY_PER_USE   = "pay_per_use"
    ONE_TIME      = "one_time"
    FREEMIUM      = "freemium"


@dataclass
class PricingPlan:
    plan_id: str
    name: str
    model: PricingModel
    price_usd: float
    description: str
    features: List[str] = field(default_factory=list)
    free_tier_limit: Optional[int] = None    # for freemium: number of free uses


@dataclass
class Transaction:
    tx_id: str
    bot_id: str
    user_id: str
    plan_id: str
    amount_usd: float
    model: PricingModel
    timestamp: float = field(default_factory=time.time)


class MonetizationManager:
    """
    Manages pricing plans and revenue tracking for a single bot.

    Example
    -------
    >>> mm = MonetizationManager(bot_id="doctor-bot")
    >>> mm.add_plan(PricingPlan(
    ...     plan_id="pro",
    ...     name="Pro Plan",
    ...     model=PricingModel.SUBSCRIPTION,
    ...     price_usd=29.99,
    ...     description="Unlimited access to all features.",
    ...     features=["Unlimited queries", "Dataset downloads", "Priority support"],
    ... ))
    >>> mm.charge(user_id="user-123", plan_id="pro")
    """

    def __init__(self, bot_id: str):
        self.bot_id = bot_id
        self._plans: Dict[str, PricingPlan] = {}
        self._transactions: List[Transaction] = []
        self._usage_counts: Dict[str, int] = {}   # user_id → free-tier usage

    # ------------------------------------------------------------------
    # Plan management
    # ------------------------------------------------------------------

    def add_plan(self, plan: PricingPlan) -> None:
        self._plans[plan.plan_id] = plan

    def get_plan(self, plan_id: str) -> Optional[PricingPlan]:
        return self._plans.get(plan_id)

    def list_plans(self) -> List[PricingPlan]:
        return list(self._plans.values())

    # ------------------------------------------------------------------
    # Charging / billing
    # ------------------------------------------------------------------

    def charge(self, user_id: str, plan_id: str) -> Optional[Transaction]:
        """
        Attempt to charge a user for the given plan.

        Freemium logic: if the user has not exceeded the free tier limit,
        the charge is 0.  After that, full price applies.

        Returns the Transaction or None if the plan does not exist.
        """
        plan = self._plans.get(plan_id)
        if plan is None:
            return None

        amount = plan.price_usd
        if plan.model == PricingModel.FREEMIUM and plan.free_tier_limit is not None:
            used = self._usage_counts.get(user_id, 0)
            if used < plan.free_tier_limit:
                amount = 0.0
            self._usage_counts[user_id] = used + 1

        payment_ok = self._process_payment(user_id, amount)
        if not payment_ok:
            return None

        tx = Transaction(
            tx_id=str(uuid.uuid4()),
            bot_id=self.bot_id,
            user_id=user_id,
            plan_id=plan_id,
            amount_usd=amount,
            model=plan.model,
        )
        self._transactions.append(tx)
        return tx

    @staticmethod
    def _process_payment(user_id: str, amount_usd: float) -> bool:
        """
        Stub payment processor.  Replace with Stripe / PayPal in production.
        """
        if amount_usd == 0.0:
            print(f"[Billing] Free-tier access granted to '{user_id}'.")
        else:
            print(f"[Billing] Charged ${amount_usd:.2f} to '{user_id}' … OK (stub)")
        return True

    # ------------------------------------------------------------------
    # Revenue analytics
    # ------------------------------------------------------------------

    def total_revenue(self) -> float:
        return round(sum(t.amount_usd for t in self._transactions), 2)

    def revenue_by_plan(self) -> Dict[str, float]:
        result: Dict[str, float] = {}
        for tx in self._transactions:
            result[tx.plan_id] = round(result.get(tx.plan_id, 0.0) + tx.amount_usd, 2)
        return result

    def revenue_summary(self) -> Dict[str, Any]:
        return {
            "bot_id": self.bot_id,
            "total_revenue_usd": self.total_revenue(),
            "total_transactions": len(self._transactions),
            "revenue_by_plan": self.revenue_by_plan(),
            "active_plans": len(self._plans),
        }

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bot_id": self.bot_id,
            "plans": [asdict(p) for p in self._plans.values()],
            "transactions": [asdict(t) for t in self._transactions],
        }
