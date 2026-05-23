from __future__ import annotations

import time

from bots.media_runtime import (
    DurableMediaQueue,
    InferenceGateway,
    MEDIA_LIFECYCLE_STATES,
    LocalAssetStore,
    MediaEngine,
    MediaJobRuntime,
    QueuePriority,
)
from bots.media_runtime.state import AssetRegistry, ExecutionStateStore, RenderJobRepository


def test_runtime_job_lifecycle_completes_with_persisted_asset(tmp_path):
    store = LocalAssetStore(root_dir=str(tmp_path / "assets"))
    runtime = MediaJobRuntime(asset_store=store, gateway=InferenceGateway())

    runtime.create_job(
        owner="test",
        media_type="audio",
        operation="text_to_music",
        payload={"text": "hello world"},
        provider_chain=["openai"],
        estimated_duration_sec=15,
        max_retries=1,
    )

    job, asset = runtime.process_next(
        media_format="mp3",
        content_type="audio/mpeg",
        extra_metadata={"scenario": "unit_test"},
    )

    assert job.state.value == "completed"
    assert job.progress_percent == 100
    assert asset.status == "active"
    assert asset.storage_path.endswith(".mp3")


def test_gateway_fallback_uses_second_provider():
    gateway = InferenceGateway()

    def _always_fail(_request):
        raise RuntimeError("primary_down")

    gateway.register_provider("broken", _always_fail, initial_health=1.0)
    result = gateway.run({"media_type": "video", "operation": "render", "script": "demo"}, ["broken", "openai"])

    assert result.provider == "openai"
    assert gateway.telemetry["fallbacks"] >= 1
    assert gateway.provider_health["broken"] < 1.0


def test_media_engine_routes_provider_chain_by_media_type(tmp_path):
    gateway = InferenceGateway()
    store = LocalAssetStore(root_dir=str(tmp_path / "assets"))
    runtime = MediaJobRuntime(asset_store=store, gateway=gateway)
    engine = MediaEngine(owner="test_media_engine", runtime=runtime, asset_store=store)

    _, asset = engine.execute_render(
        operation="render_video",
        media_type="video",
        payload={"script": "hello"},
        output_format="mp4",
        output_content_type="video/mp4",
    )

    assert asset["provider"] == "ffmpeg-local"


def test_media_engine_persists_job_and_asset_with_repositories(tmp_path):
    gateway = InferenceGateway()
    store = LocalAssetStore(root_dir=str(tmp_path / "assets"))
    runtime = MediaJobRuntime(asset_store=store, gateway=gateway)
    state_store = ExecutionStateStore(file_path=str(tmp_path / "execution_state.json"))
    job_repo = RenderJobRepository(state_store)
    asset_registry = AssetRegistry(state_store)
    engine = MediaEngine(
        owner="test_media_engine",
        runtime=runtime,
        asset_store=store,
        job_repository=job_repo,
        asset_registry=asset_registry,
    )

    job, asset = engine.execute_render(
        operation="render_audio",
        media_type="audio",
        payload={"text": "music"},
        output_format="mp3",
        output_content_type="audio/mpeg",
    )
    persisted = engine.persist_artifact(
        originating_job=job["job_id"],
        provider="ffmpeg-local",
        media_format="json",
        content_type="application/json",
        content_bytes=b"{\"status\":\"ok\"}",
        lineage=[asset["asset_id"]],
        metadata={"kind": "manifest"},
    )

    assert job_repo.get(job["job_id"])["state"] == "completed"
    assert asset_registry.get(asset["asset_id"])["originating_job"] == job["job_id"]
    assert asset_registry.get(persisted["asset_id"])["metadata"]["kind"] == "manifest"


def test_media_engine_telemetry_snapshot_tracks_runtime_metrics(tmp_path):
    gateway = InferenceGateway()
    store = LocalAssetStore(root_dir=str(tmp_path / "assets"))
    runtime = MediaJobRuntime(asset_store=store, gateway=gateway)
    engine = MediaEngine(owner="test_media_engine", runtime=runtime, asset_store=store)

    engine.execute_render(
        operation="render_image",
        media_type="image",
        payload={"prompt": "hello"},
        output_format="png",
        output_content_type="image/png",
    )
    snapshot = engine.telemetry_snapshot()

    assert snapshot["execution_count"] == 1
    assert snapshot["avg_execution_ms"] >= 0
    assert snapshot["queue_depth_max"] >= 0
    assert snapshot["artifact_size_bytes_total"] > 0
    assert snapshot["provider_avg_latency_ms"]
    assert "runtime_slo" in snapshot
    assert "provider_governance" in snapshot
    assert "asset_graph" in snapshot


def test_runtime_queue_supports_cancel_dead_letter_and_stall_recovery(tmp_path):
    gateway = InferenceGateway()
    store = LocalAssetStore(root_dir=str(tmp_path / "assets"))
    runtime = MediaJobRuntime(asset_store=store, gateway=gateway, queue=DurableMediaQueue(max_depth=5))

    job = runtime.create_job(
        owner="test",
        media_type="audio",
        operation="text_to_music",
        payload={"text": "hello world"},
        provider_chain=["openai"],
        estimated_duration_sec=10,
        max_retries=1,
        priority=QueuePriority.HIGH,
    )
    assert runtime.cancel_job(job.job_id) is True
    assert runtime.get_job(job.job_id).state.value == "canceled"
    assert runtime.queue_snapshot()["canceled_count"] >= 1

    job_2 = runtime.create_job(
        owner="test",
        media_type="audio",
        operation="text_to_music",
        payload={"text": "queued"},
        provider_chain=["openai"],
        estimated_duration_sec=10,
        max_retries=1,
    )
    runtime._queue._items[job_2.job_id].leased_by = "worker"
    runtime._queue._items[job_2.job_id].lease_until = time.time() - 5
    assert runtime.recover_stalled_jobs(stall_after_seconds=0) >= 1


def test_provider_governance_scorecards_include_latency_reliability_and_cost():
    gateway = InferenceGateway()
    _ = gateway.run({"media_type": "audio", "operation": "render", "text": "hello"}, ["openai"])
    snapshot = gateway.provider_governance_snapshot()
    assert snapshot["scorecards"]["openai"]["avg_latency_ms"] >= 0
    assert snapshot["scorecards"]["openai"]["reliability"] >= 0
    assert snapshot["scorecards"]["openai"]["avg_cost"] >= 0


def test_provider_governance_fallback_and_policy_routing_for_video():
    gateway = InferenceGateway()

    def _always_fail(_request):
        raise RuntimeError("provider_outage")

    gateway.register_provider("broken", _always_fail, initial_health=1.0)
    fallback_result = gateway.run(
        {"media_type": "video", "operation": "render", "script": "demo"},
        ["broken", "openai"],
    )
    assert fallback_result.provider == "openai"
    assert gateway.telemetry["fallbacks"] >= 1

    result = gateway.run(
        {"media_type": "video", "operation": "render", "script": "demo"},
        ["broken", "openai", "ffmpeg-local"],
        policy_context={"media_type": "video", "tier": "enterprise", "latency_target_ms": 1200},
    )

    assert result.provider in {"openai", "ffmpeg-local"}
    assert gateway.provider_health["broken"] < 1.0


def test_runtime_transitions_to_dead_lettered_after_retry_exhaustion(tmp_path):
    gateway = InferenceGateway()
    store = LocalAssetStore(root_dir=str(tmp_path / "assets"))
    runtime = MediaJobRuntime(asset_store=store, gateway=gateway)

    def _fail(_request):
        raise RuntimeError("provider hard fail")

    gateway.register_provider("always_fail", _fail, initial_health=1.0)
    job = runtime.create_job(
        owner="test",
        media_type="audio",
        operation="text_to_music",
        payload={"text": "hard fail"},
        provider_chain=["always_fail"],
        max_retries=1,
    )

    try:
        runtime.process_next(media_format="mp3", content_type="audio/mpeg")
    except Exception:
        pass

    assert runtime.get_job(job.job_id).state.value == "dead_lettered"
    assert runtime.queue_snapshot()["dead_letter_count"] >= 1


def test_runtime_state_set_matches_global_contract():
    observed_states = {
        "queued",
        "running",
        "completed",
        "failed",
        "canceled",
        "retrying",
        "dead_lettered",
        "stalled",
    }
    assert observed_states == set(MEDIA_LIFECYCLE_STATES)


def test_asset_graph_tracks_lineage_and_consistency(tmp_path):
    store = LocalAssetStore(root_dir=str(tmp_path / "assets"))
    root = store.persist(
        owner="test",
        originating_job="job_1",
        provider="openai",
        media_format="png",
        content_type="image/png",
        content_bytes=b"root",
    )
    child = store.persist(
        owner="test",
        originating_job="job_2",
        provider="openai",
        media_format="png",
        content_type="image/png",
        content_bytes=b"child",
        lineage=[root.asset_id],
    )
    context = store.graph_context(child.asset_id)
    assert root.asset_id in context["ancestors"]
    assert store.graph_snapshot()["consistency_valid"] is True
