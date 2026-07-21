from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP_BOTS_DIR = ROOT / "App_bots"


def test_division_json_systems_have_local_contracts():
    files = sorted(APP_BOTS_DIR.glob("*.json"))
    assert files, "division JSON systems must exist"
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict), path
        assert payload.get("name") or path.stem
        child_bots = payload.get("bots") if isinstance(payload.get("bots"), list) else []
        assert payload.get("mission") or payload.get("description") or payload.get("capabilities") or payload.get("systems") or child_bots
        if child_bots:
            first = child_bots[0]
            assert isinstance(first, dict), path
            assert first.get("description") or first.get("capabilities"), path


def test_division_json_systems_are_sandbox_first():
    readiness_index = json.loads(
        (ROOT / "config/generated/bot_end_to_end_readiness/index.json").read_text(encoding="utf-8")
    )
    policy = readiness_index["policy"]
    assert policy["default_execution"] == "local_first_no_external_provider_required"
    assert "optional" in policy["external_models"]
    assert policy["approval_required_for"]
