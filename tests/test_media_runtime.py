from __future__ import annotations

from bots.media_runtime import (
    InferenceGateway,
    LocalAssetStore,
    MediaEngine,
    MediaJobRuntime,
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
