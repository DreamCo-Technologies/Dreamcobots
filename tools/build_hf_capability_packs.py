#!/usr/bin/env python3
"""Materialize Hugging Face capability study-pack folders (metadata only)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "config" / "huggingface-capability-packs.json"
OUT_ROOT = ROOT / "study_packs"
REPORT = ROOT / "reports" / "HUGGINGFACE_CAPABILITY_PACKS.md"

CARD = """# {pack_id}

Capability pack for Buddy study / future student training.

- train_allowed: {train_allowed}
- min_native_pass_rate: {floor}
- teacher: xai/grok-best-available
- automatic weight download: no

Pin exact Hugging Face `repo_id` + `revision` in sources.json before any train job.
"""


def main() -> int:
    doc = json.loads(SRC.read_text(encoding="utf-8"))
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    written = []
    for pack in doc["packs"]:
        dest = OUT_ROOT / pack["id"]
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "CARD.md").write_text(
            CARD.format(pack_id=pack["id"], train_allowed=pack["train_allowed"], floor=pack["min_native_pass_rate"]),
            encoding="utf-8",
        )
        sources = {
            "pack_id": pack["id"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "hf_datasets": [],
            "hf_models": [],
            "search_hints": pack.get("search_hints", []),
            "note": "Fill with pinned repo_id + revision + license after Phase 1 review.",
        }
        evals = {
            "capability_ids": pack["capability_ids"],
            "min_native_pass_rate": pack["min_native_pass_rate"],
            "tasks": [],
            "train_allowed": pack["train_allowed"],
        }
        (dest / "sources.json").write_text(json.dumps(sources, indent=2) + "\n", encoding="utf-8")
        (dest / "evals.json").write_text(json.dumps(evals, indent=2) + "\n", encoding="utf-8")
        (dest / "evidence").mkdir(exist_ok=True)
        written.append(pack["id"])
    index = {
        "schema": "dreamco.study_packs_index.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "packs": written,
        "count": len(written),
        "train_in_default_ci": False,
    }
    (OUT_ROOT / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    lines = ["# Hugging Face Capability Packs", "", f"- Packs: **{len(written)}**", "", "| Pack | Capabilities | Train allowed |", "| --- | --- | --- |"]
    for pack in doc["packs"]:
        lines.append(f"| `{pack['id']}` | {', '.join(pack['capability_ids'])} | {pack['train_allowed']} |")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "packs": written}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
