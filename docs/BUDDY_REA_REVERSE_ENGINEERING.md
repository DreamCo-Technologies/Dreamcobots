# Buddy REA integration and evidence-driven optimization

Reference: REA (Reverse Engineer Anything), official upstream: https://github.com/morluto/rea ; https://rea.tools/ .

REA is an optional local MCP/CLI tool for authorized reverse engineering of software, JS/Electron applications, native binaries, and runtime behavior. It is **not** a model trainer. Install only after reviewing upstream code, licensing, target authorization, and environment prerequisites. Do not automatically execute `npx`, download tools, or inspect third-party binaries in CI.

## Local setup (manual, opt-in)

- Requires supported Node.js and npm; native inspection may additionally require Ghidra, Hopper, or IDA and their applicable licenses.
- In an approved sandbox, review `npx rea-agents setup` and the modifications it proposes before confirming. Do not store private target files, binary dumps, holdout answers, secrets, or copyrighted third-party code in Git.
- Use the findings contract in `tools/buddy_reverse_engineering.py` to record claim, evidence, and limitations with an independently measured benchmark.
- Distill only original, authorized, privacy-reviewed general lessons using `tools/master_teacher_distillation_loop.py`.

## Evaluation protocol

1. Define the specific task and permitted target; capture version, license, scope, threat model, source lineage, and authorization.
2. Record a reproducible baseline for quality, correctness, safety, time, memory, energy and monetary cost where measurable.
3. Inspect authorized behavior with REA; separate direct observations from inference and label uncertainty.
4. Independently implement an original candidate improvement without copying protected implementation code.
5. Run champion and candidate on the same authorized task inputs, at least three repeats; use `tools/buddy_paired_inference.py` for offline adapter smoke tests.
6. Use separately permissioned private holdouts for independent certification, never exposed to research or training agents.
7. Compare paired correctness, tool success, latency, resource use, costs, regressions and safety. Estimate uncertainty per independent task, not by treating repeated trials as independent.
8. Apply `tools/master_teacher_evidence_gate.py` and require independent review, rollback readiness, and explicit promotion authorization.

## Model-weight training readiness

Weight distillation requires a specified teacher and student, model licenses and redistribution permissions, approved datasets, a reserved uncontaminated holdout bank, training code, checkpoint provenance, measured GPU/CPU budget, owner-approved spend and independent evaluation. No weight training or paid inference is enabled by this change.

## Current limitations

This branch contains offline building blocks, not an installed REA MCP server, a configured Buddy model endpoint, private holdouts, or a production-ready trainer. No external model inference or actual model-improvement verification is implied by committing these files.
