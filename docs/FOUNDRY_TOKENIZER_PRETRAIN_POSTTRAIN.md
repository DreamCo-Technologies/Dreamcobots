# DreamCo Foundry: tokenizer, pretraining and post-training

## Pipeline
1. Verify an Ed25519-signed authorization manifest and every dataset SHA-256.
2. Train a tokenizer using deterministic train buckets 00–89 only.
3. Pack signed train records into fixed-length uint32 shards with the 60/25/15 curriculum mix.
4. Run separately authorized PT/CPT, SFT or DPO backend jobs.
5. Evaluate validation buckets 90–94 during development and reserve 95–99 for evaluation only.
6. Promote only when signed evaluation evidence shows no regression.

## Rights manifest
The manifest is JSON with schema `dreamco.foundry.authorization.v1`. It lives beside its referenced dataset files. Required dataset fields: `dataset_id`, `path`, `sha256`, `license_tier` (PUBLIC_DOMAIN, PERMISSIVE_COMMERCIAL, DREAMCO_ORIGINAL), `commercial_use: true`, `policy_decision_id`, and `category` (study_guides, verified_trajectories, general_replay, verified_preferences). The detached signature is base64 Ed25519 over canonical JSON (UTF-8, sorted keys, compact separators). The trusted public key must be provisioned out-of-band; never commit a private signing key.

A platform license label, scraped metadata, or row-level boolean is not an authorization. The policy gate owner must verify item-level rights and sign the manifest. If the signing key, signature, evidence, or file hash is missing, processing fails closed.

## Sign the rights manifest
The policy owner must review the item-level evidence, then run the signer in a protected environment. The private key is never stored in the repository:

```bash
python -m stages.01_policy_gate.sign_training_manifest \\
  --manifest data/foundry/authorization.json \\
  --registry contracts/license_policy.yaml \\
  --private-key /secure/offline/foundry-policy-private.pem \\
  --signature-output data/foundry/authorization.sig \\
  --approve-commercial-training --approved-by "Policy Owner" \\
  --policy-decision-id "POLICY-REVIEW-REFERENCE"
```

The signer rejects third-party items unless the existing policy gate grants commercial-training permission and the item-level license evidence is verified. DreamCo-original data requires a matching owner-attestation file and SHA-256. The signed manifest is then verified by every downstream reader.

## Commands
Install optional dependencies in an isolated environment: `cryptography`, `tokenizers`, `transformers`, `numpy`, and `pyyaml`.

```bash
python -m stages.05_model_foundry.train_tokenizer --manifest data/foundry/authorization.json --signature data/foundry/authorization.sig --public-key keys/foundry-policy-public.pem --output artifacts/foundry/tokenizer
python -m stages.05_model_foundry.pack_tokens --manifest data/foundry/authorization.json --signature data/foundry/authorization.sig --public-key keys/foundry-policy-public.pem --tokenizer artifacts/foundry/tokenizer --output artifacts/foundry/shards --sequence-length 1024
python -m stages.05_model_foundry.train_weights --stage pretrain --manifest data/foundry/authorization.json --signature data/foundry/authorization.sig --public-key keys/foundry-policy-public.pem --recipe stages/05_model_foundry/recipes/scratch_45m_division.yaml --dry-run
```

The current weight runner is a strict preflight boundary, not a claim that PT/CPT, SFT or DPO backends have been executed. A backend must be pinned, reviewed and separately enabled before any weight updates. This avoids silently running expensive jobs or accepting unreviewed TRL/Transformers API changes.

## Holdout and compute
- Bucket calculation: `int(sha256(task_id)[:8], 16) % 100`.
- Train: 00–89; validation: 90–94; holdout: 95–99.
- Tokenizer training, packing, SFT and preference construction read only train.
- Holdout evaluation is a separate evaluation-only command; holdout records must never enter vocabulary building or weight updates.
- Pull-request CI runs only CPU guardrail tests. GPU training requires a self-hosted runner, an enabled repository variable and an explicit approval reference. No hosted GPU or paid compute is assumed.
- The example base-model ID is illustrative; verify the model's license and pin an immutable revision before use.
