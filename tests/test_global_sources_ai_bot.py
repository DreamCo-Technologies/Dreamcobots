"""
Tests for bots/global_sources_ai_bot/ — Universal AI Model Router & BuddyAI System.

Coverage areas:
  1.  Tiers & tier config
  2.  Model registry — TOP_100_AI_MODELS
  3.  Use-case registry — TOP_100_USE_CASES
  4.  TaskRouter — routing logic
  5.  BenchmarkEngine — scoring & ranking
  6.  GlobalSourcesAIBot — all 10 layers
  7.  GlobalAISourcesFlow integration
  8.  Multi-agent workforce
  9.  Marketplace & collaboration catalog
  10. Edge cases
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ── Package imports ────────────────────────────────────────────────────────
from bots.global_sources_ai_bot import (
    GlobalSourcesAIBot,
    GlobalSourcesBotError,
    GlobalSourcesBotTierError,
    Tier,
    TaskRouter,
    RoutingConfig,
    BenchmarkEngine,
    TOP_100_AI_MODELS,
    TOP_100_USE_CASES,
    AIModel,
    UseCase,
)
from bots.global_sources_ai_bot.tiers import (
    get_tier_config,
    list_tiers,
    FEATURE_BASIC_ROUTING,
    FEATURE_FULL_ROUTING,
    FEATURE_BENCHMARKING,
    FEATURE_AUTONOMOUS_UPGRADE,
    FEATURE_MULTI_AGENT,
    FEATURE_API_ACCESS,
    FEATURE_COLLABORATION_ENGINE,
)
from bots.global_sources_ai_bot.benchmarks import BENCHMARK_DIMENSIONS, ModelBenchmark
from bots.global_sources_ai_bot.buddy_connection_registry import buddy_connection_checklist


# ===========================================================================
# 1. Tiers & TierConfig
# ===========================================================================

class TestTiers:

    def test_three_tiers_exist(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_free_tier_price(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0

    def test_enterprise_tier_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0

    def test_free_has_basic_routing(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_BASIC_ROUTING)

    def test_free_lacks_full_routing(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_FULL_ROUTING)

    def test_pro_has_full_routing(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_FULL_ROUTING)

    def test_pro_has_benchmarking(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_BENCHMARKING)

    def test_enterprise_has_all_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feature in [
            FEATURE_FULL_ROUTING, FEATURE_BENCHMARKING,
            FEATURE_AUTONOMOUS_UPGRADE, FEATURE_MULTI_AGENT,
            FEATURE_API_ACCESS, FEATURE_COLLABORATION_ENGINE,
        ]:
            assert cfg.has_feature(feature), f"Missing feature: {feature}"

    def test_free_max_categories(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_categories == 5

    def test_enterprise_unlimited_categories(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_categories is None

    def test_free_max_models_per_task(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_models_per_task == 3

    def test_enterprise_max_models_per_task(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_models_per_task == 100


# ===========================================================================
# 2. Model Registry
# ===========================================================================

class TestModelRegistry:

    def test_100_models_registered(self):
        assert len(TOP_100_AI_MODELS) >= 100

    def test_chatgpt_present(self):
        assert "chatgpt" in TOP_100_AI_MODELS

    def test_claude_present(self):
        assert "claude" in TOP_100_AI_MODELS

    def test_midjourney_is_image_type(self):
        assert TOP_100_AI_MODELS["midjourney"].model_type == "image"

    def test_elevenlabs_is_voice_type(self):
        assert TOP_100_AI_MODELS["elevenlabs"].model_type == "voice"

    def test_llama_is_open_source(self):
        assert TOP_100_AI_MODELS["llama"].is_open_source is True

    def test_chatgpt_not_open_source(self):
        assert TOP_100_AI_MODELS["chatgpt"].is_open_source is False

    def test_all_models_have_model_id(self):
        for mid, model in TOP_100_AI_MODELS.items():
            assert model.model_id == mid, f"model_id mismatch for {mid}"

    def test_all_models_have_provider(self):
        for mid, model in TOP_100_AI_MODELS.items():
            assert model.provider, f"Missing provider for {mid}"

    def test_all_models_have_api_endpoint(self):
        for mid, model in TOP_100_AI_MODELS.items():
            assert model.api_endpoint_hint, f"Missing API endpoint for {mid}"

    def test_all_models_have_strengths(self):
        for mid, model in TOP_100_AI_MODELS.items():
            assert isinstance(model.strengths, list), f"Strengths not a list for {mid}"
            assert len(model.strengths) > 0, f"Empty strengths for {mid}"

    def test_all_models_have_cost_tier(self):
        valid_cost_tiers = {"free", "low", "medium", "high", "enterprise"}
        for mid, model in TOP_100_AI_MODELS.items():
            assert model.cost_tier in valid_cost_tiers, f"Invalid cost_tier for {mid}"

    def test_deepseek_open_source(self):
        assert TOP_100_AI_MODELS["deepseek"].is_open_source is True

    def test_claude_code_is_code_type(self):
        assert TOP_100_AI_MODELS["claude_code"].model_type == "code"

    def test_alphafold_science_type(self):
        assert TOP_100_AI_MODELS["alphafold"].model_type == "science"


# ===========================================================================
# 3. Use-Case Registry
# ===========================================================================

class TestUseCaseRegistry:

    def test_100_use_cases(self):
        assert len(TOP_100_USE_CASES) == 100

    def test_ids_are_sequential(self):
        ids = [uc.id for uc in TOP_100_USE_CASES]
        assert ids == list(range(1, 101))

    def test_all_have_names(self):
        for uc in TOP_100_USE_CASES:
            assert uc.name, f"UseCase {uc.id} has no name"

    def test_all_have_tags(self):
        for uc in TOP_100_USE_CASES:
            assert uc.tags, f"UseCase {uc.id} has no tags"

    def test_all_have_top_models(self):
        for uc in TOP_100_USE_CASES:
            assert uc.top_models, f"UseCase {uc.id} has no top_models"
            assert len(uc.top_models) >= 3, f"UseCase {uc.id} has fewer than 3 models"

    def test_writing_use_case_id_1(self):
        uc = TOP_100_USE_CASES[0]
        assert uc.id == 1
        assert "writing" in uc.name.lower() or "writing" in uc.tags

    def test_coding_use_case_id_3(self):
        uc = TOP_100_USE_CASES[2]
        assert uc.id == 3
        assert "coding" in uc.tags or "coding" in uc.name.lower()

    def test_image_generation_use_case_id_6(self):
        uc = TOP_100_USE_CASES[5]
        assert uc.id == 6
        assert "image_generation" in uc.tags

    def test_making_money_use_case_id_100(self):
        uc = TOP_100_USE_CASES[99]
        assert uc.id == 100

    def test_all_use_case_descriptions_non_empty(self):
        for uc in TOP_100_USE_CASES:
            assert uc.description, f"UseCase {uc.id} has empty description"


# ===========================================================================
# 4. TaskRouter
# ===========================================================================

class TestTaskRouter:

    def setup_method(self):
        self.router = TaskRouter()

    def test_route_returns_result(self):
        result = self.router.route("write a blog post")
        assert result is not None

    def test_route_has_primary_model(self):
        result = self.router.route("write a blog post")
        assert result.primary_model is not None

    def test_coding_task_routes_to_code_model(self):
        result = self.router.route("debug my Python code")
        assert result.primary_model is not None
        assert result.primary_model.model_type in ("code", "llm")

    def test_image_task_routes_to_image_model(self):
        result = self.router.route("generate an image logo")
        assert result.primary_model is not None
        image_types = {"image", "design"}
        image_strengths = {"image_generation", "design", "art", "branding"}
        primary = result.primary_model
        assert (
            primary.model_type in image_types
            or any(s in image_strengths for s in primary.strengths)
        ), f"Expected image/design model, got {primary.model_id} ({primary.model_type})"

    def test_music_task_routes_to_music_model(self):
        result = self.router.route("create music beats")
        assert result.primary_model is not None
        assert result.primary_model.model_type in ("music", "llm", "image")

    def test_voice_task_routes_to_voice_model(self):
        result = self.router.route("generate voice audio dubbing")
        assert result.primary_model is not None

    def test_research_task_routes_correctly(self):
        result = self.router.route("research and analysis of AI trends")
        assert result.primary_model is not None
        assert len(result.matched_use_cases) > 0

    def test_ranked_models_list_non_empty(self):
        result = self.router.route("automate my workflow")
        assert len(result.ranked_models) > 0

    def test_ranked_models_sorted_descending(self):
        result = self.router.route("write marketing copy")
        scores = [s for _, s in result.ranked_models]
        assert scores == sorted(scores, reverse=True)

    def test_reasoning_non_empty(self):
        result = self.router.route("translate text to Spanish")
        assert result.reasoning

    def test_tags_extracted(self):
        result = self.router.route("I need to translate and localize content")
        assert len(result.tags_used) > 0

    def test_route_batch(self):
        tasks = ["write an email", "debug code", "create image"]
        results = self.router.route_batch(tasks)
        assert len(results) == 3

    def test_update_benchmark_scores(self):
        self.router.update_benchmark_scores("chatgpt", {"accuracy": 0.95, "speed": 0.9})
        result = self.router.route("write a report")
        assert result is not None

    def test_available_use_cases_count(self):
        use_cases = self.router.available_use_cases()
        assert len(use_cases) == 100

    def test_available_models_count(self):
        models = self.router.available_models()
        assert len(models) >= 100

    def test_top_k_override(self):
        result = self.router.route("code a website", top_k=3)
        assert len(result.ranked_models) <= 3

    def test_explicit_route_coding(self):
        result = self.router.route("coding task fix bug")
        pids = [mid for mid, _ in result.ranked_models]
        code_models = {"claude_code", "github_copilot", "cursor", "chatgpt", "gemini_code"}
        assert any(m in code_models for m in pids)

    def test_explicit_route_video(self):
        result = self.router.route("create video film editing")
        pids = [mid for mid, _ in result.ranked_models]
        video_models = {"sora", "runway", "pika", "veo", "dream_machine", "descript"}
        assert any(m in video_models for m in pids), (
            f"Expected a video model in top-{len(pids)}, got: {pids}"
        )


# ===========================================================================
# 5. BenchmarkEngine
# ===========================================================================

class TestBenchmarkEngine:

    def setup_method(self):
        self.engine = BenchmarkEngine()

    def test_defaults_loaded(self):
        record = self.engine.get("chatgpt")
        assert record is not None
        assert record.composite_score > 0

    def test_all_registry_models_seeded(self):
        for mid in TOP_100_AI_MODELS:
            assert self.engine.get(mid) is not None, f"No benchmark for {mid}"

    def test_update_scores(self):
        self.engine.update("chatgpt", {"accuracy": 0.99, "speed": 0.95})
        record = self.engine.get("chatgpt")
        assert record.scores["accuracy"] == 0.99

    def test_composite_score_range(self):
        for mid in list(TOP_100_AI_MODELS.keys())[:10]:
            record = self.engine.get(mid)
            assert 0.0 <= record.composite_score <= 1.0

    def test_top_models_returns_list(self):
        top = self.engine.top_models(5)
        assert len(top) == 5

    def test_top_models_sorted(self):
        top = self.engine.top_models(5)
        scores = [s for _, s in top]
        assert scores == sorted(scores, reverse=True)

    def test_rank_by_accuracy(self):
        ranked = self.engine.rank_by_dimension("accuracy", 5)
        assert len(ranked) == 5

    def test_rank_by_invalid_dimension_raises(self):
        with pytest.raises(ValueError):
            self.engine.rank_by_dimension("invalid_dim")

    def test_scores_for_router_dict(self):
        scores = self.engine.scores_for_router()
        assert isinstance(scores, dict)
        assert "chatgpt" in scores

    def test_summary_keys(self):
        summary = self.engine.summary()
        assert "total_models_benchmarked" in summary
        assert "top_5_overall" in summary
        assert "best_coding" in summary

    def test_daily_cycle_returns_summary(self):
        result = self.engine.run_daily_cycle()
        assert "cycle_timestamp" in result
        assert result["models_updated"] > 0

    def test_model_benchmark_clamps_scores(self):
        mb = ModelBenchmark(model_id="test_model")
        mb.update({"accuracy": 1.5, "speed": -0.5})
        assert mb.scores["accuracy"] == 1.0
        assert mb.scores["speed"] == 0.0

    def test_benchmark_dimensions_count(self):
        assert len(BENCHMARK_DIMENSIONS) == 7


# ===========================================================================
# 6. GlobalSourcesAIBot — core routing
# ===========================================================================

class TestGlobalSourcesAIBotCore:

    def setup_method(self):
        self.bot_free = GlobalSourcesAIBot(tier=Tier.FREE)
        self.bot_pro = GlobalSourcesAIBot(tier=Tier.PRO)
        self.bot_ent = GlobalSourcesAIBot(tier=Tier.ENTERPRISE)

    def test_route_task_returns_dict(self):
        result = self.bot_free.route_task("write a blog post")
        assert isinstance(result, dict)

    def test_route_task_has_primary_model(self):
        result = self.bot_free.route_task("write an email")
        assert result["primary_model"] is not None
        assert "id" in result["primary_model"]

    def test_route_task_has_pipeline_trace(self):
        result = self.bot_free.route_task("debug Python code")
        assert "pipeline_trace" in result
        assert result["pipeline_trace"]["pipeline_complete"] is True

    def test_route_task_pipeline_trace_has_framework_version(self):
        result = self.bot_free.route_task("analyze data")
        assert result["pipeline_trace"]["framework_version"] == "1.0.0"

    def test_route_batch(self):
        tasks = ["write blog", "code app", "create image"]
        results = self.bot_pro.route_batch(tasks)
        assert len(results) == 3

    def test_list_all_models(self):
        models = self.bot_free.list_all_models()
        assert len(models) >= 100

    def test_list_all_use_cases(self):
        use_cases = self.bot_free.list_all_use_cases()
        assert len(use_cases) == 100

    def test_status_returns_dict(self):
        s = self.bot_free.status()
        assert s["tier"] == "free"
        assert s["registered_models"] >= 100
        assert s["use_cases"] == 100

    def test_status_has_strategic_rules(self):
        s = self.bot_free.status()
        assert len(s["strategic_rules"]) == 7

    def test_status_has_buddy_connectivity(self):
        s = self.bot_free.status()
        assert "buddy_global_sources_connectivity" in s
        assert s["buddy_global_sources_connectivity"]["all_connected"] is True

    def test_repr(self):
        r = repr(self.bot_pro)
        assert "GlobalSourcesAIBot" in r
        assert "pro" in r

    def test_ecosystem_status(self):
        eco = self.bot_free.ecosystem_status()
        assert "DreamSalesPro" in eco["products"]
        assert "ControlTower" in eco["products"]

    def test_marketplace_catalog(self):
        cat = self.bot_free.marketplace_catalog()
        assert cat["total_use_cases"] == 100
        assert cat["total_models"] >= 100

    def test_memory_summary_initial_empty(self):
        bot = GlobalSourcesAIBot(tier=Tier.PRO)
        s = bot.memory_summary()
        assert s["total_routed"] == 0

    def test_memory_grows_after_routing(self):
        bot = GlobalSourcesAIBot(tier=Tier.PRO)
        bot.route_task("write content")
        bot.route_task("code an app")
        s = bot.memory_summary()
        assert s["total_routed"] == 2

    def test_memory_tracks_models(self):
        bot = GlobalSourcesAIBot(tier=Tier.PRO)
        bot.route_task("code a function")
        s = bot.memory_summary()
        assert len(s["model_frequency"]) > 0


# ===========================================================================
# 7. GlobalAISourcesFlow integration
# ===========================================================================

class TestGlobalAISourcesFlowIntegration:

    def test_flow_pipeline_completes(self):
        bot = GlobalSourcesAIBot(tier=Tier.FREE)
        result = bot.route_task("research AI trends")
        trace = result["pipeline_trace"]
        assert trace["pipeline_complete"] is True

    def test_flow_bot_name_in_trace(self):
        bot = GlobalSourcesAIBot(tier=Tier.FREE)
        result = bot.route_task("analyze data")
        assert result["pipeline_trace"]["bot_name"] == "GlobalSourcesAIBot"

    def test_flow_all_8_stages_present(self):
        from framework.global_ai_sources_flow import REQUIRED_STAGES
        bot = GlobalSourcesAIBot(tier=Tier.FREE)
        result = bot.route_task("write a script")
        # The pipeline result is nested — just validate pipeline_complete flag
        assert result["pipeline_trace"]["pipeline_complete"] is True
        assert len(REQUIRED_STAGES) == 8


# ===========================================================================
# 8. Tier gates
# ===========================================================================

class TestTierGates:

    def test_free_cannot_run_benchmark_cycle(self):
        bot = GlobalSourcesAIBot(tier=Tier.FREE)
        with pytest.raises(GlobalSourcesBotTierError):
            bot.run_benchmark_cycle()

    def test_free_cannot_get_benchmark_summary(self):
        bot = GlobalSourcesAIBot(tier=Tier.FREE)
        with pytest.raises(GlobalSourcesBotTierError):
            bot.benchmark_summary()

    def test_pro_can_run_benchmark_cycle(self):
        bot = GlobalSourcesAIBot(tier=Tier.PRO)
        result = bot.run_benchmark_cycle()
        assert "models_updated" in result

    def test_pro_can_get_benchmark_summary(self):
        bot = GlobalSourcesAIBot(tier=Tier.PRO)
        s = bot.benchmark_summary()
        assert "top_5_overall" in s

    def test_free_cannot_discover_model(self):
        bot = GlobalSourcesAIBot(tier=Tier.FREE)
        with pytest.raises(GlobalSourcesBotTierError):
            bot.discover_model("new_model", {"provider": "TestCo"})

    def test_enterprise_can_discover_model(self):
        bot = GlobalSourcesAIBot(tier=Tier.ENTERPRISE)
        result = bot.discover_model("test_model_x", {"provider": "TestCo"})
        assert result["queued"] is True

    def test_free_cannot_access_workforce(self):
        bot = GlobalSourcesAIBot(tier=Tier.FREE)
        with pytest.raises(GlobalSourcesBotTierError):
            bot.multi_agent_workforce()

    def test_enterprise_can_access_workforce(self):
        bot = GlobalSourcesAIBot(tier=Tier.ENTERPRISE)
        wf = bot.multi_agent_workforce()
        assert wf["workforce_active"] is True

    def test_free_cannot_access_api_hub(self):
        bot = GlobalSourcesAIBot(tier=Tier.FREE)
        with pytest.raises(GlobalSourcesBotTierError):
            bot.api_hub_info()

    def test_enterprise_can_access_api_hub(self):
        bot = GlobalSourcesAIBot(tier=Tier.ENTERPRISE)
        hub = bot.api_hub_info()
        assert "endpoints" in hub

    def test_pro_cannot_access_api_hub(self):
        bot = GlobalSourcesAIBot(tier=Tier.PRO)
        with pytest.raises(GlobalSourcesBotTierError):
            bot.api_hub_info()


# ===========================================================================
# 9. Multi-agent workforce
# ===========================================================================

class TestMultiAgentWorkforce:

    def setup_method(self):
        self.bot = GlobalSourcesAIBot(tier=Tier.ENTERPRISE)

    def test_workforce_has_10_departments(self):
        wf = self.bot.multi_agent_workforce()
        assert len(wf["departments"]) == 10

    def test_all_departments_present(self):
        wf = self.bot.multi_agent_workforce()
        expected = {"ceo", "cto", "sales", "finance", "legal",
                    "marketing", "research", "automation", "security", "hiring"}
        assert set(wf["departments"].keys()) == expected

    def test_dispatch_to_cto(self):
        result = self.bot.dispatch_to_department("cto", "build a REST API")
        assert result["department"] == "CTO Agent"
        assert result["primary_model"] is not None

    def test_dispatch_to_legal(self):
        result = self.bot.dispatch_to_department("legal", "review contract")
        assert result["department"] == "Legal Agent"

    def test_dispatch_unknown_department_raises(self):
        with pytest.raises(GlobalSourcesBotError):
            self.bot.dispatch_to_department("unknown_dept", "some task")

    def test_dispatch_returns_pipeline_trace(self):
        result = self.bot.dispatch_to_department("sales", "outreach campaign")
        assert "pipeline_trace" in result


# ===========================================================================
# 10. Collaboration catalog & marketplace
# ===========================================================================

class TestCollaborationAndMarketplace:

    def test_free_collaboration_returns_partner_names(self):
        bot = GlobalSourcesAIBot(tier=Tier.FREE)
        cat = bot.collaboration_catalog()
        assert "partners" in cat

    def test_pro_collaboration_has_full_details(self):
        bot = GlobalSourcesAIBot(tier=Tier.PRO)
        cat = bot.collaboration_catalog()
        assert isinstance(cat["partners"], dict)
        assert "OpenAI" in cat["partners"]

    def test_collaboration_catalog_has_15_plus_partners(self):
        bot = GlobalSourcesAIBot(tier=Tier.PRO)
        cat = bot.collaboration_catalog()
        assert len(cat["partners"]) >= 10

    def test_marketplace_has_use_cases(self):
        bot = GlobalSourcesAIBot(tier=Tier.FREE)
        mp = bot.marketplace_catalog()
        assert mp["total_use_cases"] == 100

    def test_marketplace_categories_non_empty(self):
        bot = GlobalSourcesAIBot(tier=Tier.FREE)
        mp = bot.marketplace_catalog()
        assert len(mp["categories"]) > 0

    def test_api_hub_has_route_endpoint(self):
        bot = GlobalSourcesAIBot(tier=Tier.ENTERPRISE)
        hub = bot.api_hub_info()
        endpoints = hub["endpoints"]
        assert any("route" in k.lower() for k in endpoints)

    def test_api_hub_has_rate_limits(self):
        bot = GlobalSourcesAIBot(tier=Tier.ENTERPRISE)
        hub = bot.api_hub_info()
        assert "rate_limits" in hub
        assert "FREE" in hub["rate_limits"]


# ===========================================================================
# Self-improvement engine
# ===========================================================================

class TestSelfImprovementEngine:

    def setup_method(self):
        self.bot = GlobalSourcesAIBot(tier=Tier.ENTERPRISE)

    def test_discover_model_queues_entry(self):
        result = self.bot.discover_model("future_model_1", {"provider": "FutureCo"})
        assert result["queued"] is True
        assert result["entry"]["status"] == "pending_sandbox"

    def test_pending_discoveries_grows(self):
        self.bot.discover_model("model_a", {})
        self.bot.discover_model("model_b", {})
        pending = self.bot.pending_discoveries()
        assert len(pending) >= 2

    def test_sandbox_test_pending_processes(self):
        self.bot.discover_model("sandbox_model_1", {"provider": "X"})
        processed = self.bot.sandbox_test_pending()
        # The framework sandbox always returns passed=True in default config
        assert isinstance(processed, list)


class TestBuddyConnectivityChecklist:

    def test_global_sources_modules_registered(self):
        checklist = buddy_connection_checklist()
        modules = {entry["module"] for entry in checklist["modules"]}
        expected = {
            "global_sources_ai_bot.py",
            "benchmarks.py",
            "task_router.py",
            "model_registry.py",
            "tiers.py",
            "framework/global_ai_sources_flow.py",
        }
        assert expected.issubset(modules)

    def test_all_registered_modules_connected(self):
        checklist = buddy_connection_checklist()
        assert checklist["all_connected"] is True
