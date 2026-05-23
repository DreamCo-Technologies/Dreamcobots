"""Tests for bots/ai_provider_registry — schema, catalog, DB, router, mapper."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module imports
# ---------------------------------------------------------------------------
from bots.ai_provider_registry.provider_schema import AIProviderObject
from bots.ai_provider_registry.taxonomy import (
    CATEGORY_TAXONOMY,
    AI_CLUSTERS,
    PRICING_TIERS,
)
from bots.ai_provider_registry.provider_catalog import (
    PROVIDER_CATALOG,
    PROVIDER_CATALOG_BY_ID,
)
from bots.ai_provider_registry.registry_db import (
    RegistryDB,
    ingest_catalog,
    export_json,
)
from bots.ai_provider_registry.router_brain import (
    RouterBrain,
    ProviderSelectorEngine,
    CostOptimizerEngine,
    CapabilityGraphEngine,
    FailureRedundancyEngine,
    TASK_CAPABILITY_MAP,
)
from bots.ai_provider_registry.bot_provider_mapper import (
    BotProviderMapper,
    BotProviderMapping,
    BOT_MAPPING_REGISTRY,
)
from bots.global_sources_ai_bot.model_registry import (
    AI_PROVIDER_REGISTRY_200,
    TOP_200_PROVIDERS,
    TOP_100_AI_MODELS,
)


# ===========================================================================
# 1. Schema tests
# ===========================================================================
class TestAIProviderObjectSchema:
    def test_to_dict_round_trip(self):
        p = AIProviderObject(
            id="test_co",
            name="Test Co",
            pricing="freemium",
            categories=["foundation_models"],
            core_skill="Test skill",
            best_at="Best at testing",
            agent_role="Test Agent",
            bundle_fit=["core_llm_pack"],
            tier="pro",
            api_access=True,
            embedding_ready=False,
            risk_level="low",
            competition_cluster="llm_core",
            layer="intelligence",
            sub_layer="foundation_models",
        )
        d = p.to_dict()
        assert d["id"] == "test_co"
        assert d["api_access"] is True
        assert d["open_source"] is False

    def test_from_dict_round_trip(self):
        p = AIProviderObject(
            id="test_co2",
            name="Test2",
            pricing="paid",
            categories=["developer_tools"],
            core_skill="Skill",
            best_at="Best",
            agent_role="Agent",
            bundle_fit=[],
            tier="enterprise",
            api_access=True,
            embedding_ready=False,
            risk_level="low",
            competition_cluster="dev_tools",
            layer="execution",
            sub_layer="developer_tools",
        )
        d = p.to_dict()
        p2 = AIProviderObject.from_dict(d)
        assert p2.id == p.id
        assert p2.tier == p.tier

    def test_open_source_flag(self):
        p = AIProviderObject(
            id="oss_co",
            name="OSS",
            pricing="open_source",
            categories=["foundation_models"],
            core_skill="S",
            best_at="B",
            agent_role="R",
            bundle_fit=[],
            tier="free",
            api_access=True,
            embedding_ready=False,
            risk_level="low",
            competition_cluster="llm_core",
            layer="intelligence",
            sub_layer="foundation_models",
            open_source=True,
        )
        assert p.open_source is True
        assert p.to_dict()["open_source"] is True


# ===========================================================================
# 2. Taxonomy tests
# ===========================================================================
class TestTaxonomy:
    def test_six_layers_present(self):
        layers = {cat.layer for cat in CATEGORY_TAXONOMY.values()}
        assert len(layers) >= 6

    def test_all_clusters_have_members(self):
        for cluster in AI_CLUSTERS.values():
            assert len(cluster.member_ids) > 0

    def test_pricing_tiers_defined(self):
        assert "free" in PRICING_TIERS
        assert "enterprise" in PRICING_TIERS
        for tier in PRICING_TIERS.values():
            assert tier.priority >= 0


# ===========================================================================
# 3. Provider catalog tests
# ===========================================================================
class TestProviderCatalog:
    def test_catalog_has_200_entries(self):
        assert len(PROVIDER_CATALOG) == 200

    def test_all_ids_unique(self):
        ids = [p.id for p in PROVIDER_CATALOG]
        assert len(ids) == len(set(ids)), "Duplicate provider IDs found"

    def test_by_id_lookup(self):
        assert "openai" in PROVIDER_CATALOG_BY_ID
        assert "anthropic" in PROVIDER_CATALOG_BY_ID
        assert "nvidia_co" in PROVIDER_CATALOG_BY_ID

    def test_openai_entry(self):
        p = PROVIDER_CATALOG_BY_ID["openai"]
        assert p.name == "OpenAI"
        assert p.pricing == "freemium"
        assert "foundation_models" in p.categories
        assert p.embedding_ready is True

    def test_mistral_open_source(self):
        p = PROVIDER_CATALOG_BY_ID["mistral_ai"]
        assert p.open_source is True
        assert p.pricing == "open_source"

    def test_all_entries_have_required_fields(self):
        for p in PROVIDER_CATALOG:
            assert p.id, f"Missing id on {p}"
            assert p.name, f"Missing name on {p}"
            assert p.pricing, f"Missing pricing on {p.id}"
            assert p.agent_role, f"Missing agent_role on {p.id}"
            assert p.tier, f"Missing tier on {p.id}"

    def test_key_providers_present(self):
        required = [
            "openai", "anthropic", "mistral_ai", "cohere", "google_ai_platform",
            "nvidia_co", "databricks_co", "huggingface_co", "pinecone_co",
            "langchain_ai", "github_copilot_co", "midjourney_co", "runway_co",
            "boston_dynamics_ai", "figure_ai_co", "harvey_ai_co",
            "darktrace_co", "crowdstrike_co", "openai",
        ]
        missing = [r for r in required if r not in PROVIDER_CATALOG_BY_ID]
        assert missing == [], f"Missing providers: {missing}"

    def test_categories_from_all_taxonomy_layers(self):
        categories = {c for p in PROVIDER_CATALOG for c in p.categories}
        expected_cats = {
            "foundation_models", "developer_tools", "cloud_infrastructure",
            "hardware_compute", "enterprise_platforms", "conversational_ai",
            "vision_speech_media", "analytics_automation", "security_compliance",
            "robotics_physical_ai", "healthcare_bio", "fintech_risk",
            "legal_contracts", "education_training", "sales_marketing",
            "data_search", "gaming_simulation", "web3_blockchain", "hr_workforce",
            "regional_emerging",
        }
        missing = expected_cats - categories
        assert missing == set(), f"Missing category coverage: {missing}"


# ===========================================================================
# 4. Model Registry (global_sources) tests
# ===========================================================================
class TestModelRegistry:
    def test_ai_provider_registry_200_size(self):
        # Should include all 200 user-specified providers as company-level entries
        assert len(AI_PROVIDER_REGISTRY_200) >= 200

    def test_top_200_is_combined(self):
        assert len(TOP_200_PROVIDERS) >= len(TOP_100_AI_MODELS)
        assert len(TOP_200_PROVIDERS) >= len(AI_PROVIDER_REGISTRY_200)

    def test_all_200_user_providers_in_registry(self):
        required = [
            "openai", "anthropic", "databricks_co", "xai", "scale_ai",
            "mistral_ai", "sambanova", "cohere", "huggingface_co", "perplexity_co",
            "google_ai_platform", "azure_ai_co", "nvidia_co", "ibm_watsonx",
            "aws_ai_co", "datarobot_co", "deepmind", "elevenlabs_co",
            "midjourney_co", "runway_co", "synthesia", "suno_co", "deepl_ai",
            "anysphere_cursor", "writer_ai", "glean", "harvey_ai_co",
            "luminance_ai", "sakana_ai", "together_ai_co", "lambda_cloud",
            "abridge_ai", "speak_ai_co", "snorkel_ai", "stackblitz",
            "vannevar_labs", "vast_data", "hebbia", "clay_ai", "captions_ai",
            "palantir_co", "uipath_co", "automation_anywhere", "c3_ai_co",
            "stability_ai", "character_ai_co", "inflection_ai", "adept_ai",
            "replit_co", "anduril_co", "scale_computing", "anthropic_safety",
            "dataiku_ai", "h2o_co", "graphcore_ai", "cerebras_ai", "groq_ai",
            "aleph_alpha", "baidu_ai", "tencent_ai_lab", "alibaba_damo",
            "sensetime", "uipath_autopilot", "thoughtspot", "fractal_analytics",
            "zeta_alpha", "openrouter_ai", "assemblyai", "speechmatics",
            "resemble_ai", "pika_labs_co", "luma_ai_co", "runpod_ai", "octoml",
            "pinecone_co", "weaviate_co", "redis_ai", "elastic_ai_co",
            "grammarly_co", "jasper_ai_co", "boston_dynamics_ai", "figure_ai_co",
            "sanctuary_ai", "covariant_ai", "nuro", "wayve", "cruise_av",
            "tempus_ai_co", "path_ai", "insilico_medicine", "benevolentai",
            "aidoc", "olive_ai", "kasisto_ai", "zest_ai", "upstart_ai",
            "darktrace_co", "crowdstrike_co", "sentinelone_co", "snyk_ai",
            "coursera_ai_co", "duolingo_ai_co", "khan_academy_ai", "udacity_ai",
            "procore_ai", "aurora_innov", "shield_ai_co", "skydio_ai",
            "samsara_ai", "uipath_test", "gong_io", "chorus_ai", "drift_ai",
            "intercom_ai", "zendesk_ai", "sprinklr_ai", "hootsuite_ai_co",
            "canva_ai_co", "figma_ai_co", "notion_ai_co", "cerebras_cloud",
            "tenstorrent", "mythic_ai", "sima_ai", "gro_intelligence",
            "climate_ai_co", "tomorrow_io", "afresh_ai", "trigo",
            "standard_ai_retail", "ironclad_ai", "evisort", "relativity_ai_co",
            "everlaw", "vectra_ai_co", "cybereason", "arctic_wolf",
            "recursion_pharma", "atomwise", "owkin", "unity_ai", "inworld_ai_co",
            "roblox_ai", "epic_games_ai", "niantic_ai", "magic_leap_ai",
            "snap_ai_co", "opensea_ai", "chainalysis", "fireblocks_ai",
            "deel_ai", "rippling_ai", "workday_ai_co", "sap_ai_co",
            "oracle_ai_co", "servicenow_ai", "snowflake_ai_co", "cloudera_ai",
            "alteryx_ai", "tibco_ai", "codeium", "tabnine", "github_copilot_co",
            "wandb", "langchain_ai", "stripe_ai_co", "plaid_ai",
            "bloomberg_ai_co", "two_sigma_ai", "kensho_ai_co", "vercel_ai",
            "supabase_ai", "neon_db", "modal_labs", "replicate_co", "labelbox",
            "weights_ai", "comet_ml", "otter_ai_co", "descript_co", "tome_ai",
            "copy_ai_co", "lavender_ai", "apollo_io_ai", "zoominfo_ai",
            "clearbit_ai", "docusign_ai_co", "legalzoom_ai", "clio_ai",
            "gusto_ai", "bamboohr_ai", "lattice_ai_co", "veritone", "moveworks",
            "forethought_ai", "abnormal_security", "tessian", "tractable_ai",
            "lemonade_ai_co", "viz_ai_co",
        ]
        missing = [r for r in required if r not in AI_PROVIDER_REGISTRY_200]
        assert missing == [], f"Missing from AI_PROVIDER_REGISTRY_200: {missing}"


# ===========================================================================
# 5. Registry DB tests
# ===========================================================================
class TestRegistryDB:
    def test_init_and_connect(self, tmp_path):
        db_file = tmp_path / "test_registry.db"
        with RegistryDB(db_file) as db:
            assert db.count() == 0

    def test_upsert_and_get(self, tmp_path):
        db_file = tmp_path / "test.db"
        p = PROVIDER_CATALOG_BY_ID["openai"]
        with RegistryDB(db_file) as db:
            db.upsert(p)
            row = db.get("openai")
        assert row is not None
        assert row["name"] == "OpenAI"

    def test_ingest_catalog(self, tmp_path):
        db_file = tmp_path / "ingest.db"
        count = ingest_catalog(PROVIDER_CATALOG, db_path=db_file)
        assert count == 200

    def test_query_by_pricing(self, tmp_path):
        db_file = tmp_path / "q.db"
        ingest_catalog(PROVIDER_CATALOG, db_path=db_file)
        with RegistryDB(db_file) as db:
            oss = db.query(is_open_source=True)
        assert len(oss) > 0
        for r in oss:
            assert r["is_open_source"] == 1

    def test_cluster_members(self, tmp_path):
        db_file = tmp_path / "cluster.db"
        ingest_catalog(PROVIDER_CATALOG, db_path=db_file)
        with RegistryDB(db_file) as db:
            members = db.cluster_members("llm_core")
        assert len(members) >= 3

    def test_stats(self, tmp_path):
        db_file = tmp_path / "stats.db"
        ingest_catalog(PROVIDER_CATALOG, db_path=db_file)
        with RegistryDB(db_file) as db:
            s = db.stats()
        assert s["total"] == 200
        assert s["embedding_ready"] > 0
        assert s["open_source"] > 0

    def test_export_json(self, tmp_path):
        db_file = tmp_path / "exp.db"
        out_file = tmp_path / "export.json"
        ingest_catalog(PROVIDER_CATALOG, db_path=db_file)
        path = export_json(out_path=out_file, db_path=db_file)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["total"] == 200
        assert len(data["providers"]) == 200

    def test_export_json_without_db(self, tmp_path):
        """export_json should fall back to catalog when no DB exists."""
        out_file = tmp_path / "fallback.json"
        path = export_json(out_path=out_file, db_path=None)
        data = json.loads(path.read_text())
        assert data["total"] == 200


# ===========================================================================
# 6. Router Brain tests
# ===========================================================================
class TestProviderSelectorEngine:
    def setup_method(self):
        self.engine = ProviderSelectorEngine()

    def test_select_returns_results(self):
        results = self.engine.select("coding")
        assert len(results) > 0

    def test_select_respects_max_results(self):
        results = self.engine.select("marketing_funnel", max_results=3)
        assert len(results) <= 3

    def test_select_with_pricing_filter(self):
        results = self.engine.select("coding", pricing_filter=["open_source", "freemium"])
        for p in results:
            assert p.pricing in ["open_source", "freemium"]

    def test_select_for_workflow(self):
        result = self.engine.select_for_workflow(["coding", "image_generation"])
        assert "coding" in result
        assert "image_generation" in result


class TestCostOptimizerEngine:
    def setup_method(self):
        self.engine = CostOptimizerEngine()

    def test_cheapest_path_low_priority(self):
        results = self.engine.cheapest_path("coding", priority="low_priority")
        assert len(results) > 0
        for p in results:
            assert p.pricing in ["free", "open_source", "freemium"]

    def test_budget_recommendation_has_three_tiers(self):
        rec = self.engine.budget_recommendation("image_generation")
        assert "free_path" in rec
        assert "balanced_path" in rec
        assert "production_path" in rec


class TestCapabilityGraphEngine:
    def setup_method(self):
        self.engine = CapabilityGraphEngine()

    def test_cluster_map_not_empty(self):
        cm = self.engine.cluster_map()
        assert len(cm) > 0

    def test_neighbors(self):
        # OpenAI competes with other LLMs in same cluster
        neighbors = self.engine.neighbors("openai")
        assert len(neighbors) > 0

    def test_what_can(self):
        result = self.engine.what_can("openai")
        assert result is not None
        assert "generative" in result.lower()

    def test_edge_count(self):
        assert self.engine.edge_count() > 10


class TestFailureRedundancyEngine:
    def setup_method(self):
        self.engine = FailureRedundancyEngine()

    def test_build_chain(self):
        chain = self.engine.build_chain("coding", chain_length=5)
        assert len(chain) > 0
        assert len(chain) <= 5

    def test_mark_failed_excludes_from_next_available(self):
        chain = self.engine.llm_fallback_chain()
        first = chain[0]
        self.engine.mark_failed(first.id)
        nxt = self.engine.next_available(chain)
        assert nxt is not None
        assert nxt.id != first.id

    def test_llm_fallback_chain(self):
        chain = self.engine.llm_fallback_chain()
        ids = [p.id for p in chain]
        assert "openai" in ids
        assert "anthropic" in ids

    def test_failover(self):
        fallbacks = self.engine.failover("openai", "coding")
        assert all(p.id != "openai" for p in fallbacks)

    def test_reset_failures(self):
        self.engine.mark_failed("openai")
        self.engine.reset_failures()
        chain = self.engine.llm_fallback_chain()
        assert self.engine.next_available(chain).id == "openai"


class TestRouterBrain:
    def setup_method(self):
        self.brain = RouterBrain()

    def test_route_marketing(self):
        result = self.brain.route("Build a marketing funnel for my Shopify store")
        assert result.task == "marketing_funnel"
        assert len(result.selected) > 0

    def test_route_coding(self):
        result = self.brain.route("Write a Python function to parse JSON")
        assert result.task == "coding"

    def test_route_image(self):
        result = self.brain.route("Create an AI illustration and art image")
        assert result.task == "image_generation"

    def test_route_legal(self):
        result = self.brain.route("Analyze my legal contract for law compliance")
        assert result.task == "legal_review"

    def test_route_result_has_fallback(self):
        result = self.brain.route("Analyze our sales data")
        assert isinstance(result.fallback_chain, list)

    def test_explain(self):
        explanation = self.brain.explain("openai")
        assert "OpenAI" in explanation
        assert "Foundation LLM Agent" in explanation

    def test_explain_unknown(self):
        result = self.brain.explain("nonexistent_provider_xyz")
        assert "not found" in result


# ===========================================================================
# 7. Bot Provider Mapper tests
# ===========================================================================
class TestBotProviderMapper:
    def setup_method(self):
        self.mapper = BotProviderMapper()

    def test_get_known_bot(self):
        m = self.mapper.get("global_sources_ai_bot")
        assert m is not None
        assert "openai" in m.primary_provider_ids

    def test_get_unknown_bot(self):
        assert self.mapper.get("nonexistent_bot_xyz") is None

    def test_providers_for_bot(self):
        providers = self.mapper.providers_for_bot("marketing_bot")
        assert len(providers) > 0

    def test_providers_for_bot_with_fallbacks(self):
        providers = self.mapper.providers_for_bot("marketing_bot", include_fallbacks=True)
        assert len(providers) >= 3

    def test_bots_using_provider(self):
        bots = self.mapper.bots_using_provider("openai")
        assert len(bots) > 0
        assert "global_sources_ai_bot" in bots

    def test_list_all(self):
        all_mappings = self.mapper.list_all()
        assert len(all_mappings) >= 10

    def test_register_new(self):
        m = BotProviderMapping(
            bot_id="test_new_bot",
            primary_provider_ids=["openai"],
            fallback_provider_ids=["anthropic"],
            task_type="research",
        )
        self.mapper.register(m)
        assert self.mapper.get("test_new_bot") is not None

    def test_summary(self):
        summary = self.mapper.summary()
        assert summary["total_bots_mapped"] >= 10
        assert summary["total_provider_references"] > 0
        assert len(summary["top_providers"]) > 0

    def test_bot_registry_constant(self):
        assert "global_sources_ai_bot" in BOT_MAPPING_REGISTRY

    def test_primary_providers_resolve(self):
        m = self.mapper.get("security_bot")
        primaries = m.primary_providers()
        assert len(primaries) > 0


# ===========================================================================
# 8. Integration: module __init__ exports
# ===========================================================================
class TestModuleInit:
    def test_all_exports_importable(self):
        import bots.ai_provider_registry as reg
        assert hasattr(reg, "RouterBrain")
        assert hasattr(reg, "PROVIDER_CATALOG")
        assert hasattr(reg, "ingest_catalog")
        assert hasattr(reg, "BotProviderMapper")
        assert hasattr(reg, "CATEGORY_TAXONOMY")
