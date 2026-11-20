# Buddy Repository Repair, Data Foundations, Benchmarks and Distillation

## 1. What each data component does

- **Dataset:** a curated, versioned collection of examples or records. A repository repair dataset might contain the failure context, root cause, patch summary, tests that proved the fix, and the final result. It needs a dataset card, provenance, license/consent status, schema, quality checks, version, and split manifest.
- **Database:** the operational system that stores and retrieves records. DreamCo's Dataset Hub uses SQLite for its local catalog and content-addressed objects for dataset files. The database tracks dataset cards, source candidates, ownership, routes, versions, hashes, jobs, and incident history. A database is not itself a training dataset.
- **Benchmark:** a controlled exam used to measure a model. A benchmark contains task prompts, expected outcomes or graders, scoring rules, and a fixed evaluation split. Keep private test/holdout examples out of training. Report baseline and candidate results under the same conditions.
- **Training run:** the reproducible process that consumes an approved dataset and a pinned base-model revision, then produces a checkpoint/adapter and logs. A queued job or config is not proof that training executed.
- **Distillation:** a teacher-student process. A capable teacher solves curated tasks and produces target answers, explanations, tool traces or preference comparisons. A smaller student learns to reproduce the desired behavior. Evaluate the student against the teacher and independent baselines; do not copy teacher weights.

## 2. How I can teach Buddy

I can act as a teacher at the task and example level, not by handing Buddy my underlying model weights. A practical pipeline:

1. Define a capability curriculum for Buddy and each MasterBot: coding, debugging, data engineering, reasoning, tool use, security, documentation and domain-specific tasks.
2. Create rights-cleared prompts and cases from DreamCo-owned code, verified PRs, tests, incident fixes, original documentation, and approved public/licensed sources.
3. Ask the teacher model to solve each task under a fixed tool and context contract. Save the prompt, teacher answer, concise explanation, observable tool calls/results, expected artifact, and evaluator result. Do not store hidden chain-of-thought; train on concise explanations, observable steps and verifiable outputs.
4. Have a deterministic grader and/or human reviewer verify the answer. Reject hallucinated commands, fabricated evidence, insecure code and unverified claims.
5. Deduplicate and normalize examples; attach source/license/provenance; remove secrets and personal data; split by project/time/source so near-duplicates cannot leak from train into test.
6. Train a student model or LoRA adapter only after data rights, base-model license, compute budget and dataset approval pass.
7. Compare the student with its own baseline, the teacher, and suitable open-weight models on the same frozen benchmark.
8. Promote only when quality, safety, reliability, latency and cost meet the acceptance thresholds. Keep the prior model and rollback path.

Teacher outputs are not automatically correct or automatically licensed for every training use. Each teacher-generated dataset needs documented terms and review. Using ChatGPT as teacher does not transfer OpenAI model weights or grant ownership of the teacher model.

## 3. Training the whole Buddy project

Treat Buddy as a family of evaluated capabilities rather than one giant undifferentiated dataset:

- **Foundation student:** general instruction following, coding, reasoning, math, tool-use and safe behavior.
- **MasterBot specialists:** a primary dataset lane per canonical MasterBot, with cross-lane shared examples only when permissions and ownership allow.
- **Adapters:** LoRA/QLoRA modules for high-value specialist gaps when retrieval and better tools are insufficient.
- **Retrieval corpora:** current facts, code, manuals, policies and source material. Retrieval can update knowledge without changing model weights.
- **Tool policies:** validated procedures for GitHub, databases, testing, CAD, deployment and research.
- **Evaluation suites:** public development sets plus private holdouts that are never placed into training.

A sensible order is retrieval + tools + tests first, then supervised fine-tuning, then LoRA/QLoRA if benchmarks show a measurable gap. Continued pretraining or full fine-tuning needs stronger rights, data and compute justification. Training from scratch is a separate, expensive research program.

## 4. Repository failure learning

Buddy's failure specialist uses:
- a stable fingerprint to group recurring failures;
- a failure class and canonical MasterBot route;
- a verified root cause and minimal repair;
- original failing check plus targeted and dependent regression evidence;
- recurrence count and a reusable verified lesson.

Current routing defaults:
- DreamCodeLab (41): code, formatting, generated artifacts and general repository repair;
- DreamQuality (63): deterministic fixtures, tests and quality gates;
- DreamData (7): datasets, ETL and data quality;
- DreamAIInfra (4): dependencies, build infrastructure and deployment systems;
- DreamCyber (24) with DreamSecurity (56): security, secrets and permission failures;
- DreamBenchmark (47): model and benchmark regressions;
- DreamKnowledge (48): documentation and knowledge-base failures;
- DreamDiscovery (62): unknown failure classes pending triage.

These are routing defaults, not a claim that the whole 65-to-45 division mapping is finalized.

A retry is not a repair. Do not turn an unverified fix into training data. The failure-learning module requires original failure and regression success, human review, explicit training permission, and affirmative exclusion of secrets and personal data before it can emit a candidate example. Candidate examples remain NOT TRAINING APPROVED until dataset-card and rights review.

## 5. GitHub Actions operating policy

GitHub Actions now includes a scheduled failure detector and a separate safe-repair worker:
- Buddy Failure Detection and Learning polls completed workflow runs every 15 minutes, groups recurring failures by fingerprint, and creates/updates canonical incident issues.
- Buddy Safe Repository Repair polls eligible incident issues every 30 minutes and runs only exact allowlisted deterministic artifact rebuilds (currently the DreamCo dataset-route index or division-model fleet generator) in an isolated branch.
- If tracked generated artifacts change, it opens a repair PR. It does not merge that PR.
- All other failure classes remain in the diagnosis queue for a specialist MasterBot and human-reviewed repair.

The general operating policy is:
- detect failed workflows and preserve incident evidence;
- run reproducible diagnostics and targeted tests;
- apply only narrowly allowlisted, deterministic repairs in an isolated branch;
- open a PR with the diff, original failure, regression results and rollback notes;
- rerun the original failed check and dependent checks;
- record a lesson only after verification.

Actions must not silently change security policy, permissions, billing, migrations, production data, deployment credentials, model weights or test expectations. Those require human review. A green badge is not enough if a test was skipped, weakened or removed.

## 6. Current implementation truth

Implemented in this repository branch: Dataset Hub local catalog and candidate routing, metadata discovery adapters, conservative license triage, training-job request validation, model benchmark scaffolding, failure fingerprint/classification, MasterBot routing and verified-lesson candidate gates.

Not yet proven by these definitions: production-grade shared object storage, exhaustive internet dataset discovery, every external connector, continuous GPU training, production model-weight updates, general-purpose autonomous code repair beyond the two allowlisted artifact rebuilds, or mastered specialist models. GitHub Actions run results and actual training artifacts must establish those facts.
