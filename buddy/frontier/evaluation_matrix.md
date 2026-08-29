# Buddy Frontier Evaluation Matrix

Buddy's frontier program must evaluate the same broad capability families used to assess leading frontier systems, while adding DreamCo-specific real-world tests. The suite is a living matrix: benchmark names, versions, task pools, and graders are pinned and refreshed as public benchmarks saturate or become contaminated.

## 1. General knowledge and reasoning

- GPQA Diamond / harder variants
- MMLU-style broad knowledge and professional domains
- Humanity's Last Exam, with and without tools where licensing/access permits
- ARC-AGI / ARC-AGI-2 style novel reasoning
- BIG-Bench Hard-style reasoning
- instruction following and constraint satisfaction
- calibration, uncertainty, abstention, and error correction

## 2. Mathematics

- FrontierMath tiers
- competition mathematics
- symbolic reasoning
- numerical reasoning
- proof and theorem-proving tasks
- multi-step word problems
- novel, held-out mathematics generated after the training cutoff

## 3. Science and research

- Frontier Science / unseen-paper reasoning
- physics, chemistry, biology, earth science, computer science
- literature retrieval and synthesis
- hypothesis generation
- experiment design
- evidence quality and citation correctness
- scientific coding and data analysis
- ability to distinguish known facts from speculation

## 4. Software engineering

- SWE-bench-family tasks with current versions where permitted
- Terminal-Bench-style tasks
- repository-level debugging
- code generation and refactoring
- code review
- test generation
- dependency/security remediation
- build and deployment repair
- long-running application development
- DreamCo's real issue backlog as a private evaluation stream

Agentic coding tests must control runtime infrastructure because environment differences can materially change results.

## 5. Tool use and agents

- multi-step tool calling
- browser/computer use
- terminal execution
- API/MCP tool use
- planning and replanning
- state management across turns
- error recovery
- long-horizon execution
- parallel subtask delegation
- verification before irreversible actions
- human escalation when authority is unclear

Test both positive and negative tool-use cases: use a tool when needed and correctly refrain when it is unnecessary.

## 6. Long context and memory

- needle retrieval across increasing context lengths
- multi-document synthesis
- graph traversal/reasoning in long contexts
- instruction persistence
- contradiction detection
- memory retrieval precision/recall
- forgetting and stale-memory handling
- cross-session learning without leaking private data

## 7. Multimodal capability

Where the deployed model stack supports it:

- image understanding
- charts/tables/diagrams
- document/PDF understanding
- OCR robustness
- visual reasoning
- video understanding
- audio/speech understanding
- multimodal tool use
- generation/editing quality when applicable

## 8. Cybersecurity and robustness

- defensive code review
- vulnerability identification and remediation
- secure configuration
- sandbox escape resistance
- prompt injection resistance
- malicious tool-output handling
- secret/credential protection
- supply-chain risk detection
- authorized CTF/security tasks only

## 9. Safety and alignment

- refusal correctness
- safe completion quality
- privacy protection
- data exfiltration resistance
- instruction hierarchy
- dangerous-action gating
- deceptive/eval-aware behavior testing
- reward-hacking resistance
- excessive-agency tests
- auditability and trace completeness

## 10. Reliability and agent quality

Every benchmark should record more than pass/fail:

- pass@1 and pass@k where meaningful
- trial variance
- completion rate
- recovery rate
- tool-call efficiency
- token/compute cost
- latency
- external-model dependency
- hallucination/error rate
- grader agreement
- regression rate

Each agent task should retain a complete trace and have a verified reference solution or independently validated grader. Repeated trials are required where stochastic behavior matters.

## 11. Human and professional work

- document generation
- spreadsheet/data analysis
- presentations and structured deliverables
- project planning
- business research
- domain-specific professional tasks
- quality judged against expert-created rubrics

## 12. Physical-world and future capability lanes

If Buddy gains access to approved physical interfaces, add controlled evaluations for robotics, navigation, manipulation, and real-world perception. Never enable unrestricted physical actions merely to increase a benchmark score.

## 13. DreamCo-specific frontier index

Create private held-out suites for:

- fixing real DreamCo issues
- recovering failed CI
- repairing benchmark failures
- improving Buddy without regressions
- repository architecture understanding
- autonomous feature implementation
- cost/latency optimization
- converting external-model solutions into native capabilities
- resolving clusters of issues from one root cause
- operating the DreamCo development loop end-to-end

## Evaluation governance

Public benchmarks are reference points, not the sole definition of intelligence. Public tasks can saturate or leak. Maintain private held-out tasks, fresh tasks, adversarial tasks, and regression suites. Never train directly on held-out evaluation answers. Review transcripts when an evaluation result is surprising or suspicious.

The suite must compare Buddy against strong frontier baselines using the same task versions, tools, timeouts, compute budgets, and grading rules. Report uncertainty rather than manufacturing a precise rank when evidence is insufficient.
