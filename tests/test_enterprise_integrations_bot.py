"""Tests for bots/enterprise_integrations_bot — Big Tech & AI integrations hub."""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.enterprise_integrations_bot.enterprise_integrations_bot import (
    EnterpriseIntegrationsBot,
    EnterpriseIntegrationsBotTierError,
    EnterpriseIntegrationsBotError,
    ProviderNotFoundError,
    SubscriptionError,
    ProviderCategory,
    Provider,
    Subscription,
    APICallRecord,
    _PROVIDERS,
    _PROVIDER_INDEX,
)
from bots.enterprise_integrations_bot.tiers import (
    get_bot_tier_info,
    BOT_FEATURES,
)


# ===========================================================================
# Tier tests
# ===========================================================================

class TestTiers:
    def test_all_three_tiers_have_features(self):
        for tier in (Tier.FREE, Tier.PRO, Tier.ENTERPRISE):
            assert len(BOT_FEATURES[tier.value]) > 0

    def test_enterprise_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.ENTERPRISE.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_pro_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_get_tier_info_returns_expected_keys(self):
        for tier in (Tier.FREE, Tier.PRO, Tier.ENTERPRISE):
            info = get_bot_tier_info(tier)
            for key in ("tier", "name", "price_usd_monthly", "features", "support_level"):
                assert key in info

    def test_free_price_is_zero(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_pro_price_greater_than_free(self):
        assert get_bot_tier_info(Tier.PRO)["price_usd_monthly"] > 0.0

    def test_enterprise_price_greater_than_pro(self):
        assert (
            get_bot_tier_info(Tier.ENTERPRISE)["price_usd_monthly"]
            > get_bot_tier_info(Tier.PRO)["price_usd_monthly"]
        )

    def test_free_features_list_contains_google(self):
        assert any("Google" in f for f in BOT_FEATURES[Tier.FREE.value])

    def test_enterprise_features_list_contains_dream_ai(self):
        assert any("Dream AI" in f for f in BOT_FEATURES[Tier.ENTERPRISE.value])


# ===========================================================================
# Instantiation tests
# ===========================================================================

class TestInstantiation:
    def test_default_tier_is_free(self):
        bot = EnterpriseIntegrationsBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_custom_user_id(self):
        bot = EnterpriseIntegrationsBot(user_id="alice")
        assert bot.user_id == "alice"

    def test_config_loaded(self):
        bot = EnterpriseIntegrationsBot()
        assert bot.config is not None

    def test_free_enables_fewer_providers_than_enterprise(self):
        free_bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        ent_bot = EnterpriseIntegrationsBot(tier=Tier.ENTERPRISE)
        assert len(free_bot._enabled_providers) < len(ent_bot._enabled_providers)


# ===========================================================================
# Provider catalogue tests
# ===========================================================================

class TestProviderCatalogue:
    def test_providers_exist(self):
        assert len(_PROVIDERS) > 0

    def test_provider_index_matches_providers(self):
        for p in _PROVIDERS:
            assert p.provider_id in _PROVIDER_INDEX

    def test_big_tech_ai_providers_present(self):
        ids = {p.provider_id for p in _PROVIDERS}
        for pid in ("google_cloud_ai", "enterprise_ai", "microsoft_azure_ai",
                    "nvidia_ai", "aws_ai"):
            assert pid in ids

    def test_big_data_analytics_providers_present(self):
        ids = {p.provider_id for p in _PROVIDERS}
        for pid in ("databricks", "palantir", "snowflake", "tableau"):
            assert pid in ids

    def test_communication_providers_present(self):
        ids = {p.provider_id for p in _PROVIDERS}
        for pid in ("slack", "microsoft_teams", "zoom"):
            assert pid in ids

    def test_dream_proprietary_providers_present(self):
        ids = {p.provider_id for p in _PROVIDERS}
        for pid in ("dream_llm", "dream_vision", "dream_voice",
                    "dream_code", "dream_analytics", "dream_collab"):
            assert pid in ids

    def test_provider_to_dict_has_required_keys(self):
        for p in _PROVIDERS:
            d = p.to_dict()
            for key in ("provider_id", "name", "category", "description",
                        "services", "min_tier"):
                assert key in d

    def test_each_provider_has_services(self):
        for p in _PROVIDERS:
            assert len(p.services) > 0


# ===========================================================================
# list_providers / get_provider tests
# ===========================================================================

class TestListProviders:
    def test_free_list_providers_non_empty(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        providers = bot.list_providers()
        assert len(providers) > 0

    def test_enterprise_has_more_providers_than_free(self):
        free_bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        ent_bot = EnterpriseIntegrationsBot(tier=Tier.ENTERPRISE)
        assert len(ent_bot.list_providers()) > len(free_bot.list_providers())

    def test_filter_by_category(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.ENTERPRISE)
        ai_providers = bot.list_providers(category=ProviderCategory.BIG_TECH_AI)
        for p in ai_providers:
            assert p["category"] == ProviderCategory.BIG_TECH_AI.value

    def test_list_all_providers_includes_unavailable(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        all_providers = bot.list_all_providers()
        available_count = bot.list_providers()
        assert len(all_providers) > len(available_count)

    def test_get_provider_known(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        p = bot.get_provider("google_cloud_ai")
        assert p["provider_id"] == "google_cloud_ai"

    def test_get_provider_unknown_raises(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        with pytest.raises(ProviderNotFoundError):
            bot.get_provider("no_such_provider")

    def test_get_provider_shows_availability(self):
        free_bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        # microsoft_azure_ai requires PRO
        p = free_bot.get_provider("microsoft_azure_ai")
        assert p["available_on_current_tier"] is False

    def test_get_provider_available_on_correct_tier(self):
        pro_bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        p = pro_bot.get_provider("microsoft_azure_ai")
        assert p["available_on_current_tier"] is True


# ===========================================================================
# call_provider / API routing tests
# ===========================================================================

class TestCallProvider:
    def test_call_google_ai_free(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.call_provider("google_cloud_ai", "chat", {"prompt": "hello"})
        assert result["provider"] == "google_cloud_ai"
        assert result["status"] == "ok"

    def test_call_enterprise_ai_free(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.call_provider("enterprise_ai", "chat", {})
        assert result["provider"] == "enterprise_ai"
        assert result["status"] == "ok"

    def test_call_azure_ai_requires_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        with pytest.raises(EnterpriseIntegrationsBotTierError):
            bot.call_provider("microsoft_azure_ai", "chat", {})

    def test_call_azure_ai_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.call_provider("microsoft_azure_ai", "chat", {})
        assert result["provider"] == "microsoft_azure_ai"

    def test_call_nvidia_ai_requires_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        with pytest.raises(EnterpriseIntegrationsBotTierError):
            bot.call_provider("nvidia_ai", "inference", {})

    def test_call_nvidia_ai_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.call_provider("nvidia_ai", "inference", {})
        assert result["status"] == "ok"

    def test_call_aws_ai_requires_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        with pytest.raises(EnterpriseIntegrationsBotTierError):
            bot.call_provider("aws_ai", "invoke", {})

    def test_call_aws_ai_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.call_provider("aws_ai", "invoke", {})
        assert result["provider"] == "aws_ai"

    def test_call_unknown_provider_raises(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.ENTERPRISE)
        with pytest.raises(ProviderNotFoundError):
            bot.call_provider("no_such_provider", "action", {})

    def test_call_logs_record(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        bot.call_provider("google_cloud_ai", "chat", {})
        assert len(bot._call_log) == 1

    def test_multiple_calls_logged(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        for _ in range(5):
            bot.call_provider("google_cloud_ai", "chat", {})
        assert len(bot._call_log) == 5


# ===========================================================================
# Convenience wrapper tests
# ===========================================================================

class TestConvenienceWrappers:
    def test_google_ai_wrapper(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.google_ai("chat")
        assert result["provider"] == "google_cloud_ai"

    def test_enterprise_ai_wrapper(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.enterprise_ai("nlu")
        assert result["provider"] == "enterprise_ai"

    def test_azure_ai_wrapper_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.azure_ai("chat")
        assert result["provider"] == "microsoft_azure_ai"

    def test_nvidia_ai_wrapper_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.nvidia_ai("inference")
        assert result["provider"] == "nvidia_ai"

    def test_aws_ai_wrapper_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.aws_ai("invoke")
        assert result["provider"] == "aws_ai"

    def test_databricks_wrapper_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.databricks("query")
        assert result["provider"] == "databricks"

    def test_snowflake_wrapper_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.snowflake("query")
        assert result["provider"] == "snowflake"

    def test_tableau_wrapper_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.tableau("dashboard")
        assert result["provider"] == "tableau"

    def test_palantir_wrapper_enterprise(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.ENTERPRISE)
        result = bot.palantir("pipeline")
        assert result["provider"] == "palantir"

    def test_palantir_requires_enterprise(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        with pytest.raises(EnterpriseIntegrationsBotTierError):
            bot.palantir("pipeline")

    def test_slack_wrapper_free(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.slack("post_message", {"channel": "#test", "text": "hi"})
        assert result["provider"] == "slack"

    def test_teams_wrapper_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.teams("post_message")
        assert result["provider"] == "microsoft_teams"

    def test_zoom_wrapper_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.zoom("create_meeting")
        assert result["provider"] == "zoom"

    def test_dream_llm_wrapper_free(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.dream_llm("chat", {"prompt": "hello"})
        assert result["provider"] == "dream_llm"
        assert result.get("proprietary") is True

    def test_dream_vision_wrapper_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.dream_vision("image_analysis")
        assert result["provider"] == "dream_vision"
        assert result.get("proprietary") is True

    def test_dream_code_wrapper_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.dream_code("code_completion")
        assert result["provider"] == "dream_code"

    def test_dream_analytics_wrapper_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.dream_analytics("dashboard")
        assert result["provider"] == "dream_analytics"

    def test_dream_collab_wrapper_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.dream_collab("messaging")
        assert result["provider"] == "dream_collab"


# ===========================================================================
# Multi-provider routing tests
# ===========================================================================

class TestRouteToBase:
    def test_route_to_best_big_tech_ai_free(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.route_to_best("chat", category=ProviderCategory.BIG_TECH_AI)
        assert result["status"] == "ok"

    def test_route_to_best_big_tech_ai_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.route_to_best("chat", category=ProviderCategory.BIG_TECH_AI)
        assert result["status"] == "ok"

    def test_route_to_best_communication_free_falls_back_to_dream(self):
        # On FREE, Slack is the only enabled COMMUNICATION provider
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.route_to_best("chat", category=ProviderCategory.COMMUNICATION)
        assert result["status"] == "ok"

    def test_route_to_best_dream_proprietary(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.route_to_best("chat", category=ProviderCategory.DREAM_PROPRIETARY)
        assert result["status"] == "ok"


# ===========================================================================
# Subscription resales tests
# ===========================================================================

class TestSubscriptionResales:
    def test_resell_subscription_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        sub = bot.resell_subscription(
            provider_id="slack",
            plan="pro",
            seats=5,
            price_per_seat_usd=8.75,
            buyer_id="buyer_001",
        )
        assert isinstance(sub, Subscription)
        assert sub.provider_id == "slack"
        assert sub.seats == 5
        assert sub.status == "active"

    def test_resell_subscription_calculates_total_price(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        sub = bot.resell_subscription(
            provider_id="slack",
            plan="pro",
            seats=10,
            price_per_seat_usd=10.0,
            buyer_id="buyer_002",
            markup_pct=20.0,
        )
        assert sub.total_price_usd == pytest.approx(120.0)

    def test_resell_subscription_requires_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        with pytest.raises(EnterpriseIntegrationsBotTierError):
            bot.resell_subscription(
                provider_id="slack",
                plan="pro",
                seats=1,
                price_per_seat_usd=8.75,
                buyer_id="buyer_free",
            )

    def test_resell_subscription_unknown_provider(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        with pytest.raises(ProviderNotFoundError):
            bot.resell_subscription(
                provider_id="no_such_provider",
                plan="pro",
                seats=1,
                price_per_seat_usd=10.0,
                buyer_id="buyer_003",
            )

    def test_resell_subscription_zero_seats_raises(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        with pytest.raises(SubscriptionError):
            bot.resell_subscription(
                provider_id="slack",
                plan="pro",
                seats=0,
                price_per_seat_usd=10.0,
                buyer_id="buyer_004",
            )

    def test_resell_subscription_negative_price_raises(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        with pytest.raises(SubscriptionError):
            bot.resell_subscription(
                provider_id="slack",
                plan="pro",
                seats=1,
                price_per_seat_usd=-5.0,
                buyer_id="buyer_005",
            )

    def test_resell_seat_limit_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        with pytest.raises(EnterpriseIntegrationsBotTierError):
            bot.resell_subscription(
                provider_id="slack",
                plan="pro",
                seats=100,
                price_per_seat_usd=10.0,
                buyer_id="buyer_006",
            )

    def test_resell_unlimited_seats_enterprise(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.ENTERPRISE)
        sub = bot.resell_subscription(
            provider_id="slack",
            plan="enterprise",
            seats=500,
            price_per_seat_usd=12.0,
            buyer_id="corp_buyer",
        )
        assert sub.seats == 500

    def test_cancel_subscription(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        sub = bot.resell_subscription(
            provider_id="slack",
            plan="pro",
            seats=2,
            price_per_seat_usd=8.0,
            buyer_id="buyer_007",
        )
        result = bot.cancel_subscription(sub.subscription_id)
        assert result["status"] == "cancelled"

    def test_cancel_unknown_subscription_raises(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        with pytest.raises(SubscriptionError):
            bot.cancel_subscription("nonexistent-id")

    def test_list_subscriptions_returns_active_only(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        sub1 = bot.resell_subscription("slack", "pro", 2, 8.0, "b1")
        sub2 = bot.resell_subscription("snowflake", "pro", 3, 15.0, "b2")
        bot.cancel_subscription(sub2.subscription_id)
        active = bot.list_subscriptions(active_only=True)
        assert len(active) == 1
        assert active[0]["subscription_id"] == sub1.subscription_id

    def test_list_subscriptions_all(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        sub1 = bot.resell_subscription("slack", "pro", 2, 8.0, "b1")
        sub2 = bot.resell_subscription("snowflake", "pro", 3, 15.0, "b2")
        bot.cancel_subscription(sub2.subscription_id)
        all_subs = bot.list_subscriptions(active_only=False)
        assert len(all_subs) == 2

    def test_get_resale_revenue(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        bot.resell_subscription("slack", "pro", 5, 10.0, "b1", markup_pct=20.0)
        bot.resell_subscription("snowflake", "pro", 3, 20.0, "b2", markup_pct=20.0)
        revenue = bot.get_resale_revenue()
        assert revenue["active_subscriptions"] == 2
        assert revenue["total_monthly_revenue_usd"] > revenue["total_monthly_cost_usd"]
        assert revenue["gross_profit_usd"] > 0

    def test_subscription_to_dict_keys(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        sub = bot.resell_subscription("slack", "pro", 1, 8.0, "b1")
        d = sub.to_dict()
        for key in ("subscription_id", "provider_id", "plan", "seats",
                    "price_per_seat_usd", "total_price_usd",
                    "buyer_id", "status", "resale_markup_pct"):
            assert key in d


# ===========================================================================
# Usage stats tests
# ===========================================================================

class TestUsageStats:
    def test_initial_stats_zero_calls(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        stats = bot.get_usage_stats()
        assert stats["total_calls"] == 0

    def test_stats_after_calls(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        bot.google_ai("chat")
        bot.enterprise_ai("nlu")
        stats = bot.get_usage_stats()
        assert stats["total_calls"] == 2

    def test_stats_provider_breakdown(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        bot.google_ai("chat")
        bot.google_ai("vision")
        bot.enterprise_ai("nlu")
        stats = bot.get_usage_stats()
        assert stats["provider_breakdown"]["google_cloud_ai"] == 2
        assert stats["provider_breakdown"]["enterprise_ai"] == 1

    def test_stats_call_limit_reported(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        stats = bot.get_usage_stats()
        assert stats["call_limit"] == 100

    def test_stats_unlimited_enterprise(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.ENTERPRISE)
        stats = bot.get_usage_stats()
        assert stats["call_limit"] is None
        assert stats["calls_remaining"] is None

    def test_quota_exceeded_raises(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        # Manually fill the call log up to the limit
        bot._call_log = [
            APICallRecord(
                call_id=str(i),
                provider_id="google_cloud_ai",
                action="chat",
                payload={},
                response={},
                user_id="user",
            )
            for i in range(100)
        ]
        with pytest.raises(EnterpriseIntegrationsBotTierError):
            bot.google_ai("chat")


# ===========================================================================
# Tier info tests
# ===========================================================================

class TestGetTierInfo:
    def test_returns_dict(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        info = bot.get_tier_info()
        assert isinstance(info, dict)

    def test_tier_matches(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        info = bot.get_tier_info()
        assert info["tier"] == "pro"


# ===========================================================================
# Chat interface tests
# ===========================================================================

class TestChatInterface:
    def test_chat_providers(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.chat("list providers")
        assert "data" in result
        assert isinstance(result["data"], list)

    def test_chat_google(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.chat("use google gemini to help me")
        assert result["data"]["provider"] == "google_cloud_ai"

    def test_chat_enterprise_ai(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.chat("call enterprise_ai enterprise_ai")
        assert result["data"]["provider"] == "enterprise_ai"

    def test_chat_azure_free_upgrade_message(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.chat("use azure ai")
        assert result["data"].get("upgrade_required") is True

    def test_chat_azure_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.chat("use azure ai")
        assert result["data"]["provider"] == "microsoft_azure_ai"

    def test_chat_nvidia_free_upgrade_message(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.chat("use nvidia nim")
        assert result["data"].get("upgrade_required") is True

    def test_chat_nvidia_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.chat("nvidia dgx inference")
        assert result["data"]["provider"] == "nvidia_ai"

    def test_chat_aws_free_upgrade_message(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.chat("use aws bedrock")
        assert result["data"].get("upgrade_required") is True

    def test_chat_aws_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.chat("aws sagemaker query")
        assert result["data"]["provider"] == "aws_ai"

    def test_chat_databricks_free_upgrade(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.chat("databricks spark query")
        assert result["data"].get("upgrade_required") is True

    def test_chat_databricks_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.chat("databricks query")
        assert result["data"]["provider"] == "databricks"

    def test_chat_snowflake_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.chat("snowflake data cloud query")
        assert result["data"]["provider"] == "snowflake"

    def test_chat_slack_free(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.chat("send message to slack")
        assert result["data"]["provider"] == "slack"

    def test_chat_teams_free_upgrade(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.chat("use microsoft teams")
        assert result["data"].get("upgrade_required") is True

    def test_chat_teams_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.chat("microsoft teams post")
        assert result["data"]["provider"] == "microsoft_teams"

    def test_chat_zoom_free_upgrade(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.chat("create zoom meeting")
        assert result["data"].get("upgrade_required") is True

    def test_chat_zoom_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.chat("zoom meeting")
        assert result["data"]["provider"] == "zoom"

    def test_chat_dreamllm(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.chat("use dreamllm to answer my question")
        assert result["data"]["provider"] == "dream_llm"

    def test_chat_subscribe_free_upgrade(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.chat("subscribe to a service")
        assert result["data"].get("upgrade_required") is True

    def test_chat_subscription_stats_pro(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.PRO)
        result = bot.chat("show subscription stats")
        assert "data" in result

    def test_chat_usage_stats(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.chat("show stats")
        assert "total_calls" in result["data"]

    def test_chat_tier_info(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.chat("show my tier features")
        assert "tier" in result["data"]

    def test_chat_default_falls_back_to_dream_llm(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.chat("some random unrecognised question")
        assert result["data"]["provider"] == "dream_llm"

    def test_chat_returns_message_string(self):
        bot = EnterpriseIntegrationsBot(tier=Tier.FREE)
        result = bot.chat("hello")
        assert isinstance(result["message"], str)
        assert len(result["message"]) > 0
