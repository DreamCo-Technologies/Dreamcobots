# Buddy domain coverage audit — 2026-10-22

Source: `main` commit `466bbefeff6cf14ac89d3e3a77c53f91b9737d90`.

- Dashboard registry: 45 divisions (`command-center/data/divisions.json`).
- MasterBot registry: 65 divisions (`config/masterbot-65-registry.json`). These are different taxonomies, not 20 missing implementations by inference.
- Model benchmark registry: 12 suite definitions (`config/buddy-model-benchmarks.json`). Definitions do not prove scores.
- Benchmark task registry: 11 task labels, `runs: 0` and `score: not measured` (`config/buddy-benchmark-task-registry.json`).
- Student adapter registry: no adapters; `trained_weights_exist: false` (`config/buddy-student-adapter-registry.json`).
- Keep Green run `39858681599` failed JSON validation at `website/data/pages-connection-index.json`; cause needs direct file investigation before modification.

## Next evidence gates

Reconcile both division taxonomies by explicit stable IDs; map one representative independent holdout per division; record model checkpoint and rights, latency, cost, safety, hardware and quality with reproducible receipts; require a reversible release. Do not claim trained weights, model parity, or production readiness from registry entries. Do not dispatch additional workflows, train on unlicensed data, or spend without approval.
