# DreamCo Universal Bot Learning Foundry

## Scope: all current and preserved bots
This program extends individualized training blueprints beyond the 55 commercial business micro-bots to the existing DreamCo inventory.

It reads the generated canonical fleet manifest (currently 1,232 entries, including its separately flagged supplemental and teammate entries), preserves the original library's 200 income bots and 12 major systems as historical-source candidates, and includes all 55 business micro-bot roles supplied by the owner. It also materializes separate 100-slot learning manifests for all 65 MasterBot lanes and all 55 domain divisions (120 division manifests total).

**Accounting rule:** these are different inventories and must not be added into a single "active bot" count. MasterBots and domain divisions are learning/ownership lanes, not additional specialist bots. Legacy records remain separate from current runtime entries until identity reconciliation. Duplicate flags remain review states, not new independent models.

## Per-bot curriculum: 100 personalized slots
| Slots | Stage | Count | Learning objective |
|---|---|---:|---|
| 001–025 | Task and role taxonomy | 25 | Task statements, skills, scope, human/robot/AI boundaries, safety and handoffs |
| 026–055 | Domain playbooks and SOPs | 30 | Industry workflows, compliance, templates, calculations, contracts and exception paths |
| 056–080 | Synthetic scenarios | 25 | Original DreamCo examples, edge cases, tool drills and failure recovery |
| 081–100 | Evaluation and tool-use harnesses | 20 | JSON contracts, deterministic tests, holdouts, red-team and regression tests |

Each slot is personalized with the bot name, division, focus tags, query and provenance references. A slot is not a downloaded source or completed lesson. Unknown third-party rights are blocked by default.

Each bot has a 10,000-example synthetic-data target. This is a target only; the generator does not fabricate completed datasets. Synthetic data must be independently authored, reviewed for leakage and validated before any training approval.

## Model size policy
- The 55 business micro-bots start with an 18.5M-parameter target each. Their theoretical aggregate is 1.0175B parameters across 55 separate models, not one dense model.
- Existing focused bots default to the 18.5M target; broader capability surfaces may be proposed for the 45M family.
- A 45M upgrade requires a documented capability gap, baseline results, memory/latency profiling and a controlled comparison.
- Parameter targets are not verified counts until the model is instantiated and its tensors are counted. All generated records are explicitly untrained and contain no weights.

## Buddy semantic router
Buddy acts as the Provost. It classifies the task, retrieves approved capability cards, selects the minimum necessary specialists, checks ownership and permissions, runs isolated tasks, validates outputs and evidence, synthesizes passing results and escalates high-impact actions. It does not load every specialist model simultaneously.

## Buddy semantic candidate router

`buddy/fleet_runtime/semantic_router.py` ranks candidates across the canonical fleet, 55 commercial business micro-bots and 212 preserved original-bot records. It uses deterministic metadata matching and delegates division/MasterBot ownership resolution to the existing governed router. It never executes a bot, loads model weights, grants permissions or turns an unresolved ownership proposal into authorization.

## Generate and validate
```bash
python tools/build_dreamco_universal_bot_learning_manifests.py
python tools/build_dreamco_universal_bot_learning_manifests.py --materialize
python -m unittest tests.test_dreamco_universal_bot_learning_manifests tests.test_buddy_semantic_router -v
```

The default run writes an inventory index. `--materialize` writes a separate JSON file for each canonical, legacy and business bot plus all 120 division learning manifests under `config/generated/dreamco-bot-learning-manifests/`. Generated artifacts should be rebuilt from their source registries, not hand-edited.

## Non-negotiable gates
1. Rights, license, terms, privacy and provenance review before ingesting third-party data.
2. Separate train, validation, test and private holdout sets; holdouts never train.
3. Isolated, resource-bounded sandbox; no production credentials or unrestricted network by default.
4. Tests, unseen transfer tasks, independent benchmark review and regression checks before capability promotion.
5. No live financial, legal, employment, security, outreach or destructive action without the relevant specialist policy and human approval.
6. No claim of trained weights, performance, mastery or production readiness from a manifest or CI job alone.
