# DreamCo Repository and Buddy Training Readiness

**Audit date:** 2026-11-26  
**Purpose:** Establish what is working, what is verified, and what must be completed before Buddy model-weight training or production release.

This is an evidence-based readiness snapshot, not a production certification. Counts below describe repository inventories and CI artifacts; they do not imply that every listed capability is operational.

## Current state

| Area | Verified state | What it means |
|---|---|---|
| Canonical domain divisions | 55 | The FreeCodeCamp routing repair adds an explicit subject-category profile for each canonical domain division. |
| MasterBot lanes | 65 | These are a separate ownership/runtime taxonomy, not 65 additional canonical domain divisions. Ten supplemental owner mappings remain unresolved. |
| Runtime divisions | 57 | Runtime smoke/audit coverage is a separate registry and must stay reconciled with the 55-domain crosswalk and 65 MasterBot lanes. |
| 500-model registry | 500 slots defined | The registry explicitly says a slot is not proof of an authenticated or running external model. |
| Division model manifest | 65 planned records | Every record remains `inventory_only_not_trained`; base model, tokenizer, dataset manifest, recipe, checkpoint, evaluation and serving fields are unselected or empty. |
| Authorized model-weight datasets | 0 registered | `config/authorized-training-datasets/manifest.json` is empty. Model-weight training must remain blocked until a private, rights-cleared dataset is registered. |
| Authorized FreeCodeCamp transcripts | 0 registered | The transcript manifest is empty. Public video metadata does not grant transcript, derivative-summary, evaluation or training permission. |
| DreamCo Bootcamp seed corpus | 14 examples | Current split is 10 train, 2 validation and 2 test. The new tokenizer path uses only the 10 training examples. |
| Trained Buddy model weights | 0 tracked checkpoints found | No model-weight artifact or verified training receipt was found in the tracked repository tree. |
| Production certification | 19 areas currently UNKNOWN | The production area-evidence manifest is empty. A current PR report is an inventory, not a certification. |

## Curriculum and division requirements

Every canonical domain division must have:

1. A stable canonical domain ID and a reviewed relationship to its MasterBot/runtime owner.
2. A shared foundation curriculum plus an explicit specialist subject profile.
3. Source metadata and provenance for each assigned course or video.
4. An original study guide authored from permitted source material, with the source and permission state retained.
5. Learning objectives, prerequisite checks, worked examples, practice exercises, answer explanations, assessment, and a capstone.
6. A sandbox or executable exercise where the subject requires code or operational practice.
7. Regression tests for routing, completion-state transitions, and evidence recording.
8. A mastery gate based on completed work and measured assessment—not queue membership or documentation alone.

The FreeCodeCamp queue builder and its 55-domain regression are the source for subject categorization. The curriculum builder and detailed study-guide schema define the actual learning sequence and content requirements. A category match is not proof that a video was studied or mastered.

## FreeCodeCamp source boundary

The catalog workflow discovered 1,741 public video metadata records, while the committed catalog snapshot was still a 1,740-record partial inventory at the time of the audit. The curriculum workflow must persist and revalidate the refreshed catalog before source coverage is called complete.

The repository currently registers no authorized FreeCodeCamp transcripts. Therefore:

- Video metadata may be categorized and linked to the official source.
- A title or description must not be represented as a detailed video summary.
- Transcript ingestion, derivative summaries, evaluation use and model training remain separate permission scopes.
- Unapproved third-party source material stays in a blocked/review state; it is not training data.

## First-party tokenizer preparation

The owner-authorized tokenizer path is deliberately narrow:

- Source: `data/dreamco_training/bootcamp/core_lessons.v1.jsonl`
- Authorization: `governance/training-authorizations/dreamco-bootcamp-core-v1-owner-attestation.json`
- Manifest builder: `tools/build_dreamco_bootcamp_tokenizer_manifest.py`
- Corpus: train split only
- Current split: 10 train, 2 validation, 2 test
- Validation and test splits are excluded from tokenizer training.
- Third-party content, private/customer data, holdouts, model-weight training and distillation are excluded.

This path can validate tokenizer training. It does not create a production tokenizer or train Buddy's neural model weights. The 14-example seed corpus is not a sufficient substitute for a reviewed, division-specific model-training dataset.

## Required execution sequence

### 1. Stabilize the repository

- Reconcile the open repair PRs into one non-duplicated sequence.
- Require all relevant CI checks to pass on the final PR head.
- Preserve failing tests and security gates; fix root causes rather than weakening assertions.
- Verify generated artifacts with their `--check` commands after generators reach a stable fixed point.
- Keep GitHub Pages deployment manual-only until a separate release approval is given.

### 2. Complete curriculum coverage

- Run the catalog refresh and synchronize derived inventory counts.
- Build the 55 explicit domain queues.
- Verify every queue contains at least one subject-matched source item.
- Generate each division's learning sequence and study-guide work items.
- Keep unapproved third-party source material in a blocked/review state.
- Review the ten supplemental MasterBot ownership mappings rather than assigning owners by guesswork.

### 3. Run the first-party tokenizer smoke

After the tokenizer PR is merged, manually run **Buddy Authorized Byte BPE Tokenizer Training** with:

- Manifest path: `data/buddy-authorized-corpora/dreamco-bootcamp-core-v1-manifest.json`
- Vocabulary size: `512`
- Explicit confirmation: enabled

Verify the resulting artifact records a passed rights gate, the train-only corpus hash, no holdout use, and `model_weight_training_executed: false`.

### 4. Prepare actual model-weight training

Before model weights can be trained:

- Register a versioned private dataset manifest under the authorized training data policy.
- Record the source hash, ownership/rights evidence, contributor status, privacy review and allowed training scope.
- Keep validation, test and holdout data isolated from training.
- Select a base model and tokenizer with verified license evidence.
- Pin the training recipe, environment, hardware, compute approval, seed and resource limits.
- Run a reproducible baseline and capture training logs, checkpoint hashes and evaluation receipts.
- Do not promote a checkpoint until quality, safety, security, cost and rollback gates pass.

### 5. Benchmark and certify

- Run the required benchmark suites against the exact candidate checkpoint.
- Record dataset version, code revision, environment, repeated-run results and baseline comparisons.
- Verify no holdout contamination and no fabricated or manually edited pass receipts.
- Populate the production area-evidence ledger only with artifacts and successful checks tied to the exact commit SHA.
- Run the strict production certification gate; an inventory report or green unrelated workflow is not a substitute.

## Deployment boundary

The repository's Cloudflare Workers Builds check has continued to appear on pull requests. That confirms a connected build integration, not necessarily a production deployment. The GitHub Pages workflow is being changed so a push to `main` can build and validate but cannot publish automatically; publishing requires an explicit manual workflow dispatch.

No production deployment is claimed by this report. Deployment isolation and runtime smoke evidence must be verified separately.

## Completion rule

Buddy is ready for model-weight training only when an approved training dataset, reproducible recipe, isolated evaluation sets, compute approval, and executable training/evaluation evidence exist. DreamCo is production-ready only when the strict production gate verifies every required area on the exact release revision.
