# DreamCo Lead Engine

## Purpose

The Lead Engine formalizes the five-stage customer-acquisition workflow: Attract, Capture, Qualify, Nurture, and Convert. It reuses the existing `server/governed-leads.ts` campaign and approval policy rather than creating a second outreach system.

## Current implementation in this change

- `server/lead-engine.ts` defines a strict lead record contract, an explainable 100-point qualification score, a five-stage plan, and an integration-readiness declaration.
- `tests/governed-leads.test.ts` covers score calculation, consent evidence, suppression, prohibited targeting, stage progression, and the external-action boundary.
- The existing `server/governed-leads.ts` remains authoritative for channel permissions, suppression, follow-up cadence, daily caps, per-message owner approval, and dispatch packet creation.
- Existing `server/outbound-adapters.ts` remains authoritative for configured outbound webhook transport and secret references.

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

This module is a deterministic policy layer. It does not discover or scrape prospects, persist CRM records, send email/SMS/voice/social messages, book calendar events, create contracts, or process payments. `leadEngineReadiness()` reports these dependencies honestly.

The existing `/api/buddy/lead-plan` endpoint remains the governed outreach planning entry point. The new qualification policy is not exposed through a new HTTP route in this PR because the repository's API authentication gate must be verified first. This change does not create a second dispatch route.

## Production completion checklist

- [x] Strict input schema and credential-like value rejection
- [x] Explainable qualification score and deterministic tiering
- [x] Five-stage plan with permission and suppression gates
- [x] Reuse of existing governed outreach and suppression policies
- [x] Focused regression tests added to the existing governed-leads test suite
- [ ] Authenticated CRM persistence and tenant isolation
- [ ] Consent evidence lifecycle and durable suppression storage
- [ ] Owner-configured lead magnet/form integration
- [ ] Approved content and signal-source adapters with provenance
- [ ] Calendar integration for owner-authorized booking
- [ ] Human-reviewed proposal and conversion handoff
- [ ] End-to-end tests against configured staging integrations
- [ ] Exact-head CI and security checks passing

## Release truth

This PR implements the qualification and stage-planning foundation. It does not certify the full Lead Engine as production-ready. The remaining checklist items require separate integration work, configured credentials, owner authorization, and passing evidence.