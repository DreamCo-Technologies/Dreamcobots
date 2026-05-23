from __future__ import annotations

from bots.media_runtime import InferenceGateway, LocalAssetStore, MediaJobRuntime


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
