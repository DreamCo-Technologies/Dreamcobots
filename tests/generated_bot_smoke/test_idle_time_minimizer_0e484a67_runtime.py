from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_runtime():
    runtime_path = ROOT / 'bots/idle-time-minimizer/runtime.py'
    spec = importlib.util.spec_from_file_location('idle_time_minimizer_0e484a67' + "_runtime", runtime_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['idle_time_minimizer_0e484a67' + "_runtime"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_idle_time_minimizer_0e484a67_runtime_smoke():
    profile = json.loads((ROOT / 'bots/idle-time-minimizer/bot_profile.json').read_text(encoding="utf-8"))
    module = load_runtime()
    bot = module.create_bot()
    assert isinstance(bot, module.IdleTimeMinimizerRuntime)
    assert bot.slug == profile["slug"]
    assert bot.storage_policy()["mode"] == "local_first"
    result = bot.run("generated smoke test", {"profile_status": profile.get("status")})
    assert result["outputs"]["live_external_action_taken"] is False
    assert result["evaluation"]["ready_for_smoke_test"] is True
