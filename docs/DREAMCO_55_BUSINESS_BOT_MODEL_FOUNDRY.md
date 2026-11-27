# DreamCo 55-Bot Business Model Foundry

## Scope and separation
This is a dedicated 55-business-specialist model fleet. It does not replace the canonical 65 MasterBot learning divisions or the separate product/division registry. The 55 roles are the exact business-bot roster supplied in the product specification.

## Model tiers
- Initial specialist micro-model: 18,543,104 config-derived parameters per bot.
- 55-model aggregate: 1,019,870,720 parameters across independent models. This is not one dense model.
- Upgrade blueprint: 45,003,264 config-derived parameters per bot.
- No pretrained weights are included. Every package is explicitly UNTRAINED until a separately authorized training run produces a checkpoint and passes evaluation.

Counts are computed for the declared bias-free Llama-style config: tied token embeddings, grouped-query attention, SwiGLU MLP, RMSNorm, and no projection biases. The model implementation must independently verify instantiated tensor counts before any commercial claim.

## 100-slot curriculum for every bot
Each bot gets a dedicated `bot_XX_manifest.json` with 100 resource slots:
1. Slots 001–025: occupational task taxonomy and role/handoff maps.
2. Slots 026–055: domain playbooks, SOPs, compliance, formulas and decision trees.
3. Slots 056–080: original synthetic scenarios, edge cases and recovery drills.
4. Slots 081–100: tool-use contracts, schema tests, benchmarks and holdout evaluation harnesses.

This creates 5,500 individually addressable resource slots. It does **not** mean 5,500 third-party resources have already been sourced or approved. Empty slots are UNASSIGNED and UNKNOWN_BLOCKED for training. Each slot must receive an exact source/version, provenance, rights review and reviewer approval before acquisition or training.

## Semantic router
BOT_01 is the semantic router, not an automatic merger of the 55 parameter sets. It classifies intent, selects only relevant specialists, sends bounded parallel tasks, validates typed outputs, resolves conflicts, applies risk/permission policies and assembles an evidence-backed answer. It must have deterministic fallbacks and must not execute external side effects without authorization.

## Learning and graduation
Every bot progresses through: catalogued -> rights reviewed -> original curriculum authored -> sandbox lab ready -> lab executed -> tests passed -> unseen transfer passed -> human review when required -> capability registered -> deployment approved. Reading or retrieving a source is not mastery. Benchmark holdouts stay out of training.

## Safety and regulated domains
Finance, tax, payroll, legal, HR, cybersecurity and healthcare-adjacent outputs require jurisdiction-aware boundaries, citations/evidence where applicable, human escalation and role-based permissions. Bots provide workflow assistance, not unlicensed professional determinations.

## Generate and validate
```bash
python scripts/generate_dreamco_business_bot_manifests.py
python -m unittest tests.test_dreamco_business_bot_manifests -v
```
