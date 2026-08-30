"""Open-code perspective registry.

Buddy may study public/open-source repositories for architecture, tests,
algorithms, failure handling and design alternatives. It records provenance
and license metadata and favors independent reimplementation over blind copy.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class OpenCodePerspective:
    repository: str
    license: str
    perspective: str
    patterns_to_extract: tuple[str, ...]
    validation: tuple[str, ...] = ("sandbox", "benchmark", "holdout", "regression")


def synthesize_pattern(perspectives: list[OpenCodePerspective]) -> dict:
    """Return a research plan; actual code reuse remains license-gated."""
    return {
        "sources": [p.repository for p in perspectives],
        "perspectives": [p.perspective for p in perspectives],
        "patterns": sorted({x for p in perspectives for x in p.patterns_to_extract}),
        "validation": sorted({x for p in perspectives for x in p.validation}),
        "reuse_policy": "license-compatible reuse only; otherwise reimplement concepts",
    }
