# Buddy Universal 1,000 Benchmark Integration

Status: approved integration specification

## Purpose
Turn the 1,000-source learning program into a measurable capability system. A source is not considered mastered because it was read; mastery requires practice, sandbox execution, validation, remediation, and repeated independent passes.

## Universal lifecycle
SOURCE -> INGEST -> NORMALIZE -> PROVENANCE -> KNOWLEDGE PACKAGE -> CAPABILITY -> TASKS -> SANDBOX -> EXECUTE -> VALIDATE -> SCORE -> DIAGNOSE -> REMEDIATE -> RETEST -> MASTERED -> PRODUCTION-PROVEN

## Mastery states
- discovered: source identified
- learned: knowledge extracted and structured
- practiced: exercises completed
- mastered: independent benchmark repeatedly passed
- production_proven: capability successfully used in an authorized real workflow

## Universal benchmark metrics
- correctness
- task completion
- reliability
- latency
- cost
- human intervention count
- source quality
- citation/provenance quality
- security
- accessibility
- reproducibility
- user satisfaction
- measurable productivity improvement

## Failure taxonomy
knowledge_gap, tool_gap, reasoning_gap, coding_gap, data_gap, environment_gap, permission_gap, ambiguity, hallucination, timeout, dependency_failure, model_failure, benchmark_misunderstanding, human_approval_required

## Recovery policy
Every failed benchmark creates a structured remediation task. Buddy should diagnose before retrying, select the smallest useful lesson or tool benchmark, retest, and record the result. Repeated failure must lower confidence rather than create false mastery.

## Free-first model policy
Buddy benchmark execution should use free/local/open models and free/open-source tooling by default. Paid models or services require explicit user authorization for that task. The benchmark records model/provider, cost, and whether the route was free-first.

## Source adapters
External sources are adapters, not hard runtime dependencies. Each adapter tracks source URL/API, retrieval date, version, license/terms, provenance, parser, normalized schema, and offline cache/package status.

## Repository intelligence
Buddy may inspect authorized repositories, identify similar implementations, compare fixes, run tests in isolated sandboxes, and propose changes. It must not modify external repositories without authorization.

## Benchmark-parallel bot
Every major benchmark family should have a dedicated training/evaluation bot responsible for source ingestion, benchmark generation, sandbox setup, task execution, scoring, gap detection, remediation, regression testing, and capability promotion.

## Universal task benchmark (#1000)
Given a previously unseen legitimate user goal, Buddy must understand the goal and constraints; decompose it into tasks; identify required capabilities; identify knowledge/tool gaps; research authoritative sources; choose the lowest-cost authorized tool route; create a sandbox; execute the plan; test and validate outputs; recover from failures; report evidence, costs, quality and human approvals; and store reusable capability updates without corrupting prior knowledge.

## Simulation architecture
Knowledge can become an interactive environment:
knowledge -> objects -> relationships -> rules -> behaviors -> environment -> physics -> agents -> user goal -> simulation -> measurement -> feedback -> learning

This supports educational, professional, construction, business, government-service, software, science, robotics, and game/simulation training.

## Data package contract
Every capability package should be machine-readable and include capability_id, source_ids, source_versions, license/provenance, prerequisites, learning objectives, benchmark tasks, sandbox requirements, scoring rubric, remediation paths, mastery threshold, regression tests, model/provider history, cost history, and last validated timestamp.

## Governance
Human approval remains mandatory where an action is consequential, regulated, irreversible, financially material, privacy-sensitive, or outside the user's authorization. Buddy should explain why escalation is needed and continue safe independent work around the blocked action.

## Recommended directory
benchmarks/sources/ | benchmarks/packages/ | benchmarks/tasks/ | benchmarks/sandboxes/ | benchmarks/results/ | benchmarks/remediation/ | benchmarks/regressions/ | benchmarks/reports/

## Definition of done
The dashboard should answer what Buddy knows, what it practiced, what it mastered, what failed, why it failed, what it learned, what it cost, what it automated, how much human time it saved, and what capabilities are production-proven.
