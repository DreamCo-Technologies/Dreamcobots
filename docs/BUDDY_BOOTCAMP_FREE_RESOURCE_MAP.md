# Buddy Bootcamp: Free Learning and Research Resource Map

**Status:** initial curated resource map; not a claim that all resources have been ingested, rights-cleared, or turned into lessons.  
**Purpose:** build a DreamCo-owned curriculum in original wording, backed by source links, exercises, reproducible labs, and explicit data-use permissions.

## Model discovery, datasets and model training

| Resource | Best use | Access / caution |
|---|---|---|
| Hugging Face Hub — https://huggingface.co/ | Discover models, datasets, Spaces and model cards | Each model/dataset has its own license and terms; inspect before use |
| Hugging Face Transformers — https://huggingface.co/docs/transformers | Tokenizers, model loading, inference and architecture concepts | Free documentation; checkpoint rights remain separate |
| Hugging Face Datasets — https://huggingface.co/docs/datasets | Dataset loading, processing and streaming | Check each dataset's license, provenance and privacy |
| Hugging Face PEFT — https://huggingface.co/docs/peft | LoRA and parameter-efficient adaptation | Free open-source tooling; model license still applies |
| Hugging Face TRL — https://huggingface.co/docs/trl | SFT, preference optimization and knowledge distillation | Includes DistillationTrainer, GKD and asynchronous distillation documentation; verify installed version/API |
| Hugging Face TRL community tutorials — https://huggingface.co/docs/trl/community_tutorials | Practical community-led training tutorials | Community quality varies; check deprecations and reproducibility |
| Unsloth — https://docs.unsloth.ai/ | Memory-efficient fine-tuning and training workflows | Hardware, model, notebook and license constraints vary |
| MLX / mlx-lm — https://github.com/ml-explore/mlx and https://github.com/ml-explore/mlx-lm | Apple Silicon local ML and model fine-tuning | Open-source tools; benchmark on actual hardware |
| Axolotl — https://docs.axolotl.ai/ | Config-driven fine-tuning workflows | Check hardware requirements and model support |
| torchtune — https://pytorch.org/torchtune/ | Readable PyTorch recipes for LLM post-training | Open-source framework |
| LlamaFactory — https://github.com/hiyouga/LLaMA-Factory | Fine-tuning workflows and UI | Verify current version, supported model and license |
| vLLM — https://docs.vllm.ai/ | High-throughput model serving and evaluation infrastructure | Serving framework, not a dataset license |
| llama.cpp — https://github.com/ggml-org/llama.cpp | Local inference and quantized model deployment | Model license still applies |
| OpenRLHF — https://github.com/OpenRLHF/OpenRLHF | Distributed RLHF/post-training research | Advanced; requires careful safety and compute controls |

## Free foundational computer science and AI courses

| Resource | Best use |
|---|---|
| freeCodeCamp — https://www.freecodecamp.org/ and https://www.youtube.com/@freecodecamp | Full courses, coding projects and transcripts/captions where available |
| Harvard CS50 — https://cs50.harvard.edu/ | Computer science foundations and problem sets |
| MIT OpenCourseWare — https://ocw.mit.edu/ | Mathematics, algorithms, systems and AI course materials |
| Stanford CS229 — https://cs229.stanford.edu/ | Machine learning theory and evaluation |
| Stanford Engineering Everywhere — https://see.stanford.edu/ | Free engineering and computer science course material |
| fast.ai — https://course.fast.ai/ | Practical deep learning with hands-on projects |
| Dive into Deep Learning — https://d2l.ai/ | Open interactive deep-learning textbook |
| Kaggle Learn — https://www.kaggle.com/learn | Short practical lessons in Python, SQL, data and ML |
| Google Machine Learning Crash Course — https://developers.google.com/machine-learning/crash-course | ML concepts, exercises and responsible AI |
| Microsoft Learn — https://learn.microsoft.com/training/ | Cloud, AI, security, data and software development |
| GitHub Skills — https://skills.github.com/ | Git, GitHub and collaborative development |
| The Missing Semester — https://missing.csail.mit.edu/ | Shell, editors, version control and developer tooling |

## Datasets and reproducible experiments

- UCI Machine Learning Repository — https://archive.ics.uci.edu/
- OpenML — https://www.openml.org/
- Hugging Face Datasets — https://huggingface.co/datasets
- Kaggle Datasets — https://www.kaggle.com/datasets
- Google Dataset Search — https://datasetsearch.research.google.com/
- Papers with Code — https://paperswithcode.com/ (paper/task/benchmark discovery; verify dataset and code terms)
- MLCommons — https://mlcommons.org/ (benchmark standards and evaluation context)

A dataset being downloadable does not mean it is approved for commercial training. Preserve dataset-level license, attribution, privacy, consent, collection and withdrawal metadata.

## Software engineering, data, security and deployment

- The Odin Project — https://www.theodinproject.com/
- Full Stack Open — https://fullstackopen.com/en/
- MDN Web Docs — https://developer.mozilla.org/
- Python official tutorial — https://docs.python.org/3/tutorial/
- PostgreSQL tutorial — https://www.postgresql.org/docs/current/tutorial.html
- Docker Get Started — https://docs.docker.com/get-started/
- Kubernetes tutorials — https://kubernetes.io/docs/tutorials/
- OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
- OWASP Web Security Testing Guide — https://owasp.org/www-project-web-security-testing-guide/
- NIST AI Risk Management Framework — https://www.nist.gov/itl/ai-risk-management-framework
- OpenTelemetry documentation — https://opentelemetry.io/docs/
- FastAPI tutorial — https://fastapi.tiangolo.com/tutorial/
- SQLBolt — https://sqlbolt.com/

## Occupation and business knowledge

- O*NET — https://www.onetonline.org/ and https://www.onetcenter.org/database.html
- U.S. Bureau of Labor Statistics Occupational Outlook Handbook — https://www.bls.gov/ooh/
- U.S. Small Business Administration learning resources — https://www.sba.gov/
- SCORE mentoring and small-business learning — https://www.score.org/
- U.S. Census Bureau data — https://www.census.gov/data.html
- Data.gov — https://data.gov/

Occupation and business resources must be mapped to specific job tasks, local regulations, safety constraints and domain benchmarks. O*NET is an occupation taxonomy and task resource, not a substitute for professional licensing, clinical guidance or current legal requirements.

## Transcript and course-material workflow

For every video/course:
1. Save source URL, title, creator, publication date, duration and topic.
2. Retrieve captions/transcripts only through permitted mechanisms and record their source and terms.
3. Record transcript availability separately from metadata-only catalog entries.
4. Extract concepts and timestamps; create an original explanation rather than copying the transcript.
5. Link each statement to its source; distinguish facts, interpretation and uncertainty.
6. Add original exercises, answer keys, projects and machine-checkable tests.
7. Map lesson to Bootcamp level, occupation/division, prerequisite and relevant model capability.
8. Review accessibility, technical accuracy, version freshness and license.
9. Keep "study/summarize allowed" separate from "use as training data allowed".
10. Track discovered, cataloged, transcript-available, summarized, rights-reviewed, training-approved and actually-used counts independently.

## DreamCo lesson format

Every lesson should include:
- title, level, prerequisites and estimated effort;
- learning objectives and key vocabulary;
- original explanation in DreamCo's own words;
- citations/source links and source/license metadata;
- diagrams or worked examples where useful;
- hands-on lab and expected output;
- exercises, tests and scoring rubric;
- common failure modes and remediation;
- occupation/division and model-capability mappings;
- accessibility and localization notes;
- evidence of review and last verification date.

## Non-negotiable safeguards

- Never treat free access as permission to copy, redistribute or train.
- Never ingest private, sensitive or customer data without a documented lawful basis and the required consent.
- Never include secrets, credentials or raw personal identifiers in lesson examples or training sets.
- Keep benchmark test sets held out from training and teacher-generated synthetic data.
- Preserve attribution and source lineage; honor license restrictions and removal/withdrawal obligations.
- Do not claim a model learned from a resource unless a documented training run actually used approved data and produced an evaluated checkpoint.

## Tokenizer and language-model course references

Buddy's original tokenizer study guide links to [Hugging Face Tokenizers](https://huggingface.co/docs/tokenizers), the [Hugging Face NLP Course tokenizer chapter](https://huggingface.co/learn/nlp-course/chapter6/1), [SentencePiece](https://github.com/google/sentencepiece), and freeCodeCamp's [Train Your Own LLM](https://www.youtube.com/watch?v=9Ge0sMm65jo). These are study references, not blanket permission to reproduce course materials, download captions, or train on third-party text. The corresponding original 12-lesson syllabus is `config/buddy-tokenizer-training-curriculum.json`.


## CPU-first 25M-class LLM and modern GLM architecture course

- [freeCodeCamp 25M CPU LLM course article](https://www.freecodecamp.org/news/build-and-train-a-25m-parameter-llm-from-scratch-on-your-cpu/)
- [freeCodeCamp YouTube: GLM-5.3-Flash from scratch](https://www.youtube.com/watch?v=-gfgQfw2g_E)
- [Expanded GLM-5.3-Flash course article](https://www.freecodecamp.org/news/build-and-train-a-glm-53-flash-model-from-scratch-with-python/)
- Original DreamCo syllabus: `config/buddy-25m-cpu-llm-course.json`; detailed guide: `docs/BUDDY_25M_CPU_LLM_STUDY_GUIDE.md`.

The 18-module path covers byte-level tokenization, embeddings, exact parameter counting, residual/hyperconnection paths, RMSNorm, RoPE/NoPE, linear and sparse attention, MoE/shared experts, vision patches, pretraining, data interleaving, sandboxed code reinforcement learning, reward design/GRPO, parameter-efficient updates, hyperparameter experiments, multi-seed statistical evaluation, regressions and rollback. It is shared with all 55 canonical divisions and 65 MasterBot lanes; specialist ownership follows the reviewed crosswalk. The course/video are references only, not permission to ingest transcripts or use third-party text as training data.

## O*NET full content-model curriculum

The full worker, job and market taxonomy plus task-by-task AI suitability rules are defined in `config/buddy-onet-content-model-curriculum.json` and `docs/BUDDY_ONET_FULL_CONTENT_MODEL_AND_TASK_PLAYBOOKS.md`. It covers worker characteristics, skills, knowledge, abilities, education, experience, licensing, work activities, work context, technology/tools and workforce outlook. Each task is classified individually; O*NET coverage is not proof an AI can perform every occupation.

## All official Hugging Face Learn courses

Buddy's current 12-course Hugging Face Learn inventory is tracked in `config/buddy-huggingface-full-learning-map.json` and is linked from the shared course scheduler. It covers LLMs, context engineering, robotics, compact post-training, agents, Deep RL, computer vision, audio, open-source AI recipes, games, diffusion and 3D. The map is refreshed against [huggingface.co/learn](https://huggingface.co/learn); the Deep RL course is flagged low-maintenance where upstream challenge/leaderboard features are retired or nonfunctional. Eighteen original ecosystem modules and all 37 task families are also mapped.

## FreeCodeCamp full video queue and interactive curriculum inventory

The shared course scheduler exposes every video ID in the checked-in freeCodeCamp metadata catalog to all 55 canonical divisions and 65 MasterBot lanes. The legacy snapshot currently contains 1,740 records and is explicitly **partial** (`inventory.complete=false`); the count is dynamic and must be refreshed from the official uploads playlist. A scheduled metadata-only workflow now verifies playlist-count/unique-ID equality and opens a review PR; it never pushes directly to main. The interactive curriculum's 37 superblocks, 38 chapters, 217 modules, 779 unique blocks and 14,038 challenges are a dated inventory snapshot and require an upstream refresh before any full-coverage claim. Lesson content, tests and transcripts remain rights-gated and must be individually verified.
