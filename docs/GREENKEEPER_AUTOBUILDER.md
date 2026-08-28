# DreamCo Greenkeeper Auto-Builder

## Purpose

Turn recurring repository health failures into durable, testable capabilities instead of repeatedly applying one-off fixes.

## Control loop

`OBSERVE → CLASSIFY → DEDUPLICATE → ROOT-CAUSE → SELECT EXISTING SYSTEM → BUILD MISSING SYSTEM → TEST → SECURITY → BENCHMARK → VERIFY → REGISTER → MONITOR`

## Failure classes

- workflow/CI
- dependency/toolchain
- test/regression
- security
- benchmark/evaluation
- runtime/deployment
- PR/review/mergeability
- documentation/configuration
- unknown

## Auto-builder contract

When a failure has no suitable existing capability, Greenkeeper may generate a bounded validator, diagnostic, test, or repair scaffold. Generated systems must:

1. have a unique stable identifier;
2. declare inputs, outputs, permissions, and dependencies;
3. include deterministic validation where possible;
4. never claim success without evidence;
5. produce machine-readable artifacts;
6. have a timeout and resource budget;
7. avoid secret/private-data leakage;
8. be covered by the repository's required gates;
9. be eligible for retirement when unused or superseded;
10. be reviewed before changing protected production behavior.

## Anti-recursion safeguards

A generated health system cannot generate another system indefinitely. Maximum generation depth is one by default. A second-level system request becomes a queued design proposal requiring explicit verification. Duplicate capability IDs are rejected.

## Repair lifecycle

`DETECTED → TRIAGED → PLANNED → GENERATED → TESTING → VERIFIED → ACTIVE → MONITORED → RETIRED`

A failed generated repair returns to `TRIAGED`; it does not silently retry forever.

## Green criteria

Repository health is green only when all applicable mandatory gates have current successful evidence. `unknown`, `stale`, `blocked`, or `not executed` never becomes green by inference.

## Learning loop

Record:

- failure fingerprint;
- affected subsystem;
- attempted repair;
- verification result;
- regression result;
- benchmark delta;
- false-positive/false-negative feedback;
- repair recurrence.

Repeated failures should increase the priority of building a durable system for that failure class.
