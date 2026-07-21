"""
Tests for the DreamCobots token billing system.

Covers:
- Tier configuration
- TokenManager (add, deduct, balance, daily reset)
- SubscriptionManager (create, change, cancel, history)
- BillingSystem facade (create account, purchase, deduct, subscribe, report)
- BuddyBot consumption tracking and billing integration
"""

import pytest
from datetime import date, timedelta

from bots.token_billing.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    list_tiers,
    FEATURE_ALL_109_MODELS,
    FEATURE_FULL_CAPACITY,
    FEATURE_LIMITED_CAPACITY,
)
from bots.token_billing.token_manager import TokenManager, InsufficientTokensError
from bots.token_billing.subscription_manager import SubscriptionManager, SubscriptionError
from bots.token_billing.billing_system import BillingSystem
from BuddyAI.buddy_bot import BuddyBot


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def billing():
    return BillingSystem()


@pytest.fixture
def billing_with_user():
    b = BillingSystem()
    b.create_account("alice", Tier.FREE)
    return b


@pytest.fixture
def token_mgr():
    tm = TokenManager()
    tm.create_account("alice")
    return tm


@pytest.fixture
def sub_mgr():
    sm = SubscriptionManager()
    sm.initialize_account("alice", Tier.FREE)
    return sm


# ---------------------------------------------------------------------------
# Tier configuration tests
# ---------------------------------------------------------------------------

class TestTierConfig:
    def test_all_tiers_present(self):
        tiers = list_tiers()
        tier_enums = {t.tier for t in tiers}
        assert Tier.FREE in tier_enums
        assert Tier.PRO_MONTHLY in tier_enums
        assert Tier.PRO_ANNUAL in tier_enums
        assert Tier.ENTERPRISE_MONTHLY in tier_enums
        assert Tier.ENTERPRISE_ANNUAL in tier_enums

    def test_free_tier_is_free(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0
        assert cfg.price_usd_total == 0.0

    def test_free_tier_has_limited_capacity(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_LIMITED_CAPACITY)
        assert not cfg.full_capacity

    def test_free_tier_daily_tokens(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.daily_tokens == 100

    def test_free_tier_all_109_models(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.ai_models_count == 109
        assert cfg.has_feature(FEATURE_ALL_109_MODELS)

    def test_pro_monthly_price(self):
        cfg = get_tier_config(Tier.PRO_MONTHLY)
        assert cfg.price_usd_monthly == 49.0
        assert cfg.price_usd_total == 49.0

    def test_pro_annual_cheaper_than_monthly(self):
        monthly = get_tier_config(Tier.PRO_MONTHLY)
        annual = get_tier_config(Tier.PRO_ANNUAL)
        assert annual.price_usd_monthly < monthly.price_usd_monthly
        # Verify computed: 490/12 = 40.83
        assert annual.price_usd_monthly == round(490.0 / 12, 2)

    def test_enterprise_monthly_unlimited_tokens(self):
        cfg = get_tier_config(Tier.ENTERPRISE_MONTHLY)
        assert cfg.daily_tokens is None
        assert cfg.is_unlimited()

    def test_enterprise_annual_unlimited_tokens(self):
        cfg = get_tier_config(Tier.ENTERPRISE_ANNUAL)
        assert cfg.daily_tokens is None
        assert cfg.is_unlimited()

    def test_pro_full_capacity(self):
        cfg = get_tier_config(Tier.PRO_MONTHLY)
        assert cfg.full_capacity
        assert cfg.has_feature(FEATURE_FULL_CAPACITY)

    def test_enterprise_full_capacity(self):
        cfg = get_tier_config(Tier.ENTERPRISE_MONTHLY)
        assert cfg.full_capacity

    def test_list_tiers_count(self):
        assert len(list_tiers()) == 5

    def test_tier_config_instance(self):
        cfg = get_tier_config(Tier.FREE)
        assert isinstance(cfg, TierConfig)


# ---------------------------------------------------------------------------
# TokenManager tests
# ---------------------------------------------------------------------------

class TestTokenManager:
    def test_create_account(self, token_mgr):
        account = token_mgr.get_account("alice")
        assert account.user_id == "alice"
        assert account.purchased_tokens == 0

    def test_create_duplicate_account_is_idempotent(self):
        tm = TokenManager()
        tm.create_account("bob")
        tm.create_account("bob")  # Should not raise
        assert tm.get_account("bob").user_id == "bob"

    def test_get_unknown_account_raises(self, token_mgr):
        with pytest.raises(KeyError):
            token_mgr.get_account("unknown_user")

    def test_add_tokens(self, token_mgr):
        balance = token_mgr.add_tokens("alice", 500)
        assert balance == 500

    def test_add_tokens_accumulate(self, token_mgr):
        token_mgr.add_tokens("alice", 100)
        balance = token_mgr.add_tokens("alice", 200)
        assert balance == 300

    def test_add_zero_tokens_raises(self, token_mgr):
        with pytest.raises(ValueError):
            token_mgr.add_tokens("alice", 0)

    def test_add_negative_tokens_raises(self, token_mgr):
        with pytest.raises(ValueError):
            token_mgr.add_tokens("alice", -10)

    def test_deduct_purchased_tokens(self, token_mgr):
        token_mgr.add_tokens("alice", 100)
        remaining = token_mgr.deduct_tokens("alice", 30, daily_allowance=50)
        assert remaining == 70

    def test_deduct_uses_daily_allowance_when_no_purchased(self, token_mgr):
        remaining = token_mgr.deduct_tokens("alice", 10, daily_allowance=50)
        account = token_mgr.get_account("alice")
        assert account.purchased_tokens == 0
        assert account.daily_tokens_used == 10

    def test_deduct_insufficient_tokens_raises(self, token_mgr):
        with pytest.raises(InsufficientTokensError):
            token_mgr.deduct_tokens("alice", 200, daily_allowance=50)

    def test_deduct_zero_raises(self, token_mgr):
        with pytest.raises(ValueError):
            token_mgr.deduct_tokens("alice", 0, daily_allowance=50)

    def test_daily_reset(self, token_mgr):
        token_mgr.deduct_tokens("alice", 50, daily_allowance=100)
        account = token_mgr.get_account("alice")
        # Simulate a day passing
        yesterday = date.today() - timedelta(days=1)
        account.last_daily_reset = yesterday
        account.reset_daily_if_needed(100)
        assert account.daily_tokens_used == 0

    def test_get_balance(self, token_mgr):
        token_mgr.add_tokens("alice", 100)
        balance = token_mgr.get_balance("alice", daily_allowance=50)
        assert balance["purchased_tokens"] == 100
        assert balance["daily_tokens_remaining"] == 50
        assert balance["total_available"] == 150

    def test_ledger_records_transactions(self, token_mgr):
        token_mgr.add_tokens("alice", 100, description="starter pack")
        token_mgr.deduct_tokens("alice", 10, daily_allowance=50, description="test call")
        ledger = token_mgr.get_ledger("alice")
        assert len(ledger) == 2
        assert ledger[0].delta == 100
        assert ledger[1].delta == -10


# ---------------------------------------------------------------------------
# SubscriptionManager tests
# ---------------------------------------------------------------------------

class TestSubscriptionManager:
    def test_initialize_free_account(self, sub_mgr):
        record = sub_mgr.get_subscription("alice")
        assert record.tier == Tier.FREE

    def test_initialize_duplicate_raises(self, sub_mgr):
        with pytest.raises(SubscriptionError):
            sub_mgr.initialize_account("alice", Tier.FREE)

    def test_get_unknown_subscription_raises(self, sub_mgr):
        with pytest.raises(KeyError):
            sub_mgr.get_subscription("unknown")

    def test_change_tier(self, sub_mgr):
        sub_mgr.change_tier("alice", Tier.PRO_MONTHLY)
        record = sub_mgr.get_subscription("alice")
        assert record.tier == Tier.PRO_MONTHLY

    def test_cancel_reverts_to_free(self, sub_mgr):
        sub_mgr.change_tier("alice", Tier.PRO_MONTHLY)
        sub_mgr.cancel_subscription("alice")
        record = sub_mgr.get_subscription("alice")
        assert record.tier == Tier.FREE

    def test_subscription_history(self, sub_mgr):
        sub_mgr.change_tier("alice", Tier.PRO_MONTHLY)
        sub_mgr.change_tier("alice", Tier.ENTERPRISE_MONTHLY)
        history = sub_mgr.get_history("alice")
        assert len(history) == 3  # FREE -> PRO -> ENTERPRISE
        assert history[0].tier == Tier.FREE
        assert history[1].tier == Tier.PRO_MONTHLY
        assert history[2].tier == Tier.ENTERPRISE_MONTHLY

    def test_previous_record_gets_cancelled_at(self, sub_mgr):
        sub_mgr.change_tier("alice", Tier.PRO_MONTHLY)
        history = sub_mgr.get_history("alice")
        assert history[0].cancelled_at is not None

    def test_get_tier_config(self, sub_mgr):
        sub_mgr.change_tier("alice", Tier.PRO_ANNUAL)
        cfg = sub_mgr.get_tier_config("alice")
        assert cfg.tier == Tier.PRO_ANNUAL


# ---------------------------------------------------------------------------
# BillingSystem tests
# ---------------------------------------------------------------------------

class TestBillingSystem:
    def test_create_account_returns_user_id(self, billing):
        uid = billing.create_account("bob", Tier.FREE)
        assert uid == "bob"

    def test_get_account_details(self, billing_with_user):
        account = billing_with_user.get_account("alice")
        assert account["user_id"] == "alice"
        assert account["tier"] == Tier.FREE.value
        assert account["daily_tokens"] == 100
        assert account["full_capacity"] is False

    def test_purchase_tokens(self, billing_with_user):
        balance = billing_with_user.purchase_tokens("alice", 500)
        assert balance == 500

    def test_deduct_tokens(self, billing_with_user):
        billing_with_user.purchase_tokens("alice", 100)
        remaining = billing_with_user.deduct_tokens("alice", 10)
        assert remaining == 90

    def test_deduct_insufficient_raises(self, billing_with_user):
        with pytest.raises(InsufficientTokensError):
            # Free tier has 100 daily tokens and 0 purchased; requesting 200 fails
            billing_with_user.deduct_tokens("alice", 200)

    def test_get_balance(self, billing_with_user):
        billing_with_user.purchase_tokens("alice", 200)
        balance = billing_with_user.get_balance("alice")
        assert balance["purchased_tokens"] == 200
        assert balance["daily_tokens_remaining"] == 100
        assert balance["total_available"] == 300

    def test_create_subscription_pro_monthly(self, billing_with_user):
        account = billing_with_user.create_subscription("alice", Tier.PRO_MONTHLY)
        assert account["tier"] == Tier.PRO_MONTHLY.value
        assert account["daily_tokens"] == 10_000

    def test_create_subscription_enterprise_unlimited(self, billing_with_user):
        account = billing_with_user.create_subscription("alice", Tier.ENTERPRISE_MONTHLY)
        assert account["daily_tokens"] is None

    def test_cancel_subscription(self, billing_with_user):
        billing_with_user.create_subscription("alice", Tier.PRO_MONTHLY)
        account = billing_with_user.cancel_subscription("alice")
        assert account["tier"] == Tier.FREE.value

    def test_get_usage_report_structure(self, billing_with_user):
        billing_with_user.purchase_tokens("alice", 100)
        billing_with_user.deduct_tokens("alice", 5, description="test")
        report = billing_with_user.get_usage_report("alice")
        assert report["user_id"] == "alice"
        assert "account" in report
        assert "balance" in report
        assert "subscription_history" in report
        assert "ledger" in report
        assert len(report["ledger"]) == 2

    def test_enterprise_daily_deduction_uses_unlimited_allowance(self, billing):
        billing.create_account("enterprise_user", Tier.ENTERPRISE_MONTHLY)
        # With unlimited daily we can deduct without purchased tokens
        remaining = billing.deduct_tokens("enterprise_user", 5_000)
        assert remaining == 0  # all from daily allowance

    def test_pro_annual_cheaper_per_month(self):
        monthly_cfg = get_tier_config(Tier.PRO_MONTHLY)
        annual_cfg = get_tier_config(Tier.PRO_ANNUAL)
        assert annual_cfg.price_usd_monthly < monthly_cfg.price_usd_monthly


# ---------------------------------------------------------------------------
# BuddyBot consumption tracking tests
# ---------------------------------------------------------------------------

class _MockBot:
    """Minimal bot stub for testing."""
    def chat(self, message: str) -> dict:
        return {"reply": f"echo: {message}"}


class TestBuddyBotConsumption:
    def test_track_usage_without_billing(self):
        buddy = BuddyBot()
        report = buddy.track_usage("alice", "test_bot", 10)
        assert report["user_id"] == "alice"
        assert report["total_tokens"] == 10
        assert report["by_bot"]["test_bot"] == 10

    def test_track_usage_accumulates(self):
        buddy = BuddyBot()
        buddy.track_usage("alice", "bot_a", 5)
        buddy.track_usage("alice", "bot_a", 3)
        report = buddy.get_consumption_report("alice")
        assert report["total_tokens"] == 8
        assert report["by_bot"]["bot_a"] == 8

    def test_track_usage_multiple_bots(self):
        buddy = BuddyBot()
        buddy.track_usage("alice", "bot_a", 5)
        buddy.track_usage("alice", "bot_b", 7)
        report = buddy.get_consumption_report("alice")
        assert report["total_tokens"] == 12
        assert report["by_bot"]["bot_a"] == 5
        assert report["by_bot"]["bot_b"] == 7

    def test_track_usage_with_billing_deducts_tokens(self):
        billing = BillingSystem()
        billing.create_account("alice", Tier.FREE)
        billing.purchase_tokens("alice", 50)

        buddy = BuddyBot(billing=billing)
        buddy.track_usage("alice", "chatbot", 10, "GPT-4 call")

        balance = billing.get_balance("alice")
        assert balance["purchased_tokens"] == 40

    def test_track_usage_publishes_event(self):
        buddy = BuddyBot()
        events = []
        buddy.event_bus.subscribe("usage_tracked", lambda data: events.append(data))
        buddy.track_usage("alice", "bot_x", 3)
        assert len(events) == 1
        assert events[0]["user_id"] == "alice"
        assert events[0]["tokens_used"] == 3

    def test_get_consumption_report_unknown_user(self):
        buddy = BuddyBot()
        report = buddy.get_consumption_report("nobody")
        assert report["total_tokens"] == 0
        assert report["by_bot"] == {}

    def test_get_consumption_report_includes_balance_when_billing_attached(self):
        billing = BillingSystem()
        billing.create_account("alice", Tier.FREE)
        billing.purchase_tokens("alice", 100)

        buddy = BuddyBot(billing=billing)
        buddy.track_usage("alice", "bot", 5)
        report = buddy.get_consumption_report("alice")
        assert "balance" in report
        assert report["balance"]["purchased_tokens"] == 95

    def test_buddy_bot_default_token_cost(self):
        buddy = BuddyBot(default_token_cost=5)
        assert buddy.default_token_cost == 5

    def test_buddy_bot_backward_compat_no_billing_arg(self):
        buddy = BuddyBot()
        assert buddy.billing is None
        bot = _MockBot()
        buddy.register_bot("mock", bot)
        response = buddy.route_message("mock", "hi")
        assert response["reply"] == "echo: hi"
