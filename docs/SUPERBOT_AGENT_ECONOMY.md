# Superbot Agent Economy

## Purpose

Allow DreamCo capabilities to discover, request and compose reusable internal services without creating duplicate bots.

## Capability registry

Each registered capability should expose:

- stable capability ID;
- owner division;
- version;
- contract;
- inputs/outputs;
- permissions;
- cost estimate;
- latency profile;
- reliability history;
- benchmark evidence;
- security classification;
- compatible consumers.

## Capability selection

When a Superbot needs a capability:

```text
need
 ↓
registry search
 ↓
compatibility filter
 ↓
policy filter
 ↓
quality/cost ranking
 ↓
request
 ↓
execute
 ↓
verify
 ↓
record outcome
```

## Internal capability economics

Capabilities can be measured by value created, compute cost, latency, reliability and downstream outcome. This is an internal optimization mechanism, not an unrestricted financial market.

Useful metrics include:

- successful calls;
- failed calls;
- cost per successful outcome;
- value attributed to the capability;
- reuse rate;
- maintenance burden;
- regression rate.

## Capability composition

Complex Superbots should compose capabilities rather than duplicate them. A new capability is justified when composition cannot satisfy the requirement and evidence demonstrates a genuine gap.

## Versioning

Providers must preserve backward compatibility where practical. Breaking changes require migration plans and consumer impact analysis.

## Governance

No capability may grant a caller more permissions than the caller already has. Capability providers cannot bypass platform policy through delegation.
