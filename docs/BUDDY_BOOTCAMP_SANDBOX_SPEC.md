# Buddy Bootcamp + Capability Sandbox Specification

## Product goal

Let a beginner choose exactly what they want their personal Buddy to become better at, receive a guided training curriculum, practice safely in a sandbox, and verify improvement against benchmarks without needing to understand ML engineering.

## User journey

```text
CHOOSE CAPABILITY
  -> BASELINE TEST
  -> PERSONAL BOOTCAMP
  -> GUIDED LESSON
  -> PRACTICE LAB
  -> SANDBOX TEST
  -> FEEDBACK
  -> TARGETED RETRAINING / RETRIEVAL
  -> RETEST
  -> REGRESSION
  -> TRANSFER TEST
  -> CAPABILITY BADGE
```

## Beginner-first interface

The first screen should ask:

**What do you want Buddy to get better at?**

Categories:

- Coding
- Writing
- Research
- Math
- Science
- Business
- Sales
- Customer support
- Real estate
- Finance literacy
- Data analysis
- Design
- Images/vision
- Document understanding
- Communication
- Planning
- Tool use
- Debugging
- Cybersecurity awareness
- Productivity
- Custom capability

Users can select one or multiple capabilities.

## Capability profile

Each capability has:

- plain-language description;
- prerequisites;
- baseline benchmark;
- skill tree;
- lessons;
- practice tasks;
- sandbox tests;
- transfer tests;
- regression tests;
- target threshold;
- difficulty levels;
- estimated practice time;
- privacy/data requirements;
- allowed learning sources.

## Bootcamp modes

### Guided
Buddy teaches step by step.

### Practice
Buddy gives increasingly difficult exercises.

### Coach
Buddy watches permitted work and gives hints without immediately solving it.

### Challenge
Timed/untimed benchmark-style tasks.

### Repair Lab
User deliberately gives Buddy broken examples so it learns diagnosis and debugging.

### Exam Prep
Practice against a benchmark blueprint while preserving unseen holdout tests.

## Sandbox architecture

Every training task should run in an isolated environment appropriate to the capability.

```text
TASK
 -> POLICY CHECK
 -> SANDBOX CREATE
 -> LOAD ALLOWED MATERIAL
 -> EXECUTE / PRACTICE
 -> COLLECT METRICS
 -> CLEANUP
 -> SCORE
 -> FEEDBACK
```

The sandbox must prevent training exercises from modifying production repositories, leaking secrets or affecting unrelated users.

## Benchmark modes

### Baseline
Measures current ability before training.

### Formative
Frequent low-stakes checks during lessons.

### Practice benchmark
Similar structure but not identical to training examples.

### Holdout
Unseen evaluation material reserved for measuring real improvement.

### Transfer
Novel tasks requiring the same underlying capability in a different context.

### Regression
Previously passed capabilities are periodically retested.

### Stress
Edge cases, ambiguity, time pressure and noisy inputs where appropriate.

## Anti-cheating / anti-memorization design

Training and evaluation data must be separated.

Never count benchmark leakage as learning.

Holdout and transfer tests should use unseen examples and, where practical, multiple equivalent task forms.

## Personal training plan

Buddy generates:

- current skill level;
- target level;
- weakest subskills;
- recommended lessons;
- practice schedule;
- benchmark targets;
- estimated effort;
- confidence;
- next best exercise.

The user can override the schedule.

## Fastest-learning strategy

Buddy should optimize practice by focusing on the highest-value skill gaps first:

`expected improvement / time and cost`

Use spaced review for retained skills and harder transfer tests to prevent false mastery.

## User-owned personalization

Users can optionally provide permitted material such as:

- their own documents;
- notes;
- photos;
- recordings;
- code;
- conversations;
- licensed books/courses;
- authorized reference material.

The product must distinguish between personal memory, retrieval sources and model-training data. Consent, ownership/licensing and deletion/export controls must be explicit.

## Capability badges

A badge is earned only after required gates pass:

`baseline -> curriculum -> practice -> holdout -> transfer -> regression`

Example:

**Buddy — Python Debugging Level 3**

- Holdout: passed
- Transfer: passed
- Regression: passed
- Last verified: timestamp
- Evidence: linked evaluation run

Badges expire/revalidate when the benchmark or capability definition changes.

## Bootcamp dashboard

Show:

- overall progress;
- capability tree;
- current lesson;
- weakest skill;
- next exercise;
- sandbox history;
- benchmark trend;
- transfer score;
- regression health;
- time/cost used;
- what Buddy learned;
- what still needs work.

## Business model hooks

The architecture supports free and paid tiers without locking core user data into a proprietary dead end.

Potential paid capabilities include:

- expanded private memory;
- larger sandboxes;
- advanced benchmark packs;
- specialized bootcamps;
- team training;
- private knowledge sources;
- higher execution limits;
- advanced personalization;
- professional certification reports.

Any paid tier must clearly state limits, data handling and export options.

## Definition of done

A Bootcamp capability is production-ready when a beginner can:

1. select it;
2. run a baseline;
3. understand the result;
4. start training;
5. practice safely;
6. run a sandbox test;
7. see why the result changed;
8. retest on unseen tasks;
9. verify that improvement generalizes;
10. export/share the resulting capability record where supported.
