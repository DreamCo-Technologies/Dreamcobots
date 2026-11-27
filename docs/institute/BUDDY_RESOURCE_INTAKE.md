# Buddy Multi-Division Resource Intake

## Status

The first implementation is an offline-first, rights-aware intake and quarantine stage. It discovers the 55 academic divisions from the canonical Institute catalog and accepts explicitly declared local Markdown or pre-cached JSONL sources. It does not fetch public datasets, make network calls, train models, or modify checkpoints.

## Why this is intentionally different from a blind 80/10/10 harvester

A resource must not be rewritten and relabeled as DreamCo-original to bypass its source license. Every source needs an explicit rights status, evidence reference, and training approval. A SHA-256 digest establishes byte identity only; it does not establish authorship, ownership, or permission.

The harvester writes only to `resource_staging/<division>/quarantine.jsonl`. It does not write `train.jsonl`, `dev_suite.jsonl`, `holdout_suite.jsonl`, or `holdout_seal.json`. Candidate material must be reviewed and promoted through a separate governed workflow. Private holdouts must be independently authored or independently rights-cleared, sealed before use, and never generated from the same intake batch as training material.

## Source manifest

Edit `config/buddy-resource-sources.json` and add one source object per approved source:

```json
{
  "division_id": "dreamcyber",
  "source_type": "local_markdown",
  "path": "docs/security/SECURITY_CONTRACTS.md",
  "expected_sha256": "64-character-sha256",
  "rights_status": "DREAMCO_ORIGINAL",
  "license_id": "DREAMCO-INTERNAL",
  "evidence_reference": "PR-or-review-record",
  "approved_for_training": true,
  "approved_for_evaluation": false
}
```

Supported source types are `local_markdown` and `cached_jsonl`. Cached JSONL records must contain string `prompt` and `completion` fields. Public datasets are not automatically approved because they are hosted on a public model/data hub; first review the exact dataset revision, license, terms, and permitted uses, then store an approved local snapshot and evidence reference.

## Run

```bash
python scripts/buddy_resource_harvester.py --dry-run
python scripts/buddy_resource_harvester.py
```

The run report records source counts, staged counts, and rejected sources. Any source with missing rights evidence, a hash mismatch, an unknown division, unsafe credential-like content, or invalid records is rejected or blocks intake. The report never represents staged candidates as trained, benchmark-ready, or holdout-safe.

## Training and five-minute loops

Do not invoke this script as an unconditional pre-training step in a five-minute workflow. A frequent loop may inspect source queues, report changes, and select review tasks, but it must not silently ingest new rights, promote records, modify holdouts, or spend compute. Training starts only after a separate approval step consumes reviewed records and records a reproducible training run manifest.

## Graduation and benchmark gate

Use the Institute Competitive Model Laboratory's release-candidate manifest, exact checkpoint/tokenizer hashes, rights-reviewed baseline registry, and development/private-holdout fixture contract. The current benchmark runner requires both development and private-holdout fixtures and blocks when the baseline registry is empty. Do not replace those checks with a simple step count, a substring keyword score, or a claimed finite loss value. A genuine training evidence record should bind the exact checkpoint hash, tokenizer hash, dataset manifest hash, run ID, optimizer/training configuration, completed steps, and finite loss history. The independent evaluator must verify those bindings before a public claim is permitted.
