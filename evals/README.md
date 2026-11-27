# DreamCo held-out evaluations

This directory is an evaluation-only plane. Its task suites and answer keys MUST NOT be copied into training, retrieval-for-training, distillation, synthetic-data generation, or curriculum-generation inputs. The checked-in starter suite is PUBLIC, so it is a smoke test, not a blind or independent certification holdout. Keep real certification tasks and answer keys in a private, access-controlled evaluation store.

## First flagship lane

- Lane: MasterBot 41, DreamCodeLab
- Public smoke suite: `evals/suites/dreamcodelab_execution_v1.json`
- Private certification suite: supplied at evaluation time from an access-controlled store; set `split` to `private_independent_holdout` and `training_use` to `NEVER_TRAIN`.
- Public smoke results cannot be used to sign or promote a checkpoint.
- Minimum passing accuracy: 0.85
- Evaluation inputs: one JSONL prediction per task, with `task_id` and `output`.
- The model adapter/inference runner is deliberately separate: export predictions from the candidate checkpoint, then pass them to the evaluator.

## Run

```bash
python tools/run_heldout_evaluation.py \
  --suite evals/suites/dreamcodelab_execution_v1.json \
  --predictions /path/to/predictions.jsonl \
  --output /path/to/evaluation-report.json \
  --model-version dreamcodelab-candidate-001
```

The evaluator is deterministic and offline. Missing, duplicate, or unknown predictions fail closed. Reports contain task-level outcomes and a SHA-256 hash of the suite. Public smoke suites can validate the harness only; the checkpoint signer rejects them and requires a private independent holdout report.

## Checkpoint evidence

After training is separately authorized and a checkpoint exists, validate it with:

```bash
export DREAMCO_CHECKPOINT_SIGNING_KEY='a-long-random-secret-from-your-secret-manager'
python tools/validate_checkpoint.py \
  --checkpoint /path/to/model.safetensors \
  --evaluation /path/to/evaluation-report.json \
  --training-config /path/to/training-config.json \
  --dataset-manifest /path/to/approved-dataset-manifest.json \
  --output /path/to/checkpoint_manifest.json \
  --expected-parameters 45000000
```

The validator requires an approved dataset manifest, a passing held-out report, reproducible training configuration, measured parameter count, finite validation perplexity, positive token throughput, measured RAM, and an HMAC-SHA256 signing key. It signs evidence; it does not train a model or certify a model's quality beyond the supplied measurements.

## Promotion policy

A lane is not `MASTERED` merely because a curriculum or blueprint exists. Promotion requires a trained checkpoint, verified artifact hash, signed evidence manifest, independent held-out pass, regression review, safety review, and human release approval. A single small starter suite is a proof-of-concept gate, not enterprise-grade certification.
