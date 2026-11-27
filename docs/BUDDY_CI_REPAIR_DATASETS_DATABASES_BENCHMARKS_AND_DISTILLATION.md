# Buddy CI Repair, Data Foundations, Benchmarks and Teacher Distillation

## 1. CI repair: what GitHub Actions does now

The branch contains two separate workflows:

- `.github/workflows/buddy-failure-learning-regression.yml` runs the failure-classification and verified-lesson tests.
- `.github/workflows/buddy-ci-safe-repair.yml` regenerates a fixed allowlist of deterministic DreamCo indexes and registries on non-main branches, runs their validators and targeted tests, and pushes only verified generated outputs back to that same branch when changes exist.

The safe repair allowlist currently includes the Buddy dataset routes, 65-MasterBot model fleet, Pages connection index, Actions prospectus and repository file prospectus. It does not rewrite arbitrary application code, dependency versions, permissions, security controls, migrations, billing, or production configuration. Those require a diagnosed repair plan and review. A retry is not a repair.

The existing Actions failure sweep/watch workflows capture run and job metadata. The Buddy failure-learning module fingerprints failures, classifies likely causes, retrieves verified lessons, and blocks promotion of unverified fixes. A lesson is reusable only after the original failing check and regression checks pass.

## 2. Dataset, database and benchmark definitions

- **Dataset:** a versioned collection of examples with a schema, provenance, license/rights evidence, privacy review, quality checks, and fixed train/validation/test splits. Example: verified DreamCo bug reports paired with the accepted fix and regression test.
- **Operational database:** stores current product state—users, bots, tasks, permissions, queues, runs and approvals. It is not automatically training data.
- **Dataset catalog/database:** stores dataset cards, versions, source references, hashes, ownership, rights status, quality reports, split manifests and MasterBot routes.
- **Object store:** holds approved immutable dataset files and model artifacts addressed by content hash.
- **Vector/search index:** helps retrieve relevant docs, code, examples and lessons at runtime. Retrieval improves access to knowledge without changing model weights.
- **Benchmark:** a fixed, repeatable test set and scoring procedure that measures whether a model can perform a task. Benchmarks are held out from training and include expected outputs, tool-success criteria, safety checks and versioned scoring rules.

Buddy should keep operational records, learning knowledge, training datasets, benchmark holdouts and model artifacts logically separated. A database record is not automatically suitable for training.

## 3. How to distill the Buddy project with ChatGPT as teacher

Treat Buddy as a collection of capabilities, not one giant prompt or one undifferentiated dataset.

1. **Inventory the curriculum.** Convert each canonical MasterBot/division capability into task families: code changes, repository diagnosis, data routing, SQL, tool use, research, planning, safety, testing, and domain-specific workflows.
2. **Collect authorized source evidence.** Use DreamCo-owned code, documentation, tests, issues, approved PRs, CI results and human-reviewed operating procedures. Record the exact source commit/version, rights, privacy status and owner lane.
3. **Build teacher examples.** I can help create instruction/answer pairs, structured plans, code patches, SQL examples, tool-selection examples, test cases, rubric scores, and explanations of why a proposed solution passes or fails. Each example should point to source evidence and acceptance tests. We can generate original practice scenarios from real failure patterns without copying secrets or personal data.
4. **Capture observable behavior, not hidden internals.** The teacher dataset can contain the prompt, answer, concise rationale, structured plan, tool calls/results that are authorized to retain, expected artifacts and verification result. I cannot export hidden chain-of-thought, private model weights, internal activations or proprietary teacher logits through this chat.
5. **Quality-control and split.** Deduplicate; validate code and SQL in sandboxes; label difficulty and capability; check rights and privacy; detect benchmark contamination; then create immutable train, validation and private test splits. Keep the private test split out of all training and model selection.
6. **Train students.** Start with a license-compatible open-weight base model. Establish a baseline. Apply supervised fine-tuning (SFT) and, when justified, LoRA/QLoRA adapters. Preference optimization can use reviewed better/worse answer pairs. Distillation from teacher probability distributions requires a teacher interface that actually exposes those distributions; ordinary chat answers support response-level distillation, not logit-level distillation.
7. **Benchmark every candidate.** Compare the untouched base model, retrieval/tool-enhanced baseline, fine-tuned student and teacher reference on identical held-out tasks. Track task success, exactness, test pass rate, tool correctness, safety, latency, throughput, memory and cost.
8. **Promote only with evidence.** A student remains experimental until it beats the relevant baseline without unacceptable regressions, passes safety/holdout tests, has a model card and reproducible training manifest, and receives independent approval.

## 4. Shared core plus specialist models

Use a shared Buddy core for routing, planning, safety, common coding/reasoning patterns and tool contracts. Give each MasterBot its own curated domain dataset, retrieval namespace, adapter/checkpoint where useful, benchmark suite, private holdout and model card. Cross-lane examples can be shared only when their rights and scope permit it. Do not create 65 separately trained weights merely to satisfy a count; train or adapt a specialist when measured evidence justifies the cost.

## 5. What “learn from a failure” means

A failure should produce a sanitized signature, exact workflow/job/step, commit, reproduction instructions, root-cause hypotheses, minimal repair, tests, and final verification. The successful repair becomes a reusable lesson only after the original failure and regressions pass. Keep raw secrets and unnecessary private logs out of the learning corpus.

## 6. Current limits and next engineering gates

- GitHub Actions currently has a bounded auto-repair lane for deterministic generated artifacts only. It is not a general AI coding agent and does not yet automatically rewrite arbitrary failing application code.
- The latest PR checks must finish before any claim that the new workflows or generated repairs pass. Queued, pending, cancelled and skipped are not successful test results.
- Scheduled GitHub Actions are best-effort automation, not guaranteed 24/7 compute.
- Model training requires rights-cleared data, available compute, reproducible manifests, isolated holdouts, cost limits and explicit approval. No production model weights are changed automatically.
- A full production platform still needs durable shared storage, backups, secrets management, connector scopes, job orchestration, training workers, artifact registry, benchmark service and operator review.

