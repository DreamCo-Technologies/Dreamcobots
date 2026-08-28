"""DreamCo server-side OpenRouter gateway.

Clients should call this layer instead of receiving a shared provider key.
The gateway is deliberately small and can be mounted behind the existing
DreamCo API/auth stack.
"""
from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class ClientPolicy:
    client_id: str
    allowed_models: frozenset[str]
    monthly_token_limit: int = 1_000_000
    allow_custom_model: bool = False
    data_collection: str = "deny"


class BuddyGateway:
    def __init__(self, policy: ClientPolicy):
        self.policy = policy
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY must remain server-side")

    def resolve_model(self, requested: str | None) -> str:
        if not requested or requested == "dreamco/auto":
            return "openrouter/auto"
        if requested.startswith("dreamco/"):
            aliases = {
                "dreamco/coding": "openrouter/auto",
                "dreamco/reasoning": "openrouter/auto",
                "dreamco/fast": "openrouter/auto",
                "dreamco/vision": "openrouter/auto",
                "dreamco/budget": "openrouter/auto",
            }
            return aliases.get(requested, "openrouter/auto")
        if not self.policy.allow_custom_model and requested not in self.policy.allowed_models:
            raise PermissionError("Requested model is not enabled for this client")
        return requested

    def build_payload(
        self,
        prompt: str,
        requested_model: str | None = None,
        fallbacks: list[str] | None = None,
    ) -> dict:
        model = self.resolve_model(requested_model)
        return {
            "model": model,
            "models": [model, *(fallbacks or [])],
            "messages": [{"role": "user", "content": prompt}],
            "provider": {
                "allow_fallbacks": True,
                "data_collection": self.policy.data_collection,
            },
        }

    def chat(self, prompt: str, requested_model: str | None = None, fallbacks: list[str] | None = None) -> dict:
        payload = self.build_payload(prompt, requested_model, fallbacks)
        request = urllib.request.Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode(),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Title": "DreamCo Buddy",
            },
        )
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.loads(response.read().decode())
