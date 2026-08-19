# Buddy Failure-to-Learning Loop

The objective is not to hide failures. The objective is to make every useful failure improve the system.

## Flow

`Failure → Capture → Classify → Reproduce → Diagnose → Fix candidate → Sandbox → Regression test → Review → Promote → Monitor`

## Failure record

Store structured information when appropriate:

- task/capability
- timestamp
- agent/model configuration
- inputs or safe references to them
- tools used
- expected result
- observed result
- error category
- severity
- reproducibility
- root-cause hypothesis
- proposed fix
- test added
- approval state
- final outcome

Sensitive user content should be minimized, protected, or omitted from training records according to the user's data policy.

## Failure categories

- correctness
- reasoning/planning
- tool use
- integration
- dependency
- environment
- permissions
- performance
- cost
- security
- privacy
- UX/accessibility
- data quality
- flaky/transient
- specification mismatch

## Automatic recovery

Safe, reversible failures may be retried or repaired automatically. Consequential operations require the configured approval policy. Repeated failures should escalate to a specialist rather than looping forever.

## Learning quality

A lesson is promoted to a reusable training/regression example only after it is validated. This prevents Buddy from learning incorrect fixes from noisy failures.
