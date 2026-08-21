# Buddy Universal Learning Engine

## Vision

Buddy should learn through as many legitimate, measurable channels as the product can safely support—not by blindly absorbing everything, but by selecting the right learning method for the task and preserving provenance, consent, evaluation and safety.

## Learning modes

### 1. Instruction learning
Learn from explicit user instructions, corrections, preferences and workflows.

### 2. Demonstration learning
Observe how a user or approved expert completes a task, then extract reusable procedures.

### 3. Retrieval learning
Search approved documentation, repositories, books, articles, manuals and knowledge bases at task time rather than permanently memorizing everything.

### 4. Structured knowledge learning
Convert trusted information into concepts, relationships, procedures and constraints in the knowledge graph.

### 5. Conversation learning
Use permitted conversations to improve personalization, terminology, workflow understanding and task context.

### 6. Visual learning
Analyze user-authorized images, screenshots, diagrams, UI states and photos to learn visual concepts and procedures.

### 7. Video/movie learning
When the user has rights/permission to use the material, extract permitted transcripts, scenes, concepts and demonstrations. Do not treat copyrighted entertainment as automatically available training data.

### 8. Code learning
Learn from repositories, commits, tests, issues, reviews, documentation and execution results when access and license/permissions permit.

### 9. Tool-use learning
Learn which tool is effective for which task from measured outcomes.

### 10. Experiment learning
Generate controlled experiments, run them in sandboxed environments and retain only validated conclusions.

### 11. Benchmark learning
Use benchmark failures to identify capability gaps, generate curriculum and target new practice.

### 12. Error-driven learning
Every verified failure can become a training/evaluation example after sensitive-data and policy checks.

### 13. Simulation learning
Create synthetic tasks and edge cases to practice rare or dangerous scenarios without affecting production.

### 14. Curriculum learning
Start with foundational skills, increase difficulty, revisit weak areas and avoid advancing solely because a single benchmark passed.

### 15. Peer/Council learning
Compare specialist analyses, identify disagreements and learn which reasoning patterns correlate with verified outcomes.

### 16. Outcome/reinforcement learning
Use measurable task outcomes to improve strategy selection. Reward verified success, reliability and efficiency—not merely activity or confident language.

### 17. Transfer learning
Retrieve validated strategies from similar problems and verify prerequisites before reuse.

### 18. Self-explanation learning
Require Buddy to explain its proposed approach, evidence and uncertainty. Use this as an audit/evaluation signal, not as proof of correctness.

### 19. Human feedback
Capture explicit ratings, corrections and approvals. Distinguish preference feedback from factual correctness.

### 20. Longitudinal learning
Track how strategies perform over time and across environments so temporary wins do not become permanent assumptions.

## Learning pipeline

```text
SOURCE
  -> RIGHTS / CONSENT CHECK
  -> INGEST
  -> CLEAN / REDACT
  -> CLASSIFY
  -> EXTRACT
  -> STORE WITH PROVENANCE
  -> RETRIEVE OR TRAIN
  -> PRACTICE / EXPERIMENT
  -> BENCHMARK
  -> REGRESSION TEST
  -> COUNCIL / HUMAN REVIEW WHEN REQUIRED
  -> PROMOTE / REJECT
  -> MONITOR
  -> REVALIDATE
```

## Obstacle-solving curriculum

When Buddy fails a benchmark:

1. identify the exact skill gap;
2. inspect error clusters rather than only the aggregate score;
3. search memory for related failures;
4. determine whether the issue is knowledge, reasoning, tool use, context, data quality, planning, implementation or evaluation;
5. create the smallest targeted curriculum;
6. generate practice tasks at multiple difficulty levels;
7. test competing strategies;
8. benchmark again;
9. run regression tests on previously mastered skills;
10. promote only if improvement is statistically/operationally meaningful and does not create unacceptable regressions.

## Bug-learning example

```text
BUG
 ↓
REPRODUCE
 ↓
MINIMAL CASE
 ↓
HYPOTHESES
 ↓
TARGETED EXPERIMENTS
 ↓
ROOT CAUSE
 ↓
MINIMAL PATCH
 ↓
UNIT TEST
 ↓
REGRESSION SUITE
 ↓
INTEGRATION TEST
 ↓
BENCHMARK
 ↓
VERIFY
 ↓
STORE REPAIR PATTERN
```

## Knowledge quality levels

- **Raw:** imported but not evaluated.
- **Observed:** directly observed with provenance.
- **Corroborated:** supported by multiple trustworthy sources or independent observations.
- **Validated:** passed a relevant executable test/benchmark.
- **Reusable:** validated across representative contexts.
- **Deprecated:** no longer reliable under current conditions.

## Memory architecture

Separate:

- user preferences;
- episodic events;
- semantic knowledge;
- procedural skills;
- repair strategies;
- benchmark examples;
- tool performance;
- safety/policy constraints.

Every memory should carry source, timestamp, scope, confidence and revalidation conditions where applicable.

## Personalization boundary

Personalized learning must respect user controls, privacy, data deletion/export requirements and applicable rights. User content is not automatically training data for a global model.

## Anti-shortcut rules

Buddy must not improve benchmarks by:

- leaking benchmark answers;
- training on hidden evaluation sets without authorization;
- memorizing test fixtures instead of learning the skill;
- weakening evaluation criteria;
- deleting failed examples;
- inflating scores with duplicate samples.

## Learning success

The Universal Learning Engine is successful when Buddy can demonstrate:

`learn -> practice -> generalize -> verify -> remember -> transfer -> improve`

with measurable gains in quality, reliability, efficiency and user outcomes.
