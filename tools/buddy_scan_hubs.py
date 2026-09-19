#!/usr/bin/env python3
"""Buddy scans known model hubs and writes learning-package manifests per capability.

Metadata only. No bulk download of weights.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "config" / "model-hub-scan-targets.json"
APP = ROOT / "App_bots"
OUT = ROOT / "study_packs" / "bot_learning_packages"
REPORT = ROOT / "reports" / "BUDDY_HUB_LEARNING_PACKAGES.md"

CAP_HINTS = {
    "code": "coding",
    "debug": "coding",
    "research": "reasoning",
    "reason": "reasoning",
    "sales": "instruction",
    "embed": "embeddings",
    "rag": "rag",
    "vector": "rag",
    "vision": "vision",
    "image": "vision",
    "speech": "speech",
    "audio": "speech",
    "translat": "translation",
    "summar": "summarization",
    "safe": "safety",
    "secur": "safety",
    "agent": "agents",
    "tool": "tools",
}


def infer_topic(text: str) -> str:
    blob = text.lower()
    for hint, topic in CAP_HINTS.items():
        if hint in blob:
            return topic
    return "instruction"


def bot_rows() -> list[dict]:
    rows = []
    if not APP.exists():
        return rows
    for path in sorted(APP.glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        division = doc.get("division") or path.stem
        for bot in doc.get("bots", []) if isinstance(doc, dict) else []:
            if not isinstance(bot, dict) or not bot.get("slug"):
                continue
            text = " ".join([
                str(bot.get("slug")),
                str(bot.get("displayName", "")),
                str(bot.get("description", "")),
                " ".join(bot.get("capabilities") or []),
            ])
            rows.append({
                "slug": bot["slug"],
                "division": division,
                "topic": infer_topic(text),
                "capabilities": list(bot.get("capabilities") or [])[:12],
            })
    return rows


def main() -> int:
    targets = json.loads(TARGETS.read_text(encoding="utf-8"))
    bots = bot_rows()
    OUT.mkdir(parents=True, exist_ok=True)
    by_topic: dict[str, list[dict]] = {}
    for bot in bots:
        by_topic.setdefault(bot["topic"], []).append(bot)
    packages = []
    for topic in targets["capability_topics"]:
        dest = OUT / f"pack.{topic}"
        dest.mkdir(parents=True, exist_ok=True)
        members = by_topic.get(topic, [])
        manifest = {
            "schema": "dreamco.bot_learning_package.v1",
            "pack_id": f"pack.{topic}",
            "topic": topic,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "hubs_scanned": [hub["id"] for hub in targets["hubs"]],
            "bot_count": len(members),
            "bots": [{"slug": row["slug"], "division": row["division"]} for row in members[:200]],
            "sources": [
                {
                    "hub": hub["id"],
                    "url": hub["url"],
                    "scan": "metadata",
                    "download": False,
                }
                for hub in targets["hubs"]
            ],
            "automatic_download": False,
            "learning_use": "Study + optional LoRA/RAG pack for these bots. Teacher route remains xai/grok-best-available.",
        }
        (dest / "package.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        packages.append(manifest)
    index = {
        "schema": "dreamco.bot_learning_package_index.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hub_count": len(targets["hubs"]),
        "bot_count": len(bots),
        "package_count": len(packages),
        "covers_entire_internet": False,
        "automatic_download": False,
        "packages": [row["pack_id"] for row in packages],
    }
    (OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Buddy Hub Learning Packages",
        "",
        f"- Hubs scanned (metadata): **{len(targets['hubs'])}**",
        f"- Bots assigned: **{len(bots)}**",
        f"- Packages: **{len(packages)}**",
        "- Bulk download: **off**",
        "",
        "| Pack | Bots |",
        "| --- | --- |",
    ]
    for row in packages:
        lines.append(f"| `{row['pack_id']}` | {row['bot_count']} |")
    lines += ["", "Hubs"] + [f"- {hub['name']}: {hub['url']}" for hub in targets["hubs"]]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "hubs": len(targets["hubs"]), "bots": len(bots), "packages": len(packages)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
