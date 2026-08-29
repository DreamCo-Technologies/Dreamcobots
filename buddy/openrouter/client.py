"""Minimal server-side OpenRouter client for Buddy.

OpenRouter is supplemental to the protected DreamCo model fleet. No API key is
stored in source control; provide OPENROUTER_API_KEY at runtime.
"""
from __future__ import annotations

import os
from typing import Any
from urllib.request import Request, urlopen
import json


BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")


class OpenRouterError(RuntimeError):
    pass


def _request(path: str, payload: dict[str, Any] | None = None) -> Any:
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise OpenRouterError("OPENROUTER_API_KEY is not configured")
    data = None if payload is None else json.dumps(payload).encode()
    request = Request(
        f"{BASE_URL.rstrip('/')}/{path.lstrip('/')}",
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("DREAMCO_APP_URL", "https://dreamco.ai"),
            "X-Title": os.getenv("DREAMCO_APP_NAME", "DreamCo Buddy"),
        },
        method="POST" if payload is not None else "GET",
    )
    try:
        with urlopen(request, timeout=float(os.getenv("OPENROUTER_TIMEOUT", "60"))) as response:
            return json.loads(response.read().decode())
    except Exception as exc:
        raise OpenRouterError(str(exc)) from exc


def list_models() -> list[dict[str, Any]]:
    """Return the live OpenRouter catalog without mutating DreamCo's catalog."""
    result = _request("models")
    return result.get("data", [])


def chat(model: str, messages: list[dict[str, Any]], *, fallback_models: list[str] | None = None,
         provider: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"model": model, "messages": messages, **kwargs}
    if fallback_models:
        payload["models"] = fallback_models
    if provider:
        payload["provider"] = provider
    return _request("chat/completions", payload)
