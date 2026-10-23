# Buddy Master Teacher: division and model coverage audit

Run `python3 tools/audit_buddy_teacher_coverage.py --output /tmp/buddy-coverage.json` after checking out a review branch. This is a **read-only inventory** with no network calls, training, model downloads, workflow dispatches, or paid API calls. Run `python3 -m unittest tests.test_audit_buddy_teacher_coverage` for the synthetic unit tests.

The tool reads the **55 actual divisions** from the production evidence ledger and separately compares the **65 MasterBot taxonomy entries**. A name in only one taxonomy is not proof of a missing or locked bot. It detects duplicate IDs and count mismatches rather than silently counting them as progress. It maps the existing task-label registry to **declared** candidate models, not verified runnable routes, and proposes **55 original synthetic representative-task designs**, one per division currently named in the ledger. If new divisions appear, they remain explicitly `representative_task_needed` until a human reviews an appropriate task.

Every division still needs an owner-approved representative task, licensed/consented data, a genuinely isolated and independently graded holdout, an exact model revision and evaluation receipt. Fixture suggestions are **not** a dataset, passing benchmark, or hidden holdout. No task-route is marked verified by catalog membership. Avoid storing private holdout answers in this public repository.

To promote any model, separately collect signed source and model license checks, rights to commercial and derivative-weight use, privacy and consent records, exact checkpoint and dataset hashes, reproducible training configuration, clean split provenance, independent baseline and repeated candidate evaluations, tool-call and safety regressions, measured local hardware/cost/latency, a rollback path, and explicit owner approval. Keep weights and personal data outside Git; preserve immutable receipt identifiers and verify hashes before promotion. The existing distillation contract remains the source of truth for actual training gates.

**Baseline observed 2026-10-23 from `main` registry content:** the ledger lists 55 actual divisions and 0 production-ready; the task registry lists 11 labels with 0 reported runs; the model benchmark catalog has 12 suite definitions; the student adapter registry has no adapters and declares no trained weights. These are repository claims, not an independently observed production runtime. A notification about hourly distillation does not prove any weight update.

## Small open-weight Buddy shortlist (research only; 2026-10-23)

The following **upstream model cards** advertise the listed licenses. Verify the exact pinned revision, any incorporated third-party assets, notices, derivative-weight redistribution, intended deployment, and dataset permissions before use. No models have been downloaded or benchmarked here.

| Candidate | Upstream model card | Stated license | First-pass rationale | Unknowns / gates |
|---|---|---|---|---|
| Qwen3-0.6B | https://huggingface.co/Qwen/Qwen3-0.6B | Apache-2.0 | Smallest candidate; prioritize CPU/Apple Silicon smoke inference and tool-call schema tests. | Measured quality, runtime compatibility, latency, memory, commercial data rights. |
| SmolLM2-1.7B-Instruct | https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct | Apache-2.0 | Small instruction-tuned baseline for English text and structured output. | Tool reliability, domain scores, real device throughput, training budget. |
| OLMo-2-0425-1B-DPO | https://huggingface.co/allenai/OLMo-2-0425-1B-DPO | Apache-2.0 | Open research artifacts and a useful independent baseline. | Apple runtime support, task quality, full dependency/weight provenance. |
| Gemma 3 1B IT | https://huggingface.co/google/gemma-3-1b-it | Gemma custom terms; access conditions | Comparison candidate only, **not** the default open-license base. | Explicit license acceptance and legal review before download, tuning, or derivative distribution. |

Apache-2.0 generally permits commercial use and modifications with its notice and other conditions; it does **not** confer rights to arbitrary third-party training datasets or hosted teacher outputs. Do not call custom-licensed weights OSI-open-source.

For a 24 GB unified-memory Apple Silicon laptop, start with **inference-only** smoke tests on an exact, pinned small checkpoint using an approved local runtime. Measure peak memory, time-to-first-token, tokens/second, total cost and temperature, alongside paired correctness and safety. Do not assume CUDA QLoRA recipes work on Apple Metal/MPS or that the machine can train a 7B model. A locally measured small-model baseline is more useful than unverified frontier-parity claims. Only consider private LoRA after source/teacher rights and independent holdouts are documented; default CI must not train or fetch weights.


## Registry vocabulary and suite-design gaps

The benchmark task labels and model catalog `task_types` use different
vocabularies. The audit now reports exact mismatches separately from
**unverified alias proposals** (for example `coding` versus `code`).
No alias is treated as a working route. It also links plausible existing
suite designs to task labels while identifying tasks needing a dedicated
benchmark; a generic suite is never a pass receipt. This is an offline
design audit only, not an evaluation of any model.

## Evidence-integrity checks

The auditor now rejects string-valued readiness flags (including `"false"`),
boolean values masquerading as integer benchmark counts, inconsistent
canonical/supplemental division subtotals, and any claimed trained weights
when the production ledger explicitly reports zero trained-weight artifacts.
These checks prevent registry bookkeeping errors from becoming false evidence;
they do **not** validate a checkpoint or prove a completed evaluation.

All 55 division task prompts are **design proposals**, not runnable benchmark
cases, consented datasets, independent hidden holdouts, training receipts,
or proof of capability. Build and independently grade small, rights-cleared
holdouts in each lane before promoting model-routing or division-readiness claims.


## Offline public development-fixture scorer (not a model benchmark)

`tools/score_buddy_dev_fixtures.py` now accepts **externally supplied** responses for three public fixtures already in `config/buddy-model-benchmarks.json`: instruction following, arithmetic reasoning, and structured JSON. Example local input:

```json
[
  {"suite_id": "instruction_following", "response": "READY"},
  {"suite_id": "arithmetic_reasoning", "response": "42"},
  {"suite_id": "structured_output", "response": "{\"result\":42,\"confidence\":0.5}"}
]
```

Save the JSON list to a local file and run `python3 tools/score_buddy_dev_fixtures.py --responses /path/to/local-responses.json --output /tmp/buddy-dev-smoke.json`. The tool checks that catalog prompts, graders and expected values match pinned public definitions, rejects unsupported/duplicate suite IDs and unexpected metadata, and writes **only pinned public fixture hashes and per-fixture pass/fail**, not response text or unsalted response hashes (which could disclose low-entropy private content). It makes zero model calls, does not identify or authenticate a model, does not run hidden holdouts, and never authorizes promotion. These public tasks are trivially memorized; even a 3/3 result proves only that the supplied strings matched the public dev fixtures. Do not report it as a Buddy model-quality improvement. The other nine suite designs still need appropriate evaluators, and all 55 divisions still need independently graded holdouts.

## Private-checkpoint and compute handoff gate (2026-10-23)

`build_training_manifest` is a **review-only handoff**, not permission to train or upload weights. An `output_repo` string cannot establish repository privacy or write authorization. The manifest and its public summary therefore explicitly report `output_repo_privacy_verified: false`, `push_checkpoint_to_private_repo: false`, and `training_execution_authorized: false` even if a request claims owner approval or specifies a nonzero budget. A separate, evidence-checked preflight must verify destination privacy, commercial/derivative model rights, dataset consent, clean independent holdouts, actual available compute, and **separate approval** before any adapter executes. The test uses a fictional public repository name and performs no upload, training, or network call.
