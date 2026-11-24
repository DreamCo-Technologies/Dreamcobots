# DreamCo PostgreSQL Division Probe

## Purpose

The PostgreSQL probe is the first runtime integration gate for the 65 MasterBot resource bundles. It checks a configured PostgreSQL service without creating schemas, applying migrations, or changing application data.

## Run

Set `DREAMCO_POSTGRES_DSN` in the execution environment (never commit it), then run:

```bash
python -m buddy.datasets.postgres_probe --output artifacts/database/postgres-probe.json
```

The optional `psycopg` dependency must be installed in the worker environment. The probe uses a five-second connection timeout, a five-second statement timeout, and a read-only transaction.

## Evidence statuses

- `BLOCKED`: no DSN is configured; no connection is attempted.
- `CONNECTED_SCHEMAS_VERIFIED`: connection and all 65 expected logical namespaces were verified.
- `CONNECTED_SCHEMA_INCOMPLETE`: connection succeeded, but one or more expected namespaces are absent.
- `ERROR`: the probe could not safely complete.

The evidence records a SHA-256 of the resource map, database identity, namespace counts, and missing namespaces. It never records the DSN or exception text that could contain credentials.

## Safety boundary

This probe does not create schemas or tables, execute migrations, grant privileges, or write application data. Namespace provisioning and migrations remain a separately reviewed change. A successful probe is not a production certification; it proves only connectivity and schema inventory at the recorded time.
