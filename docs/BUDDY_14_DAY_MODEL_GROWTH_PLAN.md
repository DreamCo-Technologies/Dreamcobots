# Buddy 14-Day Model Growth and Expansion Plan

**Window:** 2026-11-21 through 2026-12-04 (14 calendar days)  
**Target:** a reproducible, tested small GPT-style learning baseline and a working evidence-driven Buddy growth loop.  
**Not a promise:** frontier GPT-5 capability, a production-ready 25M model, or a full DreamCo fleet certification cannot be guaranteed by a date. Completion is evidence-gated.

## What “grow” means

Buddy improves along four separately measured axes:
1. **Knowledge growth:** versioned, rights-cleared retrieval and lesson memory with source lineage.
2. **Skill growth:** specialist capability units, sandbox practice, targeted tests and held-out transfer.
3. **Model growth:** optional fine-tuning/adapters or small-model weight updates only after dataset, license, compute and approval gates pass.
4. **System growth:** new tools/routes/providers are registered behind permissions, contract tests, rollback and independent benchmarks.

Do not equate adding parameters, documents, bots or prompts with improved capability. A capability is promoted only when a pinned benchmark improves without unacceptable regression.

## Day-by-day execution

| Day | Date | Deliverable | Exit evidence |
|---|---|---|---|
| 1 | Nov 21 | Reproducible environment, baseline harness, model/data cards | Pinned dependencies, seed, hardware profile, baseline test report |
| 2 | Nov 22 | Tokenizer and data pipeline | UTF-8 round-trip, deduplication, split-isolation and provenance tests |
| 3 | Nov 23 | Tiny causal language-model skeleton | Tensor-shape, causal-mask, finite-gradient and tiny-batch tests |
| 4 | Nov 24 | Transformer block and positional encoding | Numerical/unit tests and causal leakage test |
| 5 | Nov 25 | Optimizer and profiling | Loss curve, tokens/sec, peak memory, run config and cost estimate |
| 6 | Nov 26 | CPU-sized pretraining experiment | Checkpoint hash, validation loss/perplexity and sample review; reduce scope if runtime exceeds budget |
| 7 | Nov 27 | Repeatability and first learning review | Second-seed run, baseline comparison and documented failure analysis |
| 8 | Nov 28 | SFT and adapter lab using synthetic/rights-cleared fixtures | Data rights manifest, adapter metadata, held-out task score |
| 9 | Nov 29 | Reward loop and evaluation | Unit-test reward harness, reward-hacking tests and regression report |
| 10 | Nov 30 | Optional multimodal patch exercise; inference packaging | Shape/contract tests; vision work is optional if core track is behind |
| 11 | Dec 1 | Buddy model registry, lineage and routing integration | Read-only route, allowlist, fallback and audit contract tests |
| 12 | Dec 2 | Capability growth and benchmark-gap closure | Same-fixture before/after scores, holdout transfer and regression results |
| 13 | Dec 3 | Reliability, security and reproducibility hardening | Adversarial tests, dependency/security scan, second-seed repeat |
| 14 | Dec 4 | Independent graduation review and next-cycle backlog | Re-runnable evidence packet, model card, explicit pass/block list |

## Daily operating loop

1. Capture current benchmark scores and the current model/checkpoint identity.
2. Select the largest verified capability gap by expected gain per unit cost.
3. Study one approved source; preserve citation, license and provenance.
4. Generate a small lesson and synthetic/rights-cleared practice fixtures.
5. Run the exercise in an isolated sandbox with network and secret access denied by default.
6. Run targeted tests, a held-out transfer test and regression tests.
7. Save run configuration, seed, logs, artifact hashes, scores and failure analysis.
8. Promote only if the candidate beats the pinned baseline and passes safety/regression gates; otherwise roll back and turn the failure into the next lesson.

## Non-negotiable gates

- Public videos/articles are curriculum references, not automatically licensed training data.
- GPT-5 is proprietary; do not claim access to GPT-5 weights or its confirmed internal architecture.
- Unknown dataset rights, missing consent, missing provenance or unclear model licenses block weight training.
- No private Gmail, user content, production secrets or customer data enters a training set by default.
- No paid compute or production weight update without explicit authorization and a documented budget.
- Keep a stable baseline and rollback path. Never overwrite the last known-good model.
- Keep knowledge retrieval, adapter fine-tuning and base-model pretraining as distinct methods with separate evidence.
- A deadline does not override failed tests. On Dec 4, report what passed, what is blocked, and the evidence; do not relabel unfinished work as complete.

## Definition of done

The 14-day milestone passes only when the repository can reproduce the small-model baseline, the Bootcamp planner generates the 14-day schedule, tests validate the growth loop and safety gates, Buddy can record and retrieve versioned lesson/evaluation evidence, and an independent rerun confirms benchmark results. If training-data rights or compute remain unavailable, the model-weight-training milestone is explicitly blocked while the curriculum, tests and non-weight knowledge/skill growth components can still be completed.


## Execution ledger — 2026-11-21 follow-up

| Work item | Status | Evidence / blocker |
|---|---|---|
| Day 1 baseline harness and model/data cards | CI_ARTIFACT_PASS | Added a pinned CPU PyTorch dependency, deterministic baseline CLI, model card, and synthetic evaluation-only data card. Bootcamp run 44914644886 passed the 8 tiny-GPT tests, 35 dataset-hub/routing tests, and 17 failure-learning/safe-repair tests; it also passed the unknown-problem CLI smoke test and uploaded baseline artifact 14711261271. CI: Python 3.13.18, PyTorch 2.10.0+cpu, CPU, seed 42, 34,432 parameters, initial synthetic-fixture loss 21.681970596313477, report hash 0070c014842a5f3716d7cc940fcdd5fc7e028d611104cb8a6758a288812768db. Local rerun also passed (Python 3.13.5; report hash 7ce5c47468dd9c2b5fc84c18c9103d7cf5a959787cd36b92ba726f8e0ad691b5). |
| Day 2 byte tokenizer | PARTIAL_LOCAL_TESTS_PASS | UTF-8 round-trip and invalid-byte-ID tests pass. Dataset deduplication, train/validation/test split isolation, and full provenance pipeline remain open. |
| Days 3–4 causal transformer skeleton | IMPLEMENTED_LOCAL_TESTS_PASS | Tensor shape, causal future-token isolation, finite gradients, and unchanged-parameter tests pass. No optimizer step or weight update occurred. |
| Days 5–7 optimizer, profiling, pretraining, checkpoint, repeat training | BLOCKED_NOT_AUTHORIZED | No separate explicit weight-training authorization or compute approval was supplied. No training, optimizer step, checkpoint, paid compute, or model download was performed. |
| Days 8–10 SFT, reward loop, multimodal exercise | NOT_STARTED | Depends on approved data/model rights, a separate training authorization, and core baseline evidence. |
| Days 11–12 Buddy registry, lineage, routing, benchmark-gap closure | PARTIAL_LOCAL_TESTS_PASS_CI_PENDING | Added a read-only model registry, explicit baseline lineage record, safe route decision gate, and benchmark contract. The untrained baseline is registered but not routable. Seven registry/routing tests passed locally; CI rerun is pending. Full runtime integration, provider allowlists/fallback, capability-quality benchmark runs, and before/after gap closure remain open. |
| Days 13–14 independent graduation and hardening | PENDING | Requires CI artifacts, repeatable evidence packet, security checks, second-seed evaluation, and independent review. |

### Baseline implementation boundary

The new tiny GPT is an untrained random-initialization reference implementation with byte-level tokenization, learned positions, causal attention, residual blocks, and a feed-forward network. The runner evaluates a seeded synthetic byte fixture and emits JSON only. It does not perform training, save model weights, access the network, or qualify for production routing. The synthetic fixture is not approved for weight training.

The follow-up Bootcamp workflow now runs the deterministic baseline tests and stores the evaluation report as a 90-day artifact on pull requests and manual/push runs. Scheduled metadata discovery skips the PyTorch install and baseline evaluation to avoid unnecessary dependency downloads.

### Deadline assessment

The December 4, 2026 target remains feasible only as a narrowed engineering milestone: reproducible tiny baseline, tokenizer/data-contract checks, Bootcamp evidence pipeline, read-only model registry/lineage/routing contracts, and a small independent benchmark suite. It is not feasible to promise a trained 25M-parameter model, 65 competitive specialist models, full DreamCo fleet mastery, or production readiness by that date under the current no-paid-compute/no-weight-update constraints. Those outcomes remain explicitly out of scope unless separately authorized and supported by rights-cleared data and compute.


### Registry and benchmark contract follow-up

A read-only `buddy-model-registry.json` now records the tiny GPT model identity, code/model-card/data-card references, untrained lifecycle state, absent training run, absent weight artifact, and disabled route. The registry validator rejects duplicate model IDs and inconsistent trained-weight metadata. The route resolver requires a trained artifact path/hash, dataset-card hash and verified rights, verified model-license URL/evidence, a separate training authorization ID, immutable base-model revision, a run ID, non-regressing direction-aware benchmark scores, holdout/regression/provenance checks, and independent review approval. Higher-is-better and lower-is-better metrics are handled separately using weighted relative improvement. The baseline is intentionally returned as `BLOCKED_NO_ELIGIBLE_MODEL`.

The benchmark contract separates engineering correctness checks (tokenizer, causality, gradients, repeatability, JSON evidence) from capability-quality benchmarks. Capability-quality scores remain null and promotion remains blocked. Passing engineering tests does not establish language quality or model mastery.
