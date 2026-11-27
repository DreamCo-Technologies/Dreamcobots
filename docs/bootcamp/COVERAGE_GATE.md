# Buddy Bootcamp coverage gate

This gate checks the integrity of the Bootcamp's existing canonical source manifests. It deliberately separates **catalog presence** from **content access**, **lesson authoring**, **practice**, **assessment**, **model training**, and **mastery**.

## Run

```bash
python tools/audit_buddy_bootcamp_coverage.py
pytest -q tests/test_buddy_bootcamp_coverage_audit.py
```

To write a machine-readable report:

```bash
python tools/audit_buddy_bootcamp_coverage.py --output reports/bootcamp-coverage-audit.json
```

## Audited tracks

- Hugging Face course and ecosystem-module inventory.
- O*NET content-model area inventory (not a claim that every occupation and task has a study guide).
- freeCodeCamp channel catalog and complete-learning-path status (not a claim that transcripts or study guides are complete).
- Tokenizer and Tolkien curriculum presence (not a claim that training ran or mastery was achieved).
- Workforce/revenue training paths and their task-playbook contract.
- Benchmark program and task registries (not a claim that benchmarks ran or scores exist).
- The 25M CPU architecture target and its disabled-by-default training policy.
- Optional O*NET task-index snapshot presence, release and completeness state.
- 65-record MasterBot registry and 55-division crosswalk approval state.

The report is intentionally conservative. It returns `coverage_gaps_present` when inventory is present but a source is partial, ownership review is pending, or downstream lesson/training evidence has not been established. It never upgrades a queued lesson to studied, a study record to mastery, or a curriculum plan to completed model training.

This is an initial structural gate. It does not download third-party resources, access gated accounts, copy course transcripts, start paid compute, or change production deployments.
