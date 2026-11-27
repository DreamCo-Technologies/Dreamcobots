# DreamCo Dataset Studio and Data Marketplace

Status: product and engineering specification. This document does not claim that dataset ingestion, training, payments, licensing enforcement, or marketplace delivery are implemented.

## Product goal

Make datasets a first-class DreamCo product. Buddy should help people discover, understand, validate, prepare, document, license, buy, sell, and learn from datasets. Dataset products support DreamCo's first-party model factory and customer workflows without weakening ownership or privacy controls.

## Dataset rights classes

Every dataset version must have exactly one primary rights class, plus supporting evidence:

1. `owned`: DreamCo created or acquired the dataset with documented rights sufficient for the intended use and distribution.
2. `licensed_for_training`: third-party dataset with explicit training rights; redistribution is separately evaluated.
3. `licensed_for_redistribution`: distribution rights documented, with training rights recorded independently.
4. `public_restricted`: publicly accessible data whose license, terms, attribution, privacy, or use restrictions still apply.
5. `customer_private`: customer-controlled data. Private by default; no cross-tenant use, model training for other tenants, resale, or publication without separate explicit authorization.
6. `research_only`: approved for research/evaluation only; never silently promoted into commercial training or resale.
7. `blocked`: unresolved rights, privacy, provenance, safety, or policy issue. No ingestion into training or marketplace.

Public availability is not proof of public-domain status or commercial reuse rights. Dataset listing, download, training, redistribution, sublicensing, and derivative-work permissions are separate fields. Store the exact license text or immutable license reference, source URL, acquisition date, attribution, restrictions, and reviewer decision.

## Dataset lifecycle

1. Discover source and capture provenance.
2. Resolve license and permitted purposes.
3. Scan privacy, personal data, secrets, harmful content, malware, and sensitive attributes.
4. Inspect schema, format, encoding, language, size, duplicates, missingness, label quality, class balance, leakage, and contamination.
5. Create immutable version manifest and content hashes.
6. Split train/validation/test with leakage-resistant grouping and documented methodology.
7. Generate dataset card, datasheet, quality report, intended-use and out-of-scope-use notes.
8. Run human review for rights, privacy, safety, and quality.
9. Publish only approved catalog metadata; deliver files only under the approved entitlement and license.
10. Monitor reports, takedown requests, license changes, and dataset drift; suspend affected versions when necessary.

## Buddy capabilities

Buddy may:
- Search approved catalog metadata and explain license restrictions.
- Profile schema, data quality, duplication, imbalance, leakage, and likely suitability for a stated task.
- Recommend preprocessing and train/validation/test strategies.
- Generate dataset cards, lineage summaries, reproducible manifests, and evaluation plans.
- Help customers prepare datasets inside their isolated workspace.
- Compare datasets on documented attributes without inventing quality scores.
- Teach data curation, licensing, privacy, and dataset engineering in Buddy Bootcamp.

Buddy must not:
- Treat a web-accessible file as free to copy, train on, or sell.
- expose customer-private rows, files, labels, or derived artifacts to another tenant.
- infer or fabricate license grants, consent, provenance, or quality results.
- publish a dataset or start a paid delivery before rights and safety gates pass.
- train on restricted data merely because it appears in a prompt, connector, or public repository.

## Marketplace products

- Dataset listing: searchable metadata, dataset card, version, size, format, language, coverage, collection date, quality evidence, license, permitted purposes, restrictions, price, delivery method, and update policy.
- Licensing options: one-time license, subscription/update feed, enterprise/site license, or custom negotiated license. Availability depends on actual rights.
- Creator tools: upload/ingest, metadata editor, license evidence, validation report, versioning, pricing, sales analytics, dispute and takedown handling.
- Buyer tools: preview permitted samples, inspect cards and quality reports, compare versions, purchase entitlements, download or access through approved APIs.
- Training add-on: use a dataset in a customer-isolated training workspace only when the dataset license permits it and customer entitlements cover the use.
- Curated bundles: combine datasets only when each component's terms permit the bundle and all notices/attributions are preserved.

## Data and model separation

A dataset license does not automatically grant rights to the trained model weights, embeddings, labels, or derived dataset. Each training run records the exact dataset versions and rights snapshots used. Each model release receives its own provenance and license review. Customer data and customer-trained derivatives remain tenant-scoped unless a separate written opt-in grants a defined reuse right.

## Required dataset record

- Stable dataset ID and immutable version ID
- Owner/creator and verified distributor
- Source and acquisition method/date
- License identifier, license text/reference, attribution, restrictions
- Separate flags for viewing, downloading, training, commercial use, redistribution, sublicensing, derivatives, and resale
- Privacy/consent and sensitive-data assessment
- Content hashes, schema, format, size, language, time coverage
- Dataset card, datasheet, quality report, scan results
- Split strategy, leakage checks, deduplication method
- Reviewers, approvals, timestamps, and audit events
- Price, currency, entitlement, delivery policy, refund/takedown process where applicable

## Trust and release gates

A dataset cannot be listed, sold, delivered, or used for training until the relevant gate passes:
- Rights: chain of title/license and intended purpose verified.
- Privacy: lawful collection/use, consent where required, minimization, deletion and retention rules.
- Security: malware/file scanning, safe parsing, access controls, signed artifacts.
- Quality: reproducible profiling and documented limitations.
- Product: clear description, license, pricing, version, support and delivery terms.
- Human approval: required for ambiguous rights, sensitive data, high-impact uses, or exceptions.

Any rights or privacy uncertainty defaults to quarantine, not approval. Provide a documented takedown and incident response path.

## Commercial model

DreamCo may sell datasets it owns or is explicitly authorized to distribute. Creators may list their own datasets after verification and may set prices subject to platform terms. Revenue share, taxes, refunds, payouts, fraud checks, and payment compliance must be implemented before real transactions. Do not represent a mock catalog as a live store.

## Suggested service boundaries

- Catalog and metadata API
- Provenance and license registry
- Ingestion and quarantine service
- Quality profiling and dataset-card generator
- Tenant-isolated storage and entitlement delivery
- Training-run dataset resolver
- Marketplace listing, checkout, payouts, and audit service
- Takedown, deletion, and incident workflow

## Initial implementation sequence

1. Dataset manifest schema and rights taxonomy.
2. Read-only catalog and dataset-card generation.
3. Local/offline validation and quality profiling.
4. Training-run lineage integration.
5. Tenant-scoped storage and access controls.
6. Rights-reviewed listing workflow.
7. Payments, entitlements, and creator payouts only after compliance/security review.
8. Usage analytics, drift monitoring, and takedown automation.

## Success measures

Track catalog records with complete provenance, rights-review coverage, percentage of datasets with reproducible quality reports, ingestion-to-approval time, buyer task success, dataset defects/takedowns, unauthorized-access incidents, and training runs with complete dataset lineage. Do not optimize for dataset volume at the expense of rights or quality.
