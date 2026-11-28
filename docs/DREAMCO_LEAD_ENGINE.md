# DreamCo Lead Engine

## Purpose

The Lead Engine formalizes the five-stage customer-acquisition workflow: Attract, Capture, Qualify, Nurture, and Convert. It reuses the existing `server/governed-leads.ts` campaign and approval policy rather than creating a second outreach system.

## Current implementation in this change

- `server/lead-engine.ts` defines a strict lead record contract, an explainable 100-point qualification score, a five-stage plan, and an integration-readiness declaration.
- `tests/governed-leads.test.ts` covers score calculation, consent evidence, suppression, prohibited targeting, stage progression, and the external-action boundary.
- The existing `server/governed-leads.ts` remains authoritative for channel permissions, suppression, follow-up cadence, daily caps, per-message owner approval, and dispatch packet creation.
- Existing `server/outbound-adapters.ts` remains authoritative for configured outbound webhook transport and secret references.
- `server/lead-engine-storage.ts` provides owner-scoped PostgreSQL persistence, idempotent activity events, and monotonic stage updates.
- `migrations/0002_lead_engine_crm.sql` creates CRM tables, composite ownership constraints, forced row-level security (RLS), and immutable activity-event updates.

## Qualification model

| Signal | Weight |
|---|---:|
| Buying intent | 30 |
| Budget fit | 25 |
| Timeline | 20 |
| Business fit | 15 |
| Engagement | 10 |
| **Total** | **100** |

The initial tiers are Hot (80-100), Warm (50-79), and Cold (0-49). These are configurable product policy defaults, not validated conversion predictions. The score is explainable decision support and must be calibrated against observed outcomes before it is used for automated prioritization claims.

A high score does not override missing permission, suppression, or required human review. A public-directory prospect without documented recipient permission remains research-only. Suppressed contacts remain blocked even when their numeric score is high.

## Stage responsibilities

1. **Attract:** content planning, permission-aware public/authorized signal research, partner/referral source tracking. Do not scrape private areas or bypass platform terms.
2. **Capture:** accept owner-approved forms, inbound requests, event/referral submissions, and authorized lead magnets. Store opaque contact references in workflow payloads.
3. **Qualify:** validate source provenance, score business fit and buying intent, explain the score, and route to a human, nurture plan, or research-only state.
4. **Nurture:** prepare a cadence plan only where channel-specific permission and suppression checks pass. Actual sends must use the governed approval and configured adapter path.
5. **Convert:** prepare a human-reviewed discovery/demo/proposal handoff. Booking, contracts, CRM writes, and payments require their own authorized integrations and approval.

## Integration boundaries

This module is a deterministic policy and persistence foundation. It does not discover or scrape prospects, send email/SMS/voice/social messages, book calendar events, create contracts, or process payments. CRM persistence is implemented in `server/lead-engine-storage.ts`, and is exposed through OAuth-protected, owner-scoped HTTP routes. `leadEngineReadiness()` reports this remaining dependency honestly.

### CRM storage setup

Apply `migrations/0002_lead_engine_crm.sql` to the target PostgreSQL database using the deployment's reviewed migration process. The application database role must not be a superuser or have `BYPASSRLS`. Every repository operation sets `app.owner_id` transaction-locally; PostgreSQL RLS then restricts reads and writes to that owner. Callers must derive `ownerId` from a verified authenticated identity, never from request-body input. Activity events are not editable; authorized deletion remains possible through a future data-rights workflow and the parent lead's cascade.

Repository functions: `saveLeadEngineRecord`, `getLeadEngineRecord`, `listLeadEngineRecords`, `appendLeadEngineActivity`, and `listLeadEngineActivities`. The repository rejects owner mismatches and stage regression; duplicate activity event IDs are idempotent.

The existing `/api/buddy/lead-plan` endpoint remains the governed outreach planning entry point. The qualification and CRM routes now use the repository's signed, expiring Google/Apple OAuth session. The server derives a stable opaque owner key from the verified provider subject; the request body cannot select a tenant. CRM writes require a same-origin Origin header and are rate-limited. This change does not create a second dispatch route.

## Production completion checklist

- [x] Strict input schema and credential-like value rejection
- [x] Explainable qualification score and deterministic tiering
- [x] Five-stage plan with permission and suppression gates
- [x] One-stage-at-a-time progression with explicit nurture permission and human-review conversion evidence
- [x] Reuse of existing governed outreach and suppression policies
- [x] Focused qualification regression tests added to the existing governed-leads test suite
- [x] Storage contract tests added to the governed test suite
- [x] Owner-scoped PostgreSQL CRM repository and tenant-isolation migration authored
- [x] Consent evidence and suppression state included in persisted lead records
- [ ] Apply migration in staging/production and verify RLS using the actual non-superuser application role
- [x] OAuth-protected CRM HTTP routes with server-derived owner identity and same-origin write checks
- [ ] Consent evidence lifecycle, expiry checks, and durable suppression update workflows
- [ ] Owner-configured lead magnet/form integration
- [ ] Approved content and signal-source adapters with provenance
- [ ] Calendar integration for owner-authorized booking
- [ ] Human-reviewed proposal and conversion handoff
- [ ] End-to-end tests against configured staging integrations
- [ ] Exact-head CI and security checks passing

## Release truth

This PR now implements qualification, stage planning, and an owner-scoped PostgreSQL CRM persistence foundation. It does not certify the full Lead Engine as production-ready. The migration has not been applied to a live database, RLS has not been exercised against the deployed application role, and authenticated HTTP, lead acquisition, nurturing, booking, and conversion integrations remain gated on separate integration work and passing evidence.