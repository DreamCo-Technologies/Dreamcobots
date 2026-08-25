# DreamCo Conversation Systems Integration Spec

This document captures the systems approved in the current DreamCo build conversation so the consolidated PR has a durable implementation checklist.

## 1. Actions Page operating system
- Single evidence-first control plane for health, goals, execution, training, benchmarks, divisions, local Buddy, data sources, repairs, security, and releases.
- Daily completion checks and stale-evidence detection.
- Truth rules: unknown is not pass; planned is not executed; training is not mastery; one successful run is not mastery; stale evidence is not current health.
- Every job records owner, purpose, inputs, execution mechanism, success criteria, evidence path, timeout, and failure action.

## 2. 65 MasterBot architecture
- Canonical registry remains the source of truth.
- Each division requires a purpose, capabilities, entrypoint, tests, benchmark suite, training plan, dashboard route, command-center route, evidence contract, dependencies, and fallback.
- Sub-bots remain implementation workers under their MasterBot rather than competing top-level systems.

## 3. Benchmark gap-closure loop
Observe -> benchmark -> identify gap -> prioritize -> curriculum -> sandbox -> train/practice -> transfer test -> remediation -> retest -> regression test -> evidence -> repeat.

Training activity must never be reported as mastery without reproducible benchmark evidence.

## 4. Buddy Bootcamp / 1,000-source curriculum
Each source follows: discover -> classify -> permitted-source/provenance check -> concept extraction -> synthesis -> lessons -> practice -> sandbox -> transfer -> score -> remediation -> regression -> evidence.

Source material is research input, not automatically redistributable training data.

## 5. DreamCo Knowledge Synthesis
Build a compact DreamCo teaching layer from permitted/licensed sources: core ideas, principles, competing viewpoints, DreamCo synthesis, examples, counterexamples, common mistakes, practice, transfer tasks, benchmarks, provenance, and confidence.

The system must not reproduce copyrighted books or websites as a substitute for original/licensed material. Commercial packages should contain DreamCo-original synthesis and properly licensed or owned training assets.

## 6. DACL commercialization
DreamCo Adaptive Capability Learning can be offered as capability audits, training sprints, continuous learning programs, private enterprise labs, benchmark labs, and fleet orchestration. Customer reports should contain baseline, post-training scores, deltas, transfer results, regressions, resource efficiency, and remaining gaps.

Do not make unsupported AGI/frontier claims.

## 7. Local Buddy model
Engineering target: approximately 500M parameters, not a claim of an existing trained checkpoint. Reference architecture: decoder-only Transformer, RMSNorm, SwiGLU, RoPE, grouped-query self-attention, tied embeddings, SentencePiece-compatible tokenizer, BF16, gradient accumulation, source-level train/validation splits, deduplication, held-out transfer tasks, early stopping, regression testing, CPU/MPS/CUDA/ROCm local modes, optional int8/int4 quantization, and no distributed-training requirement.

Provide a minimal local chat CLI and optional JSON output. Keep the reference stack lightweight and make accelerator dependencies optional.

## 8. 65 division dashboards
Every division should have its own Actions dashboard and command center with: current objective, execution queue, training queue, benchmark gap, recent runs, failures, evidence, resource usage, daily completion state, and next action.

## 9. Commercial training packages
Potential outputs include curriculum lessons, practice tasks, benchmark tasks, remediation sets, evaluation rubrics, scorecards, provenance, versioning, and evidence ledgers. Only assets DreamCo owns or is licensed to redistribute should be packaged for resale.

## 10. Integration rule
This spec is a checklist, not proof that every implementation exists. The consolidated PR must progressively replace each checklist item with real source code, tests, workflows, and evidence. Dashboard status must remain truthful while work is incomplete.
