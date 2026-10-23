# Buddy Master Teacher: division and model coverage audit

Run `python3 tools/audit_buddy_teacher_coverage.py --output /tmp/buddy-coverage.json` after checking out a review branch. This is a **read-only inventory** with no network calls, training, model downloads, workflow dispatches, or paid API calls. Run `python3 -m unittest tests.test_audit_buddy_teacher_coverage` for the synthetic unit tests.

The tool reads the **55 actual divisions** from the production evidence ledger and separately compares the **65 MasterBot taxonomy entries**. A name in only one taxonomy is not proof of a missing or locked bot. It detects duplicate IDs and count mismatches rather than silently counting them as progress. It maps the existing task-label registry to **declared** candidate models, not verified runnable routes, and proposes a small set of **original synthetic fixture designs**. The remaining divisions are explicitly `representative_task_needed`.

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
