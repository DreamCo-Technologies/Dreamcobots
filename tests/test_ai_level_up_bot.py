"""
Tests for bots/ai_level_up_bot/

Covers all modules:
  1. Tiers
  2. AI Companies Database
  3. AI Course Engine
  4. Token Marketplace
  5. AI Skill Tree
  6. AI Agents Generator
  7. AILevelUpBot main class (integration)
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from bots.ai_level_up_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_AI_COMPANIES_DATABASE,
    FEATURE_AI_COURSE_ENGINE,
    FEATURE_TOKEN_MARKETPLACE,
    FEATURE_AI_SKILL_TREE,
    FEATURE_AI_AGENTS_GENERATOR,
    FEATURE_FULL_DATABASE,
    FEATURE_API_ACCESS,
    FEATURE_WHITE_LABEL,
)
from bots.ai_level_up_bot.ai_companies_database import AICompanyDatabase, AICompany
from bots.ai_level_up_bot.ai_course_engine import AICourseEngine, MODE_VIDEO, MODE_CODING_LAB
from bots.ai_level_up_bot.token_marketplace import TokenMarketplace, MARKUP_PERCENTAGE
from bots.ai_level_up_bot.ai_skill_tree import AISkillTree, NodeStatus
from bots.ai_level_up_bot.ai_agents_generator import AIAgentsGenerator, AgentStatus
from bots.ai_level_up_bot.ai_level_up_bot import AILevelUpBot, AILevelUpTierError


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_starter_price(self):
        cfg = get_tier_config(Tier.STARTER)
        assert cfg.price_usd_monthly == 29.0

    def test_pro_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 99.0

    def test_enterprise_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 399.0

    def test_enterprise_unlimited_tokens(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited_tokens()

    def test_enterprise_unlimited_companies(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited_companies()

    def test_starter_has_limited_tokens(self):
        cfg = get_tier_config(Tier.STARTER)
        assert cfg.max_tokens_per_day == 5

    def test_starter_has_database_feature(self):
        cfg = get_tier_config(Tier.STARTER)
        assert cfg.has_feature(FEATURE_AI_COMPANIES_DATABASE)

    def test_starter_lacks_api_access(self):
        cfg = get_tier_config(Tier.STARTER)
        assert not cfg.has_feature(FEATURE_API_ACCESS)

    def test_enterprise_has_all_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feature in [
            FEATURE_AI_COMPANIES_DATABASE,
            FEATURE_AI_COURSE_ENGINE,
            FEATURE_TOKEN_MARKETPLACE,
            FEATURE_AI_SKILL_TREE,
            FEATURE_AI_AGENTS_GENERATOR,
            FEATURE_FULL_DATABASE,
            FEATURE_API_ACCESS,
            FEATURE_WHITE_LABEL,
        ]:
            assert cfg.has_feature(feature), f"Missing: {feature}"

    def test_upgrade_path_starter_to_pro(self):
        upgrade = get_upgrade_path(Tier.STARTER)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_path_pro_to_enterprise(self):
        upgrade = get_upgrade_path(Tier.PRO)
        assert upgrade is not None
        assert upgrade.tier == Tier.ENTERPRISE

    def test_upgrade_path_enterprise_is_none(self):
        upgrade = get_upgrade_path(Tier.ENTERPRISE)
        assert upgrade is None

    def test_tier_catalogue_keys(self):
        for tier in Tier:
            assert tier.value in TIER_CATALOGUE

    def test_pro_max_course_levels(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.max_course_levels == 7

    def test_enterprise_max_course_levels(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_course_levels == 10


# ===========================================================================
# 2. AI Companies Database
# ===========================================================================

class TestAICompaniesDatabase:
    def setup_method(self):
        self.db = AICompanyDatabase()

    def test_has_100_plus_companies(self):
        assert self.db.count() >= 100

    def test_get_openai(self):
        company = self.db.get_company("OpenAI")
        assert company is not None
        assert company.company_name == "OpenAI"
        assert company.region == "USA"
        assert company.api_available is True

    def test_get_anthropic(self):
        company = self.db.get_company("Anthropic")
        assert company is not None
        assert "Claude" in company.tools

    def test_get_company_case_insensitive(self):
        company = self.db.get_company("openai")
        assert company is not None
        assert company.company_name == "OpenAI"

    def test_get_nonexistent_company_returns_none(self):
        result = self.db.get_company("NonExistentCorp")
        assert result is None

    def test_get_tool_chatgpt(self):
        company = self.db.get_tool("ChatGPT")
        assert company is not None
        assert company.company_name == "OpenAI"

    def test_get_tool_case_insensitive(self):
        company = self.db.get_tool("chatgpt")
        assert company is not None

    def test_get_tool_partial_match(self):
        company = self.db.get_tool("DALL")
        assert company is not None

    def test_get_tool_not_found_returns_none(self):
        result = self.db.get_tool("ZZZ_NONEXISTENT_TOOL")
        assert result is None

    def test_get_by_category_core_ai_models(self):
        companies = self.db.get_by_category("Core AI Models")
        names = [c.company_name for c in companies]
        assert "OpenAI" in names
        assert "Anthropic" in names
        assert "Google DeepMind" in names

    def test_get_by_category_coding_platforms(self):
        companies = self.db.get_by_category("AI Coding Platforms")
        names = [c.company_name for c in companies]
        assert "GitHub" in names
        assert "DreamCo" in names

    def test_get_by_category_image_generation(self):
        companies = self.db.get_by_category("AI Image Generation")
        names = [c.company_name for c in companies]
        assert "Midjourney" in names
        assert "Stability AI" in names

    def test_get_by_category_video_generation(self):
        companies = self.db.get_by_category("AI Video Generation")
        names = [c.company_name for c in companies]
        assert "Runway" in names
        assert "Pika Labs" in names

    def test_get_by_category_voice_audio(self):
        companies = self.db.get_by_category("AI Voice & Audio")
        names = [c.company_name for c in companies]
        assert "ElevenLabs" in names
        assert "PlayHT" in names

    def test_get_by_category_music(self):
        companies = self.db.get_by_category("AI Music")
        names = [c.company_name for c in companies]
        assert "Suno AI" in names
        assert "Boomy" in names

    def test_get_by_category_productivity(self):
        companies = self.db.get_by_category("AI Productivity Tools")
        names = [c.company_name for c in companies]
        assert "Grammarly" in names
        assert "Notion" in names

    def test_get_by_category_automation(self):
        companies = self.db.get_by_category("AI Agents & Automation")
        names = [c.company_name for c in companies]
        assert "Zapier" in names
        assert "UiPath" in names

    def test_get_by_category_infrastructure(self):
        companies = self.db.get_by_category("AI Infrastructure Platforms")
        names = [c.company_name for c in companies]
        assert "NVIDIA" in names
        assert "Hugging Face" in names

    def test_get_by_category_chinese_companies(self):
        companies = self.db.get_by_category("Major Chinese AI Companies")
        names = [c.company_name for c in companies]
        assert "Baidu" in names
        assert "Alibaba" in names
        assert "Tencent" in names

    def test_get_by_category_european_leaders(self):
        companies = self.db.get_by_category("European AI Leaders")
        names = [c.company_name for c in companies]
        assert "Aleph Alpha" in names
        assert "Silo AI" in names

    def test_get_by_category_science_healthcare(self):
        companies = self.db.get_by_category("AI for Science & Healthcare")
        names = [c.company_name for c in companies]
        assert "Insilico Medicine" in names
        assert "Deep Genomics" in names
        assert "Tempus" in names

    def test_get_by_region_usa(self):
        usa = self.db.get_by_region("USA")
        assert len(usa) >= 20

    def test_get_by_region_china(self):
        china = self.db.get_by_region("China")
        names = [c.company_name for c in china]
        assert "Baidu" in names
        assert "DeepSeek" in names

    def test_get_by_region_europe(self):
        europe = self.db.get_by_region("Europe")
        names = [c.company_name for c in europe]
        assert "Mistral AI" in names

    def test_get_with_api(self):
        api_companies = self.db.get_with_api()
        assert len(api_companies) >= 50
        for company in api_companies:
            assert company.api_available is True

    def test_get_by_pricing_freemium(self):
        freemium = self.db.get_by_pricing("freemium")
        assert len(freemium) >= 10

    def test_get_by_pricing_token_based(self):
        token = self.db.get_by_pricing("token-based")
        assert len(token) >= 5

    def test_list_categories_returns_sorted_list(self):
        categories = self.db.list_categories()
        assert isinstance(categories, list)
        assert len(categories) >= 10
        assert categories == sorted(categories)

    def test_list_regions_returns_sorted_list(self):
        regions = self.db.list_regions()
        assert isinstance(regions, list)
        assert "USA" in regions
        assert "China" in regions
        assert regions == sorted(regions)

    def test_add_company(self):
        initial = self.db.count()
        new_co = AICompany(
            company_name="TestCorp AI",
            category="Core AI Models",
            tools=["TestTool"],
            pricing="freemium",
            region="USA",
            api_available=True,
        )
        self.db.add_company(new_co)
        assert self.db.count() == initial + 1
        assert self.db.get_company("TestCorp AI") is not None

    def test_to_dict_list(self):
        data = self.db.to_dict_list()
        assert isinstance(data, list)
        assert len(data) >= 100
        required_fields = {"company_name", "category", "tools", "pricing", "region", "api_available"}
        for entry in data[:5]:
            assert required_fields.issubset(entry.keys())

    def test_company_to_dict_structure(self):
        company = self.db.get_company("OpenAI")
        d = company.to_dict()
        assert d["company_name"] == "OpenAI"
        assert isinstance(d["tools"], list)
        assert isinstance(d["api_available"], bool)

    def test_extra_companies_merged(self):
        extra = [
            AICompany(
                company_name="ExtraAI",
                category="Core AI Models",
                tools=["ExtraTool"],
                pricing="free",
                region="USA",
                api_available=False,
            )
        ]
        db2 = AICompanyDatabase(extra_companies=extra)
        assert db2.get_company("ExtraAI") is not None

    def test_deepseek_is_chinese(self):
        co = self.db.get_company("DeepSeek")
        assert co.region == "China"

    def test_mistral_is_european(self):
        co = self.db.get_company("Mistral AI")
        assert co.region == "Europe"

    def test_stability_ai_is_open_source(self):
        co = self.db.get_company("Stability AI")
        assert co.pricing == "open-source"

    def test_meta_platforms_open_source(self):
        co = self.db.get_company("Meta Platforms")
        assert co.pricing == "open-source"

    def test_nvidia_api_available(self):
        co = self.db.get_company("NVIDIA")
        assert co.api_available is True

    def test_midjourney_no_api(self):
        co = self.db.get_company("Midjourney")
        assert co.api_available is False


# ===========================================================================
# 3. AI Course Engine
# ===========================================================================

class TestAICourseEngine:
    def setup_method(self):
        self.engine = AICourseEngine(max_level=10)

    def test_total_levels_is_ten(self):
        assert self.engine.total_levels() == 10

    def test_get_level_1_basics(self):
        lvl = self.engine.get_level(1)
        assert lvl is not None
        assert lvl.level == 1
        assert "AI Basics" in lvl.name

    def test_get_level_2_prompt_engineering(self):
        lvl = self.engine.get_level(2)
        assert lvl is not None
        assert "Prompt" in lvl.name

    def test_get_level_10_superintelligence(self):
        lvl = self.engine.get_level(10)
        assert lvl is not None
        assert "Superintelligence" in lvl.name

    def test_get_level_returns_none_for_out_of_range(self):
        assert self.engine.get_level(11) is None
        assert self.engine.get_level(0) is None

    def test_max_level_limits_access(self):
        limited = AICourseEngine(max_level=3)
        assert limited.get_level(3) is not None
        assert limited.get_level(4) is None

    def test_list_accessible_levels_respects_max(self):
        limited = AICourseEngine(max_level=5)
        levels = limited.list_accessible_levels()
        assert len(levels) == 5
        assert all(lvl.level <= 5 for lvl in levels)

    def test_level_has_modules(self):
        for i in range(1, 11):
            lvl = self.engine.get_level(i)
            assert len(lvl.modules) >= 3, f"Level {i} has too few modules"

    def test_level_to_dict_structure(self):
        lvl = self.engine.get_level(1)
        d = lvl.to_dict()
        assert "level" in d
        assert "name" in d
        assert "modules" in d
        assert "certification" in d
        assert "total_duration_minutes" in d

    def test_certification_names(self):
        cert = self.engine.get_certification(10)
        assert cert == "DreamCo AI Master Certification"

    def test_level_1_certification(self):
        cert = self.engine.get_certification(1)
        assert "DreamCo" in cert

    def test_get_certification_invalid_level_returns_none(self):
        assert self.engine.get_certification(99) is None

    def test_teaching_modes_available(self):
        modes = self.engine.list_all_teaching_modes()
        assert MODE_VIDEO in modes
        assert MODE_CODING_LAB in modes

    def test_level_duration_positive(self):
        for i in range(1, 11):
            lvl = self.engine.get_level(i)
            assert lvl.total_duration_minutes() > 0

    def test_level_has_prerequisite(self):
        lvl2 = self.engine.get_level(2)
        assert lvl2.prerequisite_level == 1

    def test_level_1_no_prerequisite(self):
        lvl1 = self.engine.get_level(1)
        assert lvl1.prerequisite_level is None


# ===========================================================================
# 4. Token Marketplace
# ===========================================================================

class TestTokenMarketplace:
    def setup_method(self):
        self.mp = TokenMarketplace()

    def test_markup_is_25_percent(self):
        assert MARKUP_PERCENTAGE == 0.25

    def test_get_price_llm_standard(self):
        price = self.mp.get_price("llm_standard")
        assert price is not None
        assert price > 0

    def test_price_includes_markup(self):
        base = self.mp.get_base_price("image_gen")
        user_price = self.mp.get_price("image_gen")
        assert abs(user_price - base * 1.25) < 0.0001

    def test_get_price_unknown_returns_none(self):
        assert self.mp.get_price("nonexistent_service") is None

    def test_calculate_cost_structure(self):
        result = self.mp.calculate_cost("llm_standard", 1000)
        assert "base_cost_usd" in result
        assert "total_cost_usd" in result
        assert "dreamco_profit_usd" in result
        assert result["total_cost_usd"] > result["base_cost_usd"]

    def test_calculate_cost_profit_is_25_percent_of_base(self):
        result = self.mp.calculate_cost("llm_standard", 1)
        expected_profit = round(result["base_cost_usd"] * 0.25, 6)
        assert abs(result["dreamco_profit_usd"] - expected_profit) < 0.000001

    def test_calculate_cost_unknown_returns_none(self):
        assert self.mp.calculate_cost("unknown", 1) is None

    def test_purchase_tokens_success(self):
        result = self.mp.purchase_tokens("image_gen", 5)
        assert "transaction_id" in result
        assert result["tokens_purchased"] == 5
        assert "total_cost_usd" in result
        assert "dreamco_profit_usd" in result

    def test_purchase_tokens_transaction_id_format(self):
        result = self.mp.purchase_tokens("llm_standard", 10)
        assert result["transaction_id"].startswith("TX-")

    def test_purchase_tokens_unknown_service(self):
        result = self.mp.purchase_tokens("bad_service", 1)
        assert "error" in result

    def test_daily_limit_enforced(self):
        mp = TokenMarketplace(max_daily_tokens=5)
        result = mp.purchase_tokens("llm_standard", 10)
        assert "error" in result

    def test_daily_limit_not_exceeded_within_cap(self):
        mp = TokenMarketplace(max_daily_tokens=10)
        result = mp.purchase_tokens("llm_standard", 5)
        assert "transaction_id" in result

    def test_reset_daily_usage(self):
        mp = TokenMarketplace(max_daily_tokens=5)
        mp.purchase_tokens("llm_standard", 5)
        mp.reset_daily_usage()
        result = mp.purchase_tokens("llm_standard", 5)
        assert "transaction_id" in result

    def test_usage_summary_structure(self):
        self.mp.purchase_tokens("llm_standard", 10)
        summary = self.mp.get_usage_summary()
        assert "total_transactions" in summary
        assert "total_revenue_usd" in summary
        assert "total_profit_usd" in summary

    def test_usage_summary_profit_positive(self):
        self.mp.purchase_tokens("image_gen", 3)
        summary = self.mp.get_usage_summary()
        assert summary["total_profit_usd"] > 0

    def test_list_service_types(self):
        services = self.mp.list_service_types()
        assert "llm_standard" in services
        assert "image_gen" in services
        assert "voice_gen" in services

    def test_multiple_purchases_accumulate(self):
        self.mp.purchase_tokens("llm_standard", 1)
        self.mp.purchase_tokens("image_gen", 1)
        summary = self.mp.get_usage_summary()
        assert summary["total_transactions"] == 2


# ===========================================================================
# 5. AI Skill Tree
# ===========================================================================

class TestAISkillTree:
    def setup_method(self):
        self.tree = AISkillTree(max_level=10)

    def test_ten_nodes_total(self):
        assert len(self.tree.list_all_nodes()) == 10

    def test_first_node_unlocked_by_default(self):
        node = self.tree.get_node_by_level(1)
        assert node.status == NodeStatus.UNLOCKED

    def test_other_nodes_locked_by_default(self):
        for level in range(2, 11):
            node = self.tree.get_node_by_level(level)
            assert node.status == NodeStatus.LOCKED

    def test_complete_level_1_unlocks_level_2(self):
        result = self.tree.complete_node("L1-FOUNDATIONS")
        assert result.get("next_node_unlocked") is True
        node2 = self.tree.get_node_by_level(2)
        assert node2.status == NodeStatus.UNLOCKED

    def test_complete_node_returns_badge(self):
        result = self.tree.complete_node("L1-FOUNDATIONS")
        assert "badge_earned" in result
        assert result["badge_earned"] == "🤖 AI Explorer"

    def test_complete_locked_node_returns_error(self):
        result = self.tree.complete_node("L5-BUSINESS")
        assert "error" in result

    def test_complete_nonexistent_node_returns_error(self):
        result = self.tree.complete_node("INVALID-NODE")
        assert "error" in result

    def test_start_node_marks_in_progress(self):
        result = self.tree.start_node("L1-FOUNDATIONS")
        assert result["status"] == NodeStatus.IN_PROGRESS.value

    def test_start_locked_node_returns_error(self):
        result = self.tree.start_node("L3-CONTENT")
        assert "error" in result

    def test_discount_increases_with_completion(self):
        self.tree.complete_node("L1-FOUNDATIONS")
        self.tree.complete_node("L2-PROMPTS")
        discount = self.tree.get_current_discount()
        assert discount > 0

    def test_initial_discount_is_zero(self):
        fresh = AISkillTree()
        assert fresh.get_current_discount() == 0.0

    def test_max_level_limits_accessible_nodes(self):
        limited = AISkillTree(max_level=5)
        accessible = limited.list_accessible_nodes()
        assert len(accessible) == 5
        assert all(n.level <= 5 for n in accessible)

    def test_progress_summary_structure(self):
        summary = self.tree.get_progress_summary()
        assert "total_nodes" in summary
        assert "completed" in summary
        assert "badges_earned" in summary
        assert summary["total_nodes"] == 10

    def test_completing_all_nodes_earns_max_discount(self):
        tree = AISkillTree(max_level=10)
        # Complete nodes sequentially
        node_ids = [n.node_id for n in tree.list_all_nodes()]
        for node_id in node_ids:
            node = tree.get_node(node_id)
            if node.status == NodeStatus.LOCKED:
                # Force unlock for testing
                node.status = NodeStatus.UNLOCKED
            tree.complete_node(node_id)
        assert tree.get_current_discount() == 25.0

    def test_level_10_badge(self):
        node = self.tree.get_node_by_level(10)
        assert "Master" in node.badge

    def test_node_to_dict_structure(self):
        node = self.tree.get_node("L1-FOUNDATIONS")
        d = node.to_dict()
        assert "node_id" in d
        assert "skills" in d
        assert "badge" in d
        assert "status" in d


# ===========================================================================
# 6. AI Agents Generator
# ===========================================================================

class TestAIAgentsGenerator:
    def setup_method(self):
        self.gen = AIAgentsGenerator(created_by="test_user")

    def test_list_templates_returns_list(self):
        templates = self.gen.list_templates()
        assert isinstance(templates, list)
        assert len(templates) >= 3

    def test_get_template_real_estate(self):
        tmpl = self.gen.get_template("real_estate_marketing")
        assert tmpl is not None
        assert "tools" in tmpl
        assert "GPT" in str(tmpl["tools"])

    def test_get_template_nonexistent_returns_none(self):
        assert self.gen.get_template("fake_template") is None

    def test_create_agent_returns_spec(self):
        result = self.gen.create_agent(
            name="Marketing Bot",
            purpose="Automate social media marketing",
            tools=["ChatGPT", "DALL-E"],
            automation_hooks=["Post scheduler"],
        )
        assert "agent_id" in result
        assert result["name"] == "Marketing Bot"
        assert result["status"] == AgentStatus.DRAFT.value

    def test_create_agent_id_format(self):
        result = self.gen.create_agent(
            name="Test Bot",
            purpose="Testing",
            tools=["ChatGPT"],
        )
        assert result["agent_id"].startswith("AGENT-")

    def test_create_from_template(self):
        result = self.gen.create_from_template("content_creator")
        assert "agent_id" in result
        assert "Content Creator" in result["name"]

    def test_create_from_invalid_template(self):
        result = self.gen.create_from_template("nonexistent")
        assert "error" in result

    def test_max_agents_limit_enforced(self):
        limited = AIAgentsGenerator(max_agents=2)
        limited.create_agent("Bot1", "purpose", ["tool"])
        limited.create_agent("Bot2", "purpose", ["tool"])
        result = limited.create_agent("Bot3", "purpose", ["tool"])
        assert "error" in result

    def test_no_limit_by_default(self):
        unlimited = AIAgentsGenerator(max_agents=None)
        for i in range(10):
            unlimited.create_agent(f"Bot{i}", "purpose", ["tool"])
        assert unlimited.count_agents() == 10

    def test_activate_agent(self):
        result = self.gen.create_agent("TestBot", "Testing", ["ChatGPT"])
        agent_id = result["agent_id"]
        activated = self.gen.activate_agent(agent_id)
        assert activated["status"] == AgentStatus.ACTIVE.value

    def test_pause_agent(self):
        result = self.gen.create_agent("TestBot", "Testing", ["ChatGPT"])
        agent_id = result["agent_id"]
        paused = self.gen.pause_agent(agent_id)
        assert paused["status"] == AgentStatus.PAUSED.value

    def test_activate_nonexistent_agent(self):
        result = self.gen.activate_agent("AGENT-9999")
        assert "error" in result

    def test_list_agents_returns_all(self):
        self.gen.create_agent("Bot1", "purpose1", ["tool1"])
        self.gen.create_agent("Bot2", "purpose2", ["tool2"])
        agents = self.gen.list_agents()
        assert len(agents) == 2

    def test_count_agents(self):
        assert self.gen.count_agents() == 0
        self.gen.create_agent("Bot", "purpose", ["tool"])
        assert self.gen.count_agents() == 1


# ===========================================================================
# 7. AILevelUpBot Integration
# ===========================================================================

class TestAILevelUpBotIntegration:
    def setup_method(self):
        self.bot = AILevelUpBot(tier=Tier.ENTERPRISE, user_id="test_user")

    def test_run_returns_status_string(self):
        status = self.bot.run()
        assert "AI Level-Up Bot" in status
        assert "ENTERPRISE" in status

    def test_teach_ai_tool_chatgpt(self):
        result = self.bot.teach_ai_tool("ChatGPT")
        assert result.get("company") == "OpenAI"
        assert "capabilities" in result
        assert "pricing" in result

    def test_teach_ai_tool_not_found(self):
        result = self.bot.teach_ai_tool("ZZZ_NONEXISTENT")
        assert "error" in result

    def test_search_companies_by_category(self):
        results = self.bot.search_companies("Core AI Models")
        assert len(results) >= 5
        for company in results[:3]:
            assert company["category"] == "Core AI Models"

    def test_get_course_level_1(self):
        result = self.bot.get_course_level(1)
        assert result.get("level") == 1
        assert "AI Basics" in result.get("name", "")

    def test_get_course_level_exceeds_tier_returns_error(self):
        starter_bot = AILevelUpBot(tier=Tier.STARTER)
        result = starter_bot.get_course_level(5)
        assert "error" in result

    def test_purchase_tokens(self):
        result = self.bot.purchase_tokens("image_gen", 2)
        assert "transaction_id" in result

    def test_advance_skill_tree(self):
        result = self.bot.advance_skill_tree("L1-FOUNDATIONS")
        assert "badge_earned" in result

    def test_create_agent_enterprise(self):
        result = self.bot.create_agent(
            name="SEO Bot",
            purpose="Generate SEO content",
            tools=["ChatGPT", "Grammarly"],
        )
        assert "agent_id" in result

    def test_create_agent_from_template(self):
        result = self.bot.create_agent_from_template("real_estate_marketing")
        assert "agent_id" in result

    def test_dashboard_structure(self):
        dash = self.bot.dashboard()
        assert "bot" in dash
        assert "tier" in dash
        assert "database_size" in dash
        assert dash["database_size"] >= 100

    def test_describe_tier_structure(self):
        info = self.bot.describe_tier()
        assert info["tier"] == "enterprise"
        assert info["price_usd_monthly"] == 399.0
        assert info["upgrade_available"] is False

    def test_starter_tier_no_skill_tree(self):
        starter = AILevelUpBot(tier=Tier.STARTER)
        with pytest.raises(AILevelUpTierError):
            starter.advance_skill_tree("L1-FOUNDATIONS")

    def test_starter_tier_no_agents_generator(self):
        starter = AILevelUpBot(tier=Tier.STARTER)
        with pytest.raises(AILevelUpTierError):
            starter.create_agent("Bot", "Purpose", ["tool"])

    def test_pro_tier_has_skill_tree(self):
        pro = AILevelUpBot(tier=Tier.PRO)
        result = pro.advance_skill_tree("L1-FOUNDATIONS")
        assert "badge_earned" in result

    def test_pro_tier_course_level_7(self):
        pro = AILevelUpBot(tier=Tier.PRO)
        result = pro.get_course_level(7)
        assert result.get("level") == 7

    def test_pro_tier_course_level_8_unavailable(self):
        pro = AILevelUpBot(tier=Tier.PRO)
        result = pro.get_course_level(8)
        assert "error" in result

    def test_bot_has_database_with_100_plus(self):
        assert self.bot.database.count() >= 100

    def test_starter_bot_limited_database_search(self):
        starter = AILevelUpBot(tier=Tier.STARTER)
        results = starter.search_companies("Core AI Models")
        # Starter tier caps companies at max_companies_accessible
        assert len(results) <= (get_tier_config(Tier.STARTER).max_companies_accessible or 25)

    def test_tier_upgrade_path_shown_in_describe(self):
        starter = AILevelUpBot(tier=Tier.STARTER)
        info = starter.describe_tier()
        assert info["upgrade_available"] is True
        assert info["upgrade_to"] == "Pro"
