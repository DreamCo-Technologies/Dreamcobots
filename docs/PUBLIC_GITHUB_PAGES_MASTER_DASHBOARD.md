# DreamCo GitHub Pages Master Dashboard

## Purpose

GitHub Pages is the public window into DreamCo's evolving open-source system. It should make the repository understandable, inspectable, benchmarkable, and downloadable without exposing private or dangerous operational data.

The existing repository already contains public-site and inventory infrastructure, including `website/`, Actions-health reporting, a Buddy page, a repository system map, a public-site builder, and a repository test registry. This plan connects those surfaces into one evidence-driven dashboard rather than replacing them with another parallel system.

## What the dashboard must expose

### Repository

- repository identity and current reviewed branch status;
- complete tracked-file inventory and scan timestamp;
- subsystem ownership and unmapped-file count;
- architecture and dependency relationships;
- change history and release history;
- known issues, blockers, regressions and owner actions.

### Buddy and bots

- bot/division registry;
- capabilities and tool contracts;
- routing/model bindings;
- runtime readiness;
- sandbox status;
- test coverage;
- assisted versus independent capability state.

### Benchmarks

For every registered benchmark, expose the applicable:

- capability/correctness result;
- quality dimensions;
- latency and time-to-useful-result;
- throughput;
- resource/tool/model/cost efficiency when measurable;
- reliability and recovery;
- parallel efficiency;
- regression state;
- independence state;
- baseline/reference;
- evidence timestamp and artifact reference;
- blocker or gap-closure status.

A benchmark is never marked mastered from a plan, model-routing path, or single unverified result.

### Actions and testing

Expose safe summaries for:

- workflow inventory;
- current workflow health;
- latest verified run status;
- test suites;
- targeted/dependent/full regression results;
- security checks;
- build checks;
- artifacts;
- benchmark runs;
- remediation history.

### Releases and downloads

Provide a public download center containing only artifacts that CI has actually produced and verified. Each artifact should show version, platform, build timestamp, verification status and source commit.

Supported targets can include Windows, macOS and Linux when reproducible packaging is actually available. Missing platforms remain visibly marked as unavailable rather than represented by broken download buttons.

## Public/private boundary

Pages must never publish:

- credentials or tokens;
- private keys;
- private user information;
- sensitive raw logs;
- secret environment values;
- uncontrolled live payment operations;
- unapproved external-action controls.

Public pages should expose **status and evidence**, not privileged control.

## Truth model

Every dashboard value needs a source and timestamp. Values should be one of:

`unknown | discovered | cataloged | implemented | tested | passing | degraded | blocked | regression | deprecated | not_applicable`

When evidence is stale or unavailable, the UI should say so.

## Update architecture

```text
Repository files
      |
      +--> inventory scanner
      +--> test registry
      +--> benchmark registry
      +--> Actions results
      +--> security results
      +--> build/release artifacts
      +--> runtime/capability maps
      |
      v
Evidence normalization
      |
      v
Deterministic public data
      |
      +--> GitHub Pages dashboard
      +--> downloadable reports
      +--> benchmark history
      +--> release center
```

Independent readers/scanners may run in parallel. Shared generated outputs are serialized or merged deterministically to prevent race conditions.

## No-bug promise handling

The project should aim for a high-confidence download experience, but no software system should claim literally zero possible bugs before verification. The release gate therefore requires reproducible builds, smoke tests, artifact validation, startup checks and platform-specific verification where available. Any unverified target remains clearly labeled.

## Ultimate dashboard principle

The goal is not to hide complexity. The goal is to make the complexity navigable:

**Everything tracked → classified → evidenced → summarized → linked to source → visible on Pages.**

That makes the public site a living window into the open-source evolution of DreamCo while preserving the safety boundary around private credentials and privileged actions.
