"""Task router. A model is eligible only with a measured score.

Sources can be open source, GitHub, frontier, or open weight. No weights are
downloaded here, and a missing score does not get a guess.
"""

from __future__ import annotations

import json
import math
from numbers import Real
from pathlib import Path

SOURCES = ["open-source", "github", "frontier", "open-weight", "hugging-face"]
ROOT = Path(__file__).resolve().parents[2]


def _valid_score(value: object) -> bool:
    """Reject booleans, non-numbers, NaN, infinity and out-of-range scores."""
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value) and 0 <= value <= 1


def register(name: str, source: str, task: str, quality: float, efficiency: float, approved_by: str, free: bool = False) -> dict:
    if source not in SOURCES:
        raise ValueError(f"unknown source: {source}")
    if approved_by not in {"owner", "user"}:
        raise ValueError("approval must come from the owner or the user")
    if not _valid_score(quality) or not _valid_score(efficiency):
        raise ValueError("scores must be finite numbers between 0 and 1")
    if not isinstance(name, str) or not name.strip() or not isinstance(task, str) or not task.strip():
        raise ValueError("model name and task must be nonempty strings")
    if type(free) is not bool:
        raise ValueError("free must be a boolean")
    return {"name": name, "source": source, "task": task, "quality": quality, "efficiency": efficiency, "approved_by": approved_by, "free": free, "provider": source, "weights_downloaded": False}


def connect_account(provider: str, paid: bool) -> dict:
    if not isinstance(provider, str) or not provider.strip():
        raise ValueError("a provider name is required")
    if type(paid) is not bool:
        raise ValueError("paid must be a boolean")
    return {"provider": provider, "paid": paid, "connected": True, "secret_stored": False}


def route(task: str, models: list[dict], free_only: bool = False, accounts: list[dict] | None = None) -> dict:
    connected = {
        row["provider"]
        for row in (accounts if isinstance(accounts, list) else [])
        if isinstance(row, dict)
        and isinstance(row.get("provider"), str)
        and bool(row["provider"].strip())
        and row.get("connected") is True
        and row.get("paid") is True
    }
    eligible = []
    for row in (models if isinstance(models, list) else []):
        if not isinstance(row, dict) or row.get("task") != task:
            continue
        if row.get("approved_by") not in {"owner", "user"}:
            continue
        if row.get("source") not in SOURCES or not isinstance(row.get("name"), str) or not row["name"].strip():
            continue
        if not _valid_score(row.get("quality")) or not _valid_score(row.get("efficiency")):
            continue
        if type(row.get("free")) is not bool:
            continue
        if free_only and not row["free"]:
            continue
        if not row["free"] and row.get("provider") not in connected:
            continue
        eligible.append(row)
    if not eligible:
        return {"task": task, "model": None, "free_only": free_only, "reason": "no approved measured score for a connected account"}
    winner = max(eligible, key=lambda row: (row["quality"], row["efficiency"], row["name"]))
    return {"task": task, "model": winner["name"], "source": winner["source"], "provider": winner.get("provider"), "quality": winner["quality"], "efficiency": winner["efficiency"], "free_only": free_only, "guessed": False}


def main() -> int:
    models = [register("paid", "frontier", "summarize", 0.95, 0.4, "owner", False), register("free", "open-weight", "summarize", 0.8, 0.7, "user", True)]
    report = {"route": route("summarize", models), "free_route": route("summarize", models, free_only=True), "accounts": ["owner", "user"], "frontier_models_use_us": False, "weights_downloaded": False}
    path = ROOT / "reports" / "MODEL_TASK_ROUTE.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["route"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
