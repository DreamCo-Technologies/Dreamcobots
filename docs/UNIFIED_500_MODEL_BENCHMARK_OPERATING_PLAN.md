# Unified 500-Model Benchmark Operating Plan

This document records the approved architecture for the public model comparison program.

## Single benchmark workflow

`.github/workflows/dreamco-unified-system.yml` is the dedicated owner of the 500-model benchmark program. It should remain one workflow even when internal execution is batched or safely parallelized.

Other Actions workflows are reserved for repository operations such as health, security, Pages deployment, releases, maintenance, and the Actions control surface.

## Evidence lifecycle

```text
catalog -> prospectus -> capability mapping -> task fixtures -> execution
       -> quality/speed/efficiency/reliability/safety/independence
       -> evidence ledger -> gap analysis -> repair -> dependent retest
       -> historical record -> Pages projection
```

## Status vocabulary

Use explicit states:

- `catalogued`
- `ready`
- `running`
- `passed`
- `failed`
- `blocked`
- `stale`
- `not_applicable`
- `needs_review`

Never interpret missing evidence as a pass.

## Independence vocabulary

- `native`: Buddy performed the task without external model assistance.
- `tool_assisted`: Buddy used allowed tools but no external model to supply the answer.
- `external_model_assisted`: another model materially contributed.
- `unknown`: evidence is insufficient.

Only `native` results can establish independent Buddy mastery.

## Quality gate

A benchmark gap closes only when the benchmark's defined quality/correctness criteria pass and the relevant safety and reliability gates pass. Speed or efficiency improvements alone cannot close a quality gap.

## Shared-fix rule

When multiple failures have a common root cause, prefer one shared framework/routing/tool/fixture repair over repeated bot-specific patches. Re-run all dependent suites affected by the shared change.

## Performance rule

Measure at least:

- wall-clock latency;
- time to useful result;
- throughput where meaningful;
- tool-call count;
- retries;
- resource use where measurable;
- benchmark orchestration duration;
- evidence-generation duration.

Do not optimize by weakening tests or reducing required quality gates.

## Public dashboard rule

Every publicly disclosable benchmark record should have a Pages representation with its source/version, status, last verification time, and evidence reference. Private credentials, private data, restricted endpoints, and privileged controls must never enter public dashboard data.

## Staleness rule

A changed model version, benchmark fixture, rubric, tool permission, or material execution environment invalidates affected comparisons until they are refreshed.

## Cost rule

The workflow must not silently trigger paid model/API calls. Evaluations requiring paid access must be explicitly configured and approved outside the default catalog/verification path.

## Benchmark interpretation

A reference model is a comparator, not universal ground truth. Results are task- and condition-specific. A single overall score must not hide capability-specific strengths and weaknesses.
