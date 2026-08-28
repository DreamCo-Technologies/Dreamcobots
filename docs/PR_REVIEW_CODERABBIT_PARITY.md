# DreamCo PR Review — CodeRabbit Parity + DreamCo Extensions

DreamCo should be evaluated against the current public CodeRabbit feature surface, but parity is a benchmark, not a dependency or a claim that every feature is already implemented.

CodeRabbit currently describes automated PR review, IDE/CLI review, one-click/autofix workflows, agent loops, pre-merge checks, agentic chat, linters/SAST integrations, code-graph context, semantic/architectural context, security scanning, and post-merge actions. Its newer Review interface also describes cohorts, code peek, chat, and severity-based triage. DreamCo's implementation should independently reproduce the useful behavior where technically and legally appropriate, then add its own evidence-first control plane. citeturn0search0turn0search1turn0search4turn0search6turn0search10

## Parity matrix

| Capability | CodeRabbit-style baseline | DreamCo target | Evidence required |
|---|---|---|---|
| PR summary | Summarize change and context | Add change intent + capability impact | PR metadata + diff |
| Inline findings | Line/file review comments | Evidence-backed findings with provenance | Diff + source location |
| Severity | Triage by importance | Severity + confidence + blast radius | Finding record |
| Codebase context | Repository/context enrichment | Capability graph + dependency/context graph | Graph artifact |
| Semantic diff | Explain meaning of changes | Semantic + contract + capability diff | Comparison artifact |
| Security | Security analysis/deep scan | Security + trust-boundary + dependency gates | Security artifacts |
| Tests | Identify missing/affected coverage | Test-impact map + regression gate | Test registry + CI |
| Pre-merge checks | Policy gates | Production Greenkeeper gates | Required checks |
| Autofix | Generate/apply fixes | Bounded repair branch + verification PR | Patch + tests |
| Fix-all | Batch related findings | Repair plan grouped by root cause | Repair plan |
| Agent loop | Review → agent → re-review | Review → Buddy repair → test → benchmark → re-review | Iteration evidence |
| Conflict handling | Assist with merge conflicts | Rebuild from current main and transplant unique capability | Replacement PR |
| PR triage | Prioritize review work | healthy/review/blocked/stale/duplicate candidate | PR registry |
| Chat | Ask questions about a change | Evidence-aware Buddy PR analyst | Conversation + sources |
| CLI/IDE | Review before PR | Local-first Buddy review adapter | Local evidence |
| Learnings | Adapt to team/project preferences | Versioned repository review policy and feedback loop | Policy history |
| Integrations | Linters/SAST/project tools | Native DreamCo benchmark, Actions, Pages, capability and recovery graph | Integration evidence |
| Post-merge | Follow-up actions | Verify deployment + benchmark + recovery state | Post-merge evidence |
| Change cohorts | Group independent work | Capability/change clusters + duplicate detection | Cluster artifact |
| Historical learning | Retain review history | Failure fingerprints + repair lineage | Recovery registry |

## DreamCo differentiators

### 1. Evidence graph
Every important finding should link to:

`PR → commit → file → symbol/route → dependency → test → workflow → benchmark → repair → verification`

### 2. Capability impact
A PR is not evaluated only as code. DreamCo asks what capability it adds, changes, removes, duplicates, or risks.

### 3. Benchmark-aware review
A code review can recommend a change, but a capability is not promoted until benchmark and regression evidence support it.

### 4. Unmergeable-PR rebuild engine
Conflicted PRs are not force-merged. DreamCo classifies the unique capability, starts from current `main`, selectively reconstructs the useful change, and validates the replacement.

### 5. Multi-model review council
Where approved model adapters exist, multiple models can independently review the same change. Agreement/disagreement becomes evidence rather than blindly trusting one model.

### 6. Resource-aware intelligence
Review depth can scale with change risk, repository size, available compute, latency budget, and free/local-first policy.

### 7. Longitudinal learning
DreamCo tracks which findings were correct, false positives, regressions, successful repairs, and benchmark improvements. Review policy evolves from measured outcomes.

## Review stages

`INTAKE → CONTEXT → DIFF → DEPENDENCY GRAPH → SECURITY → TEST IMPACT → SEMANTIC/ARCHITECTURE → CAPABILITY IMPACT → BENCHMARK IMPACT → DUPLICATE/OVERLAP → MERGEABILITY → FINDINGS → REPAIR PLAN → VERIFICATION → RE-REVIEW → PROMOTION`

## Decision states

- `GREEN`: applicable gates passed with current evidence.
- `YELLOW`: reviewable but evidence incomplete or stale.
- `RED`: release-blocking finding or failed required gate.
- `BLUE`: unmergeable; rebuild recommended.
- `PURPLE`: duplicate/overlapping capability candidate.
- `GRAY`: not applicable or not executed.

Unknown is never silently converted to green.

## Safety boundary

DreamCo may learn from publicly documented techniques and observable execution evidence. It must not attempt to expose private hidden chain-of-thought, secrets, private prompts, or protected data. The system should explain decisions using concise evidence and artifacts rather than publishing private internal reasoning.

## Competitive benchmark

DreamCo should periodically run a feature-by-feature evaluation against the current public CodeRabbit feature set. The comparison must distinguish:

1. implemented and verified;
2. implemented but unverified;
3. partially implemented;
4. planned;
5. not applicable;
6. blocked by dependency/permission.

The goal is not to copy CodeRabbit. The goal is to build an open, inspectable, benchmark-driven PR operating system that can meet or exceed useful review capabilities while adding DreamCo's capability graph, benchmark loop, recovery engine, model council, and evidence lineage.
