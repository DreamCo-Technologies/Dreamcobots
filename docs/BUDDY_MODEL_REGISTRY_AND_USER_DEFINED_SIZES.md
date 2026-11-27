# Buddy model registry, custom sizes, and marketplace gates

## User-defined model sizes

DreamCo model sizing is not limited to the preset parameter buckets. A user may request any positive integer parameter count. The registry's 25M, 45M, 100M, 500M, 1B, 7B, 13B, and 70B values are planning presets, not a maximum-size catalog.

Before training, Buddy must estimate feasibility from the selected architecture and declared compute environment, including:
- CPU/GPU type and count, accelerator memory, system RAM, and available concurrency
- estimated training time, available compute hours, storage, and cost
- precision, sequence length, batch size, optimizer state, checkpoint cadence, and recovery overhead

If the requested configuration does not fit the available resources, Buddy must explain the constraint and offer an explicit smaller configuration. It must never silently change the requested parameter count or claim that every size can be trained on every device.

## Supported training approaches

The registry can describe from-scratch training, continued pretraining, supervised fine-tuning, LoRA, teacher-student distillation, preference optimization, multimodal fine-tuning, and evaluation-only runs. A listed method is a supported workflow category, not evidence that a particular model has completed that training.

## Model routing

Buddy routes only models with:
- an immutable model and dataset lineage
- verified dataset rights and model-license evidence
- a separate training authorization and training-run record
- a content-addressed weight artifact
- held-out capability benchmarks, regression checks, provenance verification, and independent review
- a production-verified lifecycle state and an explicit route policy

If no model passes every gate, the registry returns `BLOCKED_NO_ELIGIBLE_MODEL`. The tiny-GPT baseline is intentionally registered as untrained, has no weight artifact, is not route-enabled, and is not eligible for sale.

## Marketplace and sale eligibility

The registry defines sale eligibility but does not implement checkout, payment processing, or model delivery. Sale remains disabled until a future marketplace release has verified ownership, dataset and model licenses, training authorization, immutable weights, benchmark evidence, security review, model card, export format, and human release approval.

A model's parameter count or training completion alone never makes it sellable. A user may buy only a model with rights and release evidence appropriate to the intended commercial use.

## Current implementation status

- Model registry and read-only routing gate: implemented in this PR.
- User-defined parameter-count policy and compute-feasibility contract: implemented as policy; hardware-specific estimator remains a separate implementation task.
- TinyGPT reference: a small CPU baseline, not a trained language model.
- Model marketplace checkout and delivery: not implemented.
- No claim is made that the model network is trained, production-ready, or generating revenue.
