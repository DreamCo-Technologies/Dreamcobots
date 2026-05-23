from __future__ import annotations

from framework import GlobalAISourcesFlow  # noqa: F401

import hashlib
import time
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
        self._provider_limits: dict[str, int] = {name: 4 for name in self._providers}
        self._provider_active_requests: dict[str, int] = {name: 0 for name in self._providers}
        self._provider_cost_per_request: dict[str, float] = {name: 0.01 for name in self._providers}
        self._provider_quality_baseline: dict[str, float] = {name: 0.9 for name in self._providers}
        self.provider_health: dict[str, float] = {name: 1.0 for name in self._providers}
        self.provider_scorecards: dict[str, dict[str, float]] = {
            name: {
                "requests": 0.0,
                "success": 0.0,
                "failures": 0.0,
                "latency_ms_total": 0.0,
                "cost_total": 0.0,
                "quality_total": 0.0,
            }
            for name in self._providers
        }
        self.telemetry: dict[str, int] = {
            "requests": 0,
            "success": 0,
            "failures": 0,
            "fallbacks": 0,
            "degraded_executions": 0,
        }

    def register_provider(
        self,
        name: str,
        handler: ProviderCallable,
        initial_health: float = 1.0,
        *,
        max_concurrency: int = 4,
        cost_per_request: float = 0.01,
        quality_baseline: float = 0.9,
    ) -> None:
        self._providers[name] = handler
        self.provider_health[name] = max(0.0, min(1.0, initial_health))
        self._provider_limits[name] = max(1, max_concurrency)
        self._provider_active_requests[name] = 0
        self._provider_cost_per_request[name] = max(0.0, cost_per_request)
        self._provider_quality_baseline[name] = max(0.0, min(1.0, quality_baseline))
        self.provider_scorecards[name] = {
            "requests": 0.0,
            "success": 0.0,
            "failures": 0.0,
            "latency_ms_total": 0.0,
            "cost_total": 0.0,
            "quality_total": 0.0,
        }

    def run(
        self,
        request: dict[str, Any],
        provider_chain: list[str],
        *,
        policy_context: dict[str, Any] | None = None,
        allow_degraded: bool = False,
    ) -> ProviderResult:
        self.telemetry["requests"] += 1
        failures: list[str] = []

        chain = [p for p in provider_chain if p in self._providers]
        if not chain:
            chain = ["openai"]
        chain = self._apply_policy(chain, policy_context or {})

        for idx, provider_name in enumerate(chain):
            if self._provider_active_requests.get(provider_name, 0) >= self._provider_limits.get(provider_name, 1):
                failures.append(f"{provider_name}: saturated")
                continue
            handler = self._providers[provider_name]
            started = time.perf_counter()
            try:
                self._provider_active_requests[provider_name] += 1
                result = handler({**request, "provider": provider_name})
                latency_ms = (time.perf_counter() - started) * 1000.0
                self.provider_health[provider_name] = min(1.0, self.provider_health.get(provider_name, 1.0) + 0.03)
                self._record_provider_success(provider_name, latency_ms)
                if idx > 0:
                    self.telemetry["fallbacks"] += 1
                self.telemetry["success"] += 1
                result.metadata.setdefault("latency_ms", round(latency_ms, 3))
                result.metadata.setdefault("provider_health", self.provider_health.get(provider_name, 1.0))
                return result
            except Exception as exc:  # pragma: no cover - error branch
                latency_ms = (time.perf_counter() - started) * 1000.0
                failures.append(f"{provider_name}: {exc}")
                self.provider_health[provider_name] = max(0.0, self.provider_health.get(provider_name, 1.0) - 0.25)
                self._record_provider_failure(provider_name, latency_ms)
            finally:
                self._provider_active_requests[provider_name] = max(
                    0, self._provider_active_requests.get(provider_name, 0) - 1
                )

        self.telemetry["failures"] += 1
        if allow_degraded:
            self.telemetry["degraded_executions"] += 1
            return self._degraded_result(request=request, provider_chain=chain, failures=failures)
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

    def _record_provider_success(self, provider_name: str, latency_ms: float) -> None:
        scorecard = self.provider_scorecards.setdefault(
            provider_name,
            {"requests": 0.0, "success": 0.0, "failures": 0.0, "latency_ms_total": 0.0, "cost_total": 0.0, "quality_total": 0.0},
        )
        scorecard["requests"] += 1.0
        scorecard["success"] += 1.0
        scorecard["latency_ms_total"] += latency_ms
        scorecard["cost_total"] += self._provider_cost_per_request.get(provider_name, 0.0)
        scorecard["quality_total"] += self._provider_quality_baseline.get(provider_name, 0.9)

    def _record_provider_failure(self, provider_name: str, latency_ms: float) -> None:
        scorecard = self.provider_scorecards.setdefault(
            provider_name,
            {"requests": 0.0, "success": 0.0, "failures": 0.0, "latency_ms_total": 0.0, "cost_total": 0.0, "quality_total": 0.0},
        )
        scorecard["requests"] += 1.0
        scorecard["failures"] += 1.0
        scorecard["latency_ms_total"] += latency_ms
        scorecard["cost_total"] += self._provider_cost_per_request.get(provider_name, 0.0)

    def _apply_policy(self, chain: list[str], policy_context: dict[str, Any]) -> list[str]:
        media_type = str(policy_context.get("media_type", "media"))
        tier = str(policy_context.get("tier", "free"))
        latency_target_ms = float(policy_context.get("latency_target_ms", 1500))
        health_floor = float(policy_context.get("health_floor", 0.15))

        def _priority(provider_name: str) -> tuple[float, float, float, float]:
            score = self.provider_scorecards.get(provider_name, {})
            requests = max(1.0, score.get("requests", 0.0))
            avg_latency = score.get("latency_ms_total", 0.0) / requests
            avg_cost = score.get("cost_total", 0.0) / requests
            success_ratio = score.get("success", 0.0) / requests
            health = self.provider_health.get(provider_name, 1.0)
            saturation = self._provider_active_requests.get(provider_name, 0) / max(
                1, self._provider_limits.get(provider_name, 1)
            )
            media_boost = 0.0 if provider_name == "ffmpeg-local" and media_type in {"video", "audio"} else 0.1
            tier_boost = -0.05 if tier in {"pro", "enterprise"} and provider_name == "openai" else 0.0
            latency_penalty = max(0.0, (avg_latency - latency_target_ms) / max(latency_target_ms, 1.0))
            health_penalty = 1.0 if health < health_floor else 0.0
            return (
                health_penalty + saturation + latency_penalty + media_boost + tier_boost,
                -success_ratio,
                avg_cost,
                avg_latency,
            )

        return sorted(chain, key=_priority)

    def _degraded_result(self, *, request: dict[str, Any], provider_chain: list[str], failures: list[str]) -> ProviderResult:
        fallback_provider = "ffmpeg-local" if "ffmpeg-local" in self._providers else provider_chain[0]
        result = self._deterministic_provider({**request, "provider": fallback_provider})
        result.metadata.update(
            {
                "degraded_execution": True,
                "fallback_provider": fallback_provider,
                "failures": failures,
            }
        )
        return result

    def provider_governance_snapshot(self) -> dict[str, Any]:
        scorecards: dict[str, Any] = {}
        for provider_name, score in self.provider_scorecards.items():
            requests = max(1.0, score.get("requests", 0.0))
            scorecards[provider_name] = {
                "health": round(self.provider_health.get(provider_name, 1.0), 4),
                "avg_latency_ms": round(score.get("latency_ms_total", 0.0) / requests, 4),
                "avg_cost": round(score.get("cost_total", 0.0) / requests, 6),
                "reliability": round(score.get("success", 0.0) / requests, 4),
                "failure_rate": round(score.get("failures", 0.0) / requests, 4),
                "quality": round(score.get("quality_total", 0.0) / requests, 4),
                "saturation": round(
                    self._provider_active_requests.get(provider_name, 0) / max(1, self._provider_limits.get(provider_name, 1)),
                    4,
                ),
            }
        return {
            "telemetry": dict(self.telemetry),
            "scorecards": scorecards,
        }
