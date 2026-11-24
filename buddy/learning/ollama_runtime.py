"""Read-only and inference-only client for a local Ollama runtime.

This adapter never pulls, deletes, creates, or pushes models. It is limited to
loopback addresses so it cannot silently send local prompts to remote hosts.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def validate_local_endpoint(endpoint: str) -> str:
    parsed = urlparse(endpoint)
    if parsed.scheme != "http" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Ollama endpoint must be an unauthenticated local HTTP URL")
    host = parsed.hostname.lower()
    if host != "localhost":
        try:
            if not ipaddress.ip_address(host).is_loopback:
                raise ValueError("Ollama endpoint must resolve to loopback only")
        except ValueError as exc:
            if "loopback only" in str(exc):
                raise
            raise ValueError("Ollama endpoint must use localhost or a loopback IP") from exc
    return endpoint.rstrip("/")


class OllamaLocalRuntime:
    def __init__(self, endpoint: str = "http://127.0.0.1:11434", timeout_seconds: int = 30):
        self.endpoint = validate_local_endpoint(endpoint)
        if timeout_seconds < 1 or timeout_seconds > 300:
            raise ValueError("timeout_seconds must be between 1 and 300")
        self.timeout_seconds = timeout_seconds

    def _post(self, path: str, payload: dict) -> dict:
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.endpoint}{path}",
            data=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:  # noqa: S310 - endpoint is loopback-validated
                raw = response.read(8 * 1024 * 1024 + 1)
            if len(raw) > 8 * 1024 * 1024:
                raise RuntimeError("Ollama response exceeded the 8 MiB safety limit")
            parsed = json.loads(raw.decode("utf-8"))
            if not isinstance(parsed, dict):
                raise RuntimeError("Ollama returned a non-object response")
            return parsed
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"local Ollama request failed: {type(exc).__name__}") from exc

    def list_models(self) -> dict:
        return self._post("/api/tags", {})

    def show_model(self, model: str) -> dict:
        if not model.strip():
            raise ValueError("model name is required")
        result = self._post("/api/show", {"model": model, "verbose": True})
        info = result.get("model_info", {}) if isinstance(result.get("model_info"), dict) else {}
        return {
            "model": model,
            "details": result.get("details", {}),
            "model_info": info,
            "parameter_count": info.get("general.parameter_count"),
            "license_metadata_present": bool(result.get("license")),
            "runtime_metadata": "reported_by_local_ollama_not_independent_license_verification",
        }

    def chat(self, model: str, messages: list[dict], *, keep_alive: str = "5m") -> dict:
        if not model.strip() or not messages:
            raise ValueError("model and at least one message are required")
        if any(not isinstance(item, dict) or item.get("role") not in {"system", "user", "assistant"} or not isinstance(item.get("content"), str) for item in messages):
            raise ValueError("messages must contain supported roles and string content")
        prompt_digest = hashlib.sha256(json.dumps(messages, sort_keys=True).encode("utf-8")).hexdigest()
        started = time.monotonic()
        result = self._post("/api/chat", {
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": keep_alive,
        })
        elapsed_ms = round((time.monotonic() - started) * 1000, 2)
        message = result.get("message", {})
        response_text = message.get("content", "") if isinstance(message, dict) else ""
        return {
            "model": result.get("model", model),
            "response": response_text,
            "prompt_sha256": prompt_digest,
            "response_sha256": hashlib.sha256(response_text.encode("utf-8")).hexdigest(),
            "total_duration_ns": result.get("total_duration"),
            "prompt_eval_count": result.get("prompt_eval_count"),
            "eval_count": result.get("eval_count"),
            "client_elapsed_ms": elapsed_ms,
            "runtime": "local_ollama",
            "training_claim": False,
        }
