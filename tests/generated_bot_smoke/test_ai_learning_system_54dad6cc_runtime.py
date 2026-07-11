from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_runtime():
    runtime_path = ROOT / 'bots/ai_learning_system/runtime.py'
    spec = importlib.util.spec_from_file_location('ai_learning_system_54dad6cc' + "_runtime", runtime_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['ai_learning_system_54dad6cc' + "_runtime"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_ai_learning_system_54dad6cc_runtime_smoke():
    profile = json.loads((ROOT / 'bots/ai_learning_system/bot_profile.json').read_text(encoding="utf-8"))
    module = load_runtime()
    bot = module.create_bot()
    assert isinstance(bot, module.AiLearningSystemRuntime)
    assert bot.slug == profile["slug"]
    assert bot.storage_policy()["mode"] == "local_first"
    result = bot.run("generated smoke test", {"profile_status": profile.get("status")})
    assert result["outputs"]["live_external_action_taken"] is False
    assert result["evaluation"]["ready_for_smoke_test"] is True
