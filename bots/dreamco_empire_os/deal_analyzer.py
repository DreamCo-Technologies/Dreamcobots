"""
DreamCo Empire OS — Deal Analyzer Module

Analyzes business opportunities, partnerships, and ventures.
Scores deals on ROI potential, risk level, market timing, and fit
with the DreamCo empire strategy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from framework import GlobalAISourcesFlow  # noqa: F401


class DealType(Enum):
    PARTNERSHIP = "partnership"
    ACQUISITION = "acquisition"
    LICENSING = "licensing"
    JOINT_VENTURE = "joint_venture"
    INVESTMENT = "investment"
    FRANCHISE = "franchise"
    SERVICE_CONTRACT = "service_contract"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Deal:
    """Represents a business deal or opportunity."""
    deal_id: str
    name: str
    deal_type: DealType
    upfront_cost_usd: float
    projected_monthly_revenue_usd: float
    risk_level: RiskLevel
    description: str = ""
    tags: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    score: Optional[float] = None

    @property
    def monthly_roi_pct(self) -> float:
        if self.upfront_cost_usd <= 0:
            return 0.0
        return round(self.projected_monthly_revenue_usd / self.upfront_cost_usd * 100, 1)

    @property
    def payback_months(self) -> Optional[float]:
        if self.projected_monthly_revenue_usd <= 0:
            return None
        return round(self.upfront_cost_usd / self.projected_monthly_revenue_usd, 1)


class DealAnalyzer:
    """
    Deal Analyzer — evaluate, score, and rank business opportunities.

    Scoring algorithm weights:
      - ROI potential      40 %
      - Risk level         30 %  (inverted — low risk = higher score)
      - Payback speed      20 %
      - Strategic fit      10 %
    """

    RISK_PENALTY = {
        RiskLevel.LOW: 0.0,
        RiskLevel.MEDIUM: 15.0,
        RiskLevel.HIGH: 30.0,
        RiskLevel.CRITICAL: 50.0,
    }

    def __init__(self) -> None:
        self._deals: dict[str, Deal] = {}
        self._analyzed_count: int = 0

    # ------------------------------------------------------------------
    # Deal management
    # ------------------------------------------------------------------

    def add_deal(
        self,
        deal_id: str,
        name: str,
        deal_type: DealType,
        upfront_cost_usd: float,
        projected_monthly_revenue_usd: float,
        risk_level: RiskLevel = RiskLevel.MEDIUM,
        description: str = "",
        tags: Optional[list] = None,
    ) -> Deal:
        """Register a new deal for analysis."""
        deal = Deal(
            deal_id=deal_id,
            name=name,
            deal_type=deal_type,
            upfront_cost_usd=max(0.0, upfront_cost_usd),
            projected_monthly_revenue_usd=max(0.0, projected_monthly_revenue_usd),
            risk_level=risk_level,
            description=description,
            tags=tags or [],
        )
        self._deals[deal_id] = deal
        return deal

    def analyze_deal(self, deal_id: str) -> dict:
        """Score a deal and return detailed analysis."""
        deal = self._get_deal(deal_id)
        score = self._compute_score(deal)
        deal.score = score
        self._analyzed_count += 1

        verdict = self._verdict(score)
        return {
            "deal_id": deal_id,
            "name": deal.name,
            "type": deal.deal_type.value,
            "upfront_cost_usd": deal.upfront_cost_usd,
            "projected_monthly_revenue_usd": deal.projected_monthly_revenue_usd,
            "monthly_roi_pct": deal.monthly_roi_pct,
            "payback_months": deal.payback_months,
            "risk_level": deal.risk_level.value,
            "score": score,
            "verdict": verdict,
            "recommendation": self._recommendation(score, deal),
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

    def rank_deals(self) -> list:
        """Return all deals ranked by score (highest first)."""
        results = []
        for deal in self._deals.values():
            if deal.score is None:
                self.analyze_deal(deal.deal_id)
            results.append({
                "deal_id": deal.deal_id,
                "name": deal.name,
                "score": deal.score,
                "monthly_roi_pct": deal.monthly_roi_pct,
                "risk_level": deal.risk_level.value,
                "verdict": self._verdict(deal.score),
            })
        results.sort(key=lambda d: d["score"], reverse=True)
        return results

    def get_summary(self) -> dict:
        """Return portfolio summary of all deals."""
        deals = list(self._deals.values())
        total_upfront = sum(d.upfront_cost_usd for d in deals)
        total_monthly_rev = sum(d.projected_monthly_revenue_usd for d in deals)
        return {
            "total_deals": len(deals),
            "analyzed": self._analyzed_count,
            "total_upfront_investment_usd": round(total_upfront, 2),
            "total_projected_monthly_revenue_usd": round(total_monthly_rev, 2),
            "avg_monthly_roi_pct": round(
                sum(d.monthly_roi_pct for d in deals) / len(deals), 1
            ) if deals else 0.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _compute_score(self, deal: Deal) -> float:
        roi_score = min(40.0, deal.monthly_roi_pct * 0.4)
        risk_penalty = self.RISK_PENALTY[deal.risk_level]
        risk_score = max(0.0, 30.0 - risk_penalty)
        payback = deal.payback_months or 24.0
        payback_score = max(0.0, 20.0 - min(20.0, payback))
        strategic_score = 10.0
        return round(roi_score + risk_score + payback_score + strategic_score, 1)

    @staticmethod
    def _verdict(score: float) -> str:
        if score >= 80:
            return "Strong Buy"
        if score >= 60:
            return "Good Opportunity"
        if score >= 40:
            return "Proceed with Caution"
        return "Pass"

    @staticmethod
    def _recommendation(score: float, deal: Deal) -> str:
        if score >= 80:
            return f"High-conviction deal. Move fast — {deal.name} aligns perfectly with empire growth."
        if score >= 60:
            return f"{deal.name} shows solid upside. Negotiate terms to reduce upfront cost."
        if score >= 40:
            return f"{deal.name} has potential but risk is elevated. Run a pilot before full commitment."
        return f"Skip {deal.name} for now. Capital is better deployed elsewhere."

    def _get_deal(self, deal_id: str) -> Deal:
        if deal_id not in self._deals:
            raise KeyError(f"Deal '{deal_id}' not found.")
        return self._deals[deal_id]
