# User Data Ownership, Company Consent, Source Study, and Subscription Control

## Product promise

The user controls which companies and services may collect, access, use, share, sell, license, trade, profile, or train on their data through DreamCo. A DreamCo connection, purchase, account, or subscription never grants blanket permission for unrelated uses.

This control center complements, rather than duplicates, `server/data-rights-policy.ts`, `server/connection-policy.ts`, `shared/personal-buddy-training-contract.ts`, and the conversation-learning governance policy.

## Independent company permissions

Every company/controller and purpose gets its own consent record. Do not bundle purposes or use pre-checked boxes. Separate choices cover:
- service delivery;
- analytics;
- personalization;
- targeted advertising;
- sale;
- sharing;
- data brokerage;
- AI training;
- model evaluation;
- research;
- automated decisions;
- cross-company profiling.

A user can opt in, opt out, or withdraw for a specific purpose and data category. Receipts record the company, purpose, categories, recipient class, retention, jurisdiction, timestamp, policy version, source, and withdrawal state. No consent means deny for optional processing. Service delivery is not consent to unrelated commercial use.

The system can immediately block future processing under DreamCo's control, revoke supported connector scopes, and prepare provider opt-out/deletion requests. It cannot guarantee that an outside company complied until that company confirms it; Buddy must show request and provider-confirmed statuses separately.

## Buddy may study user-authorized sources

Buddy should support user-directed study of:
- official account exports;
- connected apps and accounts;
- email, calendars, cloud drives, and documents;
- GitHub repositories and developer tools;
- databases and APIs;
- user-uploaded photos, audio, and video;
- social and commerce accounts;
- public web sources.

Every source requires owner authority, exact scopes, purpose, rights review, retention, refresh schedule, and a visible revoke/disconnect control. Start read-only. Do not bypass logins, paywalls, captchas, access controls, or provider terms; never ask users to paste passwords. Study, retrieval, evaluation, personalization, and model training are distinct uses. Training remains off unless separately opted in and rights-cleared. Public availability alone does not prove redistribution or training rights.

## Subscription and recurring-payment control

A personal billing center should list each connected subscription with provider, plan, price, currency, interval, next renewal, payment method reference, and current status. Users can view, disable optional auto-renewals, request pause/resume/cancel, and change plans. Purchases, upgrades, and paid add-ons require fresh exact approval after price and renewal terms are shown. Only the authenticated account owner can act on their subscription.

A cancellation request is not a completed cancellation. Show pending until the provider confirms the change and its effective date. Preserve receipts and audit events. Never cancel another person's subscription or hide fees, trial-to-paid conversions, renewal dates, or cancellation friction.

## Suggested control-center screens

1. **My Data:** data inventory, sources, categories, export, correction, deletion, retention.
2. **Company Permissions:** searchable company list; separate purpose-level opt-in/opt-out controls; consent history and withdrawal receipts.
3. **Buddy Study Sources:** connect, scope selection, read-only study, refresh schedule, activity history, disconnect/revoke.
4. **Subscriptions & Spending:** subscriptions, renewals, price alerts, spend caps, approvals, pause/cancel, receipts.
5. **Privacy Requests:** provider access/correction/export/deletion/opt-out requests and verified response status.

Buttons must be real authenticated actions, not decorative toggles. Show confirmation before high-impact changes, and show the actual result from the provider. Record actor, scope, purpose, timestamp, policy version, result, and evidence in an append-only audit log.

## Implementation contracts added

- `config/user-data-and-subscription-control-policy.json`: deny-by-default product rules.
- `server/user-control-center-policy.ts`: Zod request contracts and plan builders for company consent, Buddy study sources, and subscriptions.
- `tests/task-and-data-policy.test.ts`: tests for purpose-specific consent, explicit authenticated action, source authority, read-only study, and exact subscription approval.

## Honest delivery status

These additions define validated request contracts and plans; they do not yet provide the full authenticated dashboard, persistent consent database, connector OAuth execution, provider-specific opt-out adapters, Stripe customer portal for each end user, or external subscription cancellation. Those must be wired to authenticated per-user routes, tenant-isolated storage, provider adapters, UI controls, and end-to-end tests before the product may claim these features are live.
