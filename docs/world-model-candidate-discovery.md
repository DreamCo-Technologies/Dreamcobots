# Continuous World-Model Candidate Discovery

Buddy should not rely on a fixed list of world-model projects. It should continuously discover new candidates, review provenance and licensing, rank their usefulness, and convert promising techniques into original benchmarks.

## Candidate lifecycle

`search → metadata → provenance/license review → relevance ranking → technique extraction → original benchmark → sandbox → evidence → regression → candidate promotion`

## Ranking

A candidate is valuable when it contributes measurable progress toward Buddy's capability gaps. Popularity alone is not a ranking criterion.

Signals include benchmark relevance, evidence quality, openness, reproducibility, capability diversity, maintenance, hardware feasibility, license compatibility, and novelty.

## Independence

The candidate registry is a teacher registry, not a dependency registry. Buddy should use projects to learn concepts and evaluation methods, then build original implementations wherever practical.
