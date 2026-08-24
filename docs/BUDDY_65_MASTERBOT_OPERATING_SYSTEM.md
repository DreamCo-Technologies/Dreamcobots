# Buddy 65-MasterBot Operating System

## Purpose

This document defines the approved target architecture for Buddy's continuous benchmark-gap-closure system. It is the canonical design contract for implementation work in `DreamCo-Technologies/Dreamcobots`.

## Hierarchy

- **Buddy** — global orchestrator and cross-division intelligence layer.
- **65 Division MasterBots** — domain owners. The 65-division registry in the product/repository is the source of truth for names and ownership; this document does not invent replacement division names.
- **Sub-bots** — existing specialized bots and capability workers. This includes the original Bots App bots, Real Estate bots, Grok AGI bots, and useful bots discovered in connected DreamCo repositories.
- **Capabilities / tools / resources** — reusable skills, APIs, websites, datasets, documentation, models, workflows, and learning resources.

## Continuous Improvement Loop

Every MasterBot follows:

`Discover -> Learn -> Practice -> Sandbox -> Benchmark -> Diagnose -> Improve -> Retest -> Verify -> Promote`

A failed benchmark loops back to diagnosis and targeted training. A capability is not marked mastered merely because a resource was read or a run succeeded once. Mastery requires repeatable, recorded evidence.

## MasterBot Command Centers

Each of the 65 MasterBots gets an operational dashboard/command center with:

- mission and capability ownership
- sub-bot roster and health
- benchmark score and trend
- failed/weak benchmark gaps
- active training jobs
- sandbox experiments
- authorized learning/resource sources
- websites/tools and verification history
- regression alerts
- next-best action
- training controls
- sandbox controls
- benchmark controls
- gap-closure controls
- mastery evidence and history
- 24-hour utilization and outcome metrics

## Actions Page

The global Actions page is Buddy's operational cockpit. It should expose:

- global benchmark-gap summary
- 65 MasterBot cards
- per-division prospectuses
- `TRAIN NOW`
- `CLOSE GAPS`
- `RUN SANDBOX`
- `RUN BENCHMARKS`
- `RETEST FAILURES`
- `STUDY RESOURCES`
- `EVOLVE`
- `DEPLOY`
- `PAUSE`
- `EMERGENCY STOP`
- 24-hour learning report
- global next-best-action recommendation

Buttons must invoke real workflows/API actions; they must not be decorative UI state.

## Benchmark Gap Engine

The benchmark engine should continuously:

1. collect benchmark results;
2. group failures by underlying capability;
3. identify blockers and regressions;
4. estimate expected improvement per unit of available compute/time;
5. prioritize the highest-value work;
6. assign work to the best MasterBot/sub-bot workers;
7. run sandbox experiments before official promotion when appropriate;
8. retest and record evidence;
9. promote proven strategies;
10. preserve failed experiments as evidence so the same work is not needlessly repeated.

## 24-Hour Capacity Optimization

The scheduler should maximize **useful** work, not artificial utilization. It should use legitimate GitHub Actions capabilities such as:

- matrix jobs for independent tasks
- benchmark sharding
- dependency and dataset caching
- artifact reuse
- incremental/change-based execution
- queue prioritization
- scheduled jobs
- checkpointing and resumable work
- deduplication of equivalent experiments
- regression-focused retesting

The system must remain within GitHub's actual service limits and must not attempt to evade quotas or abuse public runners.

## Capability Registry

Each bot/capability record should contain at least:

- stable ID
- primary MasterBot owner
- optional secondary capability tags
- source repository/path
- description
- tools/APIs
- dependencies
- benchmark targets
- current score
- best score
- repeat-pass rate
- evidence references
- training resources
- status: discovered / training / sandbox / tested / verified / mastered / blocked / deprecated
- last evaluated timestamp

## Bot Consolidation Policy

Do not delete useful bots merely because they are numerous. First extract their unique capabilities and benchmark evidence. Equivalent specialists may later be consolidated into stronger sub-bots/superbots when testing shows that consolidation preserves or improves performance.

The additional Bots App and Real Estate bot inventory must be reconciled into the registry rather than being silently excluded. User-reported counts are tracked separately from verified repository counts until inspected and evidenced.

Grok AGI bots remain preserved as experimental/model-specific specialists. Their strategies can be benchmarked and promoted when they demonstrate measurable value.

## Resource Learning Policy

MasterBots may use authorized resources such as official documentation, open-access research, public-domain/openly licensed books, free educational materials, public datasets, permitted videos, and other sources the system is authorized to access. Copyrighted media must not be scraped or copied without authorization.

Resource consumption is not itself mastery. The system must connect learning to practice and benchmark evidence.

## Measurement

The global scoreboard should distinguish:

- benchmarks attempted
- benchmarks passed
- repeatedly passed benchmarks
- benchmark regressions
- capability gaps open/closed
- verified mastered capabilities
- resources studied
- websites/tools verified
- sandbox experiments
- useful runtime utilization
- idle capacity
- duplicate work avoided
- benchmark improvement per hour/run
- current highest-value gap
- current blocked work

No benchmark, website, bot, or mastery count should be presented as verified unless supported by repository/test telemetry or other recorded evidence.

## Production Safety

All large integrations should be performed through feature branches and pull requests. Do not overwrite `main` or destroy source repositories while consolidating capabilities. Preserve provenance so every promoted capability can be traced to its source and evaluation evidence.

## Implementation Order

1. Reconcile the actual 65-division registry.
2. Build the canonical bot/capability registry.
3. Map existing bots and connected repositories into MasterBot ownership.
4. Implement the benchmark-gap engine and evidence model.
5. Implement the 24-hour capacity-aware scheduler.
6. Build the Actions page and 65 MasterBot command centers.
7. Connect functional training/sandbox/benchmark controls.
8. Add telemetry, regression detection, and mastery reports.
9. Optimize GitHub Actions throughput within service limits.
10. Verify the full system end-to-end before promoting changes to `main`.
