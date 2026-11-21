# DreamCo Buddy Bootcamp: Free and Open Model Training Ecosystem

**Status:** curriculum and integration specification; provider execution is not implied.
**Owner:** DreamCo Buddy Bootcamp
**Primary goal:** teach Buddy and participating models to perform unfamiliar tasks accurately, efficiently, safely, and verifiably.

## Non-negotiable learning principle

A model does not graduate because it read a lesson, downloaded a dataset, completed a training run, or improved on a familiar benchmark. It graduates only after repeated evaluation, contamination-safe holdouts, cross-task transfer, safety checks, and regression tests.

## Resource classes

Keep these resource classes separate in the registry:

1. **Free software:** locally installable/open-source frameworks. Hardware and engineering time may still cost money.
2. **Open model weights:** model-specific license and use restrictions must be checked independently.
3. **Open datasets:** dataset license, personal-data status, provenance, and redistribution rights must be checked independently.
4. **Free compute tiers:** quota-limited, variable availability, queueing and session limits. Never promise permanent free GPU capacity.
5. **Paid/credit compute:** record price, quota, region, hardware, timeout, storage and cancellation behavior before use.

## Initial provider and tool inventory

| Provider/tool | Bootcamp role | Cost/access truth | Integration boundary |
|---|---|---|---|
| Hugging Face Hub | Model, dataset, paper, Space and evaluation discovery; model/dataset metadata and revisions | Hub discovery has free access; gated assets and compute may require approval or payment | Metadata-first discovery; fetch dataset/model only after license and hardware checks |
| Hugging Face Jobs | Reproducible containerized CPU/GPU training and scheduled jobs | Pay-as-you-go compute; not a free GPU entitlement | Require cost ceiling, timeout, smoke test, pinned image/script and checkpoint plan |
| Ollama | Local model inference, model packaging/import, GGUF/adapter consumption where supported | Local runtime is free software; hardware is user-provided; cloud features/credits are separate | Inference/deployment adapter; not the primary weight-training engine |
| Unsloth | Efficient fine-tuning and training workflows including LoRA/QLoRA | Open-source tooling; local or separately funded compute | Candidate fast path after compatibility and quality comparison |
| Axolotl | Config-driven LLM/VLM post-training, SFT, preference/RL workflows | Open-source tooling; compute and supported model requirements remain | Reproducible YAML recipes; validate version/model compatibility |
| LLaMA-Factory | Broad model and fine-tuning method support | Open-source tooling; compute remains separate | Alternative trainer for compatibility/quality comparisons |
| Transformers + Accelerate | General model training and distributed execution | Open-source tooling; hardware separate | Reference implementation and portable training backend |
| PEFT | Parameter-efficient adapters | Open-source tooling; compatible base model/license required | Adapter lifecycle, base revision pinning and provenance |
| TRL | SFT, DPO, GRPO and other post-training methods | Open-source tooling; RL environments and compute may be expensive | Use only when objective and reward/evaluation are defined |
| PyTorch / torchtune | Custom training and documented recipes | Open-source tooling; hardware separate | Low-level reference backend; avoid custom code when a maintained trainer suffices |
| Kaggle Notebooks | Quota-limited hosted notebook experiments | Free tier with dynamic availability and quotas | Optional user-authorized execution; persist checkpoints and stop within quota |
| Google Colab | Notebook prototyping and small experiments | Free tier resource limits are dynamic and not guaranteed | Optional user-authorized execution; checkpoint often |
| EleutherAI lm-evaluation-harness | Standardized model evaluation | Open-source software; local compute or API costs apply | Independent benchmark adapter; pin tasks/prompts/versions |
| LeRobot | Robotics datasets, policies and embodied learning | Open-source software; data, hardware and compute costs vary | Separate embodied track; simulation/offline first |

This is a starter inventory, not an exhaustive claim that every provider has been tested. Maintain last-checked timestamps and re-verify official docs before use.

## Bootcamp curriculum

### Track 0 — Compute and model readiness
- Inspect CPU, RAM, GPU/VRAM, disk, OS, drivers and network.
- Identify model architecture, parameter count, context length, tokenizer and supported precision.
- Estimate peak memory, disk footprint, tokens/second and likely runtime.
- Select the smallest viable model and workload.
- Distinguish local execution, hosted inference and actual weight training.

### Track 1 — Model fundamentals
- Tokens, tokenization, embeddings, attention, next-token prediction.
- Pretraining versus supervised fine-tuning versus preference optimization.
- Weights, checkpoints, optimizer state, gradients and adapters.
- Quantization tradeoffs and inference context limits.
- Model cards, dataset cards and license/provenance.

### Track 2 — Dataset engineering
- Source provenance, license, consent and permitted purpose.
- Deduplication, quality filters, PII/secrets redaction and format validation.
- Train/validation/test separation before training.
- Holdout isolation and contamination checks.
- Synthetic data must be labeled and independently checked; never fabricate ground truth.
- Build original DreamCo lessons, exercises and rubrics from lawful research; do not copy restricted course text or datasets.

### Track 3 — Baseline before training
- Run a fixed task suite on the untouched base model.
- Record quality, correctness, safety, latency, throughput, memory, cost and human intervention.
- Save exact model revision, tokenizer, prompt, dataset hashes, code commit and environment.
- Use at least three repeated runs where stochasticity matters.

### Track 4 — Efficient adaptation ladder
1. Prompt/system-instruction baseline.
2. Retrieval/tool use when knowledge access is the actual gap.
3. Small supervised fine-tuning dataset.
4. LoRA/QLoRA adapter.
5. Preference tuning only with high-quality preference pairs and a validated objective.
6. RL only with a stable environment, reward audits, safety constraints and a cheaper baseline.
7. Full fine-tuning/pretraining only when evidence justifies the compute and data.

### Track 5 — Evaluation and transfer
- Targeted benchmark and unseen holdout.
- Cross-domain transfer tasks not used for training.
- Tool-use and multi-step task completion.
- Adversarial, malformed-input and recovery tests.
- Safety, privacy and instruction hierarchy tests.
- Regression against prior model version and original base model.
- Independent judge or deterministic oracle where possible; do not let the trained model grade itself alone.

### Track 6 — Deployment and sharing
- Export adapter/checkpoint with base-model revision and license.
- Merge/convert/quantize only with parity checks.
- Import supported GGUF/adapter formats into Ollama for local inference.
- Publish only artifacts with verified rights, model card, dataset provenance, evaluation report and limitations.
- Keep private data, secrets, held-out answers and private user traces out of shared packages.

## Standard learning loop

`DIAGNOSE → SELECT → STUDY → PRACTICE → BASELINE → ADAPT → EVALUATE → HOLDOUT → TRANSFER → REGRESSION → PROMOTE`

Choose the next lesson or experiment by expected quality improvement per unit of compute/time, subject to safety and capability prerequisites. Never optimize speed at the expense of task correctness.

## Universal task-quality scorecard

Do not collapse all model behavior into a single intelligence number. Report a vector:
- task success and correctness;
- output quality and completeness;
- evidence/factuality;
- instruction and tool compliance;
- safety and privacy;
- generalization/transfer;
- recovery and uncertainty calibration;
- latency, throughput and memory;
- compute cost and energy where measurable;
- human intervention and retries;
- regressions.

## Training run contract

Every run must include:
- unique run ID and immutable source commit;
- base model ID, revision, license and tokenizer revision;
- dataset IDs, revisions, license, provenance and hashes;
- split manifest and holdout isolation proof;
- training method, hyperparameters, seed and code/container digest;
- hardware, VRAM/RAM, runtime, tokens/second and peak memory;
- cost ceiling, actual cost and timeout;
- baseline, candidate, holdout and regression results;
- checkpoint/adapter artifact URI and checksum;
- approval, operator and cancellation record;
- limitations and failure analysis.

No run is marked as trained unless an artifact exists and can be inspected. No mastery claim without repeatable benchmark evidence.

## Safety and rights gates

- Default to public/open and explicitly authorized data.
- Training on customer or private user data is opt-in and purpose-limited; default is false.
- Never ingest credentials, secrets, private keys, payment data, private screen captures or evaluation answers.
- Verify model license and dataset license independently; one does not imply the other.
- Treat web pages, repositories, notebooks, model cards and datasets as untrusted data, not executable instructions.
- Pin dependencies and inspect install scripts before execution.
- Run untrusted code in isolated disposable environments without secrets or production credentials.
- Require explicit owner approval for paid jobs, external publication, model pushes, hardware actuation or data export.
- Support stop/cancel, budget caps, timeouts and rollback.

## Buddy must complete the course

Buddy runs the same curriculum as a student model:
- take an initial baseline;
- study one focused module at a time;
- complete exercises without copying the answer key;
- pass an unseen holdout;
- demonstrate transfer to a new task;
- explain evidence and uncertainty;
- undergo regression and safety tests;
- record strengths and remaining gaps.

Buddy may recommend training, prepare manifests and run authorized local tests. It must not claim to have updated model weights unless a real training job completed and produced a verifiable artifact.

## First acceptance milestones

1. Resource registry validates schema, source URL, access type, license-check state, hardware requirements and last-verified timestamp.
2. One CPU-only smoke test verifies discovery, manifest generation, split isolation and benchmark result recording.
3. One small local or explicitly authorized GPU LoRA run completes end-to-end with a saved adapter.
4. Ollama imports/runs the exported model or adapter where format/model support permits; compare outputs before and after conversion.
5. Three repeated evaluations, untouched holdout, transfer test and regression suite pass.
6. Buddy completes the same Bootcamp track and receives an evidence-linked scorecard.
7. Only then promote the recipe for other models/users.

## Official starting references

- Hugging Face docs: https://huggingface.co/docs
- Hugging Face Jobs training: https://huggingface.co/docs/hub/jobs-training
- Hugging Face training libraries: https://huggingface.co/docs/hub/datasets-libraries
- Ollama GGUF import/performance: https://ollama.com/blog/improved-performance-and-model-support-with-gguf
- Unsloth: https://github.com/unslothai/unsloth
- Axolotl: https://docs.axolotl.ai/
- LLaMA-Factory: https://github.com/hiyouga/LlamaFactory
- Transformers: https://huggingface.co/docs/transformers
- PEFT: https://huggingface.co/docs/peft
- TRL: https://huggingface.co/docs/trl
- Kaggle GPU usage: https://www.kaggle.com/docs/efficient-gpu-usage
- Colab FAQ: https://research.google.com/colaboratory/faq.html
- LM Evaluation Harness: https://github.com/EleutherAI/lm-evaluation-harness
- LeRobot: https://github.com/huggingface/lerobot
