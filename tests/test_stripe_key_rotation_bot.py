"""
Tests for bots/stripe_key_rotation_bot/

Covers:
  1. Tiers and feature flags
  2. StripeKeyRotationBot — key validation, rotation, GitHub Secret update,
     payment workflow validation, old key deactivation, notifications
  3. Full rotation pipeline (run_rotation)
  4. Audit log
  5. Secure key handling — keys never appear in results
  6. Chat / process interfaces
  7. Edge cases and error handling
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.stripe_key_rotation_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_MANUAL_ROTATION,
    FEATURE_SCHEDULED_ROTATION,
    FEATURE_GITHUB_SECRETS_UPDATE,
    FEATURE_EMAIL_NOTIFICATION,
    FEATURE_SLACK_NOTIFICATION,
    FEATURE_AUDIT_TRAIL,
    FEATURE_KEY_VALIDATION,
    FEATURE_OLD_KEY_DEACTIVATION,
    FEATURE_PAYMENT_WORKFLOW_TEST,
    FEATURE_MULTI_ENV_ROTATION,
)
from bots.stripe_key_rotation_bot.stripe_key_rotation_bot import (
    StripeKeyRotationBot,
    RotationTierError,
    RotationValidationError,
    RotationWorkflowError,
    Bot,
    _mask_key,
    _key_fingerprint,
    _REDACTED,
)


# ===========================================================================
# Helpers
# ===========================================================================

def _bot(tier: Tier = Tier.STARTER, key: str = "sk_test_abc123def456ghi789jkl0") -> StripeKeyRotationBot:
    return StripeKeyRotationBot(
        tier=tier,
        stripe_api_key=key,
        github_token="ghp_test_token_fake",
        github_repo="DreamCo-Technologies/Dreamcobots",
        notify_email="admin@dreamco.ai",
        slack_webhook_url="https://hooks.slack.com/services/test/fake",
        simulation_mode=True,
    )


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        assert len(list_tiers()) == 3

    def test_starter_price(self):
        cfg = get_tier_config(Tier.STARTER)
        assert cfg.price_usd_monthly == 0.0

    def test_growth_price(self):
        cfg = get_tier_config(Tier.GROWTH)
        assert cfg.price_usd_monthly == 29.0

    def test_enterprise_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 99.0

    def test_starter_has_manual_rotation(self):
        cfg = get_tier_config(Tier.STARTER)
        assert cfg.has_feature(FEATURE_MANUAL_ROTATION)

    def test_starter_lacks_scheduled_rotation(self):
        cfg = get_tier_config(Tier.STARTER)
        assert not cfg.has_feature(FEATURE_SCHEDULED_ROTATION)

    def test_growth_has_scheduled_rotation(self):
        cfg = get_tier_config(Tier.GROWTH)
        assert cfg.has_feature(FEATURE_SCHEDULED_ROTATION)

    def test_growth_has_audit_trail(self):
        cfg = get_tier_config(Tier.GROWTH)
        assert cfg.has_feature(FEATURE_AUDIT_TRAIL)

    def test_starter_lacks_audit_trail(self):
        cfg = get_tier_config(Tier.STARTER)
        assert not cfg.has_feature(FEATURE_AUDIT_TRAIL)

    def test_enterprise_has_multi_env_rotation(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_MULTI_ENV_ROTATION)

    def test_upgrade_from_starter_to_growth(self):
        nxt = get_upgrade_path(Tier.STARTER)
        assert nxt is not None
        assert nxt.tier == Tier.GROWTH

    def test_upgrade_from_growth_to_enterprise(self):
        nxt = get_upgrade_path(Tier.GROWTH)
        assert nxt.tier == Tier.ENTERPRISE

    def test_no_upgrade_from_enterprise(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_all_tiers_have_key_validation(self):
        for tier in Tier:
            cfg = get_tier_config(tier)
            assert cfg.has_feature(FEATURE_KEY_VALIDATION)

    def test_all_tiers_have_github_secrets_update(self):
        for tier in Tier:
            cfg = get_tier_config(tier)
            assert cfg.has_feature(FEATURE_GITHUB_SECRETS_UPDATE)

    def test_all_tiers_have_payment_workflow_test(self):
        for tier in Tier:
            cfg = get_tier_config(tier)
            assert cfg.has_feature(FEATURE_PAYMENT_WORKFLOW_TEST)

    def test_starter_lacks_old_key_deactivation(self):
        cfg = get_tier_config(Tier.STARTER)
        assert not cfg.has_feature(FEATURE_OLD_KEY_DEACTIVATION)

    def test_growth_has_old_key_deactivation(self):
        cfg = get_tier_config(Tier.GROWTH)
        assert cfg.has_feature(FEATURE_OLD_KEY_DEACTIVATION)


# ===========================================================================
# 2. Secure key helpers
# ===========================================================================

class TestSecureKeyHelpers:
    def test_mask_key_hides_most_of_key(self):
        key = "sk_test_abc123def456ghi789jkl0"
        masked = _mask_key(key)
        assert "sk_test_" in masked
        assert "abc123def456ghi789jkl0" not in masked
        assert _REDACTED in masked

    def test_mask_empty_key_returns_redacted(self):
        assert _mask_key("") == _REDACTED

    def test_fingerprint_is_deterministic(self):
        key = "sk_test_abc123"
        assert _key_fingerprint(key) == _key_fingerprint(key)

    def test_different_keys_different_fingerprints(self):
        assert _key_fingerprint("sk_test_aaa") != _key_fingerprint("sk_test_bbb")

    def test_fingerprint_empty_returns_empty(self):
        assert _key_fingerprint("") == ""

    def test_fingerprint_is_16_chars(self):
        fp = _key_fingerprint("sk_test_abc123def456")
        assert len(fp) == 16


# ===========================================================================
# 3. Validate current key
# ===========================================================================

class TestValidateCurrentKey:
    def test_valid_test_key(self):
        bot = _bot(key="sk_test_abc123def456ghi789jkl0")
        result = bot.validate_current_key()
        assert result["valid"] is True
        assert result["simulation"] is True

    def test_no_key_returns_invalid(self):
        bot = _bot(key="")
        result = bot.validate_current_key()
        assert result["valid"] is False
        assert _REDACTED in result["masked_key"]

    def test_masked_key_not_full_key(self):
        key = "sk_test_abc123def456ghi789jkl0"
        bot = _bot(key=key)
        result = bot.validate_current_key()
        assert key not in str(result["masked_key"])
        assert key not in str(result)

    def test_starter_tier_has_key_validation(self):
        bot = _bot(tier=Tier.STARTER)
        result = bot.validate_current_key()
        assert "valid" in result


# ===========================================================================
# 4. Key rotation
# ===========================================================================

class TestRotateKey:
    def test_rotation_succeeds(self):
        bot = _bot()
        result = bot.rotate_key()
        assert result["success"] is True
        assert result["rotation_id"].startswith("rot_")

    def test_rotation_id_is_unique(self):
        bot = _bot()
        id1 = bot.rotate_key()["rotation_id"]
        id2 = bot.rotate_key()["rotation_id"]
        assert id1 != id2

    def test_new_key_not_exposed_in_result(self):
        bot = _bot(key="sk_test_abc123def456ghi789jkl0")
        result = bot.rotate_key()
        result_str = str(result)
        assert "sk_test_abc123def456ghi789jkl0" not in result_str
        # New key is masked — ellipsis present in the masked value
        assert "…" in result.get("masked_new_key", "")

    def test_masked_new_key_contains_redacted(self):
        bot = _bot()
        result = bot.rotate_key()
        assert _REDACTED in result["masked_new_key"]

    def test_rotation_count_increments(self):
        bot = _bot()
        assert bot._rotation_count == 0
        bot.rotate_key()
        assert bot._rotation_count == 1
        bot.rotate_key()
        assert bot._rotation_count == 2

    def test_old_fingerprint_recorded(self):
        key = "sk_test_abc123def456ghi789jkl0"
        bot = _bot(key=key)
        old_fp = _key_fingerprint(key)
        bot.rotate_key()
        assert bot._old_key_fingerprint == old_fp

    def test_starter_tier_can_rotate(self):
        bot = _bot(tier=Tier.STARTER)
        result = bot.rotate_key()
        assert result["success"] is True

    def test_last_rotation_at_set_after_rotate(self):
        bot = _bot()
        assert bot._last_rotation_at == ""
        bot.rotate_key()
        assert bot._last_rotation_at != ""


# ===========================================================================
# 5. GitHub Secret update
# ===========================================================================

class TestUpdateGithubSecret:
    def test_update_succeeds_in_simulation(self):
        bot = _bot()
        result = bot.update_github_secret()
        assert result["success"] is True
        assert result["secret_name"] == "STRIPE_SECRET_KEY"
        assert result["simulation"] is True

    def test_custom_secret_name(self):
        bot = _bot()
        result = bot.update_github_secret("MY_STRIPE_KEY")
        assert result["secret_name"] == "MY_STRIPE_KEY"

    def test_no_key_raises_validation_error(self):
        bot = _bot(key="")
        with pytest.raises(RotationValidationError):
            bot.update_github_secret()

    def test_repo_included_in_result(self):
        bot = _bot()
        result = bot.update_github_secret()
        assert result["repo"] == "DreamCo-Technologies/Dreamcobots"


# ===========================================================================
# 6. Payment workflow validation
# ===========================================================================

class TestValidatePaymentWorkflows:
    def test_all_workflows_pass_in_simulation(self):
        bot = _bot(key="sk_test_abc123def456ghi789jkl0")
        result = bot.validate_payment_workflows()
        assert result["all_passed"] is True

    def test_payment_capture_workflow_present(self):
        bot = _bot()
        result = bot.validate_payment_workflows()
        names = [r["workflow"] for r in result["results"]]
        assert "payment_capture" in names

    def test_subscription_workflow_present(self):
        bot = _bot()
        result = bot.validate_payment_workflows()
        names = [r["workflow"] for r in result["results"]]
        assert "subscription" in names

    def test_webhook_handling_workflow_present(self):
        bot = _bot()
        result = bot.validate_payment_workflows()
        names = [r["workflow"] for r in result["results"]]
        assert "webhook_handling" in names

    def test_three_workflows_checked(self):
        bot = _bot()
        result = bot.validate_payment_workflows()
        assert len(result["results"]) == 3

    def test_no_key_all_workflows_fail(self):
        bot = _bot(key="")
        result = bot.validate_payment_workflows()
        assert result["all_passed"] is False
        assert all(not r["passed"] for r in result["results"])

    def test_simulation_flag_in_result(self):
        bot = _bot()
        result = bot.validate_payment_workflows()
        assert result["simulation"] is True


# ===========================================================================
# 7. Deactivate old key
# ===========================================================================

class TestDeactivateOldKey:
    def test_deactivate_after_rotation_growth_tier(self):
        bot = _bot(tier=Tier.GROWTH)
        bot.rotate_key()
        result = bot.deactivate_old_key()
        assert result["success"] is True
        assert result["simulation"] is True

    def test_deactivate_clears_old_fingerprint(self):
        bot = _bot(tier=Tier.GROWTH)
        bot.rotate_key()
        assert bot._old_key_fingerprint != ""
        bot.deactivate_old_key()
        assert bot._old_key_fingerprint == ""

    def test_deactivate_without_rotate_raises_validation_error(self):
        bot = _bot(tier=Tier.GROWTH)
        with pytest.raises(RotationValidationError):
            bot.deactivate_old_key()

    def test_starter_tier_lacks_deactivation(self):
        bot = _bot(tier=Tier.STARTER)
        bot.rotate_key()
        with pytest.raises(RotationTierError):
            bot.deactivate_old_key()

    def test_deactivated_fingerprint_in_result(self):
        key = "sk_test_abc123def456ghi789jkl0"
        bot = _bot(tier=Tier.GROWTH, key=key)
        expected_fp = _key_fingerprint(key)
        bot.rotate_key()
        result = bot.deactivate_old_key()
        assert result["deactivated_fingerprint"] == expected_fp


# ===========================================================================
# 8. Notifications
# ===========================================================================

class TestNotify:
    def test_email_notification_starter(self):
        bot = _bot(tier=Tier.STARTER)
        result = bot.notify(rotation_id="rot_test", channel="email")
        assert "email" in result["channels_notified"]

    def test_slack_notification_growth(self):
        bot = _bot(tier=Tier.GROWTH)
        result = bot.notify(rotation_id="rot_test", channel="slack")
        assert "slack" in result["channels_notified"]

    def test_all_channels_enterprise(self):
        bot = _bot(tier=Tier.ENTERPRISE)
        result = bot.notify(rotation_id="rot_test", channel="all")
        assert "email" in result["channels_notified"]
        assert "slack" in result["channels_notified"]

    def test_no_email_configured_skips_email(self):
        bot = StripeKeyRotationBot(
            tier=Tier.STARTER,
            stripe_api_key="sk_test_abc",
            notify_email="",
            simulation_mode=True,
        )
        result = bot.notify(channel="email")
        assert "email" not in result["channels_notified"]

    def test_no_slack_configured_skips_slack(self):
        bot = StripeKeyRotationBot(
            tier=Tier.GROWTH,
            stripe_api_key="sk_test_abc",
            slack_webhook_url="",
            simulation_mode=True,
        )
        result = bot.notify(channel="slack")
        assert "slack" not in result["channels_notified"]

    def test_starter_lacks_slack(self):
        # Starter tier should not have slack feature, so no slack even with URL
        bot = _bot(tier=Tier.STARTER)
        result = bot.notify(rotation_id="rot_test", channel="all")
        assert "slack" not in result["channels_notified"]


# ===========================================================================
# 9. Full rotation pipeline
# ===========================================================================

class TestRunRotation:
    def test_pipeline_succeeds_starter(self):
        bot = _bot(tier=Tier.STARTER)
        result = bot.run_rotation()
        assert result["overall_success"] is True
        assert "pipeline_id" in result
        assert "steps" in result

    def test_pipeline_succeeds_growth(self):
        bot = _bot(tier=Tier.GROWTH)
        result = bot.run_rotation()
        assert result["overall_success"] is True

    def test_pipeline_succeeds_enterprise(self):
        bot = _bot(tier=Tier.ENTERPRISE)
        result = bot.run_rotation()
        assert result["overall_success"] is True

    def test_pipeline_contains_all_starter_steps(self):
        bot = _bot(tier=Tier.STARTER)
        result = bot.run_rotation()
        steps = result["steps"]
        assert "validate_current_key" in steps
        assert "rotate_key" in steps
        assert "update_github_secret" in steps
        assert "validate_payment_workflows" in steps
        assert "notify" in steps

    def test_pipeline_includes_deactivate_for_growth(self):
        bot = _bot(tier=Tier.GROWTH)
        result = bot.run_rotation()
        assert "deactivate_old_key" in result["steps"]

    def test_pipeline_no_deactivate_for_starter(self):
        bot = _bot(tier=Tier.STARTER)
        result = bot.run_rotation()
        assert "deactivate_old_key" not in result["steps"]

    def test_rotation_count_after_pipeline(self):
        bot = _bot()
        bot.run_rotation()
        assert bot._rotation_count == 1

    def test_pipeline_id_unique_per_run(self):
        bot = _bot()
        id1 = bot.run_rotation()["pipeline_id"]
        id2 = bot.run_rotation()["pipeline_id"]
        assert id1 != id2

    def test_secrets_not_in_pipeline_result(self):
        key = "sk_test_super_secret_key_12345678"
        bot = _bot(key=key)
        result = bot.run_rotation()
        result_str = str(result)
        assert key not in result_str
        assert "ghp_test_token_fake" not in result_str


# ===========================================================================
# 10. Audit log
# ===========================================================================

class TestAuditLog:
    def test_audit_log_available_growth(self):
        bot = _bot(tier=Tier.GROWTH)
        bot.run_rotation()
        log = bot.get_audit_log()
        assert isinstance(log, list)
        assert len(log) > 0

    def test_audit_log_events_have_timestamp(self):
        bot = _bot(tier=Tier.GROWTH)
        bot.run_rotation()
        for entry in bot.get_audit_log():
            assert "timestamp" in entry

    def test_audit_log_no_secret_values(self):
        key = "sk_test_audit_secret_key_999"
        bot = _bot(tier=Tier.GROWTH, key=key)
        bot.run_rotation()
        log_str = str(bot.get_audit_log())
        assert key not in log_str

    def test_audit_log_not_available_starter(self):
        bot = _bot(tier=Tier.STARTER)
        with pytest.raises(RotationTierError):
            bot.get_audit_log()

    def test_audit_log_contains_rotation_event(self):
        bot = _bot(tier=Tier.GROWTH)
        bot.rotate_key()
        events = [e["event"] for e in bot.get_audit_log()]
        assert "rotate_key" in events


# ===========================================================================
# 11. Status / reporting
# ===========================================================================

class TestGetStatus:
    def test_status_returns_dict(self):
        bot = _bot()
        status = bot.get_status()
        assert isinstance(status, dict)

    def test_status_includes_tier(self):
        bot = _bot(tier=Tier.GROWTH)
        assert bot.get_status()["tier"] == "growth"

    def test_status_key_configured_true(self):
        bot = _bot(key="sk_test_abc123")
        assert bot.get_status()["key_configured"] is True

    def test_status_key_configured_false_when_missing(self):
        bot = _bot(key="")
        assert bot.get_status()["key_configured"] is False

    def test_status_never_returns_raw_key(self):
        key = "sk_test_status_secret_key_xyz"
        bot = _bot(key=key)
        status_str = str(bot.get_status())
        assert key not in status_str

    def test_status_rotation_count_zero_initially(self):
        bot = _bot()
        assert bot.get_status()["rotation_count"] == 0

    def test_status_last_rotation_never_initially(self):
        bot = _bot()
        assert bot.get_status()["last_rotation_at"] == "never"


# ===========================================================================
# 12. Chat / process interface
# ===========================================================================

class TestChatInterface:
    def test_chat_rotate_command(self):
        bot = _bot()
        result = bot.chat("please rotate the keys")
        assert "message" in result
        assert "rotation" in result["message"].lower() or "key" in result["message"].lower()

    def test_chat_status_command(self):
        bot = _bot()
        result = bot.chat("what is the status?")
        assert "data" in result

    def test_chat_validate_command(self):
        bot = _bot()
        result = bot.chat("validate the key")
        assert "validation" in result["message"].lower() or "key" in result["message"].lower()

    def test_chat_default_response(self):
        bot = _bot()
        result = bot.chat("hello world")
        assert "message" in result
        assert bot.tier.value in result["message"]

    def test_process_delegates_to_chat(self):
        bot = _bot()
        result = bot.process({"command": "status"})
        assert "data" in result

    def test_process_empty_command(self):
        bot = _bot()
        result = bot.process({})
        assert "message" in result

    def test_bot_alias(self):
        assert Bot is StripeKeyRotationBot


# ===========================================================================
# 13. Security — keys never exposed
# ===========================================================================

class TestKeySecurityInvariants:
    """Ensure API keys are never returned in method outputs or exceptions."""

    _SECRET_KEY = "sk_test_never_expose_this_key_abc123xyz789"

    def _bot(self) -> StripeKeyRotationBot:
        return _bot(key=self._SECRET_KEY)

    def _assert_key_not_in(self, value: object) -> None:
        assert self._SECRET_KEY not in str(value), (
            f"SECRET KEY was exposed in output: {str(value)[:200]}"
        )

    def test_validate_does_not_expose_key(self):
        self._assert_key_not_in(self._bot().validate_current_key())

    def test_rotate_does_not_expose_old_key(self):
        self._assert_key_not_in(self._bot().rotate_key())

    def test_rotate_does_not_expose_new_key_in_result(self):
        bot = self._bot()
        result = bot.rotate_key()
        # The internal _stripe_key was replaced; the old key must not appear
        self._assert_key_not_in(result)

    def test_update_github_secret_does_not_expose_key(self):
        self._assert_key_not_in(self._bot().update_github_secret())

    def test_validate_workflows_does_not_expose_key(self):
        self._assert_key_not_in(self._bot().validate_payment_workflows())

    def test_run_rotation_does_not_expose_key(self):
        self._assert_key_not_in(self._bot().run_rotation())

    def test_status_does_not_expose_key(self):
        self._assert_key_not_in(self._bot().get_status())

    def test_chat_does_not_expose_key(self):
        self._assert_key_not_in(self._bot().chat("rotate"))

    def test_github_token_not_in_status(self):
        bot = self._bot()
        assert "ghp_test_token_fake" not in str(bot.get_status())
