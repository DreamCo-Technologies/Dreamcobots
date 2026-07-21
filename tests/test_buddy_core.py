"""
Tests for bots/buddy_core/

Covers all Buddy Core System modules:
  1. Tiers
  2. Intent Parser
  3. Tool DB
  4. Bot Generator
  5. Feedback Loop
  6. Privacy Engine
  7. Lead Engine
  8. BuddyCore (integration)
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.buddy_core.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    list_tiers,
    get_upgrade_path,
    FEATURE_INTENT_PARSER,
    FEATURE_TOOL_INJECTION,
    FEATURE_BOT_GENERATOR,
    FEATURE_FEEDBACK_LOOP,
    FEATURE_PRIVACY_VAULT,
    FEATURE_LEAD_ENGINE,
    FEATURE_ADVANCED_AI,
    FEATURE_WHITE_LABEL,
    FEATURE_CUSTOM_ENCRYPTION,
    FEATURE_ENTERPRISE_LOGS,
)
from bots.buddy_core.intent_parser import (
    IntentParser,
    IntentParserError,
    IntentType,
    Industry,
    ParsedIntent,
)
from bots.buddy_core.tool_db import (
    ToolDB,
    ToolDBError,
    ToolCategory,
    Tool,
)
from bots.buddy_core.bot_generator import (
    BotGenerator,
    BotGeneratorError,
    BotStatus,
    BotDNA,
    GeneratedBot,
)
from bots.buddy_core.feedback_loop import (
    FeedbackLoop,
    PerformanceTracker,
    RevenueTracker,
    AutoOptimizer,
    MetricType,
    PerformanceMetric,
    Optimization,
)
from bots.buddy_core.privacy_engine import (
    PrivacyEngine,
    PermissionManager,
    ActivityLogger,
    DataVault,
    DataVaultError,
    SafetyGuardrail,
    PermissionLevel,
    ActionCategory,
    PrivacyEngineError,
    UserPermission,
    ActivityLog,
)
from bots.buddy_core.lead_engine import (
    LeadEngine,
    LeadEngineError,
    LeadScraper,
    LeadScorer,
    MonetizationEngine,
    LeadSource,
    LeadStatus,
    LeadTier,
    MonetizationStrategy,
    Lead,
    Revenue,
)
from bots.buddy_core.buddy_core import (
    BuddyCore,
    BuddyCoreError,
    BuddyCoreTierError,
)
from bots.buddy_core import Tier as PublicTier


# ===========================================================================
# 1. TestBuddyCoreTiers
# ===========================================================================

class TestBuddyCoreTiers:

    def test_tier_enum_values(self):
        assert Tier.FREE.value == "free"
        assert Tier.PRO.value == "pro"
        assert Tier.ENTERPRISE.value == "enterprise"

    def test_get_tier_config_free(self):
        cfg = get_tier_config(Tier.FREE)
        assert isinstance(cfg, TierConfig)
        assert cfg.tier == Tier.FREE
        assert cfg.price_usd_monthly == 0.0

    def test_get_tier_config_pro(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0

    def test_get_tier_config_enterprise(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0

    def test_free_max_bots(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_bots_per_day == 3

    def test_pro_max_bots(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.max_bots_per_day == 20

    def test_enterprise_unlimited_bots(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_bots_per_day is None
        assert cfg.is_unlimited_bots()

    def test_enterprise_unlimited_leads(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_leads_per_day is None
        assert cfg.is_unlimited_leads()

    def test_free_has_bot_generator(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_BOT_GENERATOR)

    def test_free_lacks_tool_injection(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_TOOL_INJECTION)

    def test_pro_has_tool_injection(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_TOOL_INJECTION)

    def test_enterprise_has_white_label(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_WHITE_LABEL)
        assert cfg.has_feature(FEATURE_CUSTOM_ENCRYPTION)
        assert cfg.has_feature(FEATURE_ENTERPRISE_LOGS)

    def test_list_tiers_returns_three(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_upgrade_path_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_path_pro_to_enterprise(self):
        upgrade = get_upgrade_path(Tier.PRO)
        assert upgrade is not None
        assert upgrade.tier == Tier.ENTERPRISE

    def test_upgrade_path_enterprise_is_none(self):
        upgrade = get_upgrade_path(Tier.ENTERPRISE)
        assert upgrade is None

    def test_support_levels(self):
        assert get_tier_config(Tier.FREE).support_level == "community"
        assert get_tier_config(Tier.PRO).support_level == "priority"
        assert get_tier_config(Tier.ENTERPRISE).support_level == "dedicated"


# ===========================================================================
# 2. TestIntentParser
# ===========================================================================

class TestIntentParser:

    def setup_method(self):
        self.parser = IntentParser()

    def test_parse_returns_parsed_intent(self):
        result = self.parser.parse("create a real estate bot")
        assert isinstance(result, ParsedIntent)

    def test_parse_create_bot_intent(self):
        result = self.parser.parse("create a bot for real estate")
        assert result.intent_type == IntentType.CREATE_BOT

    def test_parse_find_leads_intent(self):
        result = self.parser.parse("find leads for my business")
        assert result.intent_type == IntentType.FIND_LEADS

    def test_parse_run_workflow_intent(self):
        result = self.parser.parse("run workflow and automate the process")
        assert result.intent_type == IntentType.RUN_WORKFLOW

    def test_parse_analyze_data_intent(self):
        result = self.parser.parse("analyze data and show stats")
        assert result.intent_type == IntentType.ANALYZE_DATA

    def test_parse_manage_tools_intent(self):
        result = self.parser.parse("manage tools and inject tools")
        assert result.intent_type == IntentType.MANAGE_TOOLS

    def test_parse_get_status_intent(self):
        result = self.parser.parse("get status of running bots")
        assert result.intent_type == IntentType.GET_STATUS

    def test_parse_unknown_intent(self):
        result = self.parser.parse("hello world random text xyz")
        assert result.intent_type == IntentType.UNKNOWN

    def test_parse_real_estate_industry(self):
        result = self.parser.parse("find real estate leads in zillow")
        assert result.industry == Industry.REAL_ESTATE

    def test_parse_finance_industry(self):
        result = self.parser.parse("analyze stock portfolio finance data")
        assert result.industry == Industry.FINANCE

    def test_parse_freelance_industry(self):
        result = self.parser.parse("create a fiverr bot for freelance jobs")
        assert result.industry == Industry.FREELANCE

    def test_parse_marketing_industry(self):
        result = self.parser.parse("run email marketing campaign with mailchimp")
        assert result.industry == Industry.MARKETING

    def test_get_confidence_unknown_is_zero(self):
        conf = self.parser.get_confidence("random text", IntentType.UNKNOWN)
        assert conf == 0.0

    def test_get_confidence_known_intent_positive(self):
        conf = self.parser.get_confidence("create a bot", IntentType.CREATE_BOT)
        assert conf > 0.0

    def test_parse_raises_on_empty_string(self):
        with pytest.raises(IntentParserError):
            self.parser.parse("")

    def test_parse_raises_on_none(self):
        with pytest.raises(IntentParserError):
            self.parser.parse(None)  # type: ignore

    def test_parse_extracts_bot_name(self):
        result = self.parser.parse("create a PropertyScout bot for real estate")
        assert result.bot_name == "PropertyscoutBot"

    def test_parse_confidence_is_float(self):
        result = self.parser.parse("create a bot")
        assert isinstance(result.confidence, float)

    def test_parse_raw_text_preserved(self):
        text = "Find leads for marketing industry"
        result = self.parser.parse(text)
        assert result.raw_text == text

    def test_get_industry_general_fallback(self):
        industry = self.parser.get_industry("random text with no industry hint")
        assert industry == Industry.GENERAL


# ===========================================================================
# 3. TestToolDB
# ===========================================================================

class TestToolDB:

    def setup_method(self):
        self.db = ToolDB()

    def test_list_all_returns_tools(self):
        tools = self.db.list_all()
        assert len(tools) >= 15

    def test_get_tool_by_id(self):
        tool = self.db.get_tool("zillow_api")
        assert tool is not None
        assert tool.name == "Zillow API"

    def test_get_tool_unknown_id_returns_none(self):
        assert self.db.get_tool("nonexistent_tool_xyz") is None

    def test_search_returns_list(self):
        results = self.db.search("email")
        assert isinstance(results, list)

    def test_search_finds_mailchimp(self):
        results = self.db.search("email marketing")
        names = [t.name for t in results]
        assert any("Mailchimp" in n or "SendGrid" in n for n in names)

    def test_get_tools_for_real_estate(self):
        tools = self.db.get_tools_for_industry("real_estate")
        assert len(tools) > 0
        tag_sets = [set(t.industry_tags) for t in tools]
        assert any("real_estate" in tags or "general" in tags for tags in tag_sets)

    def test_get_tools_for_finance(self):
        tools = self.db.get_tools_for_industry("finance")
        assert any(t.tool_id == "plaid" for t in tools)

    def test_inject_tools_returns_tools(self):
        tools = self.db.inject_tools("TestBot", "real_estate")
        assert len(tools) > 0

    def test_inject_tools_capped_at_six(self):
        tools = self.db.inject_tools("BigBot", "general")
        assert len(tools) <= 6

    def test_tool_dataclass_fields(self):
        tool = self.db.get_tool("stripe")
        assert tool is not None
        assert isinstance(tool.is_free, bool)
        assert isinstance(tool.monthly_cost_usd, float)
        assert isinstance(tool.category, ToolCategory)

    def test_search_with_industry_filter(self):
        results = self.db.search("api", industry="real_estate")
        for t in results:
            assert "real_estate" in t.industry_tags or "general" in t.industry_tags

    def test_hubspot_is_free(self):
        tool = self.db.get_tool("hubspot_crm")
        assert tool is not None
        assert tool.is_free is True

    def test_salesforce_not_free(self):
        tool = self.db.get_tool("salesforce")
        assert tool is not None
        assert tool.is_free is False


# ===========================================================================
# 4. TestBotGenerator
# ===========================================================================

class TestBotGenerator:

    def setup_method(self):
        self.gen = BotGenerator()

    def test_create_bot_returns_generated_bot(self):
        bot = self.gen.create_bot("TestBot")
        assert isinstance(bot, GeneratedBot)

    def test_create_bot_has_pending_status(self):
        bot = self.gen.create_bot("Alpha")
        assert bot.status == BotStatus.PENDING

    def test_create_bot_stores_name(self):
        bot = self.gen.create_bot("BetaBot")
        assert bot.name == "BetaBot"

    def test_create_bot_with_industry(self):
        bot = self.gen.create_bot("RealtyBot", industry="real_estate")
        assert bot.dna.industry == "real_estate"

    def test_create_bot_injects_tools(self):
        bot = self.gen.create_bot("MarketBot", industry="marketing")
        assert len(bot.tools) > 0

    def test_create_bot_generates_template(self):
        bot = self.gen.create_bot("MyBot")
        assert "class" in bot.template_code

    def test_create_bot_unique_ids(self):
        b1 = self.gen.create_bot("Bot1")
        b2 = self.gen.create_bot("Bot2")
        assert b1.bot_id != b2.bot_id

    def test_build_changes_status_to_ready(self):
        bot = self.gen.create_bot("BuildBot")
        built = self.gen.build(bot.bot_id)
        assert built.status == BotStatus.READY

    def test_deploy_changes_status_to_deployed(self):
        bot = self.gen.create_bot("DeployBot")
        self.gen.build(bot.bot_id)
        deployed = self.gen.deploy(bot.bot_id)
        assert deployed.status == BotStatus.DEPLOYED

    def test_deploy_without_build_raises(self):
        bot = self.gen.create_bot("NoBuilBot")
        with pytest.raises(BotGeneratorError):
            self.gen.deploy(bot.bot_id)

    def test_get_bot_by_id(self):
        bot = self.gen.create_bot("GetBot")
        retrieved = self.gen.get_bot(bot.bot_id)
        assert retrieved is not None
        assert retrieved.bot_id == bot.bot_id

    def test_get_bot_unknown_returns_none(self):
        assert self.gen.get_bot("nonexistent-id-xyz") is None

    def test_list_bots(self):
        self.gen.create_bot("List1")
        self.gen.create_bot("List2")
        bots = self.gen.list_bots()
        assert len(bots) >= 2

    def test_get_stats_returns_dict(self):
        self.gen.create_bot("StatsBot")
        stats = self.gen.get_stats()
        assert "total" in stats
        assert "by_status" in stats

    def test_create_bot_empty_name_raises(self):
        with pytest.raises(BotGeneratorError):
            self.gen.create_bot("")

    def test_generate_template_contains_industry(self):
        code = self.gen.generate_template("InfoBot", "finance")
        assert "finance" in code

    def test_bot_dna_fields(self):
        bot = self.gen.create_bot("DnaBot", purpose="Test purpose", industry="health")
        assert isinstance(bot.dna, BotDNA)
        assert bot.dna.purpose == "Test purpose"
        assert bot.dna.industry == "health"


# ===========================================================================
# 5. TestFeedbackLoop
# ===========================================================================

class TestFeedbackLoop:

    def setup_method(self):
        self.tracker = PerformanceTracker()
        self.revenue = RevenueTracker()
        self.optimizer = AutoOptimizer()
        self.loop = FeedbackLoop()

    def test_record_metric(self):
        m = self.tracker.record("bot1", MetricType.PERFORMANCE, 0.8)
        assert isinstance(m, PerformanceMetric)
        assert m.bot_id == "bot1"

    def test_get_metrics_for_bot(self):
        self.tracker.record("bot2", MetricType.REVENUE, 100.0)
        self.tracker.record("bot2", MetricType.ENGAGEMENT, 0.6)
        metrics = self.tracker.get_metrics("bot2")
        assert len(metrics) == 2

    def test_get_average(self):
        self.tracker.record("avg_bot", MetricType.PERFORMANCE, 0.4)
        self.tracker.record("avg_bot", MetricType.PERFORMANCE, 0.6)
        avg = self.tracker.get_average("avg_bot", MetricType.PERFORMANCE)
        assert abs(avg - 0.5) < 1e-9

    def test_get_average_empty_returns_zero(self):
        avg = self.tracker.get_average("nonexistent", MetricType.REVENUE)
        assert avg == 0.0

    def test_tracker_stats(self):
        self.tracker.record("s_bot", MetricType.ERROR_RATE, 0.05)
        stats = self.tracker.get_stats()
        assert stats["total_records"] >= 1

    def test_record_revenue(self):
        r = self.revenue.record_revenue("rb1", 49.99, "stripe")
        assert r["bot_id"] == "rb1"
        assert r["amount"] == 49.99

    def test_get_revenue_for_bot(self):
        self.revenue.record_revenue("rb2", 25.0)
        self.revenue.record_revenue("rb2", 75.0)
        assert self.revenue.get_revenue("rb2") == 100.0

    def test_get_total_revenue(self):
        self.revenue.record_revenue("x", 10.0)
        self.revenue.record_revenue("y", 20.0)
        total = self.revenue.get_total_revenue()
        assert total >= 30.0

    def test_revenue_summary(self):
        summary = self.revenue.get_summary()
        assert "total_revenue" in summary
        assert "by_bot" in summary

    def test_analyzer_returns_list(self):
        suggestions = self.optimizer.analyze("ana_bot", self.tracker)
        assert isinstance(suggestions, list)

    def test_apply_optimization_creates_record(self):
        self.tracker.record("opt_bot", MetricType.PERFORMANCE, 0.2)
        opt = self.optimizer.apply_optimization("opt_bot", "boost_performance", self.tracker)
        assert isinstance(opt, Optimization)
        assert opt.bot_id == "opt_bot"

    def test_get_optimizations_for_bot(self):
        self.tracker.record("go_bot", MetricType.ENGAGEMENT, 0.1)
        self.optimizer.apply_optimization("go_bot", "increase_engagement", self.tracker)
        opts = self.optimizer.get_optimizations("go_bot")
        assert len(opts) >= 1

    def test_optimizer_stats(self):
        stats = self.optimizer.get_stats()
        assert "total_optimizations" in stats

    def test_feedback_loop_run_cycle(self):
        result = self.loop.run_cycle("cycle_bot")
        assert "bot_id" in result
        assert "metrics_summary" in result

    def test_feedback_loop_get_summary(self):
        summary = self.loop.get_summary()
        assert "performance" in summary
        assert "revenue" in summary
        assert "optimizer" in summary


# ===========================================================================
# 6. TestPrivacyEngine
# ===========================================================================

class TestPrivacyEngine:

    def setup_method(self):
        self.pm = PermissionManager()
        self.logger = ActivityLogger()
        self.vault = DataVault()
        self.guardrail = SafetyGuardrail()
        self.engine = PrivacyEngine()

    def test_set_permission_returns_user_permission(self):
        perm = self.pm.set_permission("u1", PermissionLevel.FULL_AUTONOMY)
        assert isinstance(perm, UserPermission)
        assert perm.user_id == "u1"

    def test_get_permission_returns_set_permission(self):
        self.pm.set_permission("u2", PermissionLevel.READ_ONLY)
        perm = self.pm.get_permission("u2")
        assert perm is not None
        assert perm.level == PermissionLevel.READ_ONLY

    def test_get_permission_unknown_user_returns_none(self):
        assert self.pm.get_permission("nonexistent_user") is None

    def test_can_perform_read_only_allows_data_access(self):
        self.pm.set_permission("ro_user", PermissionLevel.READ_ONLY)
        assert self.pm.can_perform("ro_user", ActionCategory.DATA_ACCESS)

    def test_can_perform_read_only_denies_financial(self):
        self.pm.set_permission("ro_user2", PermissionLevel.READ_ONLY)
        assert not self.pm.can_perform("ro_user2", ActionCategory.FINANCIAL)

    def test_can_perform_full_autonomy_allows_all(self):
        self.pm.set_permission("fa_user", PermissionLevel.FULL_AUTONOMY)
        for cat in ActionCategory:
            assert self.pm.can_perform("fa_user", cat)

    def test_require_permission_raises_when_denied(self):
        self.pm.set_permission("deny_user", PermissionLevel.READ_ONLY)
        with pytest.raises(PrivacyEngineError):
            self.pm.require_permission("deny_user", ActionCategory.FINANCIAL)

    def test_require_permission_passes_when_allowed(self):
        self.pm.set_permission("allow_user", PermissionLevel.FULL_AUTONOMY)
        self.pm.require_permission("allow_user", ActionCategory.FINANCIAL)

    def test_activity_log_creates_entry(self):
        entry = self.logger.log("log_user", "read data", ActionCategory.DATA_ACCESS)
        assert isinstance(entry, ActivityLog)
        assert entry.user_id == "log_user"

    def test_get_logs_for_user(self):
        self.logger.log("lu1", "action1", ActionCategory.BOT_CREATION)
        self.logger.log("lu1", "action2", ActionCategory.COMMUNICATION)
        logs = self.logger.get_logs("lu1")
        assert len(logs) == 2

    def test_get_all_logs_no_user(self):
        self.logger.log("u_a", "act", ActionCategory.SYSTEM)
        logs = self.logger.get_logs()
        assert len(logs) >= 1

    def test_get_logs_limit(self):
        for i in range(10):
            self.logger.log("limit_user", f"action{i}", ActionCategory.DATA_ACCESS)
        logs = self.logger.get_logs("limit_user", limit=5)
        assert len(logs) <= 5

    def test_logger_stats(self):
        self.logger.log("stat_user", "x", ActionCategory.COMMUNICATION)
        stats = self.logger.get_stats()
        assert stats["total_logs"] >= 1

    def test_vault_store_returns_token(self):
        token = self.vault.store("api_key", "secret123", "vault_user")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_vault_retrieve_correct_user(self):
        token = self.vault.store("pw", "mypassword", "vu1")
        value = self.vault.retrieve(token, "vu1")
        assert value == "mypassword"

    def test_vault_retrieve_wrong_user_raises(self):
        token = self.vault.store("key", "val", "owner")
        with pytest.raises(DataVaultError):
            self.vault.retrieve(token, "intruder")

    def test_vault_retrieve_bad_token_raises(self):
        with pytest.raises(DataVaultError):
            self.vault.retrieve("invalid_token_xyz", "some_user")

    def test_vault_delete_returns_true(self):
        token = self.vault.store("x", "y", "del_user")
        assert self.vault.delete(token, "del_user") is True

    def test_vault_delete_bad_token_returns_false(self):
        assert self.vault.delete("nonexistent", "any_user") is False

    def test_guardrail_low_risk_approved(self):
        result = self.guardrail.check_action("read data", ActionCategory.DATA_ACCESS, "u1")
        assert result["approved"] is True
        assert result["requires_confirmation"] is False

    def test_guardrail_financial_requires_confirmation(self):
        result = self.guardrail.check_action("transfer funds", ActionCategory.FINANCIAL, "u1")
        assert result["requires_confirmation"] is True
        assert result["approved"] is False

    def test_guardrail_confirm_action(self):
        result = self.guardrail.check_action("delete system", ActionCategory.SYSTEM, "admin")
        action_id = result["action_id"]
        assert self.guardrail.confirm_action(action_id) is True

    def test_guardrail_cancel_action(self):
        result = self.guardrail.check_action("transfer", ActionCategory.FINANCIAL, "u2")
        action_id = result["action_id"]
        assert self.guardrail.cancel_action(action_id) is True

    def test_guardrail_confirm_unknown_id_false(self):
        assert self.guardrail.confirm_action("nonexistent-id") is False

    def test_guardrail_get_pending_actions(self):
        self.guardrail.check_action("pay invoice", ActionCategory.FINANCIAL, "u3")
        pending = self.guardrail.get_pending_actions()
        assert len(pending) >= 1

    def test_privacy_engine_has_all_components(self):
        assert hasattr(self.engine, "permissions")
        assert hasattr(self.engine, "logger")
        assert hasattr(self.engine, "vault")
        assert hasattr(self.engine, "guardrail")


# ===========================================================================
# 7. TestLeadEngine
# ===========================================================================

class TestLeadEngine:

    def setup_method(self):
        self.scraper = LeadScraper()
        self.scorer = LeadScorer()
        self.monetization = MonetizationEngine()
        self.engine = LeadEngine()

    def test_scrape_returns_leads(self):
        leads = self.scraper.scrape(LeadSource.LINKEDIN, count=5)
        assert len(leads) == 5

    def test_scrape_sets_raw_status(self):
        leads = self.scraper.scrape(LeadSource.GOOGLE_BUSINESS, count=3)
        for lead in leads:
            assert lead.status == LeadStatus.RAW

    def test_scrape_sets_correct_source(self):
        leads = self.scraper.scrape(LeadSource.TWITTER, count=2)
        for lead in leads:
            assert lead.source == LeadSource.TWITTER

    def test_validate_lead_with_email(self):
        lead = self.scraper.scrape(LeadSource.DIRECT, count=1)[0]
        lead.email = "test@example.com"
        lead.phone = None
        validated = self.scraper.validate(lead)
        assert validated.status == LeadStatus.VALIDATED

    def test_enrich_adds_metadata(self):
        lead = self.scraper.scrape(LeadSource.YELP, count=1)[0]
        enriched = self.scraper.enrich(lead)
        assert enriched.metadata.get("enriched") is True

    def test_score_sets_quality_score(self):
        lead = self.scraper.scrape(LeadSource.REDDIT, count=1)[0]
        lead.email = "a@b.com"
        lead.phone = "+1-555-000-1234"
        lead.company = "Acme Corp"
        lead.status = LeadStatus.VALIDATED
        lead.metadata["enriched"] = True
        scored = self.scorer.score(lead)
        assert scored.quality_score > 0.0

    def test_score_sets_tier(self):
        lead = self.scraper.scrape(LeadSource.LINKEDIN, count=1)[0]
        lead.email = "x@y.com"
        lead.phone = "+1-555-123-4567"
        lead.company = "BigCo"
        lead.status = LeadStatus.VALIDATED
        lead.metadata["enriched"] = True
        scored = self.scorer.score(lead)
        assert scored.tier in (LeadTier.HOT, LeadTier.WARM, LeadTier.COLD)

    def test_rank_sorts_by_score(self):
        leads = self.scraper.scrape(LeadSource.GOOGLE_BUSINESS, count=5)
        for l in leads:
            self.scorer.score(l)
        ranked = self.scorer.rank(leads)
        scores = [l.quality_score for l in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_get_hot_leads_filters(self):
        leads = self.scraper.scrape(LeadSource.TWITTER, count=10)
        for l in leads:
            l.email = "e@x.com"
            l.phone = "+1-555-999-0001"
            l.company = "Corp"
            l.status = LeadStatus.VALIDATED
            l.metadata["enriched"] = True
            self.scorer.score(l)
        hot = self.scorer.get_hot_leads(leads)
        for l in hot:
            assert l.tier == LeadTier.HOT

    def test_sell_lead_creates_revenue(self):
        lead = self.scraper.scrape(LeadSource.DIRECT, count=1)[0]
        rev = self.monetization.sell_lead(lead, 9.99)
        assert isinstance(rev, Revenue)
        assert rev.amount_usd == 9.99

    def test_sell_lead_updates_status(self):
        lead = self.scraper.scrape(LeadSource.DIRECT, count=1)[0]
        self.monetization.sell_lead(lead, 5.0)
        assert lead.status == LeadStatus.SOLD

    def test_sell_lead_invalid_price_raises(self):
        lead = self.scraper.scrape(LeadSource.DIRECT, count=1)[0]
        with pytest.raises(LeadEngineError):
            self.monetization.sell_lead(lead, 0.0)

    def test_create_subscription(self):
        sub = self.monetization.create_subscription("user1", "pro", 49.0)
        assert sub["status"] == "active"
        assert sub["amount_usd"] == 49.0

    def test_affiliate_revenue(self):
        rev = self.monetization.add_affiliate_revenue("partner_x", 25.0)
        assert rev.strategy == MonetizationStrategy.AFFILIATE

    def test_get_total_revenue(self):
        lead = self.scraper.scrape(LeadSource.DIRECT, count=1)[0]
        self.monetization.sell_lead(lead, 10.0)
        self.monetization.add_affiliate_revenue("src", 5.0)
        total = self.monetization.get_total_revenue()
        assert total >= 15.0

    def test_run_campaign_returns_dict(self):
        result = self.engine.run_campaign("real_estate", LeadSource.LINKEDIN, count=10)
        assert "total_leads" in result
        assert result["total_leads"] == 10

    def test_lead_engine_stats(self):
        self.engine.run_campaign("marketing", LeadSource.GOOGLE_BUSINESS, count=5)
        stats = self.engine.get_stats()
        assert stats["total_campaigns"] >= 1


# ===========================================================================
# 8. TestBuddyCore (integration)
# ===========================================================================

class TestBuddyCore:

    def setup_method(self):
        self.buddy_free = BuddyCore(tier=Tier.FREE, operator_name="FreeBot")
        self.buddy_pro = BuddyCore(tier=Tier.PRO, operator_name="ProBot")
        self.buddy_ent = BuddyCore(tier=Tier.ENTERPRISE, operator_name="EntBot")

    def test_public_import_tier(self):
        assert PublicTier.PRO == Tier.PRO

    def test_get_tier_info_returns_dict(self):
        info = self.buddy_pro.get_tier_info()
        assert "tier" in info
        assert info["tier"] == "pro"

    def test_can_access_existing_feature(self):
        assert self.buddy_pro.can_access(FEATURE_TOOL_INJECTION) is True

    def test_can_access_missing_feature(self):
        assert self.buddy_free.can_access(FEATURE_TOOL_INJECTION) is False

    def test_require_raises_tier_error(self):
        with pytest.raises(BuddyCoreTierError):
            self.buddy_free._require(FEATURE_TOOL_INJECTION)

    def test_create_bot_free(self):
        result = self.buddy_free.create_bot("FreeBot1")
        assert result["status"] == "created"

    def test_create_bot_pro(self):
        result = self.buddy_pro.create_bot("ProBot1", industry="marketing")
        assert "bot_id" in result

    def test_inject_tools_pro(self):
        result = self.buddy_pro.inject_tools("CampaignBot", "marketing")
        assert result["tools_injected"] > 0

    def test_inject_tools_free_raises(self):
        with pytest.raises(BuddyCoreTierError):
            self.buddy_free.inject_tools("Bot", "marketing")

    def test_run_lead_campaign(self):
        result = self.buddy_free.run_lead_campaign("real_estate", count=5)
        assert "total_leads" in result
        assert result["total_leads"] == 5

    def test_run_feedback_cycle_pro(self):
        bot = self.buddy_pro.create_bot("FbBot")
        result = self.buddy_pro.run_feedback_cycle(bot["bot_id"])
        assert "bot_id" in result

    def test_run_feedback_cycle_free_raises(self):
        with pytest.raises(BuddyCoreTierError):
            self.buddy_free.run_feedback_cycle("fake_bot_id")

    def test_set_permissions_pro(self):
        result = self.buddy_pro.set_permissions("user1", "full_autonomy")
        assert result["level"] == "full_autonomy"

    def test_set_permissions_invalid_level_raises(self):
        with pytest.raises(BuddyCoreError):
            self.buddy_pro.set_permissions("u1", "super_admin")

    def test_log_activity(self):
        result = self.buddy_pro.log_activity("u1", "read data", "data_access")
        assert result["status"] == "success"

    def test_check_action_safety(self):
        result = self.buddy_pro.check_action_safety("transfer", "financial", "u1")
        assert "approved" in result

    def test_store_secure_pro(self):
        result = self.buddy_pro.store_secure("api_key", "secret", "u1")
        assert result["status"] == "stored"
        assert "token" in result

    def test_store_secure_free_raises(self):
        with pytest.raises(BuddyCoreTierError):
            self.buddy_free.store_secure("k", "v", "u")

    def test_dashboard_returns_dict(self):
        dash = self.buddy_pro.dashboard()
        assert "tier" in dash
        assert "bots" in dash
        assert "leads" in dash

    def test_chat_create_bot(self):
        reply = self.buddy_free.chat("create a real estate bot")
        assert "message" in reply

    def test_chat_find_leads(self):
        reply = self.buddy_free.chat("find leads for marketing")
        assert reply["intent"] == "find_leads"

    def test_chat_get_status(self):
        reply = self.buddy_pro.chat("get status of the system")
        assert reply["intent"] == "get_status"

    def test_chat_analyze_data(self):
        reply = self.buddy_pro.chat("analyze data and show metrics")
        assert reply["intent"] == "analyze_data"

    def test_process_chat_command(self):
        result = self.buddy_pro.process({"command": "chat", "message": "get status"})
        assert "intent" in result

    def test_process_create_bot_command(self):
        result = self.buddy_pro.process({"command": "create_bot", "name": "ProcessBot", "industry": "finance"})
        assert result["status"] == "created"

    def test_process_run_lead_campaign(self):
        result = self.buddy_pro.process({"command": "run_lead_campaign", "industry": "health", "count": 5})
        assert "total_leads" in result

    def test_process_dashboard_command(self):
        result = self.buddy_pro.process({"command": "dashboard"})
        assert "tier" in result

    def test_process_get_tier_info(self):
        result = self.buddy_pro.process({"command": "get_tier_info"})
        assert result["tier"] == "pro"

    def test_process_unknown_command_raises(self):
        with pytest.raises(BuddyCoreError):
            self.buddy_pro.process({"command": "unknown_xyz"})

    def test_enterprise_has_all_features(self):
        for feature in [
            FEATURE_WHITE_LABEL, FEATURE_CUSTOM_ENCRYPTION, FEATURE_ENTERPRISE_LOGS
        ]:
            assert self.buddy_ent.can_access(feature)
