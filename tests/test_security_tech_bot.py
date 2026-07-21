"""
Tests for bots/security_tech_bot/tiers.py and bots/security_tech_bot/security_tech_bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
BOT_DIR = os.path.join(REPO_ROOT, 'bots', 'security_tech_bot')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.security_tech_bot.security_tech_bot import (
    SecurityTechBot,
    SecurityTechBotTierError,
    SecurityTechBotRequestLimitError,
)


# -----------------------------------------------------------------------
# Tier info tests
# -----------------------------------------------------------------------

class TestSecurityTechBotTierInfo:
    def _load_tiers(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_sec_tiers", os.path.join(BOT_DIR, "tiers.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_tier_info_keys(self):
        mod = self._load_tiers()
        info = mod.get_security_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "security_features", "scan_limit", "support_level"):
            assert key in info

    def test_free_price_zero(self):
        mod = self._load_tiers()
        assert mod.get_security_tier_info(Tier.FREE)["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        mod = self._load_tiers()
        assert mod.get_security_tier_info(Tier.ENTERPRISE)["requests_per_month"] is None

    def test_enterprise_unlimited_scans(self):
        mod = self._load_tiers()
        assert mod.get_security_tier_info(Tier.ENTERPRISE)["scan_limit"] is None

    def test_free_fewer_scans_than_pro(self):
        mod = self._load_tiers()
        free_lim = mod.SCAN_LIMITS[Tier.FREE.value]
        pro_lim = mod.SCAN_LIMITS[Tier.PRO.value]
        assert free_lim < pro_lim


# -----------------------------------------------------------------------
# SecurityTechBot tests
# -----------------------------------------------------------------------

class TestSecurityTechBot:
    def test_default_tier_free(self):
        bot = SecurityTechBot()
        assert bot.tier == Tier.FREE

    def test_scan_vulnerabilities_returns_dict(self):
        bot = SecurityTechBot()
        result = bot.scan_vulnerabilities("example.com")
        assert isinstance(result, dict)

    def test_scan_vulnerabilities_keys(self):
        bot = SecurityTechBot()
        result = bot.scan_vulnerabilities("example.com")
        for key in ("target", "scan_type", "findings", "total_findings",
                    "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_scan_basic_free_ok(self):
        bot = SecurityTechBot(tier=Tier.FREE)
        result = bot.scan_vulnerabilities("example.com", scan_type="basic")
        assert result["scan_type"] == "basic"

    def test_scan_full_free_raises(self):
        bot = SecurityTechBot(tier=Tier.FREE)
        with pytest.raises(SecurityTechBotTierError):
            bot.scan_vulnerabilities("example.com", scan_type="full")

    def test_scan_full_pro_ok(self):
        bot = SecurityTechBot(tier=Tier.PRO)
        result = bot.scan_vulnerabilities("example.com", scan_type="full")
        assert result["scan_type"] == "full"
        assert len(result["findings"]) > 0

    def test_full_scan_more_findings_than_basic(self):
        bot = SecurityTechBot(tier=Tier.PRO)
        basic = bot.scan_vulnerabilities("t.com", scan_type="basic")
        full = bot.scan_vulnerabilities("t.com", scan_type="full")
        assert full["total_findings"] >= basic["total_findings"]

    def test_scan_limit_free(self):
        bot = SecurityTechBot(tier=Tier.FREE)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_sec_t", os.path.join(BOT_DIR, "tiers.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        limit = mod.SCAN_LIMITS[Tier.FREE.value]
        for _ in range(limit):
            bot.scan_vulnerabilities("example.com")
        with pytest.raises(SecurityTechBotTierError):
            bot.scan_vulnerabilities("example.com")

    def test_check_password_strength_returns_dict(self):
        bot = SecurityTechBot()
        result = bot.check_password_strength("Password123!")
        assert isinstance(result, dict)

    def test_check_password_strength_keys(self):
        bot = SecurityTechBot()
        result = bot.check_password_strength("abc")
        for key in ("score", "strength", "entropy_bits", "recommendations",
                    "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_weak_password_detected(self):
        bot = SecurityTechBot()
        result = bot.check_password_strength("abc")
        assert result["strength"] == "Weak"
        assert len(result["recommendations"]) > 0

    def test_strong_password_detected(self):
        bot = SecurityTechBot()
        result = bot.check_password_strength("Tr0ub4dor&3XKfc!LongPass")
        assert result["strength"] in ("Strong", "Moderate")

    def test_password_recommendations_for_short(self):
        bot = SecurityTechBot()
        result = bot.check_password_strength("short")
        assert any("12" in r for r in result["recommendations"])

    def test_audit_dependencies_free_raises(self):
        bot = SecurityTechBot(tier=Tier.FREE)
        with pytest.raises(SecurityTechBotTierError):
            bot.audit_dependencies([{"name": "requests", "version": "1.0.0"}])

    def test_audit_dependencies_pro_ok(self):
        bot = SecurityTechBot(tier=Tier.PRO)
        result = bot.audit_dependencies([
            {"name": "requests", "version": "2.0.0"},
            {"name": "flask", "version": "1.0.0"},
        ])
        assert isinstance(result, dict)
        assert "total_checked" in result
        assert result["total_checked"] == 2

    def test_audit_detects_vulnerable_version(self):
        bot = SecurityTechBot(tier=Tier.PRO)
        result = bot.audit_dependencies([{"name": "oldlib", "version": "1.2.3"}])
        assert len(result["vulnerable"]) == 1

    def test_audit_clean_version(self):
        bot = SecurityTechBot(tier=Tier.PRO)
        result = bot.audit_dependencies([{"name": "newlib", "version": "2.0.0"}])
        assert result["clean"] == 1
        assert len(result["vulnerable"]) == 0

    def test_generate_security_report_enterprise_only(self):
        bot_free = SecurityTechBot(tier=Tier.FREE)
        with pytest.raises(SecurityTechBotTierError):
            bot_free.generate_security_report([])

    def test_generate_security_report_pro_only(self):
        bot_pro = SecurityTechBot(tier=Tier.PRO)
        with pytest.raises(SecurityTechBotTierError):
            bot_pro.generate_security_report([])

    def test_generate_security_report_enterprise_ok(self):
        bot = SecurityTechBot(tier=Tier.ENTERPRISE)
        scan = bot.scan_vulnerabilities("example.com")
        result = bot.generate_security_report([scan])
        assert isinstance(result, dict)
        assert "report_id" in result
        assert result["total_scans"] == 1

    def test_request_limit_raises(self):
        bot = SecurityTechBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(SecurityTechBotRequestLimitError):
            bot.check_password_strength("test")

    def test_enterprise_no_request_limit(self):
        bot = SecurityTechBot(tier=Tier.ENTERPRISE)
        bot._request_count = 999_999
        result = bot.check_password_strength("test123")
        assert result["requests_remaining"] == "unlimited"

    def test_describe_tier_returns_string(self):
        bot = SecurityTechBot()
        output = bot.describe_tier()
        assert isinstance(output, str)
        assert "Free" in output

    def test_show_upgrade_path_from_free(self):
        bot = SecurityTechBot()
        output = bot.show_upgrade_path()
        assert "Pro" in output

    def test_show_upgrade_path_enterprise(self):
        bot = SecurityTechBot(tier=Tier.ENTERPRISE)
        output = bot.show_upgrade_path()
        assert "top-tier" in output
