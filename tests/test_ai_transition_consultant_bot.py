"""
Tests for the AI Transition Consultant Bot.

Validates:
  1. Tiers — feature flags, monthly limits, tier info
  2. AITransitionConsultantBot — assess_business, recommend_solutions,
     create_training_module, plan_workflow_integration, get_consultation_dashboard
  3. Tier gating — FREE limited to basic_assessment, ENTERPRISE gets workflow_integration
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.ai_transition_consultant_bot.tiers import (
    Tier,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    BOT_FEATURES,
    MONTHLY_LIMITS,
    DAILY_LIMITS,
    get_bot_tier_info,
    FEATURE_BASIC_ASSESSMENT,
    FEATURE_FULL_ASSESSMENT,
    FEATURE_SOLUTION_RECOMMENDATIONS,
    FEATURE_TRAINING_MODULES,
    FEATURE_WORKFLOW_INTEGRATION,
    FEATURE_DEDICATED_SUPPORT,
    FEATURE_WHITE_LABEL,
    FEATURE_COMMERCIAL_RIGHTS,
)
from bots.ai_transition_consultant_bot.ai_transition_consultant_bot import (
    AITransitionConsultantBot,
    AITransitionConsultantBotError,
)


# ===========================================================================
# Tier tests
# ===========================================================================

class TestTiers:
    def test_tier_enum_values(self):
        assert Tier.FREE.value == "free"
        assert Tier.PRO.value == "pro"
        assert Tier.ENTERPRISE.value == "enterprise"

    def test_three_tiers_exist(self):
        assert len(list_tiers()) == 3

    def test_free_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_upgrade_free_to_pro(self):
        assert get_upgrade_path(Tier.FREE).tier == Tier.PRO

    def test_upgrade_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_free_has_basic_assessment(self):
        assert FEATURE_BASIC_ASSESSMENT in BOT_FEATURES[Tier.FREE.value]

    def test_free_lacks_workflow_integration(self):
        assert FEATURE_WORKFLOW_INTEGRATION not in BOT_FEATURES[Tier.FREE.value]

    def test_pro_has_full_assessment(self):
        assert FEATURE_FULL_ASSESSMENT in BOT_FEATURES[Tier.PRO.value]

    def test_pro_has_training_modules(self):
        assert FEATURE_TRAINING_MODULES in BOT_FEATURES[Tier.PRO.value]

    def test_enterprise_has_workflow_integration(self):
        assert FEATURE_WORKFLOW_INTEGRATION in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_enterprise_has_commercial_rights(self):
        assert FEATURE_COMMERCIAL_RIGHTS in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_monthly_limit_free(self):
        assert MONTHLY_LIMITS[Tier.FREE.value] == 3

    def test_monthly_limit_pro(self):
        assert MONTHLY_LIMITS[Tier.PRO.value] == 30

    def test_monthly_limit_enterprise_unlimited(self):
        assert MONTHLY_LIMITS[Tier.ENTERPRISE.value] is None

    def test_tier_info_returns_dict(self):
        info = get_bot_tier_info(Tier.PRO)
        assert isinstance(info, dict)
        assert "features" in info


# ===========================================================================
# Instantiation
# ===========================================================================

class TestInit:
    def test_default_tier_is_free(self):
        bot = AITransitionConsultantBot()
        assert bot.tier == Tier.FREE

    def test_monthly_count_starts_zero(self):
        bot = AITransitionConsultantBot()
        assert bot._monthly_count == 0

    def test_assessments_start_empty(self):
        bot = AITransitionConsultantBot()
        assert len(bot._assessments) == 0


# ===========================================================================
# assess_business
# ===========================================================================

class TestAssessBusiness:
    def setup_method(self):
        self.bot = AITransitionConsultantBot(tier=Tier.PRO)

    def test_returns_dict(self):
        result = self.bot.assess_business({"name": "Acme", "industry": "retail"})
        assert isinstance(result, dict)

    def test_has_assessment_id(self):
        result = self.bot.assess_business({"name": "Acme"})
        assert "assessment_id" in result

    def test_has_ai_readiness_score(self):
        result = self.bot.assess_business({"name": "Acme"})
        assert "ai_readiness_score" in result
        assert 0 <= result["ai_readiness_score"] <= 100

    def test_has_maturity_level(self):
        result = self.bot.assess_business({"name": "Acme"})
        assert "maturity_level" in result

    def test_stores_assessment(self):
        result = self.bot.assess_business({"name": "Acme"})
        assert result["assessment_id"] in self.bot._assessments

    def test_increments_monthly_count(self):
        self.bot.assess_business({"name": "Acme"})
        assert self.bot._monthly_count == 1

    def test_free_can_assess(self):
        bot = AITransitionConsultantBot(tier=Tier.FREE)
        result = bot.assess_business({"name": "Small Co"})
        assert "assessment_id" in result


# ===========================================================================
# recommend_solutions
# ===========================================================================

class TestRecommendSolutions:
    def test_pro_can_recommend(self):
        bot = AITransitionConsultantBot(tier=Tier.PRO)
        assessment = bot.assess_business({"name": "TechCorp"})
        result = bot.recommend_solutions(assessment["assessment_id"])
        assert isinstance(result, dict)
        assert "recommendations" in result

    def test_has_estimated_investment(self):
        bot = AITransitionConsultantBot(tier=Tier.PRO)
        assessment = bot.assess_business({"name": "TechCorp"})
        result = bot.recommend_solutions(assessment["assessment_id"])
        assert "total_estimated_investment_usd" in result

    def test_free_cannot_recommend(self):
        bot = AITransitionConsultantBot(tier=Tier.FREE)
        with pytest.raises(AITransitionConsultantBotError):
            bot.recommend_solutions("some_id")


# ===========================================================================
# create_training_module
# ===========================================================================

class TestCreateTrainingModule:
    def test_pro_can_create_module(self):
        bot = AITransitionConsultantBot(tier=Tier.PRO)
        result = bot.create_training_module("machine learning basics", "managers")
        assert isinstance(result, dict)
        assert "module_id" in result

    def test_has_sections(self):
        bot = AITransitionConsultantBot(tier=Tier.PRO)
        result = bot.create_training_module("AI tools", "developers")
        assert "sections" in result
        assert len(result["sections"]) > 0

    def test_has_learning_objectives(self):
        bot = AITransitionConsultantBot(tier=Tier.PRO)
        result = bot.create_training_module("data analytics", "analysts")
        assert "learning_objectives" in result

    def test_free_cannot_create_training_module(self):
        bot = AITransitionConsultantBot(tier=Tier.FREE)
        with pytest.raises(AITransitionConsultantBotError):
            bot.create_training_module("AI basics", "all staff")


# ===========================================================================
# plan_workflow_integration
# ===========================================================================

class TestPlanWorkflowIntegration:
    def test_enterprise_can_plan_integration(self):
        bot = AITransitionConsultantBot(tier=Tier.ENTERPRISE)
        result = bot.plan_workflow_integration({"name": "CRM", "department": "sales"})
        assert isinstance(result, dict)
        assert "ai_touchpoints" in result

    def test_has_timeline(self):
        bot = AITransitionConsultantBot(tier=Tier.ENTERPRISE)
        result = bot.plan_workflow_integration({"name": "HR workflow"})
        assert "integration_timeline_weeks" in result

    def test_free_cannot_plan_workflow(self):
        bot = AITransitionConsultantBot(tier=Tier.FREE)
        with pytest.raises(AITransitionConsultantBotError):
            bot.plan_workflow_integration({"name": "HR"})

    def test_pro_cannot_plan_workflow(self):
        bot = AITransitionConsultantBot(tier=Tier.PRO)
        with pytest.raises(AITransitionConsultantBotError):
            bot.plan_workflow_integration({"name": "HR"})


# ===========================================================================
# get_consultation_dashboard
# ===========================================================================

class TestGetConsultationDashboard:
    def test_returns_dict(self):
        bot = AITransitionConsultantBot(tier=Tier.PRO)
        assert isinstance(bot.get_consultation_dashboard(), dict)

    def test_contains_bot_name(self):
        bot = AITransitionConsultantBot(tier=Tier.PRO)
        assert bot.get_consultation_dashboard()["bot_name"] == "AITransitionConsultantBot"

    def test_enterprise_remaining_unlimited(self):
        bot = AITransitionConsultantBot(tier=Tier.ENTERPRISE)
        assert bot.get_consultation_dashboard()["remaining"] == "unlimited"

    def test_monthly_limit_enforced(self):
        bot = AITransitionConsultantBot(tier=Tier.FREE)
        bot._monthly_count = 3
        with pytest.raises(AITransitionConsultantBotError):
            bot.assess_business({"name": "Overflow Co"})
