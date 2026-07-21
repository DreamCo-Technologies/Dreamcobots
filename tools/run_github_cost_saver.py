#!/usr/bin/env python3
"""Run GitHub Cost Saver Bot against the current repository."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "bots" / "github-cost-saver" / "runtime.py"


def load_runtime():
    spec = importlib.util.spec_from_file_location("github_cost_saver_runtime", RUNTIME_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["github_cost_saver_runtime"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_runtime()
    bot = module.create_bot()
    result = bot.run("scan repository for GitHub cost savings", {"repo_path": ROOT, "write_report": True})
    print(json.dumps({
        "bot": result["bot"],
        "report_path": result["report_path"],
        "summary": result["summary"],
        "top_recommendations": result["recommendations"][:4],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
