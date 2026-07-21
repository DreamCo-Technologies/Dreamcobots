"""
Tests for the DreamCo SaaS production-hardening features.

Covers:
  - event_bus.BaseEventBus
  - event_bus.RedisQueueBus (fallback mode without Redis)
  - saas.auth.auth.AuthService
  - saas.auth.user_model
  - saas.auth.middleware.AuthMiddleware / RateLimiter
  - saas.stripe_billing.StripeBillingService (simulation mode)
  - core.sandbox_runner.SandboxRunner
  - core.bot_validator.BotValidator
  - core.worker.BotWorker / WorkerPool (in-memory / fallback)
"""

from __future__ import annotations

import os
import sys
import tempfile
import time

import pytest

# Ensure repo root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# Event Bus tests
# ---------------------------------------------------------------------------


class TestBaseEventBus:
    def setup_method(self):
        from event_bus.base_bus import BaseEventBus
        self.bus = BaseEventBus()

    def test_publish_calls_subscriber(self):
        received = []
        self.bus.subscribe("deal_found", lambda d: received.append(d))
        self.bus.publish("deal_found", {"profit": 1000})
        assert len(received) == 1
        assert received[0]["profit"] == 1000

    def test_multiple_subscribers_all_notified(self):
        results = []
        self.bus.subscribe("event", lambda d: results.append("h1"))
        self.bus.subscribe("event", lambda d: results.append("h2"))
        self.bus.publish("event", {})
        assert "h1" in results and "h2" in results

    def test_unsubscribe_removes_handler(self):
        called = []
        handler = lambda d: called.append(1)
        self.bus.subscribe("evt", handler)
        self.bus.unsubscribe("evt", handler)
        self.bus.publish("evt", {})
        assert len(called) == 0

    def test_get_events_returns_published(self):
        self.bus.publish("a", 1)
        self.bus.publish("b", 2)
        events = self.bus.get_events()
        assert len(events) == 2

    def test_subscriber_count(self):
        self.bus.subscribe("x", lambda _: None)
        self.bus.subscribe("x", lambda _: None)
        assert self.bus.subscriber_count("x") == 2

    def test_no_subscribers_does_not_raise(self):
        self.bus.publish("unknown_event", {"data": "test"})

    def test_clear_resets_state(self):
        self.bus.subscribe("z", lambda _: None)
        self.bus.publish("z", {})
        self.bus.clear()
        assert self.bus.subscriber_count("z") == 0
        assert len(self.bus.get_events()) == 0


class TestRedisQueueBusFallback:
    """Test RedisQueueBus in fallback mode (no Redis)."""

    def setup_method(self):
        from event_bus.redis_bus import RedisQueueBus
        self.queue = RedisQueueBus(queue_name="test_queue")
        # Force fallback even if Redis happens to be running
        self.queue._redis = None

    def test_enqueue_and_dequeue(self):
        job = {"bot_path": "bots.test", "bot_name": "test_bot"}
        self.queue.enqueue(job)
        result = self.queue.dequeue()
        assert result is not None
        assert result["bot_name"] == "test_bot"

    def test_dequeue_empty_returns_none(self):
        self.queue.clear()
        result = self.queue.dequeue()
        assert result is None

    def test_queue_length(self):
        self.queue.clear()
        self.queue.enqueue({"a": 1})
        self.queue.enqueue({"b": 2})
        assert self.queue.queue_length() == 2

    def test_clear(self):
        self.queue.enqueue({"c": 3})
        self.queue.clear()
        assert self.queue.queue_length() == 0


class TestRedisEventBusFallback:
    """Test RedisEventBus falls back to in-memory when Redis unavailable."""

    def setup_method(self):
        from event_bus.redis_bus import RedisEventBus
        self.bus = RedisEventBus()
        self.bus._redis = None  # force fallback

    def test_publish_still_calls_subscribers(self):
        received = []
        self.bus.subscribe("test", lambda d: received.append(d))
        self.bus.publish("test", {"x": 1})
        assert len(received) == 1

    def test_redis_available_returns_false(self):
        assert self.bus.redis_available is False


# ---------------------------------------------------------------------------
# Auth tests
# ---------------------------------------------------------------------------


class TestAuthService:
    def setup_method(self):
        from saas.auth.auth import AuthService, UserRegistry
        self.registry = UserRegistry()
        self.auth = AuthService(registry=self.registry)

    def test_signup_success(self):
        result = self.auth.signup("alice", "alice@example.com", "password123")
        assert result["success"] is True
        assert "user_id" in result
        assert "token" in result

    def test_signup_duplicate_email_rejected(self):
        self.auth.signup("alice", "alice@example.com", "password123")
        result = self.auth.signup("alice2", "alice@example.com", "password123")
        assert result["success"] is False
        assert "email" in result["error"].lower()

    def test_signup_short_password_rejected(self):
        result = self.auth.signup("bob", "bob@example.com", "short")
        assert result["success"] is False

    def test_signup_missing_fields_rejected(self):
        result = self.auth.signup("", "bob@example.com", "password123")
        assert result["success"] is False

    def test_login_success(self):
        self.auth.signup("charlie", "charlie@example.com", "mypassword")
        result = self.auth.login("charlie@example.com", "mypassword")
        assert result["success"] is True
        assert "token" in result
        assert result["tier"] == "free"

    def test_login_wrong_password_rejected(self):
        self.auth.signup("dave", "dave@example.com", "correct_pass")
        result = self.auth.login("dave@example.com", "wrong_pass")
        assert result["success"] is False

    def test_login_unknown_email_rejected(self):
        result = self.auth.login("nobody@example.com", "password123")
        assert result["success"] is False

    def test_verify_token_returns_user(self):
        r = self.auth.signup("eve", "eve@example.com", "password123")
        user = self.auth.verify_token(r["token"])
        assert user is not None
        assert user.email == "eve@example.com"

    def test_verify_invalid_token_returns_none(self):
        user = self.auth.verify_token("invalid.token.here")
        assert user is None

    def test_upgrade_tier(self):
        r = self.auth.signup("frank", "frank@example.com", "password123")
        result = self.auth.upgrade_tier(r["user_id"], "pro")
        assert result["success"] is True
        assert result["tier"] == "pro"

    def test_upgrade_tier_unknown_user(self):
        from saas.auth.user_model import SubscriptionTier
        result = self.auth.upgrade_tier("nonexistent_id", SubscriptionTier.PRO)
        assert result["success"] is False

    def test_quota_management(self):
        r = self.auth.signup("grace", "grace@example.com", "password123")
        uid = r["user_id"]
        quota = self.auth.check_quota(uid)
        assert quota["allowed"] is True
        assert quota["remaining"] > 0

    def test_consume_quota_decrements(self):
        r = self.auth.signup("hank", "hank@example.com", "password123")
        uid = r["user_id"]
        initial = self.auth.check_quota(uid)["remaining"]
        self.auth.consume_quota(uid)
        after = self.auth.check_quota(uid)["remaining"]
        assert after == initial - 1

    def test_reset_daily_quotas(self):
        r = self.auth.signup("iris", "iris@example.com", "password123")
        uid = r["user_id"]
        self.auth.consume_quota(uid)
        self.auth.consume_quota(uid)
        count = self.auth.reset_daily_quotas()
        assert count >= 1
        assert self.auth.check_quota(uid)["runs_today"] == 0


# ---------------------------------------------------------------------------
# User model tests
# ---------------------------------------------------------------------------


class TestUserModel:
    def test_tier_features_free(self):
        from saas.auth.user_model import SubscriptionTier, get_tier_features
        features = get_tier_features(SubscriptionTier.FREE)
        assert features.max_runs_per_day == 5
        assert features.price_usd_monthly == 0.0
        assert features.can_use_redis_queue is False

    def test_tier_features_pro(self):
        from saas.auth.user_model import SubscriptionTier, get_tier_features
        features = get_tier_features(SubscriptionTier.PRO)
        assert features.max_runs_per_day == 100
        assert features.can_use_redis_queue is True
        assert features.price_usd_monthly > 0

    def test_tier_features_enterprise(self):
        from saas.auth.user_model import SubscriptionTier, get_tier_features
        features = get_tier_features(SubscriptionTier.ENTERPRISE)
        assert features.max_bots == 10_000
        assert features.support_level == "dedicated"

    def test_upgrade_path_free_to_pro(self):
        from saas.auth.user_model import SubscriptionTier, get_tier_upgrade_path
        assert get_tier_upgrade_path(SubscriptionTier.FREE) == SubscriptionTier.PRO

    def test_upgrade_path_enterprise_is_none(self):
        from saas.auth.user_model import SubscriptionTier, get_tier_upgrade_path
        assert get_tier_upgrade_path(SubscriptionTier.ENTERPRISE) is None


# ---------------------------------------------------------------------------
# Middleware / Rate Limiter tests
# ---------------------------------------------------------------------------


class TestAuthMiddleware:
    def setup_method(self):
        from saas.auth.auth import AuthService, UserRegistry
        from saas.auth.middleware import AuthMiddleware
        registry = UserRegistry()
        auth_svc = AuthService(registry=registry)
        self.auth_svc = auth_svc
        self.middleware = AuthMiddleware(auth_service=auth_svc)

    def test_authenticate_valid_token(self):
        r = self.auth_svc.signup("joe", "joe@example.com", "password123")
        user, err = self.middleware.authenticate(f"Bearer {r['token']}")
        assert user is not None
        assert err is None

    def test_authenticate_missing_header(self):
        user, err = self.middleware.authenticate(None)
        assert user is None
        assert err is not None

    def test_authenticate_invalid_token(self):
        user, err = self.middleware.authenticate("Bearer bad_token_here")
        assert user is None
        assert err is not None

    def test_require_tier_sufficient(self):
        from saas.auth.auth import Tier
        from saas.auth.user_model import SubscriptionTier
        r = self.auth_svc.signup("kim", "kim@example.com", "password123")
        self.auth_svc.upgrade_tier(r["user_id"], Tier.PRO)
        user = self.auth_svc.verify_token(r["token"])
        err = self.middleware.require_tier(user, SubscriptionTier.FREE)
        assert err is None

    def test_require_tier_insufficient(self):
        from saas.auth.user_model import SubscriptionTier
        r = self.auth_svc.signup("lena", "lena@example.com", "password123")
        user = self.auth_svc.verify_token(r["token"])
        err = self.middleware.require_tier(user, SubscriptionTier.PRO)
        assert err is not None

    def test_extract_bearer_token(self):
        from saas.auth.middleware import extract_bearer_token
        token = extract_bearer_token("Bearer mytoken123")
        assert token == "mytoken123"

    def test_extract_bearer_token_missing(self):
        from saas.auth.middleware import extract_bearer_token
        assert extract_bearer_token(None) is None
        assert extract_bearer_token("") is None


class TestRateLimiter:
    def setup_method(self):
        from saas.auth.middleware import RateLimiter
        self.limiter = RateLimiter(max_requests=3, window_seconds=10)

    def test_allows_within_limit(self):
        for _ in range(3):
            assert self.limiter.is_allowed("user1") is True

    def test_blocks_over_limit(self):
        for _ in range(3):
            self.limiter.is_allowed("user2")
        assert self.limiter.is_allowed("user2") is False

    def test_remaining_decrements(self):
        self.limiter.is_allowed("user3")
        remaining = self.limiter.remaining("user3")
        assert remaining == 2

    def test_reset_clears_window(self):
        for _ in range(3):
            self.limiter.is_allowed("user4")
        self.limiter.reset("user4")
        assert self.limiter.is_allowed("user4") is True

    def test_different_users_isolated(self):
        for _ in range(3):
            self.limiter.is_allowed("user5")
        # user6 should still be allowed
        assert self.limiter.is_allowed("user6") is True


# ---------------------------------------------------------------------------
# Stripe Billing tests (simulation mode)
# ---------------------------------------------------------------------------


class TestStripeBillingSimulation:
    def setup_method(self):
        from saas.stripe_billing import StripeBillingService
        self.billing = StripeBillingService(simulation_mode=True)

    def test_create_customer_returns_id(self):
        result = self.billing.create_customer("usr_123", "test@example.com")
        assert result["success"] is True
        assert "customer_id" in result

    def test_create_subscription_free(self):
        cust = self.billing.create_customer("usr_001", "a@b.com")
        result = self.billing.create_subscription(cust["customer_id"], "free", "usr_001")
        assert result["success"] is True
        assert result["tier"] == "free"
        assert result["amount_usd"] == 0.0

    def test_create_subscription_pro(self):
        cust = self.billing.create_customer("usr_002", "c@d.com")
        result = self.billing.create_subscription(cust["customer_id"], "pro", "usr_002")
        assert result["success"] is True
        assert result["amount_usd"] == 29.0

    def test_create_subscription_enterprise(self):
        cust = self.billing.create_customer("usr_003", "e@f.com")
        result = self.billing.create_subscription(cust["customer_id"], "enterprise", "usr_003")
        assert result["success"] is True
        assert result["amount_usd"] == 499.0

    def test_cancel_subscription(self):
        cust = self.billing.create_customer("usr_004", "g@h.com")
        sub = self.billing.create_subscription(cust["customer_id"], "pro", "usr_004")
        cancel = self.billing.cancel_subscription(sub["subscription_id"])
        assert cancel["success"] is True
        assert cancel["status"] == "cancelled"

    def test_upgrade_subscription(self):
        cust = self.billing.create_customer("usr_005", "i@j.com")
        sub = self.billing.create_subscription(cust["customer_id"], "free", "usr_005")
        upgrade = self.billing.upgrade_subscription(sub["subscription_id"], "pro", "usr_005")
        assert upgrade["success"] is True
        assert upgrade["new_tier"] == "pro"

    def test_revenue_summary(self):
        cust = self.billing.create_customer("usr_006", "k@l.com")
        self.billing.create_subscription(cust["customer_id"], "pro", "usr_006")
        summary = self.billing.revenue_summary()
        assert "total_revenue_usd" in summary
        assert summary["total_subscriptions"] >= 1

    def test_invalid_tier_rejected(self):
        cust = self.billing.create_customer("usr_007", "m@n.com")
        result = self.billing.create_subscription(cust["customer_id"], "invalid_tier")
        assert result["success"] is False

    def test_webhook_simulation(self):
        result = self.billing.handle_webhook(b"{}", "sig_test")
        assert result["success"] is True
        assert result["simulation"] is True


# ---------------------------------------------------------------------------
# Sandbox Runner tests
# ---------------------------------------------------------------------------


class TestSandboxRunner:
    def setup_method(self):
        from core.sandbox_runner import SandboxRunner
        self.runner = SandboxRunner(timeout_seconds=5)

    def test_run_code_success(self):
        result = self.runner.run_code("print('hello sandbox')")
        assert result["success"] is True
        assert "hello sandbox" in result["output"]

    def test_run_code_syntax_error(self):
        result = self.runner.run_code("def broken(: pass")
        assert result["success"] is False

    def test_run_code_runtime_error(self):
        result = self.runner.run_code("raise ValueError('test error')")
        assert result["success"] is False
        assert result["exit_code"] != 0

    def test_run_code_timeout(self):
        from core.sandbox_runner import SandboxRunner
        fast_runner = SandboxRunner(timeout_seconds=1)
        result = fast_runner.run_code("import time; time.sleep(10)")
        assert result["timed_out"] is True
        assert result["success"] is False

    def test_run_file_not_found(self):
        result = self.runner.run_file("/nonexistent/path/bot.py")
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_run_file_real_file(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write("print('from file')\n")
            path = f.name
        try:
            result = self.runner.run_file(path)
            assert result["success"] is True
            assert "from file" in result["output"]
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# Bot Validator tests
# ---------------------------------------------------------------------------


class TestBotValidator:
    def setup_method(self):
        from core.bot_validator import BotValidator
        self.validator = BotValidator()

    def test_valid_simple_bot(self):
        source = "def run():\n    return {'revenue': 100}\n"
        ok, issues = self.validator.validate_source(source)
        assert ok is True
        assert len(issues) == 0

    def test_blocked_eval(self):
        source = "result = eval('1+1')\n"
        ok, issues = self.validator.validate_source(source)
        assert ok is False
        assert any("eval" in i for i in issues)

    def test_blocked_exec(self):
        source = "exec('import os')\n"
        ok, issues = self.validator.validate_source(source)
        assert ok is False

    def test_blocked_os_import(self):
        source = "import os\nprint(os.getcwd())\n"
        ok, issues = self.validator.validate_source(source)
        assert ok is False

    def test_blocked_subprocess_import(self):
        source = "import subprocess\n"
        ok, issues = self.validator.validate_source(source)
        assert ok is False

    def test_blocked_os_system(self):
        source = "os.system('ls')\n"
        ok, issues = self.validator.validate_source(source)
        assert ok is False

    def test_syntax_error_caught(self):
        source = "def broken(: pass\n"
        ok, issues = self.validator.validate_source(source)
        assert ok is False
        assert any("syntax" in i.lower() for i in issues)

    def test_valid_math_imports(self):
        source = "import math\nresult = math.sqrt(9)\n"
        ok, issues = self.validator.validate_source(source)
        assert ok is True

    def test_validate_file_not_found(self):
        ok, issues = self.validator.validate_file("/nonexistent/bot.py")
        assert ok is False

    def test_validate_non_py_file(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not python")
            path = f.name
        try:
            ok, issues = self.validator.validate_file(path)
            assert ok is False
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# Worker tests (fallback mode without Redis)
# ---------------------------------------------------------------------------


class TestBotWorker:
    def setup_method(self):
        from event_bus.redis_bus import RedisQueueBus
        from core.worker import BotWorker

        self.queue = RedisQueueBus(queue_name="worker_test_queue")
        self.queue._redis = None  # force fallback

        self.worker = BotWorker(queue=self.queue, max_jobs=5)

    def test_process_one_empty_queue_returns_none(self):
        self.queue.clear()
        result = self.worker.process_one(timeout=0)
        assert result is None

    def test_process_one_runs_a_job(self):
        self.queue.enqueue({
            "bot_path": "DreamCo.bots.dealBot",
            "bot_name": "dealBot",
        })
        result = self.worker.process_one(timeout=0)
        assert result is not None
        assert "bot" in result

    def test_jobs_processed_counter(self):
        self.queue.enqueue({"bot_path": "DreamCo.bots.dealBot", "bot_name": "dealBot"})
        self.worker.process_one()
        assert self.worker.jobs_processed == 1

    def test_run_forever_stops_after_max_jobs(self):
        for _ in range(3):
            self.queue.enqueue({"bot_path": "DreamCo.bots.dealBot", "bot_name": "dealBot"})
        from core.worker import BotWorker
        w = BotWorker(queue=self.queue, max_jobs=2)
        w.run_forever()
        assert w.jobs_processed == 2


class TestWorkerPool:
    def test_pool_processes_jobs(self):
        from event_bus.redis_bus import RedisQueueBus
        from core.worker import WorkerPool

        queue = RedisQueueBus(queue_name="pool_test_queue")
        queue._redis = None

        for _ in range(4):
            queue.enqueue({"bot_path": "DreamCo.bots.dealBot", "bot_name": "dealBot"})

        pool = WorkerPool(size=2, queue=queue, max_jobs_per_worker=2)
        pool.start()
        pool.join(timeout=5.0)

        assert pool.total_jobs_processed() >= 2
