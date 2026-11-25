# DreamCo multi-source study, transcript and model-building program

## Goal

Run a continuous, evidence-driven learning cycle for all 55 domain divisions, mapped across the 65-MasterBot fleet (including 20 shared-platform MasterBots), using these source families:

1. **GitHub repositories** — primary source code, READMEs, tests, notebooks, releases and immutable revisions, subject to license review.
2. **Hugging Face** — dataset/model/Space discovery, task metadata, cards, licenses, gated terms, benchmarks and approved training assets.
3. **freeCodeCamp** — course/video discovery, official learning links and item-level transcript permissions.
4. **O*NET and official workforce sources** — occupation/task definitions and task-to-skill study paths.
5. **Official procurement and public-service sources** — government sales, grants, contracting and community-service learning with eligibility and human-review safeguards.
6. **Ollama** — local model execution, model packaging/import, reproducible inference and evaluation of locally available models.
7. **User-owned data** — separately registered and used only under the user's purpose-specific consent.

The runtime policy is `config/buddy-continuous-study-policy.json`. It schedules work 24/7 but must pause when there is no authorized content, no available compute, a budget cap is reached, or a required evaluator is unavailable. It must not spin endlessly or incur unapproved paid costs.

## What “all transcripts” means

The FreeCodeCamp inventory is a catalog of public video metadata, not a transcript corpus. The current catalog workflow has verified 1,741 metadata entries, but it has not downloaded video, audio or captions. A public video page or caption track is not blanket permission to download, retain, transform, redistribute or train on it.

The transcript pipeline must:
- discover transcript candidates and their canonical source URLs;
- record source owner, license/terms, territory or scope where relevant, and the exact permitted uses;
- require item-level rights evidence before transcript retrieval or retention;
- distinguish permission for evaluation, internal study-guide derivation, redistribution and model training;
- hash and version every authorized transcript;
- block missing, ambiguous, revoked or incompatible permissions;
- retain only the minimum content needed for the approved purpose;
- create original explanations, exercises, code labs and quizzes rather than republishing course transcripts.

**Do not scrape captions, bypass access controls, or use yt-dlp to download transcript/media payloads as a workaround.** If a source offers an official transcript API/export or an explicit open license, use that route and record the evidence. If not, keep the source as a link-only study reference until authorization is obtained.

## Continuous daily study schedule

- All 55 domain divisions receive five candidate lesson slots each day: 275 planned domain-lesson slots/day. The 65-MasterBot fleet is mapped to those curricula through the crosswalk; unresolved or unapproved ownership mappings do not receive privileged routing or training assignments.
- Buddy diagnoses each division's benchmark gaps and prerequisites before choosing material.
- The study worker prioritizes high expected learning gain per minute and rotates fairly across divisions.
- A lesson moves through source review, study-guide generation, sandbox exercise, targeted test, unseen holdout, regression and evidence ledger.
- Unmastered topics return to the queue with spaced-retrieval intervals of 1, 3, 7, 14 and 30 days.
- A division is not marked mastered from reading or summarization alone. The policy requires repeated independent passes, a separate holdout and passing regression tests.
- Failed evaluations are retained as failures and drive targeted remediation; they are never converted into passes.
- The scheduler runs when permitted work exists; it does not mean a single machine should run at 100% CPU/GPU around the clock.

## Hugging Face workflow

For each candidate dataset or model:
1. Discover by task, language, domain, modality, recency and benchmark relevance.
2. Capture repository ID, immutable revision/commit, dataset card/model card, license identifier, license URL, authorship, citation, gated status, splits, schema/features and data provenance.
3. Treat a missing or vague license as `UNKNOWN` and block ingestion for training.
4. Review gated access terms and account-specific restrictions separately.
5. Scan for PII, secrets, unsafe code, contamination and benchmark leakage.
6. Create a reproducible dataset manifest with hashes and split boundaries.
7. Keep train, validation, test and holdout splits isolated; never train on the holdout.
8. Generate original division study guides and tasks only from content whose permitted use includes that derivation.
9. Record every training/evaluation run and its exact model, tokenizer, dataset revisions and configuration.

Hugging Face dataset cards expose important provenance and metadata such as license, language, task categories and dataset features, but a card is a review input—not a substitute for reading the actual license and terms. See the official [Dataset Cards guide](https://huggingface.co/docs/hub/en/datasets-cards), [dataset information endpoint](https://huggingface.co/docs/dataset-viewer/info) and [dataset upload guidance](https://huggingface.co/docs/hub/en/datasets-adding).

## Ollama workflow

Ollama is a local model runtime and packaging/deployment layer, not a substitute for the training pipeline. For each candidate model:
- record model name, exact digest/revision, upstream owner, base model, license, quantization and architecture;
- review base-model and adapter licenses independently;
- test inference locally against division-specific benchmark suites;
- import supported Safetensors or GGUF weights/adapters using a versioned Modelfile;
- ensure a LoRA adapter is paired with the exact base model it was trained against;
- record prompt template, system prompt, context settings, runtime version, hardware, latency, memory and output quality;
- do not use model outputs as training data unless provider/model terms and a separate approval permit it.

Official references: [Ollama model import](https://ollama.readthedocs.io/en/import/), [Modelfile reference](https://github.com/ollama/ollama/blob/main/docs/modelfile.mdx) and [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md).

## 45-million-parameter division-model track

The freeCodeCamp tutorial currently located for small-model construction is titled **Build and Train a 25M Parameter LLM From Scratch on Your CPU** (October 8, 2026), not 45M. Use its educational sequence as the baseline, then scale the configuration to a measured 45,000,000-parameter target. The tutorial describes a compact byte-level vocabulary, modern decoder architecture, pretraining, and a code-execution reward loop. A separate freeCodeCamp course on training an LLM covers data loading, BPE tokenization, transformer architecture, pretraining, supervised fine-tuning and LoRA.

Per division, the proposed research path is:

1. **Define task scope** — capabilities, exclusions, user impact, domain vocabulary and measurable benchmarks.
2. **Build the data inventory** — only authorized, high-quality and diverse corpora; remove duplicates and contamination; document provenance.
3. **Train tokenizer** — compare byte-level and BPE approaches; freeze and hash tokenizer before training.
4. **Specify model** — decoder-only transformer configuration with explicit context length, vocabulary, layers, attention heads, hidden width, normalization, positional encoding and tied/untied embeddings.
5. **Count parameters** — calculate exact trainable parameter count from the instantiated model; tune architecture until the measured count is near 45M, and record the exact count rather than assuming a label.
6. **Pretrain** — causal next-token objective, AdamW or justified optimizer, learning-rate schedule, gradient clipping, checkpointing, train/validation loss and reproducible seeds.
7. **Instruction tune** — use separately authorized instruction-response data; keep a clean evaluation holdout.
8. **Preference/reward experiments** — begin with deterministic unit-test rewards for code and task completion; only add RL methods after stable supervised baselines and reward-hacking tests exist.
9. **Evaluate** — domain knowledge, reasoning, coding/task execution, calibration, safety, robustness, latency, memory and cost; compare against fixed baselines and previous Buddy versions.
10. **Package for Ollama** — export supported weights/adapters, validate conversion, create a Modelfile, run smoke tests and preserve hashes.
11. **Promote cautiously** — no division model becomes production default without holdout and regression passes, owner approval, model card and rollback checkpoint.

A 45M model is a useful compact research model, not a frontier GPT-5 system. Reaching similar behavior cannot be inferred from parameter count. It requires independent evidence across capability, reliability, safety and scale.

### One shared engine, 65 MasterBot model targets

Keep one tested training codebase and architecture generator. Generate 55 domain-division curriculum configurations from the canonical 55-domain registry. Separately, generate up to 65 MasterBot model blueprints from the canonical 65-MasterBot registry, then connect them to domain curricula only through reviewed crosswalk entries. Do not treat 65 MasterBots as 65 domain divisions. Do not silently share training data across divisions: each corpus item must be rights-cleared and routed under its approved scope. If compute is constrained, first train and validate one representative pilot; scale to the remaining divisions only after measured cost, throughput and quality justify it. Division adapters may be compared with independent full models, but do not claim they are equivalent.

## Original Buddy Bootcamp course factory

Each authorized source item can produce an original course package:
- learning objectives and prerequisites;
- concise concept map and glossary;
- original explanation with cited source links;
- worked examples and runnable code;
- exercises with deterministic tests;
- mini-project and rubric;
- knowledge checks and spaced-retrieval cards;
- division-specific benchmark and unseen holdout;
- answer key and remediation path;
- provenance, rights evidence and content hashes.

Never copy a full transcript or course lesson into a DreamCo course. Preserve attribution and link learners to the original course. Use the template at `buddy/bootcamp/templates/study-guide-template.md`.

## Current verified state and blockers

- FreeCodeCamp: 1,741 metadata entries were verified in a CI discovery artifact; that is not 1,741 transcripts.
- Transcript manifest: currently empty; no transcript payloads have been approved or evaluated.
- Buddy transcript inference adapter: not yet registered.
- Hugging Face: existing taxonomy/capability discovery map covers 65 MasterBots, but entries are discovery-only and training approval is false by default.
- Ollama: this plan specifies local inference/import workflow; it does not claim Ollama is installed, connected or running on a user's machine.
- Training: no 45M model weights have been trained by this change. Compute, dataset rights, training runtime and measured evaluation are still prerequisites.

## Source curriculum references

- freeCodeCamp, [Build and Train a 25M Parameter LLM From Scratch on Your CPU](https://www.freecodecamp.org/news/build-and-train-a-25m-parameter-llm-from-scratch-on-your-cpu//)
- freeCodeCamp, [Create a Large Language Model from Scratch with Python](https://www.youtube.com/watch?v=UU1WVnMk4E8)
- freeCodeCamp, [Train Your Own LLM](https://www.youtube.com/watch?v=9Ge0sMm65jo)
- freeCodeCamp, [GLM-5.3-Flash model architecture and training course](https://www.youtube.com/watch?v=-gfgQfw2g_E)


## Implemented adapter and architecture details

The technology radar now includes a Hugging Face Datasets API discovery source in addition to model listings, preserving a bounded metadata allowlist (license label, language, task categories, size categories, gated flag, downloads, likes, revision timestamp and tags). Every discovery record is explicitly marked `UNVERIFIED_DISCOVERY_ONLY` and `training_approved: false`. Dataset-card metadata is a triage signal; the actual license, repository terms, provenance and intended use still require review. CI tests the metadata extraction using fixtures; the connected Hugging Face search service may rate-limit requests, so refresh failures must preserve the last good catalog.

The Ollama adapter is `buddy.learning.ollama_runtime.OllamaLocalRuntime`. It accepts only local loopback HTTP endpoints, lists models, inspects model metadata and runs non-streaming chat inference. It deliberately does not expose pull, create, delete or push operations. Its output records prompt/response hashes, latency and token counters without claiming training. Tests use a mocked local API; a green test is not proof that Ollama is installed or running on the user's device.

### Reference 45M-class architecture blueprint

The architecture generator `tools/build_division_45m_model_blueprints.py` builds one design-only configuration per canonical MasterBot. The reference configuration is:
- 384 hidden width, 19 decoder blocks, 6 attention heads (64 dimensions/head)
- 1,536 SwiGLU intermediate width, 512-token vocabulary and 1,024-token context
- fused Q/K/V plus output projection, RoPE, pre-norm RMSNorm, no linear biases
- tied token embeddings and language-model head

For this explicit no-bias architecture, the count is:

`vocab × hidden + layers × (4 × hidden² + 3 × hidden × intermediate + 2 × hidden) + hidden`

That yields **45,038,208 trainable parameters** per blueprint, about 45.038M. The generator validates all 65 MasterBot IDs and writes a JSON blueprint artifact. This is an architecture calculation—not a trained model, not a 45M weight file, and not evidence of GPT-5-level capability. The output intentionally leaves tokenizer/weight hashes and authorized dataset manifests empty and sets training approval false.

The separate Ollama and blueprint workflows validate the adapter contract and exact parameter arithmetic. They do not incur GPU charges or start a training run.


## User-designated summary library integration

Every approved source guide is converted into the `dreamco.buddy_learning_package.v1` format by `tools/organize_buddy_learning_assets.py`. The package retains the original source revision, rights evidence and attribution, extracts the best knowledge, and includes a sequenced study path, examples, exercises, answer key, knowledge checks, capstone and spaced review. The user is recorded as the designated owner of original DreamCo-authored instructional expression, subject to applicable law, contributor agreements and upstream license terms; third-party materials remain owned by their respective rightsholders.

The adapter `buddy.learning.dreamco_summary_source` routes eligible packages into the existing `buddy.learning.study_resource_scheduler`. It validates canonical division and asset IDs, source revisions and rights before returning a study plan. Progress events are append-only and evidence-linked; model-training events additionally require the package's explicit asset-level training permission. A package is queued, not studied, until Buddy completes the learning activity and evidence is recorded. Mastery requires independent assessment and capstone evidence.

The current source rights manifest and user-data manifest are empty. Therefore the pipeline correctly produces an empty or partial approved-guide library until sources and user data are individually authorized and guides are completed and reviewed. This is not a claim that 1,000 summaries, every Hugging Face artifact, or all transcripts already exist.

## Canonical tokenizer course integration

The tokenizer stage now has a 12-lesson Buddy course: [Buddy Tokenizer Engineering and Training Course](../../docs/BUDDY_TOKENIZER_TRAINING_STUDY_GUIDE.md), with its syllabus at `config/buddy-tokenizer-training-curriculum.json`. Map the lessons to the 55 division curricula and 65 MasterBot lanes through the existing reviewed ownership crosswalk. Relevant lanes include Hugging Face Tokenizers, Transformers, model architecture, data quality, evaluation and model release. Keep the course references link-only unless the exact source grants additional rights. The curriculum's mastery gate requires exercises, reproducibility, independent held-out evaluation and model/tokenizer compatibility checks.

