# Specialized Bot Knowledge Report

Give every DreamCo bot a specialized knowledge system for its division, customers, competitors, app-store product, workflows, safety gates, and learning loop.

## Summary

- Knowledge profiles: 1248 / 1248
- Knowledge domains per bot: 9
- Bots with all domains: 1248
- Source policy coverage: 1248
- Memory policy coverage: 1248
- Runtime/tooling knowledge: 1248
- Safety/approval knowledge: 1248
- App builder knowledge: 1248
- Profile shards: 45 in `reports/specialized_bot_knowledge_profiles`

## Knowledge Domains

### Domain Expertise

Know the bot's industry, job, terminology, workflows, metrics, regulations, and common failure modes.

- Artifacts: domain_glossary, workflow_map, kpi_list, risk_notes

### Customer Intelligence

Know who the bot helps, what problem they have, what proof they need, and what outcome they care about.

- Artifacts: target_customer, problem_brief, buying_triggers, objection_notes

### Competitor Intelligence

Study public competitors, substitutes, pricing, feature gaps, reviews, positioning, onboarding, and trust signals.

- Artifacts: competitor_map, feature_gap_matrix, pricing_notes, differentiation_angle

### App Builder Knowledge

Know how to turn the bot into a usable app, website, course, game, simulation, dashboard, or workflow.

- Artifacts: app_concept, screen_map, api_contract_notes, sandbox_plan, deployment_plan

### Money and Business Model

Know ethical ways the bot can create value, package offers, reduce costs, recover revenue, or support paid client work.

- Artifacts: offer_stack, pricing_hypothesis, unit_economics_notes, blocked_claims

### Marketing and Distribution

Know the audience, launch copy, content ideas, SEO angles, demo script, and outreach drafts without sending anything live.

- Artifacts: audience_segments, content_drafts, demo_script, launch_checklist

### Runtime and Tooling

Know its tools, APIs, webhooks, workflows, skills, sandbox tests, fixtures, and dashboard route.

- Artifacts: tool_contracts, api_contracts, webhook_contracts, workflow_runbook, test_commands

### Safety and Approval

Know what it may draft versus what requires owner approval before customer, money, deployment, or account impact.

- Artifacts: approval_gates, risk_label, safe_mode_limits, rollback_notes

### Learning Memory

Store only useful, source-backed lessons with retention tier, source, confidence, usefulness reason, and next test.

- Artifacts: source_notes, lesson_summary, confidence_score, next_experiment, retention_tier

## Source Policy

- Allowed: public documentation, public pricing pages, public reviews, public case studies, owner-approved notes, generated sandbox evidence, test reports
- Blocked: secrets, private account data without approval, copied proprietary code, paywalled content without permission, personal data beyond approved lead records, low-signal raw scratchpads
