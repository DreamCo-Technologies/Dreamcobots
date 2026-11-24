# DreamCo object storage evidence

The object storage adapter supports AWS S3 and S3-compatible HTTPS endpoints through the standard boto3 credential chain. It does not create buckets, change bucket policies, or write user datasets during health checks.

## Required environment
- DREAMCO_OBJECT_STORE_BUCKET — primary training/evidence bucket
- DREAMCO_OBJECT_STORE_BACKUP_BUCKET — distinct backup bucket
- DREAMCO_OBJECT_STORE_REGION — region (defaults to us-east-1)
- DREAMCO_OBJECT_STORE_ENDPOINT_URL — optional HTTPS S3-compatible endpoint
- DREAMCO_OBJECT_STORE_HEALTHCHECK_PREFIX — optional prefix (defaults to dreamco/healthchecks)
- DREAMCO_ALLOW_OBJECT_STORE_CANARY=1 — explicit opt-in for a live canary

The runtime identity needs bucket configuration read access plus narrowly scoped put/get/head/copy permissions under the health-check prefix in both buckets. Do not grant public access or account-wide administrative permissions.

## Evidence checks
- Versioning must be enabled on both buckets.
- Server-side encryption must be configured on both buckets.
- All four S3 public-access-block controls must be true on both buckets.
- The backup bucket must have a lifecycle retention period.
- The opt-in canary writes a tiny generated object to the primary bucket, reads it back, copies it to the separate backup bucket, reads the backup, restores it to a new primary key, and verifies the restored bytes.

Use run_division_object_store_healthcheck(masterbot_id, ...) to place canaries under a per-division prefix such as divisions/007. IDs are validated against the canonical 1–65 range. The result emits the evidence fields consumed by the division release gate. Missing bucket configuration returns BLOCKED. Without explicit canary opt-in, the result is CONFIGURED_NOT_VALIDATED and backup_restore_test remains NOT_RUN.

## Limitations
- A cross-bucket canary restore is not a full disaster-recovery exercise and does not prove cross-account or cross-region resilience.
- This adapter does not provision buckets, configure IAM, set encryption policies, or install lifecycle rules.
- A live successful result is required before a division can pass the object-storage release gate.
- The health-check prefix should be covered by lifecycle retention so generated canary objects expire under the approved retention policy.

## Per-division dataset uploads

Use upload_division_dataset(masterbot_id, dataset_id, dataset_version, source_file, content_sha256, upload_approval_id). It requires DREAMCO_ALLOW_DATASET_OBJECT_UPLOAD=1, a verified source SHA-256, and an approval reference. Objects are written under divisions/NNN/datasets/DATASET_ID/vVERSION/HASH.jsonl, with version ID, object metadata, encryption, size, and readback hash verified before returning PERSISTED evidence. It never writes into another division's prefix. This adapter currently uploads the object; the separate ingestion orchestrator must still persist the returned object reference into the per-division PostgreSQL catalog before the dataset can be considered production-persistent.
