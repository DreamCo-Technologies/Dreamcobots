from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_runtime():
    runtime_path = ROOT / 'bots/trading-bot-mgr/runtime.py'
    spec = importlib.util.spec_from_file_location('trading_bot_mgr_66da55b5' + "_runtime", runtime_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['trading_bot_mgr_66da55b5' + "_runtime"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_trading_bot_mgr_66da55b5_runtime_smoke():
    profile = json.loads((ROOT / 'bots/trading-bot-mgr/bot_profile.json').read_text(encoding="utf-8"))
    module = load_runtime()
    bot = module.create_bot()
    assert isinstance(bot, module.TradingBotMgrRuntime)
    assert bot.slug == profile["slug"]
    assert bot.storage_policy()["mode"] == "local_first"
    result = bot.run("generated smoke test", {"profile_status": profile.get("status")})
    assert result["outputs"]["live_external_action_taken"] is False
    assert result["evaluation"]["ready_for_smoke_test"] is True
