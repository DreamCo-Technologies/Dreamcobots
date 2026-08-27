# DreamCo Digital Asset Strategy

Buddy treats digital assets as first-class operational objects rather than loose files.

## Asset lifecycle

`discovered -> registered -> verified -> available -> composed -> deployed -> monitored -> deprecated -> archived`

## Asset graph

Assets expose capabilities and dependency edges. This lets Buddy answer:

- What can solve this task?
- Which assets provide the capability?
- What dependencies would be involved?
- Which assets are verified and trusted?
- What is the lowest-risk/cost route?
- What changes if an asset becomes unavailable?

## Recommended future asset classes

Models, datasets, agents, bots, skills, tools, APIs, connectors, prompts, workflows, code, repositories, documents, knowledge, templates, schemas, configurations, infrastructure, benchmarks, experiments, policies, media, packages, containers, plugins, reports, dashboards and secret references.

## Safety

Registry metadata may describe credentials, but raw secrets never belong in the registry. External actions remain subject to authorization, policy and approval gates.

## Composition

Future Buddy work should be able to compose verified assets into temporary task-specific plans, test them in a sandbox, score them, and preserve successful compositions as versioned workflows.
