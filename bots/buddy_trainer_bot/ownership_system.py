"""
Ownership System — Payment models and licensing for personal Buddy bots.

Capabilities
------------
* Multi-tier pricing: FREE, PRO ($49/mo), ENTERPRISE ($199/mo), OWNER ($499 one-time).
* Purchase and activate Buddy bot licenses.
* Manage subscriptions: upgrade, downgrade, cancel.
* Apply sponsorships so low-income users can access Buddy for free.
* Track revenue and license inventory.
* Validate license status before granting feature access.

No real payment gateway is called — all transactions are simulated for
portability.  Production deployments can integrate Stripe, PayPal, or
Coinbase Commerce by replacing the _process_payment() stub.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401
from bots.buddy_trainer_bot.tiers import Tier, TierConfig, get_tier_config, TIER_CATALOGUE


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    CRYPTO = "crypto"
    SPONSORED = "sponsored"          # Free access via sponsorship program
    DREAMCOIN = "dreamcoin"


class LicenseStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    SPONSORED = "sponsored"
    PENDING = "pending"


class TransactionType(Enum):
    SUBSCRIPTION_NEW = "subscription_new"
    SUBSCRIPTION_RENEWAL = "subscription_renewal"
    SUBSCRIPTION_UPGRADE = "subscription_upgrade"
    SUBSCRIPTION_DOWNGRADE = "subscription_downgrade"
    SUBSCRIPTION_CANCEL = "subscription_cancel"
    ONE_TIME_PURCHASE = "one_time_purchase"
    SPONSORSHIP_GRANT = "sponsorship_grant"
    REFUND = "refund"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class License:
    """A Buddy bot license held by a user."""
    license_id: str
    user_id: str
    tier: Tier
    status: LicenseStatus
    payment_method: PaymentMethod
    amount_paid_usd: float
    activated_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None      # None for lifetime / OWNER tier
    github_buddy_provisioned: bool = False
    notes: str = ""

    def is_valid(self) -> bool:
        if self.status != LicenseStatus.ACTIVE and self.status != LicenseStatus.SPONSORED:
            return False
        if self.expires_at is not None and time.time() > self.expires_at:
            return False
        return True

    def to_dict(self) -> dict:
        return {
            "license_id": self.license_id,
            "user_id": self.user_id,
            "tier": self.tier.value,
            "status": self.status.value,
            "payment_method": self.payment_method.value,
            "amount_paid_usd": self.amount_paid_usd,
            "activated_at": self.activated_at,
            "expires_at": self.expires_at,
            "github_buddy_provisioned": self.github_buddy_provisioned,
            "valid": self.is_valid(),
        }


@dataclass
class Transaction:
    """A payment or licensing transaction."""
    transaction_id: str
    user_id: str
    transaction_type: TransactionType
    tier: Tier
    amount_usd: float
    payment_method: PaymentMethod
    status: str          # "completed" | "failed" | "refunded"
    timestamp: float = field(default_factory=time.time)
    license_id: Optional[str] = None
    reference: str = ""

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "transaction_type": self.transaction_type.value,
            "tier": self.tier.value,
            "amount_usd": self.amount_usd,
            "payment_method": self.payment_method.value,
            "status": self.status,
            "timestamp": self.timestamp,
            "license_id": self.license_id,
        }


@dataclass
class Sponsorship:
    """A sponsorship grant enabling a user to access Buddy for free."""
    sponsorship_id: str
    beneficiary_user_id: str
    sponsor_user_id: str       # "dreamco_foundation" for platform-funded grants
    tier_granted: Tier
    reason: str
    granted_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    active: bool = True

    def to_dict(self) -> dict:
        return {
            "sponsorship_id": self.sponsorship_id,
            "beneficiary_user_id": self.beneficiary_user_id,
            "sponsor_user_id": self.sponsor_user_id,
            "tier_granted": self.tier_granted.value,
            "reason": self.reason,
            "granted_at": self.granted_at,
            "expires_at": self.expires_at,
            "active": self.active,
        }


# ---------------------------------------------------------------------------
# Pricing helpers
# ---------------------------------------------------------------------------

MONTHLY_BILLING_DAYS = 30

def _subscription_expiry(days: int = MONTHLY_BILLING_DAYS) -> float:
    return time.time() + days * 86_400


def _process_payment(
    amount_usd: float, payment_method: PaymentMethod
) -> tuple[bool, str]:
    """
    Simulate a payment transaction.

    Returns (success: bool, reference: str).
    Production: replace with real gateway call.
    """
    if amount_usd < 0:
        return False, "invalid_amount"
    ref = f"pay_{uuid.uuid4().hex[:16]}"
    return True, ref


# ---------------------------------------------------------------------------
# Core class
# ---------------------------------------------------------------------------

class OwnershipSystem:
    """
    Manages Buddy bot licenses, subscriptions, and sponsorships.

    Parameters
    ----------
    platform_id : str
        Identifier for this ownership system instance.
    """

    def __init__(self, platform_id: str = "buddy_ownership_v1") -> None:
        self.platform_id = platform_id
        self._licenses: dict[str, License] = {}          # license_id -> License
        self._user_licenses: dict[str, list[str]] = {}   # user_id -> [license_ids]
        self._transactions: list[Transaction] = []
        self._sponsorships: dict[str, Sponsorship] = {}
        self._total_revenue: float = 0.0

    # ------------------------------------------------------------------
    # License purchase
    # ------------------------------------------------------------------

    def purchase_license(
        self,
        user_id: str,
        tier: Tier,
        payment_method: PaymentMethod = PaymentMethod.CREDIT_CARD,
    ) -> dict:
        """
        Purchase a new Buddy bot license for *user_id*.

        For OWNER tier the payment is one-time ($499).
        For other tiers it is a monthly subscription.

        Returns a result dict with the new license and transaction.
        """
        config: TierConfig = get_tier_config(tier)

        if tier == Tier.OWNER:
            amount = config.price_usd_one_time
            tx_type = TransactionType.ONE_TIME_PURCHASE
            expires_at = None   # lifetime
        elif tier == Tier.FREE:
            amount = 0.0
            tx_type = TransactionType.SUBSCRIPTION_NEW
            expires_at = _subscription_expiry()
        else:
            amount = config.price_usd_monthly
            tx_type = TransactionType.SUBSCRIPTION_NEW
            expires_at = _subscription_expiry()

        success, ref = _process_payment(amount, payment_method)
        if not success:
            return {
                "success": False,
                "message": "Payment processing failed. Please try again.",
            }

        license_id = f"lic_{uuid.uuid4().hex[:12]}"
        license_status = LicenseStatus.ACTIVE

        lic = License(
            license_id=license_id,
            user_id=user_id,
            tier=tier,
            status=license_status,
            payment_method=payment_method,
            amount_paid_usd=amount,
            expires_at=expires_at,
        )
        self._licenses[license_id] = lic
        self._user_licenses.setdefault(user_id, []).append(license_id)
        self._total_revenue += amount

        tx = Transaction(
            transaction_id=f"tx_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            transaction_type=tx_type,
            tier=tier,
            amount_usd=amount,
            payment_method=payment_method,
            status="completed",
            license_id=license_id,
            reference=ref,
        )
        self._transactions.append(tx)

        msg = (
            f"🎉 Welcome to Buddy {config.name} tier! "
            + (
                "Your lifetime OWNER license is active. Buddy bot GitHub system is ready to provision."
                if tier == Tier.OWNER
                else f"Your ${amount:.2f}/month subscription is active."
            )
        )

        return {
            "success": True,
            "license": lic.to_dict(),
            "transaction": tx.to_dict(),
            "message": msg,
        }

    # ------------------------------------------------------------------
    # Subscription management
    # ------------------------------------------------------------------

    def upgrade_subscription(
        self,
        user_id: str,
        new_tier: Tier,
        payment_method: PaymentMethod = PaymentMethod.CREDIT_CARD,
    ) -> dict:
        """Upgrade a user's active subscription to a higher tier."""
        active = self._get_active_license(user_id)
        if active is None:
            return {"success": False, "message": "No active license found for this user."}

        if list(Tier).index(new_tier) <= list(Tier).index(active.tier):
            return {"success": False, "message": "New tier must be higher than current tier."}

        # Cancel old license
        active.status = LicenseStatus.CANCELLED
        # Purchase new tier
        result = self.purchase_license(user_id, new_tier, payment_method)
        if result["success"]:
            result["transaction"]["transaction_type"] = TransactionType.SUBSCRIPTION_UPGRADE.value
        return result

    def cancel_subscription(self, user_id: str) -> dict:
        """Cancel the user's active subscription."""
        active = self._get_active_license(user_id)
        if active is None:
            return {"success": False, "message": "No active license found."}
        active.status = LicenseStatus.CANCELLED
        tx = Transaction(
            transaction_id=f"tx_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            transaction_type=TransactionType.SUBSCRIPTION_CANCEL,
            tier=active.tier,
            amount_usd=0.0,
            payment_method=active.payment_method,
            status="completed",
            license_id=active.license_id,
        )
        self._transactions.append(tx)
        return {
            "success": True,
            "message": f"Subscription cancelled. License '{active.license_id}' is no longer active.",
        }

    def _get_active_license(self, user_id: str) -> Optional[License]:
        for lid in self._user_licenses.get(user_id, []):
            lic = self._licenses.get(lid)
            if lic and lic.is_valid():
                return lic
        return None

    # ------------------------------------------------------------------
    # Sponsorships (help the poor pay for Buddy)
    # ------------------------------------------------------------------

    def grant_sponsorship(
        self,
        beneficiary_user_id: str,
        tier_granted: Tier = Tier.PRO,
        reason: str = "financial_hardship",
        sponsor_user_id: str = "dreamco_foundation",
        duration_days: Optional[int] = 30,
    ) -> dict:
        """
        Grant a sponsored (free) license to a user in need.

        DreamCo's mission: make Buddy accessible to everyone.
        """
        sponsorship_id = f"sp_{uuid.uuid4().hex[:12]}"
        expires_at = _subscription_expiry(duration_days) if duration_days else None

        sp = Sponsorship(
            sponsorship_id=sponsorship_id,
            beneficiary_user_id=beneficiary_user_id,
            sponsor_user_id=sponsor_user_id,
            tier_granted=tier_granted,
            reason=reason,
            expires_at=expires_at,
        )
        self._sponsorships[sponsorship_id] = sp

        # Issue a sponsored license
        license_id = f"lic_{uuid.uuid4().hex[:12]}"
        lic = License(
            license_id=license_id,
            user_id=beneficiary_user_id,
            tier=tier_granted,
            status=LicenseStatus.SPONSORED,
            payment_method=PaymentMethod.SPONSORED,
            amount_paid_usd=0.0,
            expires_at=expires_at,
            notes=f"Sponsored by {sponsor_user_id}: {reason}",
        )
        self._licenses[license_id] = lic
        self._user_licenses.setdefault(beneficiary_user_id, []).append(license_id)

        tx = Transaction(
            transaction_id=f"tx_{uuid.uuid4().hex[:12]}",
            user_id=beneficiary_user_id,
            transaction_type=TransactionType.SPONSORSHIP_GRANT,
            tier=tier_granted,
            amount_usd=0.0,
            payment_method=PaymentMethod.SPONSORED,
            status="completed",
            license_id=license_id,
        )
        self._transactions.append(tx)

        config = get_tier_config(tier_granted)
        return {
            "success": True,
            "sponsorship": sp.to_dict(),
            "license": lic.to_dict(),
            "message": (
                f"Sponsorship granted! {beneficiary_user_id} now has free access to "
                f"Buddy {config.name} tier for {duration_days or 'unlimited'} days."
            ),
        }

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_access(self, user_id: str, required_tier: Tier) -> dict:
        """Check whether *user_id* has a valid license for *required_tier*."""
        active = self._get_active_license(user_id)
        tier_order = list(Tier)

        if active is None:
            return {
                "allowed": False,
                "reason": "No active license.",
                "upgrade_url": "https://dreamcobots.com/upgrade",
            }

        user_tier_idx = tier_order.index(active.tier)
        required_tier_idx = tier_order.index(required_tier)

        if user_tier_idx >= required_tier_idx:
            return {
                "allowed": True,
                "tier": active.tier.value,
                "license_id": active.license_id,
            }

        return {
            "allowed": False,
            "reason": f"Your {active.tier.value} license does not include {required_tier.value} features.",
            "upgrade_url": "https://dreamcobots.com/upgrade",
        }

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_user_license(self, user_id: str) -> Optional[License]:
        return self._get_active_license(user_id)

    def list_transactions(self, user_id: Optional[str] = None) -> list[Transaction]:
        if user_id:
            return [t for t in self._transactions if t.user_id == user_id]
        return list(self._transactions)

    def revenue_summary(self) -> dict:
        return {
            "platform_id": self.platform_id,
            "total_revenue_usd": round(self._total_revenue, 2),
            "total_licenses": len(self._licenses),
            "active_licenses": sum(1 for l in self._licenses.values() if l.is_valid()),
            "total_sponsorships": len(self._sponsorships),
            "total_transactions": len(self._transactions),
        }
