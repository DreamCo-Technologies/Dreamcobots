"""Tests for bots/lead_generator_bot/lead_generator_bot.py"""
import sys, os
REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.lead_generator_bot.lead_generator_bot import LeadGeneratorBot


class TestLeadGeneratorBotInstantiation:
    def test_default_tier_is_free(self):
        bot = LeadGeneratorBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = LeadGeneratorBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = LeadGeneratorBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = LeadGeneratorBot()
        assert bot.config is not None

    def test_flow_initialized(self):
        bot = LeadGeneratorBot()
        assert bot.flow is not None


class TestSearchLeads:
    def test_returns_list(self):
        bot = LeadGeneratorBot(tier=Tier.PRO)
        result = bot.search_leads("tech")
        assert isinstance(result, list)

    def test_filters_by_industry(self):
        bot = LeadGeneratorBot(tier=Tier.PRO)
        result = bot.search_leads("finance")
        for lead in result:
            assert "finance" in lead["industry"].lower()

    def test_free_tier_limit(self):
        bot = LeadGeneratorBot(tier=Tier.FREE)
        result = bot.search_leads("tech", limit=50)
        assert len(result) <= 10

    def test_pro_tier_limit(self):
        bot = LeadGeneratorBot(tier=Tier.PRO)
        result = bot.search_leads("tech", limit=200)
        assert len(result) <= 100

    def test_location_filter(self):
        bot = LeadGeneratorBot(tier=Tier.PRO)
        result = bot.search_leads("tech", location="Austin")
        for lead in result:
            assert "Austin" in lead["location"]

    def test_result_has_required_keys(self):
        bot = LeadGeneratorBot(tier=Tier.PRO)
        result = bot.search_leads("tech")
        if result:
            lead = result[0]
            for key in ("id", "name", "company", "industry"):
                assert key in lead

    def test_free_hides_contact_info(self):
        bot = LeadGeneratorBot(tier=Tier.FREE)
        result = bot.search_leads("finance")
        if result:
            lead = result[0]
            assert lead.get("email") in (None, "[UPGRADE TO PRO]", "***")


class TestScoreLead:
    def test_returns_dict(self):
        bot = LeadGeneratorBot(tier=Tier.PRO)
        lead = {"id": "L001", "industry": "tech", "company_size": "large",
                "revenue_estimate": 5_000_000, "verified": True, "score": 85}
        result = bot.score_lead(lead)
        assert isinstance(result, dict)

    def test_score_in_range(self):
        bot = LeadGeneratorBot(tier=Tier.PRO)
        lead = {"id": "L001", "industry": "tech", "company_size": "mid",
                "revenue_estimate": 2_000_000, "verified": True, "score": 75}
        result = bot.score_lead(lead)
        assert 0 <= result.get("score", result.get("lead_score", 0)) <= 100


class TestGetLeadDetails:
    def test_pro_returns_details(self):
        bot = LeadGeneratorBot(tier=Tier.PRO)
        result = bot.get_lead_details("L001")
        assert isinstance(result, dict)
        assert result.get("id") == "L001"

    def test_free_raises_error(self):
        bot = LeadGeneratorBot(tier=Tier.FREE)
        with pytest.raises(Exception):
            bot.get_lead_details("L001")


class TestExportToCsv:
    def test_returns_string(self):
        bot = LeadGeneratorBot(tier=Tier.PRO)
        leads = bot.search_leads("tech", limit=3)
        csv_str = bot.export_to_csv(leads)
        assert isinstance(csv_str, str)
        assert len(csv_str) > 0

    def test_free_tier_raises(self):
        bot = LeadGeneratorBot(tier=Tier.FREE)
        with pytest.raises(Exception):
            bot.export_to_csv([])


class TestRunPipeline:
    def test_run_returns_pipeline_complete(self):
        bot = LeadGeneratorBot()
        result = bot.run()
        assert result.get("pipeline_complete") is True
