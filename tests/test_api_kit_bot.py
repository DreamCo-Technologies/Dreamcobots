"""
Tests for the DreamCo API Kit Bot package.

Covers: tiers, API kit catalog, sandbox manager, one-click deploy,
        main bot orchestrator, tier enforcement, and edge cases.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta, timezone

import pytest

from bots.api_kit_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_API_KIT_BASIC,
    FEATURE_SANDBOX_BASIC,
    FEATURE_SECRET_KEY_MANAGEMENT,
    FEATURE_ONE_CLICK_DEPLOY,
    FEATURE_ANALYTICS,
    FEATURE_ADVANCED_SANDBOX,
    FEATURE_AUTO_KEY_EXPIRATION,
    FEATURE_WHITE_LABEL,
    FEATURE_FORTUNE500_INTEGRATIONS,
    FEATURE_DEDICATED_SUPPORT,
)
from bots.api_kit_bot.api_kit_catalog import (
    APIKitCatalog,
    APIKit,
    HEALTHCARE_DIAGNOSTICS,
    PRODUCTIVITY,
    FINANCE,
    E_COMMERCE,
    HR,
    EDUCATION,
    MARKETING,
    LEGAL,
    LOGISTICS,
    ENTERTAINMENT,
)
from bots.api_kit_bot.sandbox_manager import SandboxManager, _generate_secret_key
from bots.api_kit_bot.one_click_deploy import (
    OneClickDeploy,
    DEPLOY_TARGETS,
    AWS_LAMBDA,
    VERCEL,
    DOCKER,
    RAILWAY,
)
from bots.api_kit_bot.api_kit_bot import APIKitBot, APIKitBotError, APIKitTierError


# ===========================================================================
# Tiers
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_free_tier_price(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0

    def test_enterprise_tier_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0

    def test_free_limits(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_api_kits == 1
        assert cfg.max_sandboxes == 1
        assert cfg.max_api_calls_per_day == 100

    def test_pro_limits(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.max_api_kits == 10
        assert cfg.max_sandboxes == 5
        assert cfg.max_api_calls_per_day == 10_000

    def test_enterprise_unlimited(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_api_kits is None
        assert cfg.max_sandboxes is None
        assert cfg.max_api_calls_per_day is None
        assert cfg.is_unlimited_kits()
        assert cfg.is_unlimited_sandboxes()
        assert cfg.is_unlimited_api_calls()

    def test_free_features(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_API_KIT_BASIC)
        assert cfg.has_feature(FEATURE_SANDBOX_BASIC)
        assert not cfg.has_feature(FEATURE_SECRET_KEY_MANAGEMENT)
        assert not cfg.has_feature(FEATURE_ONE_CLICK_DEPLOY)

    def test_pro_features(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_SECRET_KEY_MANAGEMENT)
        assert cfg.has_feature(FEATURE_ONE_CLICK_DEPLOY)
        assert cfg.has_feature(FEATURE_ANALYTICS)
        assert not cfg.has_feature(FEATURE_ADVANCED_SANDBOX)
        assert not cfg.has_feature(FEATURE_WHITE_LABEL)

    def test_enterprise_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feature in [
            FEATURE_ADVANCED_SANDBOX,
            FEATURE_AUTO_KEY_EXPIRATION,
            FEATURE_WHITE_LABEL,
            FEATURE_FORTUNE500_INTEGRATIONS,
            FEATURE_DEDICATED_SUPPORT,
        ]:
            assert cfg.has_feature(feature)

    def test_upgrade_path_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_path_pro_to_enterprise(self):
        upgrade = get_upgrade_path(Tier.PRO)
        assert upgrade is not None
        assert upgrade.tier == Tier.ENTERPRISE

    def test_upgrade_path_enterprise_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None


# ===========================================================================
# API Kit Catalog
# ===========================================================================

class TestAPIKitCatalog:
    def setup_method(self):
        self.catalog = APIKitCatalog()

    def test_catalog_has_20_plus_kits(self):
        kits = self.catalog.list_kits()
        assert len(kits) >= 20

    def test_get_kit_returns_correct_kit(self):
        kit = self.catalog.get_kit("kit_001")
        assert kit is not None
        assert kit.kit_id == "kit_001"

    def test_get_kit_unknown_returns_none(self):
        assert self.catalog.get_kit("kit_999") is None

    def test_list_kits_by_category(self):
        finance_kits = self.catalog.list_kits(FINANCE)
        assert len(finance_kits) > 0
        for k in finance_kits:
            assert k.category == FINANCE

    def test_search_kits_returns_matches(self):
        results = self.catalog.search_kits("fraud")
        assert any("fraud" in k.name.lower() or "fraud" in k.description.lower() for k in results)

    def test_search_kits_no_match(self):
        results = self.catalog.search_kits("xyznonexistent123")
        assert results == []

    def test_get_popular_kits_default_5(self):
        popular = self.catalog.get_popular_kits()
        assert len(popular) == 5

    def test_get_popular_kits_custom_n(self):
        popular = self.catalog.get_popular_kits(n=3)
        assert len(popular) == 3

    def test_get_kit_pricing_all_kits(self):
        pricing = self.catalog.get_kit_pricing()
        assert len(pricing) >= 20
        for p in pricing:
            assert "kit_id" in p
            assert "monthly_price_usd" in p

    def test_kit_to_dict_structure(self):
        kit = self.catalog.get_kit("kit_001")
        d = kit.to_dict()
        for key in ["kit_id", "name", "category", "description", "endpoints",
                    "sample_code", "monthly_price_usd", "setup_fee_usd",
                    "ai_model_type", "response_time_ms"]:
            assert key in d

    def test_all_categories_present(self):
        all_categories = {k.category for k in self.catalog.list_kits()}
        expected = {
            HEALTHCARE_DIAGNOSTICS, PRODUCTIVITY, ENTERTAINMENT, FINANCE,
            E_COMMERCE, HR, EDUCATION, MARKETING, LEGAL, LOGISTICS,
        }
        assert expected.issubset(all_categories)


# ===========================================================================
# Sandbox Manager
# ===========================================================================

class TestSandboxManager:
    def setup_method(self):
        self.mgr = SandboxManager()

    def test_create_sandbox_returns_dict(self):
        result = self.mgr.create_sandbox("owner1", "Test Sandbox")
        assert "sandbox_id" in result
        assert "secret_key" in result
        assert result["status"] == "ACTIVE"

    def test_secret_key_starts_with_prefix(self):
        result = self.mgr.create_sandbox("owner1", "Test Sandbox")
        assert result["secret_key"].startswith("sk_sandbox_")

    def test_secret_key_generation_prefix(self):
        key = _generate_secret_key()
        assert key.startswith("sk_sandbox_")

    def test_secret_key_uniqueness(self):
        k1 = _generate_secret_key()
        k2 = _generate_secret_key()
        assert k1 != k2

    def test_create_sandbox_has_expiry(self):
        result = self.mgr.create_sandbox("owner1", "Expiry Test")
        assert "expires_at" in result
        assert result["expires_at"] is not None

    def test_validate_secret_key_correct(self):
        sb = self.mgr.create_sandbox("owner1", "Key Test")
        assert self.mgr.validate_secret_key(sb["sandbox_id"], sb["secret_key"]) is True

    def test_validate_secret_key_wrong(self):
        sb = self.mgr.create_sandbox("owner1", "Key Test")
        assert self.mgr.validate_secret_key(sb["sandbox_id"], "wrong_key") is False

    def test_validate_unknown_sandbox(self):
        assert self.mgr.validate_secret_key("sbx_nonexistent", "any_key") is False

    def test_rotate_key_returns_new_key(self):
        sb = self.mgr.create_sandbox("owner1", "Rotate Test")
        old_key = sb["secret_key"]
        result = self.mgr.rotate_secret_key(sb["sandbox_id"])
        assert result["secret_key"] != old_key
        assert result["secret_key"].startswith("sk_sandbox_")
        assert result["rotated"] is True

    def test_rotated_key_validates(self):
        sb = self.mgr.create_sandbox("owner1", "Rotate Validate")
        old_key = sb["secret_key"]
        rotated = self.mgr.rotate_secret_key(sb["sandbox_id"])
        new_key = rotated["secret_key"]
        assert self.mgr.validate_secret_key(sb["sandbox_id"], new_key) is True
        assert self.mgr.validate_secret_key(sb["sandbox_id"], old_key) is False

    def test_deactivate_sandbox(self):
        sb = self.mgr.create_sandbox("owner1", "Deactivate Test")
        result = self.mgr.deactivate_sandbox(sb["sandbox_id"])
        assert result["status"] == "INACTIVE"
        info = self.mgr.get_sandbox(sb["sandbox_id"])
        assert info["status"] == "INACTIVE"

    def test_list_sandboxes_owner_filter(self):
        self.mgr.create_sandbox("alice", "Alice SB1")
        self.mgr.create_sandbox("alice", "Alice SB2")
        self.mgr.create_sandbox("bob", "Bob SB1")
        alice_list = self.mgr.list_sandboxes("alice")
        assert len(alice_list) == 2
        assert all(s["owner_id"] == "alice" for s in alice_list)

    def test_get_sandbox_analytics_empty(self):
        sb = self.mgr.create_sandbox("owner1", "Analytics Test")
        analytics = self.mgr.get_sandbox_analytics(sb["sandbox_id"])
        assert analytics["requests_count"] == 0
        assert analytics["success_rate"] == 0.0
        assert analytics["error_rate"] == 0.0

    def test_get_sandbox_analytics_after_requests(self):
        sb = self.mgr.create_sandbox("owner1", "Analytics Test 2")
        sid = sb["sandbox_id"]
        self.mgr.record_request(sid, "/diagnose", 200, True)
        self.mgr.record_request(sid, "/diagnose", 300, True)
        self.mgr.record_request(sid, "/conditions/1", 150, False)
        analytics = self.mgr.get_sandbox_analytics(sid)
        assert analytics["requests_count"] == 3
        assert analytics["success_rate"] == pytest.approx(2 / 3, rel=1e-3)
        assert analytics["error_rate"] == pytest.approx(1 / 3, rel=1e-3)
        assert len(analytics["top_endpoints"]) > 0

    def test_check_expiry_not_expired(self):
        sb = self.mgr.create_sandbox("owner1", "Expiry Check")
        info = self.mgr.check_expiry(sb["sandbox_id"])
        assert info["is_expired"] is False
        assert info["days_remaining"] > 0

    def test_auto_expire_sandboxes(self):
        mgr = SandboxManager()
        sb = mgr.create_sandbox("owner1", "Auto Expire Test")
        sid = sb["sandbox_id"]
        # Manually backdate the expiry
        past = (datetime.now(tz=timezone.utc) - timedelta(days=1)).isoformat()
        mgr._sandboxes[sid]["expires_at"] = past
        expired = mgr.auto_expire_sandboxes()
        assert sid in expired
        assert mgr._sandboxes[sid]["status"] == "INACTIVE"

    def test_auto_expire_does_not_expire_active_valid(self):
        mgr = SandboxManager()
        sb = mgr.create_sandbox("owner1", "Not Expired")
        expired = mgr.auto_expire_sandboxes()
        assert sb["sandbox_id"] not in expired

    def test_rotate_unknown_sandbox_returns_error(self):
        result = self.mgr.rotate_secret_key("sbx_nonexistent")
        assert "error" in result

    def test_get_sandbox_unknown_returns_error(self):
        result = self.mgr.get_sandbox("sbx_nonexistent")
        assert "error" in result


# ===========================================================================
# One-Click Deploy
# ===========================================================================

class TestOneClickDeploy:
    def setup_method(self):
        self.deployer = OneClickDeploy()

    def test_deploy_kit_returns_deploying(self):
        result = self.deployer.deploy_kit("kit_001", "owner1", AWS_LAMBDA)
        assert result["status"] == "DEPLOYING"
        assert "deployment_id" in result
        assert "endpoint_url" in result

    def test_deploy_kit_unknown_target(self):
        result = self.deployer.deploy_kit("kit_001", "owner1", "unknown_target")
        assert "error" in result

    def test_simulate_deployment_ready(self):
        dep = self.deployer.deploy_kit("kit_001", "owner1", VERCEL)
        result = self.deployer.simulate_deployment_ready(dep["deployment_id"])
        assert result["status"] == "LIVE"
        assert "endpoint_url" in result

    def test_get_deployment_metrics_before_live(self):
        dep = self.deployer.deploy_kit("kit_001", "owner1", DOCKER)
        metrics = self.deployer.get_deployment_metrics(dep["deployment_id"])
        assert "Not available" in metrics.get("metrics", "")

    def test_get_deployment_metrics_after_live(self):
        dep = self.deployer.deploy_kit("kit_001", "owner1", RAILWAY)
        self.deployer.simulate_deployment_ready(dep["deployment_id"])
        metrics = self.deployer.get_deployment_metrics(dep["deployment_id"])
        assert "uptime_pct" in metrics
        assert "requests_total" in metrics

    def test_rollback_deployment(self):
        dep = self.deployer.deploy_kit("kit_001", "owner1", AWS_LAMBDA)
        result = self.deployer.rollback_deployment(dep["deployment_id"])
        assert result["rolled_back"] is True
        assert result["status"] == "ROLLED_BACK"

    def test_list_deployments_owner_filter(self):
        self.deployer.deploy_kit("kit_001", "alice", AWS_LAMBDA)
        self.deployer.deploy_kit("kit_002", "alice", VERCEL)
        self.deployer.deploy_kit("kit_003", "bob", DOCKER)
        alice_deps = self.deployer.list_deployments("alice")
        assert len(alice_deps) == 2

    def test_deploy_targets_list(self):
        assert len(DEPLOY_TARGETS) == 7


# ===========================================================================
# APIKitBot (orchestrator + tier enforcement)
# ===========================================================================

class TestAPIKitBot:
    def test_free_bot_browse_kits(self):
        bot = APIKitBot(owner_id="free_user", tier=Tier.FREE)
        kits = bot.browse_kits()
        assert len(kits) >= 20

    def test_free_bot_get_kit(self):
        bot = APIKitBot(owner_id="free_user", tier=Tier.FREE)
        kit = bot.get_kit("kit_001")
        assert kit["kit_id"] == "kit_001"

    def test_free_bot_create_sandbox(self):
        bot = APIKitBot(owner_id="free_user", tier=Tier.FREE)
        sb = bot.create_sandbox("My Sandbox")
        assert sb["secret_key"].startswith("sk_sandbox_")
        assert sb["status"] == "ACTIVE"

    def test_free_bot_sandbox_limit_enforced(self):
        bot = APIKitBot(owner_id="limited_user", tier=Tier.FREE)
        bot.create_sandbox("SB1")
        with pytest.raises(APIKitTierError):
            bot.create_sandbox("SB2")

    def test_free_bot_secret_key_management_blocked(self):
        bot = APIKitBot(owner_id="free_user", tier=Tier.FREE)
        sb = bot.create_sandbox("My Sandbox")
        with pytest.raises(APIKitTierError):
            bot.rotate_key(sb["sandbox_id"])

    def test_free_bot_analytics_blocked(self):
        bot = APIKitBot(owner_id="free_user", tier=Tier.FREE)
        sb = bot.create_sandbox("My Sandbox")
        with pytest.raises(APIKitTierError):
            bot.get_sandbox_analytics(sb["sandbox_id"])

    def test_free_bot_deploy_blocked(self):
        bot = APIKitBot(owner_id="free_user", tier=Tier.FREE)
        with pytest.raises(APIKitTierError):
            bot.deploy_kit("kit_001", AWS_LAMBDA)

    def test_pro_bot_rotate_key(self):
        bot = APIKitBot(owner_id="pro_user", tier=Tier.PRO)
        sb = bot.create_sandbox("Pro Sandbox")
        old_key = sb["secret_key"]
        result = bot.rotate_key(sb["sandbox_id"])
        assert result["secret_key"] != old_key

    def test_pro_bot_analytics(self):
        bot = APIKitBot(owner_id="pro_user", tier=Tier.PRO)
        sb = bot.create_sandbox("Pro Sandbox")
        analytics = bot.get_sandbox_analytics(sb["sandbox_id"])
        assert "requests_count" in analytics

    def test_pro_bot_deploy(self):
        bot = APIKitBot(owner_id="pro_user", tier=Tier.PRO)
        dep = bot.deploy_kit("kit_001", VERCEL)
        assert dep["status"] == "DEPLOYING"

    def test_get_tier_info_free(self):
        bot = APIKitBot(owner_id="user", tier=Tier.FREE)
        info = bot.get_tier_info()
        assert info["tier"] == "free"
        assert info["price_usd_monthly"] == 0.0

    def test_get_upgrade_info_from_free(self):
        bot = APIKitBot(owner_id="user", tier=Tier.FREE)
        info = bot.get_upgrade_info()
        assert info["upgrade_to"] == "pro"
        assert len(info["new_features"]) > 0

    def test_get_upgrade_info_from_enterprise(self):
        bot = APIKitBot(owner_id="user", tier=Tier.ENTERPRISE)
        info = bot.get_upgrade_info()
        assert "highest tier" in info["message"].lower()

    def test_validate_key(self):
        bot = APIKitBot(owner_id="user", tier=Tier.FREE)
        sb = bot.create_sandbox("Key Validate")
        assert bot.validate_key(sb["sandbox_id"], sb["secret_key"]) is True
        assert bot.validate_key(sb["sandbox_id"], "bad_key") is False

    def test_chat_returns_string(self):
        bot = APIKitBot(owner_id="user", tier=Tier.PRO)
        response = bot.chat("show me the kits")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_chat_sandbox_message(self):
        bot = APIKitBot(owner_id="user", tier=Tier.PRO)
        response = bot.chat("how do I create a new sandbox?")
        assert "sandbox" in response.lower()

    def test_chat_deploy_message(self):
        bot = APIKitBot(owner_id="user", tier=Tier.PRO)
        response = bot.chat("tell me about deploy options")
        assert "deploy" in response.lower() or "lambda" in response.lower()

    def test_enterprise_all_features(self):
        bot = APIKitBot(owner_id="ent_user", tier=Tier.ENTERPRISE)
        # Should not raise
        sb = bot.create_sandbox("Ent Sandbox")
        bot.rotate_key(sb["sandbox_id"])
        bot.get_sandbox_analytics(sb["sandbox_id"])
        bot.deploy_kit("kit_001", AWS_LAMBDA)
