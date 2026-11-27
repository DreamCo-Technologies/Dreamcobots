# DreamCo Institute: 100-Resource Foundry & Bootcamp Reference Library

## Purpose
This curated library maps 100 external resources across ten domains. Buddy studies them to understand taxonomies, curricula, architecture patterns, training methods, inference, data engineering, robotics, evaluation and MLOps, then independently authors DreamCo blueprints, lessons, synthetic exercises and tests.

**This is not a list of 100 datasets cleared for training.** Every entry starts NOT_REVIEWED with training permission UNKNOWN_BLOCKED. Inclusion does not authorize downloads, training, fine-tuning, redistribution or commercial repackaging.

## Ten bootcamp tracks
1. Workforce, task and economic taxonomies: O*NET, ESCO, BLS, NOC, ISCO-08, NICE, DOT, MIT Work of the Future, WEF, Schema.org.
2. Interactive engineering and curriculum: freeCodeCamp, The Odin Project, Exercism, CS50, MIT OCW, OSSU, Full Stack Open, roadmap.sh, NeetCode/LeetCode, Project Euler.
3. Model hubs and architectures: Hugging Face, OLMo, EleutherAI, PyTorch Hub, ONNX Model Zoo, Papers With Code, OpenMMLab, Kaggle, ModelScope, GitHub Models.
4. Pretraining and synthetic pedagogy: Cosmopedia, FineWeb-Edu, OpenAssistant, The Stack v2, OpenStax, GSM8K, MATH, UltraFeedback, CodeAlpaca/Evol-Instruct, Wikimedia dumps.
5. Training and alignment: Transformers, TRL, PEFT, Accelerate, nanoGPT, LitGPT, Axolotl, Unsloth, DeepSpeed, PyTorch Lightning.
6. Local inference and edge: Ollama, llama.cpp, ONNX Runtime, ExecuTorch, WebLLM/MLC, vLLM, LM Studio, LocalAI, GPT4All, TensorRT-LLM.
7. Data parsing and clean-room tooling: DataTrove, MinHash/datasketch, Tree-sitter, Docling, Unstructured, Instructor, Outlines, Faster-Whisper, Pandoc, Presidio.
8. Robotics and simulation: ROS 2, LeRobot, Isaac Lab, MuJoCo, Gazebo, PyBullet, Gymnasium, MoveIt 2, Webots, PX4/MAVSDK.
9. Benchmarking and trust: LM Evaluation Harness, EvalPlus/HumanEval, IFEval, SWE-bench, Promptfoo, Garak, Evaluate, Pydantic, pytest, Mutmut.
10. MLOps and delivery: GitHub Actions, DVC, W&B/MLflow, Docker, FastAPI, Qdrant/ChromaDB, SQLite/PostgreSQL, SafeTensors, Ruff, CycloneDX/Syft.

## How Buddy learns from each source
- Record purpose, scope, exact version/revision, official docs and source.
- Study abstract concepts, interface contracts, task patterns and evaluation methods.
- Review license, terms, attribution, privacy, patent and model/dataset restrictions before any content acquisition.
- Independently author DreamCo explanations, architecture specifications, labs, synthetic examples, tests and implementation notes.
- Keep third-party artifacts and excerpts separate from DreamCo-authored materials.
- Record revision IDs, hashes, provenance and reviewer decisions; unknown rights always BLOCK.
- Keep benchmark answer keys out of training and preserve independent private holdouts.

## Required lesson artifact
Each resource becomes a Buddy Bootcamp lesson with objectives, prerequisites, concepts, original explanation, hands-on lab, deterministic tests, rights/security exercise, Human/Robot/AI work-routing exercise where applicable, independent holdout, rubric, source provenance, reviewer sign-off and mastery evidence.

## Relationship to quarantined intake
The existing `scripts/buddy_resource_harvester.py` and `config/buddy-resource-sources.json` remain the offline intake path. This external catalog contains URLs and research metadata, not approved local files. Never auto-convert entries into training-approved source declarations. After exact revision and rights review, an approved local snapshot may be declared in the source manifest and staged to quarantine. Quarantine is not training approval.

## Can Buddy compete with these resources?
Buddy is DreamCo's orchestration, learning, routing, governance and evidence layer. These resources are specialist curricula, datasets, frameworks, runtimes, simulators and evaluators. Buddy should integrate and orchestrate them, not claim it already replaces all of them. Competitive parity must be demonstrated capability-by-capability with working adapters, original labs, reproducible tests, versioned evidence and independently verified outcomes. A catalog entry is not proof of implementation or mastery.

## Validation
```bash
python -m unittest tests.test_dreamco_foundry_reference_library -v
```


## All 65 DreamCo divisions are Learning Divisions

The ten categories above are shared foundational resource collections, **not** the division structure. DreamCo's canonical registry contains 65 MasterBot divisions, and every one is a full Learning Division with its own curriculum, research, teaching, practicum, assessment, remediation, certification and continuous-improvement loop.

Every division must maintain:
- Foundations, domain knowledge, tools/workflows, applied projects, safety/quality, advanced practice and teaching tracks.
- Approved, division-relevant sources plus shared foundational references; unknown rights remain blocked.
- Original lessons, hands-on labs, division-specific deterministic tests and independent holdouts.
- A skill-gap and remediation queue, with retesting after remediation.
- Evidence-backed mastery records, reviewer sign-off and versioned learning history.
- Human/Robot/AI task-routing exercises appropriate to its domain.

Buddy coordinates shared learning and cross-division collaboration, while each MasterBot retains ownership of its own curriculum, tests and mastery evidence. Course completion alone never means mastery.
