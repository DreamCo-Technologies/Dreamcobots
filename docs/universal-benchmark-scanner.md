# Buddy Universal Benchmark Scanner

The scanner is the orchestration layer for Buddy's benchmark mastery program.

## Core loop

`discover → classify → deduplicate → map → generate original variant → sandbox → execute → collect evidence → score → recover → regression → promote/retrain → report`

## Benchmark lenses

- GitHub: repository engineering, collaboration, CI/CD, debugging, delivery.
- O*NET: occupations, tasks, skills, knowledge, abilities, and professional work activities.
- Codecademy-aligned: programming concepts, hands-on coding, projects, testing, and transfer.
- DreamCo internal: proprietary capability goals and regression suites.
- Authorized external sources: additional learning and professional benchmarks.

## Mastery requirements

Buddy must pass original variants and cross-source transfer tests. A course completion or copied exercise does not equal mastery.

## Failure handling

Failures are preserved as evidence. Buddy classifies the failure, selects a recovery strategy, retries safely, verifies the result, records the learning, and schedules a harder follow-up.

## Repository safety

Only DreamCo-owned or explicitly authorized repositories may be analyzed or changed. Read-only analysis is the default. Credentials, access controls, destructive operations, and unsupported completion claims are prohibited.
