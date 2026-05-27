from __future__ import annotations

from collections import deque

from global_ai_sources.sources_manager import AISource, SourcesManager


class ResourceOptimizer:
    def __init__(self, *, manager: SourcesManager | None = None, cache_size: int = 128) -> None:
        self.manager = manager or SourcesManager()
        self.cache_size = max(8, cache_size)
        self._routing_cache: dict[str, AISource] = {}
        self._cache_order: deque[str] = deque()

    def select_source(self, *, task: str, domain: str, modality: str, max_cost_score: float = 1.0) -> AISource | None:
        cache_key = f"{task}|{domain}|{modality}|{max_cost_score}"
        if cache_key in self._routing_cache:
            return self._routing_cache[cache_key]
        ranked = self.manager.rank_sources(domain=domain, modality=modality, max_cost_score=max_cost_score)
        selected = ranked[0] if ranked else None
        if selected is not None:
            self._cache(cache_key, selected)
        return selected

    def fallback_chain(self, *, domain: str, modality: str, max_cost_score: float = 1.0, limit: int = 3) -> list[AISource]:
        ranked = self.manager.rank_sources(domain=domain, modality=modality, max_cost_score=max_cost_score)
        return ranked[: max(1, limit)]

    def efficiency_score(self, *, successful_calls: int, total_calls: int, average_cost_score: float) -> float:
        if total_calls <= 0:
            return 0.0
        success_rate = successful_calls / total_calls
        cost_efficiency = max(0.0, 1.0 - average_cost_score)
        return round(((success_rate * 0.7) + (cost_efficiency * 0.3)) * 100, 2)

    def _cache(self, key: str, source: AISource) -> None:
        self._routing_cache[key] = source
        self._cache_order.append(key)
        while len(self._cache_order) > self.cache_size:
            oldest = self._cache_order.popleft()
            self._routing_cache.pop(oldest, None)

