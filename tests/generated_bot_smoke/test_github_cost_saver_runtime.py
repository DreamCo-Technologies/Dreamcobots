from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_runtime():
    runtime_path = ROOT / "bots/github-cost-saver/runtime.py"
    spec = importlib.util.spec_from_file_location("github_cost_saver_runtime", runtime_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["github_cost_saver_runtime"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_github_cost_saver_runtime_smoke(tmp_path):
    profile = json.loads((ROOT / "bots/github-cost-saver/bot_profile.json").read_text(encoding="utf-8"))
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text(
        """
name: ci
on:
  schedule:
    - cron: "0 * * * *"
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/upload-artifact@v4
        with:
          name: report
          path: reports
""",
        encoding="utf-8",
    )

    module = load_runtime()
    bot = module.create_bot()
    assert isinstance(bot, module.GitHubCostSaverRuntime)
    assert bot.slug == profile["slug"]
    assert bot.storage_policy()["mode"] == "local_first"
    result = bot.run("generated smoke test", {"repo_path": tmp_path})
    assert result["live_external_action_taken"] is False
    assert result["evaluation"]["ready_for_smoke_test"] is True
