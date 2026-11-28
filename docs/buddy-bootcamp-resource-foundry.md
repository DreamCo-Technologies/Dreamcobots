# Buddy Bootcamp 100-resource Foundry

## What this adds

- `config/buddy-bootcamp-100-resource-manifest.json`: 100 catalog entries grouped into ten foundry layers, mapped to the canonical DreamCo 65-MasterBot registry and five delivery stages.
- `tools/generate_buddy_bootcamp_challenges.py`: deterministic challenge-spec generator that accepts staged O*NET-like task records and emits original DreamCo challenge framing, a JSON Schema contract, pytest grading assertions, and provenance metadata.
- Each resource record includes official upstream reference links where a specific project or specification is identifiable. Reference links help discovery; they do not grant license, training, redistribution, or commercial rights. Resource 89 deliberately requires choosing and reviewing a specific MCTS/tree-search implementation before adoption.

## Canonical division count

DreamCo's current curriculum model distinguishes 55 business/domain divisions from 65 MasterBot learning lanes. The manifest keeps these registries separate: resource-to-domain mapping uses the 55 division curriculum list, while cross-cutting execution references the 65 MasterBot lanes. This avoids treating shared platform services as additional business divisions.

## Resource and ownership policy

The manifest preserves the resource/license descriptions from the proposal where appropriate but marks every entry `REVIEW_REQUIRED_BEFORE_USE`. Several proposed labels are not safe to treat as blanket permissions: products have different editions, packages have dependencies, hosted services have separate terms, benchmark datasets have separate rights, and some tools have non-permissive or source-available components. A permissive software license does not grant exclusive ownership of that software or all outputs created with it.

DreamCo can own original lesson prose, challenge framing, tests, rubrics, integration code, and independently authored synthetic examples to the extent the relevant contributors and dependencies grant those rights. Upstream task descriptions, documentation, trademarks, model weights, and datasets remain governed by their own terms.

## Generate challenges

First stage a JSONL file containing only task records whose source rights have been reviewed. Each row must include:

- `task_id`
- `task_statement`
- `occupation_code`
- `occupation_title`
- optional `source_url`

Create a source-specific rights manifest:

```json
{
  "source_id": "onet-release-reviewed-2026",
  "license_id": "exact-source-license-or-terms-reference",
  "commercial_use_approved": true,
  "training_use_approved": true,
  "evaluation_only": false,
  "privacy_review_status": "APPROVED",
  "review_status": "APPROVED",
  "reviewer": "authorized-reviewer",
  "reviewed_at": "2026-11-27T00:00:00Z",
  "evidence_uri": "internal-rights-review-record"
}
```

The values above are a schema example, not a claim that any specific O*NET release has been approved. Do not fabricate approval. Use the exact release and terms after review.

```bash
python tools/generate_buddy_bootcamp_challenges.py \
  --input-jsonl staged/onet-approved-tasks.jsonl \
  --rights-manifest staged/onet-rights-approval.json \
  --source-id onet-release-reviewed-2026 \
  --source-license-id exact-source-license-or-terms-reference \
  --division-id 41 \
  --output-jsonl build/dreamcodelab-challenges.jsonl \
  --max-tasks 100
```

The generator fails closed unless commercial and training rights, privacy review, source identity, reviewer, date, and evidence reference are explicitly approved. It never accepts evaluation-only data. It does not download O*NET, scrape websites, start model training, or create blind holdouts.

## Verification boundaries

The generated JSON Schema and pytest contract are public grading interfaces, not secret benchmark answer keys. A real Mastery gate still requires a separately authored private holdout, deterministic tests, measured checkpoint, regression review, safety review, and human release approval. Never route private holdouts into training or distillation.
