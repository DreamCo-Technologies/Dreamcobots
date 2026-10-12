"""Model routing for fleet runs.

Live calls reuse ``buddy.openrouter.gateway.BuddyGateway`` and happen only when
BOTH ``DREAMCO_FLEET_LIVE_MODEL=1`` and ``OPENROUTER_API_KEY`` are set in the
server-side environment. Otherwise the deterministic offline path is used and
the result says so. CI never sets these variables.
"""
from __future__ import annotations

import os
from typing import Any, Callable

LIVE_FLAG = "DREAMCO_FLEET_LIVE_MODEL"


def live_enabled(env: dict[str, str] | None = None) -> bool:
    env = env if env is not None else dict(os.environ)
    return env.get(LIVE_FLAG) == "1" and bool(env.get("OPENROUTER_API_KEY"))


def complete(prompt: str, profile: dict[str, Any], offline: Callable[[], str],
             env: dict[str, str] | None = None) -> dict[str, Any]:
    """Route a prompt. Returns {"text", "mode", "model"}.

    ``offline`` builds the deterministic fallback text. Live failures fall
    back to offline and record the error class (never the message body, which
    could echo request content).
    """
    if profile.get("mode") != "offline_only" and live_enabled(env):
        try:
            from buddy.openrouter.gateway import BuddyGateway, ClientPolicy

            gateway = BuddyGateway(ClientPolicy(client_id="dreamco-fleet-runtime", allowed_models=frozenset()))
            response = gateway.chat(prompt, requested_model=profile.get("live_alias", "dreamco/auto"))
            choice = (response.get("choices") or [{}])[0]
            text = ((choice.get("message") or {}).get("content") or "").strip()
            if text:
                return {"text": text, "mode": "live_model", "model": response.get("model", "unknown")}
            fallback_reason = "empty_live_response"
        except Exception as exc:  # pragma: no cover - requires network + key
            fallback_reason = f"live_error:{type(exc).__name__}"
    else:
        fallback_reason = "live_model_not_enabled"
    return {"text": offline(), "mode": "offline_deterministic", "model": None, "fallback_reason": fallback_reason}
