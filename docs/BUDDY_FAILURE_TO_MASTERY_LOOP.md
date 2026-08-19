# Buddy Failure-to-Mastery Loop

Every failed task should become structured training evidence.

## Loop

`Attempt → Observe → Diagnose → Classify → Choose specialist → Repair → Retest → Compare → Record lesson → Regression test → Promote or retry`

## Failure classes

- code/build
- dependency
- configuration
- environment
- test regression
- performance
- quality
- safety/policy
- integration
- authentication/permission
- data quality
- UX/accessibility
- network/service availability
- model/tool failure
- unclear user requirement

## Specialist routing

Buddy may route one problem through multiple specialists when appropriate. Each specialist should receive a narrow task and return evidence, not merely a conclusion.

## Promotion rules

A repair is promoted only when relevant tests pass and no higher-priority regression is introduced. If evidence is insufficient, Buddy reports **Needs more evidence** rather than claiming mastery.

## Learning artifacts

Store structured records for:

- original failure
- environment/context
- suspected cause
- evidence
- attempted fixes
- successful fix
- tests added
- benchmark delta
- regression result
- remaining limitations

Sensitive credentials and private data must never be copied into training records.
