"""Native, approval-gated Anthropic Messages and Gemini GenerateContent adapters."""
from __future__ import annotations
import json, os, re, time
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

class NativeProviderError(RuntimeError):
    """A native provider request failed a policy or transport check."""

MODEL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,180}$")

def _validate(model: str, allowed_models: list[str] | tuple[str, ...], approval_id: str,
              max_tokens: int, timeout_seconds: int) -> None:
    if not approval_id or not approval_id.strip():
        raise NativeProviderError("paid_request_requires_approval_id")
    if not isinstance(model, str) or not MODEL_ID.fullmatch(model):
        raise NativeProviderError("invalid_model_id")
    if not allowed_models or model not in allowed_models:
        raise NativeProviderError("model_not_in_owner_approved_allowlist")
    if isinstance(max_tokens, bool) or not isinstance(max_tokens, int) or not 1 <= max_tokens <= 8192:
        raise NativeProviderError("max_tokens_out_of_range")
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= 120:
        raise NativeProviderError("timeout_out_of_range")

def _post(url: str, headers: dict[str, str], body: dict[str, Any], timeout: int,
          opener: Callable[..., Any] | None) -> tuple[dict[str, Any], float]:
    request=Request(url,data=json.dumps(body).encode(),method="POST",
                    headers={**headers,"Content-Type":"application/json","Accept":"application/json"})
    started=time.monotonic()
    try:
        with (opener or urlopen)(request,timeout=timeout) as response:
            status=int(response.status)
            payload=json.loads(response.read().decode("utf-8"))
        if status<200 or status>=300: raise NativeProviderError(f"provider_http_status_{status}")
    except NativeProviderError: raise
    except HTTPError as exc: raise NativeProviderError(f"provider_http_status_{int(exc.code)}") from None
    except (URLError,TimeoutError,OSError,ValueError,json.JSONDecodeError) as exc:
        raise NativeProviderError(f"provider_request_failed_{type(exc).__name__}") from None
    except Exception as exc: raise NativeProviderError(f"provider_request_failed_{type(exc).__name__}") from None
    if not isinstance(payload,dict): raise NativeProviderError("provider_response_not_an_object")
    return payload,round((time.monotonic()-started)*1000,2)

def anthropic_messages(model: str, messages: list[dict[str,str]], *,
        allowed_models: list[str] | tuple[str,...], paid_approval_id: str,
        max_tokens: int=1024, system: str="", timeout_seconds: int=30,
        opener: Callable[...,Any] | None=None) -> dict[str,Any]:
    _validate(model,allowed_models,paid_approval_id,max_tokens,timeout_seconds)
    key=os.environ.get("ANTHROPIC_API_KEY","").strip()
    if not key: raise NativeProviderError("anthropic_credential_not_configured")
    if not isinstance(messages,list) or not messages or len(messages)>100:
        raise NativeProviderError("messages_must_contain_1_to_100_items")
    clean=[]
    for item in messages:
        if not isinstance(item,dict) or item.get("role") not in {"user","assistant"}:
            raise NativeProviderError("invalid_anthropic_message_role")
        value=item.get("content")
        if not isinstance(value,str) or not value.strip() or len(value)>100000:
            raise NativeProviderError("message_content_invalid_or_too_large")
        clean.append({"role":item["role"],"content":value})
    if not isinstance(system,str) or len(system)>100000:
        raise NativeProviderError("system_prompt_invalid_or_too_large")
    body={"model":model,"max_tokens":max_tokens,"messages":clean}
    if system.strip(): body["system"]=system
    payload,latency=_post("https://api.anthropic.com/v1/messages",
        {"x-api-key":key,"anthropic-version":"2023-06-01","User-Agent":"DreamCo-Buddy/1.0"},
        body,timeout_seconds,opener)
    content=payload.get("content")
    if not isinstance(content,list): raise NativeProviderError("anthropic_response_missing_content")
    answer="".join(x.get("text","") for x in content if isinstance(x,dict) and x.get("type")=="text")
    if not answer: raise NativeProviderError("anthropic_response_missing_text")
    usage=payload.get("usage") or {}
    return {"status":"COMPLETED","provider_id":"anthropic","model":payload.get("model",model),
        "response_text":answer,"usage":{"prompt_tokens":usage.get("input_tokens"),
        "completion_tokens":usage.get("output_tokens")},"latency_ms":latency,
        "paid_approval_id":paid_approval_id,"credentials_emitted":False,"provider_raw_response_stored":False}

def gemini_generate_content(model: str, messages: list[dict[str,str]], *,
        allowed_models: list[str] | tuple[str,...], paid_approval_id: str,
        max_tokens: int=1024, system: str="", timeout_seconds: int=30,
        opener: Callable[...,Any] | None=None) -> dict[str,Any]:
    _validate(model,allowed_models,paid_approval_id,max_tokens,timeout_seconds)
    key=os.environ.get("GEMINI_API_KEY","").strip()
    if not key: raise NativeProviderError("gemini_credential_not_configured")
    if not isinstance(messages,list) or not messages or len(messages)>100:
        raise NativeProviderError("messages_must_contain_1_to_100_items")
    contents=[]
    for item in messages:
        if not isinstance(item,dict) or item.get("role") not in {"user","assistant"}:
            raise NativeProviderError("invalid_gemini_message_role")
        value=item.get("content")
        if not isinstance(value,str) or not value.strip() or len(value)>100000:
            raise NativeProviderError("message_content_invalid_or_too_large")
        contents.append({"role":"user" if item["role"]=="user" else "model","parts":[{"text":value}]})
    if not isinstance(system,str) or len(system)>100000:
        raise NativeProviderError("system_prompt_invalid_or_too_large")
    body={"contents":contents,"generationConfig":{"maxOutputTokens":max_tokens}}
    if system.strip(): body["systemInstruction"]={"parts":[{"text":system}]}
    payload,latency=_post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        {"x-goog-api-key":key,"User-Agent":"DreamCo-Buddy/1.0"},body,timeout_seconds,opener)
    candidates=payload.get("candidates")
    if not isinstance(candidates,list) or not candidates:
        raise NativeProviderError("gemini_response_missing_candidates")
    parts=(candidates[0].get("content") or {}).get("parts",[])
    answer="".join(p.get("text","") for p in parts if isinstance(p,dict))
    if not answer: raise NativeProviderError("gemini_response_missing_text")
    usage=payload.get("usageMetadata") or {}
    return {"status":"COMPLETED","provider_id":"gemini","model":model,"response_text":answer,
        "usage":{"prompt_tokens":usage.get("promptTokenCount"),
        "completion_tokens":usage.get("candidatesTokenCount"),"total_tokens":usage.get("totalTokenCount")},
        "latency_ms":latency,"paid_approval_id":paid_approval_id,
        "credentials_emitted":False,"provider_raw_response_stored":False}
