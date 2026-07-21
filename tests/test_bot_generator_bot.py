"""Tests for bots/bot_generator_bot/ — BotGeneratorBot and supporting modules.

Validates GLOBAL AI SOURCES FLOW framework compliance and all bot generation
pipeline stages: parser, tool injector, template engine, deployer, and the
main BotGeneratorBot orchestrator.
"""
import sys
import os
import tempfile

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.bot_generator_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    list_tiers,
    get_upgrade_path,
    FEATURE_BASIC_GENERATION,
    FEATURE_TOOL_INJECTION,
    FEATURE_AUTO_DEPLOY,
    FEATURE_CUSTOM_DNA,
)
from bots.bot_generator_bot.parser import BotParser, BotIntent, _slugify
from bots.bot_generator_bot.tool_injector import ToolInjector
from bots.bot_generator_bot.template_engine import TemplateEngine
from bots.bot_generator_bot.deployer import BotDeployer
from bots.bot_generator_bot.bot_generator_bot import (
    BotGeneratorBot,
    BotGeneratorTierError,
)


# ---------------------------------------------------------------------------
# Framework compliance
# ---------------------------------------------------------------------------

class TestFrameworkCompliance:
    def test_bot_generator_bot_imports_globalaisourcesflow(self):
        """bot_generator_bot.py must import GlobalAISourcesFlow."""
        bot_file = os.path.join(
            REPO_ROOT, "bots", "bot_generator_bot", "bot_generator_bot.py"
        )
        text = open(bot_file).read()
        assert "GlobalAISourcesFlow" in text

    def test_parser_has_framework_marker(self):
        parser_file = os.path.join(
            REPO_ROOT, "bots", "bot_generator_bot", "parser.py"
        )
        text = open(parser_file).read()
        assert any(
            marker in text
            for marker in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW", "global_ai_sources_flow")
        )

    def test_tool_injector_has_framework_marker(self):
        injector_file = os.path.join(
            REPO_ROOT, "bots", "bot_generator_bot", "tool_injector.py"
        )
        text = open(injector_file).read()
        assert any(
            marker in text
            for marker in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW", "global_ai_sources_flow")
        )

    def test_template_engine_has_framework_marker(self):
        engine_file = os.path.join(
            REPO_ROOT, "bots", "bot_generator_bot", "template_engine.py"
        )
        text = open(engine_file).read()
        assert any(
            marker in text
            for marker in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW", "global_ai_sources_flow")
        )

    def test_deployer_has_framework_marker(self):
        deployer_file = os.path.join(
            REPO_ROOT, "bots", "bot_generator_bot", "deployer.py"
        )
        text = open(deployer_file).read()
        assert any(
            marker in text
            for marker in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW", "global_ai_sources_flow")
        )


# ---------------------------------------------------------------------------
# Tiers
# ---------------------------------------------------------------------------

class TestTiers:
    def test_three_tiers_exist(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_free_tier_price(self):
        config = get_tier_config(Tier.FREE)
        assert config.price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        config = get_tier_config(Tier.PRO)
        assert config.price_usd_monthly == 49.0

    def test_enterprise_tier_price(self):
        config = get_tier_config(Tier.ENTERPRISE)
        assert config.price_usd_monthly == 199.0

    def test_free_has_bot_limit(self):
        config = get_tier_config(Tier.FREE)
        assert config.max_bots_per_month == 3

    def test_pro_has_bot_limit(self):
        config = get_tier_config(Tier.PRO)
        assert config.max_bots_per_month == 30

    def test_enterprise_unlimited_bots(self):
        config = get_tier_config(Tier.ENTERPRISE)
        assert config.max_bots_per_month is None
        assert config.is_unlimited_bots()

    def test_free_has_basic_generation(self):
        config = get_tier_config(Tier.FREE)
        assert config.has_feature(FEATURE_BASIC_GENERATION)

    def test_free_lacks_tool_injection(self):
        config = get_tier_config(Tier.FREE)
        assert not config.has_feature(FEATURE_TOOL_INJECTION)

    def test_pro_has_tool_injection(self):
        config = get_tier_config(Tier.PRO)
        assert config.has_feature(FEATURE_TOOL_INJECTION)

    def test_pro_has_auto_deploy(self):
        config = get_tier_config(Tier.PRO)
        assert config.has_feature(FEATURE_AUTO_DEPLOY)

    def test_enterprise_has_custom_dna(self):
        config = get_tier_config(Tier.ENTERPRISE)
        assert config.has_feature(FEATURE_CUSTOM_DNA)

    def test_upgrade_from_free_is_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_from_pro_is_enterprise(self):
        upgrade = get_upgrade_path(Tier.PRO)
        assert upgrade is not None
        assert upgrade.tier == Tier.ENTERPRISE

    def test_no_upgrade_from_enterprise(self):
        upgrade = get_upgrade_path(Tier.ENTERPRISE)
        assert upgrade is None


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class TestBotParser:
    def setup_method(self):
        self.parser = BotParser()

    def test_returns_bot_intent(self):
        intent = self.parser.parse("Make a real estate lead bot")
        assert isinstance(intent, BotIntent)

    def test_detects_real_estate_industry(self):
        intent = self.parser.parse("Build a real estate lead bot")
        assert intent.industry == "real_estate"

    def test_detects_dental_industry(self):
        intent = self.parser.parse("Make a dentist lead bot")
        assert intent.industry == "dental"

    def test_detects_legal_industry(self):
        intent = self.parser.parse("Build a lawyer outreach bot")
        assert intent.industry == "legal"

    def test_detects_fitness_industry(self):
        intent = self.parser.parse("Create a fitness gym bot")
        assert intent.industry == "fitness"

    def test_unknown_industry_defaults_to_general(self):
        intent = self.parser.parse("xyz123 bot")
        assert intent.industry == "general"

    def test_detects_lead_generation_goal(self):
        intent = self.parser.parse("Find leads for real estate")
        assert intent.goal == "generate_leads"

    def test_detects_analytics_goal(self):
        intent = self.parser.parse("Build an analytics dashboard bot")
        assert intent.goal == "track_analytics"

    def test_default_goal_is_generate_leads(self):
        intent = self.parser.parse("xyz123 random bot")
        assert intent.goal == "generate_leads"

    def test_confidence_above_zero(self):
        intent = self.parser.parse("Make a dental lead bot")
        assert intent.confidence > 0.0

    def test_confidence_max_one(self):
        intent = self.parser.parse("Make a dental analytics bot")
        assert intent.confidence <= 1.0

    def test_tools_is_list(self):
        intent = self.parser.parse("Make a real estate lead bot")
        assert isinstance(intent.tools, list)

    def test_monetization_has_default(self):
        intent = self.parser.parse("Make a real estate lead bot")
        assert isinstance(intent.monetization, list)
        assert len(intent.monetization) > 0

    def test_to_dna_returns_dict(self):
        intent = self.parser.parse("Make a real estate lead bot")
        dna = intent.to_dna()
        assert isinstance(dna, dict)
        assert "industry" in dna
        assert "goal" in dna
        assert "tools" in dna
        assert "bot_name" in dna

    def test_to_dna_industry_matches(self):
        intent = self.parser.parse("Make a dental lead bot")
        dna = intent.to_dna()
        assert dna["industry"] == "dental"


class TestSlugify:
    def test_lowercase(self):
        assert _slugify("Hello World") == "hello_world"

    def test_spaces_to_underscore(self):
        assert _slugify("real estate") == "real_estate"

    def test_removes_special_chars(self):
        assert _slugify("hello-world!") == "helloworld"


# ---------------------------------------------------------------------------
# Tool Injector
# ---------------------------------------------------------------------------

class TestToolInjector:
    def setup_method(self):
        self.injector = ToolInjector()

    def test_list_available_tools_nonempty(self):
        tools = self.injector.list_available_tools()
        assert len(tools) > 0

    def test_list_tool_has_name(self):
        tools = self.injector.list_available_tools()
        for tool in tools:
            assert "name" in tool

    def test_list_tool_has_description(self):
        tools = self.injector.list_available_tools()
        for tool in tools:
            assert "description" in tool

    def test_list_tool_has_category(self):
        tools = self.injector.list_available_tools()
        for tool in tools:
            assert "category" in tool

    def test_get_tool_google_maps(self):
        tool = self.injector.get_tool("google_maps")
        assert tool is not None
        assert tool.name == "google_maps"

    def test_get_tool_unknown_returns_none(self):
        tool = self.injector.get_tool("nonexistent_tool")
        assert tool is None

    def test_inject_adds_resolved_tools(self):
        dna = {"industry": "real_estate", "tools": ["google_maps", "email_finder"]}
        result = self.injector.inject(dna)
        assert "resolved_tools" in result
        assert len(result["resolved_tools"]) == 2

    def test_inject_unknown_tool_goes_to_missing(self):
        dna = {"industry": "general", "tools": ["unknown_tool_xyz"]}
        result = self.injector.inject(dna)
        assert "unknown_tool_xyz" in result["missing_tools"]

    def test_inject_preserves_original_keys(self):
        dna = {"industry": "dental", "goal": "generate_leads", "tools": ["google_maps"]}
        result = self.injector.inject(dna)
        assert result["industry"] == "dental"
        assert result["goal"] == "generate_leads"

    def test_inject_resolved_tool_has_stub(self):
        dna = {"industry": "real_estate", "tools": ["google_maps"]}
        result = self.injector.inject(dna)
        tool = result["resolved_tools"][0]
        assert "stub" in tool
        assert len(tool["stub"]) > 0

    def test_tools_for_category_scraping(self):
        scraping = self.injector.tools_for_category("scraping")
        assert len(scraping) > 0
        for t in scraping:
            assert t.category == "scraping"

    def test_tools_for_category_payment(self):
        payment = self.injector.tools_for_category("payment")
        assert len(payment) > 0


# ---------------------------------------------------------------------------
# Template Engine
# ---------------------------------------------------------------------------

class TestTemplateEngine:
    def setup_method(self):
        self.engine = TemplateEngine()

    def _make_dna(self, **kwargs):
        base = {
            "industry": "real_estate",
            "goal": "generate_leads",
            "bot_name": "real_estate_generate_leads_bot",
            "tools": ["google_maps"],
            "monetization": ["subscriptions"],
            "resolved_tools": [],
        }
        base.update(kwargs)
        return base

    def test_build_returns_dict(self):
        result = self.engine.build(self._make_dna())
        assert isinstance(result, dict)

    def test_build_has_source(self):
        result = self.engine.build(self._make_dna())
        assert "source" in result
        assert len(result["source"]) > 0

    def test_build_has_bot_name(self):
        result = self.engine.build(self._make_dna())
        assert result["bot_name"] == "real_estate_generate_leads_bot"

    def test_build_has_class_name(self):
        result = self.engine.build(self._make_dna())
        assert result["class_name"] == "RealEstateGenerateLeadsBot"

    def test_build_has_filename(self):
        result = self.engine.build(self._make_dna())
        assert result["filename"] == "real_estate_generate_leads_bot.py"

    def test_build_has_generated_at(self):
        result = self.engine.build(self._make_dna())
        assert "generated_at" in result

    def test_source_contains_class_definition(self):
        result = self.engine.build(self._make_dna())
        assert "class RealEstateGenerateLeadsBot" in result["source"]

    def test_source_contains_framework_reference(self):
        result = self.engine.build(self._make_dna())
        assert any(
            marker in result["source"]
            for marker in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW")
        )

    def test_source_contains_run_method(self):
        result = self.engine.build(self._make_dna())
        assert "def run(" in result["source"]

    def test_source_contains_process_method(self):
        result = self.engine.build(self._make_dna())
        assert "def process(" in result["source"]

    def test_source_contains_get_summary(self):
        result = self.engine.build(self._make_dna())
        assert "def get_summary(" in result["source"]

    def test_source_with_injected_tools_has_stubs(self):
        injector = ToolInjector()
        dna = self._make_dna(tools=["google_maps", "email_finder"])
        dna = injector.inject(dna)
        result = self.engine.build(dna)
        assert "def scrape_google_maps" in result["source"]


# ---------------------------------------------------------------------------
# Deployer
# ---------------------------------------------------------------------------

class TestBotDeployer:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.deployer = BotDeployer(bots_root=self.tmp)
        self.engine = TemplateEngine()

    def _make_build_result(self, bot_name="test_deploy_bot"):
        dna = {
            "industry": "dental",
            "goal": "generate_leads",
            "bot_name": bot_name,
            "tools": [],
            "monetization": ["subscriptions"],
            "resolved_tools": [],
        }
        return self.engine.build(dna)

    def test_dry_run_returns_dict(self):
        build_result = self._make_build_result()
        result = self.deployer.deploy(build_result, dry_run=True)
        assert isinstance(result, dict)

    def test_dry_run_does_not_create_files(self):
        build_result = self._make_build_result("no_write_bot")
        self.deployer.deploy(build_result, dry_run=True)
        bot_dir = os.path.join(self.tmp, "no_write_bot")
        assert not os.path.exists(bot_dir)

    def test_deploy_creates_directory(self):
        build_result = self._make_build_result("create_dir_bot")
        self.deployer.deploy(build_result, dry_run=False)
        bot_dir = os.path.join(self.tmp, "create_dir_bot")
        assert os.path.isdir(bot_dir)

    def test_deploy_creates_bot_file(self):
        build_result = self._make_build_result("file_bot")
        self.deployer.deploy(build_result, dry_run=False)
        bot_file = os.path.join(self.tmp, "file_bot", "file_bot.py")
        assert os.path.isfile(bot_file)

    def test_deploy_creates_init_file(self):
        build_result = self._make_build_result("init_bot")
        self.deployer.deploy(build_result, dry_run=False)
        init_file = os.path.join(self.tmp, "init_bot", "__init__.py")
        assert os.path.isfile(init_file)

    def test_deploy_creates_config_json(self):
        build_result = self._make_build_result("config_bot")
        self.deployer.deploy(build_result, dry_run=False)
        config_file = os.path.join(self.tmp, "config_bot", "bot_config.json")
        assert os.path.isfile(config_file)

    def test_deploy_result_has_deployed_path(self):
        build_result = self._make_build_result("path_bot")
        result = self.deployer.deploy(build_result, dry_run=True)
        assert "deployed_path" in result

    def test_deploy_result_has_files_written(self):
        build_result = self._make_build_result("files_bot")
        result = self.deployer.deploy(build_result, dry_run=True)
        assert "files_written" in result
        assert len(result["files_written"]) == 4

    def test_deploy_result_dry_run_flag(self):
        build_result = self._make_build_result("flag_bot")
        result = self.deployer.deploy(build_result, dry_run=True)
        assert result["dry_run"] is True

    def test_list_deployed_bots_returns_list(self):
        bots = self.deployer.list_deployed_bots()
        assert isinstance(bots, list)

    def test_get_deploy_log_returns_list(self):
        build_result = self._make_build_result("log_bot")
        self.deployer.deploy(build_result, dry_run=True)
        log = self.deployer.get_deploy_log()
        assert isinstance(log, list)
        assert len(log) == 1


# ---------------------------------------------------------------------------
# BotGeneratorBot (full pipeline)
# ---------------------------------------------------------------------------

class TestBotGeneratorBotInstantiation:
    def test_default_tier_is_free(self):
        bot = BotGeneratorBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = BotGeneratorBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = BotGeneratorBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_has_parser(self):
        bot = BotGeneratorBot()
        assert bot._parser is not None

    def test_has_injector(self):
        bot = BotGeneratorBot()
        assert bot._injector is not None

    def test_has_engine(self):
        bot = BotGeneratorBot()
        assert bot._engine is not None

    def test_has_deployer(self):
        bot = BotGeneratorBot()
        assert bot._deployer is not None

    def test_initial_bots_generated_is_zero(self):
        bot = BotGeneratorBot()
        assert bot._bots_generated == 0


class TestBotGeneratorBotGenerate:
    def test_free_generate_returns_dict(self):
        bot = BotGeneratorBot(tier=Tier.FREE)
        result = bot.generate("Make a real estate lead bot")
        assert isinstance(result, dict)

    def test_result_has_source(self):
        bot = BotGeneratorBot(tier=Tier.FREE)
        result = bot.generate("Make a dental lead bot")
        assert "source" in result
        assert len(result["source"]) > 0

    def test_result_has_intent(self):
        bot = BotGeneratorBot(tier=Tier.FREE)
        result = bot.generate("Make a dental lead bot")
        assert "intent" in result
        assert result["intent"]["industry"] == "dental"

    def test_result_has_tier(self):
        bot = BotGeneratorBot(tier=Tier.FREE)
        result = bot.generate("Make a dental lead bot")
        assert result["tier"] == "free"

    def test_result_has_build_result(self):
        bot = BotGeneratorBot(tier=Tier.FREE)
        result = bot.generate("Make a dental lead bot")
        assert "build_result" in result
        assert "bot_name" in result["build_result"]

    def test_bots_generated_increments(self):
        bot = BotGeneratorBot(tier=Tier.FREE)
        bot.generate("Make a lead bot")
        assert bot._bots_generated == 1
        bot.generate("Make a marketing bot")
        assert bot._bots_generated == 2

    def test_generation_log_grows(self):
        bot = BotGeneratorBot(tier=Tier.FREE)
        bot.generate("Make a lead bot")
        log = bot.get_generation_log()
        assert len(log) == 1

    def test_free_tier_no_tool_injection(self):
        bot = BotGeneratorBot(tier=Tier.FREE)
        result = bot.generate("Make a real estate lead bot")
        assert result["dna"]["resolved_tools"] == []

    def test_pro_tier_has_tool_injection(self):
        bot = BotGeneratorBot(tier=Tier.PRO)
        result = bot.generate("Make a real estate lead bot")
        assert len(result["dna"]["resolved_tools"]) > 0

    def test_enterprise_custom_dna(self):
        bot = BotGeneratorBot(tier=Tier.ENTERPRISE)
        custom = {
            "industry": "legal",
            "goal": "generate_leads",
            "bot_name": "law_firm_leads_bot",
            "tools": [],
            "monetization": ["subscriptions"],
        }
        result = bot.generate("", custom_dna=custom)
        assert result["dna"]["industry"] == "legal"

    def test_free_cannot_use_custom_dna(self):
        bot = BotGeneratorBot(tier=Tier.FREE)
        custom = {"industry": "legal", "goal": "generate_leads", "bot_name": "x", "tools": []}
        with pytest.raises(BotGeneratorTierError):
            bot.generate("", custom_dna=custom)

    def test_free_monthly_limit_enforced(self):
        bot = BotGeneratorBot(tier=Tier.FREE)
        for _ in range(3):
            bot.generate("Make a lead bot")
        with pytest.raises(BotGeneratorTierError):
            bot.generate("Make another bot")

    def test_enterprise_no_monthly_limit(self):
        bot = BotGeneratorBot(tier=Tier.ENTERPRISE)
        for _ in range(5):
            bot.generate("Make a lead bot")
        assert bot._bots_generated == 5

    def test_pro_deploy_dry_run(self):
        tmp = tempfile.mkdtemp()
        bot = BotGeneratorBot(tier=Tier.PRO, bots_root=tmp)
        result = bot.generate("Make a real estate lead bot", dry_run=True)
        assert result["deploy_result"] is not None
        assert result["deploy_result"]["dry_run"] is True

    def test_free_cannot_deploy(self):
        bot = BotGeneratorBot(tier=Tier.FREE)
        with pytest.raises(BotGeneratorTierError):
            bot.generate("Make a real estate lead bot", deploy=True)


class TestBotGeneratorBotHelpers:
    def test_list_available_tools_nonempty(self):
        bot = BotGeneratorBot()
        tools = bot.list_available_tools()
        assert len(tools) > 0

    def test_get_summary_returns_dict(self):
        bot = BotGeneratorBot()
        summary = bot.get_summary()
        assert isinstance(summary, dict)

    def test_get_summary_has_tier(self):
        bot = BotGeneratorBot(tier=Tier.PRO)
        summary = bot.get_summary()
        assert summary["tier"] == "pro"

    def test_get_summary_has_bots_generated(self):
        bot = BotGeneratorBot()
        bot.generate("Make a lead bot")
        summary = bot.get_summary()
        assert summary["bots_generated_this_session"] == 1

    def test_get_summary_remaining_decrements(self):
        bot = BotGeneratorBot(tier=Tier.FREE)
        bot.generate("Make a lead bot")
        summary = bot.get_summary()
        assert summary["remaining_this_month"] == 2

    def test_enterprise_summary_remaining_is_unlimited(self):
        bot = BotGeneratorBot(tier=Tier.ENTERPRISE)
        summary = bot.get_summary()
        assert summary["remaining_this_month"] == "unlimited"


class TestBotGeneratorBotChat:
    def test_chat_returns_dict(self):
        bot = BotGeneratorBot()
        result = bot.chat("hello")
        assert isinstance(result, dict)

    def test_chat_make_triggers_generation(self):
        bot = BotGeneratorBot()
        result = bot.chat("Make a dental bot")
        assert "data" in result
        assert bot._bots_generated == 1

    def test_chat_tools_query(self):
        bot = BotGeneratorBot()
        result = bot.chat("What tools are available?")
        assert "data" in result
        assert isinstance(result["data"], list)

    def test_chat_summary_query(self):
        bot = BotGeneratorBot()
        result = bot.chat("Show me the summary")
        assert "data" in result

    def test_process_delegates_to_chat(self):
        bot = BotGeneratorBot()
        result = bot.process({"command": "hello"})
        assert isinstance(result, dict)

    def test_process_empty_command(self):
        bot = BotGeneratorBot()
        result = bot.process({})
        assert isinstance(result, dict)
        assert "message" in result
