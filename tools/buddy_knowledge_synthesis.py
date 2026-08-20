#!/usr/bin/env python3
"""Build original, evidence-grounded learning artifacts from authorized source notes."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Iterable


@dataclass(frozen=True)
class Evidence:
    source_id: str
    claim: str
    kind: str = "fact"
    confidence: float = 0.5
    citation: str = ""


@dataclass(frozen=True)
class Synthesis:
    topic: str
    claims: tuple[str, ...]
    disagreements: tuple[str, ...]
    original_examples: tuple[str, ...]
    exercises: tuple[str, ...]
    evidence_ids: tuple[str, ...]


def evidence_id(item: Evidence) -> str:
    return sha256(f"{item.source_id}|{item.claim}|{item.citation}".encode()).hexdigest()[:16]


def synthesize(topic: str, evidence: Iterable[Evidence]) -> Synthesis:
    items = [item for item in evidence if item.claim.strip()]
    items.sort(key=lambda x: x.confidence, reverse=True)
    claims = tuple(dict.fromkeys(item.claim.strip() for item in items))
    disagreements = tuple(
        f"Review conflicting or differently scoped claims before presenting a single conclusion: {claim}"
        for claim in claims if len(claims) > 1 and any(other != claim for other in claims)
    )[:3]
    return Synthesis(
        topic=topic,
        claims=claims,
        disagreements=disagreements,
        original_examples=(
            f"Create a new real-world example for {topic}.",
            f"Create a counterexample that exposes a limitation of one approach to {topic}.",
        ),
        exercises=(
            f"Explain {topic} without consulting the source notes.",
            f"Solve an unseen problem involving {topic}.",
            f"Debug a flawed solution involving {topic}.",
            f"Compare two approaches to {topic} and justify the choice.",
        ),
        evidence_ids=tuple(evidence_id(item) for item in items),
    )


def build_learning_artifact(topic: str, evidence: Iterable[Evidence]) -> dict:
    result = synthesize(topic, evidence)
    return {
        "artifact_type": "original-learning-artifact",
        "synthesis": asdict(result),
        "rules": {
            "retain_provenance": True,
            "write_independently": True,
            "do_not_copy_protected_expression": True,
            "benchmark_unseen_tasks": True,
        },
    }
