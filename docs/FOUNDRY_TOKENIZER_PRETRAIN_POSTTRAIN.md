# DreamCo Foundry: tokenizer, pretraining and post-training

## End-to-end pipeline

1. **Rights gate:** verify the Ed25519-signed source manifest and every dataset SHA-256.
2. **Tokenizer:** train a byte-level BPE tokenizer from scratch, or learn domain BPE pieces and append only missing tokens to a pinned base tokenizer without renumbering existing tokens.
3. **Token packing:** create fixed-length uint32 training and validation shards. The training mix is 60% study guides, 25% verified trajectories and 15% general replay by token count.
4. **Shard signature:** the policy owner signs the packed-shard manifest after verifying its source-manifest digest and every shard hash.
5. **Weight training:** run causal PT/CPT, assistant/tool-only SFT, then DPO using verified chosen/rejected trajectories.
6. **Holdout evaluation:** run local-only inference on category `holdout_benchmarks`, deterministic buckets 95–99. No holdout records are read by tokenizer training, packing, SFT or DPO.
7. **Promotion:** compare baseline and candidate reports from the exact same holdout suite and scoring configuration. Merge a LoRA adapter only after the promotion gate passes.

## Signed rights manifest

The manifest is JSON with schema `dreamco.foundry.authorization.v1`. It lives beside its referenced dataset files. Each dataset entry includes:

- `dataset_id`, `path`, `sha256`
- `license_tier`: `PUBLIC_DOMAIN`, `PERMISSIVE_COMMERCIAL`, or `DREAMCO_ORIGINAL`
- `commercial_use: true`, `policy_decision_id`, `approved_by`
- `category`: `study_guides`, `verified_trajectories`, `general_replay`, `verified_preferences`, or `holdout_benchmarks`

Open-weight base models require a signed `models` entry with exact `model_id` and 40-character `revision`, an allowed commercial-use tier, `commercial_use: true`, `license_evidence_id`, and item-level `source_evidence`. The policy signer validates the evidence before signing the whole manifest.

The detached signature is base64 Ed25519 over canonical JSON (UTF-8, sorted keys, compact separators). The trusted public key must be provisioned out-of-band; never commit a private signing key. A platform license label, scraped metadata, or row-level boolean is not authorization. Missing rights evidence, signatures, or file hashes fail closed.

## Sign the source manifest

The policy owner reviews item-level dataset and model-license evidence, then runs the signer in a protected environment. The private key stays outside the repository:

```bash
python -m stages.01_policy_gate.sign_training_manifest \
  --manifest data/foundry/authorization.json \
  --registry contracts/license_policy.yaml \
  --private-key /secure/offline/foundry-policy-private.pem \
  --signature-output data/foundry/authorization.sig \
  --approve-commercial-training --approved-by "Policy Owner" \
  --policy-decision-id "POLICY-REVIEW-REFERENCE"
```

Third-party datasets and base models require item-level `source_evidence` that passes the existing commercial-training policy gate. DreamCo-original data requires a matching owner attestation and SHA-256.

## Tokenizer and token shards

Install optional dependencies in an isolated environment using `stages/05_model_foundry/requirements-foundry.txt`.

Scratch tokenizer:

```bash
python -m stages.05_model_foundry.train_tokenizer --mode scratch --vocab-size 16384 \
  --manifest data/foundry/authorization.json --signature data/foundry/authorization.sig \
  --public-key keys/foundry-policy-public.pem --output artifacts/foundry/tokenizer
```

Open-weight tokenizer extension (the signed manifest must authorize the exact base model revision):

```bash
python -m stages.05_model_foundry.train_tokenizer --mode extend --vocab-size 16384 \
  --base-model Qwen/Qwen2.5-Coder-1.5B --base-revision "$REVIEWED_40_CHAR_SHA" \
  --manifest data/foundry/authorization.json --signature data/foundry/authorization.sig \
  --public-key keys/foundry-policy-public.pem --output artifacts/foundry/tokenizer
```

Extension learns domain BPE pieces separately, appends only tokens absent from the base vocabulary, and preserves existing token IDs. The model loader mean-initializes new embedding rows and the LoRA recipe trains only the newly added token rows through PEFT sparse trainable-token support.

Pack the authorized train/validation records, then sign the shard manifest:

```bash
python -m stages.05_model_foundry.pack_tokens \
  --manifest data/foundry/authorization.json --signature data/foundry/authorization.sig \
  --public-key keys/foundry-policy-public.pem --tokenizer artifacts/foundry/tokenizer \
  --output artifacts/foundry/token_shards --sequence-length 1024

python -m stages.01_policy_gate.sign_token_shards \
  --shard-manifest artifacts/foundry/token_shards/manifest.json \
  --source-manifest data/foundry/authorization.json \
  --source-signature data/foundry/authorization.sig \
  --public-key keys/foundry-policy-public.pem \
  --private-key /secure/offline/foundry-policy-private.pem \
  --signature-output artifacts/foundry/token_shards/manifest.sig
```

The shard signer checks the signed source manifest, its raw SHA-256, the train-only split declaration, holdout exclusion, and every train/validation shard hash before signing.

## Weight training

The 45M scratch recipe uses a small Llama-compatible causal LM initialized from random weights. The open-weight recipe uses a pinned, signed-authorized base checkpoint and LoRA. Both support pretraining/CPT, SFT and DPO.

Run preflight first; it verifies signed source data and the signed shard manifest but performs no optimizer steps:

```bash
python -m stages.05_model_foundry.train_weights --stage all \
  --manifest data/foundry/authorization.json --signature data/foundry/authorization.sig \
  --public-key keys/foundry-policy-public.pem \
  --shard-manifest artifacts/foundry/token_shards/manifest.json \
  --shard-signature artifacts/foundry/token_shards/manifest.sig \
  --recipe stages/05_model_foundry/recipes/scratch_45m_division.yaml \
  --tokenizer artifacts/foundry/tokenizer \
  --token-shards artifacts/foundry/token_shards
```

Only after reviewing the source rights, model authorization, recipe, hardware budget and preflight output should an operator add `--execute --authorize-weight-updates --authorization-reference POLICY-APPROVAL-ID`. The training script masks SFT loss to assistant and tool-call tokens. DPO pairs are accepted only when the chosen response has `LAB_PASSED` plus `TEACH_BACK_VERIFIED` and the rejected response has `LAB_FAILED`.

## Holdout inference and promotion

Holdout benchmark records must be signed under category `holdout_benchmarks`, have task IDs in buckets 95–99, and include `prompt`, `expected_answer`, and `expected_safety` (`ALLOW` or `REFUSE`). The runner uses local model/tokenizer files only; it does not download data or send prompts to an API.

Run the same benchmark suite and scoring configuration against a baseline and candidate:

```bash
python -m stages.05_model_foundry.run_holdout_eval \
  --manifest data/foundry/authorization.json --signature data/foundry/authorization.sig \
  --public-key keys/foundry-policy-public.pem --checkpoint artifacts/foundry/baseline \
  --tokenizer artifacts/foundry/tokenizer --output reports/baseline.json

python -m stages.05_model_foundry.run_holdout_eval \
  --manifest data/foundry/authorization.json --signature data/foundry/authorization.sig \
  --public-key keys/foundry-policy-public.pem --checkpoint artifacts/foundry/candidate \
  --tokenizer artifacts/foundry/tokenizer --output reports/candidate.json

python -m stages.05_model_foundry.eval_holdout \
  --manifest data/foundry/authorization.json --signature data/foundry/authorization.sig \
  --public-key keys/foundry-policy-public.pem --baseline reports/baseline.json \
  --candidate reports/candidate.json --output reports/holdout-promotion.json
```

For a LoRA adapter, pass `--base-model` and `--base-revision` to each inference command; the signed manifest must authorize that exact model revision. The current runner uses normalized exact-match answer scoring and deterministic refusal markers. These are transparent baseline checks, not a substitute for human/domain-specific safety evaluation. Promotion requires the configured minimum thresholds and no regression against baseline.

Only after a passing baseline-comparison report may an operator merge an open-weight adapter. The merge command uses the tokenizer saved with the adapter and requires the explicit `--execute-merge` flag:

```bash
python -m stages.05_model_foundry.merge_adapter \
  --base-model Qwen/Qwen2.5-Coder-1.5B --base-revision "$REVIEWED_40_CHAR_SHA" \
  --manifest data/foundry/authorization.json --signature data/foundry/authorization.sig \
  --public-key keys/foundry-policy-public.pem --adapter artifacts/foundry/candidate \
  --holdout-report reports/holdout-promotion.json \
  --output artifacts/foundry/merged-standalone --execute-merge
```

The merge utility verifies signed model authorization, the exact source-manifest digest, the passing holdout report and the adapter checkpoint SHA-256.

## Split, compute and truth boundaries

- Bucket formula: `int(sha256(task_id)[:8], 16) % 100`.
- Train: 00–89; validation: 90–94; holdout: 95–99.
- Tokenizer and all weight updates read only train. Validation is evaluation-only. Holdout is read only by the local inference runner and promotion gate.
- Pull-request CI runs CPU compile and guardrail tests only. GPU training is manual and requires a self-hosted GPU runner, a protected local policy-signing key path, signed data and an explicit approval reference. Baseline comparison is performed only when a local baseline checkpoint is configured; otherwise promotion remains blocked.
- GitHub-hosted GPU compute, paid APIs and model-provider API keys are not required. No model weights have been trained merely by merging these code changes.
