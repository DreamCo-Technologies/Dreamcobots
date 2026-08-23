# DreamCo 65 MasterBot Actions Command Center

## Purpose

This document defines the canonical Actions-page contract for the 65 MasterBots. The existing 45 domain divisions remain intact; 20 platform/capability MasterBots extend the architecture to 65. The registry is machine-readable in `config/masterbot-65-registry.json`.

## Hierarchy

`Buddy -> 65 MasterBots -> sub-bots -> capabilities/tools/resources -> sandbox -> benchmarks -> gap closure`

Every bot has one primary MasterBot owner. Cross-domain work uses collaborator links instead of duplicate ownership. Grok AGI bots, Bots App bots, Real Estate bots, and bots discovered in the other DreamCo repositories retain source lineage.

## Per-division prospectus

Every MasterBot dashboard must expose:

1. **Mission** — what the division owns and what success means.
2. **Capability map** — skills, tools, APIs, websites/resources and dependencies.
3. **Sub-bot workforce** — assigned specialists, status, performance and lineage.
4. **Benchmark scorecard** — attempted, passed, repeat-pass rate, regressions and evidence age.
5. **Gap queue** — failed or weak capabilities ranked by expected benchmark improvement per runner-minute.
6. **Training queue** — current curriculum and next-best action.
7. **Sandbox** — isolated practice before official benchmark scoring.
8. **Resource lab** — authorized books, documentation, open resources, videos and datasets relevant to current gaps.
9. **Runtime panel** — active jobs, queued work, cached work, artifacts and useful/idle capacity.
10. **Mastery evidence** — reproducible passing evidence; no mastery claim from activity alone.

## Training buttons

Each dashboard should expose these controls and wire them to real workflows:

- **TRAIN NOW** — execute the highest-value training item for this MasterBot.
- **CLOSE GAPS** — build a targeted remediation queue from current benchmark failures.
- **RUN SANDBOX** — practice without changing official mastery status.
- **RUN BENCHMARKS** — execute the division's eligible benchmark suite.
- **RETEST FAILURES** — concentrate on previously failed tasks after remediation.
- **STUDY RESOURCES** — select authorized learning resources tied to active gaps.
- **EVOLVE STRATEGIES** — compare sub-bot/strategy variants and preserve measurable winners.
- **MASTER DOMAIN** — run the full learn -> practice -> benchmark -> diagnose -> retest loop.

If backend wiring is unavailable, the UI must show that state instead of pretending a job ran.

## 24/7 benchmark scheduler

The global scheduler should optimize **useful benchmark-gap closure per available runner-minute**, not raw job count.

Priority inputs:

- benchmark failure severity;
- expected score improvement;
- historical success probability;
- estimated runtime;
- dependency readiness;
- regression risk;
- resource freshness;
- duplicate-work penalty.

Use legitimate GitHub Actions capacity efficiently through:

- matrix parallelism for independent tasks;
- benchmark sharding;
- dependency and dataset caching;
- artifact reuse;
- change-aware execution;
- deduplicated experiment keys;
- priority queues;
- bounded retries and backoff;
- result reuse when inputs and code are unchanged.

Never attempt to bypass GitHub quotas or create meaningless jobs merely to increase run counts.

## 65 MasterBots

The exact names, IDs and mission statements are maintained in `config/masterbot-65-registry.json` so the Actions page, bot placement audit, benchmark engine and reports share one source of truth.

## Evidence standard

A benchmark is **mastered** only when the system has repeatable passing evidence under the configured evaluation policy. A site/resource is **mastered** only when the relevant tasks are successfully demonstrated and the evidence is recorded. Bot counts must distinguish verified inventory from user-reported or pending sources.
