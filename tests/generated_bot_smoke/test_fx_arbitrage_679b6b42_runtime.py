from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_runtime():
    runtime_path = ROOT / 'bots/fx-arbitrage/runtime.py'
    spec = importlib.util.spec_from_file_location('fx_arbitrage_679b6b42' + "_runtime", runtime_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['fx_arbitrage_679b6b42' + "_runtime"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_fx_arbitrage_679b6b42_runtime_smoke():
    profile = json.loads((ROOT / 'bots/fx-arbitrage/bot_profile.json').read_text(encoding="utf-8"))
    module = load_runtime()
    bot = module.create_bot()
    assert isinstance(bot, module.FxArbitrageRuntime)
    assert bot.slug == profile["slug"]
    assert bot.storage_policy()["mode"] == "local_first"
    result = bot.run("generated smoke test", {"profile_status": profile.get("status")})
    assert result["outputs"]["live_external_action_taken"] is False
    assert result["evaluation"]["ready_for_smoke_test"] is True
