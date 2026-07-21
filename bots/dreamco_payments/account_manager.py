"""
DreamCo Payments — Account Manager

Handles user onboarding, identity verification, fraud detection, notifications,
and custom limit management.

Business types:
  - "standard"     — General merchant
  - "real_estate"  — Real-estate flipping automation hints
  - "auto_dealer"  — Car-flipping automation hints
"""

import uuid
import datetime
from typing import Optional

from bots.dreamco_payments.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    FEATURE_FRAUD_DETECTION,
    FEATURE_CUSTOM_LIMITS,
    FEATURE_REAL_ESTATE_AUTOMATION,
    FEATURE_AUTO_DEALER_AUTOMATION,
)
from framework import GlobalAISourcesFlow  # noqa: F401


class AccountTierError(Exception):
    """Raised when an account feature is not available on the current tier."""


_VALID_BUSINESS_TYPES = {"standard", "real_estate", "auto_dealer"}

_BUSINESS_HINTS: dict[str, list[str]] = {
    "real_estate": [
        "Automate escrow payment scheduling",
        "Track closing-cost disbursements per property",
        "Reconcile rental-income deposits automatically",
        "Generate IRS Schedule E payment summaries",
    ],
    "auto_dealer": [
        "Automate floorplan financing payments",
        "Track auction purchase wires and lot fees",
        "Reconcile dealer-to-dealer transfer payments",
        "Generate per-vehicle profit/loss payment reports",
    ],
    "standard": [],
}

# Simple rule-based fraud signals for mock detection
_FRAUD_RULES = [
    ("high_amount", lambda d: d.get("amount", 0) > 10_000),
    ("unknown_currency", lambda d: d.get("currency", "USD") not in {
        "USD", "EUR", "GBP", "CAD", "AUD", "JPY", "MXN"
    }),
    ("suspicious_country", lambda d: d.get("country", "") in {"XX", "ZZ"}),
    ("velocity_flag", lambda d: d.get("transaction_count_1h", 0) > 20),
    ("card_mismatch", lambda d: d.get("billing_country") != d.get("ip_country")
     and d.get("billing_country") is not None
     and d.get("ip_country") is not None),
]


class AccountManager:
    """
    Tier-aware account manager for DreamCo Payments.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature access.
    """

    def __init__(self, tier: Tier = Tier.STARTER) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self._users: dict[str, dict] = {}
        self._notifications: dict[str, list] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            raise AccountTierError(
                f"Feature '{feature}' is not available on the "
                f"{self.config.name} tier.  Please upgrade."
            )

    @staticmethod
    def _now_iso() -> str:
        return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ------------------------------------------------------------------
    # User onboarding
    # ------------------------------------------------------------------

    def onboard_user(
        self,
        user_id: str,
        name: str,
        email: str,
        business_type: str = "standard",
    ) -> dict:
        """
        Onboard a new user onto the DreamCo Payments platform.

        Parameters
        ----------
        user_id : str
            Unique user identifier.
        name : str
            User's full name or business name.
        email : str
            Contact email address.
        business_type : str
            One of 'standard', 'real_estate', or 'auto_dealer'.

        Returns
        -------
        dict
            User profile including automation hints for specialist types.
        """
        if business_type not in _VALID_BUSINESS_TYPES:
            raise ValueError(
                f"Invalid business_type '{business_type}'.  "
                f"Valid values: {sorted(_VALID_BUSINESS_TYPES)}"
            )

        hints = _BUSINESS_HINTS.get(business_type, [])
        record = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "business_type": business_type,
            "status": "active",
            "verification_level": "none",
            "limits": {},
            "automation_hints": hints,
            "created_at": self._now_iso(),
            "tier": self.tier.value,
        }
        self._users[user_id] = record
        self._notifications[user_id] = []
        return dict(record)

    # ------------------------------------------------------------------
    # Identity verification
    # ------------------------------------------------------------------

    def verify_user(self, user_id: str, verification_docs: dict) -> dict:
        """
        Process identity verification documents for a user.

        Parameters
        ----------
        user_id : str
            User to verify.
        verification_docs : dict
            Mock document metadata (e.g. {"id_type": "passport", "doc_id": "P123"}).

        Returns
        -------
        dict
            Verification result with status and verification_level.
        """
        if user_id not in self._users:
            raise KeyError(f"User '{user_id}' not found.")

        doc_id = verification_docs.get("doc_id", "")
        id_type = verification_docs.get("id_type", "unknown")

        # Mock logic: any non-empty doc_id passes at 'basic'; include 'address' to reach 'enhanced'
        if not doc_id:
            level = "none"
            status = "failed"
        elif verification_docs.get("address_proof"):
            level = "enhanced"
            status = "verified"
        else:
            level = "basic"
            status = "verified"

        self._users[user_id]["verification_level"] = level
        return {
            "user_id": user_id,
            "status": status,
            "verification_level": level,
            "id_type": id_type,
            "verified_at": self._now_iso(),
        }

    # ------------------------------------------------------------------
    # Fraud detection  (GROWTH+)
    # ------------------------------------------------------------------

    def detect_fraud(self, transaction_data: dict) -> dict:
        """
        Analyze transaction data and return a risk assessment.

        Requires GROWTH or ENTERPRISE tier.

        Parameters
        ----------
        transaction_data : dict
            Transaction fields such as amount, currency, country, etc.

        Returns
        -------
        dict
            risk_score (0.0–1.0), risk_level ('low'/'medium'/'high'), flags.
        """
        self._require_feature(FEATURE_FRAUD_DETECTION)

        flags = [name for name, rule in _FRAUD_RULES if rule(transaction_data)]
        score = round(min(len(flags) / len(_FRAUD_RULES), 1.0), 4)

        if score < 0.3:
            level = "low"
        elif score < 0.7:
            level = "medium"
        else:
            level = "high"

        return {
            "risk_score": score,
            "risk_level": level,
            "flags": flags,
            "assessed_at": self._now_iso(),
        }

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    def send_notification(
        self,
        user_id: str,
        event_type: str,
        message: str,
    ) -> dict:
        """
        Send an in-platform notification to a user.

        Parameters
        ----------
        user_id : str
            Recipient user.
        event_type : str
            Event category (e.g. 'payment_received', 'refund_issued').
        message : str
            Notification body.

        Returns
        -------
        dict
            Notification record.
        """
        if user_id not in self._notifications:
            self._notifications[user_id] = []

        notification = {
            "notification_id": f"notif_{uuid.uuid4().hex[:8]}",
            "user_id": user_id,
            "event_type": event_type,
            "message": message,
            "sent_at": self._now_iso(),
        }
        self._notifications[user_id].append(notification)
        return dict(notification)

    # ------------------------------------------------------------------
    # User profile
    # ------------------------------------------------------------------

    def get_user_profile(self, user_id: str) -> dict:
        """
        Retrieve the full profile of a user.

        Parameters
        ----------
        user_id : str
            User to retrieve.

        Returns
        -------
        dict
            User profile record.
        """
        if user_id not in self._users:
            raise KeyError(f"User '{user_id}' not found.")
        return dict(self._users[user_id])

    # ------------------------------------------------------------------
    # Custom limits  (ENTERPRISE only)
    # ------------------------------------------------------------------

    def update_user_limits(self, user_id: str, limits: dict) -> dict:
        """
        Override default transaction limits for a user.

        Requires ENTERPRISE tier.

        Parameters
        ----------
        user_id : str
            User to update.
        limits : dict
            Limit overrides (e.g. {"daily_max": 50000, "per_txn_max": 5000}).

        Returns
        -------
        dict
            Updated user profile.
        """
        self._require_feature(FEATURE_CUSTOM_LIMITS)

        if user_id not in self._users:
            raise KeyError(f"User '{user_id}' not found.")

        self._users[user_id]["limits"].update(limits)
        return dict(self._users[user_id])
