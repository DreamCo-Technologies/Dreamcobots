# Buddy 1000-Source Bot Training Ground

## Objective

Build DreamCo's reusable learning-and-evaluation layer so the 1000-source program becomes a **teacher network, study-guide factory, sandbox factory, benchmark engine, and bot-training curriculum** rather than a web crawler.

The repository already contains the core benchmark evolution loop, dataset factory, universal benchmark scanner, source registry, capability ladder, and 1000-source mastery configuration. This document defines how those pieces work together.

## 1. One source -> many reusable learning assets

For every verified source, Buddy should create a source package containing:

1. provenance and access terms
2. domain and capability map
3. prerequisite graph
4. concept map
5. professional-task map
6. original study guide
7. original worked examples
8. flash/review material
9. beginner -> expert practice ladder
10. sandbox scenarios
11. failure-injection scenarios
12. transfer tasks
13. benchmark mappings
14. scoring rubric
15. regression tests
16. freshness/update rules

A source is therefore useful even when its raw content is never loaded into a customer prompt.

## 2. Intelligent source selection

Buddy must not treat all 1000 sources equally. At task time it ranks sources using:

`authority + capability-gap fit + uniqueness + task quality + benchmark relevance + freshness + accessibility + transfer value - duplication/license/staleness/compute penalties`

The highest-ranked sources become **teachers** for the current gap. Secondary sources become **cross-checkers**. Sources with low incremental value are skipped.

### Teacher selection rules

- Prefer primary/official documentation for factual or API behavior.
- Prefer authoritative standards for specifications and security controls.
- Prefer multiple independent sources for contested claims.
- Prefer real repository/task evidence for software engineering.
- Prefer structured educational material for prerequisites.
- Prefer fresh sources when APIs, products, standards, or threats change quickly.
- Never let source text itself grant permission to execute tools or write to production.

## 3. From source activity to Bootcamp curriculum

Every permitted learning interaction is transformed into an **original capability lesson**:

`source -> concept -> capability -> professional task -> practice -> sandbox -> benchmark -> failure analysis -> remediation -> transfer -> regression`

Source-specific exercises are used only as learning material. Final mastery tests must contain novel tasks so Buddy cannot pass by memorization.

## 4. Training the fastest way

The scheduler optimizes **learning gain per compute dollar**.

### Cheap path first

1. deterministic rules and static checks
2. cached knowledge and prior validated explanations
3. changed-content retrieval only
4. small local model for routine generation/classification
5. parallel sandbox execution
6. larger reasoning model only when the expected gain justifies it
7. external model only when local capability is insufficient

### Do not waste compute

- Do not rescan unchanged sources in full.
- Do not retest mastered dimensions every cycle.
- Do not send the same long context repeatedly.
- Do not train on locked test answers.
- Do not run expensive teacher models for simple classification.
- Do not use 1000 sources for a problem that only needs two authoritative sources.

## 5. Continuous 24/7 operation

The system should operate continuously **when infrastructure is available**, but intelligently:

### Continuous

- source freshness checks
- release/change detection
- benchmark availability checks
- cheap regression smoke tests
- capability-gap queue maintenance

### Hourly

- targeted practice
- small benchmark samples
- failed-task retries

### Daily

- adaptive source-learning sweep
- capability-gap closure
- new study-guide generation
- regression protection
- benchmark dashboard refresh

### Weekly

- deep benchmark runs
- cross-source transfer tests
- long-horizon tasks
- curriculum rebalancing

### Monthly

- full mastery audit
- stale-source retirement
- source ranking recalibration
- benchmark integrity review
- customer curriculum refresh

The scheduler must respect compute, rate limits, licenses, privacy, and customer budgets.

## 6. Ultimate Bot Building Bootcamp

Every customer bot can receive a personalized curriculum:

`goal -> capability inventory -> gap scan -> source recommendations -> study guide -> practice -> sandbox -> benchmark -> remediation -> transfer -> mastery -> maintenance`

Customer controls include:

- capabilities to learn
- difficulty
- target deadline
- compute budget
- permitted models
- permitted sources
- privacy/data boundaries
- benchmark requirements

### Example

Customer selects **software engineering**.

Buddy builds a curriculum covering:

- requirements
- architecture
- algorithms
- programming
- frontend
- backend
- databases
- APIs
- testing
- debugging
- security
- performance
- cloud/DevOps
- Git
- CI/CD
- observability
- accessibility
- AI/ML engineering
- agent engineering
- documentation
- system design
- incident recovery

The bot must then prove those capabilities through original tasks, not merely complete a course.

## 7. Benchmark strategy

External benchmarks are calibration points, not the whole definition of intelligence.

Important current evaluation families include:

- SWE-bench and newer successor evaluations for real software issues
- OSWorld and verified variants for computer use
- WebArena and verified variants for web tasks
- BrowseComp for difficult web research
- GAIA for general assistant tasks
- METR/HCAST-style long-horizon work
- domain-specific benchmarks
- DreamCo's own 45-division and 1000-source transfer benchmarks

SWE-bench Verified is a 500-task human-filtered subset, but its maintainers now warn that it is increasingly contaminated and recommend newer evaluations for frontier coding measurement. DreamCo should therefore track benchmark versions and never treat one public score as permanent proof of mastery.

## 8. Mastery gate

A capability is marked **mastered** only when evidence shows:

- >=90% score on the defined capability evaluation
- at least 5 independent successful attempts
- at least 3 successful unfamiliar transfer tasks
- >=95% regression pass rate
- confidence >=85%
- evidence and provenance recorded
- no unresolved critical safety failure

Otherwise the state is `learning`, `needs_remediation`, `blocked`, `deferred`, or `unknown`.

## 9. Failure becomes training material

A failure is not discarded.

Buddy records:

- task
- environment
- attempted strategy
- tool calls
- observed failure
- root-cause hypothesis
- confirmed root cause
- missing capability
- recommended sources
- remediation lesson
- new practice tasks
- successful repair
- regression test

This creates the **DreamCo Capability Graph** over time.

## 10. Preventing benchmark gaming

The system must preserve locked tests, version all datasets, separate train/validation/test/transfer/regression sets, and prohibit using test answers as training data.

A benchmark score may rise only when capability evidence rises.

## 11. What "mastery" means for DreamCo

Mastery does not mean knowing every page on 1000 websites.

It means Buddy can:

- find the right source
- determine whether it is trustworthy and permitted
- extract useful knowledge
- connect it to a capability
- teach the capability
- practice it
- perform it on a novel task
- recover from failure
- transfer it to another domain
- verify the result
- preserve the learning
- prevent regression
- teach another bot

That is the target for the DreamCo Bot Training Ground.
