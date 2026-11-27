# Buddy Distillation Excellence Standard

**Status:** proposed engineering standard; implementation and benchmark evidence are not yet established.  
**Goal:** make Buddy an exceptionally capable teacher, evaluator, and distillation orchestrator while allowing approved external teacher models whenever they outperform Buddy on a task.

## Product principle

Buddy is the learning orchestrator, not a mandatory single source of truth. It may teach directly, consult one or more approved teacher models, compare their answers, use tools and authoritative references to verify claims, and produce a rights-cleared training target for a student model. A teacher is selected by measured task performance, not brand, parameter count, or confidence.

## Distillation pipeline

1. **Define the capability.** Specify task, user, domain, allowed actions, safety boundaries, target latency/cost, and measurable acceptance tests.
2. **Establish a baseline.** Evaluate the student and candidate teachers on a frozen, representative, held-out suite before collecting training examples.
3. **Select teachers per task.** Compare Buddy, approved open-weight models, and permitted API teachers. Record exact model/version, license or terms, access mode, cost, latency, context limits, and evaluation results.
4. **Use multi-teacher review when valuable.** Route independent answers to specialist teachers; use a verifier or evidence-based adjudicator to resolve disagreement. Preserve disagreement and uncertainty rather than averaging incompatible claims. A teacher ensemble is optional, not automatically better.
5. **Generate traceable examples.** Store prompt/task, teacher identity and version, response, tool/evidence references, quality scores, safety labels, reviewer decisions, and rights/provenance. Separate teacher-generated synthetic data from human-authored and public-source data.
6. **Filter and curate.** Deduplicate; detect leakage, PII, unsafe instructions, hallucinations, low-quality reasoning, and benchmark contamination. Keep rejected examples and reasons in audit metadata, not training sets.
7. **Choose the right learning method.** Use supervised fine-tuning for high-quality demonstrations; preference optimization for valid comparisons; logit/soft-target distillation only when teacher weights or supported logits are legitimately available; on-policy or online distillation when the teacher can evaluate student-generated outputs; tool-use training for verified tool trajectories; adapters/LoRA for domain specialization. Do not pretend black-box text outputs provide logits.
8. **Train in an isolated, reproducible run.** Pin dataset versions, model revisions, tokenizer/chat template, code, config, seed, hardware, optimizer, hyperparameters, and resource budget. Save checkpoint hashes and intermediate metrics.
9. **Evaluate independently.** Compare student to its own baseline and relevant teacher(s) on held-out domain tasks, adversarial and safety tests, calibration, factuality, tool correctness, latency, memory, and cost. Repeat across seeds where practical.
10. **Promote cautiously.** Require predeclared acceptance thresholds, no critical safety regression, reproducibility, model card, lineage, rollback checkpoint, and explicit approval for production deployment.

## Teacher selection and governance

- Buddy is eligible to teach only on tasks where current evaluations show it is sufficiently reliable.
- External teachers are allowed when their model license, provider terms, privacy rules, and data-use terms permit the intended use.
- Open weights do not automatically mean unrestricted training, redistribution, or commercial use. Check the exact model license and acceptable-use terms.
- API output rights and retention/training terms vary by provider and plan. Record them before use.
- Never route confidential customer data to an external teacher unless that customer's configuration and the provider's terms explicitly permit it.
- Use least-privilege credentials, per-tenant data boundaries, redaction, retention controls, and auditable routing.
- Do not train on copyrighted course transcripts, videos, books, or datasets merely because they are publicly viewable or free to study. Respect licenses, platform terms, consent, attribution, and applicable law.
- A source may be studied or summarized without being approved as model-training data. Track these permissions separately.

## Quality system

Maintain separate scores for:
- factual correctness and citation support;
- task completion and executable correctness;
- reasoning/step validity where it can be independently checked;
- safety and policy compliance;
- robustness to paraphrase and distribution shift;
- calibration and appropriate abstention;
- latency, memory, compute and per-task cost;
- teacher/student disagreement and verifier confidence.

Never optimize only for imitation of the teacher. The student should be rewarded for independently verified correctness, not reproducing teacher errors or stylistic quirks.

## Required registries and evidence

- Teacher registry: model/provider, version, license/terms, allowed data classes, supported modalities, costs, latency, evaluation evidence.
- Student registry: base model, tokenizer, adapter/checkpoint hashes, intended domain, deployment targets, lineage.
- Dataset registry: source, owner, license/terms, consent, collection date, transformations, PII review, splits, exclusions, retention and withdrawal path.
- Experiment ledger: run ID, code commit, configuration, seed, compute, costs, metrics, artifacts, reviewer and promotion decision.
- Benchmark registry: task definitions, frozen test sets, scoring rules, contamination checks and historical comparisons.
- Distillation lineage: every student checkpoint traces to teachers, data, transformations, training run and evaluation.

## Bootcamp lessons and labs

1. Teacher/student concepts; parameters versus logits versus generated text.
2. Evaluation before training; build a frozen baseline suite.
3. Dataset rights, provenance, privacy, deduplication and leakage.
4. High-quality teacher demonstrations and supervised fine-tuning.
5. Multi-teacher routing, disagreement analysis and evidence-based adjudication.
6. Preference data and preference optimization.
7. Logit-based versus black-box distillation.
8. On-policy, online and self-distillation; failure modes and ceilings.
9. Tool-use trajectories and executable reward verification.
10. LoRA/QLoRA, full fine-tuning, quantization and hardware-aware choices.
11. Domain-specialist student training and cross-domain transfer.
12. Independent evaluation, red-teaming, model cards and rollback.

Each lesson must contain learning objectives, sourced explanation in DreamCo's own original wording, source links and license notes, worked example, exercise, automated tests, rubric, common failure modes, and evidence artifact. A transcript is source material, not a finished DreamCo lesson.

## Acceptance gates

- A baseline exists before training.
- Teacher and dataset rights are documented.
- Training and evaluation splits are separated and leakage-checked.
- No private/customer data crosses tenant or provider boundaries.
- A reproducible run emits checkpoint hashes and complete experiment metadata.
- Student is evaluated against its baseline and appropriate teacher(s) on held-out tasks.
- Critical safety regressions block promotion.
- Model card, provenance, rollback and approval are present before deployment.
- A curriculum lesson or generated answer is never mislabeled as a trained checkpoint.

## Initial implementation sequence

1. Extend the existing teacher/model and dataset registries; do not create duplicate registries.
2. Add a teacher-router interface with capability, policy, cost and evaluation constraints.
3. Add a deterministic distillation dataset schema and provenance validator.
4. Add a baseline/teacher/student evaluation harness and disagreement report.
5. Add a small, rights-cleared sandbox experiment using an approved open-weight teacher/student pair.
6. Add repeatable tests and artifacts; only then expand to domain lanes.

**No training job, external API spend, paid compute, customer-data transfer, model promotion, or production deployment is authorized by this specification.**
