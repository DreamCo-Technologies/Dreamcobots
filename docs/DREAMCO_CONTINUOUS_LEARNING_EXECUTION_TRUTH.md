# Continuous learning schedule: execution truth

The Buddy Continuous Learning Fleet workflow has two scheduled planning cadences:

- Every five minutes: one canonical MasterBot division is selected using a round-robin lane.
- Every six hours: the full 65-division registry is prepared for a plan-only sweep.

The rotating five-minute lane and six-hour full sweep use separate concurrency groups so a full sweep does not occupy the rotating-lane group. The rotating lane has a bounded four-minute job timeout and the full matrix has bounded parallelism.

## What a successful scheduled run proves

A successful planner run proves that GitHub Actions checked out the repository, selected a canonical division, generated a plan-only record, and uploaded that record as an artifact. Each record declares:

- `status = PLAN_ONLY_NOT_EXECUTED`
- `artifact_kind = PLAN_ONLY_NOT_A_MODEL_CHECKPOINT`
- `weights_trained = false`
- `training_job_executed = false`
- `compute_consumed = false`
- `mastery_claim = not_claimed_without_evidence`

The artifact is named `latest-plan.json`. The six-hour matrix uses the same plan-only worker. The cross-run aggregator reads both new plan records and historical `latest-checkpoint.json` records for compatibility, but labels its output `AGGREGATED_RUN_EVIDENCE_NOT_MODEL_TRAINING`.

## What it does not prove

A green planner workflow does not prove that a model was trained, weights changed, a tokenizer was trained, a dataset was ingested, or a model endpoint is serving. The planner does not download datasets or model weights, does not consume GPU compute, and does not call a paid teacher/provider.

## Actual training gate

Actual model training remains a separate approved execution path. It requires all of the following:

1. A versioned training-job manifest tied to one division/model version.
2. Rights-cleared, provenance-verified, privacy-reviewed, immutable dataset manifests.
3. Pinned base-model and tokenizer revisions with verified usage rights.
4. An approved compute budget and an available isolated training runner.
5. Reproducible seeds/configuration, checkpoints and artifact hashes.
6. Post-training domain, general, safety, privacy, robustness, regression and resource benchmarks.
7. Human review before any release or production promotion.

The dedicated division training workflow is manual-dispatch and expects an appropriately configured self-hosted GPU runner. Until the required runner, secrets, persistent data services and approval records are actually available and exercised, the five-minute and six-hour workflows remain planning/readiness cycles—not continuous weight training. GitHub schedules are best-effort and do not guarantee 24/7 compute.
