#!/usr/bin/env python3
"""One approved model per step. A choice is not a measured winner."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def board() -> dict:
    policy = json.loads((ROOT / "config/buddy-capability-evolution-policy.json").read_text(encoding="utf-8"))
    connections = json.loads((ROOT / "config/buddy-universal-connection-catalog.json").read_text(encoding="utf-8"))
    study = json.loads((ROOT / "website/data/weight-study.json").read_text(encoding="utf-8"))
    steps = list(policy["evolution_loop"])
    approved = [{"id": row["repo"], "license": row["license"], "approved": True, "called": False} for row in study["models"] if row.get("gated") is False]
    links = []
    for row in connections["connections"]:
        links.append({"id": row["id"], "name": row["name"], "status": row["status"], "setup_url": row["setup_url"], "page": row["buddy_surface"], "api": "api" in row.get("auth", "") or "api" in row["name"].lower()})
    workflows = sorted(path.name for path in (ROOT / ".github/workflows").glob("*.yml"))
    return {
        "steps": steps,
        "approved_models": approved,
        "connections": links,
        "apis": [row for row in links if row["api"]],
        "workflows": workflows,
        "plugins": json.loads((ROOT / "study_packs/hub/plugin-catalog.json").read_text(encoding="utf-8"))["plugins"],
        "measured_best": None,
        "called": False,
    }


def plan(task: str, choices: dict | None = None) -> dict:
    made = board()
    allowed = {row["id"] for row in made["approved_models"]}
    text = " ".join((task or "").split())
    if len(text) < 2:
        raise ValueError("Name the task.")
    rows = []
    for step in made["steps"]:
        picked = (choices or {}).get(step) or "Buddy's own code"
        if picked != "Buddy's own code" and picked not in allowed:
            picked = "Buddy's own code"
        rows.append({"step": step, "model": picked, "called": False, "measured_best": None})
    return {"task": text, "steps": rows, "called": False, "measured_best": None}


if __name__ == "__main__":
    made = board()
    assert len(made["steps"]) >= 8 and len(made["approved_models"]) == 5
    assert made["plugins"] >= 50000 and made["called"] is False and made["measured_best"] is None
    assert made["apis"] and made["workflows"] and made["connections"]
    chosen = {step: made["approved_models"][index % 5]["id"] for index, step in enumerate(made["steps"])}
    routed = plan("write a lesson", chosen)
    assert routed["steps"][0]["model"] == made["approved_models"][0]["id"]
    assert routed["steps"][1]["model"] != routed["steps"][0]["model"]
    assert routed["measured_best"] is None
    out = ROOT / "website/data/step-board.json"
    public = {key: made[key] for key in ("steps", "approved_models", "connections", "apis", "workflows", "plugins", "measured_best", "called")}
    out.write_text(json.dumps(public, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"steps": len(made["steps"]), "models": len(made["approved_models"]), "connections": len(made["connections"]), "apis": len(made["apis"]), "workflows": len(made["workflows"]), "measured_best": None}))
