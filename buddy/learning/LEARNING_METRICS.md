# Buddy Learning Metrics

Buddy should reduce dependence on external models by demonstrating verified native capability, not by deleting its model fleet.

## Primary signals

- `native_solve_rate`: verified tasks solved without external assistance.
- `external_assistance_rate`: verified tasks requiring external assistance.
- `verified`: total verified learning events.
- `promoted`: capabilities promoted after policy gates.

## Decision rule

A capability is eligible for promotion only after the repository's mastery policy is satisfied. External-model success is retained as useful teaching evidence but does not count as native mastery.

## Fleet preservation

The original DreamCo model catalog remains intact. OpenRouter and other providers remain available as supplemental teachers/fallbacks until native parity is demonstrated and regression-protected.

## Interpretation

Improvement means native solve rate rises while external assistance rate falls on comparable benchmark cohorts. A lower model count by itself is not evidence of learning.
