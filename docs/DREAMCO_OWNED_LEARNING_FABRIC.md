# DreamCo-Owned Learning Fabric

## Product direction

DreamCo is building one place where a user can learn, build, execute, evaluate, and improve. Buddy should turn a user's goal into a capability plan, route the user or agent to appropriate learning resources, create original DreamCo learning material, execute practice in an approved sandbox, evaluate the result, and retain reusable evidence.

This is not a plan to copy every course or ingest every repository file as training data. It is a rights-aware system that converts eligible knowledge into original DreamCo lessons, labs, datasets, and benchmark tasks.

## Repository inventory: start with what already exists

The repository already contains multiple overlapping but useful learning systems. The fabric treats them as existing inputs and contracts to reconcile—not as permission to create another competing scheduler.

| Existing area | Role in the fabric |
|---|---|
| `config/unified-repository-learning-registry.json` | Repository-wide learning, quality, benchmark, and evidence domains |
| `config/buddy-1000-source-bootcamp.json` | 1,000-source discovery and task-based study lifecycle |
| `config/buddy-training-data-provenance-policy.json` | Ownership, license, attribution, privacy, and reuse policy |
| `config/buddy-learning-source-adapters.json` | Connector inventory and source access boundaries |
| `buddy/bootcamp/learning_source_catalog.yaml` | Public learning-provider catalog |
| `buddy/bootcamp/resource_registry.yaml` | Model, dataset, training, inference, and evaluation resources |
| `buddy/bootcamp/task_learning_router.py` | Task-to-resource ranking and study route |
| `buddy/learning/study_resource_scheduler.py` | Capability-gap-driven resource scheduling |
| `buddy/learning/own_training.py` and `sourced_perspective.py` | Original-perspective and source-attribution safeguards |
| `buddy/frontier/learning_orchestrator.py` | Bounded learning jobs from evaluation failures |
| `buddy/learning/continuous_learning_controller.py` | Evidence and promotion decisions |
| `buddy_os/integration/learning_os_connection_graph.py` | Runtime connection discovery and readiness checks |
| `benchmarks/`, `study_packs/`, `data/dreamco_training/` | Candidate tasks, study packs, benchmark assets, and original course bundles |
| `config/onet-priority-curriculum.json` and `config/onet-sandbox-dataset-spec.json` | Occupational skill and real-world task mapping |

The source of truth for detailed inventory is the repository itself. The new manifest at `config/dreamco-owned-learning-fabric.json` records the catalog roots and canonical registries. An initial complete Git-tree scan created `data/dreamco_training/catalog/repository_asset_inventory_seed.json` with 1,223 candidate paths, blob hashes, and sizes; it deliberately copied no file bodies and marks every candidate as rights-review-pending and ineligible for training.

## One canonical catalog, multiple asset types

The catalog must distinguish these layers instead of flattening everything into an undifferentiated training-data folder:

1. **Source registry** — public course providers, official docs, open datasets, standards, repositories, papers, and connected apps.
2. **Repository asset inventory** — DreamCo code, Markdown, schemas, prompts, examples, tests, benchmarks, generated reports, and existing study packs.
3. **Rights and provenance ledger** — creator, owner, license, URL, source version, permitted transformations, attribution, privacy classification, and review state.
4. **Skill and occupation taxonomy** — capabilities, prerequisites, O*NET task/skill relationships, and job-family mappings.
5. **Original lesson library** — DreamCo explanations, diagrams, worked examples, and study guides written from authorized research.
6. **Practice and project library** — original labs, coding challenges, simulations, project briefs, and debugging exercises.
7. **Benchmark and holdout library** — task tests, transfer tasks, locked exams, regression fixtures, and scoring rubrics.
8. **Failure and repair library** — verified failure signatures, root causes, safe fixes, and regression cases.
9. **Execution evidence ledger** — run IDs, tool results, tests, artifacts, latency, cost, model/provider, and safety outcomes.
10. **Model-training manifests** — versioned, rights-cleared train/validation/holdout dataset manifests and training-run metadata.

Every record receives a stable ID, content hash, source references, creation/transformation history, owner/license classification, quality score, skill tags, and status.

## How we make the knowledge genuinely DreamCo's

A third-party course is a reference, not automatically a DreamCo training asset. Buddy may use authorized metadata and permitted material to understand the subject, but the output must be original:

- Explain the concept in DreamCo's own structure and language.
- Compare multiple independent sources and retain disagreements or uncertainty.
- Create new examples, exercises, code tasks, project briefs, rubrics, and transfer tests.
- Avoid reproducing proprietary course text, transcripts, slides, quizzes, or answer keys.
- Keep source citations and license/attribution conditions attached to derived assets.
- Label assets with unknown rights as `unknown_do_not_publish` until reviewed.
- Never label third-party content as DreamCo-owned simply because it is public or accessible.

Repository files also need classification. A source file may be DreamCo code, a third-party dependency notice, user-contributed material, generated output, a licensed dataset, or a reference link. File location alone does not establish ownership or training permission.

## From every repository resource to a useful catalog entry

The inventory process should scan the configured roots and create a manifest, not indiscriminately concatenate all files into one model-training corpus.

For each candidate asset:

1. Capture repository path, blob/content hash, file type, size, branch/commit, and last-modified revision.
2. Deduplicate exact content and identify likely near-duplicates for review.
3. Read structured metadata first: JSON/YAML manifests, schemas, READMEs, course indexes, benchmark definitions, and attribution files.
4. Extract capability tags and links to related bots, workflows, tests, docs, and benchmarks.
5. Determine ownership and reuse rights from explicit evidence; default to blocked/unknown when unclear.
6. Create an original lesson or task only when the source material can lawfully support that transformation.
7. Attach original task variants and evaluation criteria.
8. Publish a versioned catalog record and preserve the source commit/hash.

This makes the entire repository discoverable while preventing a repository scan from silently converting secrets, user data, third-party code, or restricted course content into training examples.

## Buddy's live task-to-learning-to-execution loop

The intended runtime sequence is:

```text
User request
  -> Buddy task intake and intent decomposition
  -> capability gap and prerequisite analysis
  -> task_learning_router selects eligible resources
  -> study_resource_scheduler prioritizes the next learning action
  -> learning fabric creates an original lesson + practice packet
  -> Buddy execution runtime runs approved tools in a sandbox
  -> targeted benchmark and unseen transfer task
  -> regression, privacy, security, and safety checks
  -> continuous_learning_controller evaluates promotion
  -> evidence ledger stores outcome and reusable lesson
  -> Buddy updates the next route and reports verified progress
```

The existing components named in the manifest are the integration points. The new execution packet contract is `dreamco.learning_execution_request.v1`; the completion event is `dreamco.learning_execution_result.v1`. The live runtime must consume these packets through the normal task authorization, tool policy, sandbox, and audit layers. The learning fabric must never become a parallel unrestricted executor.

### Execution packet minimum fields

- `request_id`, `user_goal`, `task_id`, `required_capabilities`
- `selected_resources` and source/rights references
- `original_lesson_id`, `practice_task_ids`, `benchmark_ids`
- `execution_mode`, `sandbox_profile`, `allowed_tools`, `approval_requirements`
- `data_policy`, `compute_budget`, `time_budget`
- `expected_artifacts`, `acceptance_criteria`, `rollback_plan`

### Completion event minimum fields

- `request_id`, `run_id`, `status`, `artifact_refs`
- `tests_and_benchmarks`, `scores`, `holdout_result`, `regression_result`
- `safety_result`, `provenance_refs`, `model_and_tool_versions`
- `latency`, `compute_cost`, `external_assistance`, `failure_signatures`
- `training_job_id` only when a separately authorized trainer actually ran

A route or lesson being generated is not proof that execution happened. A successful external model response is not proof that Buddy solved the task natively. A benchmark result is not a training run.

## Data preparation and model training are separate

The fabric can create original training candidates and versioned dataset manifests. Actual weight or adapter training requires a separate registered trainer, a compatible model license, a rights-cleared dataset, compute approval, a held-out evaluation set, and a recorded run artifact.

Current status for this branch: **no model weights or adapters have been trained and no training job has been launched.** Do not change this state until actual trainer output and evaluation evidence exist.

## Quality and promotion gates

A candidate lesson or dataset is not automatically approved. Required gates:

- rights, license, attribution, and provenance review
- privacy and secret scanning
- originality and source-faithfulness review
- deduplication and dataset contamination checks
- train/validation/transfer/locked-holdout separation
- sandbox practice and task-specific benchmark pass
- unseen transfer task pass
- regression and safety pass
- versioned evidence and reproducible build metadata

Mastery requires repeated independent success, transfer to an unfamiliar task, and no critical regression. Reading a course or collecting 1,000 links is not mastery.

## Phased implementation

### Phase 1 — Catalog and inventory
Reconcile existing registries; inventory the configured repository roots; emit a versioned asset manifest with hashes, ownership classes, source links, and unresolved rights.

### Phase 2 — Original DreamCo content factory
Generate original lessons, project labs, practice tasks, rubrics, and study plans from approved source records. Build subject tracks from programming, AI/ML, data, cloud, cybersecurity, design, business, occupational skills, and real-world workflows.

### Phase 3 — Buddy runtime bridge
Connect task intake, resource ranking, lesson generation, sandbox execution, benchmark evaluation, and evidence recording through the execution packet and completion event contracts.

### Phase 4 — Dataset and model training
Build rights-cleared, deduplicated datasets; version splits; train only approved open models/adapters; record trainer, hardware, configuration, costs, checkpoints, and independent evaluation.

### Phase 5 — User-facing DreamCo platform
Expose one user journey for learn, build, execute, evaluate, and improve, with transparent source attribution, skill progress, artifacts, costs, and readiness evidence.

## Current implementation boundary

This branch establishes the new catalog manifest and integration contract. It does not yet claim that a full repository scan has completed, that every provider account is connected, that every existing workflow is passing, or that Buddy's production task dispatcher has already consumed the new packet. Those are implementation and verification milestones tracked separately.
