# Buddy Action Memory & Context Fabric

## Purpose

Give Buddy's Actions system durable, structured context without turning every past event into uncontrolled memory.

## Context layers

```text
CURRENT ACTION
   ↓
MISSION CONTEXT
   ↓
USER-AUTHORIZED PREFERENCES
   ↓
DIVISION / CAPABILITY CONTEXT
   ↓
VERIFIED HISTORICAL RESULTS
   ↓
GOVERNED LONG-TERM STRATEGIES
```

## Memory classes

- `ephemeral`: only needed during the current action;
- `mission`: retained for the mission lifecycle;
- `authorized_preference`: user-approved reusable preference;
- `operational`: system state, dependencies and capability health;
- `verified_strategy`: reusable strategy supported by evaluation evidence;
- `audit`: immutable governance record.

## Memory rules

Memory must have provenance, scope, timestamp and retention policy. Unverified model guesses are not promoted into durable strategies.

## Retrieval

Actions should retrieve only context relevant to the current mission, capability and authorization scope. Retrieval should support recency, relevance, reliability and provenance weighting.

## Contradictions

When sources conflict, Buddy should surface the conflict, prefer authoritative and newer evidence when appropriate, and avoid silently rewriting historical facts.

## Outcome learning

```text
ACTION
 ↓
OBSERVED OUTCOME
 ↓
VERIFICATION
 ↓
EVALUATION
 ↓
CANDIDATE STRATEGY
 ↓
SIMULATION / REPLAY
 ↓
PROMOTION IF VALIDATED
```

## Forgetting / retirement

Stale operational context, expired permissions and obsolete strategies should be retired according to policy. Audit history is retained according to governance requirements.
