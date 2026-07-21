"""
Predictive Expansion AI

Analyses regional and country-level market data to score and rank
expansion opportunities.  Provides "region/country cloning" analytics
so DreamCo can replicate its most profitable bot configurations into
new markets with the highest predicted ROI.

Features
--------
  - Region profile registration (population, avg income, market size)
  - AI-driven expansion scoring algorithm
  - Top-N expansion recommendations
  - CRM gearbox integration hooks (Phase 5 priority)
  - SMS Scheduler AI follow-up layer hooks

Revenue hook output:
    {
        "revenue": projected expansion revenue,
        "leads_generated": number of markets identified,
        "conversion_rate": predicted entry success rate,
        "action": description,
    }
"""

from __future__ import annotations

import sys
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class MarketType(Enum):
    URBAN = "urban"
    SUBURBAN = "suburban"
    RURAL = "rural"
    INTERNATIONAL = "international"


class ExpansionPhase(Enum):
    LEAD_GENERATION = "phase_1_lead_gen"
    CRM_INTEGRATION = "phase_2_crm"
    MULTI_CHANNEL = "phase_3_marketing"
    BUYER_NETWORK = "phase_4_buyers"
    OMNIVERSAL = "phase_5_omniversal"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class RegionProfile:
    region_id: str
    name: str
    country: str
    market_type: MarketType
    population: int
    avg_household_income: float  # USD
    real_estate_volume_annual: float  # USD
    digital_adoption_rate: float  # 0–1
    competition_density: float  # 0–1 (1 = very competitive)
    notes: str = ""
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "region_id": self.region_id,
            "name": self.name,
            "country": self.country,
            "market_type": self.market_type.value,
            "population": self.population,
            "avg_household_income": self.avg_household_income,
            "real_estate_volume_annual": self.real_estate_volume_annual,
            "digital_adoption_rate": self.digital_adoption_rate,
            "competition_density": self.competition_density,
            "notes": self.notes,
        }


@dataclass
class ExpansionScore:
    region_id: str
    region_name: str
    score: float  # 0–100
    recommended_phase: ExpansionPhase
    projected_revenue: float
    confidence: float  # 0–1
    rationale: str
    scored_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "region_id": self.region_id,
            "region_name": self.region_name,
            "score": round(self.score, 2),
            "recommended_phase": self.recommended_phase.value,
            "projected_revenue": round(self.projected_revenue, 2),
            "confidence": round(self.confidence, 4),
            "rationale": self.rationale,
            "scored_at": self.scored_at,
        }


# ---------------------------------------------------------------------------
# CRM Gearbox (Phase 5 integration hook)
# ---------------------------------------------------------------------------


@dataclass
class CRMFollowUpTask:
    task_id: str
    region_id: str
    contact_email: str
    follow_up_message: str
    scheduled_at: str
    channel: str = "sms"  # sms | email | voice
    status: str = "scheduled"

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "region_id": self.region_id,
            "contact_email": self.contact_email,
            "follow_up_message": self.follow_up_message,
            "scheduled_at": self.scheduled_at,
            "channel": self.channel,
            "status": self.status,
        }


# ---------------------------------------------------------------------------
# PredictiveExpansion
# ---------------------------------------------------------------------------


class PredictiveExpansion:
    """
    AI-driven expansion scoring and region cloning analytics.

    Usage
    -----
    pe = PredictiveExpansion()
    pe.register_region("Atlanta", "USA", MarketType.URBAN,
                       population=500_000, avg_income=65_000,
                       re_volume=2e9, digital=0.82, competition=0.4)
    scores = pe.score_all_regions()
    top = pe.get_top_regions(n=5)
    """

    # Scoring weights
    _W_INCOME = 0.25
    _W_VOLUME = 0.30
    _W_DIGITAL = 0.20
    _W_COMPETITION = 0.15  # inverse: lower competition = higher score
    _W_POPULATION = 0.10

    # Revenue projection multiplier (USD per population unit per score point)
    _REVENUE_MULTIPLIER = 0.002

    def __init__(self) -> None:
        self._regions: Dict[str, RegionProfile] = {}
        self._scores: Dict[str, ExpansionScore] = {}
        self._crm_tasks: List[CRMFollowUpTask] = []

    # ------------------------------------------------------------------
    # Region management
    # ------------------------------------------------------------------

    def register_region(
        self,
        name: str,
        country: str,
        market_type: MarketType,
        population: int,
        avg_household_income: float,
        real_estate_volume_annual: float,
        digital_adoption_rate: float,
        competition_density: float,
        notes: str = "",
    ) -> RegionProfile:
        """Register a new region for expansion analysis."""
        region_id = f"reg_{uuid.uuid4().hex[:8]}"
        profile = RegionProfile(
            region_id=region_id,
            name=name,
            country=country,
            market_type=market_type,
            population=population,
            avg_household_income=avg_household_income,
            real_estate_volume_annual=real_estate_volume_annual,
            digital_adoption_rate=digital_adoption_rate,
            competition_density=competition_density,
            notes=notes,
        )
        self._regions[region_id] = profile
        return profile

    def list_regions(self) -> List[dict]:
        return [r.to_dict() for r in self._regions.values()]

    # ------------------------------------------------------------------
    # AI Scoring
    # ------------------------------------------------------------------

    def score_region(self, region_id: str) -> ExpansionScore:
        """
        Calculate an expansion score (0–100) for a registered region.

        The algorithm weights:
          - Average household income (higher = better)
          - Real-estate transaction volume (higher = better)
          - Digital adoption rate (higher = better)
          - Competition density (lower = better)
          - Population size (larger = better)
        """
        if region_id not in self._regions:
            raise KeyError(f"Region '{region_id}' not found.")
        region = self._regions[region_id]

        # Normalise each factor to 0–1 against reasonable benchmarks
        income_norm = min(region.avg_household_income / 150_000, 1.0)
        volume_norm = min(region.real_estate_volume_annual / 10_000_000_000, 1.0)
        digital_norm = region.digital_adoption_rate
        competition_inv = 1.0 - region.competition_density
        population_norm = min(region.population / 5_000_000, 1.0)

        raw_score = (
            income_norm * self._W_INCOME
            + volume_norm * self._W_VOLUME
            + digital_norm * self._W_DIGITAL
            + competition_inv * self._W_COMPETITION
            + population_norm * self._W_POPULATION
        )
        score = round(raw_score * 100, 2)

        # Recommend expansion phase based on score
        if score >= 75:
            phase = ExpansionPhase.OMNIVERSAL
        elif score >= 60:
            phase = ExpansionPhase.BUYER_NETWORK
        elif score >= 45:
            phase = ExpansionPhase.MULTI_CHANNEL
        elif score >= 30:
            phase = ExpansionPhase.CRM_INTEGRATION
        else:
            phase = ExpansionPhase.LEAD_GENERATION

        projected_revenue = round(region.population * score * self._REVENUE_MULTIPLIER, 2)
        confidence = min(digital_norm * 0.5 + (1 - region.competition_density) * 0.5, 1.0)

        rationale = (
            f"Score {score:.1f}/100. "
            f"Income rank: {income_norm:.0%}, "
            f"Volume rank: {volume_norm:.0%}, "
            f"Digital: {digital_norm:.0%}, "
            f"Competition: {region.competition_density:.0%} (inv={competition_inv:.0%}). "
            f"Recommended entry: {phase.value}."
        )

        expansion_score = ExpansionScore(
            region_id=region_id,
            region_name=region.name,
            score=score,
            recommended_phase=phase,
            projected_revenue=projected_revenue,
            confidence=confidence,
            rationale=rationale,
        )
        self._scores[region_id] = expansion_score
        return expansion_score

    def score_all_regions(self) -> List[dict]:
        """Score every registered region and return sorted results."""
        for region_id in self._regions:
            self.score_region(region_id)
        return sorted(
            [s.to_dict() for s in self._scores.values()],
            key=lambda s: s["score"],
            reverse=True,
        )

    def get_top_regions(self, n: int = 5) -> List[dict]:
        """Return the top-n expansion targets by score."""
        all_scores = self.score_all_regions()
        return all_scores[:n]

    # ------------------------------------------------------------------
    # Phase 5 CRM Gearbox + SMS Scheduler AI Follow-up Layer
    # ------------------------------------------------------------------

    def schedule_crm_followup(
        self,
        region_id: str,
        contact_email: str,
        message: str,
        scheduled_at: Optional[str] = None,
        channel: str = "sms",
    ) -> CRMFollowUpTask:
        """
        Schedule a CRM follow-up task for a target region.

        Integrates with the Phase 5 CRM gearbox and SMS Scheduler AI layer.
        """
        task = CRMFollowUpTask(
            task_id=f"task_{uuid.uuid4().hex[:8]}",
            region_id=region_id,
            contact_email=contact_email,
            follow_up_message=message,
            scheduled_at=scheduled_at or datetime.now(timezone.utc).isoformat(),
            channel=channel,
        )
        self._crm_tasks.append(task)
        return task

    def get_crm_followups(self, region_id: Optional[str] = None) -> List[dict]:
        """Return all scheduled CRM follow-up tasks."""
        tasks = self._crm_tasks
        if region_id:
            tasks = [t for t in tasks if t.region_id == region_id]
        return [t.to_dict() for t in tasks]

    # ------------------------------------------------------------------
    # Revenue output (standard DreamCo format)
    # ------------------------------------------------------------------

    def get_revenue_output(self) -> dict:
        if not self._scores:
            self.score_all_regions()
        total_projected = sum(s.projected_revenue for s in self._scores.values())
        avg_confidence = (
            sum(s.confidence for s in self._scores.values()) / len(self._scores)
            if self._scores
            else 0.0
        )
        return {
            "revenue": round(total_projected, 2),
            "leads_generated": len(self._regions),
            "conversion_rate": round(avg_confidence, 4),
            "action": f"Predictive expansion: {len(self._regions)} regions scored. "
                      f"Total projected revenue ${total_projected:,.2f}",
        }
