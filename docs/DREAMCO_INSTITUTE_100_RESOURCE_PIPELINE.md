# DreamCo Institute — 100-Resource Clean-Room Reference Registry

This registry records the 100 requested external resources across ten domains. Listing is discovery metadata, not an assertion that a resource is free, open, licensed for commercial use, or authorized for model training.

## Admission policy

Every resource begins as NOT_ACQUIRED / UNVERIFIED / BLOCKED_PENDING_REVIEW. Before any snapshot or content is admitted, the pipeline must record its exact source/version, terms and license, permitted uses, acquisition method, SHA-256, provenance, privacy/PII review, and retention/deletion obligations. Missing or ambiguous rights fail closed.

Do not scrape around access controls, copy proprietary course content, redistribute datasets, or train on source code/data merely because it is publicly reachable. Keep third-party notices and attribution where required. If training rights are not established, the resource may be usable only for permitted metadata or high-level conceptual reference; this is a legal review decision, not an automatic exemption.

## Quarantine stages

1. Discover source and canonical owner.
2. Review current license, terms, access controls and commercial/training permissions.
3. Acquire only an authorized snapshot.
4. Record immutable URL/version/date/hash and provenance.
5. Scan files and parse in an isolated environment.
6. Review privacy, PII, secrets, malware and sensitive content.
7. Extract abstract task taxonomies, engineering patterns and assessment structures only where permitted.
8. Independently author DreamCo lessons, schemas, code and synthetic examples.
9. Run similarity/originality review and independent holdout tests.
10. Approve, reject, or retain in reference-only status with an audit record.

## Registry

The machine-readable source of truth is `config/dreamco_institute_resource_registry.json`. It contains exactly 100 entries in ten categories. Each entry starts blocked until its individual review evidence is complete.

## No false claims

A source registry is not a dataset. A curriculum map is not a trained model. An architecture configuration is not a verified parameter count. A benchmark is not valid until an identified model artifact is run and the results are reproducible. Graduation requires evidence, not a checklist declaration.
