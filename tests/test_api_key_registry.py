"""
Tests for saas/auth/api_key_registry.py — ClientApiKeyRegistry.
"""

import pytest
from saas.auth.api_key_registry import (
    ClientApiKeyRegistry,
    ClientApiKey,
    API_KEY_CATEGORIES,
    _tier_prefix,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_registry() -> ClientApiKeyRegistry:
    return ClientApiKeyRegistry()


def _create_key(registry, user_id="usr_abc", label="Test Key",
                category="full_access", tier="free"):
    return registry.generate_key(user_id=user_id, label=label,
                                 category=category, tier=tier)


# ===========================================================================
# _tier_prefix
# ===========================================================================

class TestTierPrefix:
    def test_enterprise(self):
        assert _tier_prefix("enterprise") == "ent"

    def test_pro(self):
        assert _tier_prefix("pro") == "pro"

    def test_free(self):
        assert _tier_prefix("free") == "free"

    def test_unknown_defaults_to_free(self):
        assert _tier_prefix("starter") == "free"

    def test_case_insensitive(self):
        assert _tier_prefix("ENTERPRISE") == "ent"
        assert _tier_prefix("Pro") == "pro"


# ===========================================================================
# API_KEY_CATEGORIES
# ===========================================================================

class TestApiKeyCategories:
    def test_contains_read_only(self):
        assert "read_only" in API_KEY_CATEGORIES

    def test_contains_full_access(self):
        assert "full_access" in API_KEY_CATEGORIES

    def test_contains_bot_runner(self):
        assert "bot_runner" in API_KEY_CATEGORIES

    def test_contains_webhook(self):
        assert "webhook" in API_KEY_CATEGORIES

    def test_contains_analytics(self):
        assert "analytics" in API_KEY_CATEGORIES

    def test_count(self):
        assert len(API_KEY_CATEGORIES) == 5


# ===========================================================================
# generate_key
# ===========================================================================

class TestGenerateKey:
    def test_returns_client_api_key(self):
        r = make_registry()
        key = _create_key(r)
        assert isinstance(key, ClientApiKey)

    def test_key_id_starts_with_kid(self):
        r = make_registry()
        key = _create_key(r)
        assert key.key_id.startswith("kid_")

    def test_key_value_starts_with_dc_free(self):
        r = make_registry()
        key = _create_key(r, tier="free")
        assert key.key.startswith("dc_free_")

    def test_key_value_starts_with_dc_pro(self):
        r = make_registry()
        key = _create_key(r, tier="pro")
        assert key.key.startswith("dc_pro_")

    def test_key_value_starts_with_dc_ent(self):
        r = make_registry()
        key = _create_key(r, tier="enterprise")
        assert key.key.startswith("dc_ent_")

    def test_key_stored_and_retrievable(self):
        r = make_registry()
        key = _create_key(r)
        retrieved = r.get_key_by_value(key.key)
        assert retrieved is not None
        assert retrieved.key_id == key.key_id

    def test_label_stored(self):
        r = make_registry()
        key = _create_key(r, label="My Key")
        assert key.label == "My Key"

    def test_category_stored(self):
        r = make_registry()
        key = _create_key(r, category="analytics")
        assert key.category == "analytics"

    def test_category_lowercased(self):
        r = make_registry()
        key = _create_key(r, category="Analytics")
        assert key.category == "analytics"

    def test_invalid_category_raises(self):
        r = make_registry()
        with pytest.raises(ValueError, match="Invalid category"):
            r.generate_key("usr_x", "Label", "not_a_category")

    def test_empty_label_raises(self):
        r = make_registry()
        with pytest.raises(ValueError, match="label"):
            r.generate_key("usr_x", "", "full_access")

    def test_whitespace_only_label_raises(self):
        r = make_registry()
        with pytest.raises(ValueError, match="label"):
            r.generate_key("usr_x", "   ", "full_access")

    def test_two_keys_have_different_key_ids(self):
        r = make_registry()
        k1 = _create_key(r)
        k2 = _create_key(r)
        assert k1.key_id != k2.key_id

    def test_two_keys_have_different_key_values(self):
        r = make_registry()
        k1 = _create_key(r)
        k2 = _create_key(r)
        assert k1.key != k2.key

    def test_is_active_default_true(self):
        r = make_registry()
        key = _create_key(r)
        assert key.is_active is True

    def test_call_count_starts_at_zero(self):
        r = make_registry()
        key = _create_key(r)
        assert key.call_count == 0


# ===========================================================================
# list_keys
# ===========================================================================

class TestListKeys:
    def setup_method(self):
        self.r = make_registry()
        self.uid = "usr_list"
        _create_key(self.r, user_id=self.uid, label="K1", category="analytics")
        _create_key(self.r, user_id=self.uid, label="K2", category="bot_runner")
        _create_key(self.r, user_id=self.uid, label="K3", category="analytics")

    def test_list_all_returns_three(self):
        keys = self.r.list_keys(self.uid)
        assert len(keys) == 3

    def test_filter_by_category_analytics(self):
        keys = self.r.list_keys(self.uid, category="analytics")
        assert len(keys) == 2
        assert all(k.category == "analytics" for k in keys)

    def test_filter_by_category_bot_runner(self):
        keys = self.r.list_keys(self.uid, category="bot_runner")
        assert len(keys) == 1

    def test_different_user_sees_no_keys(self):
        keys = self.r.list_keys("usr_other")
        assert keys == []

    def test_revoked_excluded_by_default(self):
        keys = self.r.list_keys(self.uid)
        kid = keys[0].key_id
        self.r.revoke_key(self.uid, kid)
        active = self.r.list_keys(self.uid)
        assert len(active) == 2

    def test_revoked_included_when_active_only_false(self):
        keys = self.r.list_keys(self.uid)
        kid = keys[0].key_id
        self.r.revoke_key(self.uid, kid)
        all_keys = self.r.list_keys(self.uid, active_only=False)
        assert len(all_keys) == 3


# ===========================================================================
# revoke_key
# ===========================================================================

class TestRevokeKey:
    def test_revoke_sets_is_active_false(self):
        r = make_registry()
        key = _create_key(r, user_id="usr_rev")
        r.revoke_key("usr_rev", key.key_id)
        retrieved = r.get_key_by_value(key.key)
        assert retrieved is None  # inactive keys not returned

    def test_revoke_returns_key_record(self):
        r = make_registry()
        key = _create_key(r, user_id="usr_rev2")
        revoked = r.revoke_key("usr_rev2", key.key_id)
        assert revoked.key_id == key.key_id
        assert revoked.is_active is False

    def test_revoke_wrong_user_raises_key_error(self):
        r = make_registry()
        key = _create_key(r, user_id="usr_a")
        with pytest.raises(KeyError):
            r.revoke_key("usr_b", key.key_id)

    def test_revoke_nonexistent_raises_key_error(self):
        r = make_registry()
        with pytest.raises(KeyError):
            r.revoke_key("usr_a", "kid_ffffffff")


# ===========================================================================
# get_key_by_value
# ===========================================================================

class TestGetKeyByValue:
    def test_returns_active_key(self):
        r = make_registry()
        key = _create_key(r, user_id="usr_gk")
        found = r.get_key_by_value(key.key)
        assert found is not None
        assert found.key_id == key.key_id

    def test_returns_none_for_revoked(self):
        r = make_registry()
        key = _create_key(r, user_id="usr_gk2")
        r.revoke_key("usr_gk2", key.key_id)
        assert r.get_key_by_value(key.key) is None

    def test_returns_none_for_unknown(self):
        r = make_registry()
        assert r.get_key_by_value("dc_free_notakey") is None


# ===========================================================================
# record_usage
# ===========================================================================

class TestRecordUsage:
    def test_increments_call_count(self):
        r = make_registry()
        key = _create_key(r, user_id="usr_ru")
        r.record_usage(key.key_id)
        r.record_usage(key.key_id)
        found = r.get_key_by_value(key.key)
        assert found.call_count == 2

    def test_updates_last_used_at(self):
        r = make_registry()
        key = _create_key(r, user_id="usr_ru2")
        assert key.last_used_at is None
        r.record_usage(key.key_id)
        assert r._store[key.key_id].last_used_at is not None

    def test_record_usage_unknown_id_no_error(self):
        r = make_registry()
        r.record_usage("kid_nonexistent")  # should not raise


# ===========================================================================
# usage_summary
# ===========================================================================

class TestUsageSummary:
    def setup_method(self):
        self.r = make_registry()
        self.uid = "usr_sum"
        k1 = _create_key(self.r, user_id=self.uid, category="analytics")
        k2 = _create_key(self.r, user_id=self.uid, category="bot_runner")
        self.r.record_usage(k1.key_id)
        self.r.record_usage(k1.key_id)
        self.r.record_usage(k2.key_id)

    def test_total_calls(self):
        s = self.r.usage_summary(self.uid)
        assert s["total_calls"] == 3

    def test_by_category(self):
        s = self.r.usage_summary(self.uid)
        assert s["by_category"]["analytics"] == 2
        assert s["by_category"]["bot_runner"] == 1

    def test_total_keys(self):
        s = self.r.usage_summary(self.uid)
        assert s["total_keys"] == 2

    def test_active_keys(self):
        s = self.r.usage_summary(self.uid)
        assert s["active_keys"] == 2

    def test_user_id_in_response(self):
        s = self.r.usage_summary(self.uid)
        assert s["user_id"] == self.uid

    def test_empty_for_unknown_user(self):
        s = self.r.usage_summary("usr_nobody")
        assert s["total_keys"] == 0
        assert s["total_calls"] == 0


# ===========================================================================
# to_dict
# ===========================================================================

class TestClientApiKeyToDict:
    def test_no_key_by_default(self):
        r = make_registry()
        key = _create_key(r)
        d = key.to_dict()
        assert "key" not in d

    def test_key_included_when_requested(self):
        r = make_registry()
        key = _create_key(r)
        d = key.to_dict(include_key=True)
        assert "key" in d
        assert d["key"] == key.key

    def test_dict_has_expected_fields(self):
        r = make_registry()
        key = _create_key(r)
        d = key.to_dict()
        for field in ("key_id", "user_id", "label", "category", "tier",
                      "created_at", "last_used_at", "is_active", "call_count"):
            assert field in d
