# Buddy Continuous Learning and Expansion

## Permanent operating objective

Buddy's learning program is continuous. The 14-day plan is the first delivery sprint and graduation checkpoint, not the end of learning. After graduation, the same governed cycle repeats indefinitely while the repository's scheduler/worker is enabled and healthy.

## Continuous cycle

1. Inventory the canonical MasterBot registry and capability map.
2. Keep a dedicated logical learning lane and run history for each MasterBot.
3. Rank capability gaps by impact, evidence confidence, and estimated cost.
4. Select only approved sources; retain URLs, publication metadata, licenses and provenance.
5. Create a lesson, practice tasks, and sandbox fixtures.
6. Run isolated tests and held-out transfer tasks.
7. Run safety, regression, and reproducibility checks.
8. Save run manifest, metrics, logs and artifact/checkpoint hashes.
9. Promote only if the candidate improves the pinned benchmark without unacceptable regression; otherwise roll back and create a remediation lesson.
10. Publish a daily missing-capabilities report and weekly benchmark/model-card review.
11. Start the next cycle; do not stop because a curriculum has been completed.

## Growth dimensions

- Knowledge: versioned, rights-cleared retrieval and lesson memory.
- Skills: tested tool use, coding, reasoning and specialist capabilities.
- Models: optional adapter or weight training only after license, data, compute, safety and approval gates pass.
- Ecosystem: new MasterBots, tools, providers and routes only after registry, permissions, contract tests and rollback support exist.

## Dedicated MasterBot lanes

Each MasterBot receives an independent queue, lesson history, benchmark profile, run manifest and remediation backlog. Shared services include source governance, dataset-rights checks, benchmark definitions, artifact registry and audit logs. Shared failures must not silently corrupt every lane. Parallel jobs are bounded by available runners and approved resource budgets.

## Always-on does not mean uncontrolled

The learning program remains active. Individual jobs may pause for resource exhaustion, provider outage, security alerts, rights uncertainty, benchmark regression or human approval. Unknown data rights block training. Private mail, customer records, credentials and production secrets are denied as training inputs by default. No proprietary GPT-5 weights are assumed or copied. No production model weights or paid compute are authorized by this policy.

## Scheduling and deployment

The proposed GitHub Actions schedule is every six hours with a daily report and weekly benchmark review. A schedule only runs while GitHub Actions is enabled and its runner/quota is available. This policy and schedule do not themselves create a continuously running compute service. Actual model training requires a separately deployed worker, approved compute, datasets and monitoring.

## Required run evidence

Every run must record a unique run ID, MasterBot ID, source references, dataset manifest and rights status, configuration hash, seed, environment, tests, before/after benchmark scores, held-out transfer score, regression result, artifact hash and promotion/rollback decision.

## Operating status

POLICY_DEFINED_NOT_DEPLOYED until the scheduled workflow, persistent storage, runner health, model registry integration and end-to-end evidence are verified. Do not claim 24/7 model training from a cron schedule alone.
