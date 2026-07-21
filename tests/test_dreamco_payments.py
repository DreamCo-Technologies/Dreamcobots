"""
Tests for bots/dreamco_payments/ and BuddyAI/

Covers PaymentProcessor, APIManager, AccountManager, ReportingDashboard,
DreamcoPaymentsBot, and BuddyBot with ~80 test cases.
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.dreamco_payments.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_PAYMENT_PROCESSING,
    FEATURE_CURRENCY_CONVERSION,
    FEATURE_FRAUD_DETECTION,
    FEATURE_CUSTOM_LIMITS,
    FEATURE_ADVANCED_REPORTING,
    FEATURE_DISCOUNT_DOMINATOR,
)
from bots.dreamco_payments.payment_processor import (
    PaymentProcessor,
    PaymentTierError,
    SUPPORTED_CURRENCIES,
)
from bots.dreamco_payments.api_manager import APIManager, APITierError, DREAMCO_STRIPE_KEY
from bots.dreamco_payments.account_manager import AccountManager, AccountTierError
from bots.dreamco_payments.reporting_dashboard import (
    ReportingDashboard,
    DashboardTierError,
    _DD_GROUPS,
)
from bots.dreamco_payments.dreamco_payments import DreamcoPaymentsBot
from BuddyAI.event_bus import EventBus
from BuddyAI.buddy_bot import BuddyBot


# ===========================================================================
# Tier configuration tests
# ===========================================================================

class TestTierConfig:
    """Tests for tiers.py configuration."""

    def test_all_three_tiers_present(self):
        """TIER_CATALOGUE should contain starter, growth, and enterprise."""
        assert set(TIER_CATALOGUE.keys()) == {"starter", "growth", "enterprise"}

    def test_starter_price(self):
        """Starter should cost $29/month."""
        assert get_tier_config(Tier.STARTER).price_usd_monthly == 29.0

    def test_growth_price(self):
        """Growth should cost $99/month."""
        assert get_tier_config(Tier.GROWTH).price_usd_monthly == 99.0

    def test_enterprise_price(self):
        """Enterprise should cost $299/month."""
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 299.0

    def test_starter_transaction_limit(self):
        """Starter allows 1 000 transactions per month."""
        assert get_tier_config(Tier.STARTER).transactions_per_month == 1_000

    def test_growth_transaction_limit(self):
        """Growth allows 10 000 transactions per month."""
        assert get_tier_config(Tier.GROWTH).transactions_per_month == 10_000

    def test_enterprise_is_unlimited(self):
        """Enterprise tier has no transaction cap."""
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited()
        assert cfg.transactions_per_month is None

    def test_list_tiers_returns_three(self):
        """list_tiers() should return exactly 3 configs."""
        assert len(list_tiers()) == 3

    def test_upgrade_path_starter_to_growth(self):
        """Upgrade from STARTER leads to GROWTH."""
        next_tier = get_upgrade_path(Tier.STARTER)
        assert next_tier is not None
        assert next_tier.tier == Tier.GROWTH

    def test_upgrade_path_enterprise_is_none(self):
        """There is no upgrade beyond ENTERPRISE."""
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_starter_has_payment_feature(self):
        """STARTER includes basic payment processing."""
        assert get_tier_config(Tier.STARTER).has_feature(FEATURE_PAYMENT_PROCESSING)

    def test_starter_missing_currency_conversion(self):
        """STARTER does not include currency conversion."""
        assert not get_tier_config(Tier.STARTER).has_feature(FEATURE_CURRENCY_CONVERSION)

    def test_growth_has_currency_conversion(self):
        """GROWTH includes currency conversion."""
        assert get_tier_config(Tier.GROWTH).has_feature(FEATURE_CURRENCY_CONVERSION)

    def test_enterprise_has_all_growth_features(self):
        """ENTERPRISE should include every GROWTH feature."""
        growth_features = set(get_tier_config(Tier.GROWTH).features)
        enterprise_features = set(get_tier_config(Tier.ENTERPRISE).features)
        assert growth_features.issubset(enterprise_features)


# ===========================================================================
# PaymentProcessor tests
# ===========================================================================

class TestPaymentProcessor:
    """Tests for payment_processor.PaymentProcessor."""

    # ---- process_payment --------------------------------------------------

    def test_process_payment_returns_dict(self):
        """process_payment should return a dict with expected keys."""
        proc = PaymentProcessor(Tier.STARTER)
        result = proc.process_payment(99.99, "USD", "card_visa", "cust_1")
        for key in ("status", "transaction_id", "amount", "currency", "customer_id"):
            assert key in result

    def test_process_payment_success_status(self):
        """Successful payment should have status 'success'."""
        proc = PaymentProcessor(Tier.STARTER)
        result = proc.process_payment(50.0, "USD", "card_mc", "cust_2")
        assert result["status"] == "success"

    def test_process_payment_unique_transaction_ids(self):
        """Two payments should produce distinct transaction IDs."""
        proc = PaymentProcessor(Tier.STARTER)
        r1 = proc.process_payment(10.0, "USD", "card", "cust_3")
        r2 = proc.process_payment(10.0, "USD", "card", "cust_3")
        assert r1["transaction_id"] != r2["transaction_id"]

    def test_process_payment_invalid_currency_raises(self):
        """Unknown currency should raise ValueError."""
        proc = PaymentProcessor(Tier.STARTER)
        with pytest.raises(ValueError):
            proc.process_payment(10.0, "XYZ", "card", "cust_4")

    def test_process_payment_negative_amount_raises(self):
        """Non-positive amount should raise ValueError."""
        proc = PaymentProcessor(Tier.STARTER)
        with pytest.raises(ValueError):
            proc.process_payment(-5.0, "USD", "card", "cust_5")

    def test_supported_currencies_count(self):
        """There should be exactly 7 supported currencies."""
        assert len(SUPPORTED_CURRENCIES) == 7

    # ---- subscriptions ----------------------------------------------------

    def test_create_subscription_returns_dict(self):
        """create_subscription should return a dict with subscription_id."""
        proc = PaymentProcessor(Tier.STARTER)
        result = proc.create_subscription("cust_6", "plan_basic", 9.99, "USD")
        assert "subscription_id" in result
        assert result["status"] == "active"

    def test_cancel_subscription_updates_status(self):
        """Cancelling a subscription should change its status to 'cancelled'."""
        proc = PaymentProcessor(Tier.STARTER)
        sub = proc.create_subscription("cust_7", "plan_pro", 29.0, "USD")
        result = proc.cancel_subscription(sub["subscription_id"])
        assert result["status"] == "cancelled"

    def test_cancel_nonexistent_subscription_raises(self):
        """Cancelling an unknown subscription should raise KeyError."""
        proc = PaymentProcessor(Tier.STARTER)
        with pytest.raises(KeyError):
            proc.cancel_subscription("sub_doesnotexist")

    def test_invalid_interval_raises(self):
        """Invalid billing interval should raise ValueError."""
        proc = PaymentProcessor(Tier.STARTER)
        with pytest.raises(ValueError):
            proc.create_subscription("cust_8", "plan", 5.0, "USD", "biannual")

    # ---- currency conversion (GROWTH+) ------------------------------------

    def test_currency_conversion_starter_raises(self):
        """Currency conversion on STARTER should raise PaymentTierError."""
        proc = PaymentProcessor(Tier.STARTER)
        with pytest.raises(PaymentTierError):
            proc.convert_currency(100.0, "USD", "EUR")

    def test_currency_conversion_growth_succeeds(self):
        """Currency conversion on GROWTH should return converted_amount."""
        proc = PaymentProcessor(Tier.GROWTH)
        result = proc.convert_currency(100.0, "USD", "EUR")
        assert "converted_amount" in result
        assert "rate" in result
        assert result["from_currency"] == "USD"
        assert result["to_currency"] == "EUR"

    def test_currency_conversion_same_currency(self):
        """Converting USD→USD should yield rate of 1.0."""
        proc = PaymentProcessor(Tier.GROWTH)
        result = proc.convert_currency(50.0, "USD", "USD")
        assert abs(result["rate"] - 1.0) < 1e-6

    # ---- recurring billing (GROWTH+) --------------------------------------

    def test_recurring_billing_starter_raises(self):
        """Recurring billing on STARTER should raise PaymentTierError."""
        proc = PaymentProcessor(Tier.STARTER)
        with pytest.raises(PaymentTierError):
            proc.process_recurring_billing("sub_fake")

    def test_recurring_billing_growth_succeeds(self):
        """Recurring billing on GROWTH should create a new transaction."""
        proc = PaymentProcessor(Tier.GROWTH)
        sub = proc.create_subscription("cust_9", "plan_x", 19.99, "USD")
        result = proc.process_recurring_billing(sub["subscription_id"])
        assert result["billing_type"] == "recurring"
        assert result["status"] == "success"

    def test_recurring_billing_cancelled_sub_raises(self):
        """Billing a cancelled subscription should raise ValueError."""
        proc = PaymentProcessor(Tier.GROWTH)
        sub = proc.create_subscription("cust_10", "plan_y", 9.0, "USD")
        proc.cancel_subscription(sub["subscription_id"])
        with pytest.raises(ValueError):
            proc.process_recurring_billing(sub["subscription_id"])

    # ---- refunds ----------------------------------------------------------

    def test_refund_full_amount(self):
        """Full refund should return a refund record with correct amount."""
        proc = PaymentProcessor(Tier.STARTER)
        txn = proc.process_payment(75.0, "USD", "card", "cust_11")
        refund = proc.refund_payment(txn["transaction_id"])
        assert refund["refund_amount"] == 75.0
        assert refund["status"] == "refunded"

    def test_refund_partial_amount(self):
        """Partial refund should reflect the specified amount."""
        proc = PaymentProcessor(Tier.STARTER)
        txn = proc.process_payment(100.0, "USD", "card", "cust_12")
        refund = proc.refund_payment(txn["transaction_id"], 30.0)
        assert refund["refund_amount"] == 30.0

    def test_refund_exceeds_original_raises(self):
        """Refund amount exceeding original should raise ValueError."""
        proc = PaymentProcessor(Tier.STARTER)
        txn = proc.process_payment(50.0, "USD", "card", "cust_13")
        with pytest.raises(ValueError):
            proc.refund_payment(txn["transaction_id"], 100.0)

    def test_refund_unknown_transaction_raises(self):
        """Refunding an unknown transaction_id should raise KeyError."""
        proc = PaymentProcessor(Tier.STARTER)
        with pytest.raises(KeyError):
            proc.refund_payment("txn_doesnotexist")

    # ---- list transactions ------------------------------------------------

    def test_list_transactions_returns_list(self):
        """list_transactions should return a list for a known customer."""
        proc = PaymentProcessor(Tier.STARTER)
        proc.process_payment(10.0, "USD", "card", "cust_14")
        proc.process_payment(20.0, "USD", "card", "cust_14")
        results = proc.list_transactions("cust_14")
        assert isinstance(results, list)
        assert len(results) == 2

    def test_list_transactions_filters_by_customer(self):
        """Transactions for one customer should not include another's."""
        proc = PaymentProcessor(Tier.STARTER)
        proc.process_payment(10.0, "USD", "card", "cust_A")
        proc.process_payment(20.0, "USD", "card", "cust_B")
        assert all(t["customer_id"] == "cust_A" for t in proc.list_transactions("cust_A"))


# ===========================================================================
# APIManager tests
# ===========================================================================

class TestAPIManager:
    """Tests for api_manager.APIManager."""

    def test_generate_api_key_returns_dict(self):
        """generate_api_key should return a dict with key_id and key."""
        mgr = APIManager(Tier.STARTER)
        result = mgr.generate_api_key("test_key", ["payments:read"])
        assert "key_id" in result
        assert "key" in result
        assert result["status"] == "active"

    def test_generated_key_is_hex_sha256(self):
        """Generated key should be a 64-char hex string (sha256)."""
        mgr = APIManager(Tier.STARTER)
        result = mgr.generate_api_key("key1", [])
        assert len(result["key"]) == 64
        int(result["key"], 16)  # raises if not valid hex

    def test_generate_unique_keys(self):
        """Each call to generate_api_key should produce a unique key."""
        mgr = APIManager(Tier.STARTER)
        k1 = mgr.generate_api_key("k1", [])
        k2 = mgr.generate_api_key("k2", [])
        assert k1["key"] != k2["key"]
        assert k1["key_id"] != k2["key_id"]

    def test_rotate_api_key_changes_value(self):
        """rotate_api_key should return a new, different key value."""
        mgr = APIManager(Tier.STARTER)
        orig = mgr.generate_api_key("rot", ["read"])
        rotated = mgr.rotate_api_key(orig["key_id"])
        assert rotated["key"] != orig["key"]

    def test_rotate_unknown_key_raises(self):
        """Rotating an unknown key_id should raise KeyError."""
        mgr = APIManager(Tier.STARTER)
        with pytest.raises(KeyError):
            mgr.rotate_api_key("kid_doesnotexist")

    def test_revoke_api_key_sets_status(self):
        """revoke_api_key should set the key's status to 'revoked'."""
        mgr = APIManager(Tier.STARTER)
        k = mgr.generate_api_key("to_revoke", [])
        result = mgr.revoke_api_key(k["key_id"])
        assert result["status"] == "revoked"

    def test_validate_active_key_returns_true(self):
        """A freshly generated key should pass validation."""
        mgr = APIManager(Tier.STARTER)
        k = mgr.generate_api_key("valid", [])
        assert mgr.validate_api_key(k["key"]) is True

    def test_validate_revoked_key_returns_false(self):
        """A revoked key should not pass validation."""
        mgr = APIManager(Tier.STARTER)
        k = mgr.generate_api_key("soon_revoked", [])
        mgr.revoke_api_key(k["key_id"])
        assert mgr.validate_api_key(k["key"]) is False

    def test_validate_random_string_returns_false(self):
        """A random string should not validate."""
        mgr = APIManager(Tier.STARTER)
        assert mgr.validate_api_key("totally_fake_key_value") is False

    def test_record_api_call_increments_count(self):
        """record_api_call should increment request_count."""
        mgr = APIManager(Tier.STARTER)
        k = mgr.generate_api_key("track", [])
        mgr.record_api_call(k["key_id"])
        mgr.record_api_call(k["key_id"])
        usage = mgr.get_usage_analytics(k["key_id"])
        assert usage["request_count"] == 2

    def test_get_usage_analytics_keys(self):
        """get_usage_analytics should return request_count and last_used."""
        mgr = APIManager(Tier.STARTER)
        k = mgr.generate_api_key("analytics", ["read"])
        usage = mgr.get_usage_analytics(k["key_id"])
        assert "request_count" in usage
        assert "last_used" in usage

    def test_list_api_keys_omits_raw_key(self):
        """list_api_keys should not expose the raw key value."""
        mgr = APIManager(Tier.STARTER)
        mgr.generate_api_key("no_leak", [])
        for entry in mgr.list_api_keys():
            assert "key" not in entry

    def test_dreamco_stripe_key_is_string(self):
        """DREAMCO_STRIPE_KEY should be a non-empty string placeholder."""
        assert isinstance(DREAMCO_STRIPE_KEY, str)
        assert len(DREAMCO_STRIPE_KEY) > 0

    def test_dreamco_stripe_key_is_not_real(self):
        """DREAMCO_STRIPE_KEY should not be a live Stripe secret key."""
        # A live key starts with 'sk_live_' – that must never be committed
        assert not DREAMCO_STRIPE_KEY.startswith("sk_live_"), (
            "DREAMCO_STRIPE_KEY must not be a live Stripe secret key"
        )


# ===========================================================================
# AccountManager tests
# ===========================================================================

class TestAccountManager:
    """Tests for account_manager.AccountManager."""

    def test_onboard_user_returns_dict(self):
        """onboard_user should return a profile dict with user_id."""
        mgr = AccountManager(Tier.STARTER)
        result = mgr.onboard_user("u1", "Alice", "alice@example.com")
        assert result["user_id"] == "u1"
        assert result["status"] == "active"

    def test_onboard_user_real_estate_has_hints(self):
        """Real-estate accounts should include automation_hints."""
        mgr = AccountManager(Tier.ENTERPRISE)
        result = mgr.onboard_user("u2", "Bob", "bob@re.com", "real_estate")
        assert len(result["automation_hints"]) > 0

    def test_onboard_user_auto_dealer_has_hints(self):
        """Auto-dealer accounts should include automation_hints."""
        mgr = AccountManager(Tier.ENTERPRISE)
        result = mgr.onboard_user("u3", "Carol", "carol@cars.com", "auto_dealer")
        assert len(result["automation_hints"]) > 0

    def test_onboard_user_standard_no_hints(self):
        """Standard accounts should have no automation hints."""
        mgr = AccountManager(Tier.STARTER)
        result = mgr.onboard_user("u4", "Dave", "dave@co.com", "standard")
        assert result["automation_hints"] == []

    def test_onboard_user_invalid_business_type_raises(self):
        """Unknown business_type should raise ValueError."""
        mgr = AccountManager(Tier.STARTER)
        with pytest.raises(ValueError):
            mgr.onboard_user("u5", "Eve", "e@e.com", "invalid_type")

    def test_verify_user_basic_level(self):
        """Verification with only doc_id should yield 'basic' level."""
        mgr = AccountManager(Tier.STARTER)
        mgr.onboard_user("u6", "Frank", "f@f.com")
        result = mgr.verify_user("u6", {"doc_id": "D123", "id_type": "passport"})
        assert result["verification_level"] == "basic"
        assert result["status"] == "verified"

    def test_verify_user_enhanced_level(self):
        """Verification with address proof should yield 'enhanced' level."""
        mgr = AccountManager(Tier.STARTER)
        mgr.onboard_user("u7", "Grace", "g@g.com")
        result = mgr.verify_user(
            "u7",
            {"doc_id": "D456", "id_type": "driver_license", "address_proof": True},
        )
        assert result["verification_level"] == "enhanced"

    def test_verify_unknown_user_raises(self):
        """Verifying an unknown user should raise KeyError."""
        mgr = AccountManager(Tier.STARTER)
        with pytest.raises(KeyError):
            mgr.verify_user("no_such_user", {"doc_id": "X"})

    def test_detect_fraud_starter_raises(self):
        """Fraud detection on STARTER should raise AccountTierError."""
        mgr = AccountManager(Tier.STARTER)
        with pytest.raises(AccountTierError):
            mgr.detect_fraud({"amount": 100})

    def test_detect_fraud_low_risk(self):
        """Normal transaction data should yield a low risk score."""
        mgr = AccountManager(Tier.GROWTH)
        result = mgr.detect_fraud({"amount": 50, "currency": "USD"})
        assert result["risk_score"] < 0.3
        assert result["risk_level"] == "low"

    def test_detect_fraud_high_amount_flagged(self):
        """A very high amount should trigger the high_amount flag."""
        mgr = AccountManager(Tier.GROWTH)
        result = mgr.detect_fraud({"amount": 50_000, "currency": "USD"})
        assert "high_amount" in result["flags"]

    def test_detect_fraud_returns_required_keys(self):
        """detect_fraud result should contain risk_score, risk_level, flags."""
        mgr = AccountManager(Tier.GROWTH)
        result = mgr.detect_fraud({"amount": 100})
        for key in ("risk_score", "risk_level", "flags"):
            assert key in result

    def test_send_notification_returns_dict(self):
        """send_notification should return a notification record."""
        mgr = AccountManager(Tier.STARTER)
        mgr.onboard_user("u8", "Hank", "h@h.com")
        result = mgr.send_notification("u8", "payment_received", "You got paid!")
        assert result["event_type"] == "payment_received"
        assert "notification_id" in result

    def test_get_user_profile_returns_correct_user(self):
        """get_user_profile should return data for the requested user."""
        mgr = AccountManager(Tier.STARTER)
        mgr.onboard_user("u9", "Iris", "i@i.com")
        profile = mgr.get_user_profile("u9")
        assert profile["name"] == "Iris"

    def test_update_user_limits_starter_raises(self):
        """update_user_limits on STARTER should raise AccountTierError."""
        mgr = AccountManager(Tier.STARTER)
        mgr.onboard_user("u10", "Jack", "j@j.com")
        with pytest.raises(AccountTierError):
            mgr.update_user_limits("u10", {"daily_max": 5000})

    def test_update_user_limits_enterprise_succeeds(self):
        """update_user_limits on ENTERPRISE should persist the limit."""
        mgr = AccountManager(Tier.ENTERPRISE)
        mgr.onboard_user("u11", "Kate", "k@k.com")
        profile = mgr.update_user_limits("u11", {"daily_max": 50_000})
        assert profile["limits"]["daily_max"] == 50_000


# ===========================================================================
# ReportingDashboard tests
# ===========================================================================

class TestReportingDashboard:
    """Tests for reporting_dashboard.ReportingDashboard."""

    def test_financial_summary_starter_raises(self):
        """Financial summary on STARTER should raise DashboardTierError."""
        dash = ReportingDashboard(Tier.STARTER)
        with pytest.raises(DashboardTierError):
            dash.get_financial_summary()

    def test_financial_summary_growth_returns_dict(self):
        """Financial summary on GROWTH should return expected keys."""
        dash = ReportingDashboard(Tier.GROWTH)
        result = dash.get_financial_summary("monthly")
        for key in ("total_revenue", "total_transactions", "period"):
            assert key in result

    def test_financial_summary_invalid_period_raises(self):
        """Unknown period should raise ValueError."""
        dash = ReportingDashboard(Tier.GROWTH)
        with pytest.raises(ValueError):
            dash.get_financial_summary("quarterly")

    def test_get_bot_performance_starter_raises(self):
        """Bot performance on STARTER should raise DashboardTierError."""
        dash = ReportingDashboard(Tier.STARTER)
        with pytest.raises(DashboardTierError):
            dash.get_bot_performance("ai_chatbot")

    def test_get_bot_performance_growth_returns_data(self):
        """Bot performance on GROWTH should return uptime and request data."""
        dash = ReportingDashboard(Tier.GROWTH)
        result = dash.get_bot_performance("ai_chatbot")
        assert "uptime_pct" in result
        assert result["bot_name"] == "ai_chatbot"

    def test_get_bot_performance_unknown_bot_raises(self):
        """Unknown bot name should raise KeyError."""
        dash = ReportingDashboard(Tier.GROWTH)
        with pytest.raises(KeyError):
            dash.get_bot_performance("nonexistent_bot")

    def test_get_all_bots_performance_returns_dict(self):
        """get_all_bots_performance should return a non-empty dict."""
        dash = ReportingDashboard(Tier.GROWTH)
        result = dash.get_all_bots_performance()
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_discount_dominator_setting_401(self):
        """Setting 401 should be in the 'analytics' group."""
        dash = ReportingDashboard(Tier.STARTER)
        result = dash.get_discount_dominator_settings(401)
        assert result["group"] == "analytics"
        assert result["setting_id"] == 401

    def test_discount_dominator_setting_600(self):
        """Setting 600 should be the last 'behavioral' setting."""
        dash = ReportingDashboard(Tier.STARTER)
        result = dash.get_discount_dominator_settings(600)
        assert result["group"] == "behavioral"

    def test_discount_dominator_invalid_id_raises(self):
        """Out-of-range setting ID should raise KeyError."""
        dash = ReportingDashboard(Tier.STARTER)
        with pytest.raises(KeyError):
            dash.get_discount_dominator_settings(400)

    def test_list_discount_dominator_analytics_count(self):
        """The analytics group should contain exactly 50 settings."""
        dash = ReportingDashboard(Tier.STARTER)
        settings = dash.list_discount_dominator_settings("analytics")
        assert len(settings) == 50

    def test_list_discount_dominator_behavioral_count(self):
        """The behavioral group should contain exactly 20 settings."""
        dash = ReportingDashboard(Tier.STARTER)
        settings = dash.list_discount_dominator_settings("behavioral")
        assert len(settings) == 20

    def test_list_discount_dominator_enterprise_count(self):
        """The enterprise group should contain exactly 30 settings."""
        dash = ReportingDashboard(Tier.STARTER)
        settings = dash.list_discount_dominator_settings("enterprise")
        assert len(settings) == 30

    def test_list_discount_dominator_invalid_group_raises(self):
        """Unknown group name should raise ValueError."""
        dash = ReportingDashboard(Tier.STARTER)
        with pytest.raises(ValueError):
            dash.list_discount_dominator_settings("unknown_group")

    def test_update_setting_starter_raises(self):
        """Updating a setting on STARTER should raise DashboardTierError."""
        dash = ReportingDashboard(Tier.STARTER)
        with pytest.raises(DashboardTierError):
            dash.update_discount_dominator_setting(401, False)

    def test_update_setting_growth_succeeds(self):
        """Updating a setting on GROWTH should persist the new value."""
        dash = ReportingDashboard(Tier.GROWTH)
        result = dash.update_discount_dominator_setting(401, False)
        assert result["value"] is False

    def test_export_json_all_tiers(self):
        """JSON export should succeed on all tiers."""
        for tier in Tier:
            dash = ReportingDashboard(tier)
            result = dash.export_report("json")
            assert result["format"] == "json"

    def test_export_csv_starter_raises(self):
        """CSV export on STARTER should raise DashboardTierError."""
        dash = ReportingDashboard(Tier.STARTER)
        with pytest.raises(DashboardTierError):
            dash.export_report("csv")

    def test_export_pdf_enterprise_only(self):
        """PDF export should succeed on ENTERPRISE, fail on GROWTH."""
        dash_ent = ReportingDashboard(Tier.ENTERPRISE)
        result = dash_ent.export_report("pdf")
        assert result["format"] == "pdf"

        dash_growth = ReportingDashboard(Tier.GROWTH)
        with pytest.raises(DashboardTierError):
            dash_growth.export_report("pdf")

    def test_export_invalid_format_raises(self):
        """Unknown export format should raise ValueError."""
        dash = ReportingDashboard(Tier.ENTERPRISE)
        with pytest.raises(ValueError):
            dash.export_report("xlsx")


# ===========================================================================
# DreamcoPaymentsBot integration tests
# ===========================================================================

class TestDreamcoPaymentsBot:
    """End-to-end tests for DreamcoPaymentsBot."""

    def test_default_tier_is_starter(self):
        """Default tier should be STARTER."""
        bot = DreamcoPaymentsBot()
        assert bot.tier == Tier.STARTER

    def test_process_payment_end_to_end(self):
        """process_payment should work through the bot facade."""
        bot = DreamcoPaymentsBot(Tier.STARTER)
        result = bot.process_payment(25.0, "USD", "card", "cust_e2e")
        assert result["status"] == "success"

    def test_create_and_cancel_subscription(self):
        """create_subscription + cancel_subscription round-trip."""
        bot = DreamcoPaymentsBot(Tier.STARTER)
        sub = bot.create_subscription("cust_sub", "plan_basic", 9.99, "USD")
        cancel = bot.cancel_subscription(sub["subscription_id"])
        assert cancel["status"] == "cancelled"

    def test_convert_currency_growth(self):
        """convert_currency should work on GROWTH tier."""
        bot = DreamcoPaymentsBot(Tier.GROWTH)
        result = bot.convert_currency(100.0, "USD", "GBP")
        assert "converted_amount" in result

    def test_generate_and_validate_api_key(self):
        """generate + validate API key round-trip."""
        bot = DreamcoPaymentsBot(Tier.STARTER)
        k = bot.generate_api_key("my_key", ["read"])
        assert bot.validate_api_key(k["key"]) is True

    def test_rotate_api_key(self):
        """rotate_api_key should return a new key value."""
        bot = DreamcoPaymentsBot(Tier.STARTER)
        k = bot.generate_api_key("rot_key", [])
        rotated = bot.rotate_api_key(k["key_id"])
        assert rotated["key"] != k["key"]

    def test_onboard_user(self):
        """onboard_user should return a valid user profile."""
        bot = DreamcoPaymentsBot(Tier.STARTER)
        result = bot.onboard_user("u_e2e", "Test User", "test@example.com")
        assert result["user_id"] == "u_e2e"

    def test_detect_fraud_growth(self):
        """detect_fraud should work on GROWTH tier."""
        bot = DreamcoPaymentsBot(Tier.GROWTH)
        result = bot.detect_fraud({"amount": 9999, "currency": "USD"})
        assert "risk_score" in result

    def test_get_financial_summary_growth(self):
        """get_financial_summary should work on GROWTH tier."""
        bot = DreamcoPaymentsBot(Tier.GROWTH)
        result = bot.get_financial_summary("monthly")
        assert "total_revenue" in result

    def test_get_bot_performance(self):
        """get_bot_performance should return metrics for known bots."""
        bot = DreamcoPaymentsBot(Tier.GROWTH)
        result = bot.get_bot_performance("dreamco_payments")
        assert result["bot_name"] == "dreamco_payments"

    def test_get_discount_dominator_settings(self):
        """get_discount_dominator_settings should return a setting dict."""
        bot = DreamcoPaymentsBot(Tier.STARTER)
        result = bot.get_discount_dominator_settings(450)
        assert result["setting_id"] == 450

    def test_describe_tier_contains_name(self):
        """describe_tier should include the tier name."""
        bot = DreamcoPaymentsBot(Tier.STARTER)
        description = bot.describe_tier()
        assert "Starter" in description

    def test_describe_tier_contains_price(self):
        """describe_tier should include the price."""
        bot = DreamcoPaymentsBot(Tier.GROWTH)
        description = bot.describe_tier()
        assert "99" in description

    def test_describe_tier_enterprise_no_upgrade(self):
        """Enterprise describe_tier should mention top-tier plan."""
        bot = DreamcoPaymentsBot(Tier.ENTERPRISE)
        description = bot.describe_tier()
        assert "top-tier" in description

    def test_chat_returns_response(self):
        """chat() should return a dict with 'response' key."""
        bot = DreamcoPaymentsBot(Tier.STARTER)
        result = bot.chat("Hello!")
        assert "response" in result
        assert "bot_name" in result

    def test_chat_tier_query(self):
        """Asking about 'tier' should include plan info in response."""
        bot = DreamcoPaymentsBot(Tier.STARTER)
        result = bot.chat("What is my current tier?")
        assert "Starter" in result["response"]

    def test_register_with_buddy(self):
        """register_with_buddy should register the bot in BuddyBot."""
        buddy = BuddyBot()
        bot = DreamcoPaymentsBot(Tier.STARTER)
        bot.register_with_buddy(buddy)
        assert "dreamco_payments" in buddy.list_bots()


# ===========================================================================
# BuddyBot tests
# ===========================================================================

class TestBuddyBot:
    """Tests for BuddyAI.buddy_bot.BuddyBot and EventBus."""

    def test_register_and_list_bots(self):
        """Registered bots should appear in list_bots()."""
        buddy = BuddyBot()
        bot = DreamcoPaymentsBot(Tier.STARTER)
        buddy.register_bot("payments", bot)
        assert "payments" in buddy.list_bots()

    def test_unregister_bot(self):
        """Unregistered bots should not appear in list_bots()."""
        buddy = BuddyBot()
        bot = DreamcoPaymentsBot(Tier.STARTER)
        buddy.register_bot("payments", bot)
        buddy.unregister_bot("payments")
        assert "payments" not in buddy.list_bots()

    def test_route_message_returns_response(self):
        """route_message should return the bot's chat() response."""
        buddy = BuddyBot()
        buddy.register_bot("payments", DreamcoPaymentsBot(Tier.STARTER))
        result = buddy.route_message("payments", "Hello")
        assert "response" in result

    def test_route_message_unknown_bot_raises(self):
        """Routing to an unregistered bot should raise KeyError."""
        buddy = BuddyBot()
        with pytest.raises(KeyError):
            buddy.route_message("nonexistent", "Hi")

    def test_broadcast_reaches_all_bots(self):
        """broadcast should send messages to all registered bots."""
        buddy = BuddyBot()
        buddy.register_bot("payments_a", DreamcoPaymentsBot(Tier.STARTER))
        buddy.register_bot("payments_b", DreamcoPaymentsBot(Tier.GROWTH))
        results = buddy.broadcast("status check")
        assert "payments_a" in results
        assert "payments_b" in results

    def test_event_bus_publish_subscribe(self):
        """EventBus should invoke subscriber callbacks on publish."""
        bus = EventBus()
        received = []
        bus.subscribe("test_event", received.append)
        bus.publish("test_event", {"key": "value"})
        assert len(received) == 1
        assert received[0]["key"] == "value"

    def test_event_bus_unsubscribe(self):
        """Unsubscribed callbacks should not be invoked."""
        bus = EventBus()
        received = []
        bus.subscribe("evt", received.append)
        bus.unsubscribe("evt", received.append)
        bus.publish("evt", "data")
        assert received == []

    def test_event_bus_get_events(self):
        """get_events should return all published event payloads."""
        bus = EventBus()
        bus.publish("order", {"id": 1})
        bus.publish("order", {"id": 2})
        events = bus.get_events("order")
        assert len(events) == 2

    def test_register_bot_fires_event(self):
        """Registering a bot should publish a bot_registered event."""
        buddy = BuddyBot()
        buddy.register_bot("test_bot", DreamcoPaymentsBot(Tier.STARTER))
        events = buddy.event_bus.get_events("bot_registered")
        assert any(e["name"] == "test_bot" for e in events)

    def test_list_bots_sorted(self):
        """list_bots should return bot names in alphabetical order."""
        buddy = BuddyBot()
        buddy.register_bot("z_bot", DreamcoPaymentsBot(Tier.STARTER))
        buddy.register_bot("a_bot", DreamcoPaymentsBot(Tier.STARTER))
        names = buddy.list_bots()
        assert names == sorted(names)
