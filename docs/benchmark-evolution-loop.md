# Buddy Benchmark Evolution Loop

A benchmark system should improve its tests without allowing the tests to become easier or contaminated.

## Continuous loop

`score → gap → research → original test → variants → locked test → sandbox → score → failure analysis → repair → retest → regression → promote/defer`

## Difficulty expansion

Buddy can make tests harder through novelty, complexity, time/resource constraints, multi-step dependencies, ambiguous inputs, edge cases, adversarial inputs, cross-domain transfer, and long-horizon tasks.

## Integrity

Test sets are locked and versioned. Test results do not become training data for the same evaluation. Previous scores and failures remain preserved so progress cannot be faked by moving the goalposts.

## Priority

The system prioritizes safety, high human value, productivity gains, expensive failure modes, broad transfer, user demand, government/business value, and research value.

## Never-stop behavior

A difficult problem creates a checkpoint and recovery task. Buddy continues unrelated work and returns to the difficult case later. Permanent failure is not a valid workflow state; the system may remain `blocked`, `deferred`, or `unknown` until evidence changes.
