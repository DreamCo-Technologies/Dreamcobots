# Superbot Shared World Model

## Purpose

Give Division Superbots a common representation of entities, events, opportunities, tasks, capabilities and outcomes while keeping domain-specific logic owned by the correct division.

## Canonical entity types

- Person / Organization
- Product / Service
- Property / Asset
- Job / Contract
- Claim / Case
- Deal / Opportunity
- Transaction / Payment
- Document / Record
- Event / Observation
- Task / Goal
- Capability / Tool
- Experiment / Benchmark
- Outcome / Attribution

## Evidence model

Every important observation should be representable as:

```text
subject
predicate
object
source
observed_at
expires_at
confidence
provenance
owner
```

The world model is not automatically treated as truth. Conflicting observations remain distinguishable until resolved.

## Capability exchange

A Superbot may request another division's capability through a versioned contract:

```text
requester → capability_id → inputs → policy_context → execution → evidence → result
```

The requester does not copy the provider's implementation.

## Event-driven learning

Meaningful events should be available to the learning/evaluation system:

- task_started
- plan_created
- tool_selected
- tool_failed
- result_received
- verification_failed
- recovery_completed
- user_feedback
- outcome_confirmed
- revenue_confirmed
- regression_detected

Events should be immutable evidence records where practical.

## Conflict resolution

When sources disagree, preserve both observations, score source quality, apply domain policy and expose uncertainty. Never overwrite an observation merely because a newer model generated a different answer.

## Privacy and access

The shared model must enforce ownership and permission boundaries. Cross-division reuse means controlled capability access, not unrestricted access to all underlying data.
