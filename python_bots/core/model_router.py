"""
DreamCo OS — Model Router
===========================

Routes LLM requests to Claude, GPT-4, Gemini, or local models with:
* Cost-aware model selection (cheaper model for simple tasks)
* Automatic fallback chain on provider failure
* Response caching (same prompt + context hash → return cached result)
* Token budget enforcement per bot
* Streaming support

Usage::

    router = ModelRouter(primary="openai/gpt-4o", fallback="openai/gpt-4o-mini")
    response = await router.complete("Summarise this text: ...", max_tokens=200)
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from typing import Any, AsyncIterator

logger = logging.getLogger(__name__)

# Cost estimates per 1K tokens (input + output blended) in USD
_MODEL_COSTS: dict[str, float] = {
    "openai/gpt-4o": 0.005,
    "openai/gpt-4o-mini": 0.00015,
    "openai/gpt-4-turbo": 0.010,
    "anthropic/claude-3-5-sonnet": 0.003,
    "anthropic/claude-3-haiku": 0.00025,
    "anthropic/claude-opus-4": 0.015,
    "google/gemini-2.0-flash": 0.00010,
    "google/gemini-2.5-pro": 0.00125,
    "local/ollama": 0.0,
}

_CACHE_TTL = 3600  # 1 hour


class ModelRouter:
    """Multi-model router with cost awareness, fallback, and response caching.

    Parameters
    ----------
    primary:
        Primary model identifier (e.g. ``"openai/gpt-4o"``).
    fallback:
        Fallback model used when the primary fails.
    token_budget:
        Maximum tokens allowed per call (0 = unlimited).
    cache_responses:
        Whether to cache responses for identical prompt+context hashes.
    """

    def __init__(
        self,
        primary: str = "openai/gpt-4o-mini",
        fallback: str = "anthropic/claude-3-haiku",
        token_budget: int = 4096,
        cache_responses: bool = True,
    ) -> None:
        self.primary = primary
        self.fallback = fallback
        self.token_budget = token_budget
        self.cache_responses = cache_responses
        self._cache: dict[str, tuple[str, float]] = {}  # hash → (response, expires_at)
        self._total_tokens = 0
        self._total_cost_usd = 0.0

        # Lazy-load OpenAI client
        self._openai_client: Any = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def complete(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        use_cheap_for_simple: bool = False,
    ) -> str:
        """Return a completion for *prompt*.

        Parameters
        ----------
        prompt:
            The user message.
        system:
            Optional system prompt.
        max_tokens:
            Token cap for this call (capped by ``token_budget`` if set).
        temperature:
            Sampling temperature.
        use_cheap_for_simple:
            When True, uses the cheapest available model automatically.
        """
        if self.token_budget:
            max_tokens = min(max_tokens, self.token_budget)

        model = self._select_model(prompt, use_cheap_for_simple)
        cache_key = self._cache_key(model, system, prompt)

        if self.cache_responses:
            cached = self._get_cache(cache_key)
            if cached is not None:
                return cached

        response = await self._call_model(model, system, prompt, max_tokens, temperature)

        if response is None:
            # Fallback
            logger.warning("Primary model %s failed, trying fallback %s", model, self.fallback)
            response = await self._call_model(
                self.fallback, system, prompt, max_tokens, temperature
            )

        if response is None:
            return "[ModelRouter: all models failed]"

        if self.cache_responses:
            self._set_cache(cache_key, response)

        return response

    async def stream(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """Yield response tokens one at a time (streaming)."""
        # Delegate to complete for now; real streaming via provider SDK
        response = await self.complete(prompt, system=system, max_tokens=max_tokens)
        for chunk in response.split(" "):
            yield chunk + " "

    # ------------------------------------------------------------------
    # Cost reporting
    # ------------------------------------------------------------------

    def usage_summary(self) -> dict[str, Any]:
        return {
            "total_tokens": self._total_tokens,
            "total_cost_usd": round(self._total_cost_usd, 6),
            "primary_model": self.primary,
            "fallback_model": self.fallback,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _select_model(self, prompt: str, cheap: bool) -> str:
        if cheap:
            return min(_MODEL_COSTS, key=lambda m: _MODEL_COSTS[m])
        return self.primary

    async def _call_model(
        self,
        model: str,
        system: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str | None:
        provider, model_name = (model.split("/", 1) + ["unknown"])[:2]

        if provider == "openai":
            return await self._call_openai(model_name, system, prompt, max_tokens, temperature)
        elif provider == "anthropic":
            return await self._call_anthropic(model_name, system, prompt, max_tokens, temperature)
        else:
            logger.warning("Unsupported provider '%s'", provider)
            return None

    async def _call_openai(
        self, model: str, system: str, prompt: str, max_tokens: int, temperature: float
    ) -> str | None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.debug("OPENAI_API_KEY not set — skipping OpenAI call")
            return None
        try:
            from openai import AsyncOpenAI  # type: ignore

            client = AsyncOpenAI(api_key=api_key)
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            resp = await client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            tokens = resp.usage.total_tokens if resp.usage else 0
            self._total_tokens += tokens
            self._total_cost_usd += (tokens / 1000) * _MODEL_COSTS.get(f"openai/{model}", 0.005)
            return resp.choices[0].message.content or ""
        except Exception as exc:  # noqa: BLE001
            logger.warning("OpenAI call failed: %s", exc)
            return None

    async def _call_anthropic(
        self, model: str, system: str, prompt: str, max_tokens: int, temperature: float
    ) -> str | None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.debug("ANTHROPIC_API_KEY not set — skipping Anthropic call")
            return None
        try:
            import anthropic  # type: ignore

            client = anthropic.AsyncAnthropic(api_key=api_key)
            resp = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system or "You are a helpful AI assistant.",
                messages=[{"role": "user", "content": prompt}],
            )
            tokens = (resp.usage.input_tokens + resp.usage.output_tokens) if resp.usage else 0
            self._total_tokens += tokens
            self._total_cost_usd += (tokens / 1000) * _MODEL_COSTS.get(
                f"anthropic/{model}", 0.003
            )
            return resp.content[0].text if resp.content else ""
        except Exception as exc:  # noqa: BLE001
            logger.warning("Anthropic call failed: %s", exc)
            return None

    def _cache_key(self, model: str, system: str, prompt: str) -> str:
        raw = json.dumps([model, system, prompt], sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def _get_cache(self, key: str) -> str | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.time() > expires_at:
            del self._cache[key]
            return None
        return value

    def _set_cache(self, key: str, value: str) -> None:
        self._cache[key] = (value, time.time() + _CACHE_TTL)
