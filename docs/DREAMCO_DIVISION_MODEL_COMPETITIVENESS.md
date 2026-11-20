# DreamCo Division Model Competitiveness Program

## Goal

Every canonical MasterBot gets an independently testable, domain-specialized model system. The target is competitive performance against the strongest currently available open-weight models on the division's own work—not an unsupported claim that 65 small models can each match a frontier general-purpose foundation model.

## Division model means a real capability

A division model has its own stable identity, versioned approved base model, optional division-specific adapter/checkpoint, domain knowledge index, allowed tools, runtime route, task runner, model card, benchmarks, private holdout set, cost profile, and release evidence. It must complete accepted domain tasks without relying on Buddy to do the actual reasoning. Buddy coordinates and delegates; it cannot conceal a weak division model by doing its work itself.

Shared base weights and common infrastructure are allowed. Division-specific data, adapters, retrieval indexes, permissions, scorecards, and release records remain separately versioned and isolated. A renamed endpoint or prompt template alone does not qualify.

## Training strategy

1. Evaluate several license-compatible open-weight base models on representative tasks.
2. Establish a reproducible baseline before tuning.
3. Improve retrieval, tools, prompts, and task decomposition first.
4. Use LoRA/QLoRA or other parameter-efficient adaptation where measured gaps justify it.
5. Use continued pretraining/full fine-tuning only when rights-cleared data, compute, and evaluation justify the cost.
6. Treat training a new foundation model from scratch as a separate research and budget decision.

## The 65 MasterBot / 45 domain crosswalk

The current canonical registry contains 65 MasterBot entries. The 45-domain taxonomy must be reconciled against those entries using explicit primary ownership and secondary collaboration links. Do not assume that 65 MasterBots equals 45 domains, and do not silently invent the mapping. Generate one model profile for every canonical MasterBot; mark the 45-domain crosswalk unresolved until the authoritative taxonomy is imported and reviewed.

## Required evaluation

Every division runs both a shared general-capability regression suite and its own expert-authored domain suite. The domain suite includes realistic end-to-end workflows, tool/runtime tests, edge cases, private held-out tasks, and regression cases from verified failures.

Compare candidates fairly: same prompts, tools, context, decoding, precision, hardware class, and benchmark version. Record parameter and active-parameter counts, license, model artifact hashes, repeated-run variance, accuracy, calibration, latency, throughput, memory, cost, safety, and reliability. Keep private holdouts out of training and tuning. Report public benchmark results separately from private internal results.

External references include the [Artificial Analysis Intelligence Index methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking), [Hugging Face Open LLM Leaderboard methodology](https://huggingface.co/docs/leaderboards/open_llm_leaderboard/about), and domain-appropriate coding/science evaluations. Leaderboards change; snapshot the exact version and date used. Do not compare incomparable model configurations or claim frontier parity from one benchmark.

## Daily improvement loop

For each division: discover benchmark gaps; prioritize dependency-unblocked work; select the lowest-risk intervention; execute in an isolated, resource-bounded runner; evaluate on validation data; run private holdout only for release candidates; run general, safety, privacy, and tool regressions; record scores and artifact hashes; then keep, revise, or roll back the candidate. A division's score improves only when measured evidence improves.

## Mastery and release

Lifecycle: `profiled → base_model_selected → domain_data_ready → baseline_measured → adaptation_ready → sandbox_trained_or_configured → domain_benchmarked → general_regression_passed → independent_review → release_eligible → mastered`.

Promotion requires rights/provenance, pinned artifacts, baseline and candidate scores, private holdout pass, general regression and safety pass, cost/latency/memory report, reproducible evidence, tested commit SHA, and independent reviewer approval. Passing makes a candidate eligible for human review only. No automatic production weight update, merge, deployment, or paid compute.

## Privacy and governance

Data rights are mandatory. User-controlled sources require explicit purpose-specific opt-in. Personal memory, product improvement, cross-user learning, and foundation-model training remain separate permissions. Raw conversations never enter shared training by default. Tenant isolation, deletion/withdrawal propagation, source provenance, and held-out split isolation are mandatory.

## Current status

This PR adds the policy and a deterministic fleet-profile builder. It does not train 65 models, provision GPUs, create provider credentials, or prove model competitiveness. The first execution target is to generate all 65 model profiles, then reconcile the authoritative 45-domain map, select base models with license checks, and establish domain-specific baselines.
