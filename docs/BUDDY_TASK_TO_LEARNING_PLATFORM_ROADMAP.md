# DreamCo Buddy: task-to-learning and platform capability roadmap

## Product objective

Buddy should accept a user's requested outcome, infer the skills and tools needed, select the best authorized learning source, teach only the missing skills, and then help complete the task with evidence. DreamCo owns the orchestration, original lessons, benchmarks, progress records, and integrations; external platforms retain ownership of their services and content.

## Request-to-completion loop

1. Parse the requested outcome and constraints.
2. Decompose the outcome into skills, prerequisites, tools, and acceptance criteria.
3. Inspect Buddy's benchmark history and identify the smallest meaningful capability gap.
4. Rank catalog resources by relevance, teaching quality, practice fit, access, cost, license, and expected gain per minute.
5. Ask for authorization before account access, gated material, or any paid resource/compute.
6. Retrieve only permitted material through an official API, public documentation, or user-provided authorized content.
7. Convert concepts into DreamCo-authored explanations, exercises, checklists, and benchmark tasks; do not copy course chapters or proprietary solutions.
8. Practice in a sandbox with synthetic or explicitly authorized data.
9. Execute the user's task in an allowed environment, with approval gates for consequential actions.
10. Verify the result, run holdout and regression tests, and explain what was learned.
11. Save a provenance-linked learning record and update the user's skill/task progress.
12. Reopen the capability if later evidence shows a regression.

## Platform capability map

| Platform | DreamCo capability to build | Boundary |
|---|---|---|
| GitHub | Repositories, branches, commits, PRs, issues, Actions, code review, release and Pages status | Use GitHub APIs and permissions; no pretending API-only access can run arbitrary local commands |
| Hugging Face | Model/dataset discovery, model cards, dataset cards, Spaces, evaluation, inference endpoints, authorized training jobs | Respect model/dataset licenses, gated access, token scopes, quotas and compute cost |
| Ollama | Local model discovery, pull/run, Modelfile/import, local API, model packaging and serving | Primarily local inference/serving; pair with a real training framework for weight updates |
| O*NET | Occupation-to-task/skill/knowledge mapping, work activities and role-based competency graphs | Preserve source attribution and data terms; O*NET alignment is not a professional license |
| freeCodeCamp / Codecademy / Khan / MIT OCW | Curriculum discovery, lesson objectives, skill prerequisites and original practice tasks | Course access, account and reuse rights vary; do not scrape or reproduce protected content |
| Cloud learning platforms | Cloud skill paths, labs, cost-aware sandbox exercises and provider certification mapping | Credits, labs, exams and compute may cost money |
| OSHA / NIST / standards bodies | Official safety, security, risk and standards references | Keep safety-critical tasks conservative; distinguish study from certification or authorization |

## Course object and progress evidence

Every course/lesson record should include: stable source ID, URL, provider, source revision/date, access status, license/terms review, skill tags, prerequisites, estimated effort, cost class, lesson objectives, original exercise, benchmark ID, holdout ID, evidence URI/hash, learner/model version, score delta, and mastery state.

Suggested mastery states: discovered, queued, studying, practiced, benchmarked, holdout_passed, graduated, regressed. A course completion badge alone never sets graduated.

## Vibe-coding experience

A user should be able to say, for example, "Build me a Shopify app that syncs inventory." Buddy should:
- plan the deliverable and acceptance tests;
- identify missing skills (Shopify API, webhooks, TypeScript, database, deployment);
- route each gap to a suitable resource;
- teach only the necessary concepts;
- generate a starter project and explain it;
- run permitted tests and debug failures;
- create a branch/PR and deployment plan;
- record a reusable, rights-cleared task recipe.

The user should not need to know which provider or framework is best. Advanced users can override the route and inspect sources, cost estimates, code, tests, and provenance.

## Implementation sequence

### Phase 1 — foundation
- Keep the resource catalog versioned and machine-readable.
- Add task-to-skill decomposition and deterministic resource ranking.
- Add explicit permissions, cost caps, license review, and access-state tracking.
- Emit a structured learning route rather than claiming external work has run.

### Phase 2 — provider adapters
Implement one adapter at a time behind a common contract: discover, describe, authorize, retrieve, execute (only if supported), evaluate, and record evidence. Add contract tests with mocked responses before live credentials. First integrations: GitHub, Hugging Face Hub, Ollama local API, and O*NET data/services.

### Phase 3 — original course factory
Generate lessons from permitted source metadata and notes, with original examples, code labs, rubrics, and tests. Track source revisions and invalidate stale lessons when upstream material changes.

### Phase 4 — execution and continuous learning
Connect task execution to isolated workspaces, repository operations, benchmark runners, and model-training handoffs. Keep training separate from retrieval/prompt improvement. Weight training requires approved datasets, a compatible model license, compute budget, baseline, validation, untouched holdout, repeated runs, and regression checks.

### Phase 5 — broad capability coverage
Expand by user demand and measured task frequency across software, data, business, skilled trades, workplace safety, cloud, cybersecurity, education, creative work, and other domains. Use domain-specific benchmarks; never collapse all skills into one misleading "intelligence" score.

## Completion definition

DreamCo is on the path to parity when each advertised capability has:
- a documented provider/source and permission model;
- a working adapter or clearly labeled manual handoff;
- unit and contract tests;
- end-to-end task evidence;
- cost, latency, reliability and safety measurements;
- documented limitations and fallback;
- user-visible progress and audit history.

"Everything they can do" is a product direction, not a claim of instant parity. Build the capability matrix, prove each integration independently, and publish honest completion states.
