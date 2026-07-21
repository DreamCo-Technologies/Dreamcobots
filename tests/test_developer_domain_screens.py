"""
Tests for frontend/screens/developer_settings_screen.py
and frontend/screens/domain_manager_screen.py.
"""

import pytest
from frontend.screens.developer_settings_screen import DeveloperSettingsScreen
from frontend.screens.domain_manager_screen import DomainManagerScreen


# ===========================================================================
# DeveloperSettingsScreen
# ===========================================================================

class TestDeveloperSettingsScreenInit:
    def test_default_user_id(self):
        s = DeveloperSettingsScreen()
        assert s.user_id == ""

    def test_default_api_keys_empty(self):
        s = DeveloperSettingsScreen()
        assert s.api_keys == []

    def test_default_selected_category(self):
        s = DeveloperSettingsScreen()
        assert s.selected_category == "all"

    def test_default_oauth_providers(self):
        s = DeveloperSettingsScreen()
        assert s.oauth_providers == {"google": False, "github": False}

    def test_valid_categories(self):
        assert "read_only" in DeveloperSettingsScreen.VALID_CATEGORIES
        assert "full_access" in DeveloperSettingsScreen.VALID_CATEGORIES
        assert "bot_runner" in DeveloperSettingsScreen.VALID_CATEGORIES
        assert "webhook" in DeveloperSettingsScreen.VALID_CATEGORIES
        assert "analytics" in DeveloperSettingsScreen.VALID_CATEGORIES
        assert len(DeveloperSettingsScreen.VALID_CATEGORIES) == 5


class TestDeveloperSettingsScreenRender:
    def setup_method(self):
        self.screen = DeveloperSettingsScreen(
            user_id="usr_test",
            user_tier="PRO",
            api_keys=[
                {"key_id": "kid_001", "label": "K1", "category": "analytics",
                 "tier": "pro", "call_count": 10, "is_active": True, "created_at": 1700000000.0},
                {"key_id": "kid_002", "label": "K2", "category": "bot_runner",
                 "tier": "pro", "call_count": 5, "is_active": True, "created_at": 1700000001.0},
            ],
        )

    def test_render_returns_dict(self):
        r = self.screen.render()
        assert isinstance(r, dict)

    def test_screen_name_correct(self):
        r = self.screen.render()
        assert r["screen"] == "DeveloperSettingsScreen"

    def test_route_correct(self):
        r = self.screen.render()
        assert r["route"] == "/settings/developer"

    def test_oauth_section_has_google_button(self):
        r = self.screen.render()
        btns = r["widgets"]["oauth_section"]["buttons"]
        ids = [b["id"] for b in btns]
        assert "btn_oauth_google" in ids

    def test_oauth_section_has_github_button(self):
        r = self.screen.render()
        btns = r["widgets"]["oauth_section"]["buttons"]
        ids = [b["id"] for b in btns]
        assert "btn_oauth_github" in ids

    def test_google_action_is_post(self):
        r = self.screen.render()
        btns = r["widgets"]["oauth_section"]["buttons"]
        google = next(b for b in btns if b["id"] == "btn_oauth_google")
        assert "POST" in google["action"]

    def test_github_action_is_post(self):
        r = self.screen.render()
        btns = r["widgets"]["oauth_section"]["buttons"]
        github = next(b for b in btns if b["id"] == "btn_oauth_github")
        assert "POST" in github["action"]

    def test_generate_key_button_present(self):
        r = self.screen.render()
        btn = r["widgets"]["api_key_generate_section"]["button"]
        assert btn["id"] == "btn_generate_key"

    def test_generate_key_action(self):
        r = self.screen.render()
        btn = r["widgets"]["api_key_generate_section"]["button"]
        assert "POST" in btn["action"]

    def test_keys_list_count_all(self):
        r = self.screen.render()
        assert r["widgets"]["api_keys_section"]["keys_list"]["count"] == 2

    def test_filter_by_category_analytics(self):
        self.screen.selected_category = "analytics"
        r = self.screen.render()
        assert r["widgets"]["api_keys_section"]["keys_list"]["count"] == 1

    def test_revoke_button_on_each_key(self):
        r = self.screen.render()
        items = r["widgets"]["api_keys_section"]["keys_list"]["items"]
        for item in items:
            assert "revoke_button" in item
            assert "DELETE" in item["revoke_button"]["action"]

    def test_usage_button_present(self):
        r = self.screen.render()
        btn = r["widgets"]["api_keys_section"]["usage_button"]
        assert btn["id"] == "btn_view_usage"
        assert "GET" in btn["action"]


class TestDeveloperSettingsScreenToDict:
    def test_to_dict_has_screen_name(self):
        s = DeveloperSettingsScreen()
        d = s.to_dict()
        assert d["screen"] == "DeveloperSettingsScreen"

    def test_to_dict_includes_user_id(self):
        s = DeveloperSettingsScreen(user_id="usr_abc")
        d = s.to_dict()
        assert d["user_id"] == "usr_abc"


class TestDeveloperSettingsScreenDemo:
    def test_demo_returns_instance(self):
        s = DeveloperSettingsScreen.demo()
        assert isinstance(s, DeveloperSettingsScreen)

    def test_demo_has_api_keys(self):
        s = DeveloperSettingsScreen.demo()
        assert len(s.api_keys) > 0

    def test_demo_google_connected(self):
        s = DeveloperSettingsScreen.demo()
        assert s.oauth_providers["google"] is True

    def test_demo_renders(self):
        rendered = DeveloperSettingsScreen.demo().render()
        assert rendered["screen"] == "DeveloperSettingsScreen"


# ===========================================================================
# DomainManagerScreen
# ===========================================================================

_SAMPLE_DOMAINS = [
    {"domain_id": "dom_001", "name": "dreamco.io", "registrar": "Namecheap",
     "status": "owned", "registration_cost_usd": 39.99, "ask_price_usd": None,
     "sold_price_usd": None, "profit_usd": None, "estimated_value_usd": 2499.99,
     "expiry_date": "2026-03-15"},
    {"domain_id": "dom_002", "name": "aibot.com", "registrar": "GoDaddy",
     "status": "listed", "registration_cost_usd": 12.99, "ask_price_usd": 4999.0,
     "sold_price_usd": None, "profit_usd": None, "estimated_value_usd": 5800.0,
     "expiry_date": "2025-11-01"},
    {"domain_id": "dom_003", "name": "earnmore.ai", "registrar": "Namecheap",
     "status": "flipped", "registration_cost_usd": 89.99, "ask_price_usd": None,
     "sold_price_usd": 3200.0, "profit_usd": 3110.01, "estimated_value_usd": 0.0,
     "expiry_date": None},
]


class TestDomainManagerScreenInit:
    def test_default_user_id(self):
        s = DomainManagerScreen()
        assert s.user_id == ""

    def test_default_domains_empty(self):
        s = DomainManagerScreen()
        assert s.domains == []

    def test_default_selected_status(self):
        s = DomainManagerScreen()
        assert s.selected_status == "all"

    def test_status_filters(self):
        assert "all" in DomainManagerScreen.STATUS_FILTERS
        assert "owned" in DomainManagerScreen.STATUS_FILTERS
        assert "listed" in DomainManagerScreen.STATUS_FILTERS
        assert "sold" in DomainManagerScreen.STATUS_FILTERS
        assert "flipped" in DomainManagerScreen.STATUS_FILTERS


class TestDomainManagerScreenRender:
    def setup_method(self):
        self.screen = DomainManagerScreen(
            user_id="usr_test",
            domains=_SAMPLE_DOMAINS,
            portfolio_summary={
                "total_domains": 3,
                "owned": 1,
                "listed": 1,
                "sold": 0,
                "flipped": 1,
                "total_invested_usd": 142.97,
                "total_revenue_usd": 3200.0,
                "total_profit_usd": 3057.03,
                "portfolio_estimated_value_usd": 8299.99,
            },
        )

    def test_render_returns_dict(self):
        assert isinstance(self.screen.render(), dict)

    def test_screen_name(self):
        assert self.screen.render()["screen"] == "DomainManagerScreen"

    def test_route(self):
        assert self.screen.render()["route"] == "/domains"

    def test_register_button_present(self):
        r = self.screen.render()
        btn_ids = [b["id"] for b in r["widgets"]["action_buttons"]]
        assert "btn_register_domain" in btn_ids

    def test_flip_button_present(self):
        r = self.screen.render()
        btn_ids = [b["id"] for b in r["widgets"]["action_buttons"]]
        assert "btn_flip_domain" in btn_ids

    def test_register_action_is_post(self):
        r = self.screen.render()
        btn = next(b for b in r["widgets"]["action_buttons"] if b["id"] == "btn_register_domain")
        assert "POST" in btn["action"]

    def test_domains_list_count_all(self):
        r = self.screen.render()
        assert r["widgets"]["domains_list"]["count"] == 3

    def test_filter_by_owned(self):
        self.screen.selected_status = "owned"
        r = self.screen.render()
        assert r["widgets"]["domains_list"]["count"] == 1

    def test_filter_by_listed(self):
        self.screen.selected_status = "listed"
        r = self.screen.render()
        assert r["widgets"]["domains_list"]["count"] == 1

    def test_filter_by_flipped(self):
        self.screen.selected_status = "flipped"
        r = self.screen.render()
        assert r["widgets"]["domains_list"]["count"] == 1

    def test_sell_button_on_each_domain(self):
        r = self.screen.render()
        items = r["widgets"]["domains_list"]["items"]
        for item in items:
            assert "sell_button" in item

    def test_sell_button_enabled_for_owned(self):
        r = self.screen.render()
        items = r["widgets"]["domains_list"]["items"]
        owned = next(i for i in items if i["status"] == "owned")
        assert owned["sell_button"]["enabled"] is True

    def test_sell_button_disabled_for_flipped(self):
        r = self.screen.render()
        items = r["widgets"]["domains_list"]["items"]
        flipped = next(i for i in items if i["status"] == "flipped")
        assert flipped["sell_button"]["enabled"] is False

    def test_portfolio_summary_card_present(self):
        r = self.screen.render()
        card = r["widgets"]["portfolio_summary_card"]
        assert card["total_domains"] == 3

    def test_search_section_present(self):
        r = self.screen.render()
        assert "search_section" in r["widgets"]

    def test_valuate_button_in_search_section(self):
        r = self.screen.render()
        assert r["widgets"]["search_section"]["valuate_button"]["id"] == "btn_valuate"

    def test_filter_row_has_all_statuses(self):
        r = self.screen.render()
        opts = r["widgets"]["filter_row"]["options"]
        for status in DomainManagerScreen.STATUS_FILTERS:
            assert status in opts


class TestDomainManagerScreenToDict:
    def test_has_screen_name(self):
        s = DomainManagerScreen()
        assert s.to_dict()["screen"] == "DomainManagerScreen"

    def test_includes_domains(self):
        s = DomainManagerScreen(domains=_SAMPLE_DOMAINS)
        assert s.to_dict()["domains"] == _SAMPLE_DOMAINS


class TestDomainManagerScreenDemo:
    def test_returns_instance(self):
        assert isinstance(DomainManagerScreen.demo(), DomainManagerScreen)

    def test_demo_has_domains(self):
        assert len(DomainManagerScreen.demo().domains) > 0

    def test_demo_renders(self):
        r = DomainManagerScreen.demo().render()
        assert r["screen"] == "DomainManagerScreen"

    def test_demo_has_portfolio_summary(self):
        s = DomainManagerScreen.demo()
        assert s.portfolio_summary["total_domains"] > 0
