# DreamCo Frontier Superbot Loop

## Purpose

Turn new ideas submitted to DreamCo into governed capability improvements without creating another uncontrolled bot fleet.

## Idea intake

All approved ideas enter a canonical idea queue with:

- idea ID
- source/context
- problem statement
- proposed outcome
- target division
- related capabilities
- expected business/user value
- evidence/source links
- risk class
- status

## Builder cell per Division Superbot

Each division has a virtual builder cell, not necessarily a separate production runtime:

```text
Division Superbot
├── Scout Builder       → finds missing capabilities and external patterns
├── Architect Builder   → proposes contracts and system changes
├── Research Builder    → gathers evidence and benchmarks
├── Implementation Builder → creates code/workflow changes
├── Test Builder        → creates contract/unit/integration/E2E tests
├── Security Builder    → reviews permissions and attack surface
├── Performance Builder → benchmarks latency/cost/reliability
├── Revenue Builder     → validates measurable commercial outcomes
└── Release Builder     → prepares migration/PR/release evidence
```

Builder cells share the same division mission and must not create duplicate production identities.

## Improvement loop

```text
IDEA
 ↓
TRIAGE
 ↓
OWNER ASSIGNMENT
 ↓
RESEARCH
 ↓
GAP ANALYSIS
 ↓
ARCHITECTURE PROPOSAL
 ↓
SANDBOX PROTOTYPE
 ↓
BENCHMARK
 ↓
SECURITY/POLICY REVIEW
 ↓
PR
 ↓
CI + CODE TRUST
 ↓
HUMAN/APPROVAL GATE WHEN REQUIRED
 ↓
RELEASE
 ↓
TELEMETRY
 ↓
OUTCOME MEASUREMENT
 ↓
LEARNING
 ↓
NEXT ITERATION
```

## Frontier status

DreamCo must not claim "frontier" because a model or feature is new. A capability earns frontier-candidate status through evidence:

- benchmark improvement over the current baseline;
- reliable evaluation set;
- acceptable cost/latency;
- security and policy compliance;
- operational reliability;
- meaningful user/business outcome;
- reproducible test evidence;
- documented limitations.

## Autonomy boundaries

Builder cells may research, analyze, generate proposals, write tests, create branches and prepare pull requests when the repository permissions allow it.

Production external side effects, destructive migrations, spending and high-impact actions remain governed by explicit policy and approval gates.

## No self-modifying production code

The improvement loop may propose and validate changes, but it does not silently rewrite its own production policy or bypass CI/approval gates. Every material change remains version-controlled and reviewable.

## New idea rule

A new idea is routed to the existing Division Superbot with the best ownership match. If no division owns it, the architecture council proposes a new domain boundary before implementation. A new standalone bot is not the default solution.
