# Superbot Self-Discovery System

## Purpose

Continuously identify useful missing capabilities, weak workflows, duplicated implementations, emerging tools and opportunities for improvement without allowing uncontrolled bot proliferation.

## Discovery sources

1. User ideas and feedback.
2. Production telemetry.
3. Failed tasks and recovery logs.
4. Benchmark regressions.
5. Repeated manual work.
6. Capability gaps in division contracts.
7. New tools/APIs/models approved by platform policy.
8. Market and domain changes.
9. Cross-division capability requests.
10. Revenue/savings opportunities.

## Discovery pipeline

```text
OBSERVE
 ↓
CLUSTER SIGNALS
 ↓
IDENTIFY GAP / OPPORTUNITY
 ↓
ESTIMATE VALUE + RISK
 ↓
FIND EXISTING CAPABILITY
 ↓
REUSE / EXTEND / COMPOSE
 ↓ if none
PROPOSE NEW CAPABILITY
 ↓
ASSIGN OWNER
 ↓
BUILD + TEST
 ↓
MEASURE
 ↓
PROMOTE OR REJECT
```

## Anti-duplication gate

Before proposing a new capability, search:

- canonical capability registry;
- division contracts;
- shared tools;
- workflows;
- legacy aliases;
- recent proposals;
- existing APIs/connectors.

If an equivalent exists, the discovery result becomes an extension or composition proposal.

## Opportunity scoring

Score candidate ideas using:

- expected user value;
- expected business value;
- frequency;
- confidence in evidence;
- implementation effort;
- operational cost;
- security/policy risk;
- differentiation;
- strategic fit.

High value and low/managed risk should be prioritized.

## Learning from failure

A failed task is not merely an error. The system should classify whether the failure indicates:

- missing knowledge;
- missing tool;
- bad tool selection;
- inadequate planning;
- weak verification;
- policy restriction;
- data quality issue;
- external provider failure;
- product UX problem.

The resulting gap should enter the same capability pipeline.

## Governance

Self-discovery may propose work and prepare evidence. It does not grant itself permissions, deploy high-impact changes, bypass CI, or declare success without measured evidence.
