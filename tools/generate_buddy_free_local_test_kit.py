#!/usr/bin/env python3
"""Create a free/local-first Buddy test kit for owner laptop validation."""

from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUTONOMY_FILE = ROOT / "config" / "generated" / "buddy_autonomous_everything.json"
LAPTOP_FILE = ROOT / "config" / "buddy_laptop_install.json"
SAFETY_FILE = ROOT / "config" / "buddy_laptop_safety.json"
JSON_FILE = ROOT / "reports" / "buddy_free_local_test_kit.json"
MD_FILE = ROOT / "reports" / "BUDDY_FREE_LOCAL_TEST_KIT.md"
HTML_FILE = ROOT / "reports" / "buddy-free-local-test-kit.html"


FREE_TESTS = [
    {
        "id": "setup",
        "name": "Laptop setup verification",
        "command": "python3 tools/setup_buddy_laptop.py",
        "cost": "free_local",
        "proves": "Buddy can validate local setup, safety policy, autonomy config, bot readiness, and smoke tests.",
    },
    {
        "id": "quick_sweep",
        "name": "Quick free sweep",
        "command": "python3 tools/local_buddy_runner.py --profile cheap",
        "cost": "free_local",
        "proves": "Buddy can run low-cost reports and checks without cloud minutes.",
    },
    {
        "id": "autonomy_catalog",
        "name": "Autonomous everything catalog",
        "command": "python3 tools/generate_buddy_autonomous_everything.py --check",
        "cost": "free_local",
        "proves": "Every connected bot/division is represented in the governed autonomy queue.",
    },
    {
        "id": "generated_bot_smoke",
        "name": "Generated bot smoke tests",
        "command": "python3 tools/run_generated_bot_smoke.py",
        "cost": "free_local",
        "proves": "Generated bot contracts can be discovered and smoke-tested locally.",
    },
    {
        "id": "typecheck",
        "name": "Dashboard TypeScript check",
        "command": "PATH=/Users/mamas/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH /Users/mamas/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm run check",
        "cost": "free_local",
        "proves": "The dashboard code compiles with the bundled local runtime.",
    },
    {
        "id": "dashboard",
        "name": "Open local dashboard",
        "command": "PATH=/Users/mamas/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH /Users/mamas/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm run dev",
        "cost": "free_local",
        "proves": "Buddy can be tested through the local app without deploying.",
    },
]

PAID_OR_LIVE_BLOCKS = [
    "paid model calls",
    "production deploys",
    "domain purchases",
    "app-store submissions",
    "payment account changes",
    "customer charges, refunds, payouts, or transfers",
    "secret creation or rotation",
    "external account signups",
    "granting repository, cloud, payment, email, or social access",
    "sending outreach, calls, messages, proposals, bids, or social posts",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> dict[str, Any]:
    autonomy = read_json(AUTONOMY_FILE, {})
    laptop = read_json(LAPTOP_FILE, {})
    safety = read_json(SAFETY_FILE, {})
    return {
        "schema": "dreamco.buddy_free_local_test_kit.v1",
        "generated_at": utc_now(),
        "mission": "Make Buddy testable in free/local-first mode before using paid services or live account actions.",
        "free_first_policy": {
            "default_mode": "free_local_first",
            "use_cloud_by_default": False,
            "use_paid_model_calls_by_default": False,
            "use_github_actions_by_default": False,
            "store_secret_values_in_repo": False,
            "live_actions_require_approval": True,
        },
        "free_tests": FREE_TESTS,
        "paid_or_live_blocks": PAID_OR_LIVE_BLOCKS,
        "current_inventory": {
            "bots_connected_to_queue": autonomy.get("totals", {}).get("bots_connected_to_queue", 0),
            "divisions_connected_to_queue": autonomy.get("totals", {}).get("divisions_connected_to_queue", 0),
            "safe_local_capabilities": laptop.get("safe_local_capabilities", []),
            "resource_limits": safety.get("resource_limits", {}),
        },
        "files_to_open": {
            "html": str(HTML_FILE.relative_to(ROOT)),
            "markdown": str(MD_FILE.relative_to(ROOT)),
            "json": str(JSON_FILE.relative_to(ROOT)),
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = ["# Buddy Free Local Test Kit", "", report["mission"], "", "## Free-First Policy", ""]
    for key, value in report["free_first_policy"].items():
        lines.append(f"- {key}: `{str(value).lower()}`")
    lines.extend(["", "## Test Commands", ""])
    for test in report["free_tests"]:
        lines.append(f"### {test['name']}")
        lines.append("")
        lines.append(f"- Cost: `{test['cost']}`")
        lines.append(f"- Proves: {test['proves']}")
        lines.append("")
        lines.append("```bash")
        lines.append(test["command"])
        lines.append("```")
        lines.append("")
    lines.extend(["## Approval Required Before Anything Paid Or Live", ""])
    for item in report["paid_or_live_blocks"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Current Inventory", ""])
    inv = report["current_inventory"]
    lines.append(f"- Bots connected to queue: {inv['bots_connected_to_queue']}")
    lines.append(f"- Divisions connected to queue: {inv['divisions_connected_to_queue']}")
    lines.append("")
    MD_FILE.write_text("\n".join(lines), encoding="utf-8")


def write_html(report: dict[str, Any]) -> None:
    tests = "\n".join(
        "<section><h2>{name}</h2><p><strong>Cost:</strong> {cost}</p><p>{proves}</p><pre>{command}</pre></section>".format(
            name=html.escape(test["name"]),
            cost=html.escape(test["cost"]),
            proves=html.escape(test["proves"]),
            command=html.escape(test["command"]),
        )
        for test in report["free_tests"]
    )
    blocks = "\n".join(f"<li>{html.escape(item)}</li>" for item in report["paid_or_live_blocks"])
    inv = report["current_inventory"]
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Buddy Free Local Test Kit</title>
  <style>
    body {{ font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; background: #f7f7f4; color: #171717; }}
    main {{ max-width: 1040px; margin: 0 auto; padding: 32px 18px 56px; }}
    header {{ border-bottom: 2px solid #1f6f5b; padding-bottom: 20px; margin-bottom: 24px; }}
    h1 {{ font-size: 34px; margin: 0 0 10px; }}
    h2 {{ font-size: 20px; margin: 0 0 8px; }}
    section {{ background: #fff; border: 1px solid #d9d7ce; border-radius: 8px; padding: 18px; margin: 14px 0; }}
    pre {{ white-space: pre-wrap; background: #111; color: #f4f4f4; padding: 12px; border-radius: 6px; overflow-x: auto; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; }}
    .metric {{ background: #e8f3ef; border: 1px solid #9cc8bb; border-radius: 8px; padding: 14px; }}
    .metric b {{ display: block; font-size: 28px; }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Buddy Free Local Test Kit</h1>
      <p>{html.escape(report["mission"])}</p>
    </header>
    <div class="grid">
      <div class="metric"><span>Bots Queued</span><b>{inv['bots_connected_to_queue']}</b></div>
      <div class="metric"><span>Divisions Queued</span><b>{inv['divisions_connected_to_queue']}</b></div>
      <div class="metric"><span>Default Cost Mode</span><b>Free</b></div>
    </div>
    {tests}
    <section>
      <h2>Approval Required Before Paid Or Live Actions</h2>
      <ul>{blocks}</ul>
    </section>
  </main>
</body>
</html>
"""
    HTML_FILE.write_text(page, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Buddy free local test kit.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.check:
        existing = read_json(JSON_FILE, {})
        ok = JSON_FILE.exists() and MD_FILE.exists() and HTML_FILE.exists()
        ok = ok and existing.get("schema") == report["schema"]
        ok = ok and existing.get("current_inventory", {}).get("bots_connected_to_queue") == report["current_inventory"]["bots_connected_to_queue"]
        print(json.dumps({"ok": ok, **report["current_inventory"]}, indent=2))
        return 0 if ok else 1
    JSON_FILE.parent.mkdir(parents=True, exist_ok=True)
    JSON_FILE.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    write_html(report)
    print(json.dumps({"ok": True, "html": str(HTML_FILE.relative_to(ROOT)), "markdown": str(MD_FILE.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
