# DreamCo division evidence and promotion gates

A division is not operationally ready because a model, dataset, workflow, or
provider appears in a registry. Registries describe intent. This gate checks
artifacts produced by real integrations.

## Required evidence domains per MasterBot

1. **Infrastructure** — database identity/connectivity, schema ownership,
   row-level security isolation tests, migration version, object-store
   write/read/checksum, backup/restore evidence, queue health and least-privilege
   identity.
2. **Dataset** — immutable dataset ID/version, source revision, license and
   rights review, consent/privacy review, content hash, quality report, split
   manifest hashes, contamination check and holdout isolation.
3. **Training** — base-model and tokenizer revision, model license, teacher
   identity/revision/terms, training code/config/seed, compute approval,
   dataset/split hashes, run logs, checkpoint hash and model card.
4. **Benchmark** — baseline and candidate revisions, same protected holdout,
   task/domain/safety/regression results, confidence intervals, latency/cost,
   reproducible run ID and artifact hashes.
5. **Runtime** — deployed endpoint identity, provider/model allowlist,
   endpoint health, auth and tenant-isolation checks, request/response
   redaction, latency/error/cost telemetry, rollback test and deployment ref.

## Evidence manifest

Each record is scoped to one canonical MasterBot ID and includes domain,
status, evidence ID, observation time, artifact path, artifact SHA-256 and
source reference. Artifact paths must stay under the operator-supplied
evidence root. Hashes are recomputed from bytes.

Use buddy.models.evidence_gate.verify_division_evidence to validate the five
required domains. Missing artifacts, failed checks, stale or mismatched hashes,
cross-division evidence, or missing source references block readiness.

## State machine

- requirements_defined_not_provisioned: architecture exists, no real resource evidence.
- configured: settings/identities exist, but connectivity is not proven.
- connected: live connectivity and identity checks pass.
- validated: integration, security, restore, and operational tests pass.
- READY_FOR_INDEPENDENT_REVIEW: all five evidence domains are hash-verified.
- certified: an independent reviewer signs the release decision.

The validator never returns certified, never updates model weights, and never
deploys a model. Production promotion requires separate human approval and a
rollback plan. A passing unit test with mocked services is test evidence only,
not live infrastructure or runtime evidence.

## Training and benchmark rules

- Keep each division's model identity, version, tokenizer policy, checkpoint
  lineage, training job, and benchmark suite separate.
- Shared base models are allowed; specialist adapters/checkpoints are owned by
  the division and pinned to exact base revisions.
- Buddy is the teacher coordinator, not a claim that teacher weights are
  trained or available. Teacher outputs require rights and provider permission.
- Evaluation-only holdouts never enter training or distillation.
- Training jobs record seed, hardware, resource use, split hashes and
  checkpoint hashes. Compare every candidate with its baseline on the same
  protected holdout.
- Route tasks only to providers/endpoints with validated lifecycle state,
  approved data classification, explicit model allowlists and budget approval.

## Current evidence truth

The PostgreSQL adapter and model-serving contract have mocked CI tests. They
do not prove a live PostgreSQL deployment, object-store integration, external
provider connectivity, model training, or production inference. Those statuses
remain blocked until the required artifacts exist.
