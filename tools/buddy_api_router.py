#!/usr/bin/env python3
"""Route a Buddy task through the generated free-first model router."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ROUTER_JSON = ROOT / "config" / "generated" / "buddy_professional_api_router.json"
FREE_JSON = ROOT / "config" / "generated" / "buddy_free_model_task_library.json"
NATIVE_JSON = ROOT / "config" / "generated" / "buddy_native_bot_coverage.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in value).strip("_")


def route_models_for_mode(task: str, mode: str) -> tuple[str, list[str]] | None:
    if not FREE_JSON.exists():
        return None
    library = read_json(FREE_JSON)
    routes = {item["task_type"]: item for item in library.get("task_routes", [])}
    route = routes.get(task)
    if not route:
        return None
    candidates = [route["primary_free_model"], *route["fallback_free_models"]]
    models = {item["id"]: item for item in library.get("models", [])}
    if mode == "local_only":
        candidates = [
            model_id
            for model_id in candidates
            if any(term in models.get(model_id, {}).get("access", "") for term in ["local", "open_source", "open_weight", "research_weight"])
        ]
    if not candidates:
        return None
    return candidates[0], candidates[1:5]


def route_native_bot(task: str) -> dict[str, Any] | None:
    if not NATIVE_JSON.exists():
        return None
    coverage = read_json(NATIVE_JSON)
    routes = coverage.get("task_routes", [])
    route = next((item for item in routes if item.get("task_type") == task), None)
    if route is None:
        route = max(
            routes,
            key=lambda item: sum(1 for word in task.split("_") if word and word in item.get("task_type", "")),
            default=None,
        )
    if route is None:
        return None
    return {
        "native_first": True,
        "primary_native_bot": route["primary_native_bot"],
        "primary_native_path": route["primary_native_path"],
        "fallback_native_paths": route["fallback_native_paths"],
        "native_coverage": route["native_coverage"],
        "approval_required_for_live_use": route["approval_required_for_live_use"],
        "coverage_source": str(NATIVE_JSON.relative_to(ROOT)),
    }


def route_task(task: str, mode: str) -> dict[str, Any]:
    router = read_json(ROUTER_JSON)
    normalized = normalize(task)
    routes = router.get("routes", [])
    route = next((item for item in routes if item.get("task_type") == normalized), None)
    if route is None:
        route = max(
            routes,
            key=lambda item: sum(1 for word in normalized.split("_") if word and word in item.get("task_type", "")),
        )
    native_route = route_native_bot(normalized) or route_native_bot(route["task_type"])
    mode_route = route_models_for_mode(route["task_type"], mode)
    primary = mode_route[0] if mode_route else route["primary_free_model"]
    fallbacks = mode_route[1] if mode_route else route["fallback_free_models"]
    paid_allowed = mode in {"premium_optional", "quality_first"}
    return {
        "schema": "dreamco.buddy_api_route_decision.v1",
        "task": task,
        "normalized_task": normalized,
        "mode": mode,
        "primary_model": primary,
        "fallback_models": fallbacks,
        "paid_call_allowed": paid_allowed,
        "paid_call_blocked_until_approval": not paid_allowed,
        "native_route": native_route,
        "route_source": str(ROUTER_JSON.relative_to(ROOT)),
        "next_step": "Run DreamCo native bot code first, then local/free sandbox. Escalate only when the user chooses premium and approval/budget exists.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Route a Buddy task to a free-first model/resource.")
    parser.add_argument("task", nargs="?", default="general_chat")
    parser.add_argument("--mode", choices=["free_first", "local_only", "premium_optional", "quality_first"], default="free_first")
    args = parser.parse_args()
    print(json.dumps(route_task(args.task, args.mode), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
