#!/usr/bin/env python3
"""Day-1 Hub drills. Ask the public Hub. Do not download weights."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "evidence"


def ids() -> list[str]:
    study = json.loads((ROOT / "config/huggingface-two-week-study.json").read_text(encoding="utf-8"))
    packs = json.loads((ROOT / "config/hf-capability-download-map.json").read_text(encoding="utf-8"))
    found = list(study["student_shortlist"])
    for names in packs["seed_models"].values():
        found.extend(names)
    for names in packs["seed_datasets"].values():
        found.extend("dataset:" + name for name in names)
    return list(dict.fromkeys(found))


def ask(kind: str, name: str) -> dict:
    if " " in name or "placeholder" in name or "study-only" in name:
        return {"id": name, "kind": kind, "state": "not_a_model_id", "code": None}
    url = "https://huggingface.co/api/" + ("datasets/" if kind == "dataset" else "models/") + name
    request = urllib.request.Request(url, headers={"User-Agent": "DreamCo-day1"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode())
            gated = bool(body.get("gated"))
            return {"id": name, "kind": kind, "state": "gated" if gated else "public", "code": response.status, "license": body.get("cardData", {}).get("license") if isinstance(body.get("cardData"), dict) else None}
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            return {"id": name, "kind": kind, "state": "gated", "code": exc.code}
        if exc.code == 404:
            return {"id": name, "kind": kind, "state": "missing", "code": 404}
        return {"id": name, "kind": kind, "state": "error", "code": exc.code}


def main() -> dict:
    rows = []
    for item in ids():
        if item.startswith("dataset:"):
            rows.append(ask("dataset", item.split(":", 1)[1]))
        else:
            rows.append(ask("model", item))
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "checked": len(rows),
        "public": sum(1 for row in rows if row["state"] == "public"),
        "gated": sum(1 for row in rows if row["state"] == "gated"),
        "missing": sum(1 for row in rows if row["state"] == "missing"),
        "not_a_model_id": sum(1 for row in rows if row["state"] == "not_a_model_id"),
        "downloaded": False,
        "token_used": False,
        "rows": rows,
    }
    (OUT / "day1-inventory.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("checked", "public", "gated", "missing", "not_a_model_id", "downloaded")}))
    return report


if __name__ == "__main__":
    main()
