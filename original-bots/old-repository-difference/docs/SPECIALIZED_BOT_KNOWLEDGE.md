# Specialized Bot Knowledge

Every DreamCo bot now has a standard specialized knowledge profile. The goal is to make each bot smarter in its own lane without storing junk, secrets, copied proprietary material, or unsafe live-action instructions.

## Knowledge Domains

- Domain Expertise: industry terms, workflows, KPIs, risks, and failure modes.
- Customer Intelligence: target customer, problem, proof needs, objections, and outcomes.
- Competitor Intelligence: public competitors, substitutes, pricing, reviews, feature gaps, and positioning.
- App Builder Knowledge: app concept, screen map, API notes, sandbox plan, and deployment plan.
- Money and Business Model: offer stack, pricing hypothesis, unit economics, and blocked claims.
- Marketing and Distribution: audience segments, content drafts, demo script, and launch checklist.
- Runtime and Tooling: tools, APIs, webhooks, workflows, skills, tests, and dashboards.
- Safety and Approval: approval gates, risk labels, safe mode limits, and rollback notes.
- Learning Memory: source notes, lesson summaries, confidence, next experiments, and retention tier.

## Source Rules

Allowed:

- Public documentation.
- Public pricing pages.
- Public reviews.
- Public case studies.
- Owner-approved notes.
- Generated sandbox evidence.
- Test reports.

Blocked:

- Secrets.
- Private account data without approval.
- Copied proprietary code.
- Paywalled content without permission.
- Personal data beyond approved lead records.
- Low-signal raw scratchpads.

## Commands

```bash
npm run report:specialized-knowledge
npm run check:specialized-knowledge
```
