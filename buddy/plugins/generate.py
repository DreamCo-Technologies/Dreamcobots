#!/usr/bin/env python3
"""Make one Buddy plugin record for every industry and app task in the benchmark file."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "config/universal-human-computer-ai-benchmark.json"
INDUSTRY = {"industry_operations", "government_and_civic", "nonprofit", "business_lifecycle", "commerce_and_money"}


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def generate() -> dict:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    plugins = []
    for domain, names in data["domains"].items():
        kind = "industry" if domain in INDUSTRY else "app"
        for name in names:
            plugins.append({
                "id": slug(domain) + "-" + slug(name),
                "kind": kind,
                "domain": domain,
                "name": name,
                "installed": False,
                "called": False,
                "weights_trained": False,
                "use": "Study this " + kind + " from the files already here. Do not send, charge, diagnose, or file.",
            })
    ids = [row["id"] for row in plugins]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Two plugins got the same id.")
    if len(plugins) != sum(len(names) for names in data["domains"].values()):
        raise RuntimeError("A source task was skipped.")
    return {
        "source": "config/universal-human-computer-ai-benchmark.json",
        "plugins": len(plugins),
        "industries": sum(1 for row in plugins if row["kind"] == "industry"),
        "apps": sum(1 for row in plugins if row["kind"] == "app"),
        "installed": False,
        "called": False,
        "weights_trained": False,
        "items": plugins,
    }


if __name__ == "__main__":
    made = generate()
    assert made["plugins"] == made["industries"] + made["apps"]
    assert made["plugins"] > 100 and made["installed"] is False and made["called"] is False
    out = ROOT / "website/data/plugins.json"
    out.write_text(json.dumps(made, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"plugins": made["plugins"], "industries": made["industries"], "apps": made["apps"], "installed": False}))
