"""
Division Performance Dashboard — DreamCo

Tracks revenue, growth, API utilization, and bot performance across all DreamCo divisions.
Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
from framework import GlobalAISourcesFlow
from bots.division_performance_dashboard.tiers import Tier, get_tier_config, FEATURE_REVENUE_TRACKING, FEATURE_GROWTH_ANALYSIS, FEATURE_API_METRICS, FEATURE_BOT_INSIGHTS, FEATURE_PREDICTIVE
from bots.division_performance_dashboard.revenue_tracker import RevenueTracker
from bots.division_performance_dashboard.growth_analysis import GrowthAnalysis
from bots.division_performance_dashboard.api_metrics import APIMetrics
from bots.division_performance_dashboard.bot_insights import BotInsights


class DivisionDashboardError(Exception):
    """Base error for Division Performance Dashboard."""

class DivisionDashboardTierError(DivisionDashboardError):
    """Raised when a feature requires a higher tier."""


class DivisionPerformanceDashboard:
    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._flow = GlobalAISourcesFlow(bot_name="DivisionPerformanceDashboard")
        self._revenue = RevenueTracker()
        self._growth = GrowthAnalysis()
        self._api = APIMetrics()
        self._bots = BotInsights()

    def _require_feature(self, feature: str):
        if not self.config.has_feature(feature):
            raise DivisionDashboardTierError(
                f"Feature '{feature}' requires a higher tier. Current tier: {self.tier.value}"
            )

    def add_division_revenue(self, division_id, division_name, revenue_usd, expenses_usd, month, year) -> dict:
        self._require_feature(FEATURE_REVENUE_TRACKING)
        rec = self._revenue.record_revenue(division_id, division_name, revenue_usd, expenses_usd, month, year)
        return {
            "division_id": rec.division_id,
            "division_name": rec.division_name,
            "revenue_usd": rec.revenue_usd,
            "expenses_usd": rec.expenses_usd,
            "month": rec.month,
            "year": rec.year,
            "profit": rec.revenue_usd - rec.expenses_usd,
        }

    def get_revenue_summary(self) -> dict:
        self._require_feature(FEATURE_REVENUE_TRACKING)
        summary = self._revenue.get_summary()
        if self.config.has_feature(FEATURE_GROWTH_ANALYSIS):
            summary["revenue_by_month"] = {}
            years = {r.year for r in self._revenue._records}
            for yr in years:
                summary["revenue_by_month"][yr] = self._revenue.get_revenue_by_month(yr)
        return summary

    def analyze_growth(self, division_id, current_revenue, previous_revenue) -> dict:
        self._require_feature(FEATURE_GROWTH_ANALYSIS)
        mom = self._growth.calculate_mom_growth(current_revenue, previous_revenue)
        records = self._revenue.get_division_revenue(division_id)
        trend = self._growth.get_growth_trend([r.revenue_usd for r in records]) if records else "stable"
        result = {
            "division_id": division_id,
            "current_revenue": current_revenue,
            "previous_revenue": previous_revenue,
            "mom_growth_pct": mom,
            "trend": trend,
        }
        if self.config.has_feature(FEATURE_PREDICTIVE):
            result["projection_6m"] = self._growth.project_revenue(current_revenue, mom, 6)
        return result

    def record_api_call(self, endpoint, division_id, response_time_ms, status_code) -> dict:
        self._require_feature(FEATURE_API_METRICS)
        call = self._api.record_call(endpoint, division_id, response_time_ms, status_code)
        return {
            "endpoint": call.endpoint,
            "division_id": call.division_id,
            "response_time_ms": call.response_time_ms,
            "status_code": call.status_code,
            "timestamp": call.timestamp,
        }

    def get_api_report(self) -> dict:
        self._require_feature(FEATURE_API_METRICS)
        return self._api.get_utilization_report()

    def register_bot(self, bot_id, bot_name, division_id) -> dict:
        self._require_feature(FEATURE_BOT_INSIGHTS)
        rec = self._bots.register_bot(bot_id, bot_name, division_id)
        return {"bot_id": rec.bot_id, "bot_name": rec.bot_name, "division_id": rec.division_id}

    def update_bot_metrics(self, bot_id, tasks_completed, success_rate, revenue_generated, uptime_pct):
        self._require_feature(FEATURE_BOT_INSIGHTS)
        self._bots.update_metrics(bot_id, tasks_completed, success_rate, revenue_generated, uptime_pct)

    def get_bot_report(self) -> dict:
        self._require_feature(FEATURE_BOT_INSIGHTS)
        return self._bots.get_performance_report()

    def dashboard(self) -> str:
        lines = [
            f"=== Division Performance Dashboard ({self.config.name} Tier) ===",
            f"Revenue Summary: Total=${self._revenue.get_total_revenue():,.2f}, Profit=${self._revenue.get_profit():,.2f}",
            f"Divisions: {len(self._revenue.list_divisions())}",
        ]
        if self.config.has_feature(FEATURE_API_METRICS):
            report = self._api.get_utilization_report()
            lines.append(f"API Calls: {report['total_calls']}, Avg Response: {report['avg_response_time_ms']:.1f}ms, Error Rate: {report['error_rate']:.1f}%")
        if self.config.has_feature(FEATURE_BOT_INSIGHTS):
            bot_report = self._bots.get_performance_report()
            lines.append(f"Bots: {bot_report['total_bots']}, Avg Success: {bot_report['avg_success_rate']*100:.1f}%")
        return "\n".join(lines)

    def super_dashboard_snapshot(self) -> dict:
        """Return normalized metrics for the unified Super Dashboard."""
        api_report = self._api.get_utilization_report()
        bot_report = self._bots.get_performance_report()
        return {
            "division_count": len(self._revenue.list_divisions()),
            "total_revenue": float(self._revenue.get_total_revenue()),
            "profit": float(self._revenue.get_profit()),
            "api_calls": int(api_report.get("total_calls", 0)),
            "avg_response_ms": float(api_report.get("avg_response_time_ms", 0.0)),
            "api_error_rate": float(api_report.get("error_rate", 0.0)),
            "total_bots": int(bot_report.get("total_bots", 0)),
            "avg_bot_success_rate": float(bot_report.get("avg_success_rate", 0.0)),
        }
