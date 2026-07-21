import sys, os
REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, REPO_ROOT)

TOOL_DIR = os.path.join(REPO_ROOT, 'analytics-elites', 'predictive_engagement_tool')
sys.path.insert(0, TOOL_DIR)

import pytest
from predictive_engagement_tool import PredictiveEngagementTool

CHAMPION_CUSTOMER = {
    "customer_id": "c001",
    "recency_days": 2,
    "frequency_30d": 10,
    "avg_session_minutes": 20,
    "email_open_rate": 0.9,
    "support_tickets_90d": 0,
}

DORMANT_CUSTOMER = {
    "customer_id": "c002",
    "recency_days": 180,
    "frequency_30d": 0,
    "avg_session_minutes": 0,
    "email_open_rate": 0.0,
    "support_tickets_90d": 5,
}


class TestPredictiveEngagementToolInstantiation:
    def test_default_tier_is_free(self):
        tool = PredictiveEngagementTool()
        assert tool.tier == "free"

    def test_pro_tier(self):
        tool = PredictiveEngagementTool(tier="pro")
        assert tool.tier == "pro"


class TestScoreEngagement:
    def test_returns_dict(self):
        tool = PredictiveEngagementTool()
        result = tool.score_engagement(CHAMPION_CUSTOMER)
        assert isinstance(result, dict)

    def test_high_engagement_score(self):
        tool = PredictiveEngagementTool()
        result = tool.score_engagement(CHAMPION_CUSTOMER)
        assert result["engagement_score"] > 60

    def test_low_engagement_score(self):
        tool = PredictiveEngagementTool()
        result = tool.score_engagement(DORMANT_CUSTOMER)
        assert result["engagement_score"] < 40

    def test_segment_present(self):
        tool = PredictiveEngagementTool()
        result = tool.score_engagement(CHAMPION_CUSTOMER)
        assert result["segment"] in PredictiveEngagementTool.SEGMENT_THRESHOLDS

    def test_customer_id_preserved(self):
        tool = PredictiveEngagementTool()
        result = tool.score_engagement(CHAMPION_CUSTOMER)
        assert result["customer_id"] == "c001"


class TestPredictChurn:
    def test_free_tier_raises_permission(self):
        tool = PredictiveEngagementTool(tier="free")
        with pytest.raises(PermissionError):
            tool.predict_churn(DORMANT_CUSTOMER)

    def test_dormant_high_churn(self):
        tool = PredictiveEngagementTool(tier="pro")
        result = tool.predict_churn(DORMANT_CUSTOMER)
        assert result["risk_level"] in ("high", "medium")

    def test_champion_low_churn(self):
        tool = PredictiveEngagementTool(tier="pro")
        result = tool.predict_churn(CHAMPION_CUSTOMER)
        assert result["risk_level"] == "low"

    def test_churn_prob_between_0_1(self):
        tool = PredictiveEngagementTool(tier="pro")
        result = tool.predict_churn(DORMANT_CUSTOMER)
        assert 0 <= result["churn_probability"] <= 1

    def test_recommended_action_present(self):
        tool = PredictiveEngagementTool(tier="pro")
        result = tool.predict_churn(DORMANT_CUSTOMER)
        assert len(result["recommended_action"]) > 0


class TestBatchScore:
    def test_returns_list(self):
        tool = PredictiveEngagementTool()
        results = tool.batch_score([CHAMPION_CUSTOMER, DORMANT_CUSTOMER])
        assert len(results) == 2

    def test_all_results_have_score(self):
        tool = PredictiveEngagementTool()
        results = tool.batch_score([CHAMPION_CUSTOMER, DORMANT_CUSTOMER])
        for r in results:
            assert "engagement_score" in r
