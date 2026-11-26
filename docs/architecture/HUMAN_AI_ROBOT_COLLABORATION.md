# Human, AI, Robot and Team Capability Allocation

## Purpose

Buddy should help each user choose the right partner for the task: the person, AI software, a physical robot, or a carefully designed combination. The unit of analysis is the **task and its conditions**, not the occupation title.

## Core principle

People, AI systems, and robots have different strengths and limitations. There is no universal winner. Buddy must split multi-step work into subtasks, select the safest capable arrangement for each step, explain why, and keep responsibility explicit.

## Existing repository foundation

This proposal extends the existing occupational curriculum, task index workflow, universal task sandbox, and capability evidence system. It does not create a second occupation catalog. The existing 31-subject occupational curriculum already covers the six major worker/job/workforce areas and defines task-level study-guide requirements. The task-index generator and refresh workflow exist, but the generated task index is not currently present on the default branch; therefore full task-level ingestion is not verified.

## Allocation categories

- **Human-led:** people perform the core task; software may assist.
- **AI-assisted:** AI researches, drafts, analyzes, or recommends; a person verifies consequential output.
- **Digital automation:** bounded software actions run with least privilege, tests, logs, and rollback.
- **Robot-assisted:** validated physical actions are performed by a specified robot under task-specific safety controls.
- **Human + AI:** human direction and accountability combined with AI speed and information processing.
- **Human + robot:** human adaptation and oversight combined with physical precision, force, or repeatability.
- **AI + robot:** AI perception/planning connected to a robot's validated sensors and actuators.
- **Human + AI + robot:** human responsibility, AI-supported planning, and robotic physical execution with safe handoffs.
- **Restricted / qualified-only:** professional authority or legal credentials remain with qualified people.
- **Not assessed:** insufficient evidence; autonomous execution is blocked.

## What each tends to do well

| Participant | Potential strengths | Important limits |
|---|---|---|
| Human | Empathy, relationships, contextual and ethical judgment, adaptable physical interaction, accountability, novel exceptions | Fatigue, finite attention, exposure to hazards, limited throughput |
| AI software | Information synthesis, language, pattern analysis, calculations, code assistance, repeatable digital workflows | Can be wrong; depends on data/tools/permissions; no physical agency or professional license by itself |
| Physical robot | Repeatable movement, manipulation, sensing, strength, endurance, hazardous or ergonomically harmful work when engineered for it | Hardware and environment limits; calibration, safety, maintenance, and recovery requirements |
| Human + AI | Human judgment with faster research, drafting, analysis, planning, and coding | Human review and source verification still required |
| Human + robot | Human adaptation with machine precision, strength, and repeatability | Requires engineered collaboration safety and trained supervision |
| AI + robot | Digital perception and planning connected to physical action | Requires validated sensing, control, fail-safe behavior, and environment testing |
| Human + AI + robot | Combines judgment, digital intelligence, and physical execution | Highest integration complexity; explicit accountability and fallback required |

These are hypotheses for routing, not guarantees. Actual capability depends on the exact person, model, tools, robot, environment, task, and evidence.

## Task allocation procedure

1. Understand the user's desired outcome and acceptance criteria.
2. Decompose the work into observable steps.
3. Identify physical, digital, social, cognitive, environmental, safety, privacy, and credential requirements.
4. Check the available human skills, model benchmarks, tool permissions, and exact robot hardware.
5. Assign each step to the best-supported participant or team.
6. State the reason, confidence, unknowns, human responsibility, and safeguards.
7. Run a sandbox or simulation before real-world execution when possible.
8. Verify results and update the capability record only from evidence.
9. Ask the user about desired automation, budget, accessibility, privacy, and human involvement when those choices matter.

## Evidence rules

- Occupational averages do not prove an individual's abilities or qualifications.
- A task statement does not prove that an AI model or robot can perform the task.
- Model evidence must name the model/version, tools, permissions, benchmark, errors, cost, latency, and human intervention.
- Robot evidence must name the exact hardware/firmware, sensors, actuators, payload, workspace, safety analysis, emergency stop, and recovery tests.
- Human credential requirements must be checked with the relevant current authority.
- For high-impact or regulated tasks, preserve qualified human review and sign-off as required.
- If evidence is missing, use **Not assessed** and do not enable autonomous execution.

## Source coverage and licensing

The occupational reference is the O*NET Database 31.0, released August 2026. Its public database is generally available under CC BY 4.0, subject to separately licensed elements. Preserve the required attribution to the database and the U.S. Department of Labor, link the license, and mark changes. This is source provenance, not DreamCo product branding.

The occupational database describes human work and worker requirements. AI and robot capability classifications must be researched and validated separately; do not attribute them to the occupational source.

## Canonical implementation

The machine-readable policy lives in `config/human-ai-robot-collaboration-taxonomy.json`. Task records should link to the existing occupation/task IDs and canonical division/MasterBot registries. Do not duplicate all tasks into each division; use shared task records and capability-based routing.

## Completion boundary

A complete source inventory, complete task-to-role crosswalk, original learning materials, task-specific evidence, tests, and human review are separate gates. A taxonomy draft or green unit test does not establish that every task has been assessed or that Buddy is competent at every occupation.
