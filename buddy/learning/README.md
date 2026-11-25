# Buddy Learning

Buddy's learning system separates **evidence collection** from **mastery claims**.

## Pipeline

- `action_failure_learning.py` — stable signatures and failure taxonomy.
- `benchmark_progress.py` — pass-rate/native-pass-rate calculations and mastery gating.
- `benchmark_learning_policy.json` — repeated-pass, holdout, regression, and dependency policy.
- `LEARNING_FROM_FAILURES.md` — failure-to-retest evidence contract.
- `record_buddy_benchmark_learning.py` — converts deterministic benchmark output into durable evidence.
- `study_resource_scheduler.py` — selects the next study source from unresolved capability gaps.
- `study_data_schema.json` — categorizes study evidence for authorized future training/reuse.

The benchmark runner remains the source of truth for benchmark execution. The recorder only serializes its result for later comparison; it does not execute untrusted output or alter production code.

## Mastery

A passing run is not automatically mastery. Buddy's policy requires repeated native passes, an independent holdout, and regression protection before a capability is promoted.

## Adaptive study loop

`benchmark failure -> capability gap -> rank resources -> study authorized material -> sandbox practice -> targeted retest -> holdout -> regression -> mastery`

The Top-1000 study curriculum is separate from the protected DreamCo model catalog. Resources are ranked by relevance to failures, technical authority, hands-on value and freshness. Study evidence is categorized by source, capability, material type, benchmark and provenance so authorized learning artifacts can later support other users/models without exposing private/client data.


## Universal library knowledge

- `universal_library_registry.py` searches only approved, rights-eligible DreamCo library guides and records internal knowledge gaps without automatic external routing.
- `library_registry_discovery.py` performs one opt-in metadata-only query against an allowlisted public registry provider. It never downloads or executes package code.
- `course_track_registry.py` exposes the 38 existing library ecosystem discovery lanes, all 531 unverified candidates parsed from the existing library mastery curriculum, and approved library guides in the shared 55-domain / 65-MasterBot lesson queue.
- `tools/create_buddy_library_guide_draft.py` creates review-required guide skeletons; it cannot grant rights or approve a guide.
- `tools/buddy_library_knowledge.py` exposes search, gap, report and explicit opt-in discovery commands.

A guide enters internal search and the course queue only after it is approved and passes the guide evidence and rights checks. Drafts, stale items and blocked items remain visible in the coverage report but are not presented as Buddy knowledge.


## Runtime bridge and local retrieval

- `runtime_bridge.py` exposes `BuddyLearningBridge.library_knowledge()` and `library_learning_queue()` and `library_coverage()` to the host-mediated Buddy runtime; the queue is scoped to a canonical division or MasterBot lane.
- `buddy/datasets/unknown_router.py` invokes the same internal-first route for library, framework, SDK, package and API questions; it reuses the existing explicit external-discovery gate.
- The bridge searches approved internal guides first through `foundry.local_rag.LocalRagStore`; the index is local, dependency-free TF-IDF and does not call an embedding or frontier model.
- An unapproved/missing guide returns a gap and any matching seed candidates, clearly labeled as unverified.
- Public registry metadata discovery requires an explicit `external_discovery=True` from the host. It does not invoke an external model, download packages or execute code.
- Knowledge-gap persistence is opt-in and requires the host to mark the query redacted. Gap records are written under ignored `.dreamco/`, never the public guide catalog or website data.
