from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class AISource:
    source_id: str
    provider: str
    modalities: tuple[str, ...]
    domains: tuple[str, ...]
    cost_score: float
    speed_score: float
    quality_score: float
    reliability_score: float
    privacy_score: float = 0.5
    metadata: dict[str, str] = field(default_factory=dict)

    def composite_score(self, *, domain: str, max_cost_score: float = 1.0) -> float:
        domain_bonus = 0.15 if domain in self.domains else 0.0
        cost_penalty = max(0.0, self.cost_score - max_cost_score) * 0.5
        return (
            (self.quality_score * 0.35)
            + (self.speed_score * 0.2)
            + (self.reliability_score * 0.3)
            + (self.privacy_score * 0.15)
            + domain_bonus
            - cost_penalty
        )


class SourcesManager:
    def __init__(self, *, sources: Iterable[AISource] | None = None) -> None:
        self._sources: dict[str, AISource] = {}
        for source in sources or self.default_sources():
            self.register_source(source)

    @staticmethod
    def default_sources() -> tuple[AISource, ...]:
        return (
            AISource("hf_text", "huggingface", ("text",), ("automation", "research"), 0.2, 0.7, 0.8, 0.85),
            AISource("openrouter_mix", "openrouter", ("text", "code"), ("engineering", "growth"), 0.35, 0.9, 0.88, 0.82),
            AISource("runway_video", "runway", ("video",), ("creative", "marketing"), 0.8, 0.65, 0.92, 0.8),
            AISource("stability_image", "stability", ("image",), ("creative", "marketing"), 0.55, 0.75, 0.9, 0.84),
            AISource("together_code", "together", ("code", "text"), ("engineering", "automation"), 0.3, 0.85, 0.84, 0.81),
        )

    def register_source(self, source: AISource) -> None:
        self._sources[source.source_id] = source

    def list_sources(self) -> list[AISource]:
        return list(self._sources.values())

    def rank_sources(
        self,
        *,
        domain: str,
        modality: str | None = None,
        max_cost_score: float = 1.0,
    ) -> list[AISource]:
        candidates = self.list_sources()
        if modality:
            candidates = [source for source in candidates if modality in source.modalities]
        return sorted(
            candidates,
            key=lambda source: source.composite_score(domain=domain, max_cost_score=max_cost_score),
            reverse=True,
        )

