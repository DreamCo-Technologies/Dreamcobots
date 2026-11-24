# DreamCo division model release evidence gate

The release gate is the final evidence join across infrastructure, data, training, benchmarks, and runtime. It is fail-closed and does not deploy or promote weights.

## Required evidence bundle

Every candidate division release identifies the canonical MasterBot ID, stable model ID/version, and tested Git commit SHA. It references eight JSON evidence artifacts by relative path and SHA-256:

1. **PostgreSQL** — read-only probe verifies all 65 namespaces, with no missing schemas.
2. **Dataset catalog** — the division's versioned manifest is persisted in its own `dreamco_division_NNN` namespace.
3. **Object storage** — live health, encryption at rest, object versioning, tested backup/restore, and retention policy.
4. **Model provider** — live inference smoke test, provider/model IDs, and request ID.
5. **Dataset card** — explicit training approval, verified rights, division ownership, non-holdout training plane, and pinned train/validation/test hashes.
6. **Training result** — completed run, immutable base-model and tokenizer revisions, matching dataset/splits, checkpoint manifest hash, file hashes, and tested commit.
7. **Benchmark report** — domain benchmark, general regression, private holdout, and safety all pass on the exact checkpoint; private test data must not be used for training; latency, throughput, memory, and cost measurements are required.
8. **Runtime deployment** — healthy HTTPS endpoint, matching model/checkpoint/commit, smoke test, deployment revision, and rollback target.

A separate independent reviewer ID and approval reference are mandatory.

## Checkpoint packaging

Copy checkpoint files into a controlled evidence package under the evidence root. Set `checkpoint_root` in the bundle to that relative directory. The gate recomputes each checkpoint file's size and SHA-256 and verifies the aggregate manifest digest emitted by the training runner.

## Result semantics

- `BLOCKED`: an artifact is missing, altered, incomplete, or fails its required check.
- `READY_FOR_INDEPENDENT_REVIEW`: all evidence references and gates verify; an independent reviewer still decides whether to release.
- The tool never changes serving traffic, promotes a model, or modifies weights.

Object storage and provider health are hard gates. A local filesystem path, documented provider, or mocked test does not count as production infrastructure evidence.
