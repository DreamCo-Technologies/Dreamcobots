# Buddy Governed Experiment Sandbox

This is the shared experiment boundary for Buddy capabilities, datasets, models, agents, tools, and benchmarks. It protects stable state by default; it is not a claim that every experiment is perfectly isolated.

## Lifecycle

`planned → running → passed | quarantined | blocked`

Every run records an immutable baseline target, deterministic input digest, provenance records, and artifact hashes. A failed or over-budget run is quarantined and retains diagnostics. It never replaces the stable version.

After an attempted host run, the contract requests host cleanup. A cleanup failure also quarantines the run and records its diagnostic; the stable rollback target stays unchanged.

## Default boundary

- No production access or secrets.
- Network disabled unless an exact allowlist is provided.
- Tools denied, read-only, or fixture-only by explicit declaration.
- Resource limits cover wall time, CPU time, memory, output, and artifact count.
- Dataset, model, and benchmark runs require a deterministic seed.
- Output is bounded and token-like values are redacted before artifact capture.

The core contract does not launch commands. An approved host adapter must provide the actual microVM, container, or equivalent isolation and enforce the declared policy. Vercel Sandbox is one possible host; local tests remain blocked until a host is intentionally configured.

## Promotion

A passed sandbox run is only a candidate. Promotion is held until independent evidence shows a baseline comparison, reproducibility, benchmark result, reality-grounding result, dataset-quality result, regression result, artifact integrity, and owner approval. Release/canary decisions remain separate.

## Limits

No sandbox framework can promise perfect security. Host configuration, supply-chain security, runtime escapes, and operator access remain material risks. Treat untrusted code and data as untrusted, use minimal permissions, and keep production credentials outside experiments.
