"""Tests for NavigationMixin, BotSettings, and BaseBot integration."""

import pytest

from BuddyAI.navigation import NavigationMixin, NAV_BUTTONS, _NAV_BY_ID
from BuddyAI.settings import BotSettings
from BuddyAI.base_bot import BaseBot


# ---------------------------------------------------------------------------
# NavigationMixin
# ---------------------------------------------------------------------------

class _MinimalBot(NavigationMixin):
    """Minimal bot that only mixes in NavigationMixin."""


@pytest.fixture
def nav_bot():
    return _MinimalBot()


def test_nav_buttons_returns_all_25(nav_bot):
    buttons = nav_bot.nav_buttons()
    assert len(buttons) == 25


def test_nav_buttons_have_required_fields(nav_bot):
    for btn in nav_bot.nav_buttons():
        assert "id" in btn
        assert "label" in btn
        assert "icon" in btn
        assert "route" in btn


def test_navigate_valid(nav_bot):
    result = nav_bot.navigate("chat")
    assert result["success"] is True
    assert result["nav_action"] == "chat"
    assert result["route"] == "/chat"


def test_navigate_unknown(nav_bot):
    result = nav_bot.navigate("nonexistent")
    assert result["success"] is False
    assert "nonexistent" in result["error"]


def test_navigate_with_context(nav_bot):
    result = nav_bot.navigate("crypto", context={"wallet": "abc"})
    assert result["context"] == {"wallet": "abc"}


@pytest.mark.parametrize("method_name, button_id", [
    ("nav_chat", "chat"),
    ("nav_empire_hq", "empire_hq"),
    ("nav_divisions", "divisions"),
    ("nav_bot_fleet", "bot_fleet"),
    ("nav_deal_analyzer", "deal_analyzer"),
    ("nav_formula_vault", "formula_vault"),
    ("nav_learning_matrix", "learning_matrix"),
    ("nav_ai_leaders", "ai_leaders"),
    ("nav_ai_models_hub", "ai_models_hub"),
    ("nav_ai_ecosystem", "ai_ecosystem"),
    ("nav_orchestration", "orchestration"),
    ("nav_marketplace", "marketplace"),
    ("nav_crypto", "crypto"),
    ("nav_payments", "payments"),
    ("nav_biz_launch", "biz_launch"),
    ("nav_code_lab", "code_lab"),
    ("nav_loans_deals", "loans_deals"),
    ("nav_debug_intel", "debug_intel"),
    ("nav_revenue", "revenue"),
    ("nav_pricing", "pricing"),
    ("nav_connections", "connections"),
    ("nav_time_capsule", "time_capsule"),
    ("nav_cost_tracking", "cost_tracking"),
    ("nav_autonomy", "autonomy"),
    ("nav_recent_chats", "recent_chats"),
])
def test_nav_shortcut_methods(nav_bot, method_name, button_id):
    fn = getattr(nav_bot, method_name)
    result = fn()
    assert result["success"] is True
    assert result["nav_action"] == button_id


# ---------------------------------------------------------------------------
# BotSettings
# ---------------------------------------------------------------------------

@pytest.fixture
def settings():
    return BotSettings(bot_name="TestBot")


def test_settings_set_and_get(settings):
    settings.set("theme", "dark")
    assert settings.get("theme") == "dark"


def test_settings_get_default(settings):
    assert settings.get("missing_key", "fallback") == "fallback"


def test_settings_delete(settings):
    settings.set("x", 1)
    assert settings.delete("x") is True
    assert settings.get("x") is None


def test_settings_delete_missing(settings):
    assert settings.delete("not_there") is False


def test_settings_all_settings(settings):
    settings.set("a", 1)
    settings.set("b", 2)
    all_s = settings.all_settings()
    assert all_s["a"] == 1
    assert all_s["b"] == 2


def test_settings_change_log(settings):
    settings.set("key", "value")
    log = settings.change_log()
    assert len(log) == 1
    assert log[0]["key"] == "key"


def test_custom_button_add_and_invoke(settings):
    settings.add_custom_button(
        button_id="my_btn",
        label="My Button",
        handler=lambda ctx: {"result": ctx.get("x", 0) * 2},
        icon="⭐",
    )
    result = settings.invoke_button("my_btn", {"x": 5})
    assert result == {"result": 10}


def test_custom_button_list(settings):
    settings.add_custom_button("btn1", "Button 1", handler=lambda _: None)
    btns = settings.list_custom_buttons()
    assert any(b["id"] == "btn1" for b in btns)
    assert all("handler" not in b for b in btns)


def test_custom_button_remove(settings):
    settings.add_custom_button("tmp", "Temp", handler=lambda _: None)
    assert settings.remove_custom_button("tmp") is True
    assert settings.remove_custom_button("tmp") is False


def test_custom_button_invoke_unknown(settings):
    with pytest.raises(KeyError):
        settings.invoke_button("no_such_button")


def test_settings_summary(settings):
    settings.set("x", 42)
    summary = settings.summary()
    assert summary["bot"] == "TestBot"
    assert summary["settings"]["x"] == 42


def test_settings_defaults(settings):
    s = BotSettings(bot_name="X", defaults={"color": "blue"})
    assert s.get("color") == "blue"


# ---------------------------------------------------------------------------
# BaseBot integration
# ---------------------------------------------------------------------------

class _ConcreteBot(BaseBot):
    pass


def test_base_bot_has_nav_buttons():
    bot = _ConcreteBot()
    assert len(bot.nav_buttons()) == 25


def test_base_bot_has_settings():
    bot = _ConcreteBot()
    assert isinstance(bot.settings, BotSettings)


def test_base_bot_capabilities_summary_includes_nav():
    bot = _ConcreteBot()
    summary = bot.capabilities_summary()
    assert summary["nav_buttons"] == 25
    assert "custom_buttons" in summary


def test_base_bot_navigate():
    bot = _ConcreteBot()
    result = bot.navigate("marketplace")
    assert result["success"] is True
    assert result["route"] == "/marketplace"
