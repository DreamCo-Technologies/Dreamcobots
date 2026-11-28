# DreamCo Universal Capability Taxonomy

## Purpose

The DreamCo Universal Capability Taxonomy is the internal reference for building, teaching, evaluating, and safely operating original AI capabilities across DreamCo. It defines what a division or MasterBot lane is expected to learn and how that learning is verified. It is a DreamCo-authored framework; it does not reproduce third-party course text, proprietary curricula, or restricted datasets.

## Two separate registries

DreamCo maintains two related but distinct scopes:

- **55 domain divisions** represent business and occupational problem areas. Each division receives its own specialist curriculum and domain-specific practical work.
- **65 MasterBot learning lanes** represent reusable platform, orchestration, governance, model, and shared learning responsibilities. They are not 65 additional business divisions.

A lesson may target one or more approved domain divisions and MasterBot lanes. A target mapping does not grant a bot permission to execute tools, access customer data, or operate outside its capability policy.

## Universal learning cycle

Every specialist capability follows the same measurable learning cycle:

1. **Understand the task.** Define the user outcome, scope, inputs, constraints, and the difference between facts and assumptions.
2. **Decompose the workflow.** Convert the outcome into small, ordered, testable steps with explicit preconditions and stop conditions.
3. **Select tools and evidence.** Identify the minimum authorized tools, source provenance, version, licensing, privacy, and cost requirements.
4. **Practice in isolation.** Use synthetic or otherwise approved data in a bounded sandbox. Never use private holdouts as training material.
5. **Verify the result.** Run deterministic tests, schema checks, safety checks, and an independent task-specific assessment.
6. **Explain and hand off.** Produce a concise result, evidence references, remaining uncertainty, and escalation instructions.
7. **Improve safely.** Record redacted practice failures, propose a repair, review it, add a new regression test, and rerun the full relevant suite before acceptance.

## Lesson contract

A complete DreamCo-authored lesson should include:

- Stable lesson ID and owner division/lane targets
- A clear objective and measurable completion criteria
- Prerequisites, required concepts, and a difficulty level
- Original explanation, practice instructions, and worked example
- A deterministic exercise with an explicit input/output contract
- A task-specific assessment and an unseen transfer assessment
- A regression benchmark and relevant safety/authorization checks
- A source and rights record for every external factual input
- A review state, version, and evidence hash
- An explicit statement of what the lesson does not authorize

A lesson marked draft-needs-owner-review, authoring-backlog, or metadata-only is not an approved learner lesson and cannot award mastery.

## Difficulty and spaced repetition

Curriculum scheduling uses practice evidence only. A sustained pass rate of at least 95% may raise difficulty by 10% and double the next review interval, capped at 30 days. A pass rate below 70% lowers difficulty by 10% and resets the interval to one day. Evaluation and private holdout results cannot change the learner curriculum.

## Evidence and mastery

Passing a single exercise is not mastery. Mastery requires the lesson-specific benchmark, independent holdout assessment, regression checks, and required reviewer approval. The runtime queue can schedule study and report progress; it cannot authorize model-weight training or grant new execution capabilities.

## External references and commercial boundaries

Public taxonomies, standards, package registries, course catalogs, and technical documentation may be used as research inputs only under their applicable terms. Record the exact source/version, license, attribution, commercial-use terms, training permission, and privacy status before using any material in datasets or lessons. Metadata-only references remain discovery records, not lesson content.

DreamCo may claim rights in original lesson prose, challenge framing, rubrics, test cases, orchestration code, and independently created synthetic examples to the extent permitted by contributor agreements and applicable law. Third-party software remains under its own license. An open-source license does not itself grant exclusive ownership of the software, dataset, or model.

## Safety and escalation

Lessons involving finance, legal matters, health, cybersecurity, physical work, credentials, payments, or other consequential domains must include domain-specific limits, a human approval boundary, and a safe escalation path. A benchmark pass is evidence about the tested task only; it is not professional certification, legal compliance, or permission to perform a regulated activity.
