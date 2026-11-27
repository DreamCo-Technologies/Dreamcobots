# DreamCo private holdout benchmark lane

## Why this is separate
Training and validation data cannot establish independent generalization. Each division needs an evaluation-only holdout with explicit evaluation rights, separate storage lineage, and a test-only task manifest. The holdout is not training-approved and the training job factory continues to reject it.

## Register a holdout
Call DatasetHub.register_evaluation_holdout(card, staged_jsonl). The card must state:
- data_plane=evaluation_only_holdout, holdout=true, training_approved=false
- evaluation_approved=true, rights_status=VERIFIED, rights evidence and passed privacy review
- canonical primary MasterBot owner and HTTPS source/license references

Every JSONL row must be test-only, assigned to that MasterBot, and contain a task ID, prompt, expected answer, and supported metric. The hub content-addresses the file, records the holdout separately, and hashes the canonical test split.

## Create and run
Use create_private_holdout_job with one baseline, at least one trained candidate, immutable model revisions, model license evidence, and a compute approval ID. The runner rechecks the card, object, owner, split hash, candidate licenses, and approval before model loading. Downloading weights additionally requires DREAMCO_ALLOW_MODEL_DOWNLOAD=1.

The first evaluator reports deterministic exact-match, token-F1, latency p95, throughput, and peak CUDA memory where available. It stores aggregate metrics and task IDs only—not prompts, reference answers, or generated outputs. It does not yet evaluate safety, broad capability, calibration, multilingual performance, or production cost.

## Evidence and limitations
- The holdout is excluded from training by a separate data plane and explicit training_approved=false status.
- This phase supports staged local JSONL files only. Private cloud object storage, encryption, row-level access controls, backup/restore and retention evidence remain required before production certification.
- The PII pattern scan is heuristic and does not replace expert privacy review.
- A mocked/unit test is contract evidence, not proof that a real model was evaluated.
- Passing this domain evaluator is only one benchmark input to the separate release gate; it cannot promote or deploy a model.
