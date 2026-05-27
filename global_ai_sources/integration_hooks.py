from __future__ import annotations

from dataclasses import dataclass

from global_ai_sources.resource_optimizer import ResourceOptimizer


@dataclass(frozen=True)
class IntegrationDecision:
    task: str
    domain: str
    modality: str
    source_id: str | None
    fallback_chain: tuple[str, ...]


def choose_source_for_task(
    *,
    task: str,
    domain: str,
    modality: str,
    optimizer: ResourceOptimizer | None = None,
) -> IntegrationDecision:
    opt = optimizer or ResourceOptimizer()
    selected = opt.select_source(task=task, domain=domain, modality=modality)
    fallback = opt.fallback_chain(domain=domain, modality=modality)
    return IntegrationDecision(
        task=task,
        domain=domain,
        modality=modality,
        source_id=selected.source_id if selected else None,
        fallback_chain=tuple(item.source_id for item in fallback),
    )

