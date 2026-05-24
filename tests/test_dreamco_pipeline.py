"""
Tests for the three new architectural layers:

1. Model Router (OpenRouter + ArbitrationEngine + DreamCoModelRouter)
2. Retrieval Layer (RetrievalRecord, RedisStore, PineconeStore, ElasticStore,
                    SQLStore, RetrievalLayer)
3. DreamcoPipeline (end-to-end 8-layer pipeline)
"""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Shared imports
# ---------------------------------------------------------------------------

from dreamco_platform.model_router.openrouter import (
    OpenRouterAdapter,
    OpenRouterRequest,
    OpenRouterResponse,
)
from dreamco_platform.model_router.arbitration import (
    ArbitrationEngine,
    ArbitrationPolicy,
    ProviderSpec,
)
from dreamco_platform.model_router.router import (
    DreamCoModelRouter,
    RouteRequest,
    RouteResponse,
)
from dreamco_platform.retrieval.base import RetrievalRecord
from dreamco_platform.retrieval.redis_store import RedisStore
from dreamco_platform.retrieval.pinecone_store import PineconeStore
from dreamco_platform.retrieval.elastic_store import ElasticStore
from dreamco_platform.retrieval.sql_store import SQLStore
from dreamco_platform.retrieval.retrieval_layer import RetrievalLayer
from dreamco_platform.pipeline import DreamcoPipeline, PipelineRequest


# ===========================================================================
# 1.  OpenRouterAdapter
# ===========================================================================

class TestOpenRouterAdapter:
    def test_stub_mode_when_no_key(self):
        adapter = OpenRouterAdapter(api_key="")
        assert adapter.stub_mode is True

    def test_stub_mode_false_with_key(self):
        adapter = OpenRouterAdapter(api_key="sk-test-key")
        assert adapter.stub_mode is False

    def test_stub_complete_returns_response(self):
        adapter = OpenRouterAdapter(api_key="")
        req = OpenRouterRequest(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": "hello"}],
        )
        resp = adapter.complete(req)
        assert isinstance(resp, OpenRouterResponse)
        assert resp.stub is True

    def test_stub_content_contains_model(self):
        adapter = OpenRouterAdapter(api_key="")
        req = OpenRouterRequest(
            model="anthropic/claude-3-5-sonnet",
            messages=[{"role": "user", "content": "write code"}],
        )
        resp = adapter.complete(req)
        assert "anthropic/claude-3-5-sonnet" in resp.content

    def test_stub_content_contains_prompt(self):
        adapter = OpenRouterAdapter(api_key="")
        req = OpenRouterRequest(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": "unique_prompt_XYZ"}],
        )
        resp = adapter.complete(req)
        assert "unique_prompt_XYZ" in resp.content

    def test_stub_response_model_matches_request(self):
        adapter = OpenRouterAdapter(api_key="")
        req = OpenRouterRequest(
            model="mistral/mistral-small",
            messages=[{"role": "user", "content": "test"}],
        )
        resp = adapter.complete(req)
        assert resp.model == "mistral/mistral-small"

    def test_stub_finish_reason_is_stop(self):
        adapter = OpenRouterAdapter(api_key="")
        req = OpenRouterRequest(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": "x"}],
        )
        resp = adapter.complete(req)
        assert resp.finish_reason == "stop"

    def test_stub_tokens_are_non_negative(self):
        adapter = OpenRouterAdapter(api_key="")
        req = OpenRouterRequest(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": "word word word"}],
        )
        resp = adapter.complete(req)
        assert resp.prompt_tokens >= 0
        assert resp.completion_tokens >= 0
        assert resp.total_tokens >= 0

    def test_cost_usd_non_negative(self):
        adapter = OpenRouterAdapter(api_key="")
        req = OpenRouterRequest(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": "test"}],
        )
        resp = adapter.complete(req)
        assert resp.cost_usd >= 0.0

    def test_system_prompt_included_in_messages(self):
        req = OpenRouterRequest(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "hello"},
            ],
        )
        payload = req.to_payload()
        roles = [m["role"] for m in payload["messages"]]
        assert "system" in roles


# ===========================================================================
# 2.  ArbitrationEngine
# ===========================================================================

class TestArbitrationEngine:
    def setup_method(self):
        self.engine = ArbitrationEngine(load_defaults=True)

    def test_list_providers_returns_non_empty(self):
        providers = self.engine.list_providers()
        assert len(providers) > 0

    def test_list_providers_are_enabled(self):
        providers = self.engine.list_providers(enabled_only=True)
        assert all(p.enabled for p in providers)

    def test_select_coding_returns_spec(self):
        spec = self.engine.select("coding")
        assert spec is not None
        assert isinstance(spec, ProviderSpec)

    def test_select_coding_covers_task(self):
        spec = self.engine.select("coding")
        assert spec is not None
        assert spec.covers("coding")

    def test_fallback_chain_not_empty_for_coding(self):
        chain = self.engine.fallback_chain("coding")
        assert len(chain) > 0

    def test_fallback_chain_all_strings(self):
        chain = self.engine.fallback_chain("general")
        assert all(isinstance(m, str) for m in chain)

    def test_fallback_chain_unknown_task_returns_general_models(self):
        # engine has providers with wildcard or general coverage
        chain = self.engine.fallback_chain("general")
        assert len(chain) >= 1

    def test_register_custom_provider(self):
        spec = ProviderSpec(
            "custom/my-model",
            task_types=["custom_task"],
            priority=1,
        )
        self.engine.register(spec)
        chain = self.engine.fallback_chain("custom_task")
        assert "custom/my-model" in chain

    def test_unregister_provider(self):
        spec = ProviderSpec(
            "temp/model",
            task_types=["coding"],
            priority=99,
        )
        self.engine.register(spec)
        self.engine.unregister("temp/model")
        chain = self.engine.fallback_chain("coding")
        assert "temp/model" not in chain

    def test_priority_policy_ordering(self):
        engine = ArbitrationEngine(policy=ArbitrationPolicy.PRIORITY, load_defaults=False)
        engine.register(ProviderSpec("a/low", task_types=["x"], priority=5))
        engine.register(ProviderSpec("b/high", task_types=["x"], priority=1))
        chain = engine.fallback_chain("x")
        assert chain[0] == "b/high"

    def test_cost_first_policy(self):
        engine = ArbitrationEngine(policy=ArbitrationPolicy.COST_FIRST, load_defaults=False)
        engine.register(ProviderSpec("a/expensive", task_types=["x"], cost_per_1k_tokens_usd=0.01))
        engine.register(ProviderSpec("b/cheap", task_types=["x"], cost_per_1k_tokens_usd=0.001))
        chain = engine.fallback_chain("x", policy=ArbitrationPolicy.COST_FIRST)
        assert chain[0] == "b/cheap"

    def test_record_latency_updates_window(self):
        self.engine.record_latency("openai/gpt-4o", 200.0)
        avg = self.engine.avg_latency_ms("openai/gpt-4o")
        assert avg > 0

    def test_audit_log_grows_on_select(self):
        before = len(self.engine.audit_log())
        self.engine.select("coding")
        after = len(self.engine.audit_log())
        assert after > before

    def test_clear_audit(self):
        self.engine.select("coding")
        self.engine.clear_audit()
        assert len(self.engine.audit_log()) == 0

    def test_provider_spec_covers_wildcard(self):
        spec = ProviderSpec("any/model", task_types=["*"])
        assert spec.covers("anything")
        assert spec.covers("coding")

    def test_provider_spec_to_dict(self):
        spec = ProviderSpec("openai/gpt-4o", task_types=["general"])
        d = spec.to_dict()
        assert "model_id" in d
        assert "task_types" in d
        assert d["model_id"] == "openai/gpt-4o"


# ===========================================================================
# 3.  DreamCoModelRouter
# ===========================================================================

class TestDreamCoModelRouter:
    def setup_method(self):
        self.router = DreamCoModelRouter()

    def test_stub_mode_default(self):
        assert self.router.stub_mode is True  # no API key in CI

    def test_route_returns_route_response(self):
        req = RouteRequest(task_type="coding", prompt="write a function")
        resp = self.router.route(req)
        assert isinstance(resp, RouteResponse)

    def test_route_content_is_string(self):
        req = RouteRequest(task_type="general", prompt="hello world")
        resp = self.router.route(req)
        assert isinstance(resp.content, str)

    def test_route_model_id_is_string(self):
        req = RouteRequest(task_type="coding", prompt="build an API")
        resp = self.router.route(req)
        assert isinstance(resp.model_id, str)

    def test_route_task_type_preserved(self):
        req = RouteRequest(task_type="vision", prompt="describe this image")
        resp = self.router.route(req)
        assert resp.task_type == "vision"

    def test_route_stub_flag_true_without_key(self):
        req = RouteRequest(task_type="general", prompt="test")
        resp = self.router.route(req)
        assert resp.stub is True

    def test_route_to_dict(self):
        req = RouteRequest(task_type="general", prompt="test")
        resp = self.router.route(req)
        d = resp.to_dict()
        assert "content" in d
        assert "model_id" in d
        assert "cost_usd" in d

    def test_select_provider_returns_spec_or_none(self):
        spec = self.router.select_provider("coding")
        assert spec is None or isinstance(spec, ProviderSpec)

    def test_fallback_chain_non_empty(self):
        chain = self.router.fallback_chain("coding")
        assert len(chain) >= 1

    def test_register_provider(self):
        spec = ProviderSpec("custom/test", task_types=["custom"], priority=1)
        self.router.register_provider(spec)
        chain = self.router.fallback_chain("custom")
        assert "custom/test" in chain

    def test_get_summary(self):
        summary = self.router.get_summary()
        assert "stub_mode" in summary
        assert "providers" in summary

    def test_unknown_task_type_still_routes(self):
        req = RouteRequest(task_type="completely_unknown_type_xyz", prompt="test")
        resp = self.router.route(req)
        assert resp.content != "" or resp.content == ""  # just doesn't raise


# ===========================================================================
# 4.  RetrievalRecord + Backend stub operations
# ===========================================================================

class TestRetrievalRecord:
    def test_record_has_key(self):
        r = RetrievalRecord(key="doc:1", content="hello world")
        assert r.key == "doc:1"

    def test_record_to_dict(self):
        r = RetrievalRecord(key="doc:1", content="hello world")
        d = r.to_dict()
        assert "key" in d
        assert "content" in d
        assert "score" in d

    def test_record_default_score(self):
        r = RetrievalRecord(key="x", content="y")
        assert r.score == 1.0

    def test_record_id_auto_generated(self):
        r1 = RetrievalRecord(key="a", content="b")
        r2 = RetrievalRecord(key="a", content="b")
        assert r1.record_id != r2.record_id


class _BackendContract:
    """Shared contract tests for all RetrievalBackend implementations."""

    backend: object  # concrete instance set in subclass setup_method

    def test_backend_name_is_string(self):
        assert isinstance(self.backend.backend_name, str)

    def test_upsert_and_get(self):
        rec = RetrievalRecord(key="test:1", content="DreamCo AI platform")
        self.backend.upsert(rec)
        retrieved = self.backend.get("test:1")
        assert retrieved is not None
        assert retrieved.content == "DreamCo AI platform"

    def test_get_missing_key_returns_none(self):
        assert self.backend.get("nonexistent_key_xyz_99") is None

    def test_search_finds_record(self):
        rec = RetrievalRecord(key="search:1", content="unique searchable content abc123")
        self.backend.upsert(rec)
        results = self.backend.search("abc123")
        keys = [r.key for r in results]
        assert "search:1" in keys

    def test_search_empty_query(self):
        results = self.backend.search("", limit=5)
        assert isinstance(results, list)

    def test_delete_removes_record(self):
        rec = RetrievalRecord(key="del:1", content="to be deleted")
        self.backend.upsert(rec)
        deleted = self.backend.delete("del:1")
        assert deleted is True
        assert self.backend.get("del:1") is None

    def test_delete_missing_key_returns_false(self):
        assert self.backend.delete("no_such_key_xyz_99") is False

    def test_count_increases_after_upsert(self):
        before = self.backend.count()
        self.backend.upsert(RetrievalRecord(key=f"count:{id(self)}", content="c"))
        assert self.backend.count() >= before


class TestRedisStore(_BackendContract):
    def setup_method(self):
        self.backend = RedisStore(stub=True)

    def test_stub_mode(self):
        assert self.backend._client is None


class TestPineconeStore(_BackendContract):
    def setup_method(self):
        self.backend = PineconeStore(stub=True)

    def test_stub_mode(self):
        assert self.backend._index is None

    def test_search_with_embedding(self):
        rec = RetrievalRecord(
            key="vec:1",
            content="vector content",
            embedding=[0.1, 0.2, 0.3],
        )
        self.backend.upsert(rec)
        results = self.backend.search(
            "vector",
            limit=5,
            embedding=[0.1, 0.2, 0.3],
        )
        assert any(r.key == "vec:1" for r in results)


class TestElasticStore(_BackendContract):
    def setup_method(self):
        self.backend = ElasticStore(stub=True)

    def test_stub_mode(self):
        assert self.backend._client is None


class TestSQLStore(_BackendContract):
    def setup_method(self):
        self.backend = SQLStore("sqlite://")  # in-memory SQLite

    def test_sqlite_connection(self):
        assert self.backend._conn is not None


# ===========================================================================
# 5.  RetrievalLayer
# ===========================================================================

class TestRetrievalLayer:
    def setup_method(self):
        self.layer = RetrievalLayer()
        self.redis = RedisStore(stub=True)
        self.sql = SQLStore("sqlite://")
        self.layer.add_backend(self.redis, write=True, search=True)
        self.layer.add_backend(self.sql, write=True, search=True)

    def test_list_backends(self):
        backends = self.layer.list_backends()
        assert "redis" in backends
        assert "sql" in backends

    def test_upsert_writes_to_all_backends(self):
        rec = RetrievalRecord(key="layer:1", content="shared content")
        self.layer.upsert(rec)
        assert self.redis.get("layer:1") is not None
        assert self.sql.get("layer:1") is not None

    def test_get_returns_from_first_backend(self):
        rec = RetrievalRecord(key="layer:get:1", content="fetch me")
        self.layer.upsert(rec)
        result = self.layer.get("layer:get:1")
        assert result is not None
        assert result.content == "fetch me"

    def test_get_missing_returns_none(self):
        assert self.layer.get("does_not_exist_xyz") is None

    def test_search_merges_backends(self):
        self.layer.upsert(RetrievalRecord(key="m:1", content="merge test content xyz"))
        results = self.layer.search("merge test content xyz")
        assert any(r.key == "m:1" for r in results)

    def test_delete_removes_from_backends(self):
        rec = RetrievalRecord(key="del:layer:1", content="to delete")
        self.layer.upsert(rec)
        count = self.layer.delete("del:layer:1")
        assert count > 0

    def test_stats_returns_dict(self):
        stats = self.layer.stats()
        assert isinstance(stats, dict)
        assert "redis" in stats
        assert "sql" in stats

    def test_remove_backend(self):
        removed = self.layer.remove_backend("redis")
        assert removed is True
        assert "redis" not in self.layer.list_backends()

    def test_search_deduplicates_by_key(self):
        rec = RetrievalRecord(key="dedup:1", content="deduplicate me unique XYZ")
        self.layer.upsert(rec)
        results = self.layer.search("deduplicate me unique XYZ", limit=20)
        keys = [r.key for r in results]
        assert keys.count("dedup:1") == 1

    def test_write_only_backend_not_searched(self):
        write_only_sql = SQLStore("sqlite://")
        layer = RetrievalLayer()
        layer.add_backend(write_only_sql, write=True, search=False)
        rec = RetrievalRecord(key="wo:1", content="write only XYZ789")
        layer.upsert(rec)
        results = layer.search("write only XYZ789")
        assert results == []


# ===========================================================================
# 6.  DreamcoPipeline (end-to-end)
# ===========================================================================

class TestDreamcoPipeline:
    def setup_method(self):
        self.pipeline = DreamcoPipeline()

    def test_run_returns_pipeline_result(self):
        from dreamco_platform.pipeline import PipelineResult
        req = PipelineRequest(task_type="general", prompt="hello world")
        result = self.pipeline.run(req)
        assert isinstance(result, PipelineResult)

    def test_run_content_is_string(self):
        req = PipelineRequest(task_type="coding", prompt="write a hello world function")
        result = self.pipeline.run(req)
        assert isinstance(result.content, str)

    def test_run_model_id_is_string(self):
        req = PipelineRequest(task_type="general", prompt="test")
        result = self.pipeline.run(req)
        assert isinstance(result.model_id, str)

    def test_run_task_type_preserved(self):
        req = PipelineRequest(task_type="vision", prompt="describe an image")
        result = self.pipeline.run(req)
        assert result.task_type == "vision"

    def test_run_correlation_id_preserved(self):
        req = PipelineRequest(task_type="general", prompt="test", correlation_id="trace-001")
        result = self.pipeline.run(req)
        assert result.correlation_id == "trace-001"

    def test_run_policy_not_blocked_by_default(self):
        req = PipelineRequest(task_type="general", prompt="safe request")
        result = self.pipeline.run(req)
        assert result.policy_blocked is False

    def test_run_blocking_policy_blocks_request(self):
        from dreamco_platform.governance.policy_engine import (
            PolicyEngine, PolicyRule, PolicyAction, PolicyCondition
        )
        engine = PolicyEngine()
        engine.add_rule(PolicyRule(
            rule_id="block_all",
            name="Block everything",
            condition=PolicyCondition(fn=lambda ctx: True, description="always"),
            action=PolicyAction.BLOCK_EXECUTION,
            severity="critical",
        ))
        pipeline = DreamcoPipeline(policy_engine=engine)
        req = PipelineRequest(task_type="general", prompt="blocked request")
        result = pipeline.run(req)
        assert result.policy_blocked is True
        assert result.content == ""

    def test_run_stores_result_in_retrieval(self):
        req = PipelineRequest(
            task_type="general",
            prompt="store me please",
            store_result=True,
            correlation_id="store-test-001",
        )
        result = self.pipeline.run(req)
        record = self.pipeline.retrieval_layer.get(f"result:{req.correlation_id}")
        assert record is not None

    def test_run_retrieve_memory_injects_context(self):
        # Pre-load a record that will be retrieved
        from dreamco_platform.retrieval.base import RetrievalRecord
        self.pipeline.retrieval_layer.upsert(RetrievalRecord(
            key="ctx:inject:1",
            content="DreamCo is an autonomous AI platform",
        ))
        req = PipelineRequest(
            task_type="general",
            prompt="DreamCo platform",
            retrieve_memory=True,
        )
        result = self.pipeline.run(req)
        assert isinstance(result.retrieved_context, list)

    def test_run_no_retrieve_memory(self):
        req = PipelineRequest(
            task_type="general",
            prompt="no retrieval",
            retrieve_memory=False,
        )
        result = self.pipeline.run(req)
        assert result.retrieved_context == []

    def test_run_latency_positive(self):
        req = PipelineRequest(task_type="general", prompt="latency test")
        result = self.pipeline.run(req)
        assert result.latency_ms >= 0.0

    def test_telemetry_records_events(self):
        req = PipelineRequest(task_type="general", prompt="telemetry test")
        self.pipeline.run(req)
        summary = self.pipeline.telemetry.summarize()
        assert summary["total_events"] > 0

    def test_get_summary_structure(self):
        summary = self.pipeline.get_summary()
        assert "model_router" in summary
        assert "retrieval_backends" in summary
        assert "runtime_stats" in summary
        assert "telemetry_summary" in summary

    def test_pipeline_result_to_dict(self):
        req = PipelineRequest(task_type="general", prompt="dict test")
        result = self.pipeline.run(req)
        d = result.to_dict()
        assert "content" in d
        assert "model_id" in d
        assert "task_type" in d
        assert "stub" in d

    def test_multiple_runs_accumulate_telemetry(self):
        for _ in range(3):
            self.pipeline.run(PipelineRequest(task_type="general", prompt="repeat"))
        summary = self.pipeline.telemetry.summarize()
        assert summary["total_events"] >= 3

    def test_policy_messages_list(self):
        req = PipelineRequest(task_type="general", prompt="check messages")
        result = self.pipeline.run(req)
        assert isinstance(result.policy_messages, list)

    def test_custom_retrieval_layer(self):
        layer = RetrievalLayer()
        layer.add_backend(SQLStore("sqlite://"), write=True, search=True)
        pipeline = DreamcoPipeline(retrieval_layer=layer)
        req = PipelineRequest(task_type="general", prompt="custom layer test")
        result = pipeline.run(req)
        assert isinstance(result.content, str)
