# Buddy open-weight baseline: review-only shortlist (2026-10-23)

**Status:** research and reproducibility *design*, not a model selection, download, training authorization, benchmark run, verified license opinion, or production-readiness claim. Keep all new model routes disabled until independent checks. No GPT-5.5 weights are available through this work and no GPT-5.5-equivalent capability is implied.

## Candidate shortlist

| Candidate (official repository) | Stated license on official model card | Approx. model parameters | Theoretical raw BF16 weight bytes* | Reason to evaluate | Limitations |
| --- | --- | ---: | ---: | --- | --- |
| [HuggingFaceTB/SmolLM2-360M-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct) | Apache-2.0 | ~360M | ~0.72 GB | First CPU/on-device feasibility and latency baseline | English-oriented; small model may fail complex coding, math, tool use |
| [Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B) | Apache-2.0 | ~0.75B actual tensor parameters (despite 0.6B name) | ~1.50 GB | Primary small Buddy quality/latency challenger | Inference and training memory higher than weights; benchmark independently |
| [Qwen/Qwen3-1.7B](https://huggingface.co/Qwen/Qwen3-1.7B) | Apache-2.0 | ~2.03B actual tensor parameters (despite 1.7B name) | ~4.06 GB | Larger quality challenger if free, approved compute permits | Higher memory/latency; no presumption of superiority on DreamCo tasks |

*Estimates are parameter count × 2 bytes, not measured peak RAM/VRAM, download size, KV cache, activation/optimizer memory, or tokens/sec. Four-bit weight storage is roughly one quarter of BF16 **before** scales, metadata, dequantization, activations, KV cache and training overhead. Never treat these figures as a hardware compatibility guarantee.

**Rights:** The linked official model cards displayed `apache-2.0` on 2026-10-23. Apache-2.0 generally permits commercial use, modification, derivative distribution, and redistribution subject to its terms, including preservation of license/notices where applicable: https://www.apache.org/licenses/LICENSE-2.0 . This is preliminary metadata review only. Before downloading, training, redistribution, or publishing derivative weights, inspect each exact model revision's LICENSE/NOTICE, upstream provenance, any third-party assets, model card and applicable platform terms; document review and approval. License metadata alone does not prove the training dataset rights or privacy clearance.

## Proposed order and honest acceptance criteria

1. **Inventory before execution:** reconcile the repository's 55 actual division entries against MasterBot taxonomy, task families, suites and capability/goal registries. The existing audit reports **12 suite definitions**, **11 task labels**, and **zero registered benchmark runs**; these are registry statements, not measured model capabilities. Keep each division unverified until independently evaluated.
2. **First working baseline:** only if the operator has *verified* rights, hardware, available free/approved resources and explicit execution approval, benchmark the unmodified SmolLM2-360M-Instruct and Qwen3-0.6B at a pinned revision on the same original, consented test tasks. Record device/CPU/GPU, RAM/VRAM peak, warm/cold latency, tokens/sec, error rate, energy or estimated compute where measurable, and actual zero-or-approved cost. Prefer the smaller model only if its independently measured task quality and safety are sufficient.
3. **Representative coverage:** start with original synthetic coding, debugging, arithmetic, SQL, tool-selection, orchestration, safety and multilingual tasks, then add real consented and provenance-checked domain tasks for finance, real estate, sales, marketing, education, science, research, multimedia and accessibility. Do not infer division mastery from generic tasks. Do not put independent holdout prompts/answers in training or public fixtures.
4. **Independent holdouts:** separate by source, task family, and near-duplicate content; keep sealed evaluation material outside the public training repository. Require grader provenance, signed or otherwise independently verifiable run receipts, task IDs, model revision/hash, dataset/split hashes, grader revision, repeat count, regressions and human review. Public development fixture scores cannot authorize model promotion.
5. **Training only after baselines:** if a modest LoRA/QLoRA experiment is justified, verify base and derivative rights, dataset consent, no secrets or personal information, exact pinned source revisions, split isolation, hardware and cost, and separate approval. Run on approved free compute only. No unattended weight upload. Preserve immutable checkpoint hashes and a rollback pointer; compare with the unmodified base on identical sealed holdouts before any release review.

## Reproducibility template (NOT an executable job)

This is a proposed hyperparameter starting point for a **separately approved** small-model LoRA experiment; not validated for any candidate architecture or hardware. Do not feed it to an unattended training runner.

```json
{
  "schema": "dreamco.buddy_lora_experiment_proposal.v1",
  "execution_authorized": false,
  "download_authorized": false,
  "publish_weights_authorized": false,
  "base_model": null,
  "base_revision_full_commit_sha": null,
  "base_license_and_notice_review_receipt": null,
  "dataset_sha256": null,
  "dataset_consent_and_rights_receipt": null,
  "train_split_sha256": null,
  "validation_split_sha256": null,
  "sealed_holdout_receipt": null,
  "target_modules": null,
  "method": "LoRA",
  "seed": 23,
  "rank": 8,
  "alpha": 16,
  "dropout": 0.05,
  "learning_rate": 0.0001,
  "micro_batch_size": 1,
  "gradient_accumulation_steps": 8,
  "max_sequence_length": 1024,
  "epochs": 1,
  "hardware_and_memory_preflight_receipt": null,
  "compute_budget_usd": 0,
  "checkpoint_artifact_sha256": null,
  "baseline_evaluation_receipt": null,
  "post_training_evaluation_receipt": null,
  "rollback_artifact_sha256": null,
  "human_release_approval_receipt": null
}
```

All null fields are deliberate **blockers**, not defaults to auto-fill. Select architecture-specific target modules and QLoRA quantization only after verifying model compatibility, installed packages, device support, memory headroom and dataset license. Do not install speculative dependencies. Training should remain disabled when any rights, provenance, cost, hardware or independent-evaluation gate is missing.

## Known CI blockers at review time

On PR #15436 head `833e1a270697d292a88a02004f8c68b857b90fbd`, the Buddy Teacher Coverage Audit succeeded (Actions run `40007963488`), but Command Center Data Contract `40007963346`, Fleet runtime truth `40007963388`, Core Health `40007963540`, Keep Green `40007963144`, and Frontier Claim Trust Gate `40007963348` failed. The Fleet runtime truth log specifically reported **111 vs 112 workflow count** and stale file-prospectus shards; repair by running canonical generators against the full checked-out repository and reviewing the diffs, never by weakening the gates. The frontier claim gate may be intentionally blocking unsupported production claims. Do not merge or deploy while unresolved.

**Evidence URLs:** https://github.com/DreamCo-Technologies/Dreamcobots/pull/15436 ; https://github.com/DreamCo-Technologies/Dreamcobots/actions/runs/40007963488 ; https://github.com/DreamCo-Technologies/Dreamcobots/actions/runs/40007963388 .

**What was not done:** no model downloaded, no LoRA/QLoRA job run, no new weights or benchmark receipts, no private dataset access, no paid API, no secrets touched, no workflow dispatched, no production deployment or merge.
