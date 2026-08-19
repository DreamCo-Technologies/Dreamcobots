# Buddy Capability Scorecard

Use this scorecard to track progress without confusing aspiration with verified capability.

| Dimension | Evidence | Target state |
|---|---|---|
| Correctness | repeatable tests | project-defined threshold |
| Quality | human + automated evaluation | project-defined threshold |
| Speed | latency/throughput measurements | task-specific threshold |
| Safety | policy/security tests | zero known critical violations |
| Reliability | repeated successful runs | project-defined uptime/pass rate |
| Recovery | failure injection + repair tests | bounded recovery with audit trail |
| Explainability | user-facing rationale/status | understandable at user level |
| Beginner UX | usability checklist | pass |
| Developer UX | PR/code-review checklist | pass |
| Cost | measured resource usage | budget target |
| Compatibility | integration regression suite | supported versions pass |
| Drift | scheduled regression evaluation | no unexplained degradation |

## Status levels

- **Unknown** — insufficient evidence
- **Experimental** — sandbox only
- **Passing** — meets the current threshold
- **Reliable** — repeated passes across representative tasks
- **Mastered** — sustained threshold performance with regression protection

These labels describe repository evidence, not a universal ranking of AI systems.
