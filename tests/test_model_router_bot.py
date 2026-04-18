"""
Tests for bots/model_router_bot/

Covers:
  1. Tiers (FREE / PRO / ENTERPRISE)
  2. ModelRouter engine
  3. TaskClassifier engine
  4. RouterAgent engine
  5. ResourceManager engine
  6. PerformanceTracker engine
  7. ModelRouterBot orchestrator (run_all_engines / get_summary)
  8. Tier gating (feature access + task-type caps)
  9. Error handling & edge cases
  10. Bot Library registration
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Tier imports
# ---------------------------------------------------------------------------
from bots.model_router_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_TASK_CLASSIFICATION,
    FEATURE_MODEL_ROUTING,
    FEATURE_RESOURCE_TOOLS,
    FEATURE_PERFORMANCE_TRACKING,
    FEATURE_COST_OPTIMIZATION,
    FEATURE_MULTI_AGENT,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
)

# ---------------------------------------------------------------------------
# Bot imports
# ---------------------------------------------------------------------------
from bots.model_router_bot.model_router_bot import (
    ModelRouterBot,
    ModelRouter,
    TaskClassifier,
    RouterAgent,
    ResourceManager,
    PerformanceTracker,
)


# ===========================================================================
# 1. TIER TESTS
# ===========================================================================

class TestTiers:
    def test_all_tiers_exist(self):
        assert Tier.FREE.value == "free"
        assert Tier.PRO.value == "pro"
        assert Tier.ENTERPRISE.value == "enterprise"

    def test_tier_catalogue_has_all_tiers(self):
        for tier in Tier:
            assert tier.value in TIER_CATALOGUE

    def test_free_tier_config(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0
        assert cfg.max_task_types == 3
        assert cfg.max_tools == 1
        assert cfg.has_feature(FEATURE_TASK_CLASSIFICATION)
        assert cfg.has_feature(FEATURE_MODEL_ROUTING)
        assert cfg.has_feature(FEATURE_RESOURCE_TOOLS)
        assert not cfg.has_feature(FEATURE_PERFORMANCE_TRACKING)
        assert not cfg.has_feature(FEATURE_COST_OPTIMIZATION)
        assert not cfg.has_feature(FEATURE_MULTI_AGENT)

    def test_pro_tier_config(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 97.0
        assert cfg.max_task_types is None
        assert cfg.max_tools is None
        assert cfg.has_feature(FEATURE_PERFORMANCE_TRACKING)
        assert cfg.has_feature(FEATURE_COST_OPTIMIZATION)
        assert not cfg.has_feature(FEATURE_MULTI_AGENT)

    def test_enterprise_tier_config(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 297.0
        assert cfg.max_task_types is None
        assert cfg.max_tools is None
        assert cfg.has_feature(FEATURE_MULTI_AGENT)
        assert cfg.has_feature(FEATURE_WHITE_LABEL)
        assert cfg.has_feature(FEATURE_API_ACCESS)
        assert cfg.has_feature(FEATURE_DEDICATED_SUPPORT)

    def test_list_tiers_returns_all(self):
        tiers = list_tiers()
        assert len(tiers) == 3
        assert all(isinstance(t, TierConfig) for t in tiers)

    def test_upgrade_path_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_path_pro_to_enterprise(self):
        upgrade = get_upgrade_path(Tier.PRO)
        assert upgrade is not None
        assert upgrade.tier == Tier.ENTERPRISE

    def test_upgrade_path_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_is_unlimited_tasks_free(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.is_unlimited_tasks()

    def test_is_unlimited_tasks_enterprise(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited_tasks()


# ===========================================================================
# 2. ModelRouter TESTS
# ===========================================================================

class TestModelRouter:
    def setup_method(self):
        self.router = ModelRouter()

    def test_route_coding(self):
        assert self.router.route("coding") == "anthropic"

    def test_route_general(self):
        assert self.router.route("general") == "openai"

    def test_route_vision(self):
        assert self.router.route("vision") == "google"

    def test_route_cheap(self):
        assert self.router.route("cheap") == "mistral"

    def test_route_search(self):
        assert self.router.route("search") == "cohere"

    def test_route_real_time(self):
        assert self.router.route("real_time") == "xai"

    def test_route_unknown_falls_back_to_openai(self):
        assert self.router.route("unknown_task_xyz") == "openai"

    def test_execute_returns_dict_with_required_keys(self):
        result = self.router.execute("coding", "build a REST API")
        assert result["task_type"] == "coding"
        assert result["provider"] == "anthropic"
        assert result["routed"] is True
        assert "response" in result
        assert "estimated_cost_usd" in result

    def test_execute_all_task_types(self):
        task_types = ["coding", "general", "vision", "cheap", "search", "real_time"]
        for tt in task_types:
            result = self.router.execute(tt, f"do a {tt} task")
            assert result["routed"] is True
            assert result["task_type"] == tt

    def test_list_routes(self):
        routes = self.router.list_routes()
        assert isinstance(routes, dict)
        assert "coding" in routes
        assert routes["coding"] == "anthropic"

    def test_get_provider_info(self):
        info = self.router.get_provider_info("anthropic")
        assert "display_name" in info
        assert "strengths" in info
        assert "cost_tier" in info

    def test_get_provider_info_unknown_returns_empty(self):
        info = self.router.get_provider_info("nonexistent_provider")
        assert info == {}

    def test_execute_cost_is_non_negative(self):
        result = self.router.execute("general", "test task")
        assert result["estimated_cost_usd"] >= 0

    def test_execute_prompt_preview_truncated(self):
        long_prompt = "x" * 200
        result = self.router.execute("general", long_prompt)
        assert len(result["prompt_preview"]) <= 120


# ===========================================================================
# 3. TaskClassifier TESTS
# ===========================================================================

class TestTaskClassifier:
    def setup_method(self):
        self.clf = TaskClassifier()

    def test_classify_coding_keyword_code(self):
        assert self.clf.classify("write some code for me") == "coding"

    def test_classify_coding_keyword_build(self):
        assert self.clf.classify("build an API endpoint") == "coding"

    def test_classify_coding_keyword_debug(self):
        assert self.clf.classify("debug this function") == "coding"

    def test_classify_vision(self):
        assert self.clf.classify("detect objects in the image") == "vision"

    def test_classify_search(self):
        assert self.clf.classify("search for lead data") == "search"

    def test_classify_real_time(self):
        assert self.clf.classify("get live trend updates") == "real_time"

    def test_classify_cheap(self):
        assert self.clf.classify("bulk process cheaply") == "cheap"

    def test_classify_general_fallback(self):
        assert self.clf.classify("help me with my business strategy") == "general"

    def test_classify_is_case_insensitive(self):
        assert self.clf.classify("BUILD A WEBSITE") == "coding"
        assert self.clf.classify("LIVE TRENDS") == "real_time"

    def test_classify_batch(self):
        tasks = ["build a bot", "show me an image", "general info"]
        results = self.clf.classify_batch(tasks)
        assert len(results) == 3
        assert all("task" in r and "task_type" in r for r in results)
        assert results[0]["task_type"] == "coding"
        assert results[1]["task_type"] == "vision"
        assert results[2]["task_type"] == "general"

    def test_classify_batch_empty(self):
        assert self.clf.classify_batch([]) == []


# ===========================================================================
# 4. RouterAgent TESTS
# ===========================================================================

class TestRouterAgent:
    def setup_method(self):
        self.agent = RouterAgent()

    def test_run_returns_dict(self):
        result = self.agent.run("build a sales bot")
        assert isinstance(result, dict)
        assert result["routed"] is True

    def test_run_classifies_correctly(self):
        result = self.agent.run("write a Python script")
        assert result["task_type"] == "coding"
        assert result["provider"] == "anthropic"

    def test_run_updates_history(self):
        self.agent.run("task one")
        self.agent.run("task two")
        assert len(self.agent.get_history()) == 2

    def test_run_batch_returns_all_results(self):
        tasks = ["code a function", "search for leads", "general update"]
        results = self.agent.run_batch(tasks)
        assert len(results) == 3

    def test_clear_history(self):
        self.agent.run("some task")
        self.agent.clear_history()
        assert self.agent.get_history() == []

    def test_get_history_returns_copy(self):
        self.agent.run("task")
        h1 = self.agent.get_history()
        h1.append({"fake": True})
        assert len(self.agent.get_history()) == 1


# ===========================================================================
# 5. ResourceManager TESTS
# ===========================================================================

class TestResourceManager:
    def setup_method(self):
        self.rm = ResourceManager()

    def test_list_tools(self):
        tools = self.rm.list_tools()
        assert "email" in tools
        assert "crm" in tools
        assert "payment" in tools
        assert "data" in tools

    def test_use_email_returns_sent_status(self):
        result = self.rm.use("email", {"email": "test@example.com", "subject": "Hello"})
        assert result["status"] == "sent"
        assert result["recipient"] == "test@example.com"
        assert "message_id" in result

    def test_use_crm_returns_saved_status(self):
        result = self.rm.use("crm", {"name": "John Doe"})
        assert result["status"] == "saved"
        assert "crm_id" in result

    def test_use_payment_returns_status(self):
        result = self.rm.use("payment", {"email": "buyer@example.com", "amount_usd": 99.0})
        assert result["status"] in ("success", "failed")
        assert result["payer"] == "buyer@example.com"

    def test_use_data_returns_fetched(self):
        result = self.rm.use("data", {"source": "SerpAPI", "query": "AI trends"})
        assert result["status"] == "fetched"
        assert "records" in result
        assert isinstance(result["data_sample"], list)

    def test_use_unknown_tool_returns_none(self):
        result = self.rm.use("unknown_tool_xyz", {})
        assert result is None

    def test_execution_log_updated(self):
        self.rm.use("email", {"email": "a@b.com"})
        self.rm.use("crm", {"name": "Bob"})
        log = self.rm.get_execution_log()
        assert len(log) == 2
        assert log[0]["tool"] == "email"
        assert log[1]["tool"] == "crm"

    def test_execution_log_is_copy(self):
        self.rm.use("email", {"email": "a@b.com"})
        log = self.rm.get_execution_log()
        log.append({"fake": True})
        assert len(self.rm.get_execution_log()) == 1


# ===========================================================================
# 6. PerformanceTracker TESTS
# ===========================================================================

class TestPerformanceTracker:
    def setup_method(self):
        self.tracker = PerformanceTracker()
        self.router = ModelRouter()

    def _make_results(self, task_types):
        return [self.router.execute(tt, f"test {tt} task") for tt in task_types]

    def test_analyze_returns_dict(self):
        results = self._make_results(["coding", "general", "vision"])
        report = self.tracker.analyze(results)
        assert isinstance(report, dict)
        assert report["total_tasks"] == 3

    def test_analyze_provider_distribution(self):
        results = self._make_results(["coding", "coding", "general"])
        report = self.tracker.analyze(results)
        dist = report["provider_distribution"]
        assert dist.get("anthropic", 0) == 2
        assert dist.get("openai", 0) == 1

    def test_analyze_most_used_provider(self):
        results = self._make_results(["coding", "coding", "vision"])
        report = self.tracker.analyze(results)
        assert report["most_used_provider"] == "anthropic"

    def test_analyze_total_cost_non_negative(self):
        results = self._make_results(["general", "cheap"])
        report = self.tracker.analyze(results)
        assert report["total_estimated_cost_usd"] >= 0

    def test_analyze_empty_returns_error(self):
        report = self.tracker.analyze([])
        assert "error" in report

    def test_analyze_suggestions_present(self):
        results = self._make_results(["general", "general", "general"])
        report = self.tracker.analyze(results)
        assert isinstance(report["optimization_suggestions"], list)
        assert len(report["optimization_suggestions"]) > 0

    def test_analyze_task_types_seen(self):
        results = self._make_results(["coding", "vision"])
        report = self.tracker.analyze(results)
        assert "coding" in report["task_types_seen"]
        assert "vision" in report["task_types_seen"]


# ===========================================================================
# 7. ModelRouterBot ORCHESTRATOR TESTS
# ===========================================================================

class TestModelRouterBot:
    def test_free_tier_run_all_engines(self):
        bot = ModelRouterBot(tier=Tier.FREE)
        report = bot.run_all_engines()
        assert report["bot"] == "ModelRouterBot"
        assert report["tier"] == "free"
        assert "tasks_routed" in report
        assert report["tasks_routed"] >= 0

    def test_pro_tier_run_all_engines(self):
        bot = ModelRouterBot(tier=Tier.PRO)
        report = bot.run_all_engines()
        assert report["tier"] == "pro"
        assert "performance_analysis" in report
        pa = report["performance_analysis"]
        assert "error" not in pa
        assert "cost_optimization" in report
        co = report["cost_optimization"]
        assert "error" not in co

    def test_enterprise_tier_run_all_engines(self):
        bot = ModelRouterBot(tier=Tier.ENTERPRISE)
        report = bot.run_all_engines()
        assert "multi_agent_results" in report
        agents = report["multi_agent_results"]
        assert isinstance(agents, list)
        assert len(agents) == 3

    def test_get_summary_returns_dict(self):
        bot = ModelRouterBot(tier=Tier.PRO)
        summary = bot.get_summary()
        assert summary["bot"] == "ModelRouterBot"
        assert "tasks_routed" in summary
        assert "routing_table" in summary
        assert "provider_distribution" in summary

    def test_get_summary_upgrade_free(self):
        bot = ModelRouterBot(tier=Tier.FREE)
        summary = bot.get_summary()
        assert summary["upgrade_available"] == "Pro"

    def test_get_summary_upgrade_enterprise_is_none(self):
        bot = ModelRouterBot(tier=Tier.ENTERPRISE)
        summary = bot.get_summary()
        assert summary["upgrade_available"] is None

    def test_get_summary_triggers_run_if_no_report(self):
        bot = ModelRouterBot(tier=Tier.PRO)
        summary = bot.get_summary()
        assert summary["tasks_routed"] >= 0

    def test_run_all_engines_has_timestamp(self):
        bot = ModelRouterBot(tier=Tier.FREE)
        report = bot.run_all_engines()
        assert "timestamp" in report
        assert report["timestamp"].endswith("Z")


# ===========================================================================
# 8. TIER GATING TESTS
# ===========================================================================

class TestTierGating:
    def test_free_classify_task_allowed(self):
        bot = ModelRouterBot(tier=Tier.FREE)
        result = bot.classify_task("build an API")
        assert result == "coding"

    def test_free_route_task_allowed(self):
        bot = ModelRouterBot(tier=Tier.FREE)
        result = bot.route_task("build an API")
        assert result is not None
        assert result["routed"] is True

    def test_free_route_task_unknown_type_falls_back(self):
        bot = ModelRouterBot(tier=Tier.FREE)
        # "real_time" is not in FREE's 3 allowed types → should fall back to "general"
        result = bot.route_task("get live social media trends right now")
        assert result is not None
        assert result["task_type"] == "general"

    def test_free_resource_tool_email_allowed(self):
        bot = ModelRouterBot(tier=Tier.FREE)
        result = bot.run_resource_tool("email", {"email": "test@test.com"})
        assert result is not None
        assert result["status"] == "sent"

    def test_free_resource_tool_crm_blocked(self):
        bot = ModelRouterBot(tier=Tier.FREE)
        result = bot.run_resource_tool("crm", {"name": "Test"})
        assert result is not None
        assert "error" in result

    def test_free_performance_tracking_blocked(self):
        bot = ModelRouterBot(tier=Tier.FREE)
        result = bot.analyze_performance([])
        assert "error" in result

    def test_free_cost_optimization_blocked(self):
        bot = ModelRouterBot(tier=Tier.FREE)
        result = bot.get_cost_optimization()
        assert "error" in result

    def test_free_multi_agent_blocked(self):
        bot = ModelRouterBot(tier=Tier.FREE)
        result = bot.broadcast_to_agents("do a task")
        assert len(result) == 1
        assert "error" in result[0]

    def test_pro_all_task_types_allowed(self):
        bot = ModelRouterBot(tier=Tier.PRO)
        for tt_keyword in ["build code", "detect image", "search data", "live trends",
                            "cheap bulk", "general help"]:
            result = bot.route_task(tt_keyword)
            assert result is not None
            assert result["routed"] is True

    def test_pro_performance_tracking_allowed(self):
        bot = ModelRouterBot(tier=Tier.PRO)
        router = ModelRouter()
        routing_results = [router.execute("general", "task")]
        report = bot.analyze_performance(routing_results)
        assert "error" not in report
        assert report["total_tasks"] == 1

    def test_pro_cost_optimization_allowed(self):
        bot = ModelRouterBot(tier=Tier.PRO)
        result = bot.get_cost_optimization()
        assert "error" not in result
        assert "routing_table" in result

    def test_pro_multi_agent_blocked(self):
        bot = ModelRouterBot(tier=Tier.PRO)
        result = bot.broadcast_to_agents("task")
        assert "error" in result[0]

    def test_enterprise_multi_agent_allowed(self):
        bot = ModelRouterBot(tier=Tier.ENTERPRISE)
        results = bot.broadcast_to_agents("coordinate campaign", agent_count=2)
        assert len(results) == 2
        assert all("agent_id" in r for r in results)
        assert all("error" not in r for r in results)

    def test_enterprise_all_tools_allowed(self):
        bot = ModelRouterBot(tier=Tier.ENTERPRISE)
        for tool, payload in [
            ("email", {"email": "e@e.com"}),
            ("crm", {"name": "Test"}),
            ("payment", {"email": "p@p.com", "amount_usd": 50}),
            ("data", {"source": "api", "query": "q"}),
        ]:
            result = bot.run_resource_tool(tool, payload)
            assert result is not None
            assert "error" not in result


# ===========================================================================
# 9. EDGE CASES
# ===========================================================================

class TestEdgeCases:
    def test_classify_empty_string_returns_general(self):
        clf = TaskClassifier()
        assert clf.classify("") == "general"

    def test_router_execute_empty_prompt(self):
        router = ModelRouter()
        result = router.execute("general", "")
        assert result["routed"] is True
        assert result["estimated_cost_usd"] == 0

    def test_resource_manager_email_missing_fields(self):
        rm = ResourceManager()
        result = rm.use("email", {})
        assert result["status"] == "sent"
        assert result["recipient"] == "unknown@example.com"

    def test_router_agent_empty_batch(self):
        agent = RouterAgent()
        assert agent.run_batch([]) == []

    def test_performance_tracker_single_result(self):
        tracker = PerformanceTracker()
        router = ModelRouter()
        result = router.execute("coding", "a single task")
        report = tracker.analyze([result])
        assert report["total_tasks"] == 1

    def test_model_router_bot_default_tier_is_free(self):
        bot = ModelRouterBot()
        assert bot.tier == Tier.FREE

    def test_run_all_engines_idempotent(self):
        bot = ModelRouterBot(tier=Tier.PRO)
        r1 = bot.run_all_engines()
        r2 = bot.run_all_engines()
        assert r1["bot"] == r2["bot"]
        assert r1["tier"] == r2["tier"]


# ===========================================================================
# 10. BOT LIBRARY REGISTRATION TESTS
# ===========================================================================

class TestBotLibraryRegistration:
    def _get_library_entries(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        return lib

    def test_model_router_bot_registered(self):
        lib = self._get_library_entries()
        entry = lib.get_bot("model_router_bot")
        assert entry is not None
        assert entry.bot_id == "model_router_bot"

    def test_model_router_bot_entry_has_correct_fields(self):
        lib = self._get_library_entries()
        entry = lib.get_bot("model_router_bot")
        assert entry is not None
        assert entry.display_name != ""
        assert entry.module_path == "bots.model_router_bot.model_router_bot"
        assert entry.class_name == "ModelRouterBot"
        assert len(entry.capabilities) > 0
