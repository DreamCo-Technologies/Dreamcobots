from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_runtime():
    runtime_path = ROOT / "bots/github-cost-saver/runtime.py"
    spec = importlib.util.spec_from_file_location("github_cost_saver_runtime", runtime_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["github_cost_saver_runtime"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_github_cost_saver_profile_and_policy():
    profile = json.loads((ROOT / "bots/github-cost-saver/bot_profile.json").read_text(encoding="utf-8"))
    module = load_runtime()
    bot = module.create_bot()

    assert isinstance(bot, module.GitHubCostSaverRuntime)
    assert bot.slug == profile["slug"]
    assert bot.storage_policy()["mode"] == "local_first"
    assert bot.billing_policy()["bypass_billing"] is False
    assert bot.billing_policy()["live_external_action_taken"] is False


def test_github_cost_saver_detects_expensive_workflow(tmp_path):
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "expensive.yml").write_text(
        """
name: expensive
on:
  schedule:
    - cron: "*/15 * * * *"
jobs:
  mac:
    runs-on: macos-latest
    steps:
      - uses: actions/upload-artifact@v4
        with:
          name: build
          path: dist
  review:
    runs-on: ubuntu-latest
    steps:
      - run: echo "copilot review pull_request"
""",
        encoding="utf-8",
    )

    module = load_runtime()
    result = module.create_bot().run("scan test repo", {"repo_path": tmp_path})

    categories = {finding["category"] for finding in result["findings"]}
    assert "actions_minutes" in categories
    assert "actions_storage" in categories
    assert "ai_review" in categories
    assert result["summary"]["estimated_monthly_savings_usd"] > 0
    assert result["live_external_action_taken"] is False
    assert result["evaluation"]["ready_for_smoke_test"] is True


def test_github_cost_saver_writes_local_report(tmp_path):
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text(
        """
name: ci
on: [push]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - run: echo test
""",
        encoding="utf-8",
    )

    module = load_runtime()
    bot = module.create_bot()
    result = bot.run("write report", {"repo_path": tmp_path, "write_report": True})

    report_path = Path(result["report_path"])
    assert report_path.exists()
    saved = json.loads(report_path.read_text(encoding="utf-8"))
    assert saved["summary"]["finding_count"] >= 2
    assert bot.events
