"""Tests for the fully-implemented Government Contract & Grant Bot."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _import_bot():
    bot_dir = os.path.join(os.path.dirname(__file__), "..", "bots", "government-contract-grant-bot")
    sys.path.insert(0, bot_dir)
    import importlib
    mod = importlib.import_module("government_contract_grant_bot")
    return mod


@pytest.fixture
def bot_module():
    return _import_bot()


@pytest.fixture
def free_bot(bot_module):
    return bot_module.GovernmentContractGrantBot(tier=bot_module.Tier.FREE)


@pytest.fixture
def pro_bot(bot_module):
    return bot_module.GovernmentContractGrantBot(tier=bot_module.Tier.PRO)


@pytest.fixture
def enterprise_bot(bot_module):
    return bot_module.GovernmentContractGrantBot(tier=bot_module.Tier.ENTERPRISE)


class TestTierConfig:
    def test_tier_enum_values(self, bot_module):
        assert bot_module.Tier.FREE.value == "free"
        assert bot_module.Tier.PRO.value == "pro"
        assert bot_module.Tier.ENTERPRISE.value == "enterprise"

    def test_tier_limits_defined(self, bot_module):
        for tier in bot_module.Tier:
            assert tier in bot_module.TIER_LIMITS

    def test_free_tier_result_limit(self, bot_module):
        assert bot_module.TIER_LIMITS[bot_module.Tier.FREE]["results_per_search"] == 5

    def test_enterprise_tier_no_limit(self, bot_module):
        assert bot_module.TIER_LIMITS[bot_module.Tier.ENTERPRISE]["results_per_search"] is None

    def test_tier_prices_defined(self, bot_module):
        assert bot_module.TIER_PRICES[bot_module.Tier.FREE] == 0
        assert bot_module.TIER_PRICES[bot_module.Tier.PRO] == 99
        assert bot_module.TIER_PRICES[bot_module.Tier.ENTERPRISE] == 299


class TestBotInit:
    def test_init_default_tier(self, bot_module):
        bot = bot_module.GovernmentContractGrantBot()
        assert bot.tier == bot_module.Tier.FREE

    def test_init_pro_tier(self, pro_bot, bot_module):
        assert pro_bot.tier == bot_module.Tier.PRO

    def test_init_enterprise_tier(self, enterprise_bot, bot_module):
        assert enterprise_bot.tier == bot_module.Tier.ENTERPRISE

    def test_flow_initialized(self, free_bot):
        assert free_bot.flow is not None

    def test_features_assigned(self, pro_bot, bot_module):
        assert "full_contract_search" in pro_bot.features
        assert "grant_search" in pro_bot.features


class TestSearchOpportunities:
    def test_search_returns_list(self, pro_bot):
        results = pro_bot.search_opportunities()
        assert isinstance(results, list)

    def test_free_tier_result_cap(self, free_bot):
        results = free_bot.search_opportunities()
        assert len(results) <= 5

    def test_enterprise_no_cap(self, enterprise_bot):
        results = enterprise_bot.search_opportunities()
        assert len(results) > 5

    def test_keyword_filter(self, pro_bot):
        results = pro_bot.search_opportunities(keyword="technology")
        for r in results:
            text = (r["title"] + r["description"]).lower()
            assert "technology" in text

    def test_naics_filter(self, pro_bot):
        results = pro_bot.search_opportunities(naics="541")
        for r in results:
            assert r["naics"].startswith("541")

    def test_agency_filter(self, pro_bot):
        results = pro_bot.search_opportunities(agency="Defense")
        for r in results:
            assert "defense" in r["agency"].lower()

    def test_set_aside_filter(self, pro_bot):
        results = pro_bot.search_opportunities(set_aside="Small Business")
        for r in results:
            assert "small business" in r["set_aside"].lower()

    def test_type_filter_contracts(self, pro_bot):
        results = pro_bot.search_opportunities(opportunity_type="contract")
        for r in results:
            assert r["type"] == "contract"

    def test_type_filter_grants(self, pro_bot):
        results = pro_bot.search_opportunities(opportunity_type="grant")
        for r in results:
            assert r["type"] == "grant"

    def test_min_value_filter(self, enterprise_bot):
        min_val = 5_000_000
        results = enterprise_bot.search_opportunities(min_value=min_val)
        for r in results:
            assert r["value"] >= min_val

    def test_max_value_filter(self, enterprise_bot):
        max_val = 1_000_000
        results = enterprise_bot.search_opportunities(max_value=max_val)
        for r in results:
            assert r["value"] <= max_val

    def test_no_results_for_bad_keyword(self, pro_bot):
        results = pro_bot.search_opportunities(keyword="xyzzy_does_not_exist_99999")
        assert results == []


class TestSearchContracts:
    def test_search_contracts_returns_only_contracts(self, pro_bot):
        results = pro_bot.search_contracts()
        for r in results:
            assert r["type"] == "contract"

    def test_search_contracts_keyword(self, pro_bot):
        results = pro_bot.search_contracts(keyword="cyber")
        assert isinstance(results, list)


class TestSearchGrants:
    def test_free_tier_grants_raises(self, free_bot, bot_module):
        with pytest.raises(bot_module.GovernmentContractGrantBotTierError):
            free_bot.search_grants()

    def test_pro_tier_grants_succeed(self, pro_bot):
        results = pro_bot.search_grants()
        for r in results:
            assert r["type"] == "grant"

    def test_enterprise_grants_keyword(self, enterprise_bot):
        results = enterprise_bot.search_grants(keyword="research")
        assert isinstance(results, list)


class TestUpcomingDeadlines:
    def test_returns_list(self, pro_bot):
        results = pro_bot.get_upcoming_deadlines(days=3650)
        assert isinstance(results, list)

    def test_days_remaining_field(self, pro_bot):
        results = pro_bot.get_upcoming_deadlines(days=3650)
        for r in results:
            assert "days_remaining" in r
            assert r["days_remaining"] >= 0

    def test_sorted_by_days_remaining(self, pro_bot):
        results = pro_bot.get_upcoming_deadlines(days=3650)
        for i in range(len(results) - 1):
            assert results[i]["days_remaining"] <= results[i + 1]["days_remaining"]

    def test_free_tier_cap(self, free_bot):
        results = free_bot.get_upcoming_deadlines(days=3650)
        assert len(results) <= 5


class TestAnalyzeOpportunity:
    def test_requires_pro(self, free_bot, bot_module):
        with pytest.raises(bot_module.GovernmentContractGrantBotTierError):
            free_bot.analyze_opportunity("W912DY-24-R-0001")

    def test_pro_returns_analysis(self, pro_bot):
        result = pro_bot.analyze_opportunity("W912DY-24-R-0001")
        assert "analysis" in result
        assert "opportunity" in result

    def test_win_probability_range(self, pro_bot):
        result = pro_bot.analyze_opportunity("W912DY-24-R-0001")
        wp = result["analysis"]["win_probability_pct"]
        assert 0 <= wp <= 100

    def test_recommended_action(self, pro_bot):
        result = pro_bot.analyze_opportunity("W912DY-24-R-0001")
        assert result["analysis"]["recommended_action"] in ("bid", "monitor", "skip")

    def test_not_found_returns_error(self, pro_bot):
        result = pro_bot.analyze_opportunity("NONEXISTENT-ID")
        assert "error" in result

    def test_enterprise_includes_requirements(self, enterprise_bot):
        result = enterprise_bot.analyze_opportunity("W912DY-24-R-0001")
        assert isinstance(result["analysis"]["key_requirements"], list)


class TestSavedSearches:
    def test_save_search_pro(self, pro_bot):
        result = pro_bot.save_search("My Tech Search", {"keyword": "technology"})
        assert result["saved"] is True

    def test_save_search_free_tier_limit(self, free_bot, bot_module):
        free_bot.save_search("Search 1", {})
        free_bot.save_search("Search 2", {})
        with pytest.raises(bot_module.GovernmentContractGrantBotTierError):
            free_bot.save_search("Search 3", {})


class TestAlerts:
    def test_add_alert_requires_pro(self, free_bot, bot_module):
        with pytest.raises(bot_module.GovernmentContractGrantBotTierError):
            free_bot.add_alert_keyword("cybersecurity")

    def test_add_alert_pro(self, pro_bot):
        result = pro_bot.add_alert_keyword("technology")
        assert result["added"] is True
        assert result["keyword"] == "technology"
        assert result["total_alerts"] == 1

    def test_alert_limit_pro(self, pro_bot, bot_module):
        limit = bot_module.TIER_LIMITS[bot_module.Tier.PRO]["alert_keywords"]
        for i in range(limit):
            pro_bot.add_alert_keyword(f"keyword_{i}")
        with pytest.raises(bot_module.GovernmentContractGrantBotTierError):
            pro_bot.add_alert_keyword("overflow")


class TestSummary:
    def test_get_summary_keys(self, pro_bot):
        summary = pro_bot.get_summary()
        assert "total_opportunities" in summary
        assert "contracts" in summary
        assert "grants" in summary
        assert "total_value_usd" in summary
        assert "small_business_set_asides" in summary

    def test_summary_counts_positive(self, pro_bot):
        summary = pro_bot.get_summary()
        assert summary["total_opportunities"] > 0
        assert summary["contracts"] > 0
        assert summary["grants"] > 0

    def test_summary_total_equals_contracts_plus_grants(self, pro_bot):
        summary = pro_bot.get_summary()
        assert summary["total_opportunities"] == summary["contracts"] + summary["grants"]

    def test_get_tier_info(self, pro_bot):
        info = pro_bot.get_tier_info()
        assert info["tier"] == "pro"
        assert info["price_monthly"] == 99
        assert isinstance(info["features"], list)


class TestPipelineRun:
    def test_run_returns_dict(self, pro_bot):
        result = pro_bot.run()
        assert isinstance(result, dict)

    def test_run_pipeline_complete(self, pro_bot):
        result = pro_bot.run()
        assert result.get("pipeline_complete") is True
