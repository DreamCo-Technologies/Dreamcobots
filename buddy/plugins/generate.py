#!/usr/bin/env python3
"""Build the plugin catalog from the task, domain, and industry files. Nothing is installed."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SANDBOX = ROOT / "config/universal-human-ai-software-task-sandbox.json"
BENCH = ROOT / "config/universal-human-computer-ai-benchmark.json"
CAPABILITIES = ROOT / "config/universal-capability-domains.json"


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def generate() -> dict:
    sandbox = json.loads(SANDBOX.read_text(encoding="utf-8"))
    bench = json.loads(BENCH.read_text(encoding="utf-8"))
    capabilities = json.loads(CAPABILITIES.read_text(encoding="utf-8"))
    items = []
    seen = set()

    def add(kind: str, name: str, domain: str, action: str = "") -> None:
        row_id = slug("-".join(part for part in (kind, domain, action, name) if part))
        if row_id in seen:
            return
        seen.add(row_id)
        items.append({"id": row_id, "kind": kind, "domain": domain, "name": name, "action": action})

    for action in sandbox["task_actions"]:
        for domain in sandbox["domains"]:
            for level in sandbox["complexity"]:
                add("task", level, domain, action)
    for name in sandbox["special_business_client_scenarios"]:
        add("app", name, "business")
    for name in sandbox["special_personal_scenarios"]:
        add("app", name, "personal")
    for domain, names in bench["domains"].items():
        kind = "industry" if domain in {"industry_operations", "government_and_civic", "nonprofit", "business_lifecycle", "commerce_and_money"} else "app"
        for name in names:
            add(kind, name, domain)
    for name in capabilities["domains"]:
        add("capability", name, "capability")

    if len(items) < 50000:
        raise RuntimeError("The catalog is smaller than the sandbox file requires.")
    return {
        "sources": [SANDBOX.name, BENCH.name, CAPABILITIES.name],
        "plugins": len(items),
        "installed": False,
        "called": False,
        "weights_trained": False,
        "note": "A row is a study route. It is not proof Buddy can do the task.",
        "items": items,
    }


if __name__ == "__main__":
    made = generate()
    assert made["plugins"] >= 50000 and made["installed"] is False and made["called"] is False
    out = ROOT / "study_packs/hub/plugin-catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(made, separators=(",", ":")) + "\n", encoding="utf-8")
    summary = {key: made[key] for key in ("sources", "plugins", "installed", "called", "weights_trained", "note")}
    summary["full_catalog"] = "study_packs/hub/plugin-catalog.json"
    (ROOT / "website/data/plugins-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"plugins": made["plugins"], "installed": False, "bytes": out.stat().st_size, "served": False}))
