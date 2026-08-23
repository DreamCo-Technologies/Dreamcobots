# Buddy Capability Catalog

## Purpose

The capability catalog is Buddy's map of what it can do, what it needs to learn, how to test it, and how to safely promote it.

## Capability lifecycle

`discovered -> specified -> learning -> practiced -> benchmarked -> mastered -> production_proven -> continuously_improved`

A capability is never considered mastered from text ingestion alone.

## Capability record

Every capability should define:

- stable capability ID
- human-readable name
- domains
- prerequisites
- source IDs
- knowledge package IDs
- task families
- tools required
- sandbox profile
- benchmark suite
- mastery threshold
- transfer tests
- regression tests
- safety constraints
- authorization requirements
- expected productivity impact
- monetization opportunities, when appropriate
- observability metrics
- known failure modes
- remediation strategies
- confidence/evidence history

## Learning efficiency

Buddy should select learning actions using expected capability gain per unit of:

- time
- compute
- money
- human attention
- source complexity

Prioritize sources that close multiple capability gaps without sacrificing authority or evidence quality.

## Capability families

### Understand
Reading, listening, visual comprehension, video analysis, document analysis, summarization, extraction, translation, classification, retrieval and synthesis.

### Learn
Curriculum planning, source discovery, concept mapping, retrieval practice, spaced repetition, teaching-back, experimentation, feedback integration and knowledge packaging.

### Software
Programming, debugging, testing, code review, architecture, Git, CI/CD, APIs, databases, frontend, backend, mobile, cloud, security, observability and deployment.

### Research
Web research, literature review, source verification, evidence ranking, data analysis, experiment design, reproducibility and research synthesis.

### Work
Task decomposition, workflow automation, productivity analysis, document generation, scheduling, customer support, sales support, operations, reporting and business process improvement.

### Build
Websites, applications, dashboards, simulations, games, educational experiences, data products, automation tools and developer tooling.

### Business
Market research, opportunity discovery, product design, pricing analysis, sales systems, marketing, lead generation, customer research, bookkeeping assistance, operations and business planning.

### Autonomous income assistance

Buddy may help a user identify legitimate income opportunities, estimate effort/revenue/risk, build assets, automate repetitive portions, track outcomes and recommend pivots.

The user remains in control. Money movement, purchases, account creation, contracts, public posting, outreach, or other consequential actions require the permission level configured by the user.

### Government/nonprofit

Government service navigation, public information research, form assistance, eligibility research, workflow automation, procurement research, grant research and nonprofit operations support, subject to applicable rules and human review.

### Creative

Books, scripts, music, video, graphics, 3D assets, game design, educational simulations, story worlds, marketing creative and production pipelines.

### Simulation

Physics-inspired environments, construction, interior design, business simulation, training simulation, educational games, robotics simulation, safety drills and domain-specific virtual labs.

### Self-improvement

Benchmark discovery, capability-gap detection, source discovery, error analysis, remediation planning, regression generation, tool discovery and strategy optimization.

## Autonomous income safety model

When a user asks, "How can Buddy help me make money?", Buddy should:

1. understand the user's skills, time, assets, constraints and risk tolerance;
2. generate multiple legitimate opportunity paths;
3. separate active income, automated income, business-building and speculative opportunities;
4. estimate startup cost, time-to-first-result, ongoing work, likely upside and major risks;
5. identify what can be automated safely;
6. present a human-control plan;
7. ask for authorization before consequential actions;
8. sandbox the workflow;
9. measure real outcomes;
10. learn from success/failure without hiding losses or overstating expected returns.

Buddy must never promise guaranteed income, conceal risk, impersonate users, spam, commit fraud, bypass platform rules, or move money without authorization.

## User control levels

- `observe`: Buddy can research and recommend only.
- `draft`: Buddy can prepare assets but cannot publish/send/execute.
- `sandbox`: Buddy can execute in isolated test environments.
- `approve_each`: Buddy asks before each consequential action.
- `bounded_autonomy`: user defines explicit limits, budgets, domains and destinations.
- `autonomous_within_policy`: Buddy may execute only inside pre-approved boundaries and must log every action.

Users can pause/revoke autonomy at any time.

## Mastery evidence

Promotion requires objective evidence, including as applicable:

- independent task success
- unseen-task transfer
- repeated passes
- regression pass
- safety checks
- reproducibility
- cost/time measurement
- human intervention measurement
- provenance

## Design goal

The catalog is intended to support an AGI-oriented engineering roadmap: broad capabilities, continual learning, tool use, self-evaluation, safe autonomy, transfer across domains, and measurable real-world usefulness. It does not claim that DreamCo or Buddy is AGI today.
