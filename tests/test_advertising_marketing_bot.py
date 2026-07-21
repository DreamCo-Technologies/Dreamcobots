"""
Tests for bots/advertising_marketing_bot/

Covers:
  1. Tiers
  2. AdvertisingMarketingBot — pipeline stages, Advertising and Marketing Team Button
  3. Chat interface
  4. CRM and lead utilities
  5. GlobalAISourcesFlow integration
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.advertising_marketing_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_TRAFFIC_GENERATION,
    FEATURE_LEAD_SCRAPER,
    FEATURE_LEAD_VALIDATOR,
    FEATURE_OUTREACH,
    FEATURE_FUNNEL,
    FEATURE_APPOINTMENT,
    FEATURE_CLOSE,
    FEATURE_PAYMENT,
    FEATURE_CRM_INTEGRATION,
    FEATURE_AUTOMATION,
    FEATURE_AI_AGENTS,
)
from bots.advertising_marketing_bot.advertising_marketing_bot import (
    AdvertisingMarketingBot,
    AdvertisingMarketingError,
    AdvertisingMarketingTierError,
    Lead,
    TrafficResult,
    OutreachResult,
    AppointmentResult,
    DealResult,
    PaymentResult,
    CRMRecord,
    LEAD_VALIDATION_THRESHOLD,
    MIN_VISITORS_PER_DOLLAR,
    MAX_VISITORS_PER_DOLLAR,
)
from framework import GlobalAISourcesFlow


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestAdvertisingMarketingTiers:
    def test_three_tiers(self):
        assert len(list_tiers()) == 3

    def test_free_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0

    def test_enterprise_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_free_max_leads(self):
        assert get_tier_config(Tier.FREE).max_leads_per_day == 100

    def test_pro_max_leads(self):
        assert get_tier_config(Tier.PRO).max_leads_per_day == 5_000

    def test_enterprise_unlimited_leads(self):
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited_leads()

    def test_free_max_campaigns(self):
        assert get_tier_config(Tier.FREE).max_campaigns == 1

    def test_pro_max_campaigns(self):
        assert get_tier_config(Tier.PRO).max_campaigns == 10

    def test_enterprise_unlimited_campaigns(self):
        assert get_tier_config(Tier.ENTERPRISE).max_campaigns is None

    def test_free_has_traffic_generation(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_TRAFFIC_GENERATION)

    def test_free_has_lead_scraper(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_LEAD_SCRAPER)

    def test_free_has_lead_validator(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_LEAD_VALIDATOR)

    def test_free_lacks_outreach(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_OUTREACH)

    def test_free_lacks_payment(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_PAYMENT)

    def test_pro_has_outreach(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_OUTREACH)

    def test_pro_has_crm(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_CRM_INTEGRATION)

    def test_pro_has_payment(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_PAYMENT)

    def test_pro_lacks_ai_agents(self):
        assert not get_tier_config(Tier.PRO).has_feature(FEATURE_AI_AGENTS)

    def test_enterprise_has_automation(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_AUTOMATION)

    def test_enterprise_has_ai_agents(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_AI_AGENTS)

    def test_upgrade_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade.tier == Tier.PRO

    def test_upgrade_pro_to_enterprise(self):
        upgrade = get_upgrade_path(Tier.PRO)
        assert upgrade.tier == Tier.ENTERPRISE

    def test_upgrade_enterprise_returns_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_tier_has_feature_method(self):
        config = get_tier_config(Tier.FREE)
        assert hasattr(config, "has_feature")

    def test_tier_is_unlimited_leads_method(self):
        config = get_tier_config(Tier.ENTERPRISE)
        assert config.is_unlimited_leads() is True

    def test_list_tiers_returns_list(self):
        assert isinstance(list_tiers(), list)

    def test_free_support_level(self):
        assert "Community" in get_tier_config(Tier.FREE).support_level

    def test_enterprise_support_level(self):
        assert "24/7" in get_tier_config(Tier.ENTERPRISE).support_level


# ===========================================================================
# 2. Bot instantiation and basics
# ===========================================================================

class TestAdvertisingMarketingBotInit:
    def test_default_tier_is_free(self):
        bot = AdvertisingMarketingBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = AdvertisingMarketingBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = AdvertisingMarketingBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_has_flow_attribute(self):
        bot = AdvertisingMarketingBot()
        assert hasattr(bot, "flow")

    def test_flow_is_global_ai_sources_flow(self):
        bot = AdvertisingMarketingBot()
        assert isinstance(bot.flow, GlobalAISourcesFlow)

    def test_flow_validates(self):
        bot = AdvertisingMarketingBot()
        assert bot.flow.validate() is True

    def test_initial_leads_empty(self):
        bot = AdvertisingMarketingBot()
        assert bot.get_leads() == []

    def test_initial_crm_records_empty(self):
        bot = AdvertisingMarketingBot()
        assert bot.get_crm_records() == []

    def test_initial_pipeline_runs_empty(self):
        bot = AdvertisingMarketingBot()
        assert bot.get_pipeline_runs() == []

    def test_get_tier_info_returns_dict(self):
        bot = AdvertisingMarketingBot()
        info = bot.get_tier_info()
        assert isinstance(info, dict)

    def test_get_tier_info_has_tier_key(self):
        bot = AdvertisingMarketingBot(tier=Tier.PRO)
        assert bot.get_tier_info()["tier"] == "pro"

    def test_get_tier_info_has_price(self):
        bot = AdvertisingMarketingBot(tier=Tier.PRO)
        assert bot.get_tier_info()["price_usd_monthly"] == 49.0

    def test_bot_name_stored(self):
        bot = AdvertisingMarketingBot(bot_name="TestBot")
        assert bot.bot_name == "TestBot"

    def test_upgrade_tier_free(self):
        bot = AdvertisingMarketingBot(tier=Tier.FREE)
        upgrade = bot.upgrade_tier()
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_tier_enterprise_returns_none(self):
        bot = AdvertisingMarketingBot(tier=Tier.ENTERPRISE)
        assert bot.upgrade_tier() is None


# ===========================================================================
# 3. Advertising and Marketing Team Button — full pipeline
# ===========================================================================

class TestAdvertisingMarketingTeamButton:
    def setup_method(self):
        self.bot = AdvertisingMarketingBot(tier=Tier.ENTERPRISE)

    def test_pipeline_returns_dict(self):
        result = self.bot.advertising_marketing_team()
        assert isinstance(result, dict)

    def test_pipeline_complete(self):
        result = self.bot.advertising_marketing_team()
        assert result["pipeline_complete"] is True

    def test_pipeline_has_stages(self):
        result = self.bot.advertising_marketing_team()
        assert "stages" in result

    def test_pipeline_has_traffic_stage(self):
        result = self.bot.advertising_marketing_team()
        assert "traffic" in result["stages"]

    def test_pipeline_has_lead_scraper_stage(self):
        result = self.bot.advertising_marketing_team()
        assert "lead_scraper" in result["stages"]

    def test_pipeline_has_validator_stage(self):
        result = self.bot.advertising_marketing_team()
        assert "validator" in result["stages"]

    def test_pipeline_has_outreach_stage(self):
        result = self.bot.advertising_marketing_team()
        assert "outreach" in result["stages"]

    def test_pipeline_has_funnel_stage(self):
        result = self.bot.advertising_marketing_team()
        assert "funnel" in result["stages"]

    def test_pipeline_has_appointment_stage(self):
        result = self.bot.advertising_marketing_team()
        assert "appointment" in result["stages"]

    def test_pipeline_has_close_stage(self):
        result = self.bot.advertising_marketing_team()
        assert "close" in result["stages"]

    def test_pipeline_has_payment_stage(self):
        result = self.bot.advertising_marketing_team()
        assert "payment" in result["stages"]

    def test_pipeline_has_crm_stage(self):
        result = self.bot.advertising_marketing_team()
        assert "crm" in result["stages"]

    def test_pipeline_has_automation_stage(self):
        result = self.bot.advertising_marketing_team()
        assert "automation" in result["stages"]

    def test_pipeline_has_ai_agents_stage(self):
        result = self.bot.advertising_marketing_team()
        assert "ai_agents" in result["stages"]

    def test_pipeline_campaign_name_stored(self):
        result = self.bot.advertising_marketing_team(campaign_name="My Campaign")
        assert result["campaign_name"] == "My Campaign"

    def test_pipeline_tier_stored(self):
        result = self.bot.advertising_marketing_team()
        assert result["tier"] == "enterprise"

    def test_pipeline_budget_stored(self):
        result = self.bot.advertising_marketing_team(budget_usd=1000.0)
        assert result["budget_usd"] == 1000.0

    def test_pipeline_records_run_history(self):
        self.bot.advertising_marketing_team()
        assert len(self.bot.get_pipeline_runs()) == 1

    def test_pipeline_multiple_runs_stored(self):
        self.bot.advertising_marketing_team()
        self.bot.advertising_marketing_team()
        assert len(self.bot.get_pipeline_runs()) == 2

    def test_traffic_stage_has_visitors(self):
        result = self.bot.advertising_marketing_team(budget_usd=100.0)
        assert result["stages"]["traffic"]["visitors"] >= 1

    def test_traffic_stage_has_cost(self):
        result = self.bot.advertising_marketing_team(budget_usd=100.0)
        assert result["stages"]["traffic"]["cost_usd"] == 100.0

    def test_lead_scraper_collects_leads(self):
        result = self.bot.advertising_marketing_team(lead_count=5)
        assert result["stages"]["lead_scraper"]["leads_collected"] == 5

    def test_validator_total_equals_scraper(self):
        result = self.bot.advertising_marketing_team(lead_count=10)
        validated = result["stages"]["validator"]["leads_validated"]
        rejected = result["stages"]["validator"]["leads_rejected"]
        assert validated + rejected == 10

    def test_outreach_messages_sent(self):
        result = self.bot.advertising_marketing_team(lead_count=5)
        assert result["stages"]["outreach"]["messages_sent"] >= 0

    def test_close_total_value_non_negative(self):
        result = self.bot.advertising_marketing_team(lead_count=5)
        assert result["stages"]["close"]["total_value_usd"] >= 0.0

    def test_payment_total_collected_non_negative(self):
        result = self.bot.advertising_marketing_team(lead_count=5)
        assert result["stages"]["payment"]["total_collected_usd"] >= 0.0

    def test_crm_records_synced_count(self):
        result = self.bot.advertising_marketing_team(lead_count=5)
        assert result["stages"]["crm"]["records_synced"] >= 0

    def test_flow_pipeline_key_present(self):
        result = self.bot.advertising_marketing_team()
        assert "flow_pipeline" in result

    def test_flow_pipeline_complete(self):
        result = self.bot.advertising_marketing_team()
        assert result["flow_pipeline"]["pipeline_complete"] is True

    def test_leads_accumulated_in_session(self):
        self.bot.advertising_marketing_team(lead_count=5)
        assert len(self.bot.get_leads()) == 5

    def test_crm_records_accumulated_in_session(self):
        self.bot.advertising_marketing_team(lead_count=10)
        assert len(self.bot.get_crm_records()) >= 0


# ===========================================================================
# 4. Free tier pipeline — limited stages
# ===========================================================================

class TestFreeTeamPipeline:
    def setup_method(self):
        self.bot = AdvertisingMarketingBot(tier=Tier.FREE)

    def test_free_pipeline_complete(self):
        result = self.bot.advertising_marketing_team(lead_count=5)
        assert result["pipeline_complete"] is True

    def test_free_has_traffic_stage(self):
        result = self.bot.advertising_marketing_team(lead_count=5)
        assert "traffic" in result["stages"]

    def test_free_has_lead_scraper_stage(self):
        result = self.bot.advertising_marketing_team(lead_count=5)
        assert "lead_scraper" in result["stages"]

    def test_free_has_validator_stage(self):
        result = self.bot.advertising_marketing_team(lead_count=5)
        assert "validator" in result["stages"]

    def test_free_lacks_outreach_stage(self):
        result = self.bot.advertising_marketing_team(lead_count=5)
        assert "outreach" not in result["stages"]

    def test_free_lacks_payment_stage(self):
        result = self.bot.advertising_marketing_team(lead_count=5)
        assert "payment" not in result["stages"]

    def test_free_lacks_crm_stage(self):
        result = self.bot.advertising_marketing_team(lead_count=5)
        assert "crm" not in result["stages"]

    def test_free_lacks_ai_agents_stage(self):
        result = self.bot.advertising_marketing_team(lead_count=5)
        assert "ai_agents" not in result["stages"]

    def test_free_lead_count_respects_daily_limit(self):
        result = self.bot.advertising_marketing_team(lead_count=200)
        assert result["stages"]["lead_scraper"]["leads_collected"] <= 100


# ===========================================================================
# 5. Data models
# ===========================================================================

class TestLeadDataModel:
    def test_lead_has_lead_id(self):
        lead = Lead()
        assert lead.lead_id is not None

    def test_lead_default_status(self):
        lead = Lead()
        assert lead.status == "raw"

    def test_lead_has_created_at(self):
        lead = Lead()
        assert lead.created_at is not None

    def test_lead_fields(self):
        lead = Lead(name="Alice", email="alice@example.com")
        assert lead.name == "Alice"
        assert lead.email == "alice@example.com"


class TestTrafficResultModel:
    def test_traffic_result_fields(self):
        t = TrafficResult(source="google", visitors=100, cost_usd=50.0)
        assert t.visitors == 100
        assert t.cost_usd == 50.0
        assert t.source == "google"


class TestOutreachResultModel:
    def test_outreach_result_default_sent(self):
        o = OutreachResult(lead_id="abc", channel="email")
        assert o.message_sent is True

    def test_outreach_result_lead_id(self):
        o = OutreachResult(lead_id="xyz", channel="sms")
        assert o.lead_id == "xyz"


class TestPaymentResultModel:
    def test_payment_result_has_link(self):
        p = PaymentResult(lead_id="123", amount_usd=500.0, payment_link="https://pay.example.com/123")
        assert "https" in p.payment_link

    def test_payment_result_has_transaction_id(self):
        p = PaymentResult(lead_id="123")
        assert p.transaction_id is not None


class TestCRMRecordModel:
    def test_crm_record_synced_by_default(self):
        r = CRMRecord(lead_id="abc")
        assert r.synced is True

    def test_crm_record_has_crm_id(self):
        r = CRMRecord(lead_id="abc")
        assert r.crm_id is not None


# ===========================================================================
# 6. Chat interface
# ===========================================================================

class TestAdvertisingMarketingBotChat:
    def setup_method(self):
        self.bot = AdvertisingMarketingBot(tier=Tier.PRO)

    def test_chat_returns_dict(self):
        assert isinstance(self.bot.chat("hello"), dict)

    def test_chat_has_message_key(self):
        result = self.bot.chat("hello")
        assert "message" in result

    def test_chat_has_action_key(self):
        result = self.bot.chat("hello")
        assert "action" in result

    def test_chat_campaign_trigger(self):
        result = self.bot.chat("start campaign")
        assert "pipeline" in result["message"].lower() or result["action"] == "suggest_pipeline"

    def test_chat_lead_query(self):
        result = self.bot.chat("how many leads do I have")
        assert result["action"] == "report_leads"

    def test_chat_crm_query(self):
        result = self.bot.chat("crm status")
        assert result["action"] == "report_crm"

    def test_chat_upgrade_pro(self):
        bot = AdvertisingMarketingBot(tier=Tier.PRO)
        result = bot.chat("how do I upgrade")
        assert result["action"] == "suggest_upgrade"

    def test_chat_upgrade_enterprise_returns_max(self):
        bot = AdvertisingMarketingBot(tier=Tier.ENTERPRISE)
        result = bot.chat("I want to upgrade")
        assert result["action"] == "already_max"

    def test_chat_general_message(self):
        result = self.bot.chat("what can you do")
        assert len(result["message"]) > 0

    def test_chat_general_action(self):
        result = self.bot.chat("what can you do")
        assert result["action"] == "general_help"


# ===========================================================================
# 7. GlobalAISourcesFlow integration
# ===========================================================================

class TestAdvertisingMarketingFlowIntegration:
    def test_bot_has_flow(self):
        bot = AdvertisingMarketingBot()
        assert hasattr(bot, "flow")

    def test_flow_instance_type(self):
        bot = AdvertisingMarketingBot()
        assert isinstance(bot.flow, GlobalAISourcesFlow)

    def test_flow_validates(self):
        bot = AdvertisingMarketingBot()
        assert bot.flow.validate() is True

    def test_run_returns_pipeline_complete(self):
        bot = AdvertisingMarketingBot(tier=Tier.ENTERPRISE)
        result = bot.advertising_marketing_team()
        assert result["pipeline_complete"] is True

    def test_flow_pipeline_key_present_in_result(self):
        bot = AdvertisingMarketingBot(tier=Tier.PRO)
        result = bot.advertising_marketing_team()
        assert "flow_pipeline" in result

    def test_flow_bot_name_matches(self):
        bot = AdvertisingMarketingBot(bot_name="MyMarketingBot")
        assert bot.flow.bot_name == "MyMarketingBot"


# ===========================================================================
# 8. Pipeline simulation constants
# ===========================================================================

class TestPipelineConstants:
    def test_lead_validation_threshold_is_float(self):
        assert isinstance(LEAD_VALIDATION_THRESHOLD, float)

    def test_lead_validation_threshold_between_zero_and_one(self):
        assert 0.0 <= LEAD_VALIDATION_THRESHOLD <= 1.0

    def test_min_visitors_per_dollar_positive(self):
        assert MIN_VISITORS_PER_DOLLAR > 0

    def test_max_visitors_greater_than_min(self):
        assert MAX_VISITORS_PER_DOLLAR > MIN_VISITORS_PER_DOLLAR

    def test_lead_validated_above_threshold(self):
        lead = Lead(score=LEAD_VALIDATION_THRESHOLD)
        bot = AdvertisingMarketingBot()
        valid = bot._validate_leads([lead])
        assert len(valid) == 1

    def test_lead_rejected_below_threshold(self):
        lead = Lead(score=max(0.0, LEAD_VALIDATION_THRESHOLD - 0.01))
        bot = AdvertisingMarketingBot()
        valid = bot._validate_leads([lead])
        assert len(valid) == 0

    def test_traffic_generation_respects_budget(self):
        bot = AdvertisingMarketingBot()
        traffic = bot._generate_traffic("general", 0.0)
        assert traffic.visitors >= 1

    def test_zero_lead_count_produces_empty_list(self):
        bot = AdvertisingMarketingBot(tier=Tier.ENTERPRISE)
        result = bot.advertising_marketing_team(lead_count=0)
        assert result["stages"]["lead_scraper"]["leads_collected"] == 0

    def test_pipeline_with_empty_leads_completes(self):
        bot = AdvertisingMarketingBot(tier=Tier.ENTERPRISE)
        result = bot.advertising_marketing_team(lead_count=0)
        assert result["pipeline_complete"] is True
