# Buddy Engineering and Model-Building Capabilities

## Objective

Buddy OS must be able to move from a plain-language request to a tested software change, understand authorized systems, build compatible implementations, and improve division-specific models through reproducible distillation and weight training.

This document defines four connected capabilities. The JSON contract is a specification and validation target; it is not proof that every runtime adapter or training backend is already deployed.

## 1. Vibe coding

Buddy should:
1. Translate natural-language intent into acceptance criteria and constraints.
2. Inspect the repository, architecture, dependencies, existing conventions, and open work.
3. Map every requirement to implementation files, tests, runtime routes, and benchmarks.
4. Produce a dependency-aware implementation plan.
5. Edit code in an isolated branch or workspace.
6. Run formatting, type checks, static analysis, unit, integration, end-to-end, security, and regression tests.
7. Explain the diff, evidence, remaining risks, and rollback.
8. Open a reviewable pull request.

A generated code snippet is not a completed task. Completion requires a reproducible run and passing evidence. Merge and production deployment remain separately approved actions.

## 2. Authorized reverse engineering

Buddy should be able to inspect systems the user owns or is authorized to assess: source repositories, public/documented APIs, user-provided binaries, authorized UI sessions, and documented workflows.

The workflow inventories components and dependencies, maps data flows and interfaces, records observable behavior, writes a specification, creates behavioral compatibility tests, and builds a clean-room implementation where appropriate.

Buddy must verify authority and scope first. It must not bypass authentication or access controls, extract credentials, exploit unauthorized systems, evade technical protection measures, or copy protected code/trade secrets without rights. The output includes an architecture map, interface contracts, reproducible tests, provenance, unknowns, and risks.

## 3. Model distillation

Each division can use an approved teacher model to produce high-quality demonstrations or targets for a smaller student model. Candidate methods include response distillation, instruction/data distillation, preference distillation, and task-specific adapter training.

The pipeline pins teacher and student revisions, verifies licenses and output/data rights, records provenance, filters and deduplicates examples, separates train/validation/private holdout, trains in a sandbox, and evaluates the student against both its baseline and the teacher on comparable tasks.

Private holdout data is never used for training or tuning. Distillation does not imply permission to use proprietary teacher outputs; rights and provider terms must be checked for the specific source.

## 4. Model-weight training

The training ladder begins with model selection and a reproducible baseline. It then uses retrieval, tools, and workflow improvements before parameter-efficient fine-tuning (LoRA/QLoRA), supervised fine-tuning, continued pretraining, or full fine-tuning. Training from scratch is a separately approved research program.

Every run pins the base model revision, tokenizer, data manifest and split hashes, code revision, hyperparameters, random seed, compute environment, and output checkpoint hashes. It records GPU/CPU time, memory, cost, latency, throughput, benchmark scores, safety results, and rollback information.

Paid compute requires explicit approval. Production weight updates require separate explicit approval and independent review.

## 5. Division-wide execution

The system must connect each canonical MasterBot to:
- a real task runner and sandbox;
- a dependency-aware queue with bounded retries and cancellation;
- a model identity and versioned adapter/checkpoint;
- domain task suites and private holdout benchmarks;
- general capability, safety, and regression suites;
- provenance-aware knowledge and dataset manifests;
- durable run records and evidence artifacts.

The 65 MasterBot registry and 45-domain taxonomy must be reconciled using an authoritative crosswalk. Until then, do not invent ownership or claim all 45 divisions have a verified mapping.

## 6. Promotion and mastery

A capability moves through explicit states: planned, configured, executable, evaluated, independently reviewed, release-eligible, and mastered. These states must not be conflated.

Promotion requires reproducible artifacts, rights and consent evidence, passing private holdout and regression tests, cost/latency/memory reports, a tested commit SHA, and independent human review. No automated merge, deployment, or production weight replacement is enabled by this contract.

## Current implementation status

The capability contract and its validation tests define the required behavior and evidence. They do not by themselves provide:
- a complete autonomous coding agent runtime;
- a reverse-engineering sandbox or UI/API adapters;
- a connected distillation/training cluster;
- approved datasets, teacher access, or GPU capacity;
- trained checkpoints or proven competitive division models.

Those are separate engineering milestones. Each must be demonstrated with real execution records before Buddy labels it operational.
