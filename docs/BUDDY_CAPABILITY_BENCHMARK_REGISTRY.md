# Buddy Capability Benchmark Registry

## Purpose

Define a common registry so Bootcamp, Sandbox, personal Buddy training and the Actions system can use the same measurable capability definitions.

## Benchmark record

Each benchmark should define:

- capability_id;
- name;
- version;
- skill dimensions;
- difficulty;
- prerequisites;
- task generator/source;
- training-data separation policy;
- scoring rubric;
- pass threshold;
- holdout policy;
- transfer policy;
- regression suite;
- security/privacy requirements;
- cost/time budget;
- evidence format;
- expiration/revalidation policy.

## Capability dimensions

A benchmark should separate, where relevant:

- knowledge;
- reasoning;
- planning;
- execution;
- tool use;
- communication;
- accuracy;
- reliability;
- safety;
- efficiency;
- generalization.

## Example capability: debugging

```text
CAPABILITY: debugging

Baseline:
- reproduce a known bug;
- identify likely root cause;
- propose a safe patch.

Bootcamp:
- logs and stack traces;
- minimal reproduction;
- dependency/runtime diagnosis;
- test-driven repair;
- regression prevention;
- debugging under ambiguity.

Sandbox:
- isolated repository;
- seeded bugs;
- hidden tests;
- controlled dependencies;
- automatic cleanup.

Pass:
- original bug fixed;
- hidden tests pass;
- no prohibited changes;
- transfer task passes;
- regression suite remains healthy.
```

## Example capability: research

Measure:

- source selection;
- evidence extraction;
- contradiction handling;
- citation/provenance;
- synthesis;
- uncertainty;
- freshness awareness.

## Example capability: coding

Measure:

- requirements understanding;
- implementation correctness;
- tests;
- debugging;
- security;
- performance;
- maintainability;
- transfer.

## Example capability: visual understanding

Measure:

- object/structure recognition;
- OCR where appropriate;
- diagram interpretation;
- UI understanding;
- instruction following;
- uncertainty.

## Benchmark lifecycle

```text
DRAFT
 -> VALIDATE
 -> BASELINE
 -> TRAINING
 -> HOLDOUT
 -> TRANSFER
 -> REGRESSION
 -> CERTIFIED
 -> MONITORED
 -> REVALIDATED / DEPRECATED
```

## Fairness and validity

Benchmarks should measure the intended skill rather than unrelated advantages such as memorization, formatting tricks or access to hidden answers.

Scores should include enough detail to diagnose weaknesses rather than only one aggregate number.

## User-facing result

Never say only:

> 84%

Prefer:

> **Debugging: 84%**
> 
> Root-cause diagnosis: 91%
> Patch correctness: 86%
> Regression prevention: 72%
> Transfer: 81%
> Safety: 98%
> 
> **Recommended next lesson: regression testing**

## Registry rule

A capability can be added to Bootcamp only when it has a measurable benchmark, safe sandbox strategy, training/holdout separation and a clear definition of mastery.
