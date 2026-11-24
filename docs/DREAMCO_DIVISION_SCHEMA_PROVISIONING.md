# DreamCo Division Schema Provisioning

## Purpose

Create one isolated PostgreSQL schema for each of the 65 MasterBot resource bundles. This is a guarded provisioning step, separate from the read-only connectivity probe.

## Owner-role contract

Each namespace `dreamco_division_NNN` must have a pre-created PostgreSQL group role with the same name. Every owner role must be `NOLOGIN` and not a superuser. The provisioning tool never creates roles, assigns passwords, or grants membership to the application role. Service identities and membership grants require a separate least-privilege review.

## Dry-run

Set `DREAMCO_POSTGRES_DSN` or `DATABASE_URL` in the protected execution environment, then run:

```bash
python -m buddy.datasets.provision_division_schemas
```

The default mode is read-only. It reports missing roles, unsafe roles, existing schemas, missing schemas, and schema-owner mismatches.

## Apply

After an operator reviews the dry-run evidence and provisions the 65 NOLOGIN owner roles through the approved identity-management process:

```bash
DREAMCO_ALLOW_DIVISION_SCHEMA_PROVISIONING=1 \
python -m buddy.datasets.provision_division_schemas \
  --apply \
  --approval-id APPROVAL-REFERENCE \
  --expected-resource-map-sha256 REVIEWED_MAP_SHA256
```

The expected SHA-256 pins the exact 65-division resource map reviewed for the operation. Apply runs in a single database transaction. It creates only missing schemas, sets each schema owner to its corresponding NOLOGIN division role, and revokes schema privileges from PUBLIC. Existing schemas with unexpected owners block the entire operation.

## Safety and completion semantics

- No DDL runs in default dry-run mode.
- Apply requires the CLI flag, non-empty approval reference, exact resource-map hash, and protected environment opt-in.
- All 65 owner roles must already exist and be NOLOGIN, non-superuser roles.
- No database roles, credentials, or application-role memberships are created.
- The tool does not create tables, apply application migrations, or certify production readiness.
- A successful result means the requested schemas were created or already existed with expected owners; runtime access and isolation tests remain separate gates.
