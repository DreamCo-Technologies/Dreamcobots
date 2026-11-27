# Buddy Bootcamp: Hugging Face, Ollama & Open-Model Training Academy

**Status:** curriculum proposal; not a claim that training jobs, datasets, weights, or model adapters have been executed or produced.  
**Owner:** DreamCo Buddy / Bootcamp  
**Purpose:** convert authoritative open-source AI learning resources into original, measurable Buddy courses.

## 1. Operating principles

Buddy must distinguish five different kinds of learning:

1. **Retrieval / RAG:** index permitted material and retrieve it at answer time. No model weights change.
2. **Prompt or policy improvement:** revise instructions, routing rules, tool schemas, or workflows and evaluate them. No model weights change.
3. **Supervised fine-tuning (SFT):** train model parameters or adapters on approved examples.
4. **Preference / reward optimization:** DPO, ORPO, KTO, GRPO or related methods, only with a valid preference/reward signal and a safe evaluation environment.
5. **Inference / deployment:** serve a model. This is not training.

Ollama is primarily a local model runner and packaging/deployment path, not a general-purpose trainer. Train with a compatible training stack (for example, Transformers + PEFT/TRL, Unsloth, Axolotl, torchtune or MLX), then export or package compatible artifacts for inference. Verify adapter/base-model compatibility before importing.

## 2. Five-minute learning-control loop

A five-minute cadence should mean **queue and health orchestration**, not blindly launching a new weight-training run every five minutes.

Every five minutes, when infrastructure is available:
- poll the training/evaluation queue and job status;
- check resource budgets, GPU availability, storage, rate limits and provider status;
- detect newly changed/approved sources and enqueue only incremental ingestion;
- validate dataset provenance, license, consent, schema, duplication and contamination;
- select at most one bounded eligible micro-job per available worker;
- checkpoint safely and record dataset hash, code revision, base-model revision, adapter/checkpoint ID, hardware, seed, hyperparameters, cost and metrics;
- run smoke evaluation before promoting any candidate;
- compare against the frozen baseline and holdout set;
- stop on OOM, runaway cost, safety regression, corrupted data, or evaluation regression.

Do **not**:
- retrain from scratch every five minutes;
- train on every discovered web page or model card;
- train on locked benchmark answers or evaluation prompts;
- assume downloaded weights are trained by DreamCo;
- promote a checkpoint without repeatable holdout and regression evidence;
- run jobs when compute budget, hardware or dataset rights are unknown.

Suggested cadence:
- **Every 5 minutes:** orchestration, queue polling, freshness deltas, job health and bounded micro-batches.
- **Hourly:** targeted small evaluations and adapter-training only when an approved queue item is ready.
- **Daily:** source review, course generation, data-quality checks and curriculum updates.
- **Weekly:** deeper benchmark, transfer, regression and cost-efficiency review.

A schedule is not proof of execution. Every run needs a verifiable job ID, logs, checkpoint or adapter artifact, evaluation report and provenance record.

## 3. Course catalogue

Each course should generate: learning objectives, prerequisites, original lessons, worked examples, sandbox lab, quiz, practical assignment, answer rubric, benchmark mapping, held-out transfer task, safety notes and completion evidence.

### Course 01 — Open-model engineering foundations
- **Learn:** model vs dataset vs tokenizer vs inference server vs trainer; base vs instruct; parameters, context, quantization, checkpoints and adapters.
- **Resources:** Hugging Face Hub https://huggingface.co/docs ; Transformers https://huggingface.co/docs/transformers ; Ollama docs https://docs.ollama.com/ .
- **Lab:** inspect one model card and one dataset card; identify architecture, license, intended use, context, quantization, supported inference/training paths.
- **Pass:** produce a correct model readiness manifest; no unsupported capability claims.

### Course 02 — Hugging Face Hub, model cards and dataset cards
- **Learn:** discover models, datasets and Spaces; inspect files, revisions, tags, licenses, intended uses and limitations.
- **Resources:** Hub https://huggingface.co/docs/hub ; model cards https://huggingface.co/docs/hub/model-cards ; dataset cards https://huggingface.co/docs/hub/datasets-cards ; Spaces https://huggingface.co/docs/hub/spaces .
- **Lab:** curate five candidate models and five datasets; compare provenance and access terms.
- **Pass:** all entries include pinned revision, license status, source link and risk notes.

### Course 03 — Datasets, data pipelines and provenance
- **Learn:** loading, streaming, filtering, deduplication, splits, schema validation, data lineage and contamination prevention.
- **Resources:** Datasets https://huggingface.co/docs/datasets ; Dataset Viewer https://huggingface.co/docs/dataset-viewer ; Data Studio https://huggingface.co/docs/hub/datasets-data-studio .
- **Lab:** create a small versioned JSONL dataset with train/validation/test splits and duplicate checks.
- **Pass:** reproducible dataset build with hashes, source records and no train/test overlap.

### Course 04 — Tokenizers and chat templates
- **Learn:** tokenization, special tokens, truncation, padding, chat templates and label masking.
- **Resources:** Tokenizers https://huggingface.co/docs/tokenizers ; chat templating https://huggingface.co/docs/transformers/chat_templating .
- **Lab:** encode/decode the same conversation using two compatible tokenizer/template pairs; inspect truncation and masked labels.
- **Pass:** dataset examples render exactly as intended and pass schema/template tests.

### Course 05 — Transformers training fundamentals
- **Learn:** forward/backward pass, loss, optimizer, scheduler, gradient accumulation, mixed precision, checkpoints and reproducibility.
- **Resources:** Transformers https://huggingface.co/docs/transformers ; Accelerate https://huggingface.co/docs/accelerate .
- **Lab:** run a tiny baseline training job on a toy dataset; record loss curve, seed, hardware and runtime.
- **Pass:** rerun produces explainable, bounded variance and a loadable checkpoint.

### Course 06 — Parameter-efficient fine-tuning: LoRA and QLoRA
- **Learn:** low-rank adapters, target modules, rank/alpha/dropout, quantization, memory tradeoffs and adapter merging.
- **Resources:** PEFT https://huggingface.co/docs/peft ; bitsandbytes https://huggingface.co/docs/bitsandbytes ; Unsloth tutorials https://unsloth.ai/docs/models/tutorials .
- **Lab:** fine-tune a small compatible instruct model with LoRA/QLoRA on a permissioned toy dataset; compare base vs adapter.
- **Pass:** measurable holdout improvement without violating safety or general capability guardrails.

### Course 07 — Supervised fine-tuning with TRL
- **Learn:** SFTTrainer, conversational datasets, packing, loss masks, eval strategy and checkpoint selection.
- **Resources:** TRL https://huggingface.co/docs/trl ; SFTTrainer https://huggingface.co/docs/trl/sft_trainer ; Unsloth integration https://huggingface.co/docs/trl/unsloth_integration .
- **Lab:** build a small instruction-following adapter and evaluate on unseen prompts.
- **Pass:** reproducible baseline comparison, held-out score and error analysis.

### Course 08 — Preference optimization and reward learning
- **Learn:** preference pairs, DPO, ORPO, KTO, reward models, GRPO, reward hacking and policy constraints.
- **Resources:** TRL https://huggingface.co/docs/trl ; Axolotl https://docs.axolotl.ai/ .
- **Lab:** use a tiny synthetic preference set; compare SFT-only with one preference method.
- **Pass:** improvement on a predeclared preference evaluation with no material safety or factuality regression. No online RL against uncontrolled external systems.

### Course 09 — Efficient training recipes and experiment management
- **Learn:** configuration-driven runs, memory profiling, gradient checkpointing, distributed training, resumability and experiment tracking.
- **Resources:** Axolotl https://docs.axolotl.ai/ ; torchtune https://meta-pytorch.org/torchtune/stable/ ; Accelerate https://huggingface.co/docs/accelerate ; Weights & Biases docs https://docs.wandb.ai/ .
- **Lab:** reproduce a documented recipe from a pinned config; profile memory and compare one safe optimization.
- **Pass:** exact config, environment, logs and artifact are archived.

### Course 10 — Local inference with Ollama
- **Learn:** pull/run models, model tags, context settings, Modelfile, API, structured output, tool calling and local serving.
- **Resources:** Ollama docs https://docs.ollama.com/ ; Modelfile https://docs.ollama.com/modelfile ; API https://docs.ollama.com/api ; model library https://ollama.com/library .
- **Lab:** serve a small model locally; benchmark latency, memory, throughput and tool-call correctness.
- **Pass:** repeatable inference benchmark and documented model/runtime version.

### Course 11 — Exporting and serving trained models locally
- **Learn:** adapter compatibility, merge/export, GGUF conversion, quantization tradeoffs and runtime parity.
- **Resources:** llama.cpp https://github.com/ggml-org/llama.cpp ; Ollama import/create https://docs.ollama.com/import ; Hugging Face GGUF https://huggingface.co/docs/hub/gguf .
- **Lab:** export a compatible fine-tuned artifact and compare its outputs with the original training checkpoint.
- **Pass:** documented parity test, quantization impact and rollback path.

### Course 12 — Evaluation, benchmarks and regression
- **Learn:** task-specific metrics, exact-match vs rubric scoring, contamination, calibration, confidence intervals, judge reliability and benchmark versioning.
- **Resources:** Evaluate https://huggingface.co/docs/evaluate ; LightEval https://github.com/huggingface/lighteval ; lm-evaluation-harness https://github.com/EleutherAI/lm-evaluation-harness ; Inspect AI https://inspect.aisi.org.uk/ .
- **Lab:** build a small benchmark with frozen baseline, hidden holdout, repeated runs and regression gate.
- **Pass:** evaluation can be rerun by another worker and yields the same decision.

### Course 13 — Multimodal and vision-language models
- **Learn:** image-text inputs, video sampling, OCR, grounding, modality-specific preprocessing and evaluation.
- **Resources:** Transformers vision https://huggingface.co/docs/transformers/tasks/image_text_to_text ; SmolVLM https://huggingface.co/docs/transformers/model_doc/smolvlm ; datasets https://huggingface.co/docs/datasets .
- **Lab:** evaluate a small vision-language model on a permissioned image set with object/attribute questions and adversarial lighting/crop cases.
- **Pass:** per-category metrics, failure examples and privacy review.

### Course 14 — Robotics and embodied AI with LeRobot
- **Learn:** robot datasets, observation/action spaces, camera calibration, imitation learning, policy training, simulation and safety.
- **Resources:** LeRobot https://huggingface.co/docs/lerobot ; LeRobot repository https://github.com/huggingface/lerobot ; SmolVLA https://huggingface.co/docs/lerobot/main/smolvla .
- **Lab:** train/evaluate a policy on an existing public dataset or simulator before attempting physical hardware.
- **Pass:** held-out simulation success, safety constraints and full dataset/model provenance.

### Course 15 — Small-model and edge training
- **Learn:** hardware-aware model selection, memory budgets, quantization, Apple MLX, CPU/GPU backends and distillation.
- **Resources:** MLX https://ml-explore.github.io/mlx/build/html/index.html ; llama.cpp https://github.com/ggml-org/llama.cpp ; Unsloth requirements https://unsloth.ai/docs/get-started/fine-tuning-for-beginners/unsloth-requirements .
- **Lab:** benchmark a small model on available hardware; measure peak RAM/VRAM, tokens/sec and task quality.
- **Pass:** select the best model under a stated quality/latency/cost budget.

### Course 16 — Distillation and teacher/student learning
- **Learn:** teacher-generated examples, soft targets, filtering, diversity, student capacity, data leakage and transfer evaluation.
- **Resources:** Transformers https://huggingface.co/docs/transformers ; TRL https://huggingface.co/docs/trl ; torchtune https://meta-pytorch.org/torchtune/stable/ .
- **Lab:** create a small teacher/student dataset using original or permitted tasks; compare student before/after.
- **Pass:** independent holdout improvement, not merely teacher-style imitation.

### Course 17 — Agent tool use and safe execution
- **Learn:** tool schemas, permissions, action confirmation, sandboxing, audit logs, prompt injection and least privilege.
- **Resources:** Hugging Face Agents Course https://huggingface.co/learn/agents-course ; MCP specification https://modelcontextprotocol.io/specification ; Inspect AI https://inspect.aisi.org.uk/ .
- **Lab:** implement a read-only agent, then a separately permissioned sandbox action; test hostile tool outputs.
- **Pass:** policy tests prove untrusted source text cannot grant permissions or bypass approvals.

### Course 18 — Production training operations and cost control
- **Learn:** job queues, worker leases, retries, idempotency, checkpoints, quotas, secrets, observability and rollback.
- **Resources:** Hugging Face Jobs https://huggingface.co/docs/huggingface_hub/guides/jobs ; Docker docs https://docs.docker.com/ ; Kubernetes Jobs https://kubernetes.io/docs/concepts/workloads/controllers/job/ .
- **Lab:** orchestrate a bounded test job with timeout, budget cap, cancellation and artifact verification.
- **Pass:** job can be resumed/cancelled safely and leaves auditable evidence.

## 4. Additional source library to ingest and map to lessons

| Resource | Use in Buddy Bootcamp |
|---|---|
| Hugging Face Learn https://huggingface.co/learn | Structured beginner-to-advanced courses |
| Hugging Face Course https://huggingface.co/learn/nlp-course | NLP/Transformers fundamentals |
| Hugging Face Agents Course https://huggingface.co/learn/agents-course | Agent design and tool use |
| Hugging Face Robotics / LeRobot https://huggingface.co/lerobot | Embodied AI datasets and policies |
| Hugging Face Hub https://huggingface.co/ | Model, dataset and Space discovery |
| Transformers https://github.com/huggingface/transformers | Model architectures and inference/training APIs |
| Datasets https://github.com/huggingface/datasets | Data loading and processing |
| Tokenizers https://github.com/huggingface/tokenizers | Fast tokenizer implementation |
| PEFT https://github.com/huggingface/peft | Adapter fine-tuning |
| TRL https://github.com/huggingface/trl | SFT and preference/RL post-training |
| Accelerate https://github.com/huggingface/accelerate | Distributed and hardware-aware execution |
| Evaluate https://github.com/huggingface/evaluate | Metric evaluation |
| Unsloth https://github.com/unslothai/unsloth | Efficient local fine-tuning |
| Axolotl https://github.com/axolotl-ai-cloud/axolotl | Config-driven fine-tuning and multimodal training |
| torchtune https://github.com/meta-pytorch/torchtune | Hackable PyTorch training recipes |
| LLaMA-Factory https://github.com/hiyouga/LLaMA-Factory | Broad fine-tuning workflows and UI |
| MLX https://github.com/ml-explore/mlx | Apple Silicon machine learning |
| MLX-LM https://github.com/ml-explore/mlx-lm | LLM inference and fine-tuning on Apple Silicon |
| llama.cpp https://github.com/ggml-org/llama.cpp | Local inference and GGUF conversion |
| Ollama https://github.com/ollama/ollama | Local model execution and packaging |
| vLLM https://github.com/vllm-project/vllm | High-throughput model serving |
| OpenRLHF https://github.com/OpenRLHF/OpenRLHF | Distributed RLHF workflows |
| DeepSpeed https://github.com/deepspeedai/DeepSpeed | Distributed and memory-efficient training |
| PyTorch tutorials https://pytorch.org/tutorials/ | Core deep-learning foundations |
| fast.ai https://course.fast.ai/ | Practical deep learning course |
| MIT OpenCourseWare https://ocw.mit.edu/ | Math, CS and ML foundations |
| Stanford CS229 https://cs229.stanford.edu/ | Machine learning foundations |
| Stanford CS224N https://web.stanford.edu/class/cs224n/ | NLP foundations |
| Stanford CS231N https://cs231n.stanford.edu/ | Computer vision foundations |
| Full Stack Deep Learning https://fullstackdeeplearning.com/ | End-to-end AI product engineering |
| Made With ML https://madewithml.com/ | Production ML engineering |
| Berkeley BAIR https://bair.berkeley.edu/ | Robotics and AI research |
| Open X-Embodiment https://robotics-transformer-x.github.io/ | Robot demonstration data and generalist policies |
| LIBERO benchmark https://libero-project.github.io/ | Simulation benchmark for robot learning |
| MuJoCo https://mujoco.org/ | Physics simulation |
| NVIDIA Isaac Lab https://isaac-sim.github.io/IsaacLab/ | Robotics simulation and policy learning |
| OpenAI Spinning Up https://spinningup.openai.com/ | RL concepts and algorithms |

These are candidate sources, not a claim that every project is compatible with every model, license, device or training method. Re-check official docs and current support matrices before selecting a recipe.

## 5. Bootcamp course object contract

Each generated course should have a stable ID and version and include:

- `course_id`, `title`, `version`, `owner`, `status`
- `objectives[]`, `prerequisites[]`, `estimated_time`, `difficulty`
- `resources[]`: URL, publisher, source type, revision/date, license/access notes, allowed uses, evidence level
- `lessons[]`: original explanations, key concepts, worked examples and knowledge checks
- `labs[]`: setup, safe environment, instructions, expected artifacts and cleanup
- `assignments[]`: tasks, constraints, test fixtures and rubric
- `benchmark`: baseline, validation, locked holdout, transfer and regression suites
- `completion_gate`: numeric thresholds, repeat count, safety gates and evidence links
- `provenance`: dataset hashes, model revision, code revision, citations and transformations
- `compute_policy`: approved hardware, maximum runtime, maximum spend and cancellation conditions

Course completion means demonstrated skill on unseen tasks; reading or finishing lessons alone does not award mastery.

## 6. Training-data and content-rights gates

- Publicly viewable does not mean licensed for training, copying, redistribution or commercial resale.
- Store source metadata and permitted references; create original explanations and exercises.
- Respect model and dataset licenses, attribution, terms, privacy, consent and deletion requests.
- Keep personal memory, retrieval indexes and model-training datasets separate.
- Do not ingest private repositories, user conversations, credentials or personal data into training without explicit authorization and a documented purpose.
- Keep evaluation holdouts separate from training data.
- Record why each dataset is permitted for the exact intended use.

## 7. First implementation sequence

1. Inventory the existing DreamCo resource registry and Bootcamp course schemas; reuse existing IDs and avoid duplicate catalogs.
2. Add the resource records above with canonical URLs, source types and provenance status.
3. Generate course manifests from the source-to-capability mapping.
4. Build original lessons and labs incrementally, starting with Courses 01–06.
5. Add one small, reproducible LoRA experiment using an explicitly licensed dataset and a model that fits the available compute.
6. Add baseline/holdout/regression evaluations before any adapter is promoted.
7. Connect the job queue to a real worker and artifact store; test cancellation, checkpoint resume, spend caps and logs.
8. Add Ollama only as a deployment/inference target after compatibility checks.
9. Expand to multimodal/robotics courses after simulation and dataset governance are working.

## 8. Evidence required before saying “Buddy trained”

A run is complete only when all are recorded:
- training job ID and terminal status;
- exact base model ID and pinned revision;
- dataset ID, pinned revision, license/provenance decision and dataset hash;
- training code/config revision and environment;
- start/end times, hardware, runtime and cost;
- checkpoint/adapter artifact identifier and integrity hash;
- baseline and post-training metrics;
- independent holdout, transfer and regression results;
- safety review and promotion/rollback decision.

No checkpoint, no evaluation, no training claim.
