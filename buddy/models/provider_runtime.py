"""Credential-safe, allowlisted OpenAI-compatible model serving."""
from __future__ import annotations
import json, os, re, time, uuid
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

class ModelServingError(RuntimeError):
    """A provider request was rejected or failed safely."""

@dataclass(frozen=True)
class Provider:
    provider_id: str
    endpoint: str
    secret_env: str
    allowed_models: tuple[str, ...]
    paid: bool
    # Conservative default until provider-specific contractual controls are verified.
    data_classification_max: str
    output_training_permission: str

PROVIDERS = {
    "openai": Provider("openai", "https://api.openai.com/v1/chat/completions", "OPENAI_API_KEY",
                       ("gpt-5.4-mini", "gpt-5.4", "gpt-4.1-mini"), True, "public", "UNKNOWN"),
    "openrouter": Provider("openrouter", "https://openrouter.ai/api/v1/chat/completions",
                           "OPENROUTER_API_KEY", (), True, "public", "UNKNOWN"),
}
MODEL_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,180}$")
CLASSIFICATION_LEVELS = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}


def _approved_models(provider_id: str, provider: Provider) -> tuple[str, ...]:
    """Return only explicitly approved model IDs for a provider."""
    if provider_id == "openrouter":
        return tuple(
            model.strip()
            for model in os.environ.get("DREAMCO_OPENROUTER_ALLOWED_MODELS", "").split(",")
            if model.strip()
        )
    return provider.allowed_models


def available_providers() -> list[dict[str, Any]]:
    return [
        {
            "provider_id": p.provider_id,
            "endpoint": p.endpoint,
            "credential_configured": bool(os.environ.get(p.secret_env)),
            "paid": p.paid,
            "model_allowlist_enforced": bool(_approved_models(p.provider_id, p)),
            "approved_model_count": len(_approved_models(p.provider_id, p)),
            "data_classification_max": p.data_classification_max,
            "output_training_permission": p.output_training_permission,
        }
        for p in PROVIDERS.values()
    ]

def chat_completion(provider_id: str, model: str, messages: list[dict[str, str]], *,
                    paid_approval_id: str = "", max_tokens: int = 512,
                    timeout_seconds: int = 30, data_classification: str = "public",
                    opener: Callable[..., Any] | None = None) -> dict[str, Any]:
    """Call a configured provider only after explicit paid-use approval."""
    provider = PROVIDERS.get(provider_id)
    if provider is None:
        raise ModelServingError("provider_not_allowlisted")
    if not isinstance(model, str) or not MODEL_PATTERN.fullmatch(model):
        raise ModelServingError("invalid_model_id")
    allowed_models = _approved_models(provider_id, provider)
    if not allowed_models or model not in allowed_models:
        raise ModelServingError("model_not_allowlisted_for_provider")
    if not isinstance(data_classification, str) or data_classification not in CLASSIFICATION_LEVELS:
        raise ModelServingError("unknown_data_classification")
    if provider.data_classification_max not in CLASSIFICATION_LEVELS:
        raise ModelServingError("provider_data_classification_policy_invalid")
    if CLASSIFICATION_LEVELS[data_classification] > CLASSIFICATION_LEVELS[provider.data_classification_max]:
        raise ModelServingError("request_data_classification_exceeds_provider_approval")
    if provider.paid and (not isinstance(paid_approval_id, str) or not paid_approval_id.strip()):
        raise ModelServingError("paid_request_requires_approval_id")
    if not isinstance(messages, list) or not messages or len(messages) > 100:
        raise ModelServingError("messages_must_contain_1_to_100_items")
    clean = []
    for item in messages:
        if not isinstance(item, dict) or item.get("role") not in {"system", "user", "assistant"}:
            raise ModelServingError("invalid_message_role_or_shape")
        content = item.get("content")
        if not isinstance(content, str) or not content.strip() or len(content) > 100000:
            raise ModelServingError("message_content_invalid_or_too_large")
        clean.append({"role": item["role"], "content": content})
    if isinstance(max_tokens, bool) or not isinstance(max_tokens, int) or not 1 <= max_tokens <= 8192:
        raise ModelServingError("max_tokens_out_of_range")
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= 120:
        raise ModelServingError("timeout_out_of_range")
    secret = os.environ.get(provider.secret_env, "").strip()
    if not secret:
        raise ModelServingError("provider_credential_not_configured")
    body = json.dumps({"model": model, "messages": clean, "max_tokens": max_tokens}).encode()
    request_id = "infer-" + uuid.uuid4().hex[:16]
    request = Request(provider.endpoint, data=body, method="POST", headers={
        "Authorization": f"Bearer {secret}", "Content-Type": "application/json",
        "Accept": "application/json", "User-Agent": "DreamCo-Buddy/1.0",
        "X-DreamCo-Request-ID": request_id})
    started = time.monotonic()
    try:
        with (opener or urlopen)(request, timeout=timeout_seconds) as response:
            status = int(response.status)
            payload = json.loads(response.read().decode("utf-8"))
        if status < 200 or status >= 300:
            raise ModelServingError(f"provider_http_status_{status}")
    except ModelServingError:
        raise
    except HTTPError as exc:
        raise ModelServingError(f"provider_http_status_{int(exc.code)}") from None
    except (URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        raise ModelServingError(f"provider_request_failed_{type(exc).__name__}") from None
    except Exception as exc:
        raise ModelServingError(f"provider_request_failed_{type(exc).__name__}") from None
    choices = payload.get("choices") if isinstance(payload, dict) else None
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise ModelServingError("provider_response_missing_choices")
    message = choices[0].get("message") or {}
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str):
        raise ModelServingError("provider_response_missing_text")
    usage = payload.get("usage") or {}
    return {"status": "COMPLETED", "request_id": request_id, "provider_id": provider_id,
            "model": str(payload.get("model") or model), "response_text": content,
            "usage": {k: usage.get(k) for k in ("prompt_tokens", "completion_tokens", "total_tokens")},
            "latency_ms": round((time.monotonic() - started) * 1000, 2),
            "paid_approval_id": paid_approval_id, "data_classification": data_classification,
            "output_training_permission": provider.output_training_permission,
            "training_use_authorized": provider.output_training_permission == "ALLOWED",
            "credentials_emitted": False, "provider_raw_response_stored": False}
