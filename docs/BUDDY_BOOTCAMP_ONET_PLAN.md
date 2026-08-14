# Buddy Bootcamp: O*NET + Repository Mastery

## Objective
Turn the repository's bot inventory, notes, benchmark systems, and O*NET work taxonomy into a single evidence-driven training and sandbox curriculum.

O*NET is used as a coverage framework, not as proof that an AI can perform an occupation safely or professionally. Every generated test requires actual execution and evidence.

## Coverage layers

1. O*NET-SOC occupations
2. O*NET tasks
3. Work activities
4. Skills
5. Knowledge
6. Abilities
7. Work styles
8. Technology skills
9. Repository-specific bot capabilities
10. Existing DreamCo benchmark suites
11. Model benchmark scorecards
12. Regression and production verification

The O*NET 30.3 database currently provides 1,016 occupation rows and a much larger set of task, skills, knowledge, abilities, work-activity and related records. The Actions workflow imports the current reference dataset at run time so the curriculum can be refreshed instead of freezing a stale copy.

## Test contract

Every generated sandbox case has:

- unique benchmark ID
- O*NET source/type/code
- task prompt
- quality evaluation
- speed measurement
- efficiency measurement
- reliability measurement
- safety evaluation
- reproducible evidence
- regression comparison

A generated case starts as `generated`, never `mastered`.

## Mastery ladder

**Generated → Executed → Validated → Benchmarked → Frontier-compared → Mastered**

Mastery is benchmark-specific. A model cannot receive a universal intelligence/mastery claim from passing one occupational test.

## Repository training loop

`Inventory → Map → Generate → Sandbox → Execute → Grade → Compare → Diagnose → Improve → Re-run → Evidence → Learn`

Builder bots should receive the benchmark failure pattern, affected capability, successful reference traces where permitted, and regression requirements—not merely a pass/fail label.

## Division prospectuses

Every discovered bot division receives a public-safe prospectus containing purpose, file evidence, capabilities, tooling plan, status and mastery evidence. The Actions UI provides a button to open each division's prospectus and route to Buddy's upgrade planner.

## Fastest route to broad coverage

- Generate deterministic cases offline first.
- Run cheap contract tests before expensive model calls.
- Cache immutable benchmark fixtures.
- Parallelize independent cases with bounded concurrency.
- Reserve frontier/model calls for cases that survive local validation.
- Compare quality and speed under the same evaluation protocol.
- Re-run only failed/regressed cases after a change.
- Promote improvements only when evidence survives regression.

## Safety boundary

No workflow should silently deploy, expose secrets, escalate permissions, or modify production from a benchmark. High-impact changes remain reviewable and reversible.
