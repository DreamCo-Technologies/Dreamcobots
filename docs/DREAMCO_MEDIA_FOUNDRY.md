# DreamCo Media Foundry

## Status

The first deliverable is a CPU-only production planner and rights-gated adapter contract. It does not download model weights, call hosted APIs, create media, or claim a render has completed. GPU workers remain optional executors.

## Architecture

- Buddy supplies a structured production request.
- The Stage 08 director validates the request and creates a shot plan.
- `buddy/media/sellability_gate.py` is the canonical asset-rights decision point.
- Real-person reference media must additionally pass the exact-file consent registry.
- A worker injects render adapters; the control plane has no hard-coded provider.
- Outputs should carry provenance sidecars and pass the existing media quality gate.

## Plan-only workflow

Run `python stages/08_media_studio/director.py stages/08_media_studio/shot-list.example.json --output media-plan.json`. The output status is `planned_not_rendered`. This is suitable for a CPU runner.

## Render adapter contract

A worker adapter implements `render_shot(shot, context)` and returns an `asset_uri`. Call `render_production` with an explicit rights manifest and adapter mapping. Every asset must pass the canonical sellability gate. Commercial rendering accepts only `sellable` decisions. `train_only` and `reference_only` assets cannot produce commercial deliverables.

For real-person references, include `subject_type: real_person`, `reference_path`, `consent_registry_path`, `kind` (`voice` or `image`), and `consent_purpose`. The registry checks the exact file hash, scope, revocation and expiry.

## Rights and ownership

Open weights are not a blanket grant of rights to outputs, training data, voices, likenesses, or redistributed checkpoints. Record the exact model checkpoint, code license, dependency licenses, dataset provenance, consent scope and customer agreement for each release. DreamCo-original assets may be marked internally owned only when owner-assignment and rights evidence requirements are met. Unknown or incomplete rights are blocked.

## Explicit non-goals for this phase

- No model training or LoRA fine-tuning.
- No GPU provisioning or paid endpoint creation.
- No voice or likeness cloning without existing consent gates.
- No automatic publishing to YouTube or other platforms.
- No promise of 4K, multi-minute continuity, watermark robustness, or unrestricted commercial rights without measured validation and legal review.

## Model license verification

The candidate registry at `config/buddy-media-model-registry.example.json` is intentionally unapproved. Candidate names are discovery leads, not license conclusions. Before commercial deployment, create a reviewed record for the exact checkpoint and supply the checkpoint SHA-256, SPDX license identifier, local license evidence file and hash, model-card HTTPS URL, explicit commercial-use and redistribution permissions, and a non-empty dependency inventory. `buddy.media.model_license_gate.verify_model_record` fails closed unless all required evidence is present and every dependency has a reviewed MIT or Apache-2.0 license record. This gate does not clear training datasets, likenesses, outputs, trademarks, or customer content; those remain separate rights decisions.
