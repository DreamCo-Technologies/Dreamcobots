# Continuous learning schedule: execution truth

The DreamCo Continuous Learning Fleet workflow is scheduled on two cadences:
- Every five minutes: one fair-share MasterBot lane is selected by round-robin.
- Every six hours: the full 65-division fleet is preflighted.

The five-minute rotating lane and six-hour full-sweep workflows use separate concurrency groups. A long full sweep therefore cannot occupy the rotating-lane concurrency group. The five-minute planner has a four-minute lane timeout.

## What a successful scheduled run proves

A successful planner run proves that GitHub Actions checked out the repository, selected a canonical MasterBot lane, generated a plan-only run record, and uploaded that record as an artifact. The artifact is named latest-plan.json and explicitly declares:
- status = PLAN_ONLY_NOT_EXECUTED
- artifact_kind = PLAN_ONLY_NOT_A_MODEL_CHECKPOINT
- weights_trained = false
- mastery_claim = not_claimed_without_evidence

The six-hour matrix workflow uses the same plan-only worker. Its job labels and artifacts now say "Prepare plan" rather than "Train" or "checkpoint." The aggregator reads both the new latest-plan.json records and older latest-checkpoint.json records for historical compatibility.

## What it does not prove

A green GitHub Actions run does not prove that a model was trained, that weights changed, or that a model endpoint is serving. The planner does not download datasets or model weights, does not consume GPU compute, and does not call a paid provider.

Actual training requires a separate approved training-job manifest, rights-cleared persistent data, pinned base model and tokenizer, a compute approval, an available runner, checkpoint hashing, and post-training benchmarks. The dedicated Transformers runner and division release gate provide those separate contracts. Until the infrastructure is connected, the scheduled workflow remains a readiness/planning cycle rather than a weight-training loop.
