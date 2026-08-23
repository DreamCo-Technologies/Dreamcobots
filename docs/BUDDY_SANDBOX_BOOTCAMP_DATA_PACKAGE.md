# Buddy Sandbox Bootcamp — Data Package

## Purpose

Create a governed training/evaluation package containing the useful gains produced by Buddy's Actions, device intelligence, division Superbots, legacy-bot consolidation, governance and builder systems.

A "gain" means a measurable improvement, validated capability, successful strategy, recovered failure, benchmark result, useful artifact, or capability gap discovered during sandbox work.

## Gain record

Each gain should capture:

- `gain_id`
- `mission_id`
- `action_id`
- `division`
- `superbot`
- `capability_id`
- `category`
- `description`
- `baseline`
- `result`
- `delta`
- `evidence`
- `verification_status`
- `reproducibility`
- `cost`
- `latency`
- `failure_modes`
- `dependencies`
- `risk_class`
- `created_at`
- `source_commit`
- `promotion_status`

## Gain categories

- capability improvement;
- reliability improvement;
- latency improvement;
- cost reduction;
- quality improvement;
- successful strategy;
- recovery strategy;
- tool integration;
- device capability;
- workflow optimization;
- test/evaluation result;
- newly discovered capability gap;
- security/compliance improvement;
- revenue-impact evidence where legitimately measured.

## Bootcamp lanes

```text
RAW EXPERIENCE
      ↓
STRUCTURE
      ↓
VERIFY
      ↓
REPLAY / SIMULATE
      ↓
BENCHMARK
      ↓
COMPARE TO BASELINE
      ↓
PROMOTE USEFUL GAINS
      ↓
REGRESSION TEST
      ↓
PUBLISH TO GOVERNED KNOWLEDGE
```

## Promotion states

`captured → verified → reproducible → benchmarked → candidate → promoted → regressed → retired`

A raw model claim or unverified action result must not become a trusted training strategy merely because it looks successful.

## Dataset partitions

- `experience/` — raw structured observations;
- `verified/` — independently checked outcomes;
- `benchmarks/` — baseline and improvement measurements;
- `strategies/` — reusable validated strategies;
- `failures/` — failures and recovery evidence;
- `capability_gaps/` — missing tools/skills/dependencies;
- `regressions/` — previously successful behavior that later degraded;
- `lineage/` — source bot, division, Superbot and commit provenance.

## Sandbox isolation

Bootcamp training/evaluation should use isolated data and execution environments. Production credentials, secrets and unauthorized private data must not be copied into the training package.

## Learning boundary

The package is for evaluation and governed improvement. It does not authorize Buddy to autonomously modify production behavior. Promotion requires the applicable governance, testing and deployment controls.

## Cross-division transfer

A gain can be proposed for another division when capability similarity supports transfer. The receiving division must validate the gain in its own evaluation environment before promotion.

## Continuous bootcamp

The package should be refreshed from new validated experiences so the Bootcamp becomes a living evaluation curriculum rather than a static dataset.
