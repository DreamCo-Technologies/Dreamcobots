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


## 7. Physical product invention and product engineering

Buddy should turn a user problem or concept into a documented product-development program: customer discovery, requirements, concept alternatives, engineering tradeoffs, architecture, materials, component selection, costed bill of materials, prototype plan, measured tests, iteration, and manufacturing/service documentation.

Track ownership, contributor rights, licenses, prior-art research, and invention-disclosure timing. Do not promise patentability or freedom to operate; legal conclusions belong to qualified IP counsel.

## 8. Hardware and software prototypes

Coordinate mechanical, electrical/electronics, embedded firmware, sensors, actuators, robotics/control, IoT, mobile/web applications, cloud services, and edge computing. Maintain schematics, wiring diagrams, component specifications, firmware/software revisions, build instructions, test fixtures, measurement logs, failure analysis, and reproducible revision history.

Hardware safety is a first-class gate: component voltage/current/power/thermal limits, battery and radio requirements, protective interlocks, environmental conditions, and regulated/life-critical use require appropriate qualified review. Simulations and generated schematics are not proof of a safe physical prototype.

## 9. 3D design and invention

Convert sketches and descriptions into parametric CAD plans, dimensioned drawings, assemblies, tolerance checks, material choices, and manufacturing-ready exports where supported. For additive manufacturing prepare STL/3MF, slicer settings, material/time/cost estimates, and printability checks; for machining or other fabrication prepare appropriate neutral geometry and process documentation.

Retain editable source files where available, versioned exports, assumptions, dimensions, tolerances, and physical prototype measurements. A rendered model or mesh is not automatically a validated engineering part.

## 10. Start a business from idea to launch

Guide a founder through customer/problem discovery, competitor and market research, demand validation, business model, pricing, unit economics, startup budget, cash runway, funding options, supplier/vendor discovery, permits and insurance research, branding, website, MVP, sales, operations, bookkeeping, customer support, and a 30/60/90-day execution plan.

Assemble practical resource directories for funding and grants, loans, incubators, mentors, makerspaces, equipment, software, materials, suppliers, contract manufacturers, testing labs, contractors, distribution, insurance, and compliance. Each lead must include source, location, last-checked date, eligibility, price or estimate, lead time, and verification status. Grants, loans, and business outcomes are never guaranteed.

Buddy may draft applications, plans, quotes, and outreach. It must not submit applications, purchase equipment, sign contracts, form legal entities, or make external commitments without explicit approval. Legal, tax, accounting, and regulated-industry questions require qualified professional review.

## 11. Resource discovery and end-to-end execution

A unified project workspace links the idea, requirements, research, design files, software repository, bill of materials, suppliers, budget, prototype runs, tests, risks, funding leads, launch tasks, and operational KPIs. A dependency-aware queue advances work while surfacing blockers, stale quotes, missing approvals, and unverified assumptions.

Resource recommendations must be sourced and dated. Distinguish estimates from quotes, leads from confirmed availability, simulations from physical test results, and drafted documents from submitted or approved applications.

## Additional implementation status

These product, hardware, CAD, and startup capabilities are specified as contracts and acceptance gates. CAD kernels, EDA tools, simulation packages, hardware lab integrations, sourcing databases, funding-resource connectors, business formation workflows, and real prototype facilities still need separate adapters and execution evidence.
