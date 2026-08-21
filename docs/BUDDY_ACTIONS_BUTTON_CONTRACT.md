# Buddy Actions Button Contract

This document is the user-facing contract for every control on `website/actions.html`.

## Golden rule

A button must never imply that work happened when the browser only created a plan or displayed evidence. Every control has one of three execution classes:

- **LOCAL** — executes only through an approved local Buddy runner; the Pages browser must not execute arbitrary shell commands.
- **REMOTE** — dispatches or reruns an approved GitHub Action with appropriate permissions.
- **READ-ONLY** — reads evidence, opens a run, or creates a repair plan without changing code.

## Current Actions controls

| Control | Class | What it does | Why it matters | Expected result |
|---|---|---|---|---|
| Run Doctor | LOCAL | Checks repository structure, runtime bindings, dependencies and configuration | Finds foundational problems before deeper tests | Machine-readable health findings |
| Run Tests | LOCAL | Runs the approved test suite and preserves the first failure | Proves behavior and prevents false-green releases | Test report + failures |
| Run Lint | LOCAL | Runs configured lint/type/static checks | Catches preventable integration problems | Diagnostics with no source mutation |
| Security Check | LOCAL/REMOTE | Runs approved security checks such as dependency/code/secret controls | Protects users and release integrity | Security evidence or release blocker |
| Benchmark Locally | LOCAL | Measures defined capability benchmarks | Separates real improvement from feature-count growth | Baseline + measurements + gap |
| Find Repair Plan | READ-ONLY | Converts evidence into the smallest reversible repair plan | Prevents blind self-modification | Repair plan + tests + rollback plan |
| Verify Pages Data | LOCAL | Validates generated dashboard data and source bindings | Prevents stale/fabricated public metrics | Data verification report |
| Prepare Device Bundle | LOCAL | Builds and validates a distributable Buddy package | Protects users from broken downloads | Verified artifact or explicit unavailable state |
| Refresh GitHub Runs | READ-ONLY | Reads public GitHub Actions run evidence and updates the dashboard | Makes the page reflect current observed workflow state | Run evidence mapped to workflows |
| Prospectus | READ-ONLY | Opens purpose, evidence, success, fallback and upgrade plan | Explains the control before execution | Detailed action contract |
| Open run/workflow | READ-ONLY | Opens the authoritative GitHub workflow page/run | Lets operators inspect actual evidence | GitHub page |
| Plan with Buddy | READ-ONLY | Sends workflow context and evidence into Buddy planning | Converts failure evidence into an actionable repair plan | Pre-filled Buddy task |

## Why a button can appear green while the system is not green

The Actions page intentionally separates **static evidence** from **live run evidence**. Static evidence can describe configured controls while a current workflow run is failing. The dashboard must show both.

A workflow is not certified merely because its YAML exists or a previous run passed.

## Why failures happen

Common classes:

1. stale generated artifacts;
2. startup/health endpoint failures;
3. dependency/version drift;
4. environment or secret/permission differences;
5. tests exposing real regressions;
6. flaky/transient external services;
7. workflow configuration mistakes;
8. missing artifacts or expected files;
9. benchmark thresholds not met;
10. a repair fixed one path but broke a dependent path.

## Failure response

```text
failure
 -> fingerprint
 -> link canonical incident
 -> determine transient vs deterministic
 -> retry only when safe
 -> reproduce deterministic failures
 -> build smallest repair
 -> targeted test
 -> dependent regression
 -> Council when required
 -> deploy/canary
 -> verify
 -> close or escalate
```

## Required safety behavior

- Browser buttons never execute arbitrary shell commands.
- Diagnostics never expose secrets.
- A retry is not a repair.
- Production changes require the appropriate policy gate.
- Destructive cleanup requires a reversible plan.
- Unknown evidence stays unknown.
- Failed work stays visible.

## Acceptance test for the Actions page

For every button, an operator must be able to answer:

1. What will happen if I press it?
2. What permissions does it need?
3. Can it change code or production?
4. Where will the evidence appear?
5. What happens if it fails?
6. What is the rollback path?
7. How does the result connect to Issues, Actions and Agents?

If the answer cannot be demonstrated by code and current evidence, the control must be labeled **planned**, **unavailable**, or **read-only** rather than presented as operational.
