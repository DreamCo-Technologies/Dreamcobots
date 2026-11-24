# DreamCo Division Resource Readiness

## Objective

Give every canonical MasterBot a complete, auditable resource blueprint so a division can progress from discovery to a tested specialist model without inventing resources or claiming unbuilt infrastructure.

## Scope

The generated map contains 65 unique division resource bundles. Each bundle defines:

- **Databases:** an isolated logical namespace, shared PostgreSQL/pgvector/full-text platform options, SQLite sandbox, object storage, migrations, tenant controls and lineage tables.
- **Datasets:** one taxonomy-driven discovery lane, subject queries, permitted source classes, provenance, rights, privacy, quality, split-hash and holdout requirements.
- **Teacher models:** Buddy's teacher-coordinator role plus capability-matched Hugging Face seed-model candidates. Candidates are not connected, licensed, benchmarked or approved merely by being listed.
- **Machine learning practice:** 30 practice areas from data design and classical ML through transformers, multimodal learning, distillation, evaluation, MLOps, privacy and serving.
- **Reverse engineering:** an authorization-first workflow for user-owned or explicitly authorized systems, followed by clean-room specifications and independent compatibility tests.
- **Distillation:** pinned teacher/student lineage, output-use rights, filtered examples, protected holdouts, reproducible training and independent evaluation.
- **Model routing:** division/task fit, certified DreamCo-first preference, privacy and consent gates, quality, latency, reliability, availability and cost.
- **Compute and operations:** free-first capacity planning, explicit paid-compute approval, run metering, observability, checkpointing, rollback and per-division dashboards.
- **Benchmarks:** domain, general capability, retrieval, tool-use, safety, privacy, robustness, regression and cost/latency suites.

## Per-division model strategy

Every division must have its own immutable model identity, version, lineage, logical endpoint/auth scope, benchmark suite and release record. The practical starting architecture is a shared base model with division-specific adapters or compact specialists where that is more economical. It does not require training 65 huge foundation models from scratch.

## Resource routing

`buddy/resources/division_resource_router.py` produces a policy-only route plan. It refuses external provider routing for sensitive data, requires explicit consent and paid-use approval for premium routes, and excludes providers that are not configured and implemented. It never makes provider calls itself. Actual dispatch requires a separately tested adapter and runtime evidence.

## Reverse engineering and distillation

Reverse engineering is limited to authorized inputs. It may map observable interfaces, workflows, APIs and data models, then create an independently authored implementation. It must not bypass access controls, extract credentials, circumvent DRM or copy protected code or weights without permission.

Distillation is only allowed when the exact teacher/provider terms permit use of the outputs. The pipeline pins teacher/student revisions, records provenance, separates private holdouts, evaluates student and teacher on identical tasks, and rejects regressions. Some providers explicitly restrict training/distillation; their outputs must not be used for this purpose unless terms expressly authorize it.

## Crosswalk owner review

The crosswalk contains **20 unresolved MasterBot-to-domain mappings** and **10 unassigned domain profiles**. The owner-review file preserves both lists with empty candidate arrays. Similar names are not treated as evidence. An authorized owner must provide the mapping and supporting evidence before the canonical crosswalk changes.

## Truth and rollout

All 65 bundles currently say `requirements_defined_not_provisioned`. This means the required resources and evidence are defined, not that databases, GPUs, models, providers or endpoints are already provisioned. Promotion states are requirements-defined, configured, connected, validated and certified; each transition needs real integration evidence.

## Validation

```bash
python tools/build_division_resource_readiness_map.py
python -m unittest tests.test_division_resource_readiness
python tools/build_division_resource_readiness_map.py --check
```
