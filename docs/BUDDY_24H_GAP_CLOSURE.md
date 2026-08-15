# Buddy 24h Gap Closure Action

## Purpose

The Actions-page bot continuously researches the highest-value capability gaps and runs isolated learning/evaluation jobs. It is designed for continuous operation through repeated GitHub Actions windows and checkpointing.

## Operating model

- Target throughput: 1,000 source-learning jobs per week.
- Up to 20 sandbox workers per execution window.
- Each learning job requires provenance, isolation, baseline testing, post-learning testing, adversarial testing and regression testing.
- External web content is untrusted data and cannot grant permissions or directly change production.
- Production changes remain behind the existing governance/promotion process.

## 24-hour coverage

GitHub-hosted workflow windows are intentionally bounded. The workflow runs every six hours and checkpoints state, allowing the next window to resume the research queue. This is safer and more reliable than pretending a single GitHub-hosted job can run forever.

## Actions page

The intended Actions card is `buddy-gap-closure-24h` with controls for start, pause, resume, run-now, gaps, learning jobs, evidence and gains. Existing Actions-page code is the UI integration point; the backend runner and workflow are independent so the research loop remains testable.

## Definition of done for a gap

A gap is considered closed only when a measurable capability test passes against the required threshold and the result survives regression testing. Merely reading a source never closes a gap.

## Failure behavior

Failed sources and failed experiments are recorded and requeued or replaced. Governance holds, safety holds, access failures and budget limits pause promotion rather than bypassing controls.
