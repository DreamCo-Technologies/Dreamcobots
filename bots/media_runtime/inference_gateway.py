from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Callable


class ProviderFailure(Exception):
    """Raised when all providers in a chain fail."""


@dataclass
class ProviderResult:
    provider: str
    payload_bytes: bytes
    content_type: str
    metadata: dict[str, Any]


ProviderCallable = Callable[[dict[str, Any]], ProviderResult]


class InferenceGateway:
    """Provider abstraction with health-scored failover and telemetry."""

    def __init__(self) -> None:
        self._providers: dict[str, ProviderCallable] = {
            "openai": self._deterministic_provider,
            "elevenlabs": self._deterministic_provider,
            "ffmpeg-local": self._deterministic_provider,
        }
        self.provider_health: dict[str, float] = {name: 1.0 for name in self._providers}
        self.telemetry: dict[str, int] = {
            "requests": 0,
            "success": 0,
            "failures": 0,
            "fallbacks": 0,
        }

    def register_provider(self, name: str, handler: ProviderCallable, initial_health: float = 1.0) -> None:
        self._providers[name] = handler
        self.provider_health[name] = max(0.0, min(1.0, initial_health))

    def run(self, request: dict[str, Any], provider_chain: list[str]) -> ProviderResult:
        self.telemetry["requests"] += 1
        failures: list[str] = []

        chain = [p for p in provider_chain if p in self._providers]
        if not chain:
            chain = ["openai"]

        for idx, provider_name in enumerate(chain):
            handler = self._providers[provider_name]
            try:
                result = handler({**request, "provider": provider_name})
                self.provider_health[provider_name] = min(1.0, self.provider_health.get(provider_name, 1.0) + 0.03)
                if idx > 0:
                    self.telemetry["fallbacks"] += 1
                self.telemetry["success"] += 1
                return result
            except Exception as exc:  # pragma: no cover - error branch
                failures.append(f"{provider_name}: {exc}")
                self.provider_health[provider_name] = max(0.0, self.provider_health.get(provider_name, 1.0) - 0.25)

        self.telemetry["failures"] += 1
        raise ProviderFailure("; ".join(failures) or "No available providers")

    def _deterministic_provider(self, request: dict[str, Any]) -> ProviderResult:
        media_type = request.get("media_type", "media")
        operation = request.get("operation", "generate")
        prompt = str(request.get("prompt") or request.get("text") or request.get("script") or "")
        provider = request.get("provider", "openai")

        digest = hashlib.sha256(f"{media_type}|{operation}|{prompt}|{provider}".encode("utf-8")).hexdigest()
        body = (
            f"provider={provider}\n"
            f"media_type={media_type}\n"
            f"operation={operation}\n"
            f"prompt_sha256={digest}\n"
        ).encode("utf-8")
        return ProviderResult(
            provider=provider,
            payload_bytes=body,
            content_type="application/octet-stream",
            metadata={"prompt_sha256": digest, "provider": provider},
        )
