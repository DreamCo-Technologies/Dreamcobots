"""Model routing for fleet runs.

Live calls reuse ``buddy.openrouter.gateway.BuddyGateway`` and happen only when
BOTH ``DREAMCO_FLEET_LIVE_MODEL=1`` and ``OPENROUTER_API_KEY`` are set in the
server-side environment. Otherwise the deterministic offline path is used and
the result says so. CI never sets these variables.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable

LIVE_FLAG = "DREAMCO_FLEET_LIVE_MODEL"


def live_enabled(env: dict[str, str] | None = None) -> bool:
    env = env if env is not None else dict(os.environ)
    return env.get(LIVE_FLAG) == "1" and bool(env.get("OPENROUTER_API_KEY"))


def complete(prompt: str, profile: dict[str, Any], offline: Callable[[], str],
             env: dict[str, str] | None = None) -> dict[str, Any]:
    """Route a prompt, optionally checking internal Bootcamp knowledge first."""
    learning_route = None
    if profile.get("internal_bootcamp_first") is True:
        from buddy.learning.buddy_knowledge_router import route_buddy_learning_query

        learning_route = route_buddy_learning_query(
            str(profile.get("internal_learning_query") or prompt),
            root=Path(profile.get("bootcamp_root") or Path(__file__).resolve().parents[2]),
            limit=int(profile.get("internal_learning_limit", 5)),
            record_gap=False,
        )
        if learning_route["route"] == "internal_approved_guide":
            return {
                "text": json.dumps(learning_route["guide_documents"], ensure_ascii=False),
                "mode": "internal_knowledge",
                "model": None,
                "learning_route": learning_route,
            }
        if learning_route["route"] == "internal_bootcamp_lesson":
            return {
                "text": json.dumps(learning_route["course_lessons"], ensure_ascii=False),
                "mode": "internal_bootcamp_study",
                "model": None,
                "learning_route": learning_route,
            }
        if profile.get("allow_external_learning_fallback") is not True:
            return {
                "text": offline(),
                "mode": "offline_deterministic",
                "model": None,
                "fallback_reason": "internal_knowledge_gap_external_fallback_disabled",
                "learning_route": learning_route,
            }
    if profile.get("mode") != "offline_only" and live_enabled(env):
        try:
            from buddy.openrouter.gateway import BuddyGateway, ClientPolicy

            gateway = BuddyGateway(ClientPolicy(client_id="dreamco-fleet-runtime", allowed_models=frozenset()))
            response = gateway.chat(prompt, requested_model=profile.get("live_alias", "dreamco/auto"))
            choice = (response.get("choices") or [{}])[0]
            text = ((choice.get("message") or {}).get("content") or "").strip()
            if text:
                result = {"text": text, "mode": "live_model", "model": response.get("model", "unknown")}
                if learning_route is not None:
                    result["learning_route"] = learning_route
                return result
            fallback_reason = "empty_live_response"
        except Exception as exc:  # pragma: no cover - requires network + key
            fallback_reason = f"live_error:{type(exc).__name__}"
    else:
        fallback_reason = "live_model_not_enabled"
    result = {"text": offline(), "mode": "offline_deterministic", "model": None, "fallback_reason": fallback_reason}
    if learning_route is not None:
        result["learning_route"] = learning_route
    return result


def complete_learning(prompt: str, profile: dict[str, Any], offline: Callable[[], str],
                      env: dict[str, str] | None = None) -> dict[str, Any]:
    """Run a learning/technical prompt through Bootcamp before any model fallback."""
    learning_profile = {**profile, "internal_bootcamp_first": True}
    return complete(prompt, learning_profile, offline, env)
