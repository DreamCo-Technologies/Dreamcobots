# Production readiness area evidence ledger

The production-readiness contract defines 19 product areas. The gate must not infer an area's state from the existence of source files, docs, tests, or workflow YAML.

Each area may be marked `VERIFIED` only when its evidence ledger entry contains:
- Existing repository artifact paths
- The exact current Git commit SHA
- A GitHub Actions workflow-run or check-run ID
- A linked run/check that completed successfully on that same SHA

A missing entry is `unknown`. An incomplete or stale entry is `partial`. Only a fully verified evidence record can produce `verified`.

The workflow uses a read-only GitHub token with Actions read permission. It does not deploy, write to the repository, or change production configuration.

The initial ledger is intentionally empty. Therefore the strict production certification must remain blocked until real implementation, test, runtime, security, deployment, observability, backup/restore, and rollback evidence is collected for every required area. A successful inventory workflow is not a production certification.
