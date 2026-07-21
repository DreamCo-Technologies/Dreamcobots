"""Tests for bots/analytics_dashboard_bot"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.analytics_dashboard_bot.analytics_dashboard_bot import AnalyticsDashboardBot
from bots.analytics_dashboard_bot.tiers import BOT_FEATURES, get_bot_tier_info


class TestAnalyticsDashboardBotInstantiation:
    def test_default_tier_is_free(self):
        bot = AnalyticsDashboardBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = AnalyticsDashboardBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = AnalyticsDashboardBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE


class TestTrackMetric:
    def test_track_metric_returns_dict(self):
        bot = AnalyticsDashboardBot()
        result = bot.track_metric("page_views", 1500)
        assert isinstance(result, dict)
        assert result["name"] == "page_views"
        assert result["value"] == 1500

    def test_track_metric_stores_entry(self):
        bot = AnalyticsDashboardBot()
        bot.track_metric("clicks", 300)
        assert len(bot._metrics) == 1

    def test_free_tier_metric_limit_3_types(self):
        bot = AnalyticsDashboardBot()
        bot.track_metric("page_views", 100)
        bot.track_metric("clicks", 50)
        bot.track_metric("conversions", 10)
        with pytest.raises(PermissionError):
            bot.track_metric("bounce_rate", 0.3)

    def test_same_metric_type_doesnt_count_against_limit(self):
        bot = AnalyticsDashboardBot()
        bot.track_metric("page_views", 100)
        bot.track_metric("clicks", 50)
        bot.track_metric("conversions", 10)
        result = bot.track_metric("page_views", 200)
        assert result["value"] == 200

    def test_enterprise_no_metric_limit(self):
        bot = AnalyticsDashboardBot(tier=Tier.ENTERPRISE)
        for i in range(25):
            bot.track_metric(f"metric_{i}", float(i))
        assert len(bot._metrics) == 25


class TestDashboardSummary:
    def test_get_dashboard_summary_returns_dict(self):
        bot = AnalyticsDashboardBot()
        bot.track_metric("page_views", 1000)
        result = bot.get_dashboard_summary()
        assert isinstance(result, dict)
        assert "total_metrics_tracked" in result

    def test_dashboard_summary_has_channels(self):
        bot = AnalyticsDashboardBot()
        bot.track_metric("views", 500, channel="website")
        bot.track_metric("clicks", 100, channel="email")
        result = bot.get_dashboard_summary()
        assert "website" in result["channels"]
        assert "email" in result["channels"]

    def test_summary_by_metric_averages(self):
        bot = AnalyticsDashboardBot()
        bot.track_metric("views", 100)
        bot.track_metric("views", 200)
        result = bot.get_dashboard_summary()
        assert result["summary_by_metric"]["views"]["avg"] == 150.0


class TestCalculateRoi:
    def test_calculate_roi_positive(self):
        bot = AnalyticsDashboardBot()
        result = bot.calculate_roi(1000.0, 3000.0)
        assert result["roi_percent"] == 200.0
        assert result["profit"] == 2000.0

    def test_calculate_roi_zero_spend(self):
        bot = AnalyticsDashboardBot()
        result = bot.calculate_roi(0.0, 500.0)
        assert result["roi_percent"] == 0.0


class TestFunnelAnalysis:
    def test_funnel_raises_on_free(self):
        bot = AnalyticsDashboardBot()
        with pytest.raises(PermissionError):
            bot.get_funnel_analysis()

    def test_funnel_works_on_pro(self):
        bot = AnalyticsDashboardBot(tier=Tier.PRO)
        result = bot.get_funnel_analysis()
        assert "stages" in result
        assert "conversions" in result
        assert "drop_off_rates" in result

    def test_funnel_custom_stages(self):
        bot = AnalyticsDashboardBot(tier=Tier.PRO)
        stages = ["visit", "signup", "purchase"]
        result = bot.get_funnel_analysis(stages=stages)
        assert result["stages"] == stages
        assert len(result["conversions"]) == 3


class TestGenerateReport:
    def test_generate_report_returns_string(self):
        bot = AnalyticsDashboardBot()
        result = bot.generate_report()
        assert isinstance(result, str)
        assert "Analytics Report" in result

    def test_report_contains_tier(self):
        bot = AnalyticsDashboardBot()
        result = bot.generate_report()
        assert "free" in result


class TestAnalyticsBotTiers:
    def test_bot_features_has_all_tiers(self):
        assert Tier.FREE.value in BOT_FEATURES
        assert Tier.PRO.value in BOT_FEATURES
        assert Tier.ENTERPRISE.value in BOT_FEATURES

    def test_pro_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_tier_config_price(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_run_returns_pipeline_complete(self):
        bot = AnalyticsDashboardBot()
        result = bot.run()
        assert result.get("pipeline_complete") is True
