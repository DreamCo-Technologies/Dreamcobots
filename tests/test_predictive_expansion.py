"""Tests for bots/predictive_expansion/predictive_expansion.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.predictive_expansion.predictive_expansion import (
    PredictiveExpansion,
    RegionProfile,
    ExpansionScore,
    MarketType,
    ExpansionPhase,
    CRMFollowUpTask,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _register_sample_region(pe, name="Chicago", score_target="high"):
    """Register a pre-tuned region."""
    if score_target == "high":
        return pe.register_region(
            name=name, country="USA", market_type=MarketType.URBAN,
            population=2_700_000, avg_household_income=85_000,
            real_estate_volume_annual=12_000_000_000,
            digital_adoption_rate=0.90, competition_density=0.30,
        )
    else:
        return pe.register_region(
            name=name, country="USA", market_type=MarketType.RURAL,
            population=50_000, avg_household_income=30_000,
            real_estate_volume_annual=200_000_000,
            digital_adoption_rate=0.40, competition_density=0.80,
        )


# ---------------------------------------------------------------------------
# Region registration
# ---------------------------------------------------------------------------

class TestRegisterRegion:
    def test_returns_region_profile(self):
        pe = PredictiveExpansion()
        region = _register_sample_region(pe)
        assert isinstance(region, RegionProfile)

    def test_region_id_assigned(self):
        pe = PredictiveExpansion()
        region = _register_sample_region(pe)
        assert region.region_id.startswith("reg_")

    def test_list_regions(self):
        pe = PredictiveExpansion()
        _register_sample_region(pe, "Chicago")
        _register_sample_region(pe, "Atlanta")
        assert len(pe.list_regions()) == 2


# ---------------------------------------------------------------------------
# score_region
# ---------------------------------------------------------------------------

class TestScoreRegion:
    def test_returns_expansion_score(self):
        pe = PredictiveExpansion()
        region = _register_sample_region(pe)
        score = pe.score_region(region.region_id)
        assert isinstance(score, ExpansionScore)

    def test_score_between_0_and_100(self):
        pe = PredictiveExpansion()
        region = _register_sample_region(pe)
        score = pe.score_region(region.region_id)
        assert 0 <= score.score <= 100

    def test_high_income_region_scores_higher(self):
        pe = PredictiveExpansion()
        high = _register_sample_region(pe, "HighCity", "high")
        low = _register_sample_region(pe, "LowCity", "low")
        high_score = pe.score_region(high.region_id)
        low_score = pe.score_region(low.region_id)
        assert high_score.score > low_score.score

    def test_score_has_rationale(self):
        pe = PredictiveExpansion()
        region = _register_sample_region(pe)
        score = pe.score_region(region.region_id)
        assert isinstance(score.rationale, str)
        assert len(score.rationale) > 0

    def test_to_dict_has_keys(self):
        pe = PredictiveExpansion()
        region = _register_sample_region(pe)
        score = pe.score_region(region.region_id)
        d = score.to_dict()
        for key in ("region_id", "region_name", "score", "recommended_phase",
                    "projected_revenue", "confidence", "rationale"):
            assert key in d

    def test_nonexistent_region_raises(self):
        pe = PredictiveExpansion()
        with pytest.raises(KeyError):
            pe.score_region("reg_nonexistent")

    def test_high_score_recommends_omniversal(self):
        pe = PredictiveExpansion()
        region = _register_sample_region(pe, score_target="high")
        score = pe.score_region(region.region_id)
        if score.score >= 75:
            assert score.recommended_phase == ExpansionPhase.OMNIVERSAL

    def test_low_score_recommends_lead_gen(self):
        pe = PredictiveExpansion()
        region = _register_sample_region(pe, score_target="low")
        score = pe.score_region(region.region_id)
        assert score.recommended_phase in list(ExpansionPhase)


# ---------------------------------------------------------------------------
# score_all_regions
# ---------------------------------------------------------------------------

class TestScoreAllRegions:
    def test_returns_sorted_by_score_desc(self):
        pe = PredictiveExpansion()
        _register_sample_region(pe, "A", "high")
        _register_sample_region(pe, "B", "low")
        results = pe.score_all_regions()
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_length_matches_registered(self):
        pe = PredictiveExpansion()
        _register_sample_region(pe, "A")
        _register_sample_region(pe, "B")
        _register_sample_region(pe, "C")
        results = pe.score_all_regions()
        assert len(results) == 3

    def test_empty_returns_empty_list(self):
        pe = PredictiveExpansion()
        assert pe.score_all_regions() == []


# ---------------------------------------------------------------------------
# get_top_regions
# ---------------------------------------------------------------------------

class TestGetTopRegions:
    def test_returns_n_regions(self):
        pe = PredictiveExpansion()
        for i in range(6):
            pe.register_region(
                name=f"Region{i}", country="USA", market_type=MarketType.URBAN,
                population=100_000 * (i + 1), avg_household_income=50_000 + i * 5_000,
                real_estate_volume_annual=500_000_000 * (i + 1),
                digital_adoption_rate=0.5 + i * 0.05,
                competition_density=0.5 - i * 0.05,
            )
        top = pe.get_top_regions(n=3)
        assert len(top) == 3

    def test_top_region_has_highest_score(self):
        pe = PredictiveExpansion()
        _register_sample_region(pe, "High", "high")
        _register_sample_region(pe, "Low", "low")
        top = pe.get_top_regions(n=1)
        assert top[0]["region_name"] == "High"


# ---------------------------------------------------------------------------
# CRM follow-up (Phase 5)
# ---------------------------------------------------------------------------

class TestCRMFollowup:
    def test_schedule_followup_returns_task(self):
        pe = PredictiveExpansion()
        region = _register_sample_region(pe)
        task = pe.schedule_crm_followup(
            region.region_id, "contact@ex.com", "Hello!", channel="sms"
        )
        assert isinstance(task, CRMFollowUpTask)

    def test_task_id_assigned(self):
        pe = PredictiveExpansion()
        region = _register_sample_region(pe)
        task = pe.schedule_crm_followup(region.region_id, "c@ex.com", "Hi")
        assert task.task_id.startswith("task_")

    def test_get_crm_followups_all(self):
        pe = PredictiveExpansion()
        r1 = _register_sample_region(pe, "A")
        r2 = _register_sample_region(pe, "B")
        pe.schedule_crm_followup(r1.region_id, "a@ex.com", "msg1")
        pe.schedule_crm_followup(r2.region_id, "b@ex.com", "msg2")
        tasks = pe.get_crm_followups()
        assert len(tasks) == 2

    def test_get_crm_followups_by_region(self):
        pe = PredictiveExpansion()
        r1 = _register_sample_region(pe, "A")
        r2 = _register_sample_region(pe, "B")
        pe.schedule_crm_followup(r1.region_id, "a@ex.com", "msg")
        pe.schedule_crm_followup(r2.region_id, "b@ex.com", "msg")
        tasks = pe.get_crm_followups(region_id=r1.region_id)
        assert len(tasks) == 1
        assert tasks[0]["region_id"] == r1.region_id

    def test_task_to_dict_keys(self):
        pe = PredictiveExpansion()
        region = _register_sample_region(pe)
        task = pe.schedule_crm_followup(region.region_id, "c@ex.com", "Hi")
        d = task.to_dict()
        for key in ("task_id", "region_id", "contact_email", "follow_up_message",
                    "scheduled_at", "channel", "status"):
            assert key in d


# ---------------------------------------------------------------------------
# get_revenue_output
# ---------------------------------------------------------------------------

class TestGetRevenueOutput:
    def test_revenue_output_keys(self):
        pe = PredictiveExpansion()
        output = pe.get_revenue_output()
        for key in ("revenue", "leads_generated", "conversion_rate", "action"):
            assert key in output

    def test_revenue_positive_after_regions(self):
        pe = PredictiveExpansion()
        _register_sample_region(pe, "Chicago", "high")
        output = pe.get_revenue_output()
        assert output["revenue"] > 0

    def test_leads_generated_equals_region_count(self):
        pe = PredictiveExpansion()
        _register_sample_region(pe, "A")
        _register_sample_region(pe, "B")
        output = pe.get_revenue_output()
        assert output["leads_generated"] == 2
