from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, Iterable, List, Optional


@dataclass
class RevenueOpportunity:
    type: str
    estimated_uplift_usd: float
    confidence: float
    action_plan: List[str]
    bot_id: Optional[str] = None


class RevenueOptimizer:
    def __init__(self, poster: Optional[Callable[[str, List[RevenueOpportunity]], None]] = None) -> None:
        self.poster = poster
        self.recommendation_log: Dict[str, List[RevenueOpportunity]] = {}
        self.last_run_at: Optional[datetime] = None

    def analyze_portfolio(self, portfolio: Iterable[dict]) -> List[RevenueOpportunity]:
        opportunities: list[RevenueOpportunity] = []
        for bot in portfolio:
            arpu = bot.get('revenue_usd', 0.0) / max(bot.get('active_users', 1), 1)
            churn = bot.get('churn_rate', 0.0)
            attach = bot.get('addon_attach_rate', 0.0)
            if arpu < bot.get('market_arpu', arpu + 1):
                opportunities.append(self._pricing_adjustment(bot, arpu))
            if churn < 0.08 and attach < 0.25:
                opportunities.append(self._upsell_sequence(bot))
            if bot.get('related_bot_count', 0) >= 2:
                opportunities.append(self._bundle_offer(bot))
        return sorted(opportunities, key=lambda item: item.estimated_uplift_usd, reverse=True)

    def run_scheduled(self, portfolio: Iterable[dict], channel: str = 'command-center') -> List[RevenueOpportunity]:
        self.last_run_at = datetime.utcnow()
        recommendations = self.analyze_portfolio(portfolio)
        self.recommendation_log[channel] = recommendations
        if self.poster:
            self.poster(channel, recommendations)
        return recommendations

    def _pricing_adjustment(self, bot: dict, arpu: float) -> RevenueOpportunity:
        target = bot.get('market_arpu', arpu)
        uplift = max(0.0, (target - arpu) * bot.get('active_users', 0) * 0.35)
        return RevenueOpportunity(
            type='pricing_adjustment',
            estimated_uplift_usd=round(uplift, 2),
            confidence=0.71,
            action_plan=[
                'Raise price for new signups by 5-8%',
                'Protect legacy customers for one renewal cycle',
                'Track conversion and refund deltas daily',
            ],
            bot_id=bot.get('bot_id'),
        )

    def _upsell_sequence(self, bot: dict) -> RevenueOpportunity:
        uplift = bot.get('active_users', 0) * max(bot.get('base_price', 0.0), 1.0) * 0.12
        return RevenueOpportunity(
            type='upsell_sequence',
            estimated_uplift_usd=round(uplift, 2),
            confidence=0.66,
            action_plan=['Offer premium analytics', 'Trigger usage-based nudges', 'Bundle annual billing discount'],
            bot_id=bot.get('bot_id'),
        )

    def _bundle_offer(self, bot: dict) -> RevenueOpportunity:
        uplift = bot.get('revenue_usd', 0.0) * 0.09
        return RevenueOpportunity(
            type='bundle_offer',
            estimated_uplift_usd=round(uplift, 2),
            confidence=0.62,
            action_plan=['Package adjacent bots', 'Apply 15% bundle incentive', 'Promote bundle in onboarding'],
            bot_id=bot.get('bot_id'),
        )
