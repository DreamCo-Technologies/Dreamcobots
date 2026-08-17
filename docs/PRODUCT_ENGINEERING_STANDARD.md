# DreamCo Product Engineering Standard

## Product principle

Every capability must answer three questions:

1. Who benefits?
2. What measurable outcome does it produce?
3. How do we prove the outcome?

## Capability lifecycle

```text
idea
  ↓
problem statement
  ↓
capability contract
  ↓
ownership
  ↓
prototype
  ↓
benchmark
  ↓
sandbox
  ↓
production
  ↓
telemetry
  ↓
feedback
  ↓
versioned improvement
```

## Revenue-capable features

A feature is not considered a money-maker merely because it estimates a dollar amount. DreamCo must distinguish:

- opportunity value;
- expected value;
- eligible value;
- user-confirmed value;
- provider-confirmed value;
- realized revenue;
- realized savings.

Every revenue-producing capability should emit an attribution event that can be reconciled against the underlying provider/source.

## User trust

Discovery systems should show source, timestamp, confidence, eligibility assumptions, exclusions and last verification time wherever those fields materially affect a user's decision.

## Automation

Automation should be progressive:

`recommend → prepare → preview → approve → execute → verify`.

High-impact external actions should not silently jump from discovery to execution.

## Data quality

Source records should retain provenance. Deduplication should produce a stable canonical record plus references to duplicate observations rather than destroying evidence.

## AI behavior

AI may rank, classify, summarize, propose and explain. Deterministic policy, validation and authorization remain authoritative for high-impact actions.

## Failure handling

Every user-visible workflow needs:

- timeout behavior;
- retry policy;
- idempotency strategy;
- partial-failure behavior;
- user-visible status;
- audit trail;
- recovery path.

## Observability

Measure at minimum:

- request volume;
- latency;
- error rate;
- successful outcome rate;
- source quality;
- capability confidence;
- external action count;
- realized business outcome.

## Release discipline

A feature is production-ready only when its contract, tests, monitoring, security policy, rollback path and owner exist. Documentation is part of the feature, not cleanup after it ships.
