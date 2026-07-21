"""
DreamCo Payments Bot — Main entry point

Composes all sub-managers (PaymentProcessor, APIManager, AccountManager,
ReportingDashboard) into a single cohesive bot with a BuddyAI-compatible
chat interface.

Usage
-----
    from bots.dreamco_payments import DreamcoPaymentsBot, Tier

    bot = DreamcoPaymentsBot(tier=Tier.GROWTH)
    result = bot.process_payment(49.99, "USD", "card_visa_4242", "cust_001")
    print(result)
"""

from bots.dreamco_payments.tiers import Tier, get_tier_config, get_upgrade_path
from bots.dreamco_payments.payment_processor import PaymentProcessor
from bots.dreamco_payments.api_manager import APIManager
from bots.dreamco_payments.account_manager import AccountManager
from bots.dreamco_payments.reporting_dashboard import ReportingDashboard
from framework import GlobalAISourcesFlow  # noqa: F401


class DreamcoPaymentsBot:
    """
    Tier-aware DreamCo Payments Bot.

    Composes PaymentProcessor, APIManager, AccountManager, and
    ReportingDashboard.  Exposes a unified API and a BuddyAI-compatible
    ``chat()`` interface.

    Parameters
    ----------
    tier : Tier
        Subscription tier.  Defaults to STARTER.
    """

    def __init__(self, tier: Tier = Tier.STARTER) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self._payment_processor = PaymentProcessor(tier)
        self._api_manager = APIManager(tier)
        self._account_manager = AccountManager(tier)
        self._dashboard = ReportingDashboard(tier)
        self._buddy_bot = None  # set via register_with_buddy()

    # ------------------------------------------------------------------
    # Payment delegation
    # ------------------------------------------------------------------

    def process_payment(
        self,
        amount: float,
        currency: str,
        payment_method: str,
        customer_id: str,
    ) -> dict:
        """Delegate to PaymentProcessor.process_payment."""
        return self._payment_processor.process_payment(
            amount, currency, payment_method, customer_id
        )

    def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        amount: float,
        currency: str,
        interval: str = "monthly",
    ) -> dict:
        """Delegate to PaymentProcessor.create_subscription."""
        return self._payment_processor.create_subscription(
            customer_id, plan_id, amount, currency, interval
        )

    def cancel_subscription(self, subscription_id: str) -> dict:
        """Delegate to PaymentProcessor.cancel_subscription."""
        return self._payment_processor.cancel_subscription(subscription_id)

    def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
    ) -> dict:
        """Delegate to PaymentProcessor.convert_currency."""
        return self._payment_processor.convert_currency(
            amount, from_currency, to_currency
        )

    def process_recurring_billing(self, subscription_id: str) -> dict:
        """Delegate to PaymentProcessor.process_recurring_billing."""
        return self._payment_processor.process_recurring_billing(subscription_id)

    def refund_payment(self, transaction_id: str, amount=None) -> dict:
        """Delegate to PaymentProcessor.refund_payment."""
        return self._payment_processor.refund_payment(transaction_id, amount)

    def list_transactions(self, customer_id: str) -> list:
        """Delegate to PaymentProcessor.list_transactions."""
        return self._payment_processor.list_transactions(customer_id)

    # ------------------------------------------------------------------
    # API management delegation
    # ------------------------------------------------------------------

    def generate_api_key(self, name: str, permissions: list) -> dict:
        """Delegate to APIManager.generate_api_key."""
        return self._api_manager.generate_api_key(name, permissions)

    def rotate_api_key(self, key_id: str) -> dict:
        """Delegate to APIManager.rotate_api_key."""
        return self._api_manager.rotate_api_key(key_id)

    def revoke_api_key(self, key_id: str) -> dict:
        """Delegate to APIManager.revoke_api_key."""
        return self._api_manager.revoke_api_key(key_id)

    def validate_api_key(self, key: str) -> bool:
        """Delegate to APIManager.validate_api_key."""
        return self._api_manager.validate_api_key(key)

    # ------------------------------------------------------------------
    # Account management delegation
    # ------------------------------------------------------------------

    def onboard_user(
        self,
        user_id: str,
        name: str,
        email: str,
        business_type: str = "standard",
    ) -> dict:
        """Delegate to AccountManager.onboard_user."""
        return self._account_manager.onboard_user(
            user_id, name, email, business_type
        )

    def verify_user(self, user_id: str, verification_docs: dict) -> dict:
        """Delegate to AccountManager.verify_user."""
        return self._account_manager.verify_user(user_id, verification_docs)

    def detect_fraud(self, transaction_data: dict) -> dict:
        """Delegate to AccountManager.detect_fraud."""
        return self._account_manager.detect_fraud(transaction_data)

    def send_notification(
        self, user_id: str, event_type: str, message: str
    ) -> dict:
        """Delegate to AccountManager.send_notification."""
        return self._account_manager.send_notification(
            user_id, event_type, message
        )

    def get_user_profile(self, user_id: str) -> dict:
        """Delegate to AccountManager.get_user_profile."""
        return self._account_manager.get_user_profile(user_id)

    # ------------------------------------------------------------------
    # Dashboard delegation
    # ------------------------------------------------------------------

    def get_financial_summary(self, period: str = "monthly") -> dict:
        """Delegate to ReportingDashboard.get_financial_summary."""
        return self._dashboard.get_financial_summary(period)

    def get_bot_performance(self, bot_name: str) -> dict:
        """Delegate to ReportingDashboard.get_bot_performance."""
        return self._dashboard.get_bot_performance(bot_name)

    def get_all_bots_performance(self) -> dict:
        """Delegate to ReportingDashboard.get_all_bots_performance."""
        return self._dashboard.get_all_bots_performance()

    def get_discount_dominator_settings(self, setting_id: int) -> dict:
        """Delegate to ReportingDashboard.get_discount_dominator_settings."""
        return self._dashboard.get_discount_dominator_settings(setting_id)

    def list_discount_dominator_settings(self, group: str) -> list:
        """Delegate to ReportingDashboard.list_discount_dominator_settings."""
        return self._dashboard.list_discount_dominator_settings(group)

    def update_discount_dominator_setting(
        self, setting_id: int, value
    ) -> dict:
        """Delegate to ReportingDashboard.update_discount_dominator_setting."""
        return self._dashboard.update_discount_dominator_setting(
            setting_id, value
        )

    def export_report(self, format_type: str) -> dict:
        """Delegate to ReportingDashboard.export_report."""
        return self._dashboard.export_report(format_type)

    # ------------------------------------------------------------------
    # Tier description
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """
        Return a formatted string describing the current tier.

        Returns
        -------
        str
            Human-readable tier summary.
        """
        cfg = self.config
        txn_limit = (
            "Unlimited"
            if cfg.transactions_per_month is None
            else f"{cfg.transactions_per_month:,}"
        )
        lines = [
            f"DreamCo Payments — {cfg.name} Tier",
            f"  Price          : ${cfg.price_usd_monthly:.2f}/month",
            f"  Transactions   : {txn_limit}/month",
            f"  Support        : {cfg.support_level}",
            f"  Features       : {', '.join(cfg.features)}",
        ]
        upgrade = get_upgrade_path(self.tier)
        if upgrade:
            lines.append(
                f"  Upgrade to     : {upgrade.name} (${upgrade.price_usd_monthly:.2f}/mo)"
            )
        else:
            lines.append("  You are on the top-tier plan.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # BuddyAI-compatible chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """
        Process a plain-text message and return a structured response.

        Provides a BuddyAI-compatible interface so the bot can be registered
        with BuddyBot and receive routed messages.

        Parameters
        ----------
        message : str
            The incoming message text.

        Returns
        -------
        dict
            response, bot_name, tier.
        """
        msg_lower = message.lower()

        if "tier" in msg_lower or "plan" in msg_lower:
            response = self.describe_tier()
        elif "currency" in msg_lower:
            response = (
                "Supported currencies: USD, EUR, GBP, CAD, AUD, JPY, MXN.  "
                "Currency conversion is available on Growth and Enterprise tiers."
            )
        elif "payment" in msg_lower:
            response = (
                "DreamCo Payments supports one-time payments, subscriptions, "
                "recurring billing, and refunds."
            )
        elif "fraud" in msg_lower:
            response = (
                "Fraud detection is available on Growth and Enterprise tiers.  "
                "Risk scores range from 0.0 (low) to 1.0 (high)."
            )
        elif "api" in msg_lower or "key" in msg_lower:
            response = (
                "API key management is available on all tiers.  "
                "Keys can be generated, rotated, and revoked."
            )
        elif "discount" in msg_lower or "dominator" in msg_lower:
            response = (
                "Discount Dominator settings (IDs 401–600) are available on "
                "all tiers for viewing.  Update access requires Growth or higher."
            )
        else:
            response = (
                f"Hello from DreamCo Payments ({self.config.name} tier)!  "
                "I can help with payments, subscriptions, currency conversion, "
                "fraud detection, and reporting."
            )

        return {
            "response": response,
            "bot_name": "dreamco_payments",
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # BuddyAI integration
    # ------------------------------------------------------------------

    def register_with_buddy(self, buddy_bot_instance) -> None:
        """
        Register this bot with a BuddyBot instance.

        Parameters
        ----------
        buddy_bot_instance : BuddyBot
            The BuddyBot orchestrator to register with.
        """
        self._buddy_bot = buddy_bot_instance
        buddy_bot_instance.register_bot("dreamco_payments", self)


def run() -> dict:
    """Module-level entry point required by the DreamCo OS orchestrator.

    Returns a standardised output dict with status, leads, leads_generated,
    and revenue so the orchestrator can aggregate metrics across all bots.
    """
    return {"status": "success", "leads": 0, "leads_generated": 0, "revenue": 750}
