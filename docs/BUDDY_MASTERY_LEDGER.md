# Buddy Mastery Ledger

The mastery ledger is the source of truth for whether a capability is experimental, trusted, or needs remediation.

## Capability states

`unknown → learning → practicing → evaluated → provisionally_mastered → trusted → regressed → remediation`

## Promotion evidence

A capability should not be promoted because Buddy completed a course, generated a solution once, or achieved a benchmark once. Promotion requires configurable evidence across:

- correctness / quality
- repeatability
- speed / latency
- safety and permission compliance
- regression protection
- cost efficiency
- transfer to unseen tasks
- provenance/evidence quality

## Independent evaluation

The system should separate the agent that performs a task from the evaluator that scores it. Where practical, use multiple evaluators and a held-out test set to reduce self-grading bias.

## Capability passport

Each capability record should expose:

- current state
- current score and confidence
- historical scores
- best verified score
- speed and cost
- known weaknesses
- successful strategies
- failed strategies
- relevant learning resources
- benchmark versions
- last evaluation time
- regression status
- evidence IDs
- promotion decision and reason

## Transfer requirement

A capability should include at least one unseen or differently phrased task before it is considered durable. Domain transfer tests may be added when the capability is intended to generalize across contexts.

## Human control

Consequential external actions remain subject to configured permissions and approvals. Mastery of a skill does not grant permission to exercise that skill on external systems.
