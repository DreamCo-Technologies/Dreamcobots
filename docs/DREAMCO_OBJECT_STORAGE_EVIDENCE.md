# DreamCo object storage health and recovery evidence

The S3-compatible adapter inspects two existing buckets and can optionally run a tiny generated-object canary. It does not create buckets, change bucket policies, provision IAM, upload training datasets, or connect to a live service during ordinary CI.

## Required environment

- `DREAMCO_OBJECT_STORE_BUCKET` — existing primary bucket
- `DREAMCO_OBJECT_STORE_BACKUP_BUCKET` — distinct existing backup bucket
- `DREAMCO_OBJECT_STORE_REGION` — optional region (defaults to `us-east-1`)
- `DREAMCO_OBJECT_STORE_ENDPOINT_URL` — optional trusted HTTPS S3-compatible endpoint; credentials in endpoint URLs are rejected
- `DREAMCO_OBJECT_STORE_HEALTHCHECK_PREFIX` — optional generated-object prefix (defaults to `dreamco/healthchecks`)
- `DREAMCO_ALLOW_OBJECT_STORE_CANARY=1` or an explicit `allow_canary=True` call — required before a live canary writes anything

The runtime identity should have only bucket-configuration read permissions and narrowly scoped put/get/head/copy access under the health-check prefix. Do not grant bucket creation, policy modification, account administration, or public access.

## Required checks

- Bucket versioning is enabled on both buckets.
- Server-side encryption is configured on both buckets.
- All four S3 public-access-block controls are enabled on both buckets.
- The backup bucket has a positive lifecycle retention period.
- A canary writes a small generated object to the primary bucket, reads it back, copies it to the backup bucket, reads the backup, restores it to a new primary key, and verifies the restored bytes and object encryption.

Per-division health checks place canary objects beneath a prefix such as `divisions/007`. Division IDs are validated against the canonical 1–65 range. Without explicit canary opt-in, the result is `CONFIGURED_NOT_VALIDATED` and `backup_restore_test` remains `NOT_RUN`. Missing security or retention controls produce `BLOCKED` without writes.

## What the evidence does not prove

- Fake-client CI tests validate adapter behavior, not live AWS/S3 connectivity.
- `CONFIGURED_NOT_VALIDATED` is not a healthy live bucket result.
- A successful cross-bucket canary is not a full disaster-recovery exercise and does not prove cross-account, cross-region, or point-in-time recovery.
- The adapter does not upload training datasets or write references to PostgreSQL. Dataset persistence requires the separate governed ingestion path, a rights/PII approval, division-scoped database catalog persistence, and an independently verified storage grant.

No bucket credentials, endpoints, or live-service claims are committed to this repository. A live canary remains blocked until the owner configures the approved secrets/variables and explicitly authorizes that operation.
