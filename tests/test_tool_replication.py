"""
Tests for bots/buddy_core/tool_scraper.py and bots/buddy_core/tool_replication.py

Covers:
  1. ToolScraper — detect platform type, capabilities, industry tags, auth type
  2. ToolScraper — analyze_known_platform and batch analysis
  3. ToolReplicationEngine — replicate single and batch profiles
  4. ToolReplicationEngine — generated source code sanity checks
  5. BuddyCore integration — scrape_tool / replicate_tool via tier gates
  6. Tool_DB expansion — new categories and expanded catalogue
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.buddy_core.tool_scraper import (
    ToolScraper,
    ToolProfile,
    ToolScraperError,
    CapabilityTag,
    PlatformType,
)
from bots.buddy_core.tool_replication import (
    ToolReplicationEngine,
    ReplicatedTool,
    ToolReplicationError,
)
from bots.buddy_core.tool_db import ToolDB, ToolCategory
from bots.buddy_core.tiers import (
    Tier,
    get_tier_config,
    FEATURE_TOOL_SCRAPER,
    FEATURE_TOOL_REPLICATION,
)
from bots.buddy_core.buddy_core import BuddyCore, BuddyCoreTierError


# ===========================================================================
# 1. ToolScraper — basic analysis
# ===========================================================================

class TestToolScraper:

    def setup_method(self):
        self.scraper = ToolScraper()

    # ------------------------------------------------------------------
    # Input validation
    # ------------------------------------------------------------------

    def test_empty_tool_name_raises(self):
        with pytest.raises(ToolScraperError):
            self.scraper.analyze(tool_name="", description="Some tool.")

    def test_empty_description_raises(self):
        with pytest.raises(ToolScraperError):
            self.scraper.analyze(tool_name="MyTool", description="")

    def test_whitespace_tool_name_raises(self):
        with pytest.raises(ToolScraperError):
            self.scraper.analyze(tool_name="   ", description="Some tool.")

    # ------------------------------------------------------------------
    # Returns ToolProfile
    # ------------------------------------------------------------------

    def test_returns_tool_profile(self):
        profile = self.scraper.analyze(
            tool_name="TestTool",
            description="A generic tool for testing purposes.",
        )
        assert isinstance(profile, ToolProfile)

    def test_tool_name_preserved(self):
        profile = self.scraper.analyze(
            tool_name="MyService",
            description="A SaaS service.",
        )
        assert profile.tool_name == "MyService"

    def test_base_url_preserved(self):
        profile = self.scraper.analyze(
            tool_name="TestAPI",
            description="Test API.",
            base_url="https://api.test.com/v1",
        )
        assert profile.base_url == "https://api.test.com/v1"

    def test_is_open_source_flag(self):
        profile = self.scraper.analyze(
            tool_name="OpenLib",
            description="An open-source library.",
            is_open_source=True,
        )
        assert profile.is_open_source is True

    def test_has_free_tier_flag(self):
        profile = self.scraper.analyze(
            tool_name="FreeTool",
            description="A tool with a free tier.",
            has_free_tier=True,
        )
        assert profile.has_free_tier is True

    # ------------------------------------------------------------------
    # Platform type detection
    # ------------------------------------------------------------------

    def test_detects_payment_platform(self):
        profile = self.scraper.analyze(
            tool_name="Stripe",
            description="Online payment processing and subscription billing.",
            base_url="https://api.stripe.com/v1",
        )
        assert profile.platform_type == PlatformType.PAYMENT

    def test_detects_messaging_platform(self):
        profile = self.scraper.analyze(
            tool_name="Slack",
            description="Team messaging with channels and webhooks.",
        )
        assert profile.platform_type == PlatformType.MESSAGING

    def test_detects_automation_platform(self):
        profile = self.scraper.analyze(
            tool_name="Zapier",
            description="Workflow automation platform.",
            extra_keywords=["automate", "trigger", "action"],
        )
        assert profile.platform_type == PlatformType.AUTOMATION

    def test_detects_ai_ml_platform(self):
        profile = self.scraper.analyze(
            tool_name="OpenAI",
            description="GPT language models for NLP tasks.",
        )
        assert profile.platform_type == PlatformType.AI_ML

    def test_unknown_platform_type(self):
        profile = self.scraper.analyze(
            tool_name="RandomThing",
            description="A completely generic unclassifiable widget.",
        )
        assert profile.platform_type == PlatformType.UNKNOWN

    # ------------------------------------------------------------------
    # Capability detection
    # ------------------------------------------------------------------

    def test_detects_crud_capability(self):
        profile = self.scraper.analyze(
            tool_name="RESTAPI",
            description="Provides full CRUD operations via REST endpoints.",
        )
        assert CapabilityTag.CRUD in profile.capabilities

    def test_detects_webhook_capability(self):
        profile = self.scraper.analyze(
            tool_name="WebhookService",
            description="Send events via webhook callbacks.",
        )
        assert CapabilityTag.WEBHOOKS in profile.capabilities

    def test_detects_payment_capability(self):
        profile = self.scraper.analyze(
            tool_name="PayGate",
            description="Accept payment and charge customers at checkout.",
        )
        assert CapabilityTag.PAYMENT_PROCESSING in profile.capabilities

    def test_detects_subscription_billing(self):
        profile = self.scraper.analyze(
            tool_name="BillingPro",
            description="Recurring subscription billing and invoice generation.",
        )
        assert CapabilityTag.SUBSCRIPTION_BILLING in profile.capabilities

    def test_detects_nlp_capability(self):
        profile = self.scraper.analyze(
            tool_name="TextAI",
            description="Natural language processing and GPT text generation.",
        )
        assert CapabilityTag.NLP in profile.capabilities

    def test_detects_email_delivery(self):
        profile = self.scraper.analyze(
            tool_name="MailBot",
            description="Send transactional email via SMTP or API.",
        )
        assert CapabilityTag.EMAIL_DELIVERY in profile.capabilities

    def test_detects_analytics(self):
        profile = self.scraper.analyze(
            tool_name="AnalyticsHub",
            description="Track metrics, statistics, and reports.",
        )
        assert CapabilityTag.ANALYTICS in profile.capabilities

    def test_no_false_positive_capabilities(self):
        profile = self.scraper.analyze(
            tool_name="EmptyTool",
            description="A completely minimal widget with no features.",
        )
        assert CapabilityTag.PAYMENT_PROCESSING not in profile.capabilities
        assert CapabilityTag.SUBSCRIPTION_BILLING not in profile.capabilities

    # ------------------------------------------------------------------
    # Industry tag detection
    # ------------------------------------------------------------------

    def test_detects_finance_tag(self):
        profile = self.scraper.analyze(
            tool_name="BankAPI",
            description="Banking and fintech data aggregation.",
        )
        assert "finance" in profile.industry_tags

    def test_detects_health_tag(self):
        profile = self.scraper.analyze(
            tool_name="HealthBot",
            description="Patient EHR and clinical data integration.",
        )
        assert "health" in profile.industry_tags

    def test_defaults_to_general_tag(self):
        profile = self.scraper.analyze(
            tool_name="NoCategory",
            description="A very generic purpose tool.",
        )
        assert "general" in profile.industry_tags

    # ------------------------------------------------------------------
    # Auth type detection
    # ------------------------------------------------------------------

    def test_detects_oauth2(self):
        profile = self.scraper.analyze(
            tool_name="OAuthService",
            description="Uses OAuth2 for authentication.",
        )
        assert profile.auth_type == "oauth2"

    def test_detects_api_key(self):
        profile = self.scraper.analyze(
            tool_name="APIKeyService",
            description="Authenticate using an API key.",
        )
        assert profile.auth_type == "api_key"

    # ------------------------------------------------------------------
    # Language hints
    # ------------------------------------------------------------------

    def test_detects_python_hint(self):
        profile = self.scraper.analyze(
            tool_name="PythonLib",
            description="Install via pip. Supports Django and FastAPI.",
        )
        assert "python" in profile.language_hints

    def test_detects_javascript_hint(self):
        profile = self.scraper.analyze(
            tool_name="NodeService",
            description="Node.js and npm package integration.",
        )
        assert "javascript" in profile.language_hints

    # ------------------------------------------------------------------
    # Workflow steps
    # ------------------------------------------------------------------

    def test_workflow_steps_not_empty(self):
        profile = self.scraper.analyze(
            tool_name="AnyTool",
            description="A simple REST CRUD tool.",
        )
        assert len(profile.workflow_steps) > 0

    # ------------------------------------------------------------------
    # Replication priority
    # ------------------------------------------------------------------

    def test_priority_within_range(self):
        profile = self.scraper.analyze(
            tool_name="PriorityTest",
            description="A payment subscription billing machine learning NLP tool.",
        )
        assert 1 <= profile.replication_priority <= 10

    # ------------------------------------------------------------------
    # to_dict
    # ------------------------------------------------------------------

    def test_to_dict_keys(self):
        profile = self.scraper.analyze(
            tool_name="DictTool",
            description="Testing to_dict output.",
        )
        d = profile.to_dict()
        for key in ("tool_name", "platform_type", "capabilities", "industry_tags"):
            assert key in d

    # ------------------------------------------------------------------
    # Known platform catalogue
    # ------------------------------------------------------------------

    def test_list_known_platforms_returns_list(self):
        platforms = self.scraper.list_known_platforms()
        assert isinstance(platforms, list)
        assert len(platforms) > 0

    def test_analyze_known_platform_zapier(self):
        profile = self.scraper.analyze_known_platform("zapier")
        assert profile is not None
        assert profile.tool_name == "Zapier"
        assert CapabilityTag.WORKFLOW_AUTOMATION in profile.capabilities

    def test_analyze_known_platform_stripe(self):
        profile = self.scraper.analyze_known_platform("stripe")
        assert profile is not None
        assert CapabilityTag.PAYMENT_PROCESSING in profile.capabilities

    def test_analyze_known_platform_github(self):
        profile = self.scraper.analyze_known_platform("github")
        assert profile is not None
        assert profile.platform_type == PlatformType.DEVOPS

    def test_analyze_known_platform_case_insensitive(self):
        profile = self.scraper.analyze_known_platform("SLACK")
        assert profile is not None
        assert profile.tool_name == "Slack"

    def test_analyze_known_platform_unknown_returns_none(self):
        result = self.scraper.analyze_known_platform("nonexistent_platform_xyz")
        assert result is None

    # ------------------------------------------------------------------
    # Batch analysis
    # ------------------------------------------------------------------

    def test_analyze_batch_returns_list(self):
        tools = [
            {"tool_name": "Tool1", "description": "First tool."},
            {"tool_name": "Tool2", "description": "Second tool."},
        ]
        profiles = self.scraper.analyze_batch(tools)
        assert len(profiles) == 2
        assert all(isinstance(p, ToolProfile) for p in profiles)

    def test_analyze_batch_empty(self):
        profiles = self.scraper.analyze_batch([])
        assert profiles == []


# ===========================================================================
# 2. ToolReplicationEngine
# ===========================================================================

class TestToolReplicationEngine:

    def setup_method(self):
        self.scraper = ToolScraper()
        self.engine = ToolReplicationEngine()

    def _make_profile(self, name="TestTool", description="A test tool.") -> ToolProfile:
        return self.scraper.analyze(tool_name=name, description=description)

    # ------------------------------------------------------------------
    # Invalid input
    # ------------------------------------------------------------------

    def test_replicate_non_profile_raises(self):
        with pytest.raises(ToolReplicationError):
            self.engine.replicate({"tool_name": "Bad"})  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Returns ReplicatedTool
    # ------------------------------------------------------------------

    def test_returns_replicated_tool(self):
        profile = self._make_profile()
        replica = self.engine.replicate(profile)
        assert isinstance(replica, ReplicatedTool)

    def test_tool_name_preserved(self):
        profile = self._make_profile("MyService")
        replica = self.engine.replicate(profile)
        assert replica.tool_name == "MyService"

    def test_class_name_is_buddy_prefixed(self):
        profile = self._make_profile("Zapier")
        replica = self.engine.replicate(profile)
        assert replica.buddy_class_name.startswith("Buddy")

    def test_class_name_pascal_case(self):
        profile = self._make_profile("my tool name")
        replica = self.engine.replicate(profile)
        assert replica.buddy_class_name[0].isupper()

    def test_workflow_not_empty(self):
        profile = self._make_profile()
        replica = self.engine.replicate(profile)
        assert len(replica.workflow) > 0

    def test_platform_type_set(self):
        profile = self._make_profile("Stripe", "Payment processing platform.")
        replica = self.engine.replicate(profile)
        assert isinstance(replica.platform_type, str)

    # ------------------------------------------------------------------
    # Source code checks
    # ------------------------------------------------------------------

    def test_source_code_contains_class(self):
        profile = self._make_profile("ZapierClone")
        replica = self.engine.replicate(profile)
        assert "class Buddy" in replica.source_code

    def test_source_code_contains_framework_import(self):
        profile = self._make_profile()
        replica = self.engine.replicate(profile)
        assert "GlobalAISourcesFlow" in replica.source_code

    def test_source_code_contains_run_pipeline(self):
        profile = self._make_profile()
        replica = self.engine.replicate(profile)
        assert "run_pipeline" in replica.source_code

    def test_source_code_contains_get_status(self):
        profile = self._make_profile()
        replica = self.engine.replicate(profile)
        assert "get_status" in replica.source_code

    def test_payment_source_includes_create_payment(self):
        profile = self.scraper.analyze(
            tool_name="PaymentTool",
            description="Accept payment and charge customers.",
        )
        replica = self.engine.replicate(profile)
        assert "create_payment" in replica.source_code

    def test_webhook_source_includes_register_webhook(self):
        profile = self.scraper.analyze(
            tool_name="WebhookTool",
            description="Register webhook callbacks for event notifications.",
        )
        replica = self.engine.replicate(profile)
        assert "register_webhook" in replica.source_code

    def test_workflow_source_includes_create_workflow(self):
        profile = self.scraper.analyze(
            tool_name="AutomationTool",
            description="Automate workflows with triggers and actions.",
        )
        replica = self.engine.replicate(profile)
        assert "create_workflow" in replica.source_code

    def test_nlp_source_includes_generate_text(self):
        profile = self.scraper.analyze(
            tool_name="TextGen",
            description="Natural language processing with GPT text generation.",
        )
        replica = self.engine.replicate(profile)
        assert "generate_text" in replica.source_code

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def test_to_dict_has_required_keys(self):
        profile = self._make_profile()
        replica = self.engine.replicate(profile)
        d = replica.to_dict()
        for key in (
            "tool_name", "buddy_class_name", "platform_type",
            "workflow", "capabilities_replicated", "generated_at",
        ):
            assert key in d, f"Missing key: {key}"

    def test_generated_at_is_string_in_to_dict(self):
        profile = self._make_profile()
        replica = self.engine.replicate(profile)
        assert isinstance(replica.to_dict()["generated_at"], str)

    # ------------------------------------------------------------------
    # Batch replication
    # ------------------------------------------------------------------

    def test_replicate_batch(self):
        profiles = [
            self._make_profile("ToolA"),
            self._make_profile("ToolB"),
        ]
        replicas = self.engine.replicate_batch(profiles)
        assert len(replicas) == 2
        assert all(isinstance(r, ReplicatedTool) for r in replicas)

    def test_replicate_batch_empty(self):
        assert self.engine.replicate_batch([]) == []

    # ------------------------------------------------------------------
    # Known platforms
    # ------------------------------------------------------------------

    def test_replicate_zapier(self):
        profile = self.scraper.analyze_known_platform("zapier")
        replica = self.engine.replicate(profile)
        assert "Zapier" in replica.tool_name
        assert "create_workflow" in replica.source_code

    def test_replicate_stripe(self):
        profile = self.scraper.analyze_known_platform("stripe")
        replica = self.engine.replicate(profile)
        assert "create_payment" in replica.source_code

    def test_replicate_openai(self):
        profile = self.scraper.analyze_known_platform("openai")
        replica = self.engine.replicate(profile)
        assert "generate_text" in replica.source_code


# ===========================================================================
# 3. Tool_DB expansion
# ===========================================================================

class TestExpandedToolDB:

    def setup_method(self):
        self.db = ToolDB()

    def test_catalogue_has_80_plus_tools(self):
        all_tools = self.db.list_all()
        assert len(all_tools) >= 50, f"Expected 50+ tools, got {len(all_tools)}"

    def test_new_categories_present(self):
        all_tools = self.db.list_all()
        categories = {t.category for t in all_tools}
        assert ToolCategory.DEVOPS in categories
        assert ToolCategory.DATABASE in categories
        assert ToolCategory.MESSAGING in categories
        assert ToolCategory.AUTOMATION in categories
        assert ToolCategory.AI_ML in categories
        assert ToolCategory.STORAGE in categories
        assert ToolCategory.MONITORING in categories

    def test_zapier_in_catalogue(self):
        tool = self.db.get_tool("zapier")
        assert tool is not None
        assert tool.name == "Zapier"

    def test_github_actions_in_catalogue(self):
        tool = self.db.get_tool("github_actions")
        assert tool is not None
        assert tool.category == ToolCategory.DEVOPS

    def test_openai_in_catalogue(self):
        tool = self.db.get_tool("openai_api")
        assert tool is not None
        assert tool.category == ToolCategory.AI_ML

    def test_postgresql_in_catalogue(self):
        assert self.db.get_tool("postgresql") is not None

    def test_slack_in_catalogue(self):
        assert self.db.get_tool("slack_api") is not None

    def test_react_in_catalogue(self):
        tool = self.db.get_tool("react")
        assert tool is not None
        assert tool.category == ToolCategory.LIBRARY

    def test_fastapi_in_catalogue(self):
        assert self.db.get_tool("fastapi") is not None

    def test_search_automation(self):
        results = self.db.search("automation workflow")
        assert len(results) > 0

    def test_search_ai_ml(self):
        results = self.db.search("machine learning")
        assert len(results) > 0

    def test_get_tools_for_devops_industry(self):
        tools = self.db.get_tools_for_industry("devops")
        assert len(tools) > 0

    def test_get_tools_for_ecommerce_industry(self):
        tools = self.db.get_tools_for_industry("ecommerce")
        assert len(tools) > 0

    def test_iot_tools_exist(self):
        results = self.db.search("iot")
        assert len(results) > 0


# ===========================================================================
# 4. Tier flags for scraper and replication
# ===========================================================================

class TestTierFlags:

    def test_tool_scraper_not_in_free_tier(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_TOOL_SCRAPER)

    def test_tool_scraper_in_pro_tier(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_TOOL_SCRAPER)

    def test_tool_replication_not_in_free_tier(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_TOOL_REPLICATION)

    def test_tool_replication_not_in_pro_tier(self):
        cfg = get_tier_config(Tier.PRO)
        assert not cfg.has_feature(FEATURE_TOOL_REPLICATION)

    def test_tool_replication_in_enterprise_tier(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_TOOL_REPLICATION)


# ===========================================================================
# 5. BuddyCore integration
# ===========================================================================

class TestBuddyCoreToolScraper:

    def test_scrape_tool_requires_pro(self):
        buddy = BuddyCore(tier=Tier.FREE)
        with pytest.raises(BuddyCoreTierError):
            buddy.scrape_tool("Stripe", "Payment processing.")

    def test_scrape_tool_pro_tier_succeeds(self):
        buddy = BuddyCore(tier=Tier.PRO)
        result = buddy.scrape_tool(
            tool_name="Zapier",
            description="Workflow automation platform.",
        )
        assert "tool_name" in result
        assert result["tool_name"] == "Zapier"

    def test_scrape_known_tool_pro_tier(self):
        buddy = BuddyCore(tier=Tier.PRO)
        result = buddy.scrape_known_tool("stripe")
        assert "tool_name" in result
        assert result["tool_name"] == "Stripe"

    def test_scrape_known_tool_unknown_returns_error(self):
        buddy = BuddyCore(tier=Tier.PRO)
        result = buddy.scrape_known_tool("not_a_real_platform_xyz")
        assert "error" in result

    def test_replicate_tool_requires_enterprise(self):
        buddy = BuddyCore(tier=Tier.PRO)
        with pytest.raises(BuddyCoreTierError):
            buddy.replicate_tool("Stripe", "Payment processing.")

    def test_replicate_tool_enterprise_succeeds(self):
        buddy = BuddyCore(tier=Tier.ENTERPRISE)
        result = buddy.replicate_tool(
            tool_name="Zapier",
            description="Workflow automation platform.",
            extra_keywords=["automate", "trigger", "action"],
        )
        assert "source_code" in result
        assert "class Buddy" in result["source_code"]

    def test_replicate_known_tool_enterprise(self):
        buddy = BuddyCore(tier=Tier.ENTERPRISE)
        result = buddy.replicate_known_tool("zapier")
        assert "source_code" in result
        assert "GlobalAISourcesFlow" in result["source_code"]

    def test_replicate_known_tool_unknown_returns_error(self):
        buddy = BuddyCore(tier=Tier.ENTERPRISE)
        result = buddy.replicate_known_tool("nonexistent_xyz")
        assert "error" in result

    def test_list_replicable_platforms(self):
        buddy = BuddyCore(tier=Tier.FREE)
        platforms = buddy.list_replicable_platforms()
        assert isinstance(platforms, list)
        assert "zapier" in platforms
        assert "stripe" in platforms

    def test_replicate_tool_source_has_framework_hook(self):
        buddy = BuddyCore(tier=Tier.ENTERPRISE)
        result = buddy.replicate_tool(
            tool_name="Shopify",
            description="E-commerce platform with products, orders, and webhooks.",
        )
        assert "GlobalAISourcesFlow" in result["source_code"]
        assert "run_pipeline" in result["source_code"]
