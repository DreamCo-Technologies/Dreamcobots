# Buddy Dataset Profile Builder

## User outcome
A user defines a goal, target model, learning methods, permitted sources, category/source weights, privacy boundaries, compute limits and evaluation requirements. The exported profile is portable and can later be imported into the authenticated Buddy Training Studio.

## Actual learning, not URL tracking
A source contributes to learning only after the permitted content has been ingested into an authorized content store. The pipeline must extract concepts, create original lessons/examples/labs, deduplicate and quality-filter content, create train/validation/holdout splits, index reusable knowledge, generate training examples and evaluate. Metadata-only sources remain discovery records and never count as learned content.

## Profile controls
- Target model and immutable base-model revision
- Retrieval, skill packs, prompt/policy, SFT, LoRA, QLoRA, preference optimization, distillation and continued-pretraining methods
- Per-category source mix, normalized to 100%
- Per-source overrides (future UI/API extension)
- Rights/provenance, privacy and tenant isolation
- Quality thresholds, deduplication and held-out data
- Compute, runtime, example and GPU-hour limits
- Baseline, transfer, holdout and regression requirements

## Weight meaning
Dataset mix weights control the relative sampling share of eligible examples by source category. They are not model parameter weights. LoRA/QLoRA training changes adapter parameters; full fine-tuning changes model parameters. Every actual parameter change requires a worker receipt, immutable checkpoint hash and before/after evaluation. Do not call source weighting a trained model.

## Five-minute learning cadence
A scheduler tick should detect changed sources, ingest newly approved content, build or refresh Bootcamp assets, prioritize the highest expected learning gain per compute cost, run at most one bounded mutating job per profile, evaluate due jobs and persist evidence. Idle cycles should do cheap queue/freshness checks and exit; do not burn GPU time just to satisfy a clock. A connected worker, secure content store and scheduler are prerequisites.

## Safety
Unknown/restricted rights block training. Public reachability is not permission. Personal data defaults to excluded/redacted. Secrets and credentials must never enter training. Tenant data must not cross user boundaries. Holdout data is never used for training. External provider upload defaults off. Full fine-tuning and continued pretraining require explicit owner approval and a compute budget.

## Implementation status
The Python profile planner validates profiles and emits a training manifest. The static browser builder exports a local JSON profile. These are not yet wired to account persistence, source-content ingestion, GPU jobs, Ollama deployment, or a live five-minute scheduler. Tests are authored but must be executed in the repository workspace before production use.
