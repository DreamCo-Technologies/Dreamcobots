import sys, os
REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, REPO_ROOT)
import pytest
from bots.division_performance_dashboard.tiers import (
    Tier, TierConfig, TIER_CATALOGUE, get_tier_config, list_tiers, get_upgrade_path,
    FEATURE_REVENUE_TRACKING, FEATURE_GROWTH_ANALYSIS, FEATURE_API_METRICS,
    FEATURE_BOT_INSIGHTS, FEATURE_PREDICTIVE, FEATURE_WHITE_LABEL, FEATURE_API_ACCESS,
    FREE_FEATURES, PRO_FEATURES, ENTERPRISE_FEATURES,
)
from bots.division_performance_dashboard.revenue_tracker import RevenueTracker, DivisionRevenue
from bots.division_performance_dashboard.growth_analysis import GrowthAnalysis
from bots.division_performance_dashboard.api_metrics import APIMetrics, APICall
from bots.division_performance_dashboard.bot_insights import BotInsights, BotRecord
from bots.division_performance_dashboard.division_performance_dashboard import (
    DivisionPerformanceDashboard, DivisionDashboardError, DivisionDashboardTierError
)


class TestTiers:
    def test_three_tiers_exist(self):
        assert len(list(Tier)) == 3

    def test_free_tier_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0

    def test_enterprise_tier_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_free_tier_name(self):
        assert get_tier_config(Tier.FREE).name == "Free"

    def test_pro_tier_name(self):
        assert get_tier_config(Tier.PRO).name == "Pro"

    def test_enterprise_tier_name(self):
        assert get_tier_config(Tier.ENTERPRISE).name == "Enterprise"

    def test_list_tiers_returns_three(self):
        assert len(list_tiers()) == 3

    def test_list_tiers_order(self):
        tiers = list_tiers()
        assert tiers[0].tier == Tier.FREE
        assert tiers[1].tier == Tier.PRO
        assert tiers[2].tier == Tier.ENTERPRISE

    def test_get_upgrade_path_free_to_pro(self):
        next_tier = get_upgrade_path(Tier.FREE)
        assert next_tier.tier == Tier.PRO

    def test_get_upgrade_path_pro_to_enterprise(self):
        next_tier = get_upgrade_path(Tier.PRO)
        assert next_tier.tier == Tier.ENTERPRISE

    def test_get_upgrade_path_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_free_has_revenue_tracking(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_REVENUE_TRACKING)

    def test_free_lacks_growth_analysis(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_GROWTH_ANALYSIS)

    def test_free_lacks_api_metrics(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_API_METRICS)

    def test_pro_has_growth_analysis(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_GROWTH_ANALYSIS)

    def test_pro_has_api_metrics(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_API_METRICS)

    def test_pro_has_bot_insights(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_BOT_INSIGHTS)

    def test_pro_lacks_predictive(self):
        assert not get_tier_config(Tier.PRO).has_feature(FEATURE_PREDICTIVE)

    def test_enterprise_has_predictive(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_PREDICTIVE)

    def test_enterprise_has_white_label(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_WHITE_LABEL)

    def test_enterprise_has_api_access(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_API_ACCESS)

    def test_tier_config_is_dataclass(self):
        cfg = get_tier_config(Tier.FREE)
        assert isinstance(cfg, TierConfig)

    def test_free_features_list(self):
        assert FEATURE_REVENUE_TRACKING in FREE_FEATURES

    def test_enterprise_features_superset(self):
        for f in PRO_FEATURES:
            assert f in ENTERPRISE_FEATURES


class TestDivisionPerformanceDashboard:
    def test_default_tier_is_free(self):
        d = DivisionPerformanceDashboard()
        assert d.tier == Tier.FREE

    def test_instantiate_free(self):
        d = DivisionPerformanceDashboard(Tier.FREE)
        assert d.tier == Tier.FREE

    def test_instantiate_pro(self):
        d = DivisionPerformanceDashboard(Tier.PRO)
        assert d.tier == Tier.PRO

    def test_instantiate_enterprise(self):
        d = DivisionPerformanceDashboard(Tier.ENTERPRISE)
        assert d.tier == Tier.ENTERPRISE

    def test_add_revenue_free_tier(self):
        d = DivisionPerformanceDashboard(Tier.FREE)
        r = d.add_division_revenue("div1", "Division 1", 10000.0, 4000.0, "January", 2024)
        assert r["division_id"] == "div1"

    def test_add_revenue_pro_tier(self):
        d = DivisionPerformanceDashboard(Tier.PRO)
        r = d.add_division_revenue("div1", "Division 1", 10000.0, 4000.0, "January", 2024)
        assert r["revenue_usd"] == 10000.0

    def test_add_revenue_enterprise_tier(self):
        d = DivisionPerformanceDashboard(Tier.ENTERPRISE)
        r = d.add_division_revenue("div1", "Division 1", 10000.0, 4000.0, "January", 2024)
        assert r["expenses_usd"] == 4000.0

    def test_add_revenue_returns_profit(self):
        d = DivisionPerformanceDashboard(Tier.FREE)
        r = d.add_division_revenue("div1", "Division 1", 10000.0, 4000.0, "January", 2024)
        assert r["profit"] == 6000.0

    def test_get_revenue_summary_free(self):
        d = DivisionPerformanceDashboard(Tier.FREE)
        d.add_division_revenue("div1", "D1", 5000.0, 2000.0, "Jan", 2024)
        s = d.get_revenue_summary()
        assert "total_revenue" in s

    def test_analyze_growth_raises_on_free(self):
        d = DivisionPerformanceDashboard(Tier.FREE)
        with pytest.raises(DivisionDashboardTierError):
            d.analyze_growth("div1", 10000.0, 8000.0)

    def test_analyze_growth_works_pro(self):
        d = DivisionPerformanceDashboard(Tier.PRO)
        r = d.analyze_growth("div1", 12000.0, 10000.0)
        assert r["mom_growth_pct"] == 20.0

    def test_analyze_growth_enterprise_has_projection(self):
        d = DivisionPerformanceDashboard(Tier.ENTERPRISE)
        r = d.analyze_growth("div1", 12000.0, 10000.0)
        assert "projection_6m" in r
        assert len(r["projection_6m"]) == 6

    def test_record_api_call_raises_on_free(self):
        d = DivisionPerformanceDashboard(Tier.FREE)
        with pytest.raises(DivisionDashboardTierError):
            d.record_api_call("/api/v1/test", "div1", 120.0, 200)

    def test_record_api_call_works_pro(self):
        d = DivisionPerformanceDashboard(Tier.PRO)
        r = d.record_api_call("/api/v1/test", "div1", 120.0, 200)
        assert r["status_code"] == 200

    def test_get_api_report_raises_on_free(self):
        d = DivisionPerformanceDashboard(Tier.FREE)
        with pytest.raises(DivisionDashboardTierError):
            d.get_api_report()

    def test_get_api_report_works_pro(self):
        d = DivisionPerformanceDashboard(Tier.PRO)
        d.record_api_call("/api/test", "div1", 100.0, 200)
        r = d.get_api_report()
        assert "total_calls" in r

    def test_register_bot_raises_on_free(self):
        d = DivisionPerformanceDashboard(Tier.FREE)
        with pytest.raises(DivisionDashboardTierError):
            d.register_bot("bot1", "Bot One", "div1")

    def test_register_bot_works_pro(self):
        d = DivisionPerformanceDashboard(Tier.PRO)
        r = d.register_bot("bot1", "Bot One", "div1")
        assert r["bot_id"] == "bot1"

    def test_update_bot_metrics_raises_on_free(self):
        d = DivisionPerformanceDashboard(Tier.FREE)
        with pytest.raises(DivisionDashboardTierError):
            d.update_bot_metrics("bot1", 100, 0.95, 5000.0, 99.9)

    def test_update_bot_metrics_works_pro(self):
        d = DivisionPerformanceDashboard(Tier.PRO)
        d.register_bot("bot1", "Bot One", "div1")
        d.update_bot_metrics("bot1", 100, 0.95, 5000.0, 99.9)
        bot = d._bots.get_bot("bot1")
        assert bot.tasks_completed == 100

    def test_get_bot_report_raises_on_free(self):
        d = DivisionPerformanceDashboard(Tier.FREE)
        with pytest.raises(DivisionDashboardTierError):
            d.get_bot_report()

    def test_get_bot_report_works_pro(self):
        d = DivisionPerformanceDashboard(Tier.PRO)
        r = d.get_bot_report()
        assert "total_bots" in r

    def test_dashboard_returns_string_free(self):
        d = DivisionPerformanceDashboard(Tier.FREE)
        assert isinstance(d.dashboard(), str)

    def test_dashboard_returns_string_pro(self):
        d = DivisionPerformanceDashboard(Tier.PRO)
        assert isinstance(d.dashboard(), str)

    def test_dashboard_returns_string_enterprise(self):
        d = DivisionPerformanceDashboard(Tier.ENTERPRISE)
        assert isinstance(d.dashboard(), str)

    def test_dashboard_contains_tier_name(self):
        d = DivisionPerformanceDashboard(Tier.PRO)
        assert "Pro" in d.dashboard()


class TestRevenueTracker:
    def setup_method(self):
        self.tracker = RevenueTracker()

    def test_record_revenue_returns_dataclass(self):
        r = self.tracker.record_revenue("div1", "D1", 5000.0, 2000.0, "Jan", 2024)
        assert isinstance(r, DivisionRevenue)

    def test_record_revenue_stores_record(self):
        self.tracker.record_revenue("div1", "D1", 5000.0, 2000.0, "Jan", 2024)
        assert len(self.tracker._records) == 1

    def test_get_total_revenue_all(self):
        self.tracker.record_revenue("div1", "D1", 5000.0, 1000.0, "Jan", 2024)
        self.tracker.record_revenue("div2", "D2", 3000.0, 1000.0, "Feb", 2024)
        assert self.tracker.get_total_revenue() == 8000.0

    def test_get_total_revenue_by_year(self):
        self.tracker.record_revenue("div1", "D1", 5000.0, 1000.0, "Jan", 2024)
        self.tracker.record_revenue("div1", "D1", 3000.0, 1000.0, "Jan", 2023)
        assert self.tracker.get_total_revenue(year=2024) == 5000.0

    def test_get_division_revenue(self):
        self.tracker.record_revenue("div1", "D1", 5000.0, 1000.0, "Jan", 2024)
        self.tracker.record_revenue("div2", "D2", 3000.0, 1000.0, "Jan", 2024)
        records = self.tracker.get_division_revenue("div1")
        assert len(records) == 1
        assert records[0].division_id == "div1"

    def test_get_profit_overall(self):
        self.tracker.record_revenue("div1", "D1", 5000.0, 2000.0, "Jan", 2024)
        self.tracker.record_revenue("div2", "D2", 3000.0, 1000.0, "Feb", 2024)
        assert self.tracker.get_profit() == 5000.0

    def test_get_profit_by_division(self):
        self.tracker.record_revenue("div1", "D1", 5000.0, 2000.0, "Jan", 2024)
        self.tracker.record_revenue("div2", "D2", 3000.0, 1000.0, "Feb", 2024)
        assert self.tracker.get_profit("div1") == 3000.0

    def test_get_top_divisions(self):
        self.tracker.record_revenue("div1", "D1", 5000.0, 2000.0, "Jan", 2024)
        self.tracker.record_revenue("div2", "D2", 3000.0, 1000.0, "Feb", 2024)
        top = self.tracker.get_top_divisions(2)
        assert top[0][0] == "div1"

    def test_get_revenue_by_month(self):
        self.tracker.record_revenue("div1", "D1", 5000.0, 1000.0, "January", 2024)
        self.tracker.record_revenue("div1", "D1", 3000.0, 1000.0, "February", 2024)
        monthly = self.tracker.get_revenue_by_month(2024)
        assert monthly["January"] == 5000.0

    def test_list_divisions(self):
        self.tracker.record_revenue("div1", "D1", 5000.0, 1000.0, "Jan", 2024)
        self.tracker.record_revenue("div2", "D2", 3000.0, 1000.0, "Jan", 2024)
        divs = self.tracker.list_divisions()
        assert len(divs) == 2

    def test_get_summary_keys(self):
        self.tracker.record_revenue("div1", "D1", 5000.0, 2000.0, "Jan", 2024)
        s = self.tracker.get_summary()
        assert all(k in s for k in ["total_revenue", "total_profit", "divisions", "records", "top_divisions"])

    def test_empty_total_revenue(self):
        assert self.tracker.get_total_revenue() == 0.0

    def test_empty_profit(self):
        assert self.tracker.get_profit() == 0.0


class TestGrowthAnalysis:
    def setup_method(self):
        self.ga = GrowthAnalysis()

    def test_mom_growth_positive(self):
        assert self.ga.calculate_mom_growth(12000.0, 10000.0) == pytest.approx(20.0)

    def test_mom_growth_negative(self):
        assert self.ga.calculate_mom_growth(8000.0, 10000.0) == pytest.approx(-20.0)

    def test_mom_growth_zero_previous(self):
        assert self.ga.calculate_mom_growth(1000.0, 0.0) == 0.0

    def test_yoy_growth_positive(self):
        assert self.ga.calculate_yoy_growth(120000.0, 100000.0) == pytest.approx(20.0)

    def test_yoy_growth_zero_previous(self):
        assert self.ga.calculate_yoy_growth(100.0, 0.0) == 0.0

    def test_cagr_basic(self):
        result = self.ga.calculate_cagr(1000.0, 1610.51, 5)
        assert result == pytest.approx(10.0, abs=0.1)

    def test_cagr_zero_initial(self):
        assert self.ga.calculate_cagr(0.0, 1000.0, 5) == 0.0

    def test_cagr_zero_years(self):
        assert self.ga.calculate_cagr(1000.0, 2000.0, 0) == 0.0

    def test_trend_growing(self):
        values = [100, 110, 120, 130, 140]
        assert self.ga.get_growth_trend(values) == "growing"

    def test_trend_declining(self):
        values = [140, 130, 120, 110, 100]
        assert self.ga.get_growth_trend(values) == "declining"

    def test_trend_stable(self):
        values = [100, 105, 100, 105, 100]
        assert self.ga.get_growth_trend(values) == "stable"

    def test_trend_single_value(self):
        assert self.ga.get_growth_trend([100]) == "stable"

    def test_project_revenue(self):
        proj = self.ga.project_revenue(10000.0, 10.0, 3)
        assert len(proj) == 3
        assert proj[0] == pytest.approx(11000.0)

    def test_benchmark_outperforming(self):
        r = self.ga.benchmark_growth("div1", 10.0, 15.0)
        assert r["status"] == "outperforming"

    def test_benchmark_underperforming(self):
        r = self.ga.benchmark_growth("div1", 10.0, 5.0)
        assert r["status"] == "underperforming"

    def test_benchmark_at_benchmark(self):
        r = self.ga.benchmark_growth("div1", 10.0, 10.0)
        assert r["status"] == "at_benchmark"

    def test_analyze_division_insufficient_data(self):
        r = self.ga.analyze_division("div1", [])
        assert r["mom_growth"] == 0.0

    def test_analyze_division_with_data(self):
        class Rev:
            def __init__(self, v):
                self.revenue_usd = v
        data = [Rev(1000), Rev(1100), Rev(1200)]
        r = self.ga.analyze_division("div1", data)
        assert r["division_id"] == "div1"


class TestAPIMetrics:
    def setup_method(self):
        self.metrics = APIMetrics()

    def test_record_call_returns_apicall(self):
        call = self.metrics.record_call("/api/test", "div1", 100.0, 200)
        assert isinstance(call, APICall)

    def test_record_call_stores(self):
        self.metrics.record_call("/api/test", "div1", 100.0, 200)
        assert len(self.metrics._calls) == 1

    def test_avg_response_time(self):
        self.metrics.record_call("/api/a", "div1", 100.0, 200)
        self.metrics.record_call("/api/b", "div1", 200.0, 200)
        assert self.metrics.get_avg_response_time() == pytest.approx(150.0)

    def test_avg_response_time_by_endpoint(self):
        self.metrics.record_call("/api/a", "div1", 100.0, 200)
        self.metrics.record_call("/api/b", "div1", 200.0, 200)
        assert self.metrics.get_avg_response_time("/api/a") == 100.0

    def test_avg_response_time_empty(self):
        assert self.metrics.get_avg_response_time() == 0.0

    def test_error_rate(self):
        self.metrics.record_call("/api/test", "div1", 100.0, 200)
        self.metrics.record_call("/api/test", "div1", 100.0, 500)
        assert self.metrics.get_error_rate() == pytest.approx(50.0)

    def test_error_rate_empty(self):
        assert self.metrics.get_error_rate() == 0.0

    def test_top_endpoints(self):
        for _ in range(3):
            self.metrics.record_call("/api/a", "div1", 100.0, 200)
        for _ in range(2):
            self.metrics.record_call("/api/b", "div1", 100.0, 200)
        top = self.metrics.get_top_endpoints(2)
        assert top[0][0] == "/api/a"

    def test_division_api_usage(self):
        self.metrics.record_call("/api/test", "div1", 100.0, 200)
        r = self.metrics.get_division_api_usage("div1")
        assert r["total_calls"] == 1

    def test_division_api_usage_empty(self):
        r = self.metrics.get_division_api_usage("unknown")
        assert r["total_calls"] == 0

    def test_utilization_report_keys(self):
        r = self.metrics.get_utilization_report()
        assert all(k in r for k in ["total_calls", "avg_response_time_ms", "error_rate", "top_endpoints", "sla_compliance"])

    def test_sla_compliance_all_within(self):
        self.metrics.record_call("/api/test", "div1", 100.0, 200)
        assert self.metrics.get_sla_compliance(500.0) == 100.0

    def test_sla_compliance_none_within(self):
        self.metrics.record_call("/api/test", "div1", 1000.0, 200)
        assert self.metrics.get_sla_compliance(500.0) == 0.0

    def test_sla_compliance_empty(self):
        assert self.metrics.get_sla_compliance() == 100.0


class TestBotInsights:
    def setup_method(self):
        self.bi = BotInsights()

    def test_register_bot(self):
        rec = self.bi.register_bot("bot1", "Bot One", "div1")
        assert isinstance(rec, BotRecord)

    def test_register_bot_stored(self):
        self.bi.register_bot("bot1", "Bot One", "div1")
        assert "bot1" in self.bi._bots

    def test_update_metrics(self):
        self.bi.register_bot("bot1", "Bot One", "div1")
        self.bi.update_metrics("bot1", 100, 0.95, 5000.0, 99.9)
        bot = self.bi.get_bot("bot1")
        assert bot.tasks_completed == 100
        assert bot.success_rate == 0.95

    def test_update_metrics_unknown_bot(self):
        with pytest.raises(KeyError):
            self.bi.update_metrics("unknown", 100, 0.95, 5000.0, 99.9)

    def test_get_bot(self):
        self.bi.register_bot("bot1", "Bot One", "div1")
        bot = self.bi.get_bot("bot1")
        assert bot.bot_id == "bot1"

    def test_get_bot_unknown(self):
        with pytest.raises(KeyError):
            self.bi.get_bot("unknown")

    def test_get_top_bots(self):
        self.bi.register_bot("bot1", "Bot One", "div1")
        self.bi.register_bot("bot2", "Bot Two", "div1")
        self.bi.update_metrics("bot1", 100, 0.9, 5000.0, 99.0)
        self.bi.update_metrics("bot2", 50, 0.8, 2000.0, 98.0)
        top = self.bi.get_top_bots(2)
        assert top[0].bot_id == "bot1"

    def test_get_division_bots(self):
        self.bi.register_bot("bot1", "Bot One", "div1")
        self.bi.register_bot("bot2", "Bot Two", "div2")
        bots = self.bi.get_division_bots("div1")
        assert len(bots) == 1

    def test_performance_report_empty(self):
        r = self.bi.get_performance_report()
        assert r["total_bots"] == 0

    def test_performance_report_with_bots(self):
        self.bi.register_bot("bot1", "Bot One", "div1")
        self.bi.update_metrics("bot1", 100, 0.9, 5000.0, 99.0)
        r = self.bi.get_performance_report()
        assert r["total_bots"] == 1
        assert r["total_revenue"] == 5000.0

    def test_underperforming_bots(self):
        self.bi.register_bot("bot1", "Bot One", "div1")
        self.bi.update_metrics("bot1", 100, 0.5, 5000.0, 99.0)
        under = self.bi.get_underperforming_bots(0.7)
        assert len(under) == 1

    def test_no_underperforming_bots(self):
        self.bi.register_bot("bot1", "Bot One", "div1")
        self.bi.update_metrics("bot1", 100, 0.9, 5000.0, 99.0)
        under = self.bi.get_underperforming_bots(0.7)
        assert len(under) == 0


class TestExceptionHierarchy:
    def test_tier_error_is_subclass_of_base(self):
        assert issubclass(DivisionDashboardTierError, DivisionDashboardError)

    def test_tier_error_is_exception(self):
        assert issubclass(DivisionDashboardTierError, Exception)

    def test_base_error_is_exception(self):
        assert issubclass(DivisionDashboardError, Exception)

    def test_raise_tier_error_caught_as_base(self):
        with pytest.raises(DivisionDashboardError):
            raise DivisionDashboardTierError("test")
