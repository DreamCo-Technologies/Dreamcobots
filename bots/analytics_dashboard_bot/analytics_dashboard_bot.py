"""Analytics Dashboard Bot — tier-aware metric tracking and reporting."""
import sys, os
import random
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.analytics_dashboard_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


METRIC_LIMITS = {Tier.FREE: 3, Tier.PRO: 20, Tier.ENTERPRISE: None}


class AnalyticsDashboardBot:
    """Tier-aware analytics dashboard bot."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.flow = GlobalAISourcesFlow(bot_name="AnalyticsDashboardBot")
        self._metrics = []

    def track_metric(self, name: str, value: float, channel: str = "website", date=None) -> dict:
        limit = METRIC_LIMITS[self.tier]
        distinct_names = set(m["name"] for m in self._metrics)
        if limit is not None and name not in distinct_names and len(distinct_names) >= limit:
            raise PermissionError(f"Metric type limit ({limit}) reached for {self.tier.value} tier")
        entry = {"name": name, "value": value, "channel": channel, "date": date or datetime.now().isoformat()}
        self._metrics.append(entry)
        return entry

    def get_dashboard_summary(self, date_range_days: int = 30) -> dict:
        channels = list(set(m["channel"] for m in self._metrics))
        distinct_names = set(m["name"] for m in self._metrics)
        summary_by_metric = {}
        for metric_name in distinct_names:
            values = [m["value"] for m in self._metrics if m["name"] == metric_name]
            summary_by_metric[metric_name] = {
                "count": len(values),
                "total": sum(values),
                "avg": sum(values) / len(values) if values else 0,
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
            }
        return {
            "date_range_days": date_range_days,
            "total_metrics_tracked": len(self._metrics),
            "channels": channels,
            "summary_by_metric": summary_by_metric,
            "generated_at": datetime.now().isoformat(),
            "tier_used": self.tier.value,
        }

    def calculate_roi(self, ad_spend: float, revenue_generated: float) -> dict:
        profit = revenue_generated - ad_spend
        roi_percent = round((profit / ad_spend * 100) if ad_spend > 0 else 0.0, 2)
        return {
            "ad_spend": ad_spend,
            "revenue_generated": revenue_generated,
            "profit": profit,
            "roi_percent": roi_percent,
            "tier_used": self.tier.value,
        }

    def get_funnel_analysis(self, stages=None) -> dict:
        if self.tier == Tier.FREE:
            raise PermissionError("Funnel analysis requires PRO or ENTERPRISE tier")
        if stages is None:
            stages = ["awareness", "interest", "consideration", "intent", "purchase"]
        conversions = [random.randint(100, 10000)]
        for _ in range(len(stages) - 1):
            prev = conversions[-1]
            conversions.append(random.randint(int(prev * 0.3), int(prev * 0.7)))
        drop_off_rates = [
            round((conversions[i] - conversions[i + 1]) / conversions[i] * 100, 1)
            for i in range(len(conversions) - 1)
        ]
        return {
            "stages": stages,
            "conversions": conversions,
            "drop_off_rates": drop_off_rates,
            "tier_used": self.tier.value,
        }

    def generate_report(self, format: str = "text") -> str:
        lines = [
            "=== Analytics Report ===",
            f"Tier: {self.tier.value}",
            f"Total metrics: {len(self._metrics)}",
            "",
        ]
        distinct_names = set(m["name"] for m in self._metrics)
        for name in distinct_names:
            values = [m["value"] for m in self._metrics if m["name"] == name]
            count = len(values)
            avg = sum(values) / count if count else 0
            lines.append(f"Metric: {name}: count={count}, avg={avg:.2f}")
        return "\n".join(lines)

    def run(self) -> dict:
        return self.flow.run_pipeline(
            raw_data={"bot": "AnalyticsDashboardBot", "tier": self.tier.value, "metrics_count": len(self._metrics)},
            learning_method="supervised",
        )
