# DreamCo Bootcamp: seven-stage implementation

This implementation adds the missing runtime contracts around the existing source catalog, policy gate, canonical 65-MasterBot registry, existing O*NET materials, division curricula, and model foundry.

| Stage | Implementation | Truth boundary |
|---|---|---|
| 00 Catalog sync | Existing `stages/00_catalog_sync` | Metadata only; no media/transcript download |
| 01 Policy gate | Existing `stages/01_policy_gate` | Unknown or unverified rights fail closed |
| 02 Clean-room synthesis | `stages/02_clean_room_synth` | JSON contract + heuristic n-gram similarity; human rights review still required |
| 03 Learning engine | `stages/03_learning_engine` | SQLite evidence states; lab pass precedes teach-back |
| 04 Division matrix | `stages/04_division_matrix` | Reads canonical 65 registry; no inferred O*NET mappings |
| 05 Model foundry | `stages/05_model_foundry` | Stable SHA-256 holdout split and pinned recipe metadata |
| 07 Truth dashboard | `stages/07_dashboard` | Counts persisted evidence; never fabricates checkpoint/training claims |

## Existing assets reused
- `config/masterbot-65-registry.json` is the canonical 65-division identity source.
- Existing 55-division curriculum artifacts and O*NET subject/task indexes remain authoritative where their own status says verified.
- `buddy/learning/model_foundry.py` remains the rights-gated local trainer. This stage adds a deterministic task holdout/evaluation contract; it does not bypass explicit training authorization.
- Existing curriculum artifacts marked draft or owner-review-required are not promoted to approved.

## Completion gates still required
A source catalog is not permission. Every source item needs item-level rights evidence before restricted ingestion/training. Each division needs owner-reviewed curriculum and verified O*NET task mappings before readiness. A learner needs lab evidence and unseen teach-back. A model needs a licensed local dataset, explicit training authorization, checkpoint hashes, and held-out evaluation artifacts. The dashboard reports only evidence that exists.

## Local validation
```sh
python -m unittest discover -s tests -p 'test_bootcamp_completion_stages.py' -v
```
