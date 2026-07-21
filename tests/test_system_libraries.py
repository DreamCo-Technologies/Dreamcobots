from __future__ import annotations

import json
from pathlib import Path

from tools.generate_system_libraries import LIBRARY_SPECS, build_outputs

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_every_library_covers_every_registered_bot():
    registry = load(ROOT / "config/master_bot_registry.json")
    outputs = build_outputs(registry)

    for name in LIBRARY_SPECS:
        payload = outputs[ROOT / "config/generated/system_libraries" / f"{name}.json"]
        assert payload["count"] == registry["summary"]["bot_count"] == 1248
        assert len(payload["entries"]) == 1248
        assert len({item["bot_id"] for item in payload["entries"]}) == 1248


def test_every_bot_has_secure_api_and_webhook_contracts():
    api_library = load(ROOT / "config/generated/system_libraries/apis.json")
    webhook_library = load(ROOT / "config/generated/system_libraries/webhooks.json")

    for api in api_library["entries"]:
        assert api["base_path"].startswith("/api/v1/bots/")
        assert "rate_limited" in api["controls"]
        assert api["custom_to_bot"] is True
        assert api["shard_path"].startswith("config/generated/system_libraries/apis/")

    api_shards = [load(ROOT / shard_path) for shard_path in api_library["shards"]]
    custom_contracts = [
        entry
        for shard in api_shards
        for entry in shard["entries"]
    ]
    assert len(custom_contracts) == 1248
    for api in custom_contracts:
        assert api["custom_contract"]["custom_to_bot"] is True
        assert any("/capabilities/" in item["path"] for item in api["operations"])
        execute = next(item for item in api["operations"] if item["path"] == "/execute-reviewed-packet")
        assert execute["approval_required"] is True

    for webhook in webhook_library["entries"]:
        assert "hmac_sha256_signature" in webhook["controls"]
        assert "delivery_id_deduplication" in webhook["controls"]
        assert "asynchronous_processing" in webhook["controls"]


def test_system_index_reports_complete_coverage():
    index = load(ROOT / "config/generated/system_libraries/index.json")

    assert len(index["builders"]) == 8
    assert len(index["libraries"]) == 7
    assert all(value == 1248 for value in index["coverage"].values())
    assert index["coverage"]["bots_with_custom_api_contracts"] == 1248
