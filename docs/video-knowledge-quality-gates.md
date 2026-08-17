# Video Knowledge Quality Gates

Promoted video knowledge must pass independent gates before it becomes part of a capability package.

## Gates

1. **Provenance** — source, license, content hash, and dataset version are known.
2. **Grounding** — claims point to evidence; temporal claims include timestamps.
3. **Consistency** — duplicates and conflicting worker results are detected and preserved.
4. **Confidence** — confidence is calibrated and `unknown` remains available.
5. **Benchmark** — locked test, transfer, and regression results exist.
6. **Safety** — policy, privacy, and access controls pass.
7. **Reproducibility** — pipeline, worker versions, parameters, and run ID are recorded.

Failed artifacts are quarantined rather than deleted automatically. They can become regression cases or evidence-repair work.

The quality gate is intentionally stricter than simple model confidence: a confident model output without evidence is not promoted knowledge.
