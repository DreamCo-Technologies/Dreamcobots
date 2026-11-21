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


## Execution record — 2026-11-21 (Day 1)

**Implementation status:** baseline harness added; CI evidence is pending. This record does not mark the GPT-style training unit as mastered.

- Added `buddy/gpt_baseline/tiny_gpt.py`: a dependency-free one-block causal decoder with byte-level tokenization, deterministic parameter initialization, causal self-attention, residual MLP, and next-byte cross-entropy measurement.
- Added a pinned configuration in `config/buddy-tiny-gpt-baseline.json` using only three original synthetic fixtures.
- Added `tools/run_buddy_gpt_baseline.py` to emit a model card and evidence manifest containing the configuration hash, initialization hash, fixture hashes, untrained validation/test losses, Python/platform profile, and commit SHA.
- Added deterministic tests for UTF-8 round-trip, forward shapes, finite logits, causal isolation, seed reproducibility, and no-weight-update behavior.
- Connected the baseline runner, tests, and 90-day evidence artifact to Buddy Sandbox Bootcamp CI.
- Fixed the dataset-discovery GitHub token guard to send authorization only to the exact HTTPS `api.github.com` origin, with deterministic lookalike-host tests. Also removed three unused test imports reported by the prior PR review.

**Evidence boundary:** this is a reproducible, untrained forward-pass reference model. It is not a 25M model, a trained assistant, a useful-capability score, or a checkpoint. No optimizer was run, no weights were updated, no external dataset was downloaded, no course/private/customer data was used, and no paid compute was used. Unit 01's tiny-batch overfit requirement remains blocked pending separate explicit weight-update authorization; Day 2–14 work must preserve that gate.

**PR lineage:** PR #17633 was merged on 2026-11-20 (merge commit `6cae4f2d02f577c2a71e041433879de446306a52`). Its original branch is no longer available. This continuation is isolated on `buddy-growth-sprint/2026-11-21-day1-baseline`, created from the then-current `main` head `63c2a460760f9d3ef5dad65c88acf35ee6cfb2da`; no merge or deployment is part of this continuation.

**Next gates:** obtain a passing Bootcamp CI run and retain its baseline artifact; implement Day 2 tokenizer/data contracts without ingesting external content; then build the trainable tiny causal model skeleton while keeping all weight-update commands disabled until separately authorized.

**December 4 scope assessment:** the repository-engineering milestone remains achievable if it is scoped to a reproducible small decoder baseline, executable Bootcamp evidence capture, deterministic registry/lineage/routing contracts, and benchmark-gap reporting. A trained 25M model, SFT/LoRA run, or production weight update is not currently a committed deliverable because data/model rights and separate training authorization are absent. If those gates remain closed, report the model-training portion as blocked rather than treating a forward-only baseline as trained.
