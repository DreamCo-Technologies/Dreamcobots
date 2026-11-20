# Buddy Always-On, All-Division Learning

## Fleet scope

The canonical source of truth is `config/masterbot-65-registry.json`. Every scheduled fleet cycle builds its matrix from that registry and requires exactly 65 unique division records. No hand-maintained partial list is allowed. Each division gets an isolated run record and a fair-share place in the queue.

## Cadence

GitHub Actions is configured to start a fleet cycle every six hours, 24 hours a day, seven days a week. Each cycle fans out to all 65 division lanes, with parallelism capped at five jobs to respect runner capacity and avoid overwhelming the repository. This is four scheduled lane invocations per division per day when GitHub Actions is enabled and not delayed or quota-limited. Manual runs are also supported.

GitHub scheduled workflows are best-effort, not a guaranteed clock or persistent compute service. The schedule can be delayed, disabled, skipped by platform limits, or stopped by repository settings. For stronger 24/7 execution, DreamCo must deploy and monitor a persistent queue/worker with approved compute and budget.

## Each division's learning loop

1. Load its own gap queue, last checkpoint and benchmark profile.
2. Read eligible shared lessons and reusable verified fixes from other DreamCo runs.
3. Select a prioritized gap and approved learning sources.
4. Study, practice and run isolated sandbox tasks.
5. Run targeted, held-out, safety and regression checks.
6. Store evidence, source lineage, config and artifact hashes.
7. Publish only reusable, verified lesson metadata and benchmark learnings to the shared cross-run bus.
8. Requeue unresolved work and start again in the next cycle.

## Mixing learning across runs

All divisions participate in a shared learning bus. Approved lesson metadata, capability-gap patterns, benchmark deltas, reusable test fixtures and verified fixes can be shared across divisions and other DreamCo runs. Every item retains source run, division, version and evidence references.

This is not blind pooling. Raw datasets, credentials, private mail, customer records and model weights are not copied between lanes by default. Each consumer lane rechecks provenance, license, consent, data isolation and compatibility. Weight sharing or production updates require their own explicit approval and evaluation gates.

## What the current workflow actually executes

The existing `tools/buddy_masterbot_training_lane.py` creates a sandbox-first checkpoint and next-action record for each MasterBot. The fleet workflow runs that coordinator and aggregates the 65 run records into a cross-division learning queue. This is orchestration and evidence generation; it is not yet a model-training engine, optimizer loop, persistent worker, or proof that model weights changed.

To claim actual continuous model training, each lane still needs a connected training executor, approved datasets and compute, durable checkpoint storage, benchmark adapters, monitoring, and tested promotion/rollback. Until those are deployed, status remains `POLICY_DEFINED_NOT_DEPLOYED`.

## Safety and quality gates

- Unknown data rights or missing provenance block use.
- Private mail, customer data, credentials and production secrets are denied by default.
- Proprietary GPT-5 weights are not assumed available or permitted.
- Paid compute and production weight updates require separate explicit approval.
- A benchmark regression prevents promotion; preserve the last known-good checkpoint.
- Resource, security or provider-health alerts pause affected work and require a health check before resuming.

## Evidence

Each lane records its MasterBot ID, run ID/attempt, timestamp, lifecycle, source references, next actions and non-mastery status. The fleet aggregation records which divisions reported and which were missing. Do not call a division trained, mastered or healthy merely because its scheduled job produced a checkpoint.
