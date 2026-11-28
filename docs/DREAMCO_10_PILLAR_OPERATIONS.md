# DreamCo 10-Pillar Operations Guide

## Operating boundary

This repository implements evidence capture, deterministic planning, validation, and offline evaluation utilities. GitHub Actions on the free tier can run these CPU-only checks within the account's current quota. GitHub Actions is not a free GPU-training service. These workflows do not buy hosted inference, download 500 models, train model weights, or make provider calls.

The 500-model inventory is intentionally empty until each model has an immutable revision, model card, access approval, license review, evaluation permission, benchmark suite, and review record. A 10-shard plan is not a benchmark run.

## Pillar map

| Pillar | Implemented entry point | Evidence boundary |
| --- | --- | --- |
| 1. Evidence-first foundation | `tools/dreamco_benchmark_v2_engine.py` | SHA-256 provenance receipts; fail-closed runner result validation |
| 2. Failure-first repair | `append_failure_replay` and `self_debug_with_reviewed_patch` | Failed practice evidence only; reviewed patch proposal and new regression-test hash required |
| 3. 500-model sharding | `tools/plan_500_model_shards.py` | Ten 50-slot readiness shards; no execution until 500 real records and separate compute approval |
| 4. Ratings and Pareto | `tools/leaderboard_math.py` | Glicko-2 requires head-to-head results; Pareto compares accuracy, latency, and parameter count |
| 5. Adaptive curriculum | `update_curriculum_state` | Practice-only updates; 95%+ raises difficulty 10% and doubles interval; below 70% lowers difficulty 10% and resets interval |
| 6. Bootcamp distillation | `distill_verified_repair` | Exactly 25 original rubric drills from human-reviewed, rights-approved, training-authorized, dataset-release-approved, PII-scrubbed, privacy-approved non-holdout repair evidence; MinHash compares lesson signatures |
| 7. Swarm evaluation | `evaluate_swarm_handoff` | Measures supplied route, schema, latency, and tool-selection evidence; it does not execute external tools |
| 8. PR regression | `build_regression_issue_draft` | Relative score drop greater than 0.5% creates a reviewable issue draft; no issue is opened automatically |
| 9. Buyer readiness | `audit_buyer_readiness` | HMAC-verified network-isolation receipt and quantization drift are required to reach human review; no compliance badge is issued |
| 10. Upgrade #101 | `propose_upgrade_101` | Repeated verified telemetry creates a draft hypothesis; no fabricated improvement percentage or automatic merge |

## Unified CLI

All input files are JSON objects. Outputs are written locally; the commands make no provider calls.

```bash
python tools/dreamco_10pillar_orchestrator.py plan-500 \
  --input config/verified-model-inventory.json \
  --output artifacts/500-model-shards/plan.json

python tools/dreamco_10pillar_orchestrator.py glicko2 \
  --input examples/glicko2-period.json \
  --output artifacts/leaderboard/glicko2.json

python tools/dreamco_10pillar_orchestrator.py curriculum \
  --input examples/curriculum-update.json \
  --output artifacts/curriculum/next-state.json
```

Other subcommands are `pareto`, `distill`, `swarm`, `regression`, `buyer-readiness`, and `upgrade-101`. The input contracts are enforced by the Python functions and their unit tests.

A distillation input must contain a single `evidence` object with a canonical SHA-256 over all evidence fields except `evidence_sha256`. It must explicitly set `status=VERIFIED_REPAIR`, `human_review_status=APPROVED`, `source_rights_approved=true`, `training_use_approved=true`, `dataset_release_approved=true`, `pii_scrubbed=true`, `privacy_review_status=APPROVED`, `holdout=false`, and `evidence_split=practice` or `curriculum`. Optional `existing_signatures` is the saved list of MinHash signatures for previously distilled lessons. The `distill` command writes one JSON object per line (JSONL), with the MinHash signature included for the next run.

For buyer-readiness, set `DREAMCO_ISOLATION_HMAC_KEY` and `DREAMCO_ISOLATION_HMAC_KEY_ID` from GitHub Actions secrets or a local secret manager. Never commit the key. The isolation receipt must be produced by a trusted runner that actually blocks network egress and records the kit hash; monkeypatching Python sockets is not an air-gap test.

## Commercial ownership and third-party inputs

DreamCo-authored lesson text, challenge framing, rubrics, orchestration code, and independently authored synthetic examples can be governed as DreamCo IP subject to contributor agreements and dependency licenses. A catalog entry or permissive license does not grant training rights to a dataset, redistribute upstream content, transfer ownership of third-party software, or grant exclusive rights to model weights. Record exact versions, upstream licenses, attribution, commercial-use terms, training permission, and privacy review before ingestion.

Public benchmark material and private holdouts must be separated. Holdout answers are never eligible for training, repair replay, distillation, or curriculum scheduling.

## What is not claimed

- No 500 models are currently declared as verified or evaluated by the empty inventory template.
- No 45M, 350M, or 1B model checkpoint is created by these CI jobs.
- A generated lesson or challenge specification is not a trained model or an awarded mastery credential.
- A passing offline test is not proof of production readiness, legal compliance, or an air-gapped security certification.
- PR regression drafts and Upgrade #101 proposals require human review and are never auto-merged.
