# DreamCo Proprietary Ownership and Rights Governance

## Policy intent

DreamCo's first-party platform, Buddy AI/OS, Bootcamp, original curriculum,
original lessons, divisions, applications, source code, inventions, datasets,
and model artifacts are intended to remain proprietary by default.

The repository-level LICENSE and NOTICE express that intent. They do not
transfer rights that DreamCo does not own, cure missing contributor
assignments, or override third-party licenses.

## Asset-level rights record

Every external or mixed-origin asset used in a product, dataset, lesson,
training run, or commercial deliverable must have a machine-readable record
containing:

- Stable asset ID and content hash.
- Owner/creator and source URL or acquisition record.
- Source type and retrieval date.
- Exact license name and SPDX identifier when available.
- Separate permissions for read/study, quote/reference, adapt, redistribute,
  commercial use, and model training.
- Attribution, notice, share-alike, and downstream obligations.
- Territory, term, audience, and other restrictions.
- Reviewer, review date, evidence location, and approval status.

## Fail-closed decision table

| Evidence | Study | Adapt | Redistribute | Commercial use | Model training |
|---|---:|---:|---:|---:|---:|
| Explicit permission for the exact use | Allow within scope | Allow within scope | Allow within scope | Allow within scope | Allow within scope |
| Read-only access or unclear terms | Hold | Block | Block | Block | Block |
| Non-commercial restriction | Evaluate only for permitted non-commercial study | Block unless expressly allowed | Block unless expressly allowed | Block | Block unless expressly allowed |
| No-derivatives restriction | Evaluate reading only | Block | Block unless permitted | Block unless permitted | Block unless expressly permitted |
| Training restriction | Evaluate reading only | Evaluate independently | Evaluate independently | Evaluate independently | Block |
| Unknown or conflicting license | Hold | Block | Block | Block | Block |

A permission in one column never implies permission in another.

## Model and dataset lineage

Each training dataset and model checkpoint must link to:
1. Source asset manifest and hashes.
2. Rights decision for the intended training and distribution use.
3. Transformations, filtering, and synthetic-generation lineage.
4. Dataset version, tokenizer version, training recipe, and code revision.
5. Evaluation results and holdout separation.
6. Checkpoint hash, parent checkpoint, adapter lineage, and promotion decision.

Do not mix unverified sources into a commercial training run. If source provenance
is incomplete, quarantine the affected records and rebuild the dataset.

## Contributor and employee IP

A repository notice is not a substitute for signed agreements. Before accepting
outside contributions or commissioning work, obtain the applicable written
assignment or license grant and confirm that it covers the intended use,
modification, commercialization, and sublicensing. Have qualified counsel
review the agreement and jurisdiction-specific requirements.

## Release gate

A release is blocked when any shipped first-party asset has an unresolved
ownership claim, any third-party asset lacks required notices, any training
record lacks source lineage, or any asset's rights do not cover the release's
actual distribution and commercial use.

A human rights reviewer must approve the final release manifest. Automated
checks provide evidence; they do not make legal determinations.
