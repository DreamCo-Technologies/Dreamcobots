# Dream AI Company + Library Intelligence

## Purpose

This document captures the approved architecture from the DreamCo planning chat for two connected systems:

1. **Dream AI Company Base** — a structured intelligence catalog for major technology and AI organizations.
2. **Library Intelligence / LibMind** — a scalable specialist system for programming languages, packages, libraries, frameworks, SDKs, runtimes, databases, infrastructure tools, and developer ecosystems.

The design is evidence-first and registry-driven. It does **not** claim a bot has mastered a company/library or that an integration works until tests or source evidence prove it.

## Dream AI Company Base

The target catalog covers at least 100 major technology organizations and 100 AI-focused organizations. Records should be refreshable rather than permanently hard-coded because products, models, pricing, APIs, leadership, and goals change.

### Company record

```json
{
  "name": "",
  "category": [],
  "founded": null,
  "founders": [],
  "origin_story": "",
  "current_goals": [],
  "products": [],
  "services": [],
  "programs": [],
  "developer_tools": [],
  "ai_products": [],
  "models": [],
  "apis": [],
  "cloud_services": [],
  "hardware": [],
  "tech_stack_evidence": [],
  "target_markets": [],
  "niche_markets": [],
  "business_models": [],
  "strengths": [],
  "limitations": [],
  "dreamco_opportunities": [],
  "replication_requirements": [],
  "replication_difficulty": "unknown",
  "bot_blueprints": [],
  "sources": [],
  "verified_at": null
}
```

### Research questions for every organization

- What problem did the company originally solve?
- How did it start and what were its important pivots?
- What is its present strategic direction?
- What products, programs, platforms, APIs, developer tools, cloud services, hardware, models, and non-AI services does it offer?
- Who buys or uses each offering?
- What niches does it serve well or poorly?
- What technologies are publicly documented as part of the offering?
- Which capabilities are useful dependencies for DreamCo?
- Which capabilities are reasonable for DreamCo to reproduce independently?
- Where can DreamCo differentiate rather than merely clone?
- What would implementation require: code, infrastructure, data, licenses, APIs, security, compliance, staff, testing, and cost?
- Which claims are current and source-verified?

## Library Intelligence / LibMind

Creating and maintaining a hand-written source-code class for every package in every ecosystem would create unnecessary duplication and dependency conflicts. The scalable implementation is a **specialist profile per library/package backed by shared execution engines**.

A pandas specialist and a NumPy specialist can therefore behave as distinct bots while using the same tested specialist runtime.

### Specialist record

```json
{
  "id": "python:pandas",
  "ecosystem": "python",
  "package": "pandas",
  "version": null,
  "official_sources": [],
  "capability_index": [],
  "api_index": [],
  "common_use_cases": [],
  "advanced_use_cases": [],
  "performance_notes": [],
  "compatibility": [],
  "security_notes": [],
  "examples": [],
  "test_matrix": [],
  "innovation_hypotheses": [],
  "evidence": [],
  "last_verified": null
}
```

### Ecosystems to support

The discovery architecture must not be limited to US projects or English-language packages. Adapters can be added for public registries and official documentation across ecosystems such as Python, JavaScript/TypeScript, Java/JVM, Kotlin, Scala, .NET/C#, Rust, Go, Ruby, PHP, Dart/Flutter, Swift, Objective-C, C/C++, R, Julia, Lua, Perl, Haskell, Elixir/Erlang, Clojure, Groovy, MATLAB/Octave-compatible ecosystems, databases, ML frameworks, cloud SDKs, infrastructure-as-code, mobile, embedded, game development, data engineering, robotics, and other verified registries.

The phrase **every library in existence** is treated as an expanding discovery target, not a false completeness claim. New ecosystems and packages can continuously enter the registry after validation.

## Specialist lifecycle

1. **Discover** a package from an approved registry or official source.
2. **Normalize** its identity, ecosystem, version, license, documentation and source references.
3. **Index** public APIs and documented capabilities.
4. **Generate** a specialist profile from the common schema.
5. **Sandbox** executable examples with ecosystem-specific dependency isolation.
6. **Test** imports, representative APIs, version compatibility and generated examples.
7. **Certify** only capabilities supported by passing evidence.
8. **Route** relevant Buddy coding tasks to the specialist.
9. **Benchmark** proposed solutions where deterministic tests are possible.
10. **Propose innovation** separately from certified functionality.
11. **Refresh** when package versions or official documentation change.

## Stability rules

DreamCo should never promise "all passing" merely because profiles were generated. Passing status must come from CI evidence.

- Keep generated profiles data-driven rather than creating thousands of near-identical Python modules.
- Isolate dependency execution by ecosystem/version using disposable environments or containers.
- Pin test environments when reproducibility matters.
- Keep discovery/network refresh jobs separate from deterministic repository CI.
- Never execute arbitrary third-party package code in the main application process.
- Validate package identity before installation to reduce dependency-confusion/typosquatting risk.
- Respect package licenses and documentation/content rights.
- Record provenance for generated knowledge.
- Require tests before marking a capability certified.
- Quarantine specialists with failing imports, incompatible dependencies, security problems, or missing evidence.
- Keep experimental innovation ideas distinct from production capabilities.
- Deduplicate aliases, forks and renamed packages without erasing their provenance.

## Shared architecture

```text
Buddy
  -> Capability Router
      -> Library Specialist Registry
          -> Specialist Runtime
              -> Ecosystem Adapter
                  -> Isolated Sandbox
                      -> Test + Benchmark Harness

Official registries/docs
  -> Discovery Adapters
      -> Normalizer
          -> Evidence Store
              -> Specialist Registry

Company sources
  -> Company Research Pipeline
      -> Normalizer
          -> Dream AI Company Base
              -> Opportunity Mapper
                  -> DreamCo roadmap proposals
```

## Initial specialist priorities

Start with high-value ecosystems and packages already relevant to DreamCo, then expand automatically. Priority examples include Python data/AI/web/testing libraries, JavaScript/TypeScript frontend/backend packages, database clients, cloud SDKs, agent frameworks, model-provider SDKs, automation tools, observability, security testing, and deployment tooling.

## Innovation engine

A specialist may generate ideas by combining documented primitives, known use cases, benchmarks, DreamCo needs, and compatible specialists. Innovation output is a proposal, not proof. Each proposal should include:

- problem being solved;
- libraries/capabilities involved;
- expected advantage;
- prototype plan;
- measurable success criteria;
- dependencies and licensing considerations;
- security/privacy considerations;
- tests required before production certification.

## DreamCo opportunity analysis

For every company or library, produce three distinct outputs:

1. **Use** — integrate or depend on the existing offering when that is the best economic/technical choice.
2. **Replicate** — implement an independent compatible capability when feasible and lawful.
3. **Differentiate** — create a DreamCo-native capability aimed at an underserved customer, workflow, price point, privacy model, orchestration layer, or automation experience.

## Build gates

A generated specialist is not production-ready until applicable gates pass:

- schema validation;
- source/provenance validation;
- package identity validation;
- dependency resolution;
- isolated import/load test;
- representative unit tests;
- security policy checks;
- license metadata check;
- compatibility test;
- Buddy routing test;
- failure/timeout handling test;
- registry deduplication check.

## Roadmap

### Phase 1 — schemas and registries

Create schemas for company records, library specialists, evidence, certification, and innovation proposals. Reuse existing DreamCo registries where possible instead of creating conflicting sources of truth.

### Phase 2 — discovery adapters

Add bounded adapters for official/public package registries and company/provider sources. Network discovery produces reviewable snapshots; ordinary CI consumes committed snapshots.

### Phase 3 — specialist factory

Generate virtual specialist profiles and route them through shared runtimes. Avoid one-process-per-library architecture.

### Phase 4 — sandbox certification

Test representative libraries in isolated environments and attach evidence to capabilities.

### Phase 5 — Buddy integration

Buddy selects specialists by language, package, version, task, compatibility and certification evidence.

### Phase 6 — company opportunity engine

Map products/services from the Dream AI Company Base against DreamCo's existing capabilities and produce `use / replicate / differentiate` proposals with implementation requirements.

### Phase 7 — continuous expansion

Scheduled discovery identifies new packages, releases, products and AI technologies. Changes remain proposals until validation passes.

## Success metrics

- number of normalized company records with current evidence;
- number of ecosystems covered;
- number of discovered specialist profiles;
- percentage with verified official sources;
- percentage with passing sandbox tests;
- percentage with certified capabilities;
- routing accuracy;
- duplicate/conflict rate;
- test pass rate;
- useful innovation proposals converted to tested features;
- cost per refresh and per certification run.

## Principle

DreamCo's advantage should not be a giant count of nominal bots. The useful asset is a governed, testable intelligence network in which Buddy can find the right specialist, prove what it can do, combine specialists safely, and turn new ecosystem knowledge into validated DreamCo capabilities.