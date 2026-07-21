"""
Tests for bots/global_bot_network/ — Global Bot Communication Network (GBN).

Coverage areas:
  1.  Tiers
  2.  Universal Bot Protocol (UBP)
  3.  Messaging Network
  4.  API Gateway
  5.  Verification System
  6.  Bot Library
  7.  Owner Dashboard
  8.  Marketplace
  9.  GlobalBotNetwork (main class)
  10. Chat / process interface
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ── Tier imports ───────────────────────────────────────────────────────────
from bots.global_bot_network.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_UBP_MESSAGING,
    FEATURE_REALTIME_DASHBOARD,
    FEATURE_EARNINGS_TRACKER,
    FEATURE_KILL_SWITCH,
    FEATURE_RATE_LIMITING,
    FEATURE_PERMISSIONS,
    FEATURE_ADVANCED_VERIFICATION,
    FEATURE_TRUSTED_BOT_STATUS,
    FEATURE_MARKETPLACE,
    FEATURE_MARKETPLACE_SELL,
    FEATURE_SLACK_INTEGRATION,
    FEATURE_DISCORD_INTEGRATION,
    FEATURE_OPENAI_INTEGRATION,
    FEATURE_WHITE_LABEL,
)

# ── UBP imports ────────────────────────────────────────────────────────────
from bots.global_bot_network.universal_bot_protocol import (
    UBPMessage,
    MessageType,
    Permission,
    UBPValidationError,
    UBPPermissionError,
    BROADCAST_TARGET,
    create_message,
    create_ping,
    create_pong,
    create_error,
    create_broadcast,
    validate_message,
)

# ── Messaging Network imports ──────────────────────────────────────────────
from bots.global_bot_network.messaging_network import (
    MessagingNetwork,
    RateLimitExceeded,
    BotNotConnected,
    RateLimiter,
    DeliveryReceipt,
)

# ── API Gateway imports ────────────────────────────────────────────────────
from bots.global_bot_network.api_gateway import (
    APIGateway,
    IntegrationType,
    Integration,
    GatewayRequest,
    GatewayResponse,
    IntegrationNotFound,
    IntegrationDisabled,
)

# ── Verification System imports ────────────────────────────────────────────
from bots.global_bot_network.verification_system import (
    VerificationSystem,
    VerificationRecord,
    VerificationLevel,
    VerificationMethod,
    VerificationError,
    BotNotRegistered,
    InsufficientVerificationMethod,
)

# ── Bot Library imports ────────────────────────────────────────────────────
from bots.global_bot_network.bot_library import (
    BotLibrary,
    BotEntry,
    BotCategory,
    BotStatus,
    BotAlreadyRegistered,
    BotNotFound,
)

# ── Owner Dashboard imports ────────────────────────────────────────────────
from bots.global_bot_network.owner_dashboard import (
    OwnerDashboard,
    BotControl,
    ActivityLogEntry,
    ChatMessage,
    EarningsRecord,
    BotNotOwned,
    BotAlreadyKilled,
)

# ── Marketplace imports ────────────────────────────────────────────────────
from bots.global_bot_network.marketplace import (
    BotMarketplace,
    MarketplaceListing,
    Purchase,
    UserWallet,
    ListingType,
    ListingStatus,
    SubscriptionInterval,
    MarketplaceError,
    ListingNotFound,
    InsufficientFunds,
    ListingUnavailable,
)

# ── Main GBN imports ───────────────────────────────────────────────────────
from bots.global_bot_network.global_bot_network import (
    GlobalBotNetwork,
    GBNError,
    GBNTierError,
    GBNBotLimitError,
)


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        assert len(list_tiers()) == 3

    def test_free_price_zero(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0

    def test_enterprise_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_free_has_ubp_messaging(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_UBP_MESSAGING)

    def test_free_has_slack(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_SLACK_INTEGRATION)

    def test_free_no_discord(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_DISCORD_INTEGRATION)

    def test_pro_has_realtime_dashboard(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_REALTIME_DASHBOARD)

    def test_pro_has_earnings_tracker(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_EARNINGS_TRACKER)

    def test_enterprise_unlimited_bots(self):
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited_bots()

    def test_free_bot_limit(self):
        assert get_tier_config(Tier.FREE).max_bots == 5

    def test_pro_bot_limit(self):
        assert get_tier_config(Tier.PRO).max_bots == 50

    def test_enterprise_has_white_label(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_WHITE_LABEL)

    def test_enterprise_has_marketplace_sell(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_MARKETPLACE_SELL)

    def test_upgrade_path_free_to_pro(self):
        assert get_upgrade_path(Tier.FREE) == Tier.PRO

    def test_upgrade_path_pro_to_enterprise(self):
        assert get_upgrade_path(Tier.PRO) == Tier.ENTERPRISE

    def test_upgrade_path_enterprise_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_tier_config_has_feature_false(self):
        assert not get_tier_config(Tier.FREE).has_feature("nonexistent_feature")

    def test_rate_limit_increases_with_tier(self):
        free = get_tier_config(Tier.FREE).max_messages_per_minute
        pro = get_tier_config(Tier.PRO).max_messages_per_minute
        ent = get_tier_config(Tier.ENTERPRISE).max_messages_per_minute
        assert free < pro < ent


# ===========================================================================
# 2. Universal Bot Protocol (UBP)
# ===========================================================================

class TestUBPMessage:
    def test_create_message_defaults(self):
        msg = create_message("bot_a", "bot_b", "Hello")
        assert msg.from_bot == "bot_a"
        assert msg.to_bot == "bot_b"
        assert msg.message == "Hello"
        assert msg.type == MessageType.MESSAGE

    def test_message_to_dict(self):
        msg = create_message("bot_a", "bot_b", "Hi")
        d = msg.to_dict()
        assert d["from"] == "bot_a"
        assert d["to"] == "bot_b"
        assert d["type"] == "message"
        assert "id" in d
        assert "timestamp" in d

    def test_message_from_dict_roundtrip(self):
        msg = create_message("bot_a", "bot_b", "Test")
        d = msg.to_dict()
        restored = UBPMessage.from_dict(d)
        assert restored.from_bot == msg.from_bot
        assert restored.to_bot == msg.to_bot
        assert restored.type == msg.type
        assert restored.message == msg.message

    def test_create_ping(self):
        ping = create_ping("bot_a", "bot_b")
        assert ping.type == MessageType.PING
        assert Permission.RESPOND.value in ping.permissions

    def test_create_pong(self):
        ping = create_ping("bot_a", "bot_b")
        pong = create_pong("bot_b", "bot_a", ping.id)
        assert pong.type == MessageType.PONG
        assert pong.metadata["reply_to"] == ping.id

    def test_create_error(self):
        err = create_error("bot_a", "bot_b", "Something went wrong")
        assert err.type == MessageType.ERROR

    def test_create_broadcast(self):
        msg = create_broadcast("bot_a", "Hello all!")
        assert msg.to_bot == BROADCAST_TARGET
        assert msg.type == MessageType.BROADCAST
        assert msg.is_broadcast()

    def test_has_permission(self):
        msg = create_message("a", "b", "x", permissions=["read", "execute"])
        assert msg.has_permission("read")
        assert msg.has_permission("execute")
        assert not msg.has_permission("admin")

    def test_unique_ids(self):
        m1 = create_message("a", "b", "x")
        m2 = create_message("a", "b", "x")
        assert m1.id != m2.id


class TestUBPValidation:
    def test_validate_valid_message(self):
        payload = {"from": "bot_a", "to": "bot_b", "type": "message"}
        validate_message(payload)  # should not raise

    def test_validate_missing_from(self):
        with pytest.raises(UBPValidationError):
            validate_message({"to": "bot_b", "type": "message"})

    def test_validate_missing_to(self):
        with pytest.raises(UBPValidationError):
            validate_message({"from": "bot_a", "type": "message"})

    def test_validate_missing_type(self):
        with pytest.raises(UBPValidationError):
            validate_message({"from": "bot_a", "to": "bot_b"})

    def test_validate_invalid_type(self):
        with pytest.raises(UBPValidationError):
            validate_message({"from": "a", "to": "b", "type": "invalid_type"})

    def test_validate_invalid_permission(self):
        with pytest.raises(UBPValidationError):
            validate_message({
                "from": "a", "to": "b", "type": "message",
                "permissions": ["superpower"]
            })

    def test_validate_non_dict_raises(self):
        with pytest.raises(UBPValidationError):
            validate_message("not a dict")

    def test_from_dict_invalid_type_raises(self):
        with pytest.raises(UBPValidationError):
            UBPMessage.from_dict({"from": "a", "to": "b", "type": "bogus"})

    def test_empty_from_raises(self):
        with pytest.raises(UBPValidationError):
            validate_message({"from": "", "to": "b", "type": "message"})


# ===========================================================================
# 3. Messaging Network
# ===========================================================================

class TestMessagingNetwork:
    def setup_method(self):
        self.net = MessagingNetwork(max_messages_per_minute=100)

    def test_connect_and_is_connected(self):
        self.net.connect("bot_a")
        assert self.net.is_connected("bot_a")

    def test_disconnect(self):
        self.net.connect("bot_a")
        self.net.disconnect("bot_a")
        assert not self.net.is_connected("bot_a")

    def test_connected_bots_list(self):
        self.net.connect("bot_a")
        self.net.connect("bot_b")
        assert set(self.net.connected_bots()) == {"bot_a", "bot_b"}

    def test_send_direct_message(self):
        received = []
        self.net.connect("bot_a")
        self.net.connect("bot_b", callback=lambda m: received.append(m))
        msg = create_message("bot_a", "bot_b", "Hello")
        receipt = self.net.send(msg)
        assert "bot_b" in receipt.delivered_to
        assert len(received) == 1
        assert received[0].message == "Hello"

    def test_send_broadcast(self):
        received_b = []
        received_c = []
        self.net.connect("bot_a")
        self.net.connect("bot_b", callback=lambda m: received_b.append(m))
        self.net.connect("bot_c", callback=lambda m: received_c.append(m))
        msg = create_broadcast("bot_a", "Broadcast!")
        self.net.send(msg)
        assert len(received_b) == 1
        assert len(received_c) == 1

    def test_broadcast_does_not_send_to_self(self):
        received_a = []
        self.net.connect("bot_a", callback=lambda m: received_a.append(m))
        self.net.connect("bot_b")
        msg = create_broadcast("bot_a", "Hello")
        self.net.send(msg)
        assert len(received_a) == 0

    def test_send_to_unconnected_raises(self):
        self.net.connect("bot_a")
        msg = create_message("bot_a", "ghost_bot", "Hi")
        with pytest.raises(BotNotConnected):
            self.net.send(msg)

    def test_ping_auto_pong(self):
        pongs = []
        self.net.connect("bot_a", callback=lambda m: pongs.append(m) if m.type == MessageType.PONG else None)
        self.net.connect("bot_b")
        ping = create_ping("bot_a", "bot_b")
        self.net.send(ping)
        assert any(p.type == MessageType.PONG for p in pongs)

    def test_message_log(self):
        self.net.connect("bot_a")
        self.net.connect("bot_b")
        msg = create_message("bot_a", "bot_b", "Test")
        self.net.send(msg)
        log = self.net.get_message_log()
        assert len(log) >= 1

    def test_message_log_filtered_by_bot(self):
        self.net.connect("bot_a")
        self.net.connect("bot_b")
        self.net.connect("bot_c")
        self.net.send(create_message("bot_a", "bot_b", "Hello"))
        self.net.send(create_message("bot_c", "bot_b", "Hi"))
        log_a = self.net.get_message_log(bot_id="bot_a")
        assert all(m["from"] == "bot_a" or m["to"] == "bot_a" for m in log_a)

    def test_message_count(self):
        self.net.connect("bot_a")
        self.net.connect("bot_b")
        for i in range(3):
            self.net.send(create_message("bot_a", "bot_b", f"msg {i}"))
        assert self.net.message_count() >= 3

    def test_get_stats(self):
        self.net.connect("bot_a")
        stats = self.net.get_stats()
        assert "connected_bots" in stats
        assert "total_messages" in stats
        assert "rate_limit_per_minute" in stats

    def test_clear_log(self):
        self.net.connect("bot_a")
        self.net.connect("bot_b")
        self.net.send(create_message("bot_a", "bot_b", "Test"))
        self.net.clear_log()
        assert self.net.message_count() == 0

    def test_get_receipt(self):
        self.net.connect("bot_a")
        self.net.connect("bot_b")
        msg = create_message("bot_a", "bot_b", "Test")
        receipt = self.net.send(msg)
        fetched = self.net.get_receipt(msg.id)
        assert fetched is not None
        assert fetched.message_id == msg.id


class TestRateLimiter:
    def test_within_limit(self):
        rl = RateLimiter(max_messages_per_minute=10)
        for _ in range(10):
            rl.check("bot")  # should not raise

    def test_exceeds_limit(self):
        rl = RateLimiter(max_messages_per_minute=3)
        for _ in range(3):
            rl.check("bot")
        with pytest.raises(RateLimitExceeded):
            rl.check("bot")

    def test_reset_clears_window(self):
        rl = RateLimiter(max_messages_per_minute=1)
        rl.check("bot")
        rl.reset("bot")
        rl.check("bot")  # should not raise

    def test_current_count(self):
        rl = RateLimiter(max_messages_per_minute=10)
        rl.check("bot")
        rl.check("bot")
        assert rl.current_count("bot") == 2

    def test_different_bots_independent(self):
        rl = RateLimiter(max_messages_per_minute=1)
        rl.check("bot_a")
        rl.check("bot_b")  # different bot, should not raise


class TestPermissionEnforcement:
    def test_task_without_execute_raises(self):
        net = MessagingNetwork(enforce_permissions=True)
        net.connect("a")
        net.connect("b")
        msg = create_message(
            "a", "b", "do task",
            msg_type=MessageType.TASK,
            permissions=["read"],  # no execute
        )
        with pytest.raises(UBPPermissionError):
            net.send(msg)

    def test_task_with_execute_passes(self):
        net = MessagingNetwork(enforce_permissions=True)
        net.connect("a")
        net.connect("b")
        msg = create_message(
            "a", "b", "do task",
            msg_type=MessageType.TASK,
            permissions=["read", "execute"],
        )
        receipt = net.send(msg)
        assert "b" in receipt.delivered_to

    def test_permission_not_enforced_when_disabled(self):
        net = MessagingNetwork(enforce_permissions=False)
        net.connect("a")
        net.connect("b")
        msg = create_message("a", "b", "task", msg_type=MessageType.TASK, permissions=["read"])
        receipt = net.send(msg)
        assert "b" in receipt.delivered_to


# ===========================================================================
# 4. API Gateway
# ===========================================================================

class TestAPIGateway:
    def setup_method(self):
        self.gw = APIGateway()
        self.gw.register_default_integrations()

    def test_list_integrations(self):
        integrations = self.gw.list_integrations()
        names = [i["name"] for i in integrations]
        assert "Slack" in names
        assert "Discord" in names
        assert "OpenAI" in names
        assert "Trello" in names
        assert "Notion" in names

    def test_slack_send_message(self):
        resp = self.gw.route("Slack", "send_message", {"channel": "#general", "text": "Hi"})
        assert resp.success
        assert resp.result["ok"] is True

    def test_discord_send_message(self):
        resp = self.gw.route("Discord", "send_message", {"channel_id": "123", "content": "Hello"})
        assert resp.success

    def test_openai_chat_completion(self):
        resp = self.gw.route("OpenAI", "chat_completion", {"user_message": "Hello AI"})
        assert resp.success
        assert "choices" in resp.result

    def test_trello_create_card(self):
        resp = self.gw.route("Trello", "create_card", {"name": "Task 1", "list_id": "list_001"})
        assert resp.success
        assert resp.result["name"] == "Task 1"

    def test_notion_create_page(self):
        resp = self.gw.route("Notion", "create_page", {"title": "Meeting Notes"})
        assert resp.success
        assert resp.result["title"] == "Meeting Notes"

    def test_unknown_integration_returns_error_response(self):
        resp = self.gw.route("NonExistent", "action")
        assert not resp.success
        assert "not registered" in resp.error.lower()

    def test_disable_integration(self):
        self.gw.disable("Slack")
        resp = self.gw.route("Slack", "send_message", {})
        assert not resp.success
        assert "disabled" in resp.error.lower()

    def test_enable_integration(self):
        self.gw.disable("Slack")
        self.gw.enable("Slack")
        resp = self.gw.route("Slack", "send_message", {})
        assert resp.success

    def test_unregister_integration(self):
        self.gw.unregister("Trello")
        resp = self.gw.route("Trello", "action")
        assert not resp.success

    def test_request_log(self):
        self.gw.route("Slack", "send_message", {})
        log = self.gw.get_request_log()
        assert len(log) >= 1

    def test_request_log_filtered(self):
        self.gw.route("Slack", "send_message", {})
        self.gw.route("Discord", "send_message", {})
        slack_log = self.gw.get_request_log(integration_name="Slack")
        assert all(r["integration"] == "Slack" for r in slack_log)

    def test_get_stats(self):
        self.gw.route("Slack", "send_message", {})
        stats = self.gw.get_stats()
        assert stats["total_requests"] >= 1
        assert stats["registered_integrations"] >= 5

    def test_custom_adapter(self):
        called = []
        def my_adapter(action, payload):
            called.append(action)
            return {"custom": True}

        self.gw.register("Custom", IntegrationType.CUSTOM, adapter=my_adapter)
        resp = self.gw.route("Custom", "do_thing")
        assert resp.success
        assert resp.result["custom"] is True
        assert "do_thing" in called

    def test_gateway_response_to_dict(self):
        resp = self.gw.route("Slack", "send_message", {})
        d = resp.to_dict()
        assert "request_id" in d
        assert "integration" in d
        assert "success" in d


# ===========================================================================
# 5. Verification System
# ===========================================================================

class TestVerificationSystem:
    def setup_method(self):
        self.vs = VerificationSystem()

    def test_register_bot(self):
        rec = self.vs.register_bot("bot_001", owner_id="user_1")
        assert rec.bot_id == "bot_001"
        assert rec.level == VerificationLevel.NONE

    def test_register_same_bot_twice_returns_existing(self):
        rec1 = self.vs.register_bot("bot_001", owner_id="user_1")
        rec2 = self.vs.register_bot("bot_001", owner_id="user_1")
        assert rec1.bot_id == rec2.bot_id

    def test_verify_basic_with_email(self):
        self.vs.register_bot("bot_001", owner_id="user_1")
        rec = self.vs.verify(
            "bot_001",
            method=VerificationMethod.EMAIL,
            target_level=VerificationLevel.BASIC,
        )
        assert rec.level == VerificationLevel.BASIC

    def test_verify_verified_with_owner_confirm(self):
        self.vs.register_bot("bot_001", owner_id="user_1")
        self.vs.verify("bot_001", VerificationMethod.EMAIL, VerificationLevel.BASIC)
        rec = self.vs.verify(
            "bot_001",
            method=VerificationMethod.OWNER_CONFIRM,
            target_level=VerificationLevel.VERIFIED,
        )
        assert rec.level == VerificationLevel.VERIFIED

    def test_verify_trusted_requires_wallet(self):
        self.vs.register_bot("bot_001", owner_id="user_1")
        self.vs.verify("bot_001", VerificationMethod.EMAIL, VerificationLevel.BASIC)
        self.vs.verify("bot_001", VerificationMethod.OWNER_CONFIRM, VerificationLevel.VERIFIED)
        with pytest.raises(InsufficientVerificationMethod):
            self.vs.verify("bot_001", VerificationMethod.EMAIL, VerificationLevel.TRUSTED)

    def test_admin_grant_bypasses_requirements(self):
        self.vs.register_bot("bot_001", owner_id="user_1")
        rec = self.vs.verify(
            "bot_001",
            method=VerificationMethod.ADMIN_GRANT,
            target_level=VerificationLevel.TRUSTED,
            admin=True,
        )
        assert rec.level == VerificationLevel.TRUSTED

    def test_admin_grant_shortcut(self):
        self.vs.register_bot("bot_001", owner_id="user_1")
        rec = self.vs.admin_grant("bot_001", VerificationLevel.TRUSTED, notes="Granted by admin")
        assert rec.level == VerificationLevel.TRUSTED

    def test_revoke_resets_to_none(self):
        self.vs.register_bot("bot_001", owner_id="user_1")
        self.vs.verify("bot_001", VerificationMethod.EMAIL, VerificationLevel.BASIC)
        rec = self.vs.revoke("bot_001", reason="Suspicious activity")
        assert rec.level == VerificationLevel.NONE
        assert len(rec.methods_completed) == 0

    def test_is_at_least(self):
        self.vs.register_bot("bot_001", owner_id="user_1")
        self.vs.verify("bot_001", VerificationMethod.EMAIL, VerificationLevel.BASIC)
        assert self.vs.is_at_least("bot_001", VerificationLevel.NONE)
        assert self.vs.is_at_least("bot_001", VerificationLevel.BASIC)
        assert not self.vs.is_at_least("bot_001", VerificationLevel.VERIFIED)

    def test_get_level_unregistered_returns_none(self):
        assert self.vs.get_level("unknown_bot") == VerificationLevel.NONE

    def test_unregistered_bot_raises(self):
        with pytest.raises(BotNotRegistered):
            self.vs.verify("ghost", VerificationMethod.EMAIL, VerificationLevel.BASIC)

    def test_unregister_bot(self):
        self.vs.register_bot("bot_001", owner_id="user_1")
        self.vs.unregister_bot("bot_001")
        assert self.vs.get_record("bot_001") is None

    def test_list_bots_by_level(self):
        self.vs.register_bot("bot_a", owner_id="u1")
        self.vs.register_bot("bot_b", owner_id="u2")
        self.vs.verify("bot_a", VerificationMethod.EMAIL, VerificationLevel.BASIC)
        basic = self.vs.list_bots(level=VerificationLevel.BASIC)
        assert len(basic) == 1
        assert basic[0]["bot_id"] == "bot_a"

    def test_get_stats(self):
        self.vs.register_bot("bot_a", owner_id="u1")
        self.vs.register_bot("bot_b", owner_id="u2")
        self.vs.verify("bot_a", VerificationMethod.EMAIL, VerificationLevel.BASIC)
        stats = self.vs.get_stats()
        assert stats["total_bots"] == 2
        assert stats["by_level"]["basic"] == 1

    def test_record_to_dict(self):
        self.vs.register_bot("bot_001", owner_id="user_1")
        rec = self.vs.get_record("bot_001")
        d = rec.to_dict()
        assert d["bot_id"] == "bot_001"
        assert "level" in d
        assert "methods_completed" in d

    def test_level_does_not_downgrade(self):
        self.vs.register_bot("bot_001", owner_id="user_1")
        self.vs.admin_grant("bot_001", VerificationLevel.TRUSTED)
        rec = self.vs.verify("bot_001", VerificationMethod.EMAIL, VerificationLevel.BASIC, admin=True)
        assert rec.level == VerificationLevel.TRUSTED  # unchanged


# ===========================================================================
# 6. Bot Library
# ===========================================================================

class TestBotLibrary:
    def setup_method(self):
        self.lib = BotLibrary()

    def test_empty_on_creation(self):
        assert self.lib.count() == 0

    def test_register_and_get_bot(self):
        entry = BotEntry(
            bot_id="test_bot",
            display_name="Test Bot",
            description="A test bot",
            category=BotCategory.AI,
            module_path="bots.test.test",
            class_name="TestBot",
        )
        self.lib.register(entry)
        retrieved = self.lib.get_bot("test_bot")
        assert retrieved.bot_id == "test_bot"

    def test_register_duplicate_raises(self):
        entry = BotEntry(
            bot_id="test_bot",
            display_name="Test Bot",
            description="desc",
            category=BotCategory.AI,
            module_path="mod",
            class_name="Cls",
        )
        self.lib.register(entry)
        with pytest.raises(BotAlreadyRegistered):
            self.lib.register(entry)

    def test_register_with_overwrite(self):
        entry = BotEntry(
            bot_id="test_bot",
            display_name="Test Bot v1",
            description="desc",
            category=BotCategory.AI,
            module_path="mod",
            class_name="Cls",
        )
        self.lib.register(entry)
        entry2 = BotEntry(
            bot_id="test_bot",
            display_name="Test Bot v2",
            description="desc",
            category=BotCategory.AI,
            module_path="mod",
            class_name="Cls",
        )
        self.lib.register(entry2, overwrite=True)
        assert self.lib.get_bot("test_bot").display_name == "Test Bot v2"

    def test_get_bot_not_found_raises(self):
        with pytest.raises(BotNotFound):
            self.lib.get_bot("nonexistent")

    def test_unregister_bot(self):
        entry = BotEntry(
            bot_id="test_bot",
            display_name="Test",
            description="",
            category=BotCategory.AI,
            module_path="mod",
            class_name="Cls",
        )
        self.lib.register(entry)
        self.lib.unregister("test_bot")
        with pytest.raises(BotNotFound):
            self.lib.get_bot("test_bot")

    def test_populate_dreamco_bots(self):
        self.lib.populate_dreamco_bots()
        assert self.lib.count() >= 30

    def test_list_bots_all(self):
        self.lib.populate_dreamco_bots()
        bots = self.lib.list_bots()
        assert len(bots) >= 30

    def test_list_bots_by_category(self):
        self.lib.populate_dreamco_bots()
        finance_bots = self.lib.list_bots(category=BotCategory.FINANCE)
        assert all(b["category"] == "finance" for b in finance_bots)

    def test_search_by_name(self):
        self.lib.populate_dreamco_bots()
        results = self.lib.search("crypto")
        assert any("crypto" in r["bot_id"] or "crypto" in r["display_name"].lower() for r in results)

    def test_search_by_capability(self):
        self.lib.populate_dreamco_bots()
        results = self.lib.search("stripe")
        assert len(results) > 0

    def test_get_stats(self):
        self.lib.populate_dreamco_bots()
        stats = self.lib.get_stats()
        assert stats["total_bots"] >= 30
        assert "by_category" in stats
        assert "by_status" in stats

    def test_bot_entry_to_dict(self):
        entry = BotEntry(
            bot_id="test_bot",
            display_name="Test",
            description="desc",
            category=BotCategory.AI,
            module_path="mod",
            class_name="Cls",
            capabilities=["chat"],
        )
        d = entry.to_dict()
        assert d["bot_id"] == "test_bot"
        assert "chat" in d["capabilities"]

    def test_financial_literacy_bot_in_library(self):
        self.lib.populate_dreamco_bots()
        entry = self.lib.get_bot("financial_literacy_bot")
        assert "credit" in entry.capabilities or "investment" in " ".join(entry.capabilities).lower()

    def test_fiverr_bot_in_library(self):
        self.lib.populate_dreamco_bots()
        entry = self.lib.get_bot("fiverr_bot")
        assert entry.category == BotCategory.FREELANCE

    def test_crypto_bot_in_library(self):
        self.lib.populate_dreamco_bots()
        entry = self.lib.get_bot("crypto_bot")
        assert entry.category == BotCategory.CRYPTO


# ===========================================================================
# 7. Owner Dashboard
# ===========================================================================

class TestOwnerDashboard:
    def setup_method(self):
        self.dash = OwnerDashboard(owner_id="owner_1")

    def test_add_and_list_bots(self):
        self.dash.add_bot("bot_a", display_name="Bot Alpha")
        bots = self.dash.list_bots()
        assert any(b["bot_id"] == "bot_a" for b in bots)

    def test_add_bot_returns_control(self):
        ctrl = self.dash.add_bot("bot_a")
        assert ctrl.bot_id == "bot_a"
        assert ctrl.is_active

    def test_get_bot(self):
        self.dash.add_bot("bot_a")
        ctrl = self.dash.get_bot("bot_a")
        assert ctrl.bot_id == "bot_a"

    def test_get_bot_not_owned_raises(self):
        with pytest.raises(BotNotOwned):
            self.dash.get_bot("unknown_bot")

    def test_remove_bot(self):
        self.dash.add_bot("bot_a")
        self.dash.remove_bot("bot_a")
        with pytest.raises(BotNotOwned):
            self.dash.get_bot("bot_a")

    def test_kill_bot(self):
        self.dash.add_bot("bot_a")
        ctrl = self.dash.kill_bot("bot_a", reason="Test kill")
        assert not ctrl.is_active
        assert ctrl.kill_reason == "Test kill"

    def test_kill_already_killed_raises(self):
        self.dash.add_bot("bot_a")
        self.dash.kill_bot("bot_a")
        with pytest.raises(BotAlreadyKilled):
            self.dash.kill_bot("bot_a")

    def test_revive_bot(self):
        self.dash.add_bot("bot_a")
        self.dash.kill_bot("bot_a")
        ctrl = self.dash.revive_bot("bot_a")
        assert ctrl.is_active

    def test_record_and_get_chat(self):
        self.dash.add_bot("bot_a")
        self.dash.record_chat("bot_a", "Hello world", direction="sent", peer="bot_b")
        feed = self.dash.get_chat_feed("bot_a")
        assert len(feed) == 1
        assert feed[0]["content"] == "Hello world"
        assert feed[0]["direction"] == "sent"

    def test_chat_feed_limit(self):
        self.dash.add_bot("bot_a")
        for i in range(5):
            self.dash.record_chat("bot_a", f"msg {i}")
        feed = self.dash.get_chat_feed("bot_a", limit=3)
        assert len(feed) == 3

    def test_activity_log(self):
        self.dash.add_bot("bot_a")  # triggers bot_added event
        log = self.dash.get_activity_log("bot_a")
        assert len(log) >= 1
        assert any(e["event"] == "bot_added" for e in log)

    def test_log_activity_manual(self):
        self.dash.add_bot("bot_a")
        self.dash.log_activity("bot_a", "custom_event", {"key": "value"})
        log = self.dash.get_activity_log("bot_a")
        assert any(e["event"] == "custom_event" for e in log)

    def test_record_earning(self):
        self.dash.add_bot("bot_a")
        rec = self.dash.record_earning("bot_a", 25.50, "gig", description="Freelance job")
        assert rec.amount_usd == 25.50
        assert rec.source == "gig"

    def test_total_earnings(self):
        self.dash.add_bot("bot_a")
        self.dash.add_bot("bot_b")
        self.dash.record_earning("bot_a", 10.0, "gig")
        self.dash.record_earning("bot_b", 20.0, "gig")
        assert self.dash.total_earnings() == 30.0
        assert self.dash.total_earnings(bot_id="bot_a") == 10.0

    def test_get_earnings_filtered(self):
        self.dash.add_bot("bot_a")
        self.dash.add_bot("bot_b")
        self.dash.record_earning("bot_a", 10.0, "gig")
        self.dash.record_earning("bot_b", 20.0, "gig")
        earnings = self.dash.get_earnings(bot_id="bot_a")
        assert all(e["bot_id"] == "bot_a" for e in earnings)

    def test_snapshot(self):
        self.dash.add_bot("bot_a")
        self.dash.add_bot("bot_b")
        self.dash.kill_bot("bot_b")
        self.dash.record_earning("bot_a", 50.0, "gig")
        snap = self.dash.snapshot()
        assert snap["owner_id"] == "owner_1"
        assert snap["total_bots"] == 2
        assert snap["active_bots"] == 1
        assert snap["killed_bots"] == 1
        assert snap["total_earnings_usd"] == 50.0

    def test_activity_log_limit(self):
        self.dash.add_bot("bot_a")
        for i in range(5):
            self.dash.log_activity("bot_a", f"event_{i}")
        log = self.dash.get_activity_log("bot_a", limit=3)
        assert len(log) == 3


# ===========================================================================
# 8. Marketplace
# ===========================================================================

class TestBotMarketplace:
    def setup_method(self):
        self.mkt = BotMarketplace()

    def test_create_listing(self):
        listing = self.mkt.create_listing(
            seller_id="seller_1",
            title="Finance Bot",
            description="A finance bot",
            listing_type=ListingType.BOT,
            price_usd=29.99,
        )
        assert listing.listing_id
        assert listing.status == ListingStatus.ACTIVE

    def test_get_listing(self):
        listing = self.mkt.create_listing("s1", "Bot A", "desc", ListingType.BOT, 10.0)
        fetched = self.mkt.get_listing(listing.listing_id)
        assert fetched.listing_id == listing.listing_id

    def test_get_listing_not_found(self):
        with pytest.raises(ListingNotFound):
            self.mkt.get_listing("nonexistent_id")

    def test_list_active(self):
        self.mkt.create_listing("s1", "Bot A", "desc", ListingType.BOT, 10.0)
        self.mkt.create_listing("s2", "Module B", "desc", ListingType.MODULE, 5.0)
        listings = self.mkt.list_active()
        assert len(listings) == 2

    def test_list_active_by_type(self):
        self.mkt.create_listing("s1", "Bot A", "desc", ListingType.BOT, 10.0)
        self.mkt.create_listing("s2", "Module B", "desc", ListingType.MODULE, 5.0)
        bots = self.mkt.list_active(listing_type=ListingType.BOT)
        assert all(l["type"] == "bot" for l in bots)

    def test_list_active_by_max_price(self):
        self.mkt.create_listing("s1", "Cheap Bot", "desc", ListingType.BOT, 5.0)
        self.mkt.create_listing("s2", "Expensive Bot", "desc", ListingType.BOT, 100.0)
        cheap = self.mkt.list_active(max_price=10.0)
        assert all(l["price_usd"] <= 10.0 for l in cheap)

    def test_search_listings(self):
        self.mkt.create_listing("s1", "Finance Bot Pro", "finance automation", ListingType.BOT, 29.0)
        results = self.mkt.list_active(query="finance")
        assert len(results) == 1

    def test_update_listing(self):
        listing = self.mkt.create_listing("s1", "Bot", "desc", ListingType.BOT, 10.0)
        updated = self.mkt.update_listing(listing.listing_id, title="New Title", price_usd=15.0)
        assert updated.title == "New Title"
        assert updated.price_usd == 15.0

    def test_remove_listing(self):
        listing = self.mkt.create_listing("s1", "Bot", "desc", ListingType.BOT, 10.0)
        self.mkt.remove_listing(listing.listing_id)
        assert self.mkt.get_listing(listing.listing_id).status == ListingStatus.REMOVED

    def test_deposit_and_get_balance(self):
        self.mkt.deposit("buyer_1", 100.0)
        assert self.mkt.get_balance("buyer_1") == 100.0

    def test_deposit_negative_raises(self):
        with pytest.raises(MarketplaceError):
            self.mkt.deposit("buyer_1", -10.0)

    def test_buy_listing(self):
        listing = self.mkt.create_listing("seller_1", "Bot", "desc", ListingType.BOT, 20.0)
        self.mkt.deposit("buyer_1", 100.0)
        purchase = self.mkt.buy(listing.listing_id, buyer_id="buyer_1")
        assert purchase.buyer_id == "buyer_1"
        assert purchase.amount_usd == 20.0

    def test_buy_deducts_buyer_balance(self):
        listing = self.mkt.create_listing("seller_1", "Bot", "desc", ListingType.BOT, 20.0)
        self.mkt.deposit("buyer_1", 100.0)
        self.mkt.buy(listing.listing_id, buyer_id="buyer_1")
        assert self.mkt.get_balance("buyer_1") == 80.0

    def test_buy_credits_seller_minus_commission(self):
        listing = self.mkt.create_listing("seller_1", "Bot", "desc", ListingType.BOT, 20.0)
        self.mkt.deposit("buyer_1", 100.0)
        self.mkt.buy(listing.listing_id, buyer_id="buyer_1")
        expected = 20.0 * (1 - BotMarketplace.COMMISSION_RATE)
        assert abs(self.mkt.get_seller_earnings("seller_1") - expected) < 0.001

    def test_buy_insufficient_funds_raises(self):
        listing = self.mkt.create_listing("seller_1", "Bot", "desc", ListingType.BOT, 50.0)
        self.mkt.deposit("buyer_1", 10.0)
        with pytest.raises(InsufficientFunds):
            self.mkt.buy(listing.listing_id, buyer_id="buyer_1")

    def test_buy_unavailable_listing_raises(self):
        listing = self.mkt.create_listing("seller_1", "Bot", "desc", ListingType.BOT, 10.0)
        self.mkt.remove_listing(listing.listing_id)
        self.mkt.deposit("buyer_1", 100.0)
        with pytest.raises(ListingUnavailable):
            self.mkt.buy(listing.listing_id, buyer_id="buyer_1")

    def test_get_purchase_history(self):
        listing = self.mkt.create_listing("seller_1", "Bot", "desc", ListingType.BOT, 10.0)
        self.mkt.deposit("buyer_1", 100.0)
        self.mkt.buy(listing.listing_id, buyer_id="buyer_1")
        history = self.mkt.get_purchase_history("buyer_1")
        assert len(history) == 1

    def test_get_sales_history(self):
        listing = self.mkt.create_listing("seller_1", "Bot", "desc", ListingType.BOT, 10.0)
        self.mkt.deposit("buyer_1", 100.0)
        self.mkt.buy(listing.listing_id, buyer_id="buyer_1")
        sales = self.mkt.get_sales_history("seller_1")
        assert len(sales) == 1

    def test_marketplace_stats(self):
        listing = self.mkt.create_listing("seller_1", "Bot", "desc", ListingType.BOT, 10.0)
        self.mkt.deposit("buyer_1", 100.0)
        self.mkt.buy(listing.listing_id, buyer_id="buyer_1")
        stats = self.mkt.get_stats()
        assert stats["total_purchases"] == 1
        assert stats["total_revenue_usd"] == 10.0

    def test_total_sales_counter_increments(self):
        listing = self.mkt.create_listing("seller_1", "Bot", "desc", ListingType.BOT, 10.0)
        self.mkt.deposit("buyer_1", 200.0)
        self.mkt.buy(listing.listing_id, buyer_id="buyer_1")
        self.mkt.deposit("buyer_2", 200.0)
        self.mkt.buy(listing.listing_id, buyer_id="buyer_2")
        assert self.mkt.get_listing(listing.listing_id).total_sales == 2

    def test_subscription_listing(self):
        listing = self.mkt.create_listing(
            "seller_1", "Premium Bot", "desc",
            ListingType.SUBSCRIPTION, 9.99,
            subscription_interval=SubscriptionInterval.MONTHLY,
        )
        assert listing.subscription_interval == SubscriptionInterval.MONTHLY

    def test_listing_to_dict(self):
        listing = self.mkt.create_listing("s1", "Bot", "desc", ListingType.BOT, 10.0, tags=["ai"])
        d = listing.to_dict()
        assert "listing_id" in d
        assert "ai" in d["tags"]


# ===========================================================================
# 9. GlobalBotNetwork — main class
# ===========================================================================

class TestGlobalBotNetwork:
    def setup_method(self):
        self.gbn = GlobalBotNetwork(owner_id="user_1", tier=Tier.PRO)

    def test_init_free_tier(self):
        gbn = GlobalBotNetwork("u", tier=Tier.FREE)
        assert gbn.tier == Tier.FREE

    def test_init_loads_dreamco_bots(self):
        assert self.gbn.bot_library.count() >= 30

    def test_connect_bot(self):
        self.gbn.connect_bot("finance_bot", display_name="Finance Bot")
        assert "finance_bot" in self.gbn.list_connected_bots()

    def test_connect_bot_registers_in_verification(self):
        self.gbn.connect_bot("finance_bot")
        rec = self.gbn.verification_system.get_record("finance_bot")
        assert rec is not None

    def test_connect_bot_adds_to_dashboard(self):
        self.gbn.connect_bot("finance_bot")
        bots = self.gbn.owner_dashboard.list_bots()
        assert any(b["bot_id"] == "finance_bot" for b in bots)

    def test_bot_limit_free_tier(self):
        gbn = GlobalBotNetwork("u", tier=Tier.FREE)
        for i in range(5):
            gbn.connect_bot(f"bot_{i}")
        with pytest.raises(GBNBotLimitError):
            gbn.connect_bot("bot_overflow")

    def test_disconnect_bot(self):
        self.gbn.connect_bot("bot_a")
        self.gbn.disconnect_bot("bot_a")
        assert "bot_a" not in self.gbn.list_connected_bots()

    def test_send_message(self):
        self.gbn.connect_bot("bot_a")
        self.gbn.connect_bot("bot_b")
        receipt = self.gbn.send_message("bot_a", "bot_b", "Hello!")
        assert "bot_b" in receipt.delivered_to

    def test_broadcast(self):
        received = []
        self.gbn.connect_bot("bot_a")
        self.gbn.messaging_network.connect("bot_b", callback=lambda m: received.append(m))
        self.gbn.connect_bot("bot_c")
        self.gbn.broadcast("bot_a", "Broadcast!")
        assert len(received) >= 1

    def test_ping(self):
        self.gbn.connect_bot("bot_a")
        self.gbn.connect_bot("bot_b")
        receipt = self.gbn.ping("bot_a", "bot_b")
        assert "bot_b" in receipt.delivered_to

    def test_call_integration_slack(self):
        resp = self.gbn.call_integration("Slack", "send_message", {"text": "Hi"})
        assert resp.success

    def test_call_integration_openai(self):
        resp = self.gbn.call_integration("OpenAI", "chat_completion", {"user_message": "Hello"})
        assert resp.success

    def test_verify_bot(self):
        self.gbn.connect_bot("bot_a")
        result = self.gbn.verify_bot(
            "bot_a",
            method=VerificationMethod.EMAIL,
            target_level=VerificationLevel.BASIC,
        )
        assert result["level"] == "basic"

    def test_verify_trusted_requires_enterprise(self):
        gbn = GlobalBotNetwork("u", tier=Tier.FREE)
        gbn.connect_bot("bot_a")
        with pytest.raises(GBNTierError):
            gbn.verify_bot(
                "bot_a",
                method=VerificationMethod.ADMIN_GRANT,
                target_level=VerificationLevel.TRUSTED,
                admin=True,
            )

    def test_get_verification_level(self):
        self.gbn.connect_bot("bot_a")
        level = self.gbn.get_verification_level("bot_a")
        assert level == "none"

    def test_kill_bot(self):
        self.gbn.connect_bot("bot_a")
        result = self.gbn.kill_bot("bot_a")
        assert not result["is_active"]
        assert "bot_a" not in self.gbn.list_connected_bots()

    def test_revive_bot(self):
        self.gbn.connect_bot("bot_a")
        self.gbn.kill_bot("bot_a")
        result = self.gbn.revive_bot("bot_a")
        assert result["is_active"]
        assert "bot_a" in self.gbn.list_connected_bots()

    def test_kill_switch_requires_feature(self):
        gbn = GlobalBotNetwork("u", tier=Tier.FREE)
        gbn.connect_bot("bot_a")
        with pytest.raises(GBNTierError):
            gbn.kill_bot("bot_a")

    def test_record_earning(self):
        self.gbn.connect_bot("bot_a")
        rec = self.gbn.record_earning("bot_a", 100.0, "gig")
        assert rec["amount_usd"] == 100.0

    def test_total_earnings(self):
        self.gbn.connect_bot("bot_a")
        self.gbn.record_earning("bot_a", 50.0, "gig")
        self.gbn.record_earning("bot_a", 75.0, "affiliate")
        assert self.gbn.total_earnings() == 125.0

    def test_earnings_requires_feature(self):
        gbn = GlobalBotNetwork("u", tier=Tier.FREE)
        gbn.connect_bot("bot_a")
        with pytest.raises(GBNTierError):
            gbn.record_earning("bot_a", 10.0, "gig")

    def test_create_listing_enterprise_only(self):
        gbn = GlobalBotNetwork("u", tier=Tier.FREE)
        with pytest.raises(GBNTierError):
            gbn.create_listing("Bot", "desc", ListingType.BOT, 10.0)

    def test_create_listing_enterprise(self):
        gbn = GlobalBotNetwork("u", tier=Tier.ENTERPRISE)
        listing = gbn.create_listing("Bot", "desc", ListingType.BOT, 10.0)
        assert listing.seller_id == "u"

    def test_get_bot_info(self):
        info = self.gbn.get_bot_info("financial_literacy_bot")
        assert info["bot_id"] == "financial_literacy_bot"

    def test_search_bots(self):
        results = self.gbn.search_bots("crypto")
        assert len(results) > 0

    def test_dashboard_snapshot(self):
        self.gbn.connect_bot("bot_a")
        snap = self.gbn.get_dashboard_snapshot()
        assert snap["tier"] == "pro"
        assert "network_stats" in snap
        assert "gateway_stats" in snap
        assert "library_stats" in snap

    def test_dashboard_requires_feature(self):
        gbn = GlobalBotNetwork("u")
        # FREE has basic_dashboard; should succeed
        gbn.connect_bot("bot_a")
        snap = gbn.get_dashboard_snapshot()
        assert snap is not None


# ===========================================================================
# 10. Chat / process interface
# ===========================================================================

class TestGBNChat:
    def setup_method(self):
        self.gbn = GlobalBotNetwork("u", tier=Tier.PRO)
        self.gbn.connect_bot("bot_a")

    def test_chat_status(self):
        resp = self.gbn.chat("status")
        assert resp["response"] == "gbn"
        assert "data" in resp

    def test_chat_dashboard(self):
        resp = self.gbn.chat("dashboard")
        assert resp["response"] == "gbn"

    def test_chat_list_bots(self):
        resp = self.gbn.chat("list bots")
        assert "bots" in resp["data"]

    def test_chat_broadcast(self):
        self.gbn.connect_bot("bot_b")
        resp = self.gbn.chat("broadcast hello everyone")
        assert resp["response"] == "gbn"

    def test_chat_library_search(self):
        resp = self.gbn.chat("search crypto")
        assert "results" in resp["data"]

    def test_chat_unknown_message(self):
        resp = self.gbn.chat("something completely random xyz")
        assert resp["response"] == "gbn"
        assert "message" in resp

    def test_process_entry_point(self):
        resp = self.gbn.process({"command": "status"})
        assert resp["response"] == "gbn"
