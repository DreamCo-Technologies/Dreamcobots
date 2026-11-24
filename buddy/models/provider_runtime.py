"""Governed OpenAI-compatible inference adapter; credentials remain in env vars."""
from __future__ import annotations
import json, os, re, time, urllib.error, urllib.request, uuid
from typing import Any, Callable

PROVIDER_ID = re.compile(r"^[a-z][a-z0-9_-]{1,39}$")
MODEL_ID = re.compile(r"^[A-Za-z0-9._:/-]{2,200}$")
ALLOWED_STATES = {"CONNECTED", "TESTED", "PRODUCTION"}

class ProviderRuntimeError(RuntimeError):
    """A provider request was rejected or could not be safely completed."""

def validate_provider(provider: dict[str, Any]) -> None:
    required = ("provider_id", "protocol", "lifecycle_state", "enabled", "base_url_env",
                "api_key_env", "allowed_models", "data_classification_max", "output_training_permission")
    if not isinstance(provider, dict) or any(k not in provider for k in required):
        raise ProviderRuntimeError("provider registry record is incomplete")
    if not PROVIDER_ID.fullmatch(str(provider["provider_id"])):
        raise ProviderRuntimeError("provider_id is invalid")
    if provider["protocol"] != "openai_compatible_chat_completions":
        raise ProviderRuntimeError("unsupported provider protocol")
    if provider["lifecycle_state"] not in ALLOWED_STATES or provider["enabled"] is not True:
        raise ProviderRuntimeError("provider is not enabled and independently tested")
    if not isinstance(provider["allowed_models"], list) or not provider["allowed_models"]:
        raise ProviderRuntimeError("provider has no explicit model allowlist")
    if provider["output_training_permission"] not in {"ALLOWED", "PROHIBITED", "UNKNOWN"}:
        raise ProviderRuntimeError("output training permission must be explicit")
    for key in ("base_url_env", "api_key_env"):
        if not re.fullmatch(r"[A-Z][A-Z0-9_]{2,80}", str(provider[key])):
            raise ProviderRuntimeError("provider secret references must be environment variable names")

class GovernedProviderRuntime:
    def __init__(self, providers: list[dict[str, Any]], *, opener: Callable[..., Any] | None = None,
                 environ: dict[str, str] | None = None):
        self.providers = {item.get("provider_id"): item for item in providers if isinstance(item, dict)}
        if len(self.providers) != len(providers):
            raise ProviderRuntimeError("provider IDs must be present and unique")
        self.opener = opener or urllib.request.urlopen
        self.environ = os.environ if environ is None else environ

    def infer(self, provider_id: str, model_id: str, messages: list[dict[str, str]], *,
              approval_id: str, data_classification: str = "internal",
              max_tokens: int = 1024, timeout_seconds: int = 30) -> dict[str, Any]:
        provider = self.providers.get(provider_id)
        if provider is None:
            raise ProviderRuntimeError("provider is not registered")
        validate_provider(provider)
        if model_id not in provider["allowed_models"] or not MODEL_ID.fullmatch(model_id):
            raise ProviderRuntimeError("model is not explicitly allowlisted for this provider")
        if not approval_id or not str(approval_id).strip():
            raise ProviderRuntimeError("per-request inference approval reference is required")
        levels = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}
        if data_classification not in levels or provider["data_classification_max"] not in levels:
            raise ProviderRuntimeError("unknown data classification")
        if levels[data_classification] > levels[provider["data_classification_max"]]:
            raise ProviderRuntimeError("request data classification exceeds provider approval")
        if not isinstance(messages, list) or not messages or any(
            not isinstance(m, dict) or m.get("role") not in {"system", "user", "assistant"}
            or not isinstance(m.get("content"), str) for m in messages):
            raise ProviderRuntimeError("messages must be a non-empty list of role/content strings")
        if isinstance(max_tokens, bool) or not isinstance(max_tokens, int) or not 1 <= max_tokens <= 8192:
            raise ProviderRuntimeError("max_tokens must be between 1 and 8192")
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= 120:
            raise ProviderRuntimeError("timeout_seconds must be between 1 and 120")
        base_url = str(self.environ.get(provider["base_url_env"], "")).strip().rstrip("/")
        api_key = str(self.environ.get(provider["api_key_env"], "")).strip()
        if not base_url or not api_key:
            raise ProviderRuntimeError("provider endpoint or secret is not configured")
        if not base_url.startswith("https://"):
            raise ProviderRuntimeError("provider endpoint must use HTTPS")
        request_id = "infer-" + uuid.uuid4().hex[:16]
        body = json.dumps({"model": model_id, "messages": messages, "max_tokens": max_tokens}).encode()
        request = urllib.request.Request(base_url + "/chat/completions", data=body, method="POST",
            headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json",
                     "X-DreamCo-Request-ID": request_id})
        started = time.monotonic()
        try:
            with self.opener(request, timeout=timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
                if not 200 <= getattr(response, "status", 200) < 300:
                    raise ProviderRuntimeError("provider returned a non-success status")
        except ProviderRuntimeError:
            raise
        except Exception as exc:
            raise ProviderRuntimeError("provider request failed (" + type(exc).__name__ + ")") from None
        choice = (payload.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        if not isinstance(message.get("content"), str):
            raise ProviderRuntimeError("provider response did not contain a text completion")
        usage = payload.get("usage") if isinstance(payload.get("usage"), dict) else {}
        return {"schema": "dreamco.inference_evidence.v1", "status": "COMPLETED",
            "request_id": request_id, "provider_id": provider_id, "model_id": model_id,
            "provider_response_id": str(payload.get("id") or ""), "output_text": message["content"],
            "usage": {k: usage[k] for k in ("prompt_tokens", "completion_tokens", "total_tokens")
                      if isinstance(usage.get(k), int)},
            "latency_ms": round((time.monotonic() - started) * 1000, 2),
            "approval_ref": approval_id, "data_classification": data_classification,
            "output_training_permission": provider["output_training_permission"],
            "training_use_authorized": provider["output_training_permission"] == "ALLOWED",
            "credentials_emitted": False}
