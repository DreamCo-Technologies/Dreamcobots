# Benchmark Candidate Selection

Buddy should search authorized repositories for examples that can inform original benchmark training.

## Candidate signals

- Problem and failure similarity
- Test and regression quality
- CI quality
- Reproducibility
- Documentation
- Maintenance health
- License/access compatibility
- Novelty and evidence strength

## Strategy

`discover → filter → rank → inspect → compare patterns → generate original benchmark → sandbox → evaluate → record evidence → promote/discard`

The goal is not to clone the best repository. The goal is to identify the engineering idea or benchmark technique worth testing, then independently implement and measure it.

## Selection principle

Prefer a small diverse set of high-quality candidates that covers different approaches to the same capability gap. This prevents Buddy from overfitting to one project's architecture or coding style.
